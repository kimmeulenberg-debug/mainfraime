# Bronnen: zo haal je je gegevens op

Menunamen veranderen weleens. Staat iets niet precies op de beschreven plek, zoek dan in de instellingen op *export*.

## Claude-chats en -projecten

1. Ga naar claude.ai → **Instellingen** → **Privacy** → **Gegevens exporteren**.
2. Je krijgt een e-mail met een downloadlink. De link is maar kort geldig, dus download het bestand direct.
3. Zet het zip-bestand in `inbox/` en importeer:
   ```bash
   python -m mainframe importeer claude inbox/<bestand>.zip
   ```

Wat wordt geïmporteerd:
- Elk gesprek wordt één archiefstuk. De tekst van bijlagen die je hebt geüpload wordt meegenomen.
- Staat er een `projects.json` in de export, dan krijgt elk project een eigen stuk met beschrijving en instructies. De kennisdocumenten van het project worden aparte stukken. Gesprekken worden aan hun project gekoppeld als de export die koppeling bevat.

## Claude Code

Claude Code bewaart je sessies op je eigen computer. Je hoeft niets te exporteren:

```bash
python -m mainframe importeer claude-code
```

- De sessies staan in `~/.claude/projects` (Windows: `C:\Users\<naam>\.claude\projects`).
- Sessies die je in de cloud draait (claude.ai/code, zoals deze) staan niet op je computer. Wat daar wordt gebouwd, staat wel in je GitHub-repositories.
- Werk je op meer computers? Voer de import dan op elke computer uit.

## ChatGPT

1. Ga naar chatgpt.com → **Instellingen** → **Gegevensbeheer** → **Gegevens exporteren**.
2. Je krijgt een e-mail met een downloadlink.
3. Importeer:
   ```bash
   python -m mainframe importeer chatgpt inbox/<bestand>.zip
   ```

Als je een antwoord opnieuw hebt laten genereren, bewaart de importer alleen de versie die je in de app ziet.

## Google Drive

Kies **Google Takeout**. Google-documenten worden dan omgezet naar Word-bestanden, zodat hun tekst doorzoekbaar wordt.

1. Ga naar takeout.google.com → **Alles deselecteren** → vink **Drive** aan.
2. Bij *Meerdere formaten*: kies voor Documenten **DOCX**.
3. Kies **Eenmalig exporteren**, als `.zip`.
4. Pak de zip uit in `inbox/` en importeer:
   ```bash
   python -m mainframe importeer map "inbox/Takeout/Drive" --bron google-drive
   ```

Google Drive voor desktop is minder geschikt. Die map bevat voor Google-documenten alleen snelkoppelingen (`.gdoc`) en niet de inhoud.

## OneNote (persoonlijk account)

Er is nog geen automatische koppeling (die staat in de roadmap). Tot die tijd exporteer je per sectie:

- **OneNote voor Windows (desktop):** open een sectie → **Bestand** → **Exporteren** → *Sectie* → **Word-document (.docx)**.
- **OneNote voor Mac of op het web:** exporteren kan alleen als PDF. PDF's worden als bijlage bewaard en zijn vindbaar op titel, maar niet op inhoud. Claude Code kan ze wel lezen als je ernaar vraagt.

Zet de bestanden in een map per notitieblok, bijvoorbeeld `inbox/OneNote/Persoonlijk/`, en importeer:

```bash
python -m mainframe importeer map inbox/OneNote --bron onenote
```

De namen van de submappen worden tags, zodat je later per notitieblok kunt filteren.

## NotebookLM

NotebookLM heeft geen openbare koppeling.

1. Kijk in Google Takeout of **NotebookLM** in de lijst staat. Zo ja, exporteer het samen met Drive en importeer de map met `--bron notebooklm`.
2. Staat het er niet bij? Kopieer dan belangrijke notities en samenvattingen naar een tekstbestand (`.md` of `.txt`) in `inbox/NotebookLM/` en importeer:
   ```bash
   python -m mainframe importeer map inbox/NotebookLM --bron notebooklm
   ```

De bronnen van een notebook staan vaak al in Google Drive en komen dan via die import binnen.

## Andere bronnen

Elke map met bestanden is te importeren. Kies zelf een bronnaam met alleen kleine letters, cijfers en `-`:

```bash
python -m mainframe importeer map <map> --bron <naam> [--project <projectnaam>]
```

Wat er met de bestanden gebeurt:
- `.md`, `.txt`, `.csv`, `.json`, `.html`, `.docx` en codebestanden worden opgeslagen als doorzoekbare tekst.
- Andere bestanden (pdf, afbeeldingen, spreadsheets) worden als bijlage gekopieerd en zijn vindbaar op naam.
