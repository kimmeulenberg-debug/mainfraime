"""Zoekindex over het hele archief (SQLite FTS5, zit standaard in Python).

De index is afgeleid van de Markdown-bestanden en kan altijd opnieuw worden
opgebouwd. Hij staat daarom niet in Git.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from mainframe.archief import alle_bestanden, lees

SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS items USING fts5(
    titel, tekst, project, tags,
    id UNINDEXED, bron UNINDEXED, type UNINDEXED, datum UNINDEXED, pad UNINDEXED,
    tokenize = 'unicode61 remove_diacritics 2'
);
"""


@dataclass
class Treffer:
    titel: str
    bron: str
    type: str
    datum: str
    project: str
    pad: str
    fragment: str


def bouw_index(archief: Path, index: Path) -> int:
    index.parent.mkdir(parents=True, exist_ok=True)
    nieuw = index.with_suffix(".tmp")
    nieuw.unlink(missing_ok=True)
    db = sqlite3.connect(nieuw)
    db.executescript(SCHEMA)
    aantal = 0
    for bestand in alle_bestanden(archief):
        kop, tekst = lees(bestand)
        if "id" not in kop:
            continue
        db.execute(
            "INSERT INTO items (titel, tekst, project, tags, id, bron, type, datum, pad)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                kop.get("titel", ""),
                tekst,
                kop.get("project") or "",
                " ".join(kop.get("tags") or []),
                kop["id"],
                kop.get("bron", ""),
                kop.get("type", ""),
                (kop.get("aangemaakt") or "")[:10],
                bestand.relative_to(archief).as_posix(),
            ),
        )
        aantal += 1
    db.commit()
    db.close()
    nieuw.replace(index)
    return aantal


def _vraag(zoekterm: str) -> str:
    """Maak van gewone zoekwoorden een veilige FTS-vraag (alle woorden moeten voorkomen)."""
    woorden = re.findall(r'"[^"]+"|\S+', zoekterm)
    return " ".join('"' + w.strip('"').replace('"', "") + '"' for w in woorden if w.strip('"'))


def zoek(
    index: Path,
    zoekterm: str,
    bron: str | None = None,
    project: str | None = None,
    limiet: int = 20,
) -> list[Treffer]:
    if not index.exists():
        raise FileNotFoundError("Er is nog geen zoekindex. Voer eerst `python -m mainframe index` uit.")
    vraag = _vraag(zoekterm)
    if not vraag:
        return []
    sql = (
        "SELECT titel, bron, type, datum, project, pad,"
        " snippet(items, 1, '**', '**', '…', 16)"
        " FROM items WHERE items MATCH ?"
    )
    parameters: list = [vraag]
    if bron:
        sql += " AND bron = ?"
        parameters.append(bron)
    if project:
        sql += " AND project LIKE ?"
        parameters.append(f"%{project}%")
    sql += " ORDER BY bm25(items, 10.0, 1.0, 3.0, 3.0) LIMIT ?"
    parameters.append(limiet)
    with sqlite3.connect(index) as db:
        return [Treffer(*rij) for rij in db.execute(sql, parameters)]
