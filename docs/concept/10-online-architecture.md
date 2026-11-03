# 10 — Architektur des Online-Systems

Aufbauend auf `online-platform/architecture/*` (chembiomed-cards.de, ATMED-core-Initialbetrieb,
WordPress/WooCommerce, Gateway/SSO).

## 1. Technologie-Stack (Entscheidung)

| Schicht | Wahl | Begründung |
|---------|------|------------|
| **Frontend** | React + TypeScript, **Vite**, Tailwind CSS | Größtes Ökosystem; als **Webcomponent** einbettbar (WordPress-Shortcode, Moodle-iframe); passt zur modernen ATMED-Weblinie |
| **Backend** | **FastAPI** (Python 3.11+), SQLAlchemy 2, Alembic, Pydantic v2 | **Gleiche Sprache wie die Generierungs-Pipeline** → geteilter Code (Kartenschema, Export); OpenAPI-nativ; async |
| **Datenbank** | **PostgreSQL 16** | Relationale Integrität, JSONB für `annotation_data`/Snapshots, Volltextsuche |
| **Objektspeicher** | **S3-kompatibel** (MinIO lokal; später dediziert/Nextcloud-kompatibel) | Trennung App/DB/Storage; portabel |
| **Export-Service** | **Playwright (Chromium)** als Worker | Identische Render-Engine wie der Build (Kap. 06) → pixelgleiche Downloads |
| **Auth** | Dev: lokales JWT · Prod: **OIDC via Authentik** | `ATMED-authentik` existiert; zentrale Identität/SSO |
| **API-Stil** | **REST** (OpenAPI 3.1) | Breit unterstützt; generierter TS-Client im Frontend |
| **Hintergrundjobs** | FastAPI + leichter Task-Runner (RQ/Dramatiq) | Export/Reindex/Batch asynchron |
| **Deployment** | **Docker Compose + Traefik** | `ATMED-traefik`; ATMED-Betriebsmuster (Kap. 15) |
| **CI/CD** | GitHub Actions | Tests, Build, Image-Push, Deploy |

> **Warum FastAPI statt Django/Laravel/Node?** Die wertvollste Code-Wiederverwendung liegt
> zwischen **Pipeline** und **API**: Kartenschema-Validierung, SMILES-/Layout-Rendering und der
> Playwright-Export existieren bereits in Python. Ein Python-Backend teilt diese Bausteine 1:1.
> React im Frontend bleibt davon unberührt und bedient Einbettung/SSR-freie SPA optimal.

## 2. Komponenten

```
┌─────────────────────────── chembiomed-cards.de ───────────────────────────┐
│  Traefik (TLS, Routing)                                                     │
│   ├─ /            → frontend (React SPA, statisch ausgeliefert)             │
│   ├─ /api         → backend  (FastAPI/uvicorn)                              │
│   ├─ /lti         → backend  (LTI 1.3 Launch/Deep Linking/AGS)             │
│   └─ /c/<id>      → qr-redirect (stabile Print→Online-Kurzlinks)           │
│                                                                            │
│  backend ──▶ PostgreSQL        (Karten-Sync + Nutzerzustand)               │
│  backend ──▶ Object Storage    (PNG/SVG/PDF, Nutzer-Uploads)               │
│  export-worker (Playwright) ◀─ Queue ◀─ backend (On-Demand-PNG/PDF)        │
│                                                                            │
│  Authentik (OIDC) ─ Login    WooCommerce ─ Lizenz-Webhook ─▶ backend       │
└────────────────────────────────────────────────────────────────────────────┘
```

## 3. Karten-Sync (Pipeline → DB)

Das Backend ist **nicht** die Autoren-Quelle. Ein **Seed/Sync** liest `cards_master.json` +
`generated/manifest.json` und schreibt/aktualisiert Karten, Kategorien, Tags in PostgreSQL
(`generate_online_assets.py` + `POST /api/admin/sync`). Nutzerzustand (Fortschritt, Notizen)
bleibt davon unberührt. So bleibt Git die Quelle der Wahrheit; die DB ist eine abgeleitete,
nutzerzustands-angereicherte Projektion.

Der Admin-Editor (Kap. 09 §6) schreibt Änderungen in die DB **und** kann sie als YAML-Patch
zurück in `data/cards/` exportieren (Round-Trip), damit Git autoritativ bleibt.

## 4. API-Oberfläche (Auszug, REST)

| Bereich | Endpunkte (Beispiele) |
|---------|------------------------|
| Karten | `GET /api/cards`, `GET /api/cards/{id}`, `GET /api/cards/{id}/versions` |
| Taxonomie | `GET /api/categories`, `GET /api/tags` |
| Lernen | `GET /api/study/queue?mode=due`, `POST /api/study/review` (SM-2-Update) |
| Fortschritt | `GET /api/progress`, `GET /api/progress/stats` |
| Notizen | `GET/POST/PATCH/DELETE /api/cards/{id}/notes` |
| Export | `POST /api/export` (png/pdf, Karte/Set/Kategorie) → Job → Download-URL |
| Admin | `POST /api/admin/cards`, `POST /api/admin/sync`, `POST /api/admin/import` |
| LTI | `POST /lti/login`, `POST /lti/launch`, `POST /lti/deep-link`, AGS-Callback |
| Lizenz | `POST /api/webhooks/woocommerce` (Paketfreischaltung) |

Bestehende Backend-Notizen (`online-platform/backend/card-api.md`, `notes-api.md`,
`license-api.md`, `media-api.md`) werden hierauf abgebildet.

## 5. Betriebsstufen

1. **Dev**: Docker Compose lokal, MinIO, lokales JWT, SQLite→besser Postgres-Container.
2. **Initial (ATMED-core)**: Compose hinter Traefik, Postgres + MinIO, Authentik-OIDC,
   WooCommerce-Webhook.
3. **Dediziert (später)**: identischer Stack auf eigenem Server (`future-dedicated-server.md`),
   Storage ggf. ausgelagert; Migration ist reines Re-Deploy + DB/Storage-Umzug.

## 6. Nicht-funktionale Anforderungen

- **Performance:** Kartenlisten paginiert/indiziert; Bilder via CDN/Cache-Header; SPA-Lazy-Loading.
- **Sicherheit:** OIDC, rollenbasierte Autorisierung serverseitig, Rate-Limits, keine Secrets im
  Repo; Uploads virenscan-/typgeprüft; Annotationsdaten als JSON validiert.
- **Beobachtbarkeit:** strukturierte Logs, Healthchecks, Metriken (passend zu ATINFRA-control).
- **DSGVO:** Nutzerzustand/Notizen sind personenbezogen → Löschkonzept, Datenexport, klare
  Rechtegrenzen (Kap. 15).
