# Changelog

## 2026-10-31
- Content-Pipeline umgesetzt: Kartenschema (`data/schema/card.schema.json`), Kategorien/Tags
  (`data/categories.yaml`, `data/tags.yaml`), Design-Tokens für Karten, HTML/CSS-Templates mit fester
  Tab-Leiste, Fischer-Projektion als SVG (`scripts/cbm/fischer.py`)
- `scripts/validate_cards.py`, `scripts/generate_cards.py` (PNG 300 dpi, PDF 148 × 105 mm, SVG,
  Vorschau, Manifest, Layout-Report), `scripts/report_review_status.py`, `Makefile`, `requirements.txt`
- Pilotserie: 20 proteinogene Aminosäuren (`bc_098`–`bc_117`, IDs vorläufig, Fachreview offen)
- CI validiert zusätzlich `data/cards/*.yaml`
- Konzept aktualisiert: Produktion aus Daten (ADR-014), Startumfang (ADR-015), vorläufige IDs (ADR-016),
  QR nur Rückseite / Logo-Platzhalter (ADR-017)

## 2026-10-09
- Vollständiges Gesamtkonzept unter `docs/concept/` ausgearbeitet (00–16 + Decision Log + offene Fragen)
- Drei-Ebenen-Architektur, kanonisches Content-Modell, Import-/Audit-Pipeline, Kartenlayout- und
  Generierungs-Pipeline, Print-/Moodle-Export, Online-Lernsystem (Funktion, Architektur, Datenmodell,
  UI/UX), Erweiterbarkeit, QS, Deployment sowie Phasenplan & Akzeptanzkriterien dokumentiert
- Architekturentscheidungen als ADR-Kurzform festgehalten; offene Abstimmungspunkte markiert
- Platzhalter `online-platform/database/data-model.md` und `lms-content/moodle-integration.md` auf
  die maßgeblichen Konzeptkapitel verwiesen; README um Konzept-Einstieg ergänzt

## 2026-05-15
- Initiale Repository-Struktur für ChemBioMed Cards angelegt
- Bereiche für Dokumentation, Card-System, Registry, Print-Produktion und Onlineplattform vorbereitet
