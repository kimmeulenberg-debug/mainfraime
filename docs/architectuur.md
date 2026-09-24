# Architectuur

## Overzicht

```
   Claude-export   ChatGPT-export   Claude Code   Google Takeout   OneNote-export
        │                │               │              │                │
        └────────────────┴───── importers ┴──────────────┴────────────────┘
                                     │
                                     ▼
                      archief/  (Markdown, één bestand per stuk)
                                     │
                     ┌───────────────┴────────────────┐
                     ▼                                ▼
          zoekindex (SQLite FTS5)             Claude Code in VS Code
          `python -m mainframe zoek`          vragen, samenvatten, verbanden
```

Er zijn drie lagen, elk met een eigen taak:

1. **Importers** (`mainframe/importers/`): elke bron heeft een eigen importer. Die zet het exportformaat van de dienst om naar het vaste archiefformaat. Komt er een nieuwe bron bij, dan is dat één nieuw bestand.
2. **Archief** (`archief/`): de bron van waarheid. Het bestaat uit gewone Markdown-bestanden, dus je kunt ze lezen in VS Code, Obsidian of Kladblok, ook over tien jaar.
3. **Toegang**: de zoekindex voor snel zoeken en Claude Code voor vragen in gewone taal. De index is afgeleid van het archief en kan altijd opnieuw worden opgebouwd met `python -m mainframe index`.

## Het archiefformaat

Mappen: `archief/<bron>/<jaar>/<datum>_<kort-id>_<titel>.md`

Een voorbeeld:

```markdown
---
id: "claude-chat-c1111111-aaaa-4bbb-8ccc-000000000001"
bron: "claude"
type: "chat"
titel: "Visie regionale gegevensuitwisseling"
aangemaakt: "2025-03-14T09:12:00Z"
gewijzigd: "2025-03-14T10:00:00Z"
project: "Informatieplan"
origineel: "https://claude.ai/chat/c1111111-aaaa-4bbb-8ccc-000000000001"
---

# Visie regionale gegevensuitwisseling

### Ik

Help me met een visie op regionale gegevensuitwisseling.

### Claude

Begin bij het Triple Aim-principe.
```

| Veld | Betekenis |
|---|---|
| `id` | Vaste, unieke sleutel, afgeleid van het id in de bron. Hiermee worden dubbelen voorkomen. |
| `bron` | `claude`, `chatgpt`, `claude-code`, `google-drive`, `onenote`, `notebooklm`, … |
| `type` | `chat`, `project`, `document`, `codesessie` of `bestand` |
| `titel` | Titel uit de bron, of de eerste vraag als er geen titel is |
| `aangemaakt` / `gewijzigd` | Tijdstip in UTC (ISO 8601) |
| `project` | Projectnaam, als de bron die kent of als je `--project` gebruikt |
| `tags` | Lijst met labels, bijvoorbeeld de submap in Drive of OneNote |
| `origineel` | Link of pad naar het origineel |
| `bijlage` | Pad naar het bewaarde bestand, als het geen tekst is (pdf, afbeelding) |

Elke regel van het kopblok is `sleutel: <JSON-waarde>`. Dat is geldige YAML, en het is eenvoudig en foutloos in te lezen zonder extra bibliotheken.

## Keuzes en waarom

| Keuze | Waarom |
|---|---|
| Alleen standaard Python, geen pakketten | Het is gratis, installeert niets en er gaat minder mis bij updates. |
| Markdown-bestanden in plaats van een database | Het formaat is open en toekomstvast, en Claude Code en andere tools kunnen het direct lezen. |
| Archief niet in Git | Het gaat om privégegevens. Bovendien is Git niet gemaakt voor grote hoeveelheden bestanden en bijlagen. |
| Exports in plaats van live koppelingen | Claude, ChatGPT en NotebookLM hebben geen API voor je chatgeschiedenis. Exports werken overal en je hebt er geen sleutels voor nodig. |
| Claude Code als AI-laag | Het zit bij Claude Pro. Voor de Claude API betaal je apart per gebruik. |
| SQLite FTS5 voor zoeken | Het zit in Python, is snel genoeg voor honderdduizenden stukken en werkt zonder accenten ("regie" vindt ook "régie"). |

## Privacy en beveiliging

- Het archief staat alleen op je eigen computer en in de back-uplocatie die je zelf kiest.
- `.gitignore` houdt het archief, de inbox, de index en toekomstige sleutelbestanden buiten GitHub.
- Het archief bevat alleen persoonlijke accounts. Werkgegevens van je werkgever en patiëntgegevens horen hier niet in, vanwege de AVG, NEN 7510 en het beleid van je werkgever.
- Zet versleuteling van je schijf aan (BitLocker op Windows, FileVault op Mac). Het archief bevat veel persoonlijke informatie.
