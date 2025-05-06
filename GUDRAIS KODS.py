from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import sqlite3
import logging
import tkinter as tk
from tkinter import ttk
from threading import Thread
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"

logging.basicConfig(filename="application.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db():
    conn = sqlite3.connect("pulcinu_pieteiksanas.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Lietotājvārds un parole ir obligāti!", "danger")
            return redirect(url_for("login"))
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM lietotaji WHERE lietotajvards = ? AND parole = ?", (username, password))
        user = cur.fetchone()
        conn.close()
        if user:
            session["user"] = username
            logging.info(f"Lietotājs '{username}' veiksmīgi autentificējās.")
            return redirect(url_for("index"))
        else:
            logging.warning(f"Neveiksmīgs autentifikācijas mēģinājums lietotājam '{username}'.")
            flash("Nepareizs lietotājvārds vai parole!", "danger")
    return render_template_string('''
    <!doctype html>
    <title>Pieslēgties</title>
    <h2>Pieslēgties</h2>
    <form method="post">
        <input name="username" placeholder="Lietotājvārds"><br>
        <input name="password" type="password" placeholder="Parole"><br>
        <button type="submit">Ieiet</button>
    </form>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for category, message in messages %}
          <li style="color:red;">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    ''')

@app.route("/index")
def index():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string('''
    <!doctype html>
    <title>R6VSK Pulciņu Sistēma</title>
    <h2>Laipni lūdzam, {{session['user']}}!</h2>
    <a href="{{ url_for('pieteikties') }}">Pieteikties pulciņam</a><br>
    <a href="{{ url_for('statistika') }}">Skatīt statistiku</a><br>
    <a href="{{ url_for('logout') }}">Iziet</a>
    ''')

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/pieteikties", methods=["GET", "POST"])
def pieteikties():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pulcini")
    pulcini = cur.fetchall()
    if request.method == "POST":
        epasts = request.form["epasts"]
        vards = request.form["vards"]
        uzvards = request.form["uzvards"]
        klase = request.form["klase"]
        pulcins_id = request.form.get("pulcins_id")
        try:
            pulcins_id_int = int(pulcins_id)
        except (TypeError, ValueError):
            pulcins_id_int = None
        if not epasts or "@edu.riga.lv" not in epasts:
            flash("Nepareizs e-pasts!", "danger")
        elif not all([vards, uzvards, klase, pulcins_id]) or pulcins_id_int is None:
            flash("Visi lauki ir obligāti!", "danger")
        else:
            cur.execute("SELECT * FROM pulcini WHERE id = ?", (pulcins_id_int,))
            izvēlētais_pulcins = cur.fetchone()
            if not izvēlētais_pulcins or izvēlētais_pulcins["pieejamas_vietas"] <= 0:
                flash("Nepareizs vai pilns pulciņš!", "danger")
            else:
                cur.execute('SELECT * FROM pieteikumi WHERE vards = ? AND uzvards = ? AND pulcins_id = ?', (vards, uzvards, pulcins_id_int))
                if cur.fetchone():
                    flash("Jūs jau esat pieteicies šim pulciņam!", "info")
                else:
                    cur.execute('INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id) VALUES (?, ?, ?, ?)', (vards, uzvards, klase, pulcins_id_int))
                    cur.execute('UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?', (pulcins_id_int,))
                    conn.commit()
                    flash(f"Pieteikums uz '{izvēlētais_pulcins['nosaukums']}' tika veiksmīgi pievienots!", "success")
    conn.close()
    return render_template_string('''
    <!doctype html>
    <title>Pieteikties pulciņam</title>
    <h2>Pieteikties pulciņam</h2>
    <form method="post">
        E-pasts: <input name="epasts"><br>
        Vārds: <input name="vards"><br>
        Uzvārds: <input name="uzvards"><br>
        Klase: <input name="klase"><br>
        Pulciņš:
        <select name="pulcins_id">
            <option value="">Izvēlies...</option>
            {% for p in pulcini %}
                <option value="{{p['id']}}">{{p['nosaukums']}} (Pieejamas vietas: {{p['pieejamas_vietas']}})</option>
            {% endfor %}
        </select><br>
        <button type="submit">Pieteikties</button>
    </form>
    <a href="{{ url_for('index') }}">Atpakaļ</a>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for category, message in messages %}
          <li style="color:{{'green' if category=='success' else 'red'}};">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    ''', pulcini=pulcini)

@app.route("/statistika")
def statistika():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
        FROM pieteikumi
        JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
        GROUP BY pulcini.nosaukums
    ''')
    stats = cur.fetchall()
    conn.close()
    return render_template_string('''
    <!doctype html>
    <title>Statistika</title>
    <h2>Pulciņu Statistika</h2>
    <ul>
    {% for pulcins in stats %}
        <li>{{ pulcins[0] }} - {{ pulcins[1] }} pieteikumi</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('index') }}">Atpakaļ</a>
    ''', stats=stats)

def open_tkinter_window():
    def check_server():
        try:
            requests.get("http://127.0.0.1:5000/")
            return True
        except requests.ConnectionError:
            return False

    def start_flask_app():
        app.run()

    # Start Flask app in a separate thread
    flask_thread = Thread(target=start_flask_app, daemon=True)
    flask_thread.start()

    # Wait for the server to start
    while not check_server():
        pass

    # Create a tkinter window
    root = tk.Tk()
    root.title("Flask App")
    root.geometry("800x600")

    # Embed a web view using tkinter's ttk.Label
    web_frame = ttk.Label(root, text="Flask app is running at http://127.0.0.1:5000/")
    web_frame.pack(expand=True, fill="both")

    # Run the tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    open_tkinter_window()