# Report — Content Review (PH / Pharma Cards)

**Stand:** 2026-10-09 · **Bedeutung:** Inhaltlicher Prüfstatus je Karte.

Dieser Report wird in Folgephasen durch `audit_cards.py` erzeugt und listet je Karte den
`review_status`, den `warning_level` und offene Prüfpunkte. Status heute:

## Übersicht

Produktive Tranche R1 in `cards/PH/metadata/`:

| Block | Karten | warning_level | review_status |
|---|---|---|---|
| Allgemeine Pharmakologie | `ph_001`–`ph_019` (19) | low/moderate | needs_review |
| Pharmakokinetik/-dynamik-Mechanismen | `ph_020`–`ph_030` (11) | low/moderate | needs_review |

Klinisch kritische Blöcke (Notfallmedikamente, Toxidrome, Antidote) folgen über den
Fachreview-Workflow; die Antidot-Karte Naloxon (`critical`, `toxicology_review_needed`) wird im
Antidot-ID-Bereich (`ph_1xx`) angelegt. Status je Karte wird durch
`scripts/pharma/validate_output.py` gegen das Export-Gating geprüft.

## Prüfregeln (werden automatisiert angewandt)

- Pflichtfelder vollständig, Scope-Enums gültig.
- `dose_contains_numeric: true` ⇒ Quelle vorhanden **und** Review-Status ≠ draft.
- Antidot-/Katecholamin-/Antikoagulans-Karten ⇒ warning_level ≥ high.
- Rückseite nicht überlang; keine Dubletten (Wirkstoff/Slug).
- Kategorie/Tags/Wirkstoffgruppe plausibel und gültig.

## Grundsatz

Keine Karte wird ohne fachliche Prüfung auf `approved` gesetzt. Bei Unsicherheit gilt
`clinical_review_needed` bzw. `toxicology_review_needed` mit dokumentierter Begründung
(siehe `10_review-sicherheit-und-governance.md`).
