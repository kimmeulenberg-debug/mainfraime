import io
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

from mainframe import archief, cli
from mainframe.importers import bestanden, chatgpt_export, claude_code, claude_export

FIXTURES = Path(__file__).parent / "fixtures"


class TijdelijkeMap(unittest.TestCase):
    def setUp(self):
        self.basis = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.basis)

    def cli(self, *argv):
        uitvoer = io.StringIO()
        with redirect_stdout(uitvoer):
            code = cli.main(["--basis", str(self.basis), *argv])
        return code, uitvoer.getvalue()


class ClaudeExportTest(TijdelijkeMap):
    def test_chats_en_projecten(self):
        items = {i.id: i for i in claude_export.importeer(FIXTURES / "claude")}
        chat = items["claude-chat-c1111111-aaaa-4bbb-8ccc-000000000001"]
        self.assertEqual(chat.project, "Informatieplan")
        self.assertIn("### Ik", chat.tekst)
        self.assertIn("Triple Aim", chat.tekst)
        self.assertIn("Wegiz en GALA", chat.tekst)
        self.assertIn("web_search", chat.tekst)
        self.assertEqual(items["claude-project-p2222222-aaaa-4bbb-8ccc-000000000002"].type, "project")
        self.assertIn("Common Ground", items["claude-projectdoc-d3333333"].tekst)
        # Lege gesprekken worden overgeslagen.
        self.assertEqual(len(items), 3)

    def test_leest_ook_zipbestand(self):
        zippad = self.basis / "export.zip"
        with zipfile.ZipFile(zippad, "w") as zf:
            zf.write(FIXTURES / "claude" / "conversations.json", "data-2025/conversations.json")
        items = list(claude_export.importeer(zippad))
        self.assertEqual(len(items), 1)
        self.assertIsNone(items[0].project)


class ChatGPTExportTest(unittest.TestCase):
    def test_volgt_zichtbare_tak(self):
        [chat] = chatgpt_export.importeer(FIXTURES / "chatgpt")
        self.assertIn("MedMij", chat.tekst)
        self.assertNotIn("VERWORPEN", chat.tekst)
        self.assertEqual(chat.aangemaakt.year, 2024)
        self.assertEqual(chat.origineel, "https://chatgpt.com/c/gpt-abc-123")


class ClaudeCodeTest(unittest.TestCase):
    def test_sessie(self):
        [sessie] = claude_code.importeer(FIXTURES / "claude-code")
        self.assertEqual(sessie.titel, "Basisframework mainframe opzetten")
        self.assertEqual(sessie.project, "mainfraime")
        self.assertIn("Ik maak de mappen aan.", sessie.tekst)
        self.assertNotIn("<meta>", sessie.tekst)
        self.assertNotIn("tool_result", sessie.tekst)


class BestandenTest(unittest.TestCase):
    def test_tekst_word_html_en_bijlage(self):
        items = {i.titel: i for i in bestanden.importeer(FIXTURES / "drive", bron="google-drive")}
        self.assertIn("NEN 7510", items["overleg"].tekst)
        self.assertEqual(items["overleg"].tags, ["Notities"])
        self.assertIn("Projectplan VIPP5", items["plan"].tekst)
        self.assertEqual(items["pagina"].tekst, "Werkafspraken&planning")
        self.assertEqual(items["logo"].type, "bestand")
        self.assertIsNotNone(items["logo"].bijlage_bron)


class ArchiefTest(TijdelijkeMap):
    def test_opnieuw_importeren_maakt_geen_dubbelen(self):
        item = next(chatgpt_export.importeer(FIXTURES / "chatgpt"))
        status, pad = archief.bewaar(item, self.basis)
        self.assertEqual(status, "nieuw")
        self.assertEqual(archief.bewaar(item, self.basis)[0], "ongewijzigd")
        item.titel = "Nieuwe titel"
        status, nieuw_pad = archief.bewaar(item, self.basis)
        self.assertEqual(status, "bijgewerkt")
        self.assertFalse(pad.exists())
        self.assertEqual(len(list(archief.alle_bestanden(self.basis))), 1)

    def test_kopblok_leest_terug(self):
        item = next(claude_export.importeer(FIXTURES / "claude"))
        item.titel = 'Titel met "aanhalingstekens": en dubbele punt'
        _, pad = archief.bewaar(item, self.basis)
        kop, tekst = archief.lees(pad)
        self.assertEqual(kop["titel"], item.titel)
        self.assertEqual(kop["id"], item.id)
        self.assertTrue(tekst.startswith("# Titel met"))


class CliTest(TijdelijkeMap):
    def test_importeren_en_zoeken(self):
        self.assertEqual(self.cli("importeer", "claude", str(FIXTURES / "claude"))[0], 0)
        self.assertEqual(self.cli("importeer", "chatgpt", str(FIXTURES / "chatgpt"))[0], 0)
        code, uitvoer = self.cli("importeer", "map", str(FIXTURES / "drive"), "--bron", "google-drive")
        self.assertEqual(code, 0)
        self.assertIn("4 nieuw", uitvoer)
        self.assertTrue(list((self.basis / "archief" / "google-drive").rglob("bijlagen/*_logo.png")))

        _, uitvoer = self.cli("zoek", "medmij")
        self.assertIn("PGO-koppelingen", uitvoer)
        # Zoeken werkt zonder accenten en met FTS-tekens in de zoekterm.
        _, uitvoer = self.cli("zoek", "vipp5", "AND", "(")
        self.assertIn("Niets gevonden", uitvoer)
        _, uitvoer = self.cli("zoek", "vipp5", "--bron", "google-drive")
        self.assertIn("plan", uitvoer)
        _, uitvoer = self.cli("zoek", "gegevensuitwisseling", "--project", "informatie")
        self.assertIn("Visie regionale", uitvoer)

        _, uitvoer = self.cli("status")
        self.assertIn("totaal", uitvoer)

    def test_status_leeg(self):
        self.assertIn("nog leeg", self.cli("status")[1])


if __name__ == "__main__":
    unittest.main()
