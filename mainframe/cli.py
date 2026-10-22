"""Opdrachtregel van het mainframe.

Voorbeelden:
    python -m mainframe importeer claude inbox/claude-export.zip
    python -m mainframe importeer chatgpt inbox/chatgpt-export.zip
    python -m mainframe importeer claude-code
    python -m mainframe importeer map inbox/takeout/Drive --bron google-drive
    python -m mainframe zoek "regie op gegevens"
    python -m mainframe status
    python -m mainframe verwerk-inbox      # alles in inbox/ importeren
    python -m mainframe onderhoud          # wat de Mac mini elke nacht doet
    python -m mainframe geheugen           # vaste context voor Claude tonen
    python3 -m mainframe taak installeer   # nachtelijke taak op de Mac mini
    python -m mainframe instellen --archief "<map in Google Drive>"
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from datetime import datetime

from mainframe import archief, config, geheugen, inbox, mac, zoeken
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
        if not inbox.geldige_bron(args.bron):
            print(
                "Gebruik voor --bron alleen kleine letters, cijfers en '-'"
                f" (en niet: {', '.join(sorted(inbox.GERESERVEERD))}).",
                file=sys.stderr,
            )
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

    print(f"Klaar: {_telling_tekst(telling)}.")
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
        print(f"    {paden.archief / t.pad}")
        print(f"    {' '.join(t.fragment.split())}")
        print()
    return 0


def _telling_tekst(telling: Counter) -> str:
    return (
        f"{telling['nieuw']} nieuw, {telling['bijgewerkt']} bijgewerkt,"
        f" {telling['ongewijzigd']} ongewijzigd"
    )


def _verwerk_inbox(paden: config.Paden, index: bool = True) -> int:
    verslag = inbox.verwerk(paden)
    for regel in verslag.regels():
        print(regel)
    if verslag.verwerkt:
        print(f"Archief: {_telling_tekst(verslag.telling)}.")
        if index:
            print(f"Zoekindex bijgewerkt ({zoeken.bouw_index(paden.archief, paden.index)} items).")
    return 1 if verslag.fouten else 0


def _onderhoud(paden: config.Paden) -> int:
    """Eén ronde onderhoud: Claude Code-sessies, inbox en zoekindex."""
    print(f"=== Onderhoud {datetime.now():%Y-%m-%d %H:%M} ===")
    if not paden.archief.exists():
        # Bijvoorbeeld als Google Drive nog niet is gestart of de map niet bereikbaar is.
        print(f"Fout: archief niet gevonden: {paden.archief}", file=sys.stderr)
        return 1
    telling: Counter[str] = Counter()
    for item in claude_code.importeer():
        status, _ = archief.bewaar(item, paden.archief)
        telling[status] += 1
    print(f"Claude Code-sessies: {_telling_tekst(telling)}.")
    code = _verwerk_inbox(paden, index=False)
    print(f"Zoekindex bijgewerkt ({zoeken.bouw_index(paden.archief, paden.index)} items).")
    return code


def _geheugen(paden: config.Paden) -> int:
    print(geheugen.toon(paden.geheugen))
    return 0


def _instellen(args, paden: config.Paden) -> int:
    if args.archief_map:
        doel = config._map(args.archief_map)
        if not doel.parent.exists():
            print(f"Fout: de bovenliggende map bestaat niet: {doel.parent}", file=sys.stderr)
            return 1
        doel.mkdir(exist_ok=True)
        pad = config.bewaar_instellingen(paden.basis, archief=str(doel))
        print(f"Opgeslagen in {pad}")
        paden = config.paden(paden.basis)
    print(f"Archief:   {paden.archief}")
    print(f"Inbox:     {paden.inbox}")
    print(f"Zoekindex: {paden.index}")
    if os.environ.get("MAINFRAME_ARCHIEF"):
        print("Let op: de omgevingsvariabele MAINFRAME_ARCHIEF is gezet en gaat voor op deze instelling.")
    return 0


def _status(paden: config.Paden) -> int:
    telling: Counter[tuple[str, str]] = Counter()
    for bestand in archief.alle_bestanden(paden.archief):
        kop, _ = archief.lees(bestand)
        telling[(kop.get("bron", "?"), kop.get("type", "?"))] += 1
    if not telling:
        print(f"Het archief in {paden.archief} is nog leeg. Zie docs/stappenplan.md om te beginnen.")
        return 0
    print(f"Archief: {paden.archief}")
    for (bron, soort), aantal in sorted(telling.items()):
        print(f"  {bron:<15} {soort:<12} {aantal:>6}")
    print(f"  {'totaal':<28} {sum(telling.values()):>6}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mainframe", description="Persoonlijk archief")
    p.add_argument("--basis", help="basismap voor inbox en zoekindex (standaard: deze repository)")
    p.add_argument("--archief", help="map van het archief (standaard: MAINFRAME_ARCHIEF of <basis>/archief)")
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
    sub.add_parser("verwerk-inbox", help="importeer alles wat in inbox/ staat")
    sub.add_parser("onderhoud", help="Claude Code-sessies + inbox + zoekindex (voor de nachtelijke taak)")
    sub.add_parser("geheugen", help="toon het geheugen van Claude (maakt het aan als het ontbreekt)")

    st = sub.add_parser("instellen", help="toon of wijzig waar het archief staat")
    st.add_argument("--archief", dest="archief_map", help="map voor het archief, bv. in Google Drive")

    tk = sub.add_parser("taak", help="automatische taak op de Mac (launchd)")
    tk.add_argument("actie", choices=["installeer", "verwijder", "start", "status"])
    tk.add_argument("--tijd", default="03:00", help="tijdstip van de dagelijkse ronde (UU:MM)")
    return p


def main(argv: list[str] | None = None) -> int:
    # Voorkom fouten bij tekens als "…" in een Windows-terminal met een oude codepagina.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    args = parser().parse_args(argv)
    paden = config.paden(args.basis, args.archief)
    if args.opdracht == "importeer":
        return _importeer(args, paden)
    if args.opdracht == "zoek":
        return _zoek(args, paden)
    if args.opdracht == "verwerk-inbox":
        return _verwerk_inbox(paden)
    if args.opdracht == "onderhoud":
        return _onderhoud(paden)
    if args.opdracht == "geheugen":
        return _geheugen(paden)
    if args.opdracht == "instellen":
        return _instellen(args, paden)
    if args.opdracht == "taak":
        if args.actie == "installeer":
            print(mac.installeer(paden, args.tijd))
        else:
            print({"verwijder": mac.verwijder, "start": mac.start, "status": mac.status}[args.actie]())
        return 0
    if args.opdracht == "index":
        print(f"Zoekindex opgebouwd ({zoeken.bouw_index(paden.archief, paden.index)} items).")
        return 0
    return _status(paden)
