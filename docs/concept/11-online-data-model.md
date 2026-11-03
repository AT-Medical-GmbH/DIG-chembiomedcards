# 11 — Datenmodell Online-System

Relationales Modell (PostgreSQL). Ergänzt/konkretisiert `online-platform/database/data-model.md`
und `schema-draft.sql`. **Karten** werden aus der Pipeline synchronisiert; **Nutzerzustand**
entsteht im Betrieb.

## 1. Entitäten (Übersicht)

```
categories ─┐            ┌─ card_tags ─ tags
            ├─< cards >──┤
            │            ├─ card_versions
            │            ├─< user_progress >─ users
            │            ├─< user_notes >──── users
            │            └─< exports >─────── users
course_assignments · moodle_contexts · learning_sessions · review_events   (optional)
```

## 2. Kern-Tabellen

### `cards`
`id (pk)` · `slug` · `card_id` · `title` · `subtitle` · `front_type` · `front_content (jsonb)` ·
`back_content (jsonb)` · `primary_category_id (fk)` · `module` · `difficulty` · `status` ·
`version` · `front_asset_url` · `back_asset_url` · `created_at` · `updated_at`
> `front_content`/`back_content` spiegeln das kanonische Kartenschema (Kap. 02) als JSONB,
> damit neue Kartentypen (Kap. 13) ohne Schema-Migration möglich sind.

### `categories`
`id` · `name` · `slug` · `color` · `icon` · `sort_order`
> Entspricht den festen Register-Tabs (Kap. 03); erweiterbar für neue Fachgebiete.

### `tags` / `card_tags`
`tags(id, name, slug)` · `card_tags(card_id, tag_id)` (m:n).

### `card_versions`
`id` · `card_id (fk)` · `content_snapshot (jsonb)` · `changed_by (fk users)` · `change_note` ·
`version` · `created_at`
> Jede inhaltliche Änderung erzeugt einen Snapshot → vollständiger Änderungsverlauf,
> unabhängig von Git.

### `users`
`id` · `external_id` (Authentik/OIDC sub) · `email` · `display_name` · `role`
(`admin|editor|reviewer|dozent|lernender`) · `created_at` · `last_seen_at`

### `user_progress` (SRS-Kern)
`id` · `user_id (fk)` · `card_id (fk)` · `status`
(`neu|gelernt|unsicher|wiederholen|beherrscht|spaeter`) · `leitner_box (1..5)` ·
`ease_factor (float)` · `interval_days (int)` · `repetitions (int)` · `next_due_at` ·
`last_reviewed_at`
> Trägt **SM-2** (ease/interval/repetitions) **und** Leitner-Box gemeinsam (Kap. 09 §1).
> Unique(user_id, card_id).

### `user_notes`
`id` · `user_id (fk)` · `card_id (fk)` · `note_text` · `annotation_data (jsonb)` ·
`visibility (private|course|shared)` · `created_at` · `updated_at`
> `annotation_data` = Liste von Overlay-Objekten (Typ, Koordinaten, Farbe, Text) — nicht
> destruktiv (Kap. 09 §4).

### `exports`
`id` · `user_id (fk)` · `type (png|pdf|set|category)` · `category_id (fk, null)` ·
`params (jsonb)` · `file_path` · `status` · `created_at`

## 3. Optionale Tabellen (für Kurs-/LMS-/Analytics-Ausbau)

- `course_assignments` — Zuordnung Set/Kategorie → Kurs/Lerngruppe.
- `moodle_contexts` — LTI-Kontext (deployment_id, context_id, resource_link_id, Rolle).
- `learning_sessions` — Sessions (Start/Ende, Kartenzahl, Modus) für Statistik.
- `review_events` — Fachreview-Ereignisse (wer, Statuswechsel, Kommentar).
- `shared_notes` / `teacher_comments` — geteilte/Dozentennotizen (falls über `user_notes.visibility`
  hinaus eigene Tabellen gewünscht).

## 4. Indizes & Integrität (Auszug)

- `user_progress(next_due_at)` — „heute fällige Karten“ schnell.
- `user_progress(user_id, status)` — Stapel „unsicher/wiederholen“.
- `cards(primary_category_id)`, `card_tags(tag_id)` — Filter.
- Volltext: GIN-Index über `cards.title/subtitle/back_content` (Suche).
- FKs mit `ON DELETE`-Regeln: Nutzerlöschung kaskadiert Fortschritt/Notizen (DSGVO, Kap. 15).

## 5. Migrationen & Seeds

- **Alembic** für Schema-Migrationen (versioniert, reversibel).
- **Seed**: `generate_online_assets.py` + `POST /api/admin/sync` befüllt `cards/categories/tags`
  aus `cards_master.json`.
- **Admin-Erstzugang**: via OIDC-Gruppe „chembiomed-admins“ (Prod) bzw. Seed-Admin (Dev),
  Konzept in Kap. 15.

## 6. Verhältnis zu `schema-draft.sql`

Das bestehende `schema-draft.sql` wird auf dieses Modell aktualisiert; dieses Kapitel ist die
maßgebliche Beschreibung, `schema-draft.sql`/Alembic die ausführbare Umsetzung.
