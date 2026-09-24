"""Vaste locaties van het mainframe.

Standaard staat alles in de map van deze repository. Met omgevingsvariabelen
kun je dat aanpassen:

- MAINFRAME_ARCHIEF: waar het archief staat, bijvoorbeeld een map in Google
  Drive zodat het automatisch wordt geback-upt.
- MAINFRAME_HOME: de basismap voor inbox en zoekindex (standaard de repository).

De zoekindex en de inbox blijven bewust buiten Google Drive: een database die
door een synchronisatiedienst wordt aangeraakt kan beschadigd raken, en
exportbestanden zijn groot en alleen tijdelijk nodig.
"""

from __future__ import annotations

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
    def inbox(self) -> Path:
        return self.basis / "inbox"

    @property
    def index(self) -> Path:
        return self.basis / ".mainframe" / "index.db"


def _map(waarde: str | Path) -> Path:
    return Path(waarde).expanduser().resolve()


def paden(basis: str | Path | None = None, archief: str | Path | None = None) -> Paden:
    """Bepaal de paden. Expliciete argumenten gaan voor omgevingsvariabelen."""
    if basis is None:
        basis = os.environ.get("MAINFRAME_HOME") or Path(__file__).resolve().parent.parent
    if archief is None:
        archief = os.environ.get("MAINFRAME_ARCHIEF") or None
    return Paden(_map(basis), _map(archief) if archief else None)
