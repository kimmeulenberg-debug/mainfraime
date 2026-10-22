# Instructies voor Claude Code

Dit is Kims persoonlijke archief. Antwoord in het Nederlands, in heldere taal.

## Vragen over het archief beantwoorden

Als Kim iets vraagt over eerdere gesprekken, projecten of documenten ("wat heb ik besproken over…", "zoek mijn notities over…"):

0. Lees mijn vaste context: `python3 -m mainframe geheugen` (over mij, lopende projecten, voorkeuren).
1. Zoek met de zoekindex: `python -m mainframe zoek <woorden>`. Filter waar nuttig met `--bron` (claude, chatgpt, claude-code, google-drive, onenote, notebooklm) of `--project`.
2. Probeer meerdere zoektermen: synoniemen, afkortingen en Engelse termen.
3. Lees daarna de gevonden bestanden voor de volledige context. `zoek` toont het volledige pad. Het archief staat in Google Drive, niet in de map `archief/` van de repository. `python3 -m mainframe instellen` toont waar.
4. Noem in je antwoord altijd de bronnen, met datum en bestandspad, zodat Kim ze kan openen.
5. Staat iets niet in het archief? Zeg dat dan eerlijk en vul het niet aan uit eigen kennis zonder dat erbij te zeggen.

Vaste opdrachten staan in `.claude/commands/`: `/archief`, `/weekoverzicht`, `/onthoud` en `/inbox`.

## Geheugen

- Het geheugen staat in `<archief>/geheugen/`. Dat zijn korte Markdown-bestanden die je wel mag aanpassen, maar alleen als ik daarom vraag (bijvoorbeeld met `/onthoud`) of nadat ik akkoord heb gegeven.
- Houd ze kort en actueel: werk bij in plaats van toe te voegen.

## Regels

- Het archief (de map uit `instellen`, en `archief/`, `inbox/` en `.mainframe/`) is privé. Commit of push het nooit en stuur het niet naar externe diensten.
- Pas archiefstukken (alles buiten `geheugen/`) niet met de hand aan. Ze worden bij de volgende import opnieuw geschreven. Wijzig in plaats daarvan de importer.
- De code gebruikt alleen de standaardbibliotheek van Python. Voeg geen afhankelijkheden toe zonder overleg.
- Op de Mac mini draait elke nacht `python3 -m mainframe onderhoud` via launchd (`python3 -m mainframe taak status`).
- Draai na elke codewijziging de tests: `python -m unittest discover -s tests`.
- Het archiefformaat staat in `docs/architectuur.md`. Houd het daarmee in lijn.
