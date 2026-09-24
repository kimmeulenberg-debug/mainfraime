"""Import van een map met bestanden.

Bruikbaar voor elke bron die je als bestanden kunt exporteren:
- Google Drive (via Google Takeout of de map van Google Drive voor desktop)
- OneNote (secties geëxporteerd als Word-document of PDF)
- NotebookLM (notities die je als tekst of Google-document hebt bewaard)

Tekstbestanden en Word-documenten worden als doorzoekbare tekst opgeslagen.
Andere bestanden (pdf, afbeeldingen, spreadsheets) worden als bijlage
gekopieerd, met een archiefkaartje ernaast zodat ze wel vindbaar zijn op naam.
"""

from __future__ import annotations

import hashlib
import html
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

from mainframe.archief import Item

TEKST = {".md", ".txt", ".csv", ".json", ".py", ".js", ".ts", ".sql", ".yaml", ".yml"}
HTML = {".html", ".htm"}
WORD = {".docx"}
OVERSLAAN = {".ds_store", "desktop.ini", "thumbs.db"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def _docx_tekst(pad: Path) -> str:
    with zipfile.ZipFile(pad) as zf:
        boom = ElementTree.fromstring(zf.read("word/document.xml"))
    alineas = []
    for alinea in boom.iter(f"{W}p"):
        tekst = "".join(t.text or "" for t in alinea.iter(f"{W}t"))
        alineas.append(tekst)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(alineas)).strip()


def _html_tekst(tekst: str) -> str:
    tekst = re.sub(r"(?is)<(script|style).*?</\1>", "", tekst)
    tekst = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr)>", "\n", tekst)
    tekst = html.unescape(re.sub(r"<[^>]+>", "", tekst))
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", tekst).strip()


def _lees(pad: Path) -> str | None:
    """Geef de tekst van een bestand, of None als het een bijlage moet worden."""
    ext = pad.suffix.lower()
    try:
        if ext in TEKST:
            return pad.read_text(encoding="utf-8", errors="replace")
        if ext in HTML:
            return _html_tekst(pad.read_text(encoding="utf-8", errors="replace"))
        if ext in WORD:
            return _docx_tekst(pad)
    except (OSError, zipfile.BadZipFile, KeyError, ElementTree.ParseError):
        return None
    return None


def importeer(pad: Path, bron: str, project: str | None = None):
    pad = Path(pad)
    basis = pad if pad.is_dir() else pad.parent
    bestanden = [pad] if pad.is_file() else sorted(p for p in pad.rglob("*") if p.is_file())
    for bestand in bestanden:
        if bestand.name.lower() in OVERSLAAN or bestand.name.startswith("."):
            continue
        relatief = bestand.relative_to(basis).as_posix()
        moment = datetime.fromtimestamp(bestand.stat().st_mtime, tz=timezone.utc)
        tekst = _lees(bestand)
        submap = bestand.parent.relative_to(basis).as_posix()
        item = Item(
            id=f"{bron}-{hashlib.sha1(relatief.encode('utf-8')).hexdigest()}",
            bron=bron,
            type="document" if tekst is not None else "bestand",
            titel=bestand.stem,
            tekst=tekst if tekst is not None else f"Bijlage: `{bestand.name}`",
            aangemaakt=moment,
            gewijzigd=moment,
            project=project,
            tags=[submap] if submap != "." else [],
            origineel=relatief,
        )
        if tekst is None:
            item.bijlage_bron = bestand
        yield item
