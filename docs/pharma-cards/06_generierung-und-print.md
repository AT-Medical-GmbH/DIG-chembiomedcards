# 06 — Technische Generierung & Druckproduktion

**Dokument:** Reproduzierbare Kartengenerierung, Einzelkarten, Druckbögen, Druckpakete
**Handover-Phasen:** 6 (Generierung), 7 (Druckfertige Dateien)

---

## 1. Generierungs-Pipeline (Phase 6)

Deterministische Kette, orchestriert über `scripts/` (erweitert) und eine `Makefile`/`make`-Fassade:

```
cards/PH/metadata/*.yaml
   │  validate_card_metadata.py (erweitert: PH-Content-Schema + Scope-Enums)
   ▼
cards/registry/cards.master.csv   ← generate_card_registry.py (YAML→CSV-Mapping fertigstellen)
   │
   ├─ generate_cards.py  (HTML/CSS-Template + Playwright → PNG/SVG/PDF)
   │     → exports/web/ph/<card_id>_front.png / _back.png
   │     → cards/PH/front/ , cards/PH/back/ (Registry-Pfade front_asset/back_asset)
   │     → exports/pdf/ph/<card_id>.pdf (Einzelkarte Front+Back)
   │     → optional SVG-Quellen
   ├─ generate_qr_codes.py (bestehend) → exports/qr/ph/<card_id>.svg
   └─ validate_output.py (neu) → prüft Vorhandensein/Abmessungen/Dateinamen
```

### 1.1 Rendering-Technologie

- **Playwright (Chromium, vorinstalliert)** rendert die HTML/CSS-Templates nach PNG und PDF.
  `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` ist gesetzt — **kein** `playwright install`.
- Feste Viewport-/DPI-Einstellungen für reproduzierbare 300-dpi-Ausgabe im Fertigformat.
- SVG als editierbare Quelle, wo sinnvoll (Schemata, Strukturformeln).

### 1.2 Pro Karte erzeugte Artefakte

| Artefakt | Pfad | Zweck |
|---|---|---|
| Front-PNG | `cards/PH/front/<slug>_front.png` | Online/Moodle |
| Back-PNG | `cards/PH/back/<slug>_back.png` | Online/Moodle |
| Front/Back-SVG (opt.) | `exports/web/ph/svg/` | editierbare Quelle |
| Einzelkarten-PDF | `exports/pdf/ph/<card_id>.pdf` | Druck/Download |
| QR-SVG | `exports/qr/ph/<card_id>.svg` | Print |

Eindeutige ID + eindeutiger Dateiname (`slug`) je Karte — eine Datei pro Seite (keine Sammelbilder).

### 1.3 Konvention der Ausgabeverzeichnisse

Da das Repo `exports/{web,pdf,qr,...}` bereits vorsieht, werden PH-Artefakte unter `exports/<ziel>/ph/`
abgelegt (modul-scoped), analog für Registry-Pfade `cards/PH/{front,back,print}`.

---

## 2. Druckfertige Dateien (Phase 7)

Alle Druckausgaben folgen der bestehenden Print-Spec (`print-production/specs/`): 148×105 mm,
3 mm Beschnitt, 5 mm Safe Zone, CMYK ISO Coated v2, 300 dpi (QR 600 dpi), PDF/X-1a/X-4.

### 2.1 Varianten

1. **Einzelkarten-PDFs** — je Karte, Vorder-/Rückseite paarweise.
2. **A4-Druckbögen** — mehrere Karten pro Seite, Vorder-/Rückseiten schnitt- und spiegelpassend,
   Schneidemarken, Ränder, optional Beschnittzugabe.
3. **A3-Druckbögen** — optional.
4. **Ausprägungen:** mit/ohne Schnittmarken; 2/4/8 Karten pro Seite (8 nur bei lesbarer Typografie).

Generiert durch `generate_print_sheets.py` (neu, baut auf `export_print_batch.py` auf) mit
Imposition-Logik (Duplex, Spiegelung der Rückseite für korrekten Durchschlag).

### 2.2 Druckpakete

Ablage unter `print-production/exports/ph/` bzw. CI-Release-Artefakte; Benennung an Kategorien/Wellen:

```
Pharma_Cards_Print_Allgemeine_Pharmakologie.zip
Pharma_Cards_Print_Pharmakokinetik_Pharmakodynamik.zip
Pharma_Cards_Print_Notfallmedikamente.zip
Pharma_Cards_Print_Anaesthesie_Intensivmedizin.zip
Pharma_Cards_Print_Antibiotika_Antiinfektiva.zip
Pharma_Cards_Print_Toxikologie.zip
Pharma_Cards_Print_Antidote.zip
Pharma_Cards_Print_Gesamtset.zip
```

Jedes Paket enthält: druckfertige PDF (Bögen), Einzelkarten-PDFs, PNGs, `README_PRINT.md`
(Format, Farbraum, Schnittmarken, Testscan-Hinweis QR).

### 2.3 Export-Gating (Sicherheit)

Nur Karten, deren `review_status`/`warning_level` das Export-Gate erfüllen (Dok. 10), kommen in
Druckpakete. `validate_output.py` bricht ab, wenn eine `critical`-Karte ohne `approved` enthalten wäre.

---

## 3. Skript-Inventar (Soll)

| Skript | Status | Aufgabe |
|---|---|---|
| `validate_card_metadata.py` | vorhanden → erweitern | Registry- + PH-Content- + Scope-Enum-Validierung |
| `generate_card_registry.py` | vorhanden (Scaffold) → fertigstellen | YAML→CSV-Mapping |
| `generate_cards.py` | **neu** | HTML/CSS→PNG/SVG/PDF je Karte (Playwright) |
| `generate_qr_codes.py` | vorhanden | QR-SVG je Karte |
| `generate_print_sheets.py` | **neu** (baut auf `export_print_batch.py`) | A4/A3-Imposition + Schnittmarken |
| `generate_moodle_import.py` | **neu** | Moodle-Pakete (Dok. 07) |
| `generate_online_assets.py` | **neu** | Web-PNG + Seed-JSON für Online-DB |
| `validate_output.py` | **neu** | Vollständigkeit/Abmessungen/Gating der Artefakte |

Alle Skripte: idempotent, `--help`, keine Netzabhängigkeit beim Rendern, CI-aufrufbar.

---

## 4. Umsetzungsstand (2026-10-31)

Implementiert und getestet (`scripts/pharma/tests/`, 33 Tests):

| Variante | Papier | Raster | Maßstab | Marken/Beschnitt |
|---|---|---|---:|---|
| `A4_2up_Schnittmarken` | A4 hoch | 1 × 2 | **100 %** | ja, 3 mm |
| `A4_2up_ohne_Marken` | A4 hoch | 1 × 2 | **100 %** | nein |
| `A4_4up_Schnittmarken` | A4 quer | 2 × 2 | 82 % | ja, 3 mm |
| `A4_8up_kompakt` | A4 hoch | 2 × 4 | 58 % | ja – kleine Schrift, nur Wiederholungsdruck |
| `A3_8up_Schnittmarken` | A3 hoch | 2 × 4 | 88 % | ja, 3 mm |

- Ausrichtung und Raster wählt `compute_layout()` automatisch für den größtmöglichen Maßstab ≤ 100 %.
  DIN A6 passt genau viermal auf A4. Mit Beschnitt und Schnittmarken geht das nur verkleinert.
- Duplex: Rückseitenbögen sind je Wendekante gespiegelt (`--flip long|short`).
- Schnittmarken liegen nur im Außenrand an den Schnittlinien, nie im Beschnitt einer Nachbarkarte.
- **Farbraum:** Chromium erzeugt RGB-PDFs. Für Offsetdruck ist die Wandlung nach PDF/X-4 CMYK
  (ISO Coated v2) in der Druckvorstufe nötig; das steht in jedem `README_PRINT.md`.
- Gating: Release-Pakete enthalten nur exportierbare Karten. Vorschaupakete (`--preview`) liegen
  getrennt unter `dist/preview/` und tragen ein ENTWURF-Wasserzeichen.
