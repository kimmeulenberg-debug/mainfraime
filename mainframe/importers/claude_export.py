"""Import van de Claude.ai-dataexport (chats en projecten).

Aanvragen via claude.ai: Instellingen → Privacy → Gegevens exporteren.
Je krijgt een e-mail met een zip-bestand. Daarin staan onder meer
`conversations.json` en (als je projecten hebt) `projects.json`.
"""

from __future__ import annotations

from pathlib import Path

from mainframe.archief import Item, tijd
from mainframe.importers._export import eerste_regel, gesprek_als_tekst, lees_json

BRON = "claude"


def _bericht_tekst(bericht: dict) -> str:
    delen = []
    for blok in bericht.get("content") or []:
        soort = blok.get("type")
        if soort == "text" and blok.get("text"):
            delen.append(blok["text"])
        elif soort == "tool_use":
            delen.append(f"*[hulpmiddel gebruikt: {blok.get('name', 'onbekend')}]*")
    if not delen and bericht.get("text"):
        delen.append(bericht["text"])
    for bijlage in bericht.get("attachments") or []:
        naam = bijlage.get("file_name") or "bijlage"
        inhoud = (bijlage.get("extracted_content") or "").strip()
        delen.append(f"**Bijlage: {naam}**\n\n{inhoud}" if inhoud else f"**Bijlage: {naam}**")
    for bestand in bericht.get("files") or []:
        delen.append(f"**Bestand: {bestand.get('file_name', 'bestand')}**")
    return "\n\n".join(delen)


def _projectnamen(projecten: list[dict]) -> dict[str, str]:
    return {p.get("uuid"): p.get("name") for p in projecten if p.get("uuid")}


def importeer(pad: Path):
    projecten = lees_json(pad, "projects.json", verplicht=False) or []
    namen = _projectnamen(projecten)

    for project in projecten:
        naam = project.get("name") or "Naamloos project"
        onderdelen = []
        if project.get("description"):
            onderdelen.append(f"## Beschrijving\n\n{project['description']}")
        if project.get("prompt_template"):
            onderdelen.append(f"## Projectinstructies\n\n{project['prompt_template']}")
        documenten = project.get("docs") or []
        if documenten:
            lijst = "\n".join(f"- {d.get('filename', 'document')}" for d in documenten)
            onderdelen.append(f"## Kennisdocumenten\n\n{lijst}")
        yield Item(
            id=f"claude-project-{project['uuid']}",
            bron=BRON,
            type="project",
            titel=naam,
            tekst="\n\n".join(onderdelen) or "(leeg project)",
            aangemaakt=tijd(project.get("created_at")),
            gewijzigd=tijd(project.get("updated_at")),
            project=naam,
            tags=["claude-project"],
            origineel=f"https://claude.ai/project/{project['uuid']}",
        )
        for doc in documenten:
            yield Item(
                id=f"claude-projectdoc-{doc.get('uuid') or project['uuid'] + '-' + doc.get('filename', '')}",
                bron=BRON,
                type="document",
                titel=doc.get("filename") or "Projectdocument",
                tekst=doc.get("content") or "",
                aangemaakt=tijd(doc.get("created_at")) or tijd(project.get("created_at")),
                project=naam,
                tags=["claude-project", "kennisdocument"],
                origineel=f"https://claude.ai/project/{project['uuid']}",
            )

    for gesprek in lees_json(pad, "conversations.json"):
        berichten = []
        for bericht in gesprek.get("chat_messages") or []:
            spreker = "Ik" if bericht.get("sender") == "human" else "Claude"
            berichten.append((spreker, _bericht_tekst(bericht)))
        tekst = gesprek_als_tekst(berichten)
        if not tekst:
            continue
        eerste_vraag = next((t for s, t in berichten if s == "Ik" and t.strip()), "")
        project_id = gesprek.get("project_uuid") or (gesprek.get("project") or {}).get("uuid")
        yield Item(
            id=f"claude-chat-{gesprek['uuid']}",
            bron=BRON,
            type="chat",
            titel=gesprek.get("name") or eerste_regel(eerste_vraag) or "Naamloos gesprek",
            tekst=tekst,
            aangemaakt=tijd(gesprek.get("created_at")),
            gewijzigd=tijd(gesprek.get("updated_at")),
            project=namen.get(project_id),
            origineel=f"https://claude.ai/chat/{gesprek['uuid']}",
        )
