# Kartenvorlage – Layout und Inhalte ändern

ChemBioMed Cards trennt **Layout** und **Inhalt** strikt. Beides lässt sich jederzeit ändern, ohne
das jeweils andere anzufassen. Hintergrund: [ADR-018](../docs/concept/decision-log.md),
[Kap. 05 Kartenlayout](../docs/concept/05-card-layout.md).

| Was ändern? | Datei | Wirkung beim nächsten `make cards` |
|---|---|---|
| **Layout** aller Karten (Aufbau, Schriftgrößen, Abstände, Boxen, Kopf-/Fußzone) | `templates/card_template.html` | alle Karten werden neu erzeugt |
| **Farben, Kartenformat, Schrift** | `brand/design-tokens/chembiomed.tokens.json` → `card` | alle Karten (und später das Online-System) |
| **Register-Tabs** (Reihenfolge, Beschriftung) | `data/categories.yaml` | alle Karten |
| **Inhalt einer einzelnen Karte** | `data/cards/<card_id>.yaml` | nur diese Karte |
| Darstellung der Fischer-Projektion / Strukturformeln | `scripts/cbm/fischer.py` / `scripts/cbm/molecule.py` | alle Karten dieses Typs |

Der Generator merkt sich je Karte einen Fingerabdruck aus Kartendaten, Vorlage, Tokens und
Renderern. Deshalb rendert `make cards` immer genau das, was sich geändert hat – nichts muss von
Hand angestoßen werden.

## Layout ändern

1. `templates/card_template.html` bearbeiten. Die Datei ist gegliedert in
   - `<style>` – das komplette Karten-CSS (Kopfzone, Fußzone, Vorderseite, Rückseite, Boxen),
   - `header()` – sechs Register-Tabs und Wortmarke,
   - **Vorderseite** – zeigt je nach `front_content.render` Fischer-Projektion, Strukturformel,
     Bezeichnung oder Formel,
   - **Rückseite** – feste Reihenfolge: Titel · Klassifikation · Eigenschaften · Biochemie | Klinik ·
     Molekularbio · Merke.
2. `make cards` – alle Karten werden neu erzeugt.
3. `reports/layout_review.md` prüfen. Der Generator meldet u. a. Text, der über die Rückseite
   hinausläuft, eine falsche Tab-Leiste, eine nicht geladene Schrift und zu dicht stehende
   Atombeschriftungen. Bei Befunden bricht `make cards` mit Fehlercode ab.
4. Übersichten ansehen: `generated/preview/contact_sheet_<themengruppe>.png`.

Beispiel: Rückseiten-Schrift größer → in `.box li` und `.box p` den Wert `font-size` ändern,
`make cards`, Überlauf-Befunde im Report kontrollieren.

## Inhalt einer Karte austauschen

1. `data/cards/<card_id>.yaml` öffnen und ändern – z. B. eine Aussage unter
   `back_sections.clinical_relevance`, den Merksatz unter `back_sections.mnemonic` oder die Struktur
   unter `front_content`.
2. `version` erhöhen (Patch für Korrekturen) und `updated_at` setzen.
3. `make build` – prüft die Datei, rendert **nur diese Karte** neu und aktualisiert die Berichte.

Eine Karte komplett ersetzen: die YAML-Datei durch eine neue mit derselben `card_id` ersetzen.
Eine neue Karte anlegen: eine bestehende Datei als Muster kopieren, `card_id`, `slug` und Inhalte
anpassen, neue Tags vorher in `data/tags.yaml` eintragen.

### Vorderseitentypen

| `front_content.render` | Verwendung | Pflichtfelder |
|---|---|---|
| `fischer_projection` | α-Aminosäuren (Konvention Kap. 05 §5.1, kein Name) | `side_chain` oder `special` |
| `molecule` | andere Moleküle als Skelettformel | `smiles`, Herkunft (`pubchem_cid` oder `structure_note`) |
| `term` | Vitamine, Peptidhormone – nur die Bezeichnung | `text` |
| `formula` | Ionen und kleine Teilchen (z. B. Ca²⁺) | `text`, nur `<sub>`/`<sup>` erlaubt |

Optionen für `molecule`: `form: physiological` (Säure-/Phosphatgruppen deprotoniert),
`labels` für Platzhalteratome (`[*:1]` → z. B. „CoA“), `layout: rdkit|coordgen`, falls der
Generator zu dicht stehende Beschriftungen meldet.
