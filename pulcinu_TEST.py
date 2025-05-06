import unittest
import sqlite3
from pulcinu_sistema_fixed import parbauda_db, pieteikties, statistika

class TestPulcinuSistema(unittest.TestCase):
    def setUp(self):
        # Izveido in-memory datubāzi un inicializē tabulas
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        parbauda_db(self.cursor)

    def tearDown(self):
        # Aizver datubāzes savienojumu
        self.conn.close()

    def test_parbauda_db(self):
        # Pārbauda, vai tabulas tika izveidotas
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in self.cursor.fetchall()}
        self.assertIn("pieteikumi", tables)
        self.assertIn("pulcini", tables)

    def test_pieteikties(self):
        # Pievieno testu datus
        self.cursor.execute("""
        INSERT INTO pulcini (nosaukums, skolotajs, laiks, kabinets, pieejamas_vietas)
        VALUES ('Datorika', 'Jānis Bērziņš', 'Pirmdiena 15:00', '101', 10)
        """)
        self.conn.commit()

        # Simulē ievadi un pārbauda pieteikumu
        inputs = iter(["test@edu.riga.lv", "Karlis", "Henrijs", "12.a", "1", "nē", "Draugs"])
        def mock_input(prompt):
            return next(inputs)

        original_input = __builtins__.input
        __builtins__.input = mock_input
        try:
            pieteikties(self.cursor)
        finally:
            __builtins__.input = original_input

        self.cursor.execute("SELECT * FROM pieteikumi")
        pieteikumi = self.cursor.fetchall()
        self.assertEqual(len(pieteikumi), 1)
        self.assertEqual(pieteikumi[0][1], "Karlis")
        self.assertEqual(pieteikumi[0][2], "Henrijs")

    def test_statistika(self):
        # Pievieno testu datus
        self.cursor.execute("""
        INSERT INTO pulcini (nosaukums, skolotajs, laiks, kabinets, pieejamas_vietas)
        VALUES ('Datorika', 'Jānis Bērziņš', 'Pirmdiena 15:00', '101', 10)
        """)
        self.cursor.execute("""
        INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
        VALUES ('Karlis', 'Henrijs', '12.a', 1, 'nē', 'Draugs')
        """)
        self.conn.commit()

        # Pārbauda statistikas izvadi
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            statistika(self.cursor)
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Datorika - 1 pieteikumi", output)

if __name__ == "__main__":
    unittest.main()