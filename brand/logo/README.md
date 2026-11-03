# Logo

Offizielles Logo „ChemBioMed Cards – by AT Medical GmbH®“, von AT Medical bereitgestellt.

| Datei | Inhalt | Verwendung |
|---|---|---|
| `source/chembiomed-cards-logo.png` | **Original** (1672 × 941 px, RGB) – unverändert | Quelle aller Varianten |
| `chembiomed-cards-logo-full.png` | vollständiges Logo inkl. Unterzeilen, transparent | Titelblätter, Druckpaket-Cover, Online-Startseite |
| `chembiomed-cards-logo-compact.png` | Bildmarke + Wortmarke ohne Unterzeilen, transparent | **Kartenkopf** (rechts oben, 9,6 mm hoch) |
| `chembiomed-cards-mark.png` | nur Bildmarke (Kartenstapel), transparent | Favicon/App-Icon, kleine Flächen |
| `chembiomed-cards-logo-full.svg` | Vektor-Nachzeichnung des vollständigen Logos | Druck (Boxen, Verpackung) – Abnahme offen |

Die Varianten sind **reine Ausschnitte** des Originals (nichts neu gezeichnet) und werden mit
`python3 scripts/derive_logo_assets.py` reproduzierbar erzeugt. Die Unterzeilen fehlen im
Kartenkopf, weil sie bei 9,6 mm Logohöhe kleiner als 1,3 mm und damit im Druck unlesbar wären;
die Urheberangabe „© AT Medical GmbH“ steht in der Fußzeile jeder Karte.

Logofarben (gemessen, als Tokens in `brand/design-tokens/chembiomed.tokens.json` → `card.logo_palette`):
Navy `#03204c` (Chem) · Petrol `#06807d` (Bio) · Rot `#a90411` (Med) · Grau `#717479` (Unterzeile).

**Vektorfassung:** `chembiomed-cards-logo-full.svg` ist eine **automatische Nachzeichnung** des
Rasteroriginals (`python3 scripts/vectorize_logo.py --check`, Flächenübereinstimmung Navy/Petrol/Rot
95–98 %). Sie ist für Druckboxen und Verpackung gedacht, aber noch **von AT Medical abzunehmen**.
Liegt eine Originalvektordatei des Logo-Erstellers vor, ersetzt sie die Nachzeichnung.
