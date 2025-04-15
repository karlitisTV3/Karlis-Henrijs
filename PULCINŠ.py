import sqlite3

# Izveido savienojumu ar datubāzi un tabulu
conn = sqlite3.connect("pulcinu_pieteiksanas.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS pieteikumi (
id INTEGER PRIMARY KEY AUTOINCREMENT,
vards TEXT,
uzvards TEXT,
klase TEXT,
novirziens TEXT,
pulcins TEXT,
ieprieks TEXT,
informacijas_avots TEXT
)
''')

# Funkcija pieteikumam

def pieteikties_pulcinam():
    print("== R6VSK Pulciņu Pieteikšanās ==")
    dati = (
        input("Vārds: "),
        input("Uzvārds: "),
        input("Klase: "),
        input("Pulciņa novirziens: "),
        input("Izvēlētais pulciņš: "),
        input("Vai esat piedalījies iepriekš? (jā/ne): ").lower(),
        input("Kā uzzinājāt par pulciņu?: ")
    )
    cursor.execute('''
    INSERT INTO pieteikumi (vards, uzvards, klase, novirziens, pulcins, ieprieks, informacijas_avots)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', dati)
    conn.commit()
    print("\nPaldies! Jūsu pieteikums tika saglabāts datubāzē.")

pieteikties_pulcinam()
conn.close()