"""Hulpfuncties om exportbestanden (zip, map of los JSON-bestand) te openen."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path


class ExportFout(Exception):
    pass


def lees_json(pad: Path, bestandsnaam: str, verplicht: bool = True):
    """Zoek `bestandsnaam` in een zip, een uitgepakte map of als los bestand."""
    pad = Path(pad)
    if pad.is_file() and pad.suffix.lower() == ".zip":
        with zipfile.ZipFile(pad) as zf:
            kandidaten = [n for n in zf.namelist() if Path(n).name == bestandsnaam]
            if kandidaten:
                kandidaten.sort(key=len)
                return json.loads(zf.read(kandidaten[0]).decode("utf-8"))
    elif pad.is_dir():
        kandidaten = sorted(pad.rglob(bestandsnaam), key=lambda p: len(p.parts))
        if kandidaten:
            return json.loads(kandidaten[0].read_text(encoding="utf-8"))
    elif pad.is_file() and pad.name == bestandsnaam:
        return json.loads(pad.read_text(encoding="utf-8"))
    elif not pad.exists():
        raise ExportFout(f"Bestand of map niet gevonden: {pad}")

    if verplicht:
        raise ExportFout(f"Geen {bestandsnaam} gevonden in {pad}")
    return None


def gesprek_als_tekst(berichten: list[tuple[str, str]]) -> str:
    """Zet (spreker, tekst)-paren om naar leesbare Markdown."""
    blokken = []
    for spreker, tekst in berichten:
        tekst = tekst.strip()
        if tekst:
            blokken.append(f"### {spreker}\n\n{tekst}")
    return "\n\n".join(blokken)


def eerste_regel(tekst: str, max_lengte: int = 80) -> str:
    regel = next((r.strip() for r in tekst.splitlines() if r.strip()), "")
    return regel if len(regel) <= max_lengte else regel[: max_lengte - 1].rstrip() + "…"
