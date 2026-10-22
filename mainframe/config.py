"""Vaste locaties van het mainframe.

Standaard staat alles in de map van deze repository. De plek van het archief
(bijvoorbeeld een map in Google Drive) stel je eenmalig in met:

    python3 -m mainframe instellen --archief "<pad naar de map>"

Dat wordt bewaard in `.mainframe/instellingen.json` (niet in Git). Volgorde
van voorrang: optie op de opdrachtregel, dan omgevingsvariabele
MAINFRAME_ARCHIEF, dan het instellingenbestand, dan `<basis>/archief`.

De zoekindex en de inbox blijven bewust buiten Google Drive: een database die
door een synchronisatiedienst wordt aangeraakt kan beschadigd raken, en
exportbestanden zijn groot en alleen tijdelijk nodig.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paden:
    basis: Path
    archief_map: Path | None = None

    @property
    def archief(self) -> Path:
        return self.archief_map or self.basis / "archief"

    @property
    def geheugen(self) -> Path:
        # In het archief, zodat het meegaat in de back-up via Google Drive.
        return self.archief / "geheugen"

    @property
    def inbox(self) -> Path:
        return self.basis / "inbox"

    @property
    def index(self) -> Path:
        return self.basis / ".mainframe" / "index.db"

    @property
    def instellingen(self) -> Path:
        return self.basis / ".mainframe" / "instellingen.json"


def _map(waarde: str | Path) -> Path:
    return Path(waarde).expanduser().resolve()


def paden(basis: str | Path | None = None, archief: str | Path | None = None) -> Paden:
    """Bepaal de paden. Expliciete argumenten gaan voor omgevingsvariabelen."""
    if basis is None:
        basis = os.environ.get("MAINFRAME_HOME") or Path(__file__).resolve().parent.parent
    basis = _map(basis)
    if archief is None:
        archief = os.environ.get("MAINFRAME_ARCHIEF") or lees_instellingen(basis).get("archief")
    return Paden(basis, _map(archief) if archief else None)


def lees_instellingen(basis: Path) -> dict:
    pad = Paden(basis).instellingen
    try:
        return json.loads(pad.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def bewaar_instellingen(basis: Path, **waarden) -> Path:
    pad = Paden(basis).instellingen
    instellingen = lees_instellingen(basis)
    instellingen.update(waarden)
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(json.dumps(instellingen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return pad
