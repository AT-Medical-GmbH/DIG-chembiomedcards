# Changelog

## 2026-11-03 (Umzug: gemeinsamer Plan Projekt 16 + Pharma Cards)
- Entscheidung von Andreas: Die beiden Umzugspakete werden zu einem Plan zusammengeführt. Grundlage
  ist ADR-024 bzw. `deploy/README_MIGRATION.md`. GitHub-PR #25 ist damit abgelöst.
- Zusammengeführt: Kernkarten (116) und Pharma Cards (110) samt Lernplattform. Konflikte in
  `.gitignore`, `CHANGELOG.md` und `Makefile` aufgelöst, alle Ziele bleiben nebeneinander.
- Build-Image: zusätzlich pytest, API-venv und Node 22.23.4 LTS (Prüfsumme gepinnt).
- Neu `.forgejo/workflows/pharma.yml`: PH-Prüfungen, Layout, API-Tests und Web-Build. Danach geht
  ein Antrag an `pharma-deploy` für das Lernplattform-Staging. Produktion nur mit „FREIGABE“ und
  Freigabedatei auf dem Host.
- `cards.yml`: PH-Moodle- und Druckpakete im Karten-Release unter `pharma/`
  (`scripts/pharma/add_to_release.py`). Vorschau und Review-PDF gehen nur nach Staging.
- `deploy/atmed-core/pharma-online/`: `pharma-deploy` mit systemd-Path-Unit.
  - Der Antragsordner ist sticky, Ergebnisse schreibt nur root (atomar).
  - Es gelten nur Commits auf `main`.
  - Rollback ist möglich; wird ein Dienst nicht gesund, kehrt das Skript automatisch zurück.
- Ergebnis von Phase 0 eingearbeitet:
  - Traefik-Netz `traefik_web`;
  - Forgejo-Sicherung nach `/srv/atmed/stacks/forgejo/sicherung` (`/srv/atmed/backups/*` ist von
    Restic ausgeschlossen);
  - fehlende Authentik-Middleware als offene Entscheidung.
- Traefik-Overlay der Lernplattform mit eindeutigem Routernamen (`PHARMA_ROUTER`).

## 2026-11-03
- Umzug auf eigene Server vorbereitet (ADR-024): Forgejo und Kartenproduktion auf ATMED-core,
  Runbook mit Phasen und Gates `deploy/README_MIGRATION.md`
- Build-/Runner-Image `deploy/builder/Dockerfile` (Playwright 1.56, Forgejo-Runner 13.2.1 mit
  Prüfsumme); Compose-Stacks `deploy/atmed-core/{forgejo,chembiomed-cards}`
- Forgejo-Workflow `.forgejo/workflows/cards.yml`: Staging automatisch, Produktion nur mit
  „FREIGABE“ und `approved`-Karten; `scripts/release_cards.py`, `deploy/scripts/publish-release.sh`,
  `rollback-release.sh`
- Read-only-Vorabprüfung `deploy/scripts/00-preflight-readonly.sh`, Migration
  `deploy/scripts/10-migrate-from-github.sh`, Forgejo-Sicherung per systemd-Timer
- Ende-zu-Ende lokal getestet (Forgejo 15.0.11, Runner, nginx); die Live-Migration von GitHub ist
  noch nicht getestet

## 2026-11-01 (Online: SvelteKit 3)
- Frontend auf SvelteKit 3 / adapter-static 4 (ersetzt Dependabot-PR #21, der allein nicht installierbar
  war): Vite 8, vite-plugin-svelte 7, TypeScript 6, Svelte 5.57.
- Konfiguration aus `svelte.config.js` in `sveltekit({...})` in `vite.config.ts` verschoben (CSP und
  SPA-Fallback unverändert); `$lib` → Subpath-Import `#lib`; `tsconfig.json` erweitert `$app/tsconfig`.
- Geprüft: `npm run check` 0 Fehler, Build ok, CSP-Hash im `index.html`, E2E-Smoke 8/8.

## 2026-10-31 (4)
- Alle offenen Fragen in einer strukturierten Abfrage entschieden; `open-questions.md` neu gefasst,
  ADR-022 (gemeinsamer Tab Allg./Anorganik) und ADR-023 (Entscheidungspaket)
- Tab-Leiste auf fünf Tabs umgestellt; alle 116 Karten-IDs bestätigt
- Masterverzeichnis: automatisch gepflegter Abschnitt „Produzierte Karten“
  (`scripts/update_master_directory.py`, Teil von `make reports`)
- Logo-Vektorfassung als Nachzeichnung (`scripts/vectorize_logo.py`), Abnahme offen

## 2026-10-31 (3)
- Offizielles ChemBioMed-Cards-Logo eingebunden: Original unter `brand/logo/source/`, reproduzierbar
  abgeleitete Varianten (vollständig, kompakt, Bildmarke) per `scripts/derive_logo_assets.py`
- Kartenkopf zeigt die Kompaktfassung statt der Text-Wortmarke; Kartenfarben aus dem Logo übernommen
  (Navy, Petrol, Rot) – ADR-021
- Neue automatische Prüfung: Logo geladen und ohne Überdeckung von Inhalten

## 2026-10-31 (2)
- Zentrale Kartenvorlage `templates/card_template.html` ersetzt die vier bisherigen Vorlagendateien
  (ADR-018); Bedienungsanleitung `templates/README.md`
- 96 weitere Karten der Handover-Soll-Liste: Derivate, Stickstoffstoffwechsel, Neurotransmitter, Hormone,
  zentraler Stoffwechsel, Lipide, Nukleotide/Coenzyme/Second Messenger, Vitamine (gesamt 116, alle
  `needs_review`, IDs vorläufig nach ADR-020)
- Strukturformeln aus PubChem mit RDKit (`scripts/cbm/molecule.py`, ADR-019); Fischer-Projektion um
  Ring-Substituenten und Hydroxyprolin erweitert; Vorderseitentypen `molecule` und `formula`
- Neue automatische Prüfungen: geladene Schrift, Mindestabstand von Atombeschriftungen
- Übersichtsbilder je Themengruppe; Einzelvorschauen nicht mehr versioniert

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

## 2026-10-31 (CI: eigener Runner)
- CI läuft auf einem eigenen Runner, weil die GitHub-Runner wegen Billing gesperrt sind:
  `runs-on: [self-hosted, linux, chembiomed]`, jeder Job im Container, nie für Fork-PRs, nur
  Leserechte.
- Neu `.github/workflows/pharma-ci.yml` mit den Jobs pipeline, api und web. Schritte ohne passende
  Dateien überspringen sich selbst.
- `docs/ci/self-hosted-runner.md`: Sicherheitsmodell, GitHub-Einstellungen (zuerst Repo privat),
  VM-Einrichtung, Wartung, Rückweg.

## 2026-10-31 (Online: Staging-Übergabe)
- `online-platform/ops/staging/`:
  - `STAGING_HANDOVER.md` für die Server-Sitzung: offene Entscheidungen, Ablauf in Einzelschritten,
    Ergebnisprüfung, Rückweg, Rückmeldeformat;
  - `staging.env.example`: OIDC aktiv, Entwürfe für Lernende gesperrt, LTI vorbereitet;
  - `preflight.sh`: nur lesend; prüft Docker, Platz, Traefik-Netz, DNS, Authentik-Discovery und den
    Checkout.

## 2026-10-31 (Online: Moodle LTI 1.3)
- LTI 1.3 Launch und Deep Linking 2.0 (`app/lti.py`, `/api/lti/{login,launch,jwks,deep-link}`):
  - state und nonce einmalig in der DB (Migration 0002), Prüfung von Signatur, Issuer, Audience,
    nonce, Deployment, Version und Nachrichtentyp;
  - App-Sitzungstoken (RS256) im URL-Fragment übergeben;
  - Rollen nur `learner`/`teacher`, nur pseudonyme Kennung gespeichert.
- SPA: `/lti/start` (Sitzung übernehmen), `/lti/auswahl` (Lehrende wählen Lernsets/Karten und geben
  sie per POST an Moodle zurück), Kopfzeile „Über Moodle · Kurs“.
- Betrieb:
  - `docker-compose.lti.yml` mit dem Tool-Schlüssel als Docker-Secret;
  - neue Abhängigkeit `python-multipart`;
  - `.gitignore` sperrt jetzt `online-platform/.env`, `secrets/`, `*.pem` und `*.key`. Vorher waren
    sie nicht ausgeschlossen.
- Tests: API 66/66 (davon LTI 22), Browser-E2E LTI 10/10 gegen `e2e/mock_moodle.py`, Smoke 8/8.

## 2026-10-31 (Online: Anmeldung OIDC/PKCE)
- SPA-Anmeldung über Authentik (Authorization Code + PKCE S256, öffentlicher Client):
  - `src/lib/oidc.ts`, Route `/auth/callback`, Anmeldeseite, Abmelden, Refresh;
  - Tokens nur in `sessionStorage`.
- API:
  - `GET /api/auth/config` liefert öffentliche Werte aus der Discovery, mit Issuer-Prüfung.
  - `POST /api/auth/token` ist ein Token-Proxy mit Feld-Whitelist und fester Redirect-URI, ohne Secret.
  - Die CSP bleibt bei `connect-src 'self'`.
- Startsperren: `OIDC_CLIENT_ID`/`OIDC_REDIRECT_URI` sind im OIDC-Modus Pflicht; in Produktion nur `https`.
- Tests: API 44/44, Browser-E2E OIDC 10/10 gegen simulierten Provider, lokaler Smoke 8/8.

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

## 2026-10-31 (Content R2)
- 50 R2-Entwürfe in `cards/PH/metadata/`: Anästhesie/Intensiv `ph_050`–`ph_064`, Intoxikationen
  `ph_087`–`ph_089`, Analgetika `ph_130`–`ph_138`, Herz-Kreislauf `ph_140`–`ph_151`,
  Interaktionen/Arzneimittelsicherheit `ph_210`–`ph_220`. Keine Zahlendosen, Prüfpunkte je Karte in
  `review_focus`, Status `clinical_review_needed` bzw. `toxicology_review_needed`.
- Scope: Kategorie `thrombozytenaggregationshemmer` (Clopidogrel, Ticagrelor, ASS) ergänzt und im
  Paket Herz-Kreislauf eingehängt, statt Thrombozytenhemmer als Antikoagulanzien zu führen.
- Layoutmessung: 110/110 Karten ohne Überlauf, alle Inhalte in der 5-mm-Sicherheitszone.
- Reports `missing_cards`, `content_review`, `content_scope`, `cards_review_needed`, `layout_review`
  aktualisiert; Registry um 50 PH-Zeilen erweitert.
- `scripts/pharma/review_packet.py` + `make ph-review-packet`: Review-PDF für das Fachreview
  (110 Karten, 113 A4-Seiten, ENTWURF-Wasserzeichen, Prüfschwerpunkte und Ergebnisfelder je Karte).

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
- Vollständiges Gesamtkonzept unter `docs/concept/` ausgearbeitet (00–16 + Decision Log + offene Fragen)
- Drei-Ebenen-Architektur, kanonisches Content-Modell, Import-/Audit-Pipeline, Kartenlayout- und
  Generierungs-Pipeline, Print-/Moodle-Export, Online-Lernsystem (Funktion, Architektur, Datenmodell,
  UI/UX), Erweiterbarkeit, QS, Deployment sowie Phasenplan & Akzeptanzkriterien dokumentiert
- Architekturentscheidungen als ADR-Kurzform festgehalten; offene Abstimmungspunkte markiert
- Platzhalter `online-platform/database/data-model.md` und `lms-content/moodle-integration.md` auf
  die maßgeblichen Konzeptkapitel verwiesen; README um Konzept-Einstieg ergänzt

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
