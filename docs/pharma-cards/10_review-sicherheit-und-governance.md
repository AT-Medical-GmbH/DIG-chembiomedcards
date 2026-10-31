# 10 — Review, Sicherheit & medizinische Governance

**Dokument:** Qualitätssicherung, Review-Workflow, Warnlevel, Dosierungspolitik, Export-Gating
**Handover-Phasen:** 14 (Qualitätssicherung), 17 (Sicherheit/Verantwortung)

---

## 1. Grundsatz

Pharma Cards ist **Ausbildungs- und Lernmaterial**, keine verbindliche Therapieanweisung. Das System
unterscheidet deutlich zwischen Lerninhalt und klinischer Handlungsanweisung. Medizinische Inhalte
durchlaufen einen verpflichtenden, dokumentierten Review, bevor sie freigegeben/exportiert werden.

---

## 2. Inhaltliche Qualitätssicherung (Prüfliste je Karte)

Jede Karte wird geprüft auf: korrekter Wirkstoffname & Schreibweise · korrekte Wirkstoffklasse ·
fachlich plausibler Wirkmechanismus · korrekte klinische Relevanz · korrekte toxikologische Relevanz ·
korrekte Antidot-Zuordnung · relevante Nebenwirkungen/Kontraindikationen/Interaktionen · keine
veralteten/missverständlichen Aussagen · keine Dopplungen · keine überlangen Rückseiten · konsistente
Begriffe · passende Kategorie/Tags · angemessener Warnlevel · gesetzter Review-Status.

**Bei Unsicherheit:** nicht raten → `clinical_review_needed` bzw. `toxicology_review_needed` setzen,
knappe Begründung dokumentieren, Korrekturvorschlag machen.

Automatisierte Vorprüfungen (im Audit, Dok. 11): Pflichtfelder, Scope-Enums, Rückseitenlänge,
Dubletten (Wirkstoff/Slug), Dosierungs-Flag-Konsistenz, Quellenpflicht.

---

## 3. Review-Workflow (verbindlich)

Statusmodell (`cards/PH/scope/review_status.yaml`):

```
draft ─▶ needs_review ─▶ ┌ clinical_review_needed ┐ ─▶ reviewed ─▶ approved
                         └ toxicology_review_needed┘
                                                        (deprecated / archived jederzeit)
```

- **Rollen:** `reviewer_pharm` gibt klinisch-pharmakologische Aussagen frei, `reviewer_tox`
  toxikologische Aussagen/Antidote; `editor` erstellt/pflegt; `admin` verwaltet.
- **Protokollierung:** jede Reviewentscheidung → `review_events` (card_id, reviewer, review_type,
  status, notes, timestamp). Jede inhaltliche Änderung → `card_versions` (Snapshot + change_note).
- **Pflicht:** Karten mit klinischer/toxikologischer Relevanz müssen das jeweilige Review durchlaufen,
  bevor `approved`.
- **Alterung:** `update_needed`-Flag stößt Re-Review an (Leitlinien-/Zulassungsänderungen).

---

## 4. Dosierungspolitik (hart)

- **Prinzip vor Zahl:** Standardmäßig Dosierungs*prinzipien* statt exakter Dosen (`dose_principles`).
- Wird eine **konkrete Zahlendosis** geführt (`dose_contains_numeric: true`), dann **zwingend**:
  (a) mindestens eine `reference` (Quelle/Leitlinie mit Jahr), und
  (b) `review_status` ∈ {clinical/toxicology_review_needed, reviewed, approved} — nie als `draft` final.
- Keine ungeprüften Dosierungen werden auf `approved` gesetzt.
- Hochrisikomedikamente, Antidote, Katecholamine, Antikoagulanzien besonders markiert (`warning_level`).

---

## 5. Warnlevel (`cards/PH/scope/warning_levels.yaml`)

`low · moderate · high · critical`. Beispiele `critical`: Hochrisikomedikamente, Antidote,
Katecholamine, Antikoagulanzien, pädiatrische Dosierungen, Toxikologie-Algorithmen,
Schwangerschaft/Stillzeit, Nieren-/Leberinsuffizienz-Anpassungen.

---

## 6. Export-Gating (durchgesetzt, nicht nur Policy)

`validate_output.py` erzwingt vor jedem Export/Seed:

| Warnlevel | Export erlaubt ab |
|---|---|
| `low` | `reviewed` oder `approved` (empfohlen); technisch ab needs_review blockiert für Print |
| `moderate` | `reviewed` oder `approved` |
| `high` | `reviewed` oder `approved` |
| `critical` | **nur `approved`** |

Optional global erzwingbar: „Export nur approved/reviewed Karten“. Admin-Warnung bei nicht geprüften
Inhalten im Redaktions-UI.

---

## 7. Kennzeichnung & Haftung

- Jede Ausgabe trägt den Hinweis „Ausbildungs-/Lernmaterial, keine Therapieanweisung“.
- Quellen und Aktualisierungsdatum werden je Karte gespeichert (`references`, `updated_at`).
- Änderungsverlauf pro Karte dauerhaft (`card_versions`).
- Verantwortlich für fachliche Freigabe: AT Medical GmbH.

---

## 8. Zu erzeugende Reports (Phase 14)

Im Audit-Lauf (Dok. 11) erzeugt/gepflegt, unter `docs/pharma-cards/reports/`:

- `content_scope.md` — Umfang/Abdeckung je Kategorie/Welle (**angelegt**).
- `missing_cards.md` — geplante, noch fehlende Karten (**angelegt**).
- `content_review.md` — inhaltlicher Prüfstatus je Karte (**angelegt**).
- `clinical_safety_review.md` — klinische Sicherheitsprüfung (Folgephase, beim ersten Review-Lauf).
- `cards_review_needed.md` — Liste `*_review_needed`-Karten mit Begründung (Folgephase).
- `final_quality_report.md` — Abschlussbericht Qualität (bei Release).
- zusätzlich entsprechend Handover: `duplicate_cards.md`, `layout_review.md`, `final_inventory.md`,
  `export_validation.md` (bei den jeweiligen Pipeline-Läufen).
