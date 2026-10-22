"""Automatisch verwerken van de inbox.

Zet exportbestanden in een submap van `inbox/` die naar de bron heet:

    inbox/claude/        zip of map van de Claude.ai-export
    inbox/chatgpt/       zip of map van de ChatGPT-export
    inbox/google-drive/  Google Takeout (zip of uitgepakte map)
    inbox/onenote/       geëxporteerde OneNote-secties
    inbox/<andere-bron>/ elke andere map met bestanden

Een Claude- of ChatGPT-zip mag ook direct in `inbox/` staan; die wordt dan
herkend aan de inhoud. Na een geslaagde import verhuist alles naar
`inbox/verwerkt/<datum>/<bron>/`. Bij een fout blijft het staan en meldt het
verslag wat er misging.
"""

from __future__ import annotations

import re
import shutil
import tempfile
import time
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from mainframe import archief
from mainframe.config import Paden
from mainframe.importers import bestanden, chatgpt_export, claude_export
from mainframe.importers._export import ExportFout, lees_json

VERWERKT = "verwerkt"
# Namen die geen bron mogen zijn, omdat ze een eigen betekenis hebben.
GERESERVEERD = {VERWERKT, "geheugen"}
BEZIG = {".crdownload", ".part", ".download", ".tmp"}
# Bestanden die minder dan zo lang geleden zijn gewijzigd, worden mogelijk nog
# gedownload of gesynchroniseerd. Die slaan we deze ronde over.
RUSTTIJD_SECONDEN = 120


@dataclass
class Verslag:
    telling: Counter = field(default_factory=Counter)
    verwerkt: list[str] = field(default_factory=list)
    wacht: list[str] = field(default_factory=list)
    fouten: list[str] = field(default_factory=list)

    def regels(self) -> list[str]:
        uit = []
        for naam in self.verwerkt:
            uit.append(f"Verwerkt: {naam}")
        for naam in self.wacht:
            uit.append(f"Wacht nog (bestand is net gewijzigd): {naam}")
        for fout in self.fouten:
            uit.append(f"Fout: {fout}")
        if not (self.verwerkt or self.wacht or self.fouten):
            uit.append("Inbox is leeg.")
        return uit


def geldige_bron(naam: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9][a-z0-9-]*", naam)) and naam not in GERESERVEERD


def herken_chatexport(pad: Path) -> str | None:
    """Zeg of een export van Claude of van ChatGPT is, aan de hand van de inhoud."""
    try:
        gesprekken = lees_json(pad, "conversations.json", verplicht=False)
    except (ExportFout, ValueError, zipfile.BadZipFile, OSError):
        return None
    if not isinstance(gesprekken, list) or not gesprekken:
        return None
    eerste = gesprekken[0]
    if "mapping" in eerste:
        return "chatgpt"
    if "chat_messages" in eerste:
        return "claude"
    return None


def _items(pad: Path, bron: str, werkmap: Path):
    if bron == "claude":
        return claude_export.importeer(pad)
    if bron == "chatgpt":
        return chatgpt_export.importeer(pad)
    # Het id van een bestand volgt uit zijn pad binnen de export. Of je een
    # Takeout-zip neerzet of de uitgepakte map: het pad begint in beide gevallen
    # met "Takeout/...", zodat een nieuwe export hetzelfde stuk bijwerkt.
    if pad.is_file() and pad.suffix.lower() == ".zip":
        with zipfile.ZipFile(pad) as zf:
            zf.extractall(werkmap)
        return bestanden.importeer(werkmap, bron=bron)
    return bestanden.importeer(pad, bron=bron, basis=pad.parent)


def _is_rustig(pad: Path, nu: float) -> bool:
    if pad.is_file():
        return nu - pad.stat().st_mtime >= RUSTTIJD_SECONDEN
    return all(nu - p.stat().st_mtime >= RUSTTIJD_SECONDEN for p in pad.rglob("*") if p.is_file())


def _verplaats(pad: Path, doelmap: Path) -> None:
    doelmap.mkdir(parents=True, exist_ok=True)
    doel = doelmap / pad.name
    teller = 2
    while doel.exists():
        doel = doelmap / f"{pad.stem}-{teller}{pad.suffix}"
        teller += 1
    shutil.move(str(pad), str(doel))


def _kandidaten(inbox: Path):
    """Geef (bron, pad)-paren. Bron None betekent: herkennen aan de inhoud."""
    for pad in sorted(inbox.iterdir()):
        if pad.name.startswith(".") or pad.name == VERWERKT:
            continue
        if pad.is_dir() and geldige_bron(pad.name):
            for deel in sorted(pad.iterdir()):
                if not deel.name.startswith("."):
                    yield pad.name, deel
        else:
            yield None, pad


def verwerk(paden: Paden, nu: float | None = None) -> Verslag:
    nu = time.time() if nu is None else nu
    verslag = Verslag()
    paden.inbox.mkdir(parents=True, exist_ok=True)
    vandaag = date.fromtimestamp(nu).isoformat()

    for bron, pad in _kandidaten(paden.inbox):
        naam = pad.relative_to(paden.inbox).as_posix()
        if pad.suffix.lower() in BEZIG or not _is_rustig(pad, nu):
            verslag.wacht.append(naam)
            continue
        if bron is None:
            bron = herken_chatexport(pad)
            if bron is None:
                verslag.fouten.append(
                    f"{naam}: onbekende export. Zet hem in een submap met de naam van de bron,"
                    " bijvoorbeeld inbox/google-drive/."
                )
                continue
        try:
            with tempfile.TemporaryDirectory() as werkmap:
                for item in _items(pad, bron, Path(werkmap)):
                    status, _ = archief.bewaar(item, paden.archief)
                    verslag.telling[status] += 1
        except (ExportFout, ValueError, zipfile.BadZipFile, OSError) as fout:
            verslag.fouten.append(f"{naam}: {fout}")
            continue
        _verplaats(pad, paden.inbox / VERWERKT / vandaag / bron)
        verslag.verwerkt.append(f"{naam} ({bron})")
    return verslag
