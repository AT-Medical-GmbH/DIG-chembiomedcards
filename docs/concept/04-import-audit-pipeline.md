# 04 — Import- & Audit-Pipeline

Die vorhandenen Karten werden **nach** dieser Konzeptphase separat hochgeladen. Dieses Kapitel
beschreibt die automatisierte Verarbeitungskette, die dann greift. Ziel: **kein manuelles
Sortieren von Bildern**, sondern eine saubere, reproduzierbare Pipeline mit nachvollziehbaren
Berichten.

## 1. Pipeline-Stufen im Überblick

```
input/uploaded_raw/   (ZIPs, Bilder, CSV/TXT/HTML/JSON, Manifeste)
        │  1) extract_uploaded_files.py
        ▼
input/extracted/      (entpackt, dedupliziert nach Hash)
        │  2) audit_cards.py
        ├────────────▶ input/rejected/        (Sammelbilder, Raster, Defekte)
        ▼
data/audit_report.json + reports/*.md
        │  3) normalize_cards.py   (interaktiv/semi-automatisch)
        ▼
data/cards/<card_id>.yaml  +  data/cards_master.json
        │  4) validate_output.py
        ▼
freigegeben für Generierung (Kap. 06)
```

## 2. Stufe 1 — Extraktion (`extract_uploaded_files.py`)

- Entpackt **alle** ZIPs rekursiv nach `input/extracted/` (jedes Archiv in eigenes Unterverzeichnis).
- Erfasst alle **Bilddateien** (PNG/JPG/JPEG/WEBP/SVG/PDF) und alle **Begleitdateien**
  (CSV/TXT/HTML/JSON/`manifest*`).
- **Sicherheitsmaßnahmen** (Umgang mit nicht vertrauenswürdigen Uploads):
  - Zip-Slip-Schutz (keine Pfade außerhalb des Zielordners),
  - Dekompressionslimits (Zip-Bomb-Schutz),
  - Skripte laufen mit `python -I` und liegen **nicht** im Datenverzeichnis.
- Dedupliziert identische Dateien über SHA-256; führt eine `extracted_manifest.json`
  (Originalpfad, Hash, Größe, Format, Maße).

## 3. Stufe 2 — Audit (`audit_cards.py`)

Das Audit **klassifiziert** jede Datei und **paart** Vorder-/Rückseiten.

### 3.1 Paarung Vorder-/Rückseite
Heuristik, in dieser Reihenfolge:
1. **Manifest** (falls vorhanden) — autoritativ.
2. **Dateinamen-Konvention** — Suffixe `_front`/`_back`, `_v`/`_r`, `_vorne`/`_hinten`, `-1`/`-2`.
3. **Pfadstruktur** — `.../front/xyz.png` ↔ `.../back/xyz.png`.
4. **Reihenfolge/Nummerierung** als letzter Rückfall (markiert als `pairing: heuristic`).

### 3.2 Erkennung fehlerhafter Bilder (→ `input/rejected/`)
Automatische Ablehnung bzw. Markierung für:
- **Sammel-/Rasterbilder** (mehrere Karten auf einer Fläche): Erkennung über
  (a) Seitenverhältnis weit außerhalb der A6-quer-Norm (≈ 1,41:1), (b) interne
  Gitter-/Trennlinien-Detektion (Kantenprojektion), (c) Dateiname (`sheet`, `grid`, `raster`,
  `collage`, `montage`), (d) Maße = Vielfaches der Einzelkartenmaße.
- **Schwarzer Zusatzrand** / Letterboxing: Randpixel-Analyse.
- **Defekte/unvollständige** Dateien: nicht dekodierbar, 0 Byte, Mindestauflösung unterschritten.
- **Dubletten**: identischer Hash **oder** perzeptueller Hash (pHash) über Schwellwert.

Abgelehnte Dateien werden **verschoben** (nicht gelöscht) nach `input/rejected/` mit Begründung
im Report — nichts geht verloren, alles ist nachvollziehbar.

### 3.3 Geprüfte Attribute je Karte
Bildmaße · Seitenverhältnis · Dateigröße · Namenskonvention · Existenz Vorder- **und**
Rückseite · Dubletten · offensichtlich falsche/unvollständige Karten · falsches Layout ·
schwarzer Zusatzrand · Mehrfachkarten-auf-einem-Bild.

## 4. Inventar (pro Karte)

`audit_cards.py` erzeugt `data/audit_report.json` mit je Karte:

```
card_id · title (soweit ableitbar) · primary_category · secondary_categories · tags ·
front_file · back_file · source (Original-Upload-Pfad) · status · review_status ·
layout_status · notes[] · pairing_method · image_meta{front,back}
```

`status` ∈ `{ok, needs_pairing, missing_back, missing_front, rejected, duplicate, review_needed}`.

## 5. Stufe 3 — Normalisierung (`normalize_cards.py`)

Überführt bestätigte Inventareinträge in das **kanonische Datenmodell** (Kap. 02):
- erzeugt/aktualisiert `data/cards/<card_id>.yaml`,
- vereinheitlicht IDs, Slugs, Kategorien, Tags (gegen `categories.yaml`/`tags.yaml`),
- gleicht Stoffnamen gegen `substances.yaml` ab (Synonym-Auflösung),
- setzt Default-`review_status: needs_review` für alles, was nicht eindeutig ist,
- baut `data/cards_master.json`.

> **Wichtig:** Normalisierung erzeugt **Datensätze**, nicht Bilder. Die *einheitlichen* Karten
> werden anschließend aus dem Datenmodell **neu generiert** (Kap. 06) — die hochgeladenen
> Alt-Bilder dienen als Inhaltsquelle/Referenz, nicht als finales Artefakt. So ist das Ziel
> „alle Karten in einheitlichem Layout“ erreichbar.

## 6. Stufe 4 — Validierung (`validate_output.py`)

Prüft `cards_master.json` gegen das JSON-Schema (Kap. 02 §5) und die Konsistenzregeln; bricht
bei harten Fehlern ab. Erzeugt `reports/export_validation.md`.

## 7. Erzeugte Berichte

| Datei | Inhalt |
|-------|--------|
| `reports/final_inventory.md` | vollständiges Kartenverzeichnis mit Status je Karte |
| `reports/duplicate_cards.md` | erkannte Dubletten (exakt + perzeptuell) mit Entscheidung |
| `reports/rejected_files.md` | abgelehnte Dateien + Begründung (Sammelbild, Rand, defekt …) |
| `reports/missing_cards.md` | fehlende Vorder-/Rückseiten **und** fehlende Soll-Karten (Kap. 14) |
| `reports/content_review.md` | fachliche Auffälligkeiten / `review_needed`-Liste |
| `reports/layout_review.md` | Layout-Auffälligkeiten (Maße, Rand, Lesbarkeit) |

## 8. Semi-automatisch, mit Mensch-in-der-Schleife

Die Pipeline ist auf **maximale Automatisierung** ausgelegt, aber jede nicht eindeutige
Entscheidung (unsichere Paarung, mögliche Dublette, vermutetes Sammelbild) wird **nicht geraten**,
sondern als `review_needed` im Report gelistet und bleibt bis zur Freigabe blockiert. Das erfüllt
die Leitplanke „Bei Unsicherheit review_needed setzen“.

## 9. Verhältnis zu bestehenden Skripten

Der Bestand enthält bereits `scripts/generate_card_registry.py`,
`scripts/validate_card_metadata.py`, `scripts/generate_qr_codes.py`,
`scripts/export_print_batch.py`. Diese werden **weiterverwendet** und an das kanonische
`cards_master.json` angebunden; die neuen Skripte (`extract_/audit_/normalize_`) ergänzen den
Import-Vorlauf. Eine detaillierte Zuordnung steht in [06 — Generierungs-Pipeline](06-generation-pipeline.md).
