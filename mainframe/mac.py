"""De automatische taak op de Mac mini (launchd).

`python3 -m mainframe taak installeer` zet een LaunchAgent klaar die
`python3 -m mainframe onderhoud` uitvoert:
- elke nacht op een vast tijdstip (standaard 03:00), en
- zodra er iets in `inbox/` verandert.

Een LaunchAgent draait als jouw gebruiker, na het inloggen. Dat is nodig,
want Google Drive voor desktop draait ook pas als je bent ingelogd.
"""

from __future__ import annotations

import os
import plistlib
import subprocess
import sys
from pathlib import Path

from mainframe.config import Paden, bewaar_instellingen

LABEL = "nl.mainframe.onderhoud"


def plist_pad() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def logbestand() -> Path:
    return Path.home() / "Library" / "Logs" / "mainframe.log"


def plist_inhoud(paden: Paden, python: str, uur: int, minuut: int) -> dict:
    omgeving = {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "PYTHONIOENCODING": "utf-8",
        "MAINFRAME_HOME": str(paden.basis),
    }
    repo = Path(__file__).resolve().parent.parent
    return {
        "Label": LABEL,
        "ProgramArguments": [python, "-m", "mainframe", "onderhoud"],
        "WorkingDirectory": str(repo),
        "EnvironmentVariables": omgeving,
        "StartCalendarInterval": {"Hour": uur, "Minute": minuut},
        "WatchPaths": [str(paden.inbox)],
        # Na een wijziging in de inbox minstens 5 minuten wachten met een nieuwe ronde.
        "ThrottleInterval": 300,
        "RunAtLoad": False,
        "StandardOutPath": str(logbestand()),
        "StandardErrorPath": str(logbestand()),
    }


def _launchctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["launchctl", *args], capture_output=True, text=True)


def _domein() -> str:
    return f"gui/{os.getuid()}"


def _alleen_mac() -> None:
    if sys.platform != "darwin":
        raise SystemExit("Deze opdracht werkt alleen op een Mac.")


def installeer(paden: Paden, tijd: str = "03:00") -> str:
    _alleen_mac()
    if paden.archief_map:
        # Leg de huidige archiefplek vast; de taak leest die uit het instellingenbestand.
        bewaar_instellingen(paden.basis, archief=str(paden.archief))
    uur, _, minuut = tijd.partition(":")
    inhoud = plist_inhoud(paden, sys.executable, int(uur), int(minuut or 0))
    pad = plist_pad()
    pad.parent.mkdir(parents=True, exist_ok=True)
    logbestand().parent.mkdir(parents=True, exist_ok=True)
    paden.inbox.mkdir(parents=True, exist_ok=True)
    _launchctl("bootout", f"{_domein()}/{LABEL}")  # oude versie eerst weg; fout is geen probleem
    with pad.open("wb") as f:
        plistlib.dump(inhoud, f)
    resultaat = _launchctl("bootstrap", _domein(), str(pad))
    if resultaat.returncode != 0:
        raise SystemExit(f"launchctl gaf een fout: {resultaat.stderr.strip()}")
    return (
        f"Taak geïnstalleerd: elke dag om {int(uur):02d}:{int(minuut or 0):02d} en bij nieuwe"
        f" bestanden in {paden.inbox}.\n"
        f"Archief: {paden.archief}\nLogboek: {logbestand()}\n"
        f"Nu meteen testen: python3 -m mainframe taak start"
    )


def verwijder() -> str:
    _alleen_mac()
    _launchctl("bootout", f"{_domein()}/{LABEL}")
    plist_pad().unlink(missing_ok=True)
    return "Taak verwijderd."


def start() -> str:
    _alleen_mac()
    resultaat = _launchctl("kickstart", f"{_domein()}/{LABEL}")
    if resultaat.returncode != 0:
        raise SystemExit("De taak is niet geïnstalleerd. Voer eerst `python3 -m mainframe taak installeer` uit.")
    return f"Onderhoud gestart. Volg het logboek met: tail -f {logbestand()}"


def status() -> str:
    _alleen_mac()
    regels = [f"Takenbestand: {plist_pad()} ({'aanwezig' if plist_pad().exists() else 'ontbreekt'})"]
    resultaat = _launchctl("print", f"{_domein()}/{LABEL}")
    if resultaat.returncode != 0:
        regels.append("De taak is niet actief.")
    else:
        for regel in resultaat.stdout.splitlines():
            regel = regel.strip()
            if regel.startswith(("state =", "last exit code =", "runs =")):
                regels.append(regel)
    if logbestand().exists():
        laatste = logbestand().read_text(encoding="utf-8", errors="replace").splitlines()[-15:]
        regels.append("--- laatste regels van het logboek ---")
        regels.extend(laatste)
    return "\n".join(regels)
