import sqlite3

def main():
    # Izveido savienojumu ar datubāzi un nodrošina, ka tā tiek aizvērta pēc lietošanas
    with sqlite3.connect("pulcinu_pieteiksanas_fixed.db") as conn:
        cursor = conn.cursor()
        parbauda_db(cursor)  # Pārbauda un izveido nepieciešamās tabulas datubāzē
        conn.commit()  # Commit after table creation
        izvele(cursor, conn)  # Sāk galveno izvēlni

def parbauda_db(cursor):
    # Izveido tabulu "pieteikumi", ja tā neeksistē
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pieteikumi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vards TEXT NOT NULL,
        uzvards TEXT NOT NULL,
        klase TEXT NOT NULL,
        pulcins_id INTEGER NOT NULL,
        ieprieks TEXT,
        informacijas_avots TEXT
    )
    """)
    # Izveido tabulu "pulcini", ja tā neeksistē
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pulcini (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nosaukums TEXT NOT NULL,
        skolotajs TEXT NOT NULL,
        laiks TEXT NOT NULL,
        kabinets TEXT NOT NULL,
        pieejamas_vietas INTEGER NOT NULL
    )
    """)

def izvele(cursor, conn):
    while True:
        print("\n== R6VSK Pulciņu Sistēma ==")
        print("1) Pieteikties pulciņam")  # Pieteikšanās pulciņam
        print("2) Skatīt statistiku")  # Skatīt pulciņu statistiku
        print("3) Skatīt pulciņu pieejamību")  # Skatīt pulciņu pieejamību
        print("4) Iziet")  # Iziet no programmas
        izvele = input("Tava izvēle - ")

        if izvele == "1":
            pieteikties(cursor, conn)  # Pass connection to pieteikties
        elif izvele == "2":
            statistika(cursor)  # Izsauc statistikas funkciju
        elif izvele == "3":
            skatīt_pieejamību(cursor)  # Izsauc pieejamības funkciju
        elif izvele == "4":
            print("Uz redzēšanos!")  # Izvada atvadu ziņu un pārtrauc ciklu
            break
        else:
            print("Nederīga izvēle!")  # Ziņo par nederīgu ievadi

def pieteikties(cursor, conn):
    # Pārbauda, vai ievadītais e-pasts ir derīgs
    epasts = input("Ievadiet savu skolas e-pastu: ")
    if "@edu.riga.lv" not in epasts:
        print("Nepareizs e-pasts!")
        return

    # Iegūst lietotāja datus
    vards = input("Vārds: ").strip()
    uzvards = input("Uzvārds: ").strip()
    klase = input("Klase: ").strip()

    # Pārbauda, vai visi lauki ir aizpildīti
    if not all([vards, uzvards, klase]):
        print("Visi lauki ir obligāti!")
        return

    # Iegūst visus pieejamos pulciņus no datubāzes
    cursor.execute("SELECT * FROM pulcini")
    pulcini = cursor.fetchall()
    if not pulcini:
        print("Nav pieejamu pulciņu.")  # Ziņo, ja nav pieejamu pulciņu
        return

    # Izvada pieejamos pulciņus
    print("Pieejamie pulciņi:")
    for pulcins in pulcini:
        print(f"{pulcins[0]}. {pulcins[1]} - {pulcins[2]} ({pulcins[3]}, Kabinets: {pulcins[4]}, Pieejamas vietas: {pulcins[5]})")

    # Pārbauda, vai izvēlētais pulciņa ID ir derīgs
    try:
        pulcins_id = int(input("Izvēlieties pulciņa ID: "))
        izvēlētais_pulcins = next(p for p in pulcini if p[0] == pulcins_id)
    except (ValueError, StopIteration):
        print("Nepareizs pulciņa ID!")
        return

    # Pārbauda, vai pulciņā ir pieejamas vietas
    if izvēlētais_pulcins[5] <= 0:
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

    try:
        # Pievieno jaunu pieteikumu datubāzē
        with conn:  # Use `with` to manage the transaction
            cursor.execute("""
            INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots))

            # Samazina pieejamo vietu skaitu izvēlētajā pulciņā
            cursor.execute('UPDATE pulcini SET pieejamas_vietas = pieejamas_vietas - 1 WHERE id = ?', (pulcins_id,))
        print(f"Pieteikums uz '{izvēlētais_pulcins[1]}' tika veiksmīgi pievienots!")
    except sqlite3.OperationalError as e:
        print(f"Kļūda: {e}")

def statistika(cursor):
    # Iegūst statistiku par pulciņiem un to pieteikumu skaitu
    cursor.execute("""
    SELECT pulcini.nosaukums, COUNT(pieteikumi.id) AS pieteikumu_skaits
    FROM pieteikumi
    JOIN pulcini ON pieteikumi.pulcins_id = pulcini.id
    GROUP BY pulcini.nosaukums
    ORDER BY pieteikumu_skaits DESC
    """)
    print("== Pulciņu Statistika ==")
    # Izvada statistiku par katru pulciņu
    for pulcins in cursor.fetchall():
        print(f"{pulcins[0]} - {pulcins[1]} pieteikumi")

def skatīt_pieejamību(cursor):
    # Iegūst visus pulciņus un to pieejamo vietu skaitu
    cursor.execute("SELECT nosaukums, pieejamas_vietas FROM pulcini")
    pulcini = cursor.fetchall()

    print("\n== Pulciņu Pieejamība ==")
    if not pulcini:
        print("Nav pieejamu pulciņu.")  # Ziņo, ja nav pieejamu pulciņu
    else:
        for pulcins in pulcini:
            print(f"{pulcins[0]} - Pieejamas vietas: {pulcins[1]}")

if __name__ == "__main__":
    main()  # Sāk programmas izpildi
