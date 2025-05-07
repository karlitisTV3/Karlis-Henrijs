from flask import Flask, render_template_string, request, redirect, url_for, flash, session
import sqlite3
import logging
import tkinter as tk
from tkinter import ttk
from threading import Thread
import requests
import webbrowser

app = Flask(__name__)
app.secret_key = "supersecretkey"

logging.basicConfig(filename="application.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_db():
    try:
        conn = sqlite3.connect("pulcinu_pieteiksanas.db")
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Datubāzes savienojuma kļūda: {e}")
        raise

@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"Internal Server Error: {e}")
    return render_template_string('''
    <!doctype html>
    <html>
    <head>
        <title>Kļūda</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
            .container { max-width: 600px; margin: 50px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); text-align: center; }
            h2 { color: #d9534f; }
            p { color: #333; }
            a { text-decoration: none; color: #007bff; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Servera kļūda</h2>
            <p>Atvainojamies, bet serveris saskārās ar problēmu. Lūdzu, mēģiniet vēlreiz vēlāk.</p>
            <a href="{{ url_for('login') }}">Atgriezties uz sākumlapu</a>
        </div>
    </body>
    </html>
    ''', 500)

@app.route("/", methods=["GET", "POST"])
def login():
    try:
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
    except sqlite3.Error as e:
        logging.error(f"Datubāzes kļūda: {e}")
        flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
    return render_template_string('''
    <!doctype html>
    <html>
    <head>
        <title>Pieslēgties</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
            .container { max-width: 400px; margin: 50px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            h2 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            input, button { margin: 10px 0; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
            button { background-color: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            a { text-decoration: none; color: #007bff; text-align: center; display: block; margin-top: 10px; }
            a:hover { text-decoration: underline; }
            ul { padding: 0; list-style: none; }
            li { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Pieslēgties</h2>
            <form method="post">
                <input name="username" placeholder="Lietotājvārds"><br>
                <input name="password" type="password" placeholder="Parole"><br>
                <button type="submit">Ieiet</button>
            </form>
            <a href="{{ url_for('register') }}">Reģistrēties</a>
            <a href="{{ url_for('reset_password') }}">Aizmirsāt paroli?</a>
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                <ul>
                {% for category, message in messages %}
                  <li>{{ message }}</li>
                {% endfor %}
                </ul>
              {% endif %}
            {% endwith %}
        </div>
    </body>
    </html>
    ''')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Visi lauki ir obligāti!", "danger")
        else:
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM lietotaji WHERE lietotajvards = ?", (username,))
                if cur.fetchone():
                    flash("Lietotājvārds jau eksistē!", "danger")
                else:
                    cur.execute("INSERT INTO lietotaji (lietotajvards, parole) VALUES (?, ?)", (username, password))
                    conn.commit()
                    flash("Reģistrācija veiksmīga! Tagad varat pieslēgties.", "success")
                conn.close()
            except sqlite3.Error as e:
                logging.error(f"Datubāzes kļūda: {e}")
                flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
    return render_template_string('''
    <!doctype html>
    <title>Reģistrēties</title>
    <h2>Reģistrēties</h2>
    <form method="post">
        <input name="username" placeholder="Lietotājvārds"><br>
        <input name="password" type="password" placeholder="Parole"><br>
        <button type="submit">Reģistrēties</button>
    </form>
    <a href="{{ url_for('login') }}">Atpakaļ</a>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for category, message in messages %}
          <li style="color:{{'green' if category=='success' else 'red'}};">{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    ''')

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]
        if not username or not new_password:
            flash("Visi lauki ir obligāti!", "danger")
        else:
            try:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM lietotaji WHERE lietotajvards = ?", (username,))
                if not cur.fetchone():
                    flash("Lietotājvārds neeksistē!", "danger")
                else:
                    cur.execute("UPDATE lietotaji SET parole = ? WHERE lietotajvards = ?", (new_password, username))
                    conn.commit()
                    flash("Parole veiksmīgi nomainīta!", "success")
                conn.close()
            except sqlite3.Error as e:
                logging.error(f"Datubāzes kļūda: {e}")
                flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
    return render_template_string('''
    <!doctype html>
    <title>Aizmirstā parole</title>
    <h2>Aizmirstā parole</h2>
    <form method="post">
        <input name="username" placeholder="Lietotājvārds"><br>
        <input name="new_password" type="password" placeholder="Jaunā parole"><br>
        <button type="submit">Nomainīt paroli</button>
    </form>
    <a href="{{ url_for('login') }}">Atpakaļ</a>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
        {% for category, message in messages %}
          <li style="color:{{'green' if category=='success' else 'red'}};">{{ message }}</li>
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
    <html>
    <head>
        <title>R6VSK Pulciņu Sistēma</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
            .container { max-width: 600px; margin: 50px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            h2 { text-align: center; color: #333; }
            a { text-decoration: none; color: #007bff; display: block; margin: 10px 0; text-align: center; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Laipni lūdzam, {{session['user']}}!</h2>
            <a href="{{ url_for('pieteikties') }}">Pieteikties pulciņam</a>
            <a href="{{ url_for('statistika') }}">Skatīt statistiku</a>
            <a href="{{ url_for('detailed_stats') }}">Detalizēta statistika</a>
            <a href="{{ url_for('logout') }}">Iziet</a>
        </div>
    </body>
    </html>
    ''')

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/pieteikties", methods=["GET", "POST"])
def pieteikties():
    if "user" not in session:
        return redirect(url_for("login"))
    try:
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
    except sqlite3.Error as e:
        logging.error(f"Datubāzes kļūda: {e}")
        flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
    return render_template_string('''
    <!doctype html>
    <html>
    <head>
        <title>Pieteikties pulciņam</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; }
            .container { max-width: 600px; margin: 50px auto; padding: 20px; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            h2 { text-align: center; color: #333; }
            form { display: flex; flex-direction: column; }
            input, select, button { margin: 10px 0; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
            button { background-color: #007bff; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            a { text-decoration: none; color: #007bff; text-align: center; display: block; margin-top: 10px; }
            a:hover { text-decoration: underline; }
            ul { padding: 0; list-style: none; }
            li { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
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
        </div>
    </body>
    </html>
    ''', pulcini=pulcini)

@app.route("/statistika")
def statistika():
    if "user" not in session:
        return redirect(url_for("login"))
    try:
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
    except sqlite3.Error as e:
        logging.error(f"Datubāzes kļūda: {e}")
        flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
        stats = []
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

@app.route("/detailed_stats")
def detailed_stats():
    if "user" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            SELECT pieteikumi.vards, pieteikumi.uzvards, pulcini.nosaukums
            FROM pieteikumi
            JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
        ''')
        details = cur.fetchall()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"Datubāzes kļūda: {e}")
        flash("Radās problēma ar datubāzi. Lūdzu, mēģiniet vēlreiz vēlāk.", "danger")
        details = []
    return render_template_string('''
    <!doctype html>
    <title>Detalizēta Statistika</title>
    <h2>Detalizēta Statistika</h2>
    <ul>
    {% for detail in details %}
        <li>{{ detail[0] }} {{ detail[1] }} - {{ detail[2] }}</li>
    {% endfor %}
    </ul>
    <a href="{{ url_for('statistika') }}">Atpakaļ</a>
    ''', details=details)

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

    # Open the Flask app in a new browser window
    webbrowser.open_new("http://127.0.0.1:5000/")

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