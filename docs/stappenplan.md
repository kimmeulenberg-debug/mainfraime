# Stappenplan: van nul naar een doorzoekbaar archief

Reken op ongeveer een uur werk, verdeeld over een paar dagen. De exports van Claude, ChatGPT en Google worden namelijk niet direct geleverd.

## Stap 1. Installeer de gereedschappen (± 20 minuten)

Installeer op je computer:

| Programma | Waarvoor | Downloaden |
|---|---|---|
| **Visual Studio Code** | je werkplaats | code.visualstudio.com |
| **Git** | versiebeheer van de code | git-scm.com |
| **Python 3.12 of nieuwer** | voert het mainframe uit | python.org (Windows: vink *Add python.exe to PATH* aan) |

Docker, Node.js en een database zijn in deze fase niet nodig. Die komen pas bij het dashboard (zie `roadmap.md`).

Controleer de installatie in een terminal (Windows: *PowerShell*, Mac: *Terminal*):

```bash
git --version
python --version      # op de Mac: python3 --version
```

> **Mac:** typ in alle opdrachten hieronder `python3` in plaats van `python`.

## Stap 2. Haal de repository binnen in VS Code (± 5 minuten)

1. Open VS Code en kies **Clone Git Repository…** (of druk op `Ctrl+Shift+P` en typ *Git: Clone*).
2. Plak `https://github.com/kimmeulenberg-debug/mainfraime` en log in bij GitHub als daarom wordt gevraagd.
3. Kies een map, bijvoorbeeld `Documenten\Mainframe`, en open de repository.
4. VS Code stelt voor om de aanbevolen extensies te installeren (Python en Claude Code). Kies **Installeren**.
5. Ga naar de branch met het fundament. Klik linksonder op de branchnaam en kies `claude/dreamy-maxwell-mzck7z`. Ben je tevreden, dan voegen we die later samen met `main`.

Open de terminal in VS Code (het menu **Terminal → New Terminal**) en test:

```bash
python -m mainframe status
```

Je krijgt de melding *"Het archief is nog leeg"*. Het werkt.

## Stap 3. Kies waar het archief komt te staan (± 5 minuten)

Standaard komt het archief in de map `archief/` binnen de repository. Die map gaat **niet** naar GitHub, dus je moet zelf voor een back-up zorgen. Er zijn twee opties:

- **A. Gebruik de standaardmap** en neem de hele map `Mainframe` op in je gewone back-up (bijvoorbeeld OneDrive of een externe schijf).
- **B. Zet het archief in je Google Drive-map.** Dan wordt het automatisch geback-upt, als je Google Drive voor desktop hebt. Stel dan eenmalig in:

  ```powershell
  # Windows (PowerShell). Sluit daarna VS Code en open het opnieuw.
  setx MAINFRAME_HOME "G:\Mijn Drive\Mainframe-data"
  ```

  ```bash
  # Mac: voeg deze regel toe aan ~/.zshrc
  export MAINFRAME_HOME="$HOME/Library/CloudStorage/GoogleDrive-<jouw-account>/Mijn Drive/Mainframe-data"
  ```

  Let op het gratis Google-account: daar heb je 15 GB, gedeeld met Gmail en Foto's.

## Stap 4. Vraag de exports aan (± 10 minuten, daarna wachten)

Doe dit op dezelfde dag, want de levering kan van een paar minuten tot een paar dagen duren. In [bronnen.md](bronnen.md) staat per bron precies waar je klikt.

- [ ] Claude.ai-export (chats en projecten)
- [ ] ChatGPT-export
- [ ] Google Takeout: Drive (en NotebookLM, als dat in de lijst staat)
- [ ] OneNote: secties exporteren als Word-document

## Stap 5. Importeer (± 10 minuten)

Zet de gedownloade bestanden in de map `inbox/` en voer uit:

```bash
python -m mainframe importeer claude inbox/<naam-van-claude-export>.zip
python -m mainframe importeer chatgpt inbox/<naam-van-chatgpt-export>.zip
python -m mainframe importeer claude-code
python -m mainframe importeer map "inbox/Takeout/Drive" --bron google-drive
python -m mainframe importeer map "inbox/OneNote" --bron onenote
python -m mainframe status
```

Je kunt elke import zo vaak herhalen als je wilt. Er ontstaan geen dubbele stukken: bestaande stukken worden bijgewerkt.

## Stap 6. Zoeken en vragen stellen

**Zelf zoeken:**

```bash
python -m mainframe zoek wegiz
python -m mainframe zoek "samen beslissen" --bron chatgpt
python -m mainframe zoek fhir --project informatieplan
```

In VS Code kan het ook zonder te typen: `Ctrl+Shift+P` → *Tasks: Run Task* → **Mainframe: zoeken**.

**Vragen stellen aan Claude:** open het Claude Code-paneel in VS Code (het Claude-icoon) en log in met je Claude Pro-account. Stel daarna een vraag, bijvoorbeeld:

> Wat heb ik het afgelopen jaar besproken over PGO-koppelingen? Maak een overzicht met bronnen.

Claude Code volgt de instructies in `CLAUDE.md`: het zoekt in het archief, leest de gevonden stukken en noemt de bronnen. Dit valt binnen je Pro-abonnement. Houd er wel rekening mee dat intensief gebruik meetelt voor je gebruikslimiet.

## Stap 7. Maak er een gewoonte van

| Wanneer | Wat |
|---|---|
| Elke week | `python -m mainframe importeer claude-code`. Claude Code verwijdert lokale sessies standaard na 30 dagen. |
| Elke maand | Nieuwe exports van Claude en ChatGPT importeren |
| Elk kwartaal | Google Takeout en OneNote opnieuw exporteren |

Een tip om langer te bewaren: zet in `~/.claude/settings.json` de regel `"cleanupPeriodDays": 365`. Dan blijven Claude Code-sessies een jaar staan.

In fase 2 (zie `roadmap.md`) automatiseren we zoveel mogelijk van deze stappen.
