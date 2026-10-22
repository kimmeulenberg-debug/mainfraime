# Fase 2: de Mac mini als thuisbasis

De Mac mini wordt het huis van je mainframe. Hij staat altijd aan, houdt het archief vanzelf bij en Claude is er altijd bereikbaar. Jij werkt vanaf je laptop of telefoon en kijkt mee.

```
 Laptop (VS Code)        iPhone (Orca / Claude-app)
        │                          │
        └────────── Tailscale ─────┘      privéverbinding, geen open poorten
                       │
                       ▼
           Mac mini, altijd aan
           ├─ Claude Code              werkt in de map van het mainframe
           ├─ Orca                     sessies bekijken en besturen op afstand
           ├─ nachtelijke taak         Claude Code-sessies + inbox + zoekindex
           ├─ mainframe                archief, zoekindex en geheugen
           └─ Google Drive voor desktop   back-up van archief en geheugen
```

Dit is dezelfde opzet als bij *Het Mainframe* (hetmainframe.nl): VS Code met Claude Code, een computer die altijd aanstaat en Orca om mee te kijken. Het verschil zit in het doel. Wij beginnen met het **archief en geheugen**, zodat Claude alles weet wat je al hebt gedaan. Taken uitvoeren in je mailbox, zoals een "digitale werknemer", komt daarna (fase 5).

Reken op een middag werk. Je doet alles op de Mac mini zelf, met scherm en toetsenbord. Na stap 3 kan het ook op afstand.

---

## Stap 1. Basisinstellingen (± 15 minuten)

1. Installeer alle updates: **Systeeminstellingen → Algemeen → Software-update**.
2. Geef de Mac een herkenbare naam: **Systeeminstellingen → Algemeen → Info → Naam**, bijvoorbeeld `mainframe`.
3. Werk met je eigen gebruikersaccount, met een sterk wachtwoord.

## Stap 2. Altijd aan (± 5 minuten)

Ga naar **Systeeminstellingen → Energie** en zet aan:

- **Voorkom automatische sluimerstand als het beeldscherm uit is**
- **Wek voor netwerktoegang**
- **Start automatisch na een stroomstoring**

Zet in **Vergrendelingsscherm** het beeldscherm uit na een paar minuten. Dat bespaart stroom, en de Mac blijft gewoon doorwerken. 24/7 aan kost ongeveer €1 stroom per maand.

**FileVault (schijfversleuteling): laat dit aan.** Je archief is privé. Het nadeel is klein: na een stroomstoring of een grote update moet je één keer zelf inloggen voordat de Mac mini weer bereikbaar is. Zet daarom automatische updates niet op "installeren", maar installeer ze zelf op een moment dat je bij de Mac bent.

## Stap 3. Bereikbaar op afstand (± 15 minuten)

1. **Tailscale** (gratis): installeer het op de Mac mini, je laptop en je iPhone, via tailscale.com of de App Store. Log op alle drie in met hetzelfde account. Je apparaten kunnen elkaar dan veilig bereiken, ook buiten je thuisnetwerk.
2. **Externe login (SSH)**: **Systeeminstellingen → Algemeen → Delen → Externe login** aan, alleen voor je eigen gebruiker.
3. **Scherm delen**: zet in hetzelfde scherm **Scherm delen** aan. Zo kun je vanaf je laptop meekijken via Finder → *Ga* → *Verbind met server* → `vnc://mainframe`.

Test vanaf je laptop: `ssh <jouw-gebruikersnaam>@mainframe`.

## Stap 4. Software installeren (± 20 minuten)

Open de Terminal op de Mac mini.

1. **Git:** `xcode-select --install` en volg de stappen.
2. **Python:** download de nieuwste versie van python.org en installeer die. Controleer met `python3 --version`. Je moet 3.12 of hoger zien.
3. **Claude Code:** installeer het volgens de officiële handleiding (code.claude.com). Start daarna `claude` en log in met je Claude Pro-account.
4. **Google Drive voor desktop:** installeer het en log in met je persoonlijke account. Kies in de voorkeuren van Google Drive bij *Mijn Drive* voor **Bestanden spiegelen**. Dan staan de bestanden echt op de Mac mini, en dat werkt het betrouwbaarst voor taken die 's nachts draaien.
5. **VS Code** (optioneel op de Mac mini zelf): handig als je er direct achter zit.

## Stap 5. Het mainframe op de Mac mini zetten (± 10 minuten)

Zet de repository in je thuismap, **niet** in *Documenten* of *Bureaublad*. macOS beschermt die mappen extra, en dan kan de nachtelijke taak er niet bij.

```bash
mkdir -p ~/Mainframe && cd ~/Mainframe
git clone https://github.com/kimmeulenberg-debug/mainfraime
cd mainfraime
git checkout claude/dreamy-maxwell-mzck7z
```

Zoek op waar Google Drive staat en vertel het mainframe waar het archief komt:

```bash
ls ~/Library/CloudStorage/          # je ziet iets als GoogleDrive-kim@gmail.com
python3 -m mainframe instellen --archief "$HOME/Library/CloudStorage/GoogleDrive-<adres>/Mijn Drive/Mainframe-archief"
python3 -m mainframe status
```

`instellen` maakt de map aan als die nog niet bestaat en onthoudt de plek. Dat geldt voor de Terminal, VS Code, Claude Code en de nachtelijke taak. Met `python3 -m mainframe instellen` zonder extra opties zie je de huidige instelling.

Staat Google Drive bij jou in het Engels, dan heet de map `My Drive` in plaats van `Mijn Drive`.

Heb je het archief al op je laptop opgebouwd? Dan staat het al in Google Drive en is het hier vanzelf beschikbaar. Bouw alleen de zoekindex opnieuw op: `python3 -m mainframe index`.

## Stap 6. De nachtelijke taak aanzetten (± 5 minuten)

```bash
python3 -m mainframe taak installeer     # standaard elke nacht om 03:00
python3 -m mainframe taak start          # nu meteen één keer proberen
python3 -m mainframe taak status         # werkt het? toont ook het logboek
```

Wat de taak doet:
- Hij importeert alle nieuwe **Claude Code-sessies**. Die raak je dus niet meer kwijt na 30 dagen.
- Hij verwerkt alles wat in **`inbox/`** staat. Dat gebeurt ook direct zodra je er iets neerzet.
- Hij werkt de **zoekindex** bij.

Een ander tijdstip kies je met `python3 -m mainframe taak installeer --tijd 05:30`. Het logboek staat in `~/Library/Logs/mainframe.log`.

**Staat in het logboek "Operation not permitted"?** Dan blokkeert macOS de toegang tot de map van Google Drive. Geef Python dan *Volledige schijftoegang*:
1. Zoek het pad op: `python3 -c "import sys; print(sys.executable)"`.
2. Ga naar **Systeeminstellingen → Privacy en beveiliging → Volledige schijftoegang** en klik op **+**.
3. Druk op `Cmd+Shift+G`, plak het pad en voeg het toe.
4. Voer `python3 -m mainframe taak start` opnieuw uit.

### De inbox gebruiken

Zet exports in een submap met de naam van de bron. De taak doet de rest en verplaatst verwerkte bestanden naar `inbox/verwerkt/`.

```
inbox/claude/          Claude.ai-export (zip)
inbox/chatgpt/         ChatGPT-export (zip)
inbox/google-drive/    Google Takeout (zip of uitgepakte map)
inbox/onenote/         OneNote-secties (.docx), eventueel in submappen per notitieblok
inbox/notebooklm/      notities als .md of .txt
```

Zip-bestanden van Claude en ChatGPT mag je ook direct in `inbox/` zetten. Die worden aan de inhoud herkend.

**Hoe krijg je een export van je laptop op de Mac mini?** Kies wat het makkelijkst is:
- Stuur hem met **AirDrop** naar de Mac mini en verplaats hem naar de inbox.
- Open de downloadlink uit de mail meteen **op de Mac mini**, via Scherm delen.
- Kopieer hem vanaf je laptop met `scp export.zip <gebruiker>@mainframe:~/Mainframe/mainfraime/inbox/claude/`.

## Stap 7. Claude altijd bereikbaar (± 20 minuten)

**Orca (aanbevolen, gratis).** Dit is ook wat Het Mainframe gebruikt.
1. Installeer Orca op de Mac mini volgens de instructies op de Orca-site.
2. Voeg de map `~/Mainframe/mainfraime` toe als project en start daarin een Claude Code-sessie.
3. Installeer Orca op je iPhone en koppel hem via Tailscale aan de Mac mini, zoals de Orca-app aangeeft.

**Alternatief: Remote Control in de Claude-app.** Dit is een functie van Claude Code zelf. Start op de Mac mini in de map van het mainframe `claude remote-control`. De sessie verschijnt daarna in de Claude-app op je telefoon, onder *Code*. Laat het Terminal-venster open. Wordt het gesloten, dan stopt ook de sessie.

**Vanaf je laptop.** Installeer in VS Code de extensie **Remote - SSH** (die staat bij de aanbevolen extensies). Verbind met `<gebruiker>@mainframe` en open de map `~/Mainframe/mainfraime`. VS Code en Claude Code werken dan op de Mac mini. Al je sessies komen daardoor vanzelf in het archief.

## Stap 8. Het geheugen invullen (± 15 minuten)

```bash
python3 -m mainframe geheugen
```

Dit maakt drie bestanden aan in `Mainframe-archief/geheugen/`: `over-mij.md`, `projecten.md` en `voorkeuren.md`. Vul ze kort in. Claude leest ze bij elke vraag over het archief.

Daarna kun je in Claude Code deze vaste opdrachten gebruiken:

| Opdracht | Wat het doet |
|---|---|
| `/archief <vraag>` | Beantwoordt een vraag uit je archief, met bronnen |
| `/weekoverzicht` | Maakt een overzicht per project van de afgelopen week |
| `/onthoud <tekst>` | Slaat iets op in het geheugen |
| `/inbox` | Verwerkt de inbox en vertelt wat er is binnengekomen |

## Controle: werkt alles?

- [ ] `python3 -m mainframe status` toont het archief in Google Drive
- [ ] `python3 -m mainframe taak status` toont de taak, en het logboek eindigt zonder fout
- [ ] Een test-export in `inbox/chatgpt/` staat binnen een paar minuten in `inbox/verwerkt/`
- [ ] Je kunt vanaf je telefoon een Claude-sessie op de Mac mini zien en besturen
- [ ] **Herstarttest:** start de Mac mini opnieuw op en log in. Werkt alles daarna weer vanzelf?

## Goed om te weten

- **Gebruikslimiet van Claude Pro.** "24/7" betekent hier *altijd bereikbaar*, niet *altijd aan het werk*. De nachtelijke taak gebruikt Claude helemaal niet. Alleen vragen en opdrachten die jij geeft, tellen mee.
- **Programma's van anderen die Claude gebruiken**, zoals OpenClaw, vallen sinds april 2026 niet meer onder je Pro-abonnement. Gebruik daarom Claude Code zelf. Orca start de echte Claude Code.
- **Alleen persoonlijke gegevens.** Ook op de Mac mini horen geen werk- of patiëntgegevens.
