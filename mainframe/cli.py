"""Opdrachtregel van het mainframe.

Voorbeelden:
    python -m mainframe importeer claude inbox/claude-export.zip
    python -m mainframe importeer chatgpt inbox/chatgpt-export.zip
    python -m mainframe importeer claude-code
    python -m mainframe importeer map inbox/takeout/Drive --bron google-drive
    python -m mainframe zoek "regie op gegevens"
    python -m mainframe status
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter

from mainframe import archief, config, zoeken
from mainframe.importers import bestanden, chatgpt_export, claude_code, claude_export
from mainframe.importers._export import ExportFout


def _importeer(args, paden: config.Paden) -> int:
    if args.soort in ("claude", "chatgpt") and not args.pad:
        print("Geef het pad naar het exportbestand (zip of map) op.", file=sys.stderr)
        return 2
    if args.soort == "claude":
        items = claude_export.importeer(args.pad)
    elif args.soort == "chatgpt":
        items = chatgpt_export.importeer(args.pad)
    elif args.soort == "claude-code":
        items = claude_code.importeer(args.pad)
    else:
        if not args.pad:
            print("Geef de map op die je wilt importeren.", file=sys.stderr)
            return 2
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.bron):
            print("Gebruik voor --bron alleen kleine letters, cijfers en '-'.", file=sys.stderr)
            return 2
        items = bestanden.importeer(args.pad, bron=args.bron, project=args.project)

    telling: Counter[str] = Counter()
    try:
        for item in items:
            status, _ = archief.bewaar(item, paden.archief)
            telling[status] += 1
    except ExportFout as fout:
        print(f"Fout: {fout}", file=sys.stderr)
        return 1

    print(
        f"Klaar: {telling['nieuw']} nieuw, {telling['bijgewerkt']} bijgewerkt,"
        f" {telling['ongewijzigd']} ongewijzigd."
    )
    if not args.geen_index:
        aantal = zoeken.bouw_index(paden.archief, paden.index)
        print(f"Zoekindex bijgewerkt ({aantal} items).")
    return 0


def _zoek(args, paden: config.Paden) -> int:
    try:
        treffers = zoeken.zoek(
            paden.index, " ".join(args.termen), bron=args.bron, project=args.project, limiet=args.aantal
        )
    except FileNotFoundError as fout:
        print(fout, file=sys.stderr)
        return 1
    if not treffers:
        print("Niets gevonden.")
        return 0
    for t in treffers:
        project = f" · {t.project}" if t.project else ""
        print(f"{t.datum}  [{t.bron}/{t.type}{project}]  {t.titel}")
        print(f"    archief/{t.pad}")
        print(f"    {' '.join(t.fragment.split())}")
        print()
    return 0


def _status(paden: config.Paden) -> int:
    telling: Counter[tuple[str, str]] = Counter()
    for bestand in archief.alle_bestanden(paden.archief):
        kop, _ = archief.lees(bestand)
        telling[(kop.get("bron", "?"), kop.get("type", "?"))] += 1
    if not telling:
        print("Het archief is nog leeg. Zie docs/stappenplan.md om te beginnen.")
        return 0
    print(f"Archief: {paden.archief}")
    for (bron, soort), aantal in sorted(telling.items()):
        print(f"  {bron:<15} {soort:<12} {aantal:>6}")
    print(f"  {'totaal':<28} {sum(telling.values()):>6}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mainframe", description="Persoonlijk archief")
    p.add_argument("--basis", help="basismap van het mainframe (standaard: deze repository)")
    sub = p.add_subparsers(dest="opdracht", required=True)

    imp = sub.add_parser("importeer", help="importeer een bron in het archief")
    imp.add_argument("soort", choices=["claude", "chatgpt", "claude-code", "map"])
    imp.add_argument("pad", nargs="?", help="exportbestand of map")
    imp.add_argument("--bron", default="bestanden", help="naam van de bron bij 'map', bv. google-drive")
    imp.add_argument("--project", help="koppel alle bestanden aan dit project (bij 'map')")
    imp.add_argument("--geen-index", action="store_true", help="zoekindex niet bijwerken")

    zk = sub.add_parser("zoek", help="zoek in het archief")
    zk.add_argument("termen", nargs="+")
    zk.add_argument("--bron")
    zk.add_argument("--project")
    zk.add_argument("--aantal", type=int, default=20)

    sub.add_parser("index", help="bouw de zoekindex opnieuw op")
    sub.add_parser("status", help="toon wat er in het archief staat")
    return p


def main(argv: list[str] | None = None) -> int:
    # Voorkom fouten bij tekens als "…" in een Windows-terminal met een oude codepagina.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = parser().parse_args(argv)
    paden = config.paden(args.basis)
    if args.opdracht == "importeer":
        return _importeer(args, paden)
    if args.opdracht == "zoek":
        return _zoek(args, paden)
    if args.opdracht == "index":
        print(f"Zoekindex opgebouwd ({zoeken.bouw_index(paden.archief, paden.index)} items).")
        return 0
    return _status(paden)
