# 02 — Datenmodell

**Dokument:** Kartendatenmodell (Content) + relationales Online-Datenmodell
**Handover-Phasen:** 3 (Kartenschema), 11 (Online-DB)

---

## 1. Grundsatz

Zwei abgestimmte Modelle:

1. **Content-Modell** — YAML je Karte (`cards/PH/metadata/*.yaml`), die editierte Quelle der Wahrheit.
2. **Online-Modell** — relationale PostgreSQL-Tabellen, aus dem Content-Modell geseedet, plus
   nutzer-/betriebsbezogene Tabellen (Fortschritt, Notizen, Reviews, Exporte).

Das Content-Modell ist eine **Obermenge** der bestehenden `cards.master.schema.json`: Alle heutigen
Felder (`card_id`, `slug`, `title`, `module`, `chapter`, `card_type`, `level`, `front_asset`,
`back_asset`, `qr_url`, `lms_url`, `print_status`, `web_status`, `review_status`) bleiben gültig. Die
Pharma-/Tox-spezifischen Felder kommen additiv hinzu. Die abgeleitete `cards.master.csv` enthält nur
die flachen Registry-Felder; die reichen Inhaltsfelder leben im YAML und in der DB.

---

## 2. Content-Modell — vollständiges Kartenschema (PH)

Jede PH-Karte ist ein YAML-Dokument. Felder (⟳ = aus Scope-Konfig validiert, siehe `cards/PH/scope/`):

### 2.1 Identität & Einordnung

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `card_id` | string `^ph_[0-9]{3}$` | ✓ | Eindeutige ID. |
| `slug` | string | ✓ | Dateiname ohne Front/Back-Suffix, z. B. `ph_020_naloxon`. |
| `title` | string | ✓ | Kartentitel. |
| `subtitle` | string | – | Untertitel (z. B. Wirkstoffgruppe). |
| `module` | const `PH` | ✓ | Immer `PH`. |
| `primary_category` | string ⟳ | ✓ | Hauptkategorie (aus `categories.yaml`). |
| `secondary_categories` | string[] ⟳ | – | Nebenkategorien. |
| `topic_group` | string ⟳ | – | Themengruppe/Kapitel. |
| `chapter` | string | ✓ | Fachliches Unterkapitel (Registry-kompatibel). |
| `drug_class` | string ⟳ | – | Wirkstoffgruppe (aus `drug_classes.yaml`). |
| `card_type` | string ⟳ | ✓ | Kartentyp (aus `card_types.yaml`). |
| `front_type` | string ⟳ | ✓ | Typ der Vorderseite (z. B. `substance`, `mechanism`, `toxidrome`, `antidote`, `interaction`, `case`). |
| `level` / `difficulty` | string ⟳ | ✓ | Niveau: `grundlagen`/`beginner` … `clinical`/`advanced`. |

### 2.2 Wirkstoff-/Fachinhalt

| Feld | Typ | Beschreibung |
|---|---|---|
| `substance_name` | string | Wirkstoff (de). |
| `generic_name` | string | INN/Freiname. |
| `trade_names_optional` | string[] | Handelsnamen (optional, nur illustrativ). |
| `mechanism_of_action` | markdown | Wirkmechanismus. |
| `pharmacodynamics` | markdown | PD. |
| `pharmacokinetics` | markdown | PK (LADME-orientiert). |
| `indications` | markdown | Indikationen/klinische Relevanz. |
| `contraindications` | markdown | Kontraindikationen/Warnhinweise. |
| `adverse_effects` | markdown | Nebenwirkungen. |
| `interactions` | markdown | Interaktionen. |
| `monitoring` | markdown | Monitoring/Überwachung. |
| `dose_principles` | markdown | **Dosierungs*prinzipien*** (bevorzugt vor exakten Dosen). |
| `renal_adjustment` | markdown | Anpassung bei Niereninsuffizienz. |
| `hepatic_adjustment` | markdown | Anpassung bei Leberinsuffizienz. |
| `pregnancy_lactation_notes` | markdown | Schwangerschaft/Stillzeit. |

### 2.3 Notfall & Toxikologie

| Feld | Typ | Beschreibung |
|---|---|---|
| `emergency_relevance` | markdown | Notfallrelevanz. |
| `toxicology_relevance` | markdown | Toxikologische Relevanz. |
| `antidote` | string ⟳ | Antidot (aus `antidotes.yaml`). |
| `toxidrome` | string ⟳ | Toxidrom (aus `toxidromes.yaml`). |

### 2.4 Didaktik

| Feld | Typ | Beschreibung |
|---|---|---|
| `clinical_pearls` | markdown | Klinischer Fallstrick / „Merke“. |
| `fun_fact` | string | Didaktischer Merkanker (optional). |
| `mnemonic` | string | Eselsbrücke (optional). |
| `back_sections` | object[] | Strukturierte Rückseiten-Boxen (Titel + Inhalt + Farbrolle, siehe Dok. 05). |
| `front_content` | object | Strukturierte Vorderseite (je nach `front_type`). |
| `learning_objectives` | string[] | Lernziele (Registry-/LMS-kompatibel). |
| `related_cards` | card_id[] | Querverweise. |
| `tags` | string[] ⟳ | Tags (aus `tags.yaml`). |

### 2.5 Sicherheit, Quellen, Status, Versionierung

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `warning_level` | enum ⟳ | ✓ | `low` \| `moderate` \| `high` \| `critical` (aus `warning_levels.yaml`). |
| `review_status` | enum ⟳ | ✓ | `draft` \| `needs_review` \| `clinical_review_needed` \| `toxicology_review_needed` \| `reviewed` \| `approved` \| `deprecated` \| `archived`. |
| `references` | object[] | bedingt | Quellen (Titel, Herausgeber, Jahr, URL/DOI). **Pflicht, sobald konkrete Dosierungen geführt werden.** |
| `source_status` | enum | ✓ | `draft` \| `approved` \| `published`. |
| `dose_contains_numeric` | bool | ✓ | Flag: enthält konkrete Zahlendosen → erzwingt Quelle + Review. |
| `version` | semver string | ✓ | z. B. `0.1.0`. |
| `author` | string | ✓ | Ersteller. |
| `reviewer` | string | – | Fachprüfer (pharma/tox). |
| `created_at` / `updated_at` | date | ✓ | ISO-Datum. |
| `print_status` / `web_status` | enum | ✓ | Produktionsstatus (Registry-kompatibel). |
| `front_asset` / `back_asset` | path | ✓ | Pfad zu generierten Bildern. |
| `qr_url` / `lms_url` | uri | ✓ / – | Stabile Verweise. |

### 2.6 Validierungsregeln (hart)

- `dose_contains_numeric: true` ⇒ `references` nicht leer **und** `review_status` ∈
  {`clinical_review_needed`, `toxicology_review_needed`, `reviewed`, `approved`} (nie `draft` ohne Quelle).
- `antidote`/`toxidrome` müssen in der jeweiligen Scope-Konfig existieren.
- `warning_level: critical` ⇒ Karte darf nur mit `review_status: approved` exportiert werden
  (Export-Gating, Dok. 10).
- Alle ⟳-Felder werden gegen `cards/PH/scope/*.yaml` geprüft (Enum aus Konfig, nicht aus Code).

Das bestehende `cards.master.schema.json` wird um einen additiven PH-Content-Schema-Teil ergänzt
(`cards/registry/ph.content.schema.json`, in Folgephase) — die Registry-CSV-Validierung bleibt unverändert.

---

## 3. Online-Modell — relationale Tabellen (PostgreSQL)

Kernschema (Auszug; vollständige DDL als Alembic-Migration in `online-platform/database/`):

```
cards(id PK, card_id UNIQUE, slug, title, subtitle,
      front_type, front_content JSONB, back_content JSONB,
      primary_category_id FK→categories, drug_class_id FK→drug_classes,
      substance_id FK→substances NULL, card_type, difficulty, level,
      warning_level, review_status, version, qr_url, lms_url,
      front_asset, back_asset, created_at, updated_at)

drug_classes(id PK, name, slug UNIQUE, parent_id FK→drug_classes NULL,
             description, color, icon)

substances(id PK, generic_name, slug UNIQUE, drug_class_id FK,
           trade_names_optional TEXT[], mechanism_summary, clinical_notes,
           toxicology_notes, review_status)

categories(id PK, name, slug UNIQUE, color, icon, sort_order, parent_id NULL)

tags(id PK, name, slug UNIQUE)
card_tags(card_id FK, tag_id FK, PK(card_id, tag_id))

card_versions(id PK, card_id FK, content_snapshot JSONB, changed_by FK→users,
              change_note, created_at)

antidotes(id PK, name, slug UNIQUE, target_intoxication, mechanism, notes)
toxidromes(id PK, name, slug UNIQUE, lead_symptoms, notes)
interaction_pairs(id PK, substance_a FK, substance_b FK, mechanism, consequence, severity)

users(id PK, external_subject UNIQUE NULL,  -- OIDC/Authentik subject
      email, display_name, role, created_at)   -- role: admin|editor|reviewer_pharm|reviewer_tox|teacher|learner

user_progress(id PK, user_id FK, card_id FK, status,
              leitner_box INT, ease_factor NUMERIC, interval_days INT,
              repetitions INT, next_due_at, last_reviewed_at,
              UNIQUE(user_id, card_id))
      -- status: new|learning|unsure|repeat|mastered|later|clinically_important|exam_relevant

user_notes(id PK, user_id FK, card_id FK, note_text, annotation_data JSONB,
           visibility, created_at, updated_at)   -- visibility: private|course|public

review_events(id PK, card_id FK, reviewer_id FK, review_type, status, notes, created_at)
      -- review_type: pharmacology|toxicology|editorial|clinical_safety

exports(id PK, user_id FK NULL, type, category_id FK NULL, file_path, created_at)

learning_sessions(id PK, user_id FK, started_at, ended_at, cards_seen INT,
                  correct INT, mode)   -- mode: learn|repeat|exam|random|due|new

-- optionale/erweiternde Tabellen
course_assignments(id PK, course_ref, card_id FK, assigned_by FK)
moodle_contexts(id PK, course_ref, lti_context_id, package_id)
shared_notes(id PK, note_id FK, scope)
teacher_comments(id PK, teacher_id FK, card_id FK, comment)
```

### 3.1 Abbildung Content → DB

- `front_content` / `back_content` werden als **JSONB** gespeichert (strukturierte Boxen inkl.
  Farbrolle), damit die Online-App aus Feldern rendert — nicht aus Bildern.
- `card_versions.content_snapshot` hält bei jeder inhaltlichen Änderung einen vollständigen
  JSONB-Snapshot (Änderungsverlauf, Pflicht für klinisch relevante Karten, Dok. 10/17).
- Kategorien/Wirkstoffgruppen/Tags/Antidote/Toxidrome werden aus `cards/PH/scope/*.yaml` geseedet —
  **eine** Definition, zwei Konsumenten (Export-Layout + DB).

### 3.2 Trennung der Datenhoheit

| Datenklasse | Quelle | Migration |
|---|---|---|
| Kartendaten | YAML → CSV → DB (idempotenter Seed) | jederzeit neu seedbar |
| Nutzerdaten (Fortschritt/Notizen) | nur DB | Dump/Restore |
| Lizenzdaten | eigene Tabelle (nicht WooCommerce-intern) | Dump/Restore |
| Review-Historie | nur DB | Dump/Restore |

Kartendaten sind reproduzierbar; Nutzer-/Lizenz-/Review-Daten sind der schützenswerte, nicht
reproduzierbare Teil und bestimmen die Backup-Strategie (Dok. 09).
