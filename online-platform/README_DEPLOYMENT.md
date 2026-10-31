# Pharma Cards – Betrieb und Deployment

Online-Lernsystem für das Modul PH (Pharma Cards). Konzept: `docs/pharma-cards/08_online-lernsystem.md`,
`09_deployment.md`. Dieses Dokument beschreibt den **tatsächlich gebauten Stand** (MVP, 2026-10-31).

> Ausbildungs- und Lernmaterial – keine Therapieanweisung. Lernende sehen nur fachlich
> freigegebene Karten (`review_status: approved`).

---

## 1. Komponenten

| Dienst | Technik | Aufgabe | Erreichbar |
|---|---|---|---|
| `pharma-web` | SvelteKit (statisch) + nginx | Oberfläche, leitet `/api` intern weiter | ja (einziger öffentlicher Dienst) |
| `pharma-api` | FastAPI, SQLAlchemy, Alembic | REST-API, Wiederholungslogik, Notizen, Review-Protokoll, Downloads | nur intern |
| `postgres` | PostgreSQL 16 | Nutzer-, Fortschritts-, Notiz-, Review-Daten | nur intern |

Kartendaten sind **kein** Datenbankinhalt, der gepflegt wird. Sie kommen beim Start aus
`cards/PH/metadata/*.yaml` (Seed, idempotent). Quelle der Wahrheit bleibt das Git-Repository.
Ein inhaltliches Update heißt deshalb: Karte im Repo ändern, Image neu bauen und deployen. Der Seed
übernimmt die Änderung und legt einen Versions-Snapshot an. Fortschritt und Notizen bleiben erhalten.
Karten, die aus dem Repo entfernt werden, deaktiviert der Seed (sie werden nicht gelöscht).

## 2. Lokal entwickeln

```bash
# Backend (aus online-platform/backend)
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt && playwright install chromium   # Chromium für PDF/PNG
export DATABASE_URL=sqlite:///./dev.db PHARMA_SHOW_UNREVIEWED=true
alembic upgrade head && python -m app.seed
uvicorn app.main:app --reload --port 8000

# Frontend (aus online-platform/frontend), Vite leitet /api an :8000 weiter
npm ci && npm run dev
```

Im lokalen Modus lässt sich oben rechts eine **Test-Identität** wählen (Lernende, Dozent,
Fachreview Pharmakologie/Toxikologie, Admin).

Tests:

```bash
cd online-platform/backend && pytest -q                     # 33 Tests (SQLite)
cd online-platform/frontend && npm run check && npm run build
python3 online-platform/e2e/smoke.py --url http://127.0.0.1:8000   # Browser-E2E (laufende Instanz)
```

## 3. Mit Docker Compose

```bash
cp online-platform/.env.example online-platform/.env      # Werte setzen, Passwort aus Vaultwarden
docker compose -f online-platform/docker-compose.yml --env-file online-platform/.env up -d --build
# -> http://127.0.0.1:8080
```

Beim Start führt `pharma-api` automatisch aus: **Konfiguration prüfen** → `alembic upgrade head` →
Seed → Server. Eine unsichere Konfiguration beendet den Container sofort mit Exit-Code 1. Andernfalls
würde Uvicorn abgestürzte Worker endlos neu starten, und der Fehlstart bliebe unsichtbar.

Hinweise zur `.env`:
- CSP-Quellen in **doppelte** Anführungszeichen setzen: `FRAME_ANCESTORS="'self' https://moodle…"`.
  Compose entfernt sonst die einfachen Anführungszeichen. Aus `'self'` wird `self`, was einen Host
  namens „self“ meint und jede Einbettung blockiert.
- Image-Größen: `pharma-web` ca. 75 MB; `pharma-api` ca. 2,3 GB mit Chromium (PDF/PNG-Downloads),
  deutlich kleiner mit `WITH_PLAYWRIGHT=0` (dann nur HTML-Download).
- Hinter einem TLS-prüfenden Firmenproxy muss dessen CA im Build vertraut werden (z. B. per
  `--build-context` und `update-ca-certificates` in einer frühen Schicht). Auf normalen Build-Hosts
  ist das nicht nötig.

Verifiziert am 2026-10-31: Beide Images gebaut, Stack mit `docker compose up` gestartet, alle drei
Dienste „healthy“. Browser-E2E 8/8 gegen nginx. PDF-Download aus dem Container. API und Datenbank sind
nicht veröffentlicht. Header-Login in Produktion wird mit Exit 1 verweigert.

### Hinter Traefik (ATMED-traefik)

```bash
docker compose -f online-platform/docker-compose.yml -f online-platform/docker-compose.traefik.yml \
  --env-file online-platform/.env up -d --build
```

Das Overlay entfernt den lokalen Port und setzt Traefik-Labels für `PHARMA_HOST`
(TLS über `TRAEFIK_CERTRESOLVER`). `pharma-web` hängt zusätzlich im externen Netz `TRAEFIK_NETWORK`.
API und Datenbank bleiben unerreichbar von außen. Vorher prüfen: Netzname, Entrypoint und
Certresolver müssen zur bestehenden Traefik-Instanz passen (Annahmen in `.env.example`).

## 4. Anmeldung und Rollen

| Modus | Einsatz | Verhalten |
|---|---|---|
| `AUTH_MODE=local` | Entwicklung, **Staging hinter Zugangsschutz** | Identität per Header (Test-Identitäten). In `PHARMA_ENV=production` verweigert die API den Start. |
| `AUTH_MODE=oidc` | Betrieb | Bearer-Token von Authentik. Signatur (JWKS), Ablauf, Issuer und Audience werden geprüft. Rolle aus `OIDC_ROLE_CLAIM` über `OIDC_ROLE_MAP`, sonst `learner`. |

Authentik vorbereiten: OAuth2/OpenID-Provider `pharma-cards` anlegen, die Gruppen `pharma-admin`,
`pharma-editor`, `pharma-reviewer-pharm`, `pharma-reviewer-tox`, `pharma-teacher` und
`pharma-learner` anlegen und den Gruppen-Claim im Token freigeben. Issuer- und JWKS-URL kommen in
die `.env`.

**Offen (nächster Schritt):** Die Browser-Anmeldung der SPA (Authorization Code + PKCE gegen
Authentik) ist noch nicht gebaut. Bis dahin läuft die Anwendung als **Staging** mit
`AUTH_MODE=local` und einem vorgeschalteten Zugangsschutz (`TRAEFIK_MIDDLEWARES`, z. B.
Authentik-Forward-Auth). Die API-Seite (Tokenprüfung, Rollen) ist fertig und getestet.

**Erster Admin:** im lokalen Modus `PHARMA_BOOTSTRAP_ADMIN=<kennung>`, im OIDC-Modus über die
Authentik-Gruppe `pharma-admin`. Es gibt keine Standardpasswörter.

## 5. Sicherheitsregeln (beim Start erzwungen)

- `PHARMA_ENV=production` mit `AUTH_MODE=local` → Start verweigert.
- `PHARMA_ENV=production` mit `PHARMA_SHOW_UNREVIEWED=true` → Start verweigert.
- Lernende sehen nur `approved`-Karten; ungeprüfte Inhalte sehen nur Review-Rollen (mit Entwurfsbanner).
- Downloads ungeprüfter Karten tragen ein ENTWURF-Wasserzeichen.
- Inline-Scripts nur per CSP-Hash, fremde Scripts gesperrt. Einbettung nur von `FRAME_ANCESTORS`.
- Review-Einträge in der App sind ein Protokoll. Den verbindlichen Freigabestatus setzt die
  Kartendatei im Repository (Pull Request = Audit-Trail).

## 6. Backup und Wiederherstellung

| Daten | Wie | Wann |
|---|---|---|
| PostgreSQL (Nutzer, Fortschritt, Notizen, Review-Protokoll) | `docker compose exec postgres pg_dump -U pharma -Fc pharma_cards > pharma_$(date +%F).dump`, danach per Restic auf ATINFRA-backup | täglich |
| Kartendaten | Git | je Commit |

Wiederherstellen: `pg_restore -U pharma -d pharma_cards --clean <datei>`, dann API neu starten
(der Seed gleicht die Karten ab). Wiederherstellung mindestens einmal auf Staging üben.

## 7. Update und Rückweg

1. Vorher Datenbank-Dump (Abschnitt 6).
2. `docker compose … up -d --build`. Migrationen laufen automatisch.
3. Smoke-Test: `python3 online-platform/e2e/smoke.py --url https://<host>` (nur Staging, lokaler Modus).
4. Rückweg: vorheriges Image-Tag (`PHARMA_VERSION`) starten. Bei Schemaänderung vorher
   `docker compose exec pharma-api alembic downgrade -1` oder den Dump zurückspielen.

## 8. Bekannte Grenzen des MVP

- SPA-Login (OIDC/PKCE) offen, siehe Abschnitt 4.
- PNG/PDF-Downloads starten je Anfrage einen Chromium-Prozess. Das reicht für Einzelkarten. Für
  große Exporte ist die Druckpipeline (`make ph-print`) gedacht.
- Annotationen: Datenmodell und API speichern `annotation_data` (JSON-Overlay). Die
  Zeichenwerkzeuge in der Oberfläche folgen.
- Editor für Karten in der App: bewusst nicht enthalten. Karten werden im Repository gepflegt
  (Review per Pull Request).
- Moodle-LTI-1.3-Endpunkte: noch nicht enthalten (Konzept: `docs/pharma-cards/07_moodle-integration.md`).
