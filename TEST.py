import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
import logging

# Configure logging
logging.basicConfig(filename="application.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    root = tk.Tk()
    root.title("R6VSK Pulciņu Sistēma")
    root.geometry("400x300")
    conn = sqlite3.connect("pulcinu_pieteiksanas.db")
    cursor = conn.cursor()

    # User authentication
    def authenticate_user():
        username = simpledialog.askstring("Lietotājvārds", "Ievadiet savu lietotājvārdu:")
        password = simpledialog.askstring("Parole", "Ievadiet savu paroli:", show="*")
        if not username or not password:
            messagebox.showerror("Kļūda", "Lietotājvārds un parole ir obligāti!")
            return False

        cursor.execute("SELECT * FROM lietotaji WHERE lietotajvards = ? AND parole = ?", (username, password))
        user = cursor.fetchone()
        if user:
            logging.info(f"Lietotājs '{username}' veiksmīgi autentificējās.")
            return True
        else:
            logging.warning(f"Neveiksmīgs autentifikācijas mēģinājums lietotājam '{username}'.")
            messagebox.showerror("Kļūda", "Nepareizs lietotājvārds vai parole!")
            return False

    # Enhanced error handling
    def execute_query(query, params=()):
        try:
            cursor.execute(query, params)
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"SQL kļūda: {e}")
            messagebox.showerror("Kļūda", f"Radās kļūda: {e}")

    def pieteikties():
        epasts = simpledialog.askstring("E-pasts", "Ievadiet savu skolas e-pastu:")
        if not epasts or "@edu.riga.lv" not in epasts:
            messagebox.showerror("Kļūda", "Nepareizs e-pasts!")
            return

        vards = simpledialog.askstring("Vārds", "Ievadiet savu vārdu:")
        uzvards = simpledialog.askstring("Uzvārds", "Ievadiet savu uzvārdu:")
        klase = simpledialog.askstring("Klase", "Ievadiet savu klasi:")

        if not all([vards, uzvards, klase]):
            messagebox.showerror("Kļūda", "Visi lauki ir obligāti!")
            return

        cursor.execute("SELECT * FROM pulcini")
        pulcini = cursor.fetchall()
        if not pulcini:
            messagebox.showinfo("Informācija", "Nav pieejamu pulciņu.")
            return

        pulcins_id = simpledialog.askinteger("Pulciņa ID", "Izvēlieties pulciņa ID:")
        izvēlētais_pulcins = next((p for p in pulcini if p[0] == pulcins_id), None)
        if not izvēlētais_pulcins or izvēlētais_pulcins[5] <= 0:
            messagebox.showerror("Kļūda", "Nepareizs vai pilns pulciņš!")
            return

        cursor.execute('SELECT * FROM pieteikumi WHERE vards = ? AND uzvards = ? AND pulcins_id = ?', (vards, uzvards, pulcins_id))
        if cursor.fetchone():
            messagebox.showinfo("Informācija", "Jūs jau esat pieteicies šim pulciņam!")
            return

        try:
            execute_query('''
            INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id)
            VALUES (?, ?, ?, ?)
            ''', (vards, uzvards, klase, pulcins_id))
            execute_query('UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?', (pulcins_id,))
            messagebox.showinfo("Veiksmīgi", f"Pieteikums uz '{izvēlētais_pulcins[1]}' tika veiksmīgi pievienots!")
            logging.info(f"Pieteikums veiksmīgi pievienots: {vards} {uzvards}, Pulciņš ID: {pulcins_id}")
        except Exception as e:
            logging.error(f"Kļūda pieteikšanās procesā: {e}")
            messagebox.showerror("Kļūda", "Radās neparedzēta kļūda!")

    def statistika():
        try:
            cursor.execute('''
            SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
            FROM pieteikumi
            JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
            GROUP BY pulcini.nosaukums
            ''')
            stats = "\n".join([f"{pulcins[0]} - {pulcins[1]} pieteikumi" for pulcins in cursor.fetchall()])
            messagebox.showinfo("Statistika", stats)
            logging.info("Statistika veiksmīgi iegūta.")
        except Exception as e:
            logging.error(f"Kļūda statistikas iegūšanā: {e}")
            messagebox.showerror("Kļūda", "Radās neparedzēta kļūda!")

    if authenticate_user():
        tk.Button(root, text="Pieteikties pulciņam", command=pieteikties).pack(pady=10)
        tk.Button(root, text="Skatīt statistiku", command=statistika).pack(pady=10)
        tk.Button(root, text="Iziet", command=root.destroy).pack(pady=10)
        root.mainloop()
    else:
        root.destroy()

if __name__ == "__main__":
    main()