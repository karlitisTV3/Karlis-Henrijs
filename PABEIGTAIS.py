import sqlite3

# Izveido savienojumu ar datubāzi un tabulas
conn = sqlite3.connect("pulcinu_pieteiksanas.db")
cursor = conn.cursor()

# Tabulu izveide
cursor.execute('''
CREATE TABLE IF NOT EXISTS pulcini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT,
    skolotajs TEXT,
    laiks TEXT,
    kabinets TEXT,
    pieejamas_vietas INTEGER
);''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pieteikumi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vards TEXT,
    uzvards TEXT,
    klase TEXT,
    pulcins_id INTEGER,
    ieprieks TEXT,
    informacijas_avots TEXT,
    FOREIGN KEY (pulcins_id) REFERENCES pulcini (id)
);
''')

# Funkcija autentifikācijai
def autentifikacija():
    while True:
        epasts = input("Ievadiet savu skolas e-pastu: ")
        if "@edu.riga.lv" not in epasts:
            print("Nepareizs e-pasts. Lūdzu, mēģiniet vēlreiz.\n")
        else:
            print("Autentifikācija veiksmīga!\n")
            break

# Funkcija pieteikumam
def pieteikties_pulcinam():
    autentifikacija()
    while True:
        print("== R6VSK Pulciņu Pieteikšanās ==")
        vards = input("Vārds: ").strip()
        uzvards = input("Uzvārds: ").strip()
        klase = input("Klase: ").strip()

        if not vards or not uzvards or not klase:
            print("Visi lauki ir obligāti. Lūdzu, mēģiniet vēlreiz.\n")
            continue

        cursor.execute("SELECT id, nosaukums, skolotajs, laiks, kabinets, pieejamas_vietas FROM pulcini")
        pulcini = cursor.fetchall()

        if not pulcini:
            print("Nav pieejamu pulciņu.\n")
            return

        print("Pieejamie pulciņi:")
        for pulcins in pulcini:
            print(f"{pulcins[0]}. {pulcins[1]} - {pulcins[2]} ({pulcins[3]}, Kabinets: {pulcins[4]}, Pieejamas vietas: {pulcins[5]})")

        try:
            pulcins_id = int(input("Izvēlieties pulciņa ID: "))
            izvēlētais_pulcins = next(p for p in pulcini if p[0] == pulcins_id)
        except (ValueError, StopIteration):
            print("Nepareizs pulciņa ID. Lūdzu, mēģiniet vēlreiz.\n")
            continue

        if izvēlētais_pulcins[5] <= 0:
            print("Šis pulciņš ir pilns. Lūdzu, izvēlieties citu.\n")
            continue

        ieprieks = input("Vai esat piedalījies iepriekš? (jā/ne): ").lower()
        informacijas_avots = input("Kā uzzinājāt par pulciņu?: ").strip()

        # Dubultu pieteikumu pārbaude
        cursor.execute('''
        SELECT * FROM pieteikumi WHERE vards = ? AND uzvards = ? AND pulcins_id = ?
        ''', (vards, uzvards, pulcins_id))
        if cursor.fetchone():
            print("Jūs jau esat pieteicies šim pulciņam.\n")
            continue

        # Saglabā pieteikumu
        cursor.execute('''
        INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots))
        conn.commit()

        # Atjaunina pieejamo vietu skaitu
        cursor.execute('''
        UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?
        ''', (pulcins_id,))
        conn.commit()

        print(f"\nPaldies! Jūsu pieteikums uz '{izvēlētais_pulcins[1]}' tika saglabāts.")
        print(f"Pulciņa informācija: {izvēlētais_pulcins[3]}, Kabinets: {izvēlētais_pulcins[4]}, Pasniedzējs: {izvēlētais_pulcins[2]}\n")
        break

# Funkcija statistikai
def statistika():
    print("== Pulciņu Statistika ==")
    cursor.execute('''
    SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
    FROM pieteikumi
    JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
    GROUP BY pulcini.nosaukums
    ORDER BY pieteikumu_skaits DESC
    ''')
    popularitate = cursor.fetchall()
    if not popularitate:
        print("Nav pieejamu datu par pulciņu statistiku.\n")
    else:
        print("Populārākie pulciņi:")
        for pulcins in popularitate:
            print(f"{pulcins[0]} - {pulcins[1]} pieteikumi")

# Galvenā izvēlne
def galvena_izvelne():
    while True:
        print("\n== R6VSK Pulciņu Sistēma ==")
        print("1. Pieteikties pulciņam")
        print("2. Skatīt statistiku")
        print("3. Iziet")
        izvele = input("Izvēlieties darbību: ").strip()

        if izvele == "1":
            pieteikties_pulcinam()
        elif izvele == "2":
            statistika()
        elif izvele == "3":
            print("Uz redzēšanos!")
            break
        else:
            print("Nepareiza izvēle. Lūdzu, mēģiniet vēlreiz.\n")

galvena_izvelne()
conn.close()