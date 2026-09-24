"""Het archiefformaat: één Markdown-bestand per archiefstuk.

Elk bestand begint met een kopblok (frontmatter) tussen twee regels `---`.
Iedere regel daarin heeft de vorm `sleutel: <JSON-waarde>`. Dat is geldige
YAML, dus ook leesbaar voor andere tools (Obsidian, VS Code), terwijl we het
zonder extra bibliotheken betrouwbaar kunnen inlezen.

Zie docs/archiefformaat.md voor de uitleg van alle velden.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Item:
    id: str
    bron: str
    type: str
    titel: str
    tekst: str
    aangemaakt: datetime | None = None
    gewijzigd: datetime | None = None
    project: str | None = None
    tags: list[str] = field(default_factory=list)
    origineel: str | None = None
    bijlage: str | None = None
    # Los bestand (pdf, afbeelding) dat als bijlage naast het item wordt bewaard.
    bijlage_bron: Path | None = None

    @property
    def kort_id(self) -> str:
        return hashlib.sha1(self.id.encode("utf-8")).hexdigest()[:10]


def slug(tekst: str, max_lengte: int = 60) -> str:
    tekst = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode("ascii")
    tekst = re.sub(r"[^a-zA-Z0-9]+", "-", tekst).strip("-").lower()
    return tekst[:max_lengte].rstrip("-") or "zonder-titel"


def tijd(waarde) -> datetime | None:
    """Zet een tijdstempel uit een export (ISO-tekst of epoch) om naar UTC."""
    if waarde is None or waarde == "":
        return None
    if isinstance(waarde, datetime):
        dt = waarde
    elif isinstance(waarde, (int, float)):
        dt = datetime.fromtimestamp(waarde, tz=timezone.utc)
    else:
        tekst = str(waarde).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(tekst)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime | None) -> str | None:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else None


def naar_markdown(item: Item) -> str:
    waarden = {
        "id": item.id,
        "bron": item.bron,
        "type": item.type,
        "titel": item.titel,
        "aangemaakt": _iso(item.aangemaakt),
        "gewijzigd": _iso(item.gewijzigd),
        "project": item.project,
        "tags": sorted(set(item.tags)),
        "origineel": item.origineel,
        "bijlage": item.bijlage,
    }
    regels = ["---"]
    for sleutel, waarde in waarden.items():
        if waarde in (None, []):
            continue
        regels.append(f"{sleutel}: {json.dumps(waarde, ensure_ascii=False)}")
    regels.append("---")
    regels.append("")
    regels.append(f"# {item.titel}")
    regels.append("")
    regels.append(item.tekst.strip())
    return "\n".join(regels) + "\n"


def lees(pad: Path) -> tuple[dict, str]:
    """Lees een archiefbestand in: (kopgegevens, tekst)."""
    inhoud = pad.read_text(encoding="utf-8")
    if not inhoud.startswith("---\n"):
        return {}, inhoud
    kop, _, tekst = inhoud[4:].partition("\n---\n")
    gegevens = {}
    for regel in kop.splitlines():
        sleutel, sep, waarde = regel.partition(": ")
        if sep:
            try:
                gegevens[sleutel] = json.loads(waarde)
            except json.JSONDecodeError:
                gegevens[sleutel] = waarde
    return gegevens, tekst.lstrip("\n")


# Markeringsbestand in de hoofdmap van het archief. Als het archief in Google
# Drive staat en later via Takeout wordt geëxporteerd, herkent de importer zo
# de eigen archiefmap en slaat die over.
MARKERING = ".mainframe-archief"


def map_voor(item: Item, archief: Path) -> Path:
    jaar = item.aangemaakt.strftime("%Y") if item.aangemaakt else "onbekend"
    return archief / item.bron / jaar


def bewaar(item: Item, archief: Path) -> tuple[str, Path]:
    """Schrijf een item weg. Geeft ('nieuw' | 'bijgewerkt' | 'ongewijzigd', pad).

    De bestandsnaam bevat een kort id, zodat opnieuw importeren hetzelfde
    bestand bijwerkt in plaats van een dubbel te maken, ook als de titel
    intussen is veranderd.
    """
    doelmap = map_voor(item, archief)
    doelmap.mkdir(parents=True, exist_ok=True)
    markering = archief / MARKERING
    if not markering.exists():
        markering.write_text("Dit is een Mainframe-archief. Niet opnieuw importeren.\n", encoding="utf-8")
    datum = item.aangemaakt.strftime("%Y-%m-%d") if item.aangemaakt else "0000-00-00"
    pad = doelmap / f"{datum}_{item.kort_id}_{slug(item.titel)}.md"
    if item.bijlage_bron:
        bijlage = doelmap / "bijlagen" / f"{item.kort_id}_{item.bijlage_bron.name}"
        bron = item.bijlage_bron.stat()
        if not bijlage.exists() or (bijlage.stat().st_size, bijlage.stat().st_mtime) != (bron.st_size, bron.st_mtime):
            bijlage.parent.mkdir(exist_ok=True)
            shutil.copy2(item.bijlage_bron, bijlage)
        item.bijlage = bijlage.relative_to(doelmap).as_posix()
    inhoud = naar_markdown(item)

    # Zoek in alle jaarmappen van deze bron: de datum kan bij een nieuwe import verschoven zijn.
    bestaande = [p for p in (archief / item.bron).glob(f"*/*_{item.kort_id}_*.md") if p != pad]
    if pad.exists():
        status = "ongewijzigd" if pad.read_text(encoding="utf-8") == inhoud else "bijgewerkt"
    else:
        status = "bijgewerkt" if bestaande else "nieuw"
    for oud in bestaande:
        oud.unlink()
        if oud.parent != doelmap:
            for bijlage in (oud.parent / "bijlagen").glob(f"{item.kort_id}_*"):
                bijlage.unlink()
    if status != "ongewijzigd":
        pad.write_text(inhoud, encoding="utf-8")
    return status, pad


def alle_bestanden(archief: Path):
    yield from sorted(p for p in archief.rglob("*.md") if p.parent.name != "bijlagen")
