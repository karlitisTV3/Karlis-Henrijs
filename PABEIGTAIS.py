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
)
''')

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
)
''')

# Funkcija autentifikācijai
def autentifikacija():
    while True:
        print("\n== R6VSK Pulciņu Sistēma ==")
        print("1) Pieteikties pulciņam")
        print("2) Skatīt statistiku")
        print("3) Iziet")
        izvele = input("Tava izvēle - ")

        if izvele == "1":
            # Izsauc funkciju pieteikties
            pieteikties(cursor)
        elif izvele == "2":
            # Izsauc funkciju statistika
            statistika(cursor)
        elif izvele == "3":
            # Iziet no programmas
            print("Uz redzēšanos!")
            break
        else:
            # Apstrādā nederīgu izvēli
            print("Nederīga izvēle!")

def pieteikties(cursor):
    # Funkcija, lai pievienotu jaunu pieteikumu pulciņam
    epasts = input("Ievadiet savu skolas e-pastu: ")
    if "@edu.riga.lv" not in epasts:
        # Validē e-pasta adresi
        print("Nepareizs e-pasts!")
        return

    # Iegūst lietotāja informāciju
    vards = input("Vārds: ").strip()
    uzvards = input("Uzvārds: ").strip()
    klase = input("Klase: ").strip()

    if not all([vards, uzvards, klase]):
        # Pārbauda, vai visi lauki ir aizpildīti
        print("Visi lauki ir obligāti!")
        return

    # Iegūst pieejamo pulciņu sarakstu no datubāzes
    cursor.execute("SELECT * FROM pulcini")
    pulcini = cursor.fetchall()
    if not pulcini:
        # Ja nav pieejamu pulciņu
        print("Nav pieejamu pulciņu.")
        return

    # Parāda pieejamos pulciņus
    print("Pieejamie pulciņi:")
    for pulcins in pulcini:
        print(f"{pulcins[0]}. {pulcins[1]} - {pulcins[2]} ({pulcins[3]}, Kabinets: {pulcins[4]}, Pieejamas vietas: {pulcins[5]})")

    try:
        # Lietotājs izvēlas pulciņa ID
        pulcins_id = int(input("Izvēlieties pulciņa ID: "))
        izvēlētais_pulcins = next(p for p in pulcini if p[0] == pulcins_id)
    except (ValueError, StopIteration):
        # Apstrādā kļūdas, ja ievadīts nederīgs ID
        print("Nepareizs pulciņa ID!")
        return

    if izvēlētais_pulcins[5] <= 0:
        # Pārbauda, vai pulciņā ir pieejamas vietas
        print("Šis pulciņš ir pilns!")
        return

    # Iegūst papildu informāciju no lietotāja
    ieprieks = input("Vai esat piedalījies iepriekš? (jā/ne): ").lower()
    informacijas_avots = input("Kā uzzinājāt par pulciņu?: ").strip()

    # Pārbauda, vai lietotājs jau ir pieteicies šim pulciņam
    cursor.execute('SELECT * FROM pieteikumi WHERE vards = ? AND uzvards = ? AND pulcins_id = ?', (vards, uzvards, pulcins_id))
    if cursor.fetchone():
        print("Jūs jau esat pieteicies šim pulciņam!")
        return

    # Pievieno jaunu pieteikumu un atjaunina pieejamo vietu skaitu
    cursor.execute('''
    INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots))
    cursor.execute('UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?', (pulcins_id,))
    print(f"Pieteikums uz '{izvēlētais_pulcins[1]}' tika veiksmīgi pievienots!")

def statistika(cursor):
    # Parāda statistiku par pulciņiem, sakārtojot pēc pieteikumu skaita
    cursor.execute('''
    SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
    FROM pieteikumi
    JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
    GROUP BY pulcini.nosaukums
    ORDER BY pieteikumu_skaits DESC
    ''')
    popularitate = cursor.fetchall()
    print("Populārākie pulciņi:")
    for pulcins in popularitate:
        print(f"{pulcins[0]} - {pulcins[1]} pieteikumi")


if __name__ == "__main__":
    # Programmas sākumpunkts
    main()