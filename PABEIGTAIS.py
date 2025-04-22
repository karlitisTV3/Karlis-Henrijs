import sqlite3

def main():
    # Izveido savienojumu ar datubāzi
    with sqlite3.connect("pulcinu_pieteiksanas.db") as conn:
        cursor = conn.cursor()
        izvele(cursor)

def izvele(cursor):
    # Galvenā izvēlne
    while True:
        print("\n== R6VSK Pulciņu Sistēma ==")
        print("1) Pieteikties pulciņam")
        print("2) Skatīt statistiku")
        print("3) Iziet")
        izvele = input("Tava izvēle - ")

        if izvele == "1":
            pieteikties(cursor)
        elif izvele == "2":
            statistika(cursor)
        elif izvele == "3":
            print("Uz redzēšanos!")
            break
        else:
            print("Nederīga izvēle!")

def pieteikties(cursor):
    # Pievieno jaunu pieteikumu
    epasts = input("Ievadiet savu skolas e-pastu: ")
    if "@edu.riga.lv" not in epasts:
        print("Nepareizs e-pasts!")
        return

    vards = input("Vārds: ").strip()
    uzvards = input("Uzvārds: ").strip()
    klase = input("Klase: ").strip()

    if not all([vards, uzvards, klase]):
        print("Visi lauki ir obligāti!")
        return

    cursor.execute("SELECT * FROM pulcini")
    pulcini = cursor.fetchall()
    if not pulcini:
        print("Nav pieejamu pulciņu.")
        return

    print("Pieejamie pulciņi:")
    for pulcins in pulcini:
        print(f"{pulcins[0]}. {pulcins[1]} - {pulcins[2]} ({pulcins[3]}, Kabinets: {pulcins[4]}, Pieejamas vietas: {pulcins[5]})")

    try:
        pulcins_id = int(input("Izvēlieties pulciņa ID: "))
        izvēlētais_pulcins = next(p for p in pulcini if p[0] == pulcins_id)
    except (ValueError, StopIteration):
        print("Nepareizs pulciņa ID!")
        return

    if izvēlētais_pulcins[5] <= 0:
        print("Šis pulciņš ir pilns!")
        return

    ieprieks = input("Vai esat piedalījies iepriekš? (jā/ne): ").lower()
    informacijas_avots = input("Kā uzzinājāt par pulciņu?: ").strip()

    cursor.execute('SELECT * FROM pieteikumi WHERE vards = ? AND uzvards = ? AND pulcins_id = ?', (vards, uzvards, pulcins_id))
    if cursor.fetchone():
        print("Jūs jau esat pieteicies šim pulciņam!")
        return

    cursor.execute('''
    INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots))
    cursor.execute('UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?', (pulcins_id,))
    print(f"Pieteikums uz '{izvēlētais_pulcins[1]}' tika veiksmīgi pievienots!")

def statistika(cursor):
    # Parāda statistiku par pulciņiem
    cursor.execute('''
    SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
    FROM pieteikumi
    JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
    GROUP BY pulcini.nosaukums
    ORDER BY pieteikumu_skaits DESC
    ''')
    print("== Pulciņu Statistika ==")
    for pulcins in cursor.fetchall():
        print(f"{pulcins[0]} - {pulcins[1]} pieteikumi")

if __name__ == "__main__":
    main()