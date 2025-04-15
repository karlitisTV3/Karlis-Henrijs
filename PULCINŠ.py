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
    pieejamie_novirzieni = {
        "Māksla": ["Zīmēšana", "Gleznošana", "Keramika"],
        "Sports": ["Futbols", "Basketbols", "Volejbols"],
        "Mūzika": ["Ģitāra", "Klavieres", "Dziedāšana"],
        "Tehnoloģijas": ["Programmēšana", "Robotika", "3D modelēšana"]
    }

    while True:
        print("== R6VSK Pulciņu Pieteikšanās ==")
        dati = (
            input("Vārds: "),
            input("Uzvārds: "),
            input("Klase: "),
        )
        print("Pieejamie novirzieni:", ", ".join(pieejamie_novirzieni.keys()))
        novirziens = input("Pulciņa novirziens: ")
        if novirziens not in pieejamie_novirzieni:
            print("Šāds novirziens neeksistē. Lūdzu, mēģiniet vēlreiz.\n")
            continue

        while True:
            print(f"Pieejamie pulciņi novirzienam '{novirziens}':", ", ".join(pieejamie_novirzieni[novirziens]))
            pulcins = input("Izvēlētais pulciņš: ")
            if pulcins not in pieejamie_novirzieni[novirziens]:
                print("Šāds pulciņš neeksistē. Lūdzu, mēģiniet vēlreiz.\n")
                continue
            break

        ieprieks = input("Vai esat piedalījies iepriekš? (jā/ne): ").lower()
        informacijas_avots = input("Kā uzzinājāt par pulciņu?: ")
        dati += (novirziens, pulcins, ieprieks, informacijas_avots)
        cursor.execute('''
        INSERT INTO pieteikumi (vards, uzvards, klase, novirziens, pulcins, ieprieks, informacijas_avots)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', dati)
        conn.commit()
        print("\nPaldies! Jūsu pieteikums tika saglabāts datubāzē.")
        break

pieteikties_pulcinam()
conn.close()