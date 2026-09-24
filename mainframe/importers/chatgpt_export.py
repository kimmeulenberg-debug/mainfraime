"""Import van de ChatGPT-dataexport.

Aanvragen via chatgpt.com: Instellingen → Gegevensbeheer → Gegevens
exporteren. Je krijgt een e-mail met een zip-bestand met `conversations.json`.

ChatGPT slaat een gesprek op als boom (je kunt antwoorden opnieuw laten
genereren). We volgen het pad vanaf het laatst getoonde bericht terug naar
het begin; dat is precies het gesprek zoals je het in de app ziet.
"""

from __future__ import annotations

from pathlib import Path

from mainframe.archief import Item, tijd
from mainframe.importers._export import gesprek_als_tekst, lees_json

BRON = "chatgpt"
SPREKERS = {"user": "Ik", "assistant": "ChatGPT", "tool": "Hulpmiddel"}


def _tekst(bericht: dict) -> str:
    inhoud = bericht.get("content") or {}
    if "parts" in inhoud:
        delen = []
        for deel in inhoud["parts"] or []:
            if isinstance(deel, str):
                delen.append(deel)
            elif isinstance(deel, dict) and deel.get("text"):
                delen.append(deel["text"])
            elif isinstance(deel, dict):
                delen.append("*[afbeelding of bijlage]*")
        return "\n\n".join(d for d in delen if d.strip())
    return inhoud.get("text") or ""


def _pad(gesprek: dict) -> list[dict]:
    knopen = gesprek.get("mapping") or {}
    huidig = gesprek.get("current_node")
    if huidig not in knopen:
        # Geen eindpunt bekend: neem de knoop zonder kinderen met het laatste tijdstip.
        bladeren = [k for k, v in knopen.items() if not v.get("children")]
        huidig = max(
            bladeren,
            key=lambda k: ((knopen[k].get("message") or {}).get("create_time") or 0),
            default=None,
        )
    pad, gezien = [], set()
    while huidig and huidig in knopen and huidig not in gezien:
        gezien.add(huidig)
        pad.append(knopen[huidig])
        huidig = knopen[huidig].get("parent")
    return list(reversed(pad))


def importeer(pad: Path):
    for gesprek in lees_json(pad, "conversations.json"):
        berichten = []
        for knoop in _pad(gesprek):
            bericht = knoop.get("message")
            if not bericht:
                continue
            rol = (bericht.get("author") or {}).get("role")
            if rol not in SPREKERS:
                continue
            if (bericht.get("metadata") or {}).get("is_visually_hidden_from_conversation"):
                continue
            berichten.append((SPREKERS[rol], _tekst(bericht)))
        tekst = gesprek_als_tekst(berichten)
        if not tekst:
            continue
        gesprek_id = gesprek.get("conversation_id") or gesprek.get("id")
        yield Item(
            id=f"chatgpt-chat-{gesprek_id}",
            bron=BRON,
            type="chat",
            titel=gesprek.get("title") or "Naamloos gesprek",
            tekst=tekst,
            aangemaakt=tijd(gesprek.get("create_time")),
            gewijzigd=tijd(gesprek.get("update_time")),
            origineel=f"https://chatgpt.com/c/{gesprek_id}",
        )
