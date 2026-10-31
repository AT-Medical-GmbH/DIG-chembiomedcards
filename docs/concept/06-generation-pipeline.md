# 06 — Technische Generierungs-Pipeline

Ziel: Karten **nicht manuell**, sondern reproduzierbar aus Daten + Templates erzeugen.

## 1. Technologieentscheidung

| Aspekt | Wahl | Begründung |
|--------|------|------------|
| Datenquelle | `data/cards_master.json` (aus YAML) | Eine validierte Quelle (Kap. 02) |
| Layout-Sprache | **HTML + CSS** (primär), **SVG** (editierbare Zweitquelle) | HTML/CSS = präzise Typo/Flow; SVG = vektor-editierbar |
| Render-Engine | **Playwright (Chromium)** | In der Umgebung vorinstalliert; pixelgenau; PNG **und** PDF aus demselben DOM |
| Templating | Jinja2 (Python) | Gleiche Sprache wie Pipeline; Tokens/Datei-Includes |
| Struktur-/Chemie-Rendering | SMILES → 2D (z. B. RDKit/Indigo) bzw. kuratiertes SVG | Aminosäuren folgen fester Fischer-Konvention (Kap. 05) |

Die Entscheidung HTML/CSS→Playwright ist bewusst dieselbe Engine wie im Online-Export-Service
(Kap. 10): **ein** Layout, konsistent in Print, Online und On-Demand-Download.

## 2. Ablauf (`generate_cards.py`)

```
cards_master.json
   └─ je Karte:
        1. Template wählen nach front_type / Rückseiten-Schema
        2. Tokens + Kartendaten in Jinja2 einsetzen
        3. HTML(front) + HTML(back) rendern
        4. Playwright → PNG (300 dpi Druck + 2× Web) und PDF (Einzelkarte)
        5. optional SVG(front/back) ableiten/ablegen
        6. Preview-Thumbnail erzeugen
   └─ Index/Manifest schreiben (generated/manifest.json)
```

## 3. Ausgaben & Namenskonvention

```
generated/
  individual/
    front/<card_id>_front.png        # z. B. bc_014_front.png
    back/<card_id>_back.png
    svg/<card_id>_{front,back}.svg
    pdf/<card_id>.pdf                # Vorder+Rückseite paarweise
  preview/<card_id>.png              # kleines Vorschaubild
  manifest.json                      # card_id → Pfade, Hashes, Maße, Build-Zeit
```

Jede Karte erhält: eindeutige ID, eindeutige Dateinamen, Front-PNG, Back-PNG, optional
Front/Back-SVG, Einzelkarten-PDF, Preview.

## 4. Templates

**Umgesetzt (ADR-018): eine zentrale Kartenvorlage** – `templates/card_template.html` enthält
CSS, Kopfzone (Register-Tabs, Wortmarke), Vorder- und Rückseite in einer Datei. Eine Änderung dort
wirkt beim nächsten Build auf alle Karten. Bedienung: [`templates/README.md`](../../templates/README.md).

| Baustein | Ort | Ändern wirkt auf |
|----------|-----|------------------|
| Layout, Typografie, Abstände | `templates/card_template.html` | alle Karten |
| Farben, Format, Schrift | `brand/design-tokens/chembiomed.tokens.json` (`card.*`) | alle Karten + Online-System |
| Register-Tabs | `data/categories.yaml` | alle Karten |
| Inhalt einer Karte | `data/cards/<card_id>.yaml` | nur diese Karte |
| Fischer-Projektion / Strukturformel | `scripts/cbm/fischer.py` / `scripts/cbm/molecule.py` | alle Karten des Typs |

Vorderseitentypen (`front_content.render`): `fischer_projection` (α-Aminosäuren), `molecule`
(Strukturformel aus SMILES, ADR-019), `term` (Bezeichnung, z. B. Vitamine, Peptidhormone),
`formula` (Summenformel für Ionen/kleine Teilchen).

Geplant, noch nicht umgesetzt: `print_sheet_template.html` (A4/A3-Montage, Kap. 07) und eine
Online-Kartenkomponente (Kap. 12), die dieselben Tokens nutzt.

## 5. Reproduzierbarkeit & Inkrementalität

- **Content-Hash je Karte** (Kartendaten + Template-Version + Token-Version) → nur geänderte
  Karten werden neu gerendert (schneller Rebuild), Ergebnis aber bit-stabil.
- Build-Metadaten (`manifest.json`) erlauben Validierung „jede erwartete Karte existiert“
  (`validate_output.py`, Kap. 04 §6).
- Ein `make build` erzeugt den **gesamten** Artefaktstand aus einem Git-Commit.

## 6. Zuordnung bestehender Skripte

| Bestehend | Rolle künftig |
|-----------|---------------|
| `scripts/generate_card_registry.py` | erzeugt flache `cards.master.csv` aus `cards_master.json` |
| `scripts/validate_card_metadata.py` | geht in `validate_output.py` auf / bleibt als Pre-Check |
| `scripts/generate_qr_codes.py` | QR-Erzeugung für `qr_url` (in Karten eingebettet) |
| `scripts/export_print_batch.py` | Grundlage für `generate_print_pdfs.py` (Kap. 07) |

## 7. Qualitäts-Gates der Generierung

- **Overflow-Check:** Rückseiten dürfen nicht über die Inhaltszone laufen (Playwright misst
  Layout-Boxen; Overflow → `layout_review`-Warnung statt stiller Abschneidung).
- **Kontrast-Check:** Text/Hintergrund-Kontrast ≥ WCAG AA (automatisch je Box).
- **AS-Vorderseiten-Lint:** kein Name auf Aminosäure-Fronten (Kap. 05 §5.1).
- **Fehlende Assets:** Struktur ohne SMILES/SVG → Build-Fehler.

Ergebnisse fließen in `reports/layout_review.md`.
