import unittest
import sqlite3
import sys  # Ensure sys is imported for stdout redirection
from pulcinu_sistema_fixed import parbauda_db, pieteikties, statistika

class TestPulcinuSistema(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")  # Izveido in-memory datubāzi
        self.cursor = self.conn.cursor()
        parbauda_db(self.cursor)  # Inicializē tabulas

    def tearDown(self):
        self.conn.close()  # Aizver datubāzes savienojumu

    def test_parbauda_db(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in self.cursor.fetchall()}
        assert "pieteikumi" in tables
        assert "pulcini" in tables

    def test_pieteikties(self):
        self.cursor.execute("""
        INSERT INTO pulcini (nosaukums, skolotajs, laiks, kabinets, pieejamas_vietas)
        VALUES ('Datorika', 'Jānis Bērziņš', 'Pirmdiena 15:00', '101', 10)
        """)
        self.conn.commit()

        inputs = iter(["test@edu.riga.lv", "Karlis", "Henrijs", "12.a", "1", "nē", "Draugs"])
        __builtins__.input = lambda _: next(inputs)  # Mock input

        try:
            pieteikties(self.cursor)
        finally:
            __builtins__.input = input  # Atjauno input

        self.cursor.execute("SELECT * FROM pieteikumi")
        pieteikumi = self.cursor.fetchall()
        assert len(pieteikumi) == 1
        assert pieteikumi[0][1] == "Karlis"
        assert pieteikumi[0][2] == "Henrijs"

    def test_statistika(self):
        self.cursor.execute("""
        INSERT INTO pulcini (nosaukums, skolotajs, laiks, kabinets, pieejamas_vietas)
        VALUES ('Datorika', 'Jānis Bērziņš', 'Pirmdiena 15:00', '101', 10)
        """)
        self.cursor.execute("""
        INSERT INTO pieteikumi (vards, uzvards, klase, pulcins_id, ieprieks, informacijas_avots)
        VALUES ('Karlis', 'Henrijs', '12.a', 1, 'nē', 'Draugs')
        """)
        self.conn.commit()

        import io
        captured_output = io.StringIO()
        sys.stdout = captured_output  # Pārvērš stdout uz StringIO

        try:
            statistika(self.cursor)
        finally:
            sys.stdout = sys.__stdout__  # Atjauno stdout

        assert "Datorika - 1 pieteikumi" in captured_output.getvalue()

if __name__ == "__main__":
    unittest.main()