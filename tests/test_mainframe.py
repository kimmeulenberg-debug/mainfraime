import io
import os
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from mainframe import archief, cli, config, geheugen, inbox, mac
from mainframe.importers import bestanden, chatgpt_export, claude_code, claude_export

FIXTURES = Path(__file__).parent / "fixtures"


class TijdelijkeMap(unittest.TestCase):
    def setUp(self):
        self.basis = Path(tempfile.mkdtemp()).resolve()  # macOS: /var is een snelkoppeling

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


class EigenArchiefOverslaanTest(TijdelijkeMap):
    def test_archief_in_drive_export_wordt_overgeslagen(self):
        drive = self.basis / "Drive"
        shutil.copytree(FIXTURES / "drive", drive)
        for item in chatgpt_export.importeer(FIXTURES / "chatgpt"):
            archief.bewaar(item, drive / "Mainframe-archief")
        titels = {i.titel for i in bestanden.importeer(drive, bron="google-drive")}
        self.assertEqual(titels, {"overleg", "pagina", "plan", "logo"})


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

    def test_archief_op_aparte_locatie(self):
        drive = self.basis / "Google Drive" / "Mainframe-archief"
        code, _ = self.cli("--archief", str(drive), "importeer", "chatgpt", str(FIXTURES / "chatgpt"))
        self.assertEqual(code, 0)
        self.assertEqual(len(list(drive.rglob("*.md"))), 1)
        self.assertFalse((self.basis / "archief").exists())
        # De zoekindex blijft lokaal, buiten de gesynchroniseerde map.
        self.assertTrue((self.basis / ".mainframe" / "index.db").exists())
        self.assertFalse(list(drive.rglob("*.db")))
        _, uitvoer = self.cli("--archief", str(drive), "zoek", "medmij")
        self.assertIn("PGO-koppelingen", uitvoer)

    def test_status_leeg(self):
        self.assertIn("nog leeg", self.cli("status")[1])


def _maak_oud(pad: Path):
    """Zet de wijzigingstijd ruim in het verleden, zodat de inbox het bestand niet als 'bezig' ziet."""
    oud = 1_700_000_000
    for p in [pad, *pad.rglob("*")] if pad.is_dir() else [pad]:
        os.utime(p, (oud, oud))


class InboxTest(TijdelijkeMap):
    def setUp(self):
        super().setUp()
        self.paden = config.paden(self.basis)
        self.inbox = self.paden.inbox

    def zip_van(self, map_: Path, doel: Path, voorvoegsel: str = "") -> Path:
        doel.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(doel, "w") as zf:
            for p in map_.rglob("*"):
                if p.is_file():
                    zf.write(p, voorvoegsel + p.relative_to(map_).as_posix())
        _maak_oud(doel)
        return doel

    def test_herkent_chatexports_in_de_hoofdmap(self):
        self.zip_van(FIXTURES / "claude", self.inbox / "data-claude.zip")
        self.zip_van(FIXTURES / "chatgpt", self.inbox / "chatgpt-export.zip")
        verslag = inbox.verwerk(self.paden)
        self.assertEqual(verslag.fouten, [])
        self.assertEqual(len(verslag.verwerkt), 2)
        self.assertEqual(verslag.telling["nieuw"], 4)
        verwerkt = list((self.inbox / "verwerkt").rglob("*.zip"))
        self.assertEqual({p.parent.name for p in verwerkt}, {"claude", "chatgpt"})
        self.assertFalse(list(self.inbox.glob("*.zip")))

    def test_submap_bepaalt_de_bron_en_zip_en_map_geven_hetzelfde_id(self):
        self.zip_van(FIXTURES / "drive", self.inbox / "google-drive" / "takeout-1.zip", "Takeout/Drive/")
        inbox.verwerk(self.paden)
        ids_zip = {archief.lees(p)[0]["id"] for p in archief.alle_bestanden(self.paden.archief)}
        self.assertEqual(len(ids_zip), 4)

        uitgepakt = self.inbox / "google-drive" / "Takeout" / "Drive"
        shutil.copytree(FIXTURES / "drive", uitgepakt)
        _maak_oud(self.inbox / "google-drive" / "Takeout")
        verslag = inbox.verwerk(self.paden)
        self.assertEqual(verslag.telling["nieuw"], 0)
        ids_map = {archief.lees(p)[0]["id"] for p in archief.alle_bestanden(self.paden.archief)}
        self.assertEqual(ids_zip, ids_map)

    def test_onderdelen_in_onenote_submap_worden_tags(self):
        doel = self.inbox / "onenote" / "Persoonlijk"
        shutil.copytree(FIXTURES / "drive" / "Notities", doel)
        _maak_oud(doel)
        inbox.verwerk(self.paden)
        [stuk] = archief.alle_bestanden(self.paden.archief)
        kop, _ = archief.lees(stuk)
        self.assertEqual((kop["bron"], kop["tags"]), ("onenote", ["Persoonlijk"]))

    def test_wacht_op_bestanden_die_nog_binnenkomen(self):
        (self.inbox / "chatgpt").mkdir(parents=True)
        shutil.copy(FIXTURES / "chatgpt" / "conversations.json", self.inbox / "chatgpt" / "conversations.json")
        (self.inbox / "export.zip.crdownload").write_bytes(b"")
        verslag = inbox.verwerk(self.paden)
        self.assertEqual(len(verslag.wacht), 2)
        self.assertEqual(verslag.verwerkt, [])

    def test_onbekend_bestand_blijft_staan_met_melding(self):
        onbekend = self.inbox / "losse-notitie.txt"
        onbekend.parent.mkdir(parents=True)
        onbekend.write_text("hallo")
        _maak_oud(onbekend)
        verslag = inbox.verwerk(self.paden)
        self.assertEqual(len(verslag.fouten), 1)
        self.assertTrue(onbekend.exists())

    def test_kapotte_zip_blijft_staan(self):
        kapot = self.inbox / "claude" / "kapot.zip"
        kapot.parent.mkdir(parents=True)
        kapot.write_bytes(b"geen zip")
        _maak_oud(kapot)
        verslag = inbox.verwerk(self.paden)
        self.assertEqual(len(verslag.fouten), 1)
        self.assertTrue(kapot.exists())


class GeheugenTest(TijdelijkeMap):
    def test_sjablonen_en_bestaande_bestanden_blijven_staan(self):
        map_ = self.basis / "archief" / "geheugen"
        map_.mkdir(parents=True)
        (map_ / "over-mij.md").write_text("# Over mij\n\nEigen tekst")
        nieuw = geheugen.zorg_voor_geheugen(map_)
        self.assertEqual({p.name for p in nieuw}, {"projecten.md", "voorkeuren.md"})
        self.assertIn("Eigen tekst", geheugen.toon(map_))

    def test_geheugen_telt_niet_mee_als_archiefstuk(self):
        self.cli("geheugen")
        self.cli("importeer", "chatgpt", str(FIXTURES / "chatgpt"))
        self.assertEqual(len(list(archief.alle_bestanden(self.basis / "archief"))), 1)
        self.assertNotIn("?", self.cli("status")[1])

    def test_geheugen_is_geen_geldige_bron(self):
        with mock.patch("sys.stderr", io.StringIO()):
            code, _ = self.cli("importeer", "map", str(FIXTURES / "drive"), "--bron", "geheugen")
        self.assertEqual(code, 2)


class OnderhoudTest(TijdelijkeMap):
    def test_onderhoud_doet_sessies_inbox_en_index(self):
        thuis = self.basis / "thuis"
        shutil.copytree(FIXTURES / "claude-code", thuis / ".claude" / "projects")
        zip_ = self.basis / "inbox" / "chatgpt" / "export.zip"
        zip_.parent.mkdir(parents=True)
        with zipfile.ZipFile(zip_, "w") as zf:
            zf.write(FIXTURES / "chatgpt" / "conversations.json", "conversations.json")
        _maak_oud(zip_)
        (self.basis / "archief").mkdir()
        with mock.patch.object(claude_code, "STANDAARD_MAP", thuis / ".claude" / "projects"):
            code, uitvoer = self.cli("onderhoud")
        self.assertEqual(code, 0, uitvoer)
        self.assertIn("Claude Code-sessies: 1 nieuw", uitvoer)
        self.assertIn("Zoekindex bijgewerkt (2 items)", uitvoer)

    def test_onderhoud_stopt_als_archief_onbereikbaar_is(self):
        with mock.patch("sys.stderr", io.StringIO()):
            code, _ = self.cli("--archief", str(self.basis / "bestaat-niet"), "onderhoud")
        self.assertEqual(code, 1)


class InstellenTest(TijdelijkeMap):
    def test_archiefplek_wordt_onthouden(self):
        drive = self.basis / "Mijn Drive" / "Mainframe-archief"
        drive.parent.mkdir()
        with mock.patch.dict(os.environ, {}, clear=False) as omgeving:
            omgeving.pop("MAINFRAME_ARCHIEF", None)
            code, uitvoer = self.cli("instellen", "--archief", str(drive))
            self.assertEqual(code, 0)
            self.assertTrue(drive.is_dir())
            self.cli("importeer", "chatgpt", str(FIXTURES / "chatgpt"))
            self.assertEqual(len(list(drive.rglob("*.md"))), 1)
            # De omgevingsvariabele gaat voor.
            omgeving["MAINFRAME_ARCHIEF"] = str(self.basis / "anders")
            self.assertEqual(config.paden(self.basis).archief, self.basis / "anders")


class MacTaakTest(unittest.TestCase):
    def test_plist(self):
        paden = config.paden("/Users/kim/Mainframe & co")
        inhoud = mac.plist_inhoud(paden, "/usr/local/bin/python3", 3, 0)
        self.assertEqual(inhoud["ProgramArguments"], ["/usr/local/bin/python3", "-m", "mainframe", "onderhoud"])
        self.assertEqual(inhoud["StartCalendarInterval"], {"Hour": 3, "Minute": 0})
        self.assertEqual(inhoud["WatchPaths"], [str(paden.inbox)])
        # Het archief komt uit het instellingenbestand, zodat `instellen` ook later nog werkt.
        self.assertNotIn("MAINFRAME_ARCHIEF", inhoud["EnvironmentVariables"])
        self.assertEqual(inhoud["EnvironmentVariables"]["MAINFRAME_HOME"], str(paden.basis))
        # plistlib zorgt voor correcte XML, ook met spaties en '&' in paden.
        import plistlib
        self.assertEqual(plistlib.loads(plistlib.dumps(inhoud)), inhoud)


if __name__ == "__main__":
    unittest.main()
