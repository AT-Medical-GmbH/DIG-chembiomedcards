# Changelog

## 2026-10-31 (P5 Online-MVP)
- `online-platform/backend/`: FastAPI-API mit SQLAlchemy/Alembic (PostgreSQL 16, SQLite für Tests).
  Seed aus `cards/PH` (idempotent, Versions-Snapshots, Deaktivierung statt Löschen). Freigabe-Gating:
  Lernende sehen nur `approved`. Wiederholung nach SM-2 oder Leitner, Markierungen, Lernsets,
  Statistik, Notizen inkl. Kursnotizen und Markdown-Export, Review-Protokoll und Änderungsverlauf
  für Review-Rollen, Downloads (HTML/PDF/PNG, Entwurfs-Wasserzeichen) über den gemeinsamen Renderer.
  Anmeldung lokal (nur Entwicklung/Staging) oder OIDC/Authentik (JWKS, Issuer/Audience, Rollen aus
  Gruppen). Startsperren in Produktion; der Container endet bei unsicherer Konfiguration mit Exit 1.
- `online-platform/frontend/`: SvelteKit-Oberfläche – Übersicht mit Tagesziel und Kategoriefortschritt,
  Lernmodus (Flip per Klick/Leertaste/Wischen, Bewertung 1–4, Fokusmodus), Kartensuche mit Filtern,
  Kartendetail mit Fachreview-Formular, Antidot-/Toxidrom-Übersicht, Notizen. Druckgetreue Karte im
  Shadow DOM ab Tablet-Breite, responsive Leseansicht (16 px) auf Smartphones. CSP mit Hashes.
- Betrieb: Dockerfiles (API, Web/nginx), `docker-compose.yml`, Traefik-Overlay, `.env.example`,
  `online-platform/README_DEPLOYMENT.md`.
- Tests: 33 API-Tests (u. a. Gating, OIDC-Ablehnung, Rollen, Seed), Browser-E2E 8/8 gegen
  PostgreSQL und gegen den gebauten Docker-Stack.

## 2026-10-31 (P4 Export: Moodle + Druck)
- `scripts/pharma/generate_moodle_import.py`: Moodle-Pakete je Paket aus
  `cards/PH/scope/packages.yaml` (import.csv, import_html.csv, TAB-/Semikolon-Zweispaltenimport mit
  CRLF bzw. BOM, PNG-Bilder, manifest.json mit SHA-256, README_IMPORT.md, byte-reproduzierbares ZIP).
- `scripts/pharma/generate_print_sheets.py`: Druckpakete mit A4/A3-Bögen 2/4/8-up (automatisch
  maximaler Maßstab, A4 2-up in 100 %), Duplex-Spiegelung je Wendekante, Schnittmarken im Außenrand,
  3 mm Beschnitt, Einzelkarten-PDF, PNG, README_PRINT.md, Manifest.
- Export-Gating in beiden Generatoren über dieselbe Regel (`validate_output.is_exportable`);
  `--preview` getrennt unter `dist/preview/` mit ENTWURF-Vermerk bzw. -Wasserzeichen.
- `scripts/pharma/check_layout.py`: misst in Chromium Überlauf und 5-mm-Sicherheitszone;
  `make ph-print` druckt nur ohne Befund. Report `docs/pharma-cards/reports/layout_review.md`.
- Layout korrigiert: 5-mm-Sicherheitszone eingehalten (vorher 4 mm), echter QR-Code
  (15 × 15 mm, Fehlerkorrektur Q) auf der Vorderseite, Rückseite als Zweispaltenfluss.
  Messung: Überlauf von 16 auf 0 Karten (4 Toxidromkarten in PR #10 gekürzt).
- 33 pytest-Tests (`scripts/pharma/tests/`), Makefile-Ziele `ph-layout-check`, `ph-moodle(-preview)`,
  `ph-print(-preview)`, `ph-test`.

## 2026-10-31 (Fachreview-Vorlauf)
- Pharma Cards – Fachreview-Prozess unter `docs/pharma-cards/review/`: Ablauf und Rollen,
  Checklisten Pharmakologie, Toxikologie und klinische Sicherheit, Protokollvorlage.
- Klinische R1-Entwürfe (30 Karten) in `cards/PH/metadata/`: Notfallmedikamente `ph_040`–`ph_049`
  (`clinical_review_needed`), Toxidrome `ph_080`–`ph_086` und Antidote `ph_100`–`ph_112`
  (`toxicology_review_needed`). Keine Zahlendosen; konkrete Prüfpunkte je Karte in `review_focus`.
- `scripts/pharma/review_report.py` + `make ph-review-report` erzeugen
  `docs/pharma-cards/reports/cards_review_needed.md`.
- Render: Vorderseite zeigt Namen der Wirkstoffgruppe statt Slug.
- Scope: Intoxikationsbild `cyanid` ergänzt (Zielgift des Antidots Hydroxocobalamin).
- Reports `missing_cards`, `content_review`, `content_scope` auf Stand R1 (60 Entwürfe) gebracht.

## 2026-10-31
- Pharma Cards (Modul PH) – P1 Pipeline: reproduzierbare Erzeugung unter `scripts/pharma/`
  (`validate_ph_cards.py`, `build_registry.py`, `render_cards.py`, `validate_output.py`) + `Makefile`
  und gemeinsames Kartenlayout `card-system/templates/pharma/card.css` (DIN A6 quer, Tab-Leiste,
  Farbrollen, Warnlevel-Badge). Rendering optional via vorinstalliertem Chromium.
- Pharma Cards – P2 Pilot-Content R1: 30 Karten in `cards/PH/metadata/` (Allgemeine Pharmakologie
  `ph_001`–`ph_019`, PK/PD-Mechanismen `ph_020`–`ph_030`), warning_level low/moderate,
  review_status needs_review, keine Dosierungen; Registry `cards.master.csv` um PH-Zeilen ergänzt
  (Nicht-PH-Zeilen unverändert).
- Export-Gating implementiert (critical nur approved; moderate/high nur reviewed/approved);
  Pilot-Karten korrekt als "im Review / nicht exportierbar" erkannt.
- Beispiel-Renders unter `card-system/examples/pharma/`; generierte Massen-Artefakte via `.gitignore`
  ausgeschlossen (reproduzierbar). Superseded Beispiel-YAML aus `cards/PH/examples/` entfernt.

## 2026-10-09
- Pharma Cards (Modul PH) — vollständiges Konzeptdossier unter `docs/pharma-cards/` (18 Phasen:
  Analyse/Architektur, Datenmodell, fachliche Zielstruktur, kuratierte Startliste, Layout, Generierung
  & Print, Moodle-Integration, Online-Lernsystem, Deployment, Review/Sicherheit, Import/Audit,
  Akzeptanzkriterien & Roadmap)
- PH-Scope-Konfiguration angelegt (`cards/PH/scope/`): Kategorien, Wirkstoffgruppen, Tags, Warnlevel,
  Review-Status, Kartentypen, Toxidrome, Antidote — Kategorien kommen aus Konfiguration, nicht aus
  Layout-Code
- Erweitertes PH-Content-Datenmodell + zwei Beispielkarten (`cards/PH/examples/`), konservativ, mit
  Review-Status, ohne finale Dosierungen
- Phase-4-Reports angelegt (`docs/pharma-cards/reports/`: content_scope, missing_cards, content_review)
- PH als Ausbau-Vertikal von ChemBioMed Cards verankert (kein Parallel-Repo)

## 2026-05-15
- Initiale Repository-Struktur für ChemBioMed Cards angelegt
- Bereiche für Dokumentation, Card-System, Registry, Print-Produktion und Onlineplattform vorbereitet
