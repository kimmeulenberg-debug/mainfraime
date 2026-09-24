# Mainframe

Mijn persoonlijke archief. Hier komen alle chats, projecten, codesessies en documenten samen op één plek, zodat ik ze kan doorzoeken en er vragen over kan stellen.

**Bronnen in versie 1:** Claude-chats en -projecten, Claude Code-sessies, ChatGPT-chats, Google Drive, OneNote en NotebookLM.

## Uitgangspunten

- **Eerst een archief.** Eerst alles bewaren en terugvinden. Een dashboard en automatiseringen komen later.
- **Ik houd zelf een kopie.** De inhoud wordt echt opgeslagen, dus niet alleen een link naar de bron. Het archief blijft bruikbaar als een dienst stopt of iets verwijdert.
- **Alles lokaal en privé.** Het archief staat op mijn eigen computer. Deze repository bevat alleen de code, nooit de inhoud (zie `.gitignore`).
- **Alleen persoonlijke accounts.** Werkgegevens en zeker patiëntgegevens horen hier niet in.
- **Geen extra kosten.** Er is alleen standaard Python nodig. Voor AI gebruik ik Claude Code, dat bij mijn Claude Pro-abonnement zit.
- **Open formaat.** Elk archiefstuk is een gewoon Markdown-bestand, leesbaar zonder deze software.

## Snel starten

```bash
python -m mainframe status                                   # wat staat er in het archief?
python -m mainframe importeer claude inbox/claude-export.zip  # Claude-chats en -projecten
python -m mainframe importeer chatgpt inbox/chatgpt.zip       # ChatGPT-chats
python -m mainframe importeer claude-code                     # Claude Code-sessies op deze computer
python -m mainframe importeer map inbox/Takeout/Drive --bron google-drive
python -m mainframe zoek "regie op gegevens"                 # zoeken in alles
```

Daarna kun je in VS Code aan Claude Code vragen stellen als *"Wat heb ik vorig jaar over FHIR besproken?"*. Claude Code zoekt dan in het archief (zie `CLAUDE.md`).

## Documentatie

| Document | Inhoud |
|---|---|
| [docs/stappenplan.md](docs/stappenplan.md) | Stap voor stap aan de slag, van installatie tot eerste zoekvraag |
| [docs/bronnen.md](docs/bronnen.md) | Hoe je per bron een export maakt |
| [docs/architectuur.md](docs/architectuur.md) | Opbouw, archiefformaat en keuzes |
| [docs/roadmap.md](docs/roadmap.md) | Wat er na versie 1 komt |

## Mappen

```
mainframe/     de code (importers, archief, zoeken)
archief/       het archief zelf, één map per bron (niet in Git)
inbox/         hier zet je exportbestanden neer om te importeren (niet in Git)
docs/          documentatie
tests/         automatische tests met voorbeeldgegevens
```
