"""Het geheugen van Claude: een paar korte Markdown-bestanden met vaste context.

Het archief bevat wat er ooit is gezegd en geschreven. Het geheugen bevat wat
Claude altijd moet weten: wie je bent, wat er loopt en hoe je wilt werken.
Het staat in `<archief>/geheugen/`, zodat het meegaat in de back-up.
"""

from __future__ import annotations

import shutil
from pathlib import Path

SJABLONEN = Path(__file__).parent / "sjablonen" / "geheugen"


def zorg_voor_geheugen(map_: Path) -> list[Path]:
    """Maak ontbrekende geheugenbestanden aan vanuit de sjablonen. Bestaande blijven staan."""
    map_.mkdir(parents=True, exist_ok=True)
    nieuw = []
    for sjabloon in sorted(SJABLONEN.glob("*.md")):
        doel = map_ / sjabloon.name
        if not doel.exists():
            shutil.copyfile(sjabloon, doel)
            nieuw.append(doel)
    return nieuw


def toon(map_: Path) -> str:
    """Alle geheugenbestanden achter elkaar, met hun pad, om aan Claude te geven."""
    zorg_voor_geheugen(map_)
    blokken = []
    for pad in sorted(map_.glob("*.md")):
        blokken.append(f"===== {pad} =====\n{pad.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(blokken)
