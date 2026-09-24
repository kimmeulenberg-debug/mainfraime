"""Import van Claude Code-sessies.

Claude Code bewaart elke sessie op je eigen computer als JSONL-bestand in
`~/.claude/projects/<projectmap>/<sessie-id>.jsonl` (op Windows:
`%USERPROFILE%\\.claude\\projects`). Deze importer leest die map uit.

Let op: Claude Code ruimt oude sessies standaard na 30 dagen op. Importeer dus
regelmatig, of verhoog `cleanupPeriodDays` in ~/.claude/settings.json.

Sessies uit Claude Code in de cloud (claude.ai/code) staan niet op je
computer; de code daarvan staat in je GitHub-repositories.
"""

from __future__ import annotations

import json
from pathlib import Path

from mainframe.archief import Item, tijd
from mainframe.importers._export import eerste_regel, gesprek_als_tekst

BRON = "claude-code"
STANDAARD_MAP = Path.home() / ".claude" / "projects"


def _tekst(inhoud) -> str:
    if isinstance(inhoud, str):
        return inhoud
    delen = []
    for blok in inhoud or []:
        soort = blok.get("type")
        if soort == "text" and blok.get("text"):
            delen.append(blok["text"])
        elif soort == "tool_use":
            delen.append(f"*[hulpmiddel: {blok.get('name', 'onbekend')}]*")
    return "\n\n".join(delen)


def _sessie(bestand: Path) -> Item | None:
    berichten, samenvatting, map_ = [], None, None
    begin = eind = None
    sessie_id = bestand.stem
    for regel in bestand.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rij = json.loads(regel)
        except json.JSONDecodeError:
            continue
        if rij.get("type") == "summary" and rij.get("summary"):
            samenvatting = rij["summary"]
            continue
        if rij.get("type") not in ("user", "assistant") or rij.get("isMeta"):
            continue
        moment = tijd(rij.get("timestamp"))
        if moment:
            begin = min(begin, moment) if begin else moment
            eind = max(eind, moment) if eind else moment
        map_ = map_ or rij.get("cwd")
        sessie_id = rij.get("sessionId") or sessie_id
        tekst = _tekst((rij.get("message") or {}).get("content"))
        if tekst.strip():
            berichten.append(("Ik" if rij["type"] == "user" else "Claude", tekst))

    tekst = gesprek_als_tekst(berichten)
    if not tekst:
        return None
    eerste_vraag = next((t for s, t in berichten if s == "Ik"), "")
    project = Path(map_).name if map_ else bestand.parent.name
    return Item(
        id=f"claude-code-{sessie_id}",
        bron=BRON,
        type="codesessie",
        titel=samenvatting or eerste_regel(eerste_vraag) or "Codesessie",
        tekst=(f"Werkmap: `{map_}`\n\n" if map_ else "") + tekst,
        aangemaakt=begin,
        gewijzigd=eind,
        project=project,
        origineel=str(bestand),
    )


def importeer(pad: Path | None = None):
    pad = Path(pad) if pad else STANDAARD_MAP
    bestanden = [pad] if pad.is_file() else sorted(pad.rglob("*.jsonl"))
    for bestand in bestanden:
        item = _sessie(bestand)
        if item:
            yield item
