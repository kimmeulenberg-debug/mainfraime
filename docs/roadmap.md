# Roadmap

Elke fase levert iets op dat je direct kunt gebruiken. Pas als een fase in de praktijk goed werkt, beginnen we aan de volgende.

## Fase 1: Archief (nu)

- [x] Archiefformaat en mappenstructuur
- [x] Importers: Claude (chats en projecten), ChatGPT, Claude Code, mappen met bestanden (Drive, OneNote, NotebookLM)
- [x] Zoekindex en zoekopdracht
- [x] Claude Code-instructies voor vragen over het archief
- [ ] Eerste echte import en evaluatie: wat mis je, wat is overbodig?

## Fase 2: Thuisbasis op de Mac mini (nu)

Zie [mac-mini.md](mac-mini.md).

- [x] Inbox die vanzelf wordt verwerkt (`inbox/<bron>/`, verwerkte bestanden naar `inbox/verwerkt/`)
- [x] Nachtelijke taak via launchd: Claude Code-sessies, inbox en zoekindex
- [x] Geheugen voor Claude (over mij, projecten, voorkeuren) in de back-up via Google Drive
- [x] Vaste opdrachten: `/archief`, `/weekoverzicht`, `/onthoud`, `/inbox`
- [x] Stappenplan: altijd aan, Tailscale, Orca, Remote Control, VS Code via SSH
- [ ] Mac mini inrichten en de herstarttest doen
- [ ] Geheugen invullen en een week in de praktijk gebruiken

## Fase 3: Rechtstreekse koppelingen en verrijking

- OneNote rechtstreeks koppelen via Microsoft Graph. Dat is gratis voor een persoonlijk account, maar je moet eenmalig een app registreren.
- Google Drive rechtstreeks koppelen via de Drive API. Dat is gratis, maar je hebt eenmalig een Google Cloud-project nodig.
- Tekst uit PDF's halen, zodat ook die op inhoud doorzoekbaar worden.

- Projecten over bronnen heen samenvoegen. Bijvoorbeeld: "Informatieplan" bestaat in Claude, ChatGPT en Drive.
- Met Claude Code samenvattingen en tags laten maken per stuk, in batches en binnen Pro.
- Een kennisbank-overzicht per onderwerp (FHIR, NEN 7510, Wegiz, …) met links naar de bronstukken.

## Fase 4: Dashboard

- Een eenvoudige webpagina op je eigen computer met zoeken, een tijdlijn en projecten.
- Pas in deze fase kiezen we voor een framework (bijvoorbeeld Next.js). Dat is geen doel op zich.

## Fase 5: Werkportaal (optioneel)

- Gmail en Agenda erbij, via Google Takeout (mbox) of de Gmail API. Afgesproken: Gmail komt later, als het archief in de praktijk goed werkt.
- Automatiseringen, bijvoorbeeld met n8n.

## Genomen besluiten

| Onderwerp | Besluit |
|---|---|
| Doel versie 1 | Eerst een archief, dashboard en automatisering later |
| Opslag | Echte kopie van de inhoud, niet alleen links |
| Accounts | Alleen persoonlijke accounts |
| Waar het draait | Lokaal, op de Mac mini die altijd aanstaat |
| Bediening op afstand | Tailscale, met Orca of Remote Control in de Claude-app |
| AI | Claude, via Claude Code (valt binnen Claude Pro) |
| Kosten | Geen extra kosten naast Claude Pro |
| Back-up | Archief en geheugen in Google Drive (`instellen --archief`), index en inbox lokaal |
| Gmail | Later, na fase 1 |
