# 15 — Deployment-Vorbereitung & Betrieb

Aufbauend auf `deploy/ATMED-core-deployment-notes.md`,
`online-platform/architecture/{atmed-core-initial-hosting,future-dedicated-server,gateway-authentication}.md`.
**Staging-first** (ATMED-Grundsatz): neue Dienste nicht experimentell auf Produktiv-Servern.

## 1. Container-Topologie

```
docker compose:
  traefik         # TLS/Routing (bzw. bestehender ATMED-Traefik übernimmt)
  frontend        # React-SPA (nginx-static)
  backend         # FastAPI/uvicorn (API + LTI + Webhooks)
  export-worker   # Playwright/Chromium (On-Demand-PNG/PDF, Batch)
  postgres        # PostgreSQL 16
  minio           # S3-kompatibler Objektspeicher (Dev/Initial)
  (redis)         # Queue/Cache für Jobs (optional)
```

## 2. Zu erstellende Artefakte

- `app/backend/Dockerfile`, `app/frontend/Dockerfile`, `export-worker/Dockerfile`
- `deploy/docker-compose.yml` (+ `docker-compose.override.yml` für Dev)
- `deploy/.env.example` (alle Variablen dokumentiert, **keine echten Secrets**)
- `deploy/README_DEPLOYMENT.md` (Setup, Update, Rollback, Backup)
- Alembic-Migrationen + Seed (Kap. 11 §5)
- Admin-Erstzugang-Konzept (siehe §5)

## 3. `.env.example` (Auszug)

```
# App
APP_BASE_URL=https://chembiomed-cards.de
DATABASE_URL=postgresql+psycopg://chembiomed:__set__@postgres:5432/chembiomed
# Storage (S3-kompatibel)
S3_ENDPOINT=https://... ; S3_BUCKET=chembiomed ; S3_ACCESS_KEY=__set__ ; S3_SECRET_KEY=__set__
# Auth (Prod: Authentik OIDC)
OIDC_ISSUER=https://auth.at-medical.de/application/o/chembiomed/
OIDC_CLIENT_ID=__set__ ; OIDC_CLIENT_SECRET=__set__
# LTI 1.3
LTI_PLATFORM_ISSUER=... ; LTI_CLIENT_ID=... ; LTI_DEPLOYMENT_ID=...
# WooCommerce Lizenz-Webhook
WOOCOMMERCE_WEBHOOK_SECRET=__set__
```

## 4. Traefik / Netz

- Traefik-Labels je Service; Hostname `chembiomed-cards.de`, TLS via bestehende ATMED-Konfiguration.
- Eigener interner Port, sauber hinter dem Reverse Proxy (keine direkten Portfreigaben).
- Initialbetrieb **ATMED-core**; Migrationspfad auf dedizierten Server ist reines Re-Deploy +
  DB-/Storage-Umzug (`future-dedicated-server.md`).

## 5. Auth, Rollen & Admin-Erstzugang

- **Prod:** OIDC via **Authentik** (SSO, Kap. 10). Rolle wird aus OIDC-Gruppen gemappt
  (`chembiomed-admins` → admin, `-editors` → editor, …).
- **Dev:** lokales JWT + Seed-Admin aus `.env` (nur Dev).
- **Erstzugang Prod:** erster Admin über Authentik-Gruppenmitgliedschaft; **kein** hartkodierter
  Default-Login.

## 6. Backup & Datenhaltung

- **PostgreSQL:** regelmäßige Dumps in die ATMED-Backup-Kette (Restic/Backup-Server);
  Point-in-Time optional.
- **Object Storage:** Versionierung + Backup der Buckets.
- **Content/Git:** Autoren-Quelle (`data/`) ist in Git — bereits versioniert/gesichert.
- Wiederherstellung dokumentiert (DB-Restore + Storage-Restore + Re-Sync aus Git).

## 7. Updates & Rollback

- Images getaggt (Git-SHA); Deploy = Tag-Wechsel + `compose up -d`.
- DB-Migrationen vorwärts über Alembic; Rollback über vorherige Migration + vorheriges Image.
- Blue/Green bzw. Staging-Validierung vor Produktiv-Switch (Staging-first).

## 8. CI/CD (GitHub Actions)

1. **Lint/Test** (Pipeline-Python, Backend, Frontend).
2. **Build** Images; **Push** in Registry.
3. **Content-Build** (optional): `make build` erzeugt Artefakte, validiert Schema.
4. **Deploy** auf Staging automatisch; Produktion nach Freigabe.

## 9. Integrationen vorbereiten

- **OIDC/Authentik**, **Moodle (LTI 1.3)**, **WordPress/WooCommerce** (Lizenz-Webhook),
  **QR-Redirect** (`/c/<id>` → stabile Kartenlinks, `online-platform/architecture/qr-redirect-service.md`).
- Saubere Trennung **App / Datenbank / Storage** (Skalierung, Umzug, Backup je Schicht).

## 10. DSGVO / Betriebssicherheit

- Personenbezug: Fortschritt, Notizen, Nutzerprofil → Lösch-/Exportkonzept, Rechte serverseitig.
- Keine Secrets im Repo; Secrets via Umgebung/Secret-Store.
- Logs ohne personenbezogene Inhalte; Zugriff gemäß ATMED-Betriebsregeln.

> Live-Serveränderungen erfolgen **nicht** im Rahmen dieses Konzepts, sondern erst nach
> ausdrücklicher Freigabe durch Andreas und nach den ATMED-SSH-/Betriebsregeln
> (ein Schritt nach dem anderen, Read-only zuerst, Backup vor Änderung).
