# Roadmap

Elke fase levert iets op dat je direct kunt gebruiken. Pas als een fase in de praktijk goed werkt, beginnen we aan de volgende.

## Fase 1: Archief (nu)

- [x] Archiefformaat en mappenstructuur
- [x] Importers: Claude (chats en projecten), ChatGPT, Claude Code, mappen met bestanden (Drive, OneNote, NotebookLM)
- [x] Zoekindex en zoekopdracht
- [x] Claude Code-instructies voor vragen over het archief
- [ ] Eerste echte import en evaluatie: wat mis je, wat is overbodig?

## Fase 2: Minder handwerk

- Automatisch importeren wat in `inbox/` wordt gezet: bestanden neerzetten en klaar.
- Een geplande taak die elke week de Claude Code-sessies importeert (Taakplanner in Windows, launchd op de Mac).
- OneNote rechtstreeks koppelen via Microsoft Graph. Dat is gratis voor een persoonlijk account, maar je moet eenmalig een app registreren.
- Google Drive rechtstreeks koppelen via de Drive API. Dat is gratis, maar je hebt eenmalig een Google Cloud-project nodig.
- Tekst uit PDF's halen, zodat ook die op inhoud doorzoekbaar worden.

## Fase 3: Structuur en verrijking

- Projecten over bronnen heen samenvoegen. Bijvoorbeeld: "Informatieplan" bestaat in Claude, ChatGPT en Drive.
- Met Claude Code samenvattingen en tags laten maken per stuk, in batches en binnen Pro.
- Een kennisbank-overzicht per onderwerp (FHIR, NEN 7510, Wegiz, …) met links naar de bronstukken.

## Fase 4: Dashboard

- Een eenvoudige webpagina op je eigen computer met zoeken, een tijdlijn en projecten.
- Pas in deze fase kiezen we voor een framework (bijvoorbeeld Next.js). Dat is geen doel op zich.

## Fase 5: Werkportaal (optioneel)

- Gmail en Agenda erbij. Gmail stond in je oorspronkelijke wens, maar niet in de lijst voor versie 1. Dat kan via Google Takeout (mbox) of via de Gmail API.
- Automatiseringen, bijvoorbeeld met n8n.

## Openstaande vragen

- Gmail: in welke fase wil je die erbij hebben?
- Back-up: kies je voor de standaardmap of voor Google Drive (zie stappenplan, stap 3)?
