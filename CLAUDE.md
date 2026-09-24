# Instructies voor Claude Code

Dit is Kims persoonlijke archief. Antwoord in het Nederlands, in heldere taal.

## Vragen over het archief beantwoorden

Als Kim iets vraagt over eerdere gesprekken, projecten of documenten ("wat heb ik besproken over…", "zoek mijn notities over…"):

1. Zoek eerst met de zoekindex: `python -m mainframe zoek <woorden>`. Filter waar nuttig met `--bron` (claude, chatgpt, claude-code, google-drive, onenote, notebooklm) of `--project`.
2. Probeer meerdere zoektermen: synoniemen, afkortingen en Engelse termen.
3. Lees daarna de gevonden bestanden in `archief/` voor de volledige context.
4. Noem in je antwoord altijd de bronnen, met datum en bestandspad, zodat Kim ze kan openen.
5. Staat iets niet in het archief? Zeg dat dan eerlijk en vul het niet aan uit eigen kennis zonder dat erbij te zeggen.

## Regels

- Het archief (`archief/`, `inbox/`, `.mainframe/`) is privé. Commit of push het nooit en stuur het niet naar externe diensten.
- Pas archiefbestanden niet met de hand aan. Ze worden bij de volgende import opnieuw geschreven. Wijzig in plaats daarvan de importer.
- De code gebruikt alleen de standaardbibliotheek van Python. Voeg geen afhankelijkheden toe zonder overleg.
- Draai na elke codewijziging de tests: `python -m unittest discover -s tests`.
- Het archiefformaat staat in `docs/architectuur.md`. Houd het daarmee in lijn.
