# 09 — Deployment-Vorbereitung

**Dokument:** Containerisierung, Compose, Traefik, OIDC/Authentik, Backup/Update, Admin-Bootstrap
**Handover-Phase:** 16

---

## 1. Zielbild

Das Online-System wird containerisiert bereitgestellt, Traefik-kompatibel, mit sauberer Trennung von
App, Datenbank und Storage — passend zur AT-Medical-Systemlandschaft (`ATMED-traefik`,
`ATMED-authentik`). Initialer Betrieb kann auf ATMED-core erfolgen; die Architektur bleibt migrierbar
(Blue/Green, bestehende Doku).

---

## 2. Container-Komposition (`docker-compose.yml`, Soll)

| Service | Image/Build | Aufgabe | Port (intern) |
|---|---|---|---|
| `pharma-api` | Build (FastAPI/Uvicorn) | REST + LTI + Export-Trigger | 8000 |
| `pharma-web` | Build (SvelteKit) | Frontend | 3000 |
| `postgres` | postgres:16 | Datenbank | 5432 |
| `object-storage` | MinIO (S3-kompatibel) oder Volume | Bilder/Exporte | 9000 |
| `qr-redirect` | bestehend/leichtgewichtig | stabile `/c/<card-id>`-Redirects | 8080 |

Reverse Proxy **Traefik** (vorhanden) terminiert TLS und routet nach Host/Pfad; die Services
exponieren nur interne Ports. Labels für Router/Service werden Traefik-konform gesetzt.

```
Internet ─▶ Traefik (TLS) ─┬─▶ pharma-web   (chembiomed-cards.de / pharma)
                           ├─▶ pharma-api   (/api, /lti)
                           └─▶ qr-redirect  (/c/<card-id>)   ← Priorität, stabil
```

---

## 3. Zu erzeugende Artefakte (Folgephase)

- `online-platform/backend/Dockerfile`, `online-platform/frontend/Dockerfile`
- `online-platform/docker-compose.yml` (+ `docker-compose.prod.yml` mit Traefik-Labels)
- `.env.example` (siehe Abschnitt 4)
- `online-platform/README_DEPLOYMENT.md`
- Alembic-Migrationsskripte (`online-platform/database/migrations/`)
- Seed-Daten (`seed_online_db`: Scope-Konfig + approved Karten)
- Admin-Erstzugang-Konzept (Abschnitt 5)
- Backup-/Update-Hinweise (Abschnitt 6/7)

---

## 4. Konfiguration (`.env.example`, keine Secrets im Repo)

```
# App
PHARMA_ENV=production
PHARMA_API_BASE_URL=https://chembiomed-cards.de/api
# DB
POSTGRES_HOST=postgres
POSTGRES_DB=pharma_cards
POSTGRES_USER=pharma
POSTGRES_PASSWORD=__set_in_deployment__
# Storage (S3-kompatibel)
S3_ENDPOINT=http://object-storage:9000
S3_BUCKET=pharma-cards
S3_ACCESS_KEY=__set_in_deployment__
S3_SECRET_KEY=__set_in_deployment__
# Auth (dev: lokal; prod: OIDC/Authentik)
AUTH_MODE=oidc              # local | oidc
OIDC_ISSUER=https://auth.at-medical.de/application/o/pharma-cards/
OIDC_CLIENT_ID=__set_in_deployment__
OIDC_CLIENT_SECRET=__set_in_deployment__
# LTI 1.3
LTI_PLATFORM_ISSUER=https://<moodle-host>
LTI_CLIENT_ID=__set_in_deployment__
```

**Secret-Politik:** Keine privaten Schlüssel/Tokens/Passwörter im Repository. Secrets über
Deployment-Umgebung/Secret-Store; `.env.example` enthält nur Platzhalter (ATMED-Governance).

---

## 5. Authentifizierung & Admin-Bootstrap

- **Dev:** `AUTH_MODE=local`, einfache lokale Nutzer, ein initialer Admin per Seed/CLI
  (`create_admin --email ...`), Passwort nur interaktiv/aus Secret, nie im Repo.
- **Prod:** `AUTH_MODE=oidc` gegen **Authentik** (vorhanden). Rollen aus OIDC-Claims/Gruppen gemappt
  auf `users.role`. JWT-Access (kurzlebig) + Refresh; Paket-/Lizenz-Claims (bestehende
  `gateway-authentication.md`).
- Übergangskompatibilität zu WooCommerce-Session bleibt wie dokumentiert möglich.

---

## 6. Backup

| Datenklasse | Backup | Frequenz |
|---|---|---|
| PostgreSQL (Nutzer/Fortschritt/Notizen/Review/Lizenz) | `pg_dump` → Restic nach ATMED-backup | täglich |
| Object-Storage (generierte Bilder/Exporte) | reproduzierbar aus Content → optional | wöchentlich |
| Kartendaten (`cards/PH/**`) | Git (versioniert) | pro Commit |
| QR-Redirect-Tabelle | Dump | täglich (hohe Priorität) |

Reproduzierbares (Bilder) muss nicht so streng gesichert werden wie Nicht-reproduzierbares
(Nutzer-/Review-/Lizenzdaten). Restic-Backups laufen über die bestehende ATMED-Backup-Infrastruktur.

---

## 7. Update & Migration

- **Schema-Updates** nur über Alembic-Migrationen (vorwärts/rückwärts), nie manuell.
- **Deploy** über CI (GitHub Actions): Build → Test → Image → Compose-Pull → Migration → Smoke-Test.
- **Zero-Downtime** nach Blue/Green (bestehende Migrationsdoku); QR-Redirect zuerst testen/freigeben.
- **Rollback:** vorherige Image-Tags + Alembic-Downgrade + DB-Restore als dokumentierter Pfad.
