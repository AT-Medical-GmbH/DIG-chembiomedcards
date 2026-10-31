# Scripts

Content-Pipeline für ChemBioMed Cards. Quelle der Wahrheit sind die Kartendatensätze unter
`data/cards/<card_id>.yaml`; alle Bilder und PDFs werden daraus erzeugt
(siehe [`docs/concept/06-generation-pipeline.md`](../docs/concept/06-generation-pipeline.md)).

| Skript | Zweck |
|---|---|
| `validate_cards.py` | Prüft Kartendaten gegen `data/schema/card.schema.json` und die Projektregeln (ID↔Modul, Tabs, Tags, kein Name auf Aminosäure-Vorderseiten, Freigaberegeln). |
| `generate_cards.py` | Rendert je Karte Vorder-/Rückseiten-PNG (300 dpi), 2-seitiges PDF (148 × 105 mm), Struktur-SVG, Vorschau; schreibt `data/cards_master.json`, `generated/manifest.json`, `reports/layout_review.md`. Unveränderte Karten werden übersprungen. |
| `report_review_status.py` | Erzeugt `reports/cards_review_needed.md` (Arbeitsliste Fachreview). |
| `cbm/` | Gemeinsame Bausteine: `model.py` (Laden/Validieren), `fischer.py` (Fischer-Projektion als SVG). |
| `generate_card_registry.py`, `validate_card_metadata.py`, `generate_qr_codes.py`, `export_print_batch.py` | Bestehende Registry-/Print-Hilfen (werden schrittweise an `cards_master.json` angebunden). |

## Schnellstart

```bash
pip install -r requirements.txt
python -m playwright install chromium   # entfällt, wenn Chromium bereits vorhanden ist
make build                               # validate + cards + reports
```

Eine einzelne Karte neu rendern: `python3 scripts/generate_cards.py --filter bc_107 --force`.

## Neue Karte anlegen

1. `data/cards/<card_id>.yaml` nach dem Muster einer bestehenden Karte anlegen
   (`review_status: needs_review`).
2. Neue Tags vorher in `data/tags.yaml` eintragen.
3. `make build` – Validierung, Rendering und Berichte laufen durch; Befunde stehen in
   `reports/layout_review.md`.
