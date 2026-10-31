# Report — Content Review (PH / Pharma Cards)

**Stand:** 2026-10-09 · **Bedeutung:** Inhaltlicher Prüfstatus je Karte.

Dieser Report wird in Folgephasen durch `audit_cards.py` erzeugt und listet je Karte den
`review_status`, den `warning_level` und offene Prüfpunkte. Status heute:

## Übersicht

| Karte | Typ | warning_level | review_status | Hinweis |
|---|---|---|---|---|
| `cards/PH/examples/ph_020_naloxon.yaml` | antidote | critical | toxicology_review_needed | Beispielkarte, fachliche Freigabe ausstehend |
| `cards/PH/examples/ph_006_agonist.yaml` | overview | low | needs_review | Beispielkarte, didaktische Prinzipkarte |

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
