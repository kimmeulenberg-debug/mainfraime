"""Vaste locaties van het mainframe.

Standaard is de map waarin deze repository staat de basismap. Met de
omgevingsvariabele MAINFRAME_HOME kun je een andere map kiezen, bijvoorbeeld
een map die door Google Drive voor desktop wordt geback-upt.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Paden:
    basis: Path

    @property
    def archief(self) -> Path:
        return self.basis / "archief"

    @property
    def inbox(self) -> Path:
        return self.basis / "inbox"

    @property
    def index(self) -> Path:
        return self.basis / ".mainframe" / "index.db"


def paden(basis: str | Path | None = None) -> Paden:
    if basis is None:
        basis = os.environ.get("MAINFRAME_HOME") or Path(__file__).resolve().parent.parent
    return Paden(Path(basis).expanduser().resolve())
