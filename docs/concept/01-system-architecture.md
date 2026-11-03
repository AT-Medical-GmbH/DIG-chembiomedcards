# 01 — Systemarchitektur

## 1. Überblick: drei Ebenen, eine Quelle

```
                 ┌──────────────────────────────────────────────┐
                 │              CONTENT-EBENE                     │
                 │   (Single Source of Truth, versioniert)        │
                 │                                                │
                 │   data/cards/*.yaml   ── Autoren-Quelle         │
                 │   data/categories.yaml, tags.yaml, substances…  │
                 │            │  normalize + validate              │
                 │            ▼                                    │
                 │   data/cards_master.json  ── kanonisch          │
                 └───────────────┬────────────────────────────────┘
                                 │  (ein Build, viele Ziele)
          ┌──────────────────────┼───────────────────────────┐
          ▼                      ▼                           ▼
 ┌────────────────┐   ┌───────────────────┐      ┌────────────────────────┐
 │  EXPORT-EBENE  │   │   ONLINE-EBENE     │      │   PRINT/MOODLE-EBENE    │
 │  PNG/SVG/PDF   │   │   App + API + DB   │      │  A4/A3-Bögen, CSV/H5P   │
 │  pro Karte     │   │   SRS, Notizen …   │      │  LTI 1.3, Importpakete  │
 └────────────────┘   └───────────────────┘      └────────────────────────┘
```

Die **Content-Ebene** ist autoritativ. Die **Online-Ebene** liest dieselben Kartendaten in
eine Datenbank ein (Seeding/Sync) und ergänzt *nutzerbezogenen* Zustand (Fortschritt, Notizen).
Bilder werden sowohl im Build (statisch) als auch zur Laufzeit (on demand) aus demselben
Layout erzeugt — es gibt **genau eine** Layout-Definition.

## 2. Datenfluss im Detail

| Schritt | Eingabe | Werkzeug | Ausgabe |
|---------|---------|----------|---------|
| 1. Import | Upload-ZIPs, Bilder, CSV/HTML/JSON | `extract_uploaded_files` | `input/extracted/` |
| 2. Audit | extrahierte Dateien | `audit_cards` | `data/audit_report.json`, `reports/*` |
| 3. Normalisierung | Rohkarten + Audit | `normalize_cards` | `data/cards/*.yaml`, `cards_master.json` |
| 4. Validierung | `cards_master.json` | `validate_output` + JSON-Schema | Pass/Fail + Report |
| 5. Generierung | `cards_master.json` + Templates | `generate_cards` (Playwright) | `generated/individual/**` |
| 6a. Print | generierte Einzelkarten | `generate_print_pdfs` | `generated/print/`, `dist/print/*.zip` |
| 6b. Moodle | `cards_master.json` + Bilder | `generate_moodle_import` | `generated/moodle/`, `dist/moodle/*.zip` |
| 6c. Online | `cards_master.json` + Bilder | `seed`/`sync` API | PostgreSQL + Object Storage |

Jeder Schritt ist **idempotent** und **reproduzierbar**: gleiche Eingabe → gleiche Ausgabe.
Der gesamte Build läuft als ein Kommando (`make build`) und in CI.

## 3. Trennung der Verantwortlichkeiten

- **Pipeline (Python)** kennt nur Daten → Artefakte. Sie weiß nichts von Nutzern.
- **Backend-API (FastAPI)** kennt Karten (lesend, aus Sync) + Nutzerzustand (schreibend).
- **Frontend (React)** ist reine Präsentations-/Interaktionsschicht über der API.
- **Storage** hält Binärartefakte; DB hält strukturierte Daten und Nutzerzustand.

Diese Trennung erlaubt es, die **Print-/Moodle-Linie unabhängig vom Online-System** zu betreiben
(z. B. bevor das Online-MVP steht) und das Online-System später auf einen dedizierten Server zu
heben, ohne die Content-Pipeline anzufassen.

## 4. Ziel-Projektstruktur (reconciled)

Die folgende Struktur führt das Handover-Schema mit der **bereits vorhandenen** Repo-Struktur
zusammen. Vorhandene Verzeichnisse bleiben erhalten; neue Pipeline-/App-Verzeichnisse werden
ergänzt.

```
DIG-chembiomedcards/
  README.md  CHANGELOG.md  LICENSE.md
  docs/
    concept/                 # ← dieses Konzept
    project-overview.md  product-vision.md  roadmap.md  …   (bestehend)
  brand/                     # (bestehend) Farben, Typo, Design-Tokens, Logo
  card-system/               # (bestehend) Layoutstandard, Kartentypen, Templates
  cards/                     # (bestehend) Kartenassets je Modul + registry/
    AC/ OC/ BC/ MB/ APC/ PH/
    registry/                # cards.master.csv, schema, package-registry
  data/                      # ← NEU: kanonische Datenebene
    cards/                   #   eine YAML je Karte (Autoren-Quelle)
    cards_master.json        #   kanonische Gesamtdatei
    categories.yaml  tags.yaml  substances.yaml
    audit_report.json
  input/                     # ← NEU: Upload-Verarbeitung
    uploaded_raw/  extracted/  rejected/
  templates/                 # ← zentrale Kartenvorlage (ADR-018)
    card_template.html         #   Layout aller Karten (Vorder- + Rückseite)
    (geplant: print_sheet_template.html)
  generated/                 # ← NEU: Build-Artefakte (gitignored, außer Beispiele)
    individual/{front,back,svg,pdf}/  moodle/  print/  preview/
  scripts/                   # (bestehend) + neue Pipeline-Skripte
    extract_uploaded_files.py  audit_cards.py  normalize_cards.py
    generate_cards.py  generate_print_pdfs.py  generate_moodle_import.py
    generate_online_assets.py  validate_output.py
    (bestehend: generate_card_registry.py, validate_card_metadata.py, …)
  app/                       # ← NEU: Online-Lernsystem
    backend/   (FastAPI)
    frontend/  (React/Vite)
    shared/    (Typen, OpenAPI-Client, Kartenschema)
  print-production/          # (bestehend) Specs, Packaging
  lms-content/               # (bestehend) Moodle-/LMS-Verknüpfung
  online-platform/           # (bestehend) Architektur-/Feature-Notizen → verweisen auf app/
  exports/                   # (bestehend) Ausgabekanäle
  reports/                   # ← NEU: Audit-/QS-Berichte (Markdown)
  dist/                      # ← NEU: versandfertige Pakete
    moodle/  print/  online/  source/
  deploy/                    # (bestehend) + Dockerfiles, compose, .env.example
```

> **Hinweis zur Abgrenzung:** `online-platform/` (bestehende Notizen) und `app/` (zukünftiger Code)
> existieren bewusst nebeneinander. `online-platform/` bleibt der Ort für Architektur-/Feature-
> Beschreibungen; `app/` wird die lauffähige Implementierung. Beide verweisen auf dieses Konzept
> als verbindliche Referenz. Siehe [offene Fragen](open-questions.md) zur möglichen späteren
> Konsolidierung.

## 5. Betriebssicht (High Level)

```
Internet ─▶ Traefik (ATMED-gateway/-core) ─▶ ┌─ frontend (statisch, SPA) ─┐
                                             ├─ backend (FastAPI/uvicorn) ─┤─▶ PostgreSQL
                                             ├─ export-worker (Playwright) ┤─▶ Object Storage (S3)
                                             └─ (optional) qr-redirect ────┘
Moodle ──LTI 1.3──▶ backend          WordPress/WooCommerce ──Lizenz-Webhook──▶ backend
Authentik ──OIDC──▶ backend (Prod-Login)
```

Details zur Laufzeitarchitektur: [10 — Online-Architektur](10-online-architecture.md);
Deployment: [15 — Deployment](15-deployment.md).

## 6. Technische Querschnittsprinzipien

- **Reproduzierbarkeit ist Pflicht** — jeder Artefakt-Stand ist aus einem Git-Commit neu baubar.
- **Schema-Validierung an jeder Grenze** — JSON-Schema für Karten, OpenAPI für die API.
- **i18n-fähig** — Inhalte primär Deutsch; Feldstruktur erlaubt spätere Übersetzungen.
- **Barrierearm** — WCAG-orientiert (Kontrast, Tastatur, Fokus) von Anfang an.
- **Keine Secrets im Repo** — `.env.example` dokumentiert Variablen; echte Werte extern.
