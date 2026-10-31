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
cd online-platform/backend && pytest -q                     # 66 Tests (SQLite)
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

### Staging

Die Übergabe für die Server-Sitzung steht in `ops/staging/STAGING_HANDOVER.md`. Sie enthält
offene Entscheidungen, den Ablauf mit der rein lesenden Vorabprüfung `ops/staging/preflight.sh`,
die Konfigurationsvorlage `ops/staging/staging.env.example`, die Ergebnisprüfung und den Rückweg.

## 4. Anmeldung und Rollen

| Modus | Einsatz | Verhalten |
|---|---|---|
| `AUTH_MODE=local` | Entwicklung, **Staging hinter Zugangsschutz** | Identität per Header (Test-Identitäten). In `PHARMA_ENV=production` verweigert die API den Start. |
| `AUTH_MODE=oidc` | Betrieb | Anmeldung im Browser über Authentik (Authorization Code + PKCE). Die API prüft bei jedem Aufruf das Bearer-Token: Signatur (JWKS), Ablauf, Issuer, Audience. Rolle aus `OIDC_ROLE_CLAIM` über `OIDC_ROLE_MAP`, sonst `learner`. |

**Ablauf der Browser-Anmeldung:** Die SPA holt `/api/auth/config` (nur öffentliche Werte) und leitet
zu Authentik. Code-Verifier, `state` und `nonce` liegen dabei in `sessionStorage`. Zurück auf
`/auth/callback` tauscht die SPA den Code über `POST /api/auth/token`. Die API reicht nur die
erlaubten Felder an den Token-Endpunkt weiter und prüft dabei die Redirect-URI. Dadurch bleibt die
CSP der SPA bei `connect-src 'self'`, und es braucht keine CORS-Freigabe in Authentik. Tokens liegen
nur in `sessionStorage` (je Tab), nie in `localStorage`. Läuft das Access-Token ab, erneuert die SPA
es per Refresh-Token. Abmelden führt über den End-Session-Endpunkt von Authentik.

Authentik vorbereiten:

1. OAuth2/OpenID-Provider `pharma-cards` anlegen.
   - Client-Typ **Public** (kein Secret).
   - Redirect-URI exakt `https://<PHARMA_HOST>/auth/callback`.
   - Signierschlüssel RS256.
   - Scopes `openid`, `profile`, `email`, `offline_access`.
   - Der Gruppen-Claim `groups` muss im Token stehen.
2. Anwendung `pharma-cards` mit diesem Provider anlegen.
3. Gruppen anlegen: `pharma-admin`, `pharma-editor`, `pharma-reviewer-pharm`, `pharma-reviewer-tox`,
   `pharma-teacher`, `pharma-learner`.
4. Werte in die `.env` übernehmen:
   - `OIDC_ISSUER` und `OIDC_JWKS_URL`;
   - `OIDC_CLIENT_ID` und `OIDC_AUDIENCE`: beide die Client-ID;
   - `OIDC_REDIRECT_URI` und `OIDC_POST_LOGOUT_URI`.

Die API muss Authentik ausgehend erreichen (JWKS, Discovery, Token-Endpunkt). In Produktion verlangt
sie eine `https`-Redirect-URI und startet sonst nicht.

Verifiziert am 2026-10-31 gegen einen simulierten Provider:
- Browser-E2E 10/10:
  - Anmeldeseite ohne Token;
  - Rücksprung auf die Ursprungsseite;
  - Rolle aus dem Gruppen-Claim;
  - Refresh nach Ablauf;
  - fremder `state` wird abgewiesen;
  - Abmelden.
- Der lokale Smoke-Test besteht weiter mit 8/8.

Der Test gegen das echte Authentik steht aus (Staging).

**Erster Admin:** im lokalen Modus `PHARMA_BOOTSTRAP_ADMIN=<kennung>`, im OIDC-Modus über die
Authentik-Gruppe `pharma-admin`. Es gibt keine Standardpasswörter.

## 4a. Moodle LTI 1.3 (Launch + Deep Linking)

Moodle startet Pharma Cards als externes Tool mit Single Sign-on. Lehrende wählen per Deep Linking ein
Lernset oder eine freigegebene Karte als Aktivität. Noten werden nicht zurückgegeben (kein AGS).

| Endpunkt | Zweck |
|---|---|
| `/api/lti/login` | Login-Init (Third-Party-Initiated Login), GET oder POST |
| `/api/lti/launch` | Launch-/Redirect-URL (form_post mit `id_token`) |
| `/api/lti/jwks` | öffentlicher Tool-Schlüssel (für die Signatur der Deep-Linking-Antwort) |

**Sicherheit und Datenschutz:**

- `state` und `nonce` werden serverseitig einmalig gespeichert (keine Cookies, funktioniert im iframe)
  und nach 10 Minuten verworfen.
- Geprüft werden:
  - Signatur über die JWKS der Plattform;
  - Issuer;
  - Audience (die eigene `client_id`);
  - Ablauf;
  - `nonce`;
  - Deployment;
  - LTI-Version `1.3.0`;
  - Nachrichtentyp.
- Rollen: Moodle-Lehrende werden `teacher`, alle anderen `learner`. Über LTI werden nie Review- oder
  Admin-Rechte vergeben, und Lernende sehen auch über Moodle nur freigegebene Karten.
- Gespeichert wird nur eine pseudonyme Kennung (Hash aus Plattform und `sub`), keine Namen und keine
  E-Mail-Adressen.
- Nach dem Start stellt die API ein eigenes Sitzungstoken aus (RS256, Standard 4 h). Es wird im
  URL-Fragment übergeben, also nicht in Server-Logs, und liegt danach nur in `sessionStorage`.
  Für Deep Linking gilt die Sitzung nur 30 Minuten.
- Ziele aus `custom` (`set=<slug>`, `card=ph_###`) werden streng geprüft. Andere Werte führen zur
  Startseite (kein Open Redirect).

**Einrichten:**

1. Tool-Schlüssel erzeugen (siehe Kopf von `docker-compose.lti.yml`). Er muss für UID 10001 lesbar
   sein. Ein Backup gehört in Vaultwarden, nie ins Repo; `.gitignore` sperrt `secrets/` und `*.pem`.
2. Moodle → Website-Administration → Plugins → Externes Tool → Tools verwalten → Tool manuell
   konfigurieren:
   - LTI-Version 1.3;
   - Tool-URL `https://<host>/api/lti/launch`;
   - Login-URL `https://<host>/api/lti/login`;
   - Weiterleitungs-URL `https://<host>/api/lti/launch`;
   - Schlüsseltyp „Schlüsselsatz-URL“ `https://<host>/api/lti/jwks`;
   - „Unterstützt Deep Linking“ an;
   - Datenschutz: Name und E-Mail **nicht** übertragen (werden ohnehin nicht genutzt).
3. Die Werte aus „Tool-Konfigurationsdetails“ in `LTI_PLATFORMS` übernehmen: Plattform-ID = `issuer`,
   Client-ID, Deployment-ID, URL für Authentifizierungsanfragen, URL für öffentliche Schlüsselsätze.
   Dazu `PHARMA_PUBLIC_URL` setzen.
4. Mit dem Overlay starten:
   `docker compose -f docker-compose.yml -f docker-compose.traefik.yml -f docker-compose.lti.yml --env-file .env up -d`.
5. Für die Einbettung als iframe `FRAME_ANCESTORS` um die Moodle-Origin erweitern. Alternativ in
   Moodle „In neuem Fenster öffnen“ wählen; das ist robuster bei Browsern mit strenger
   Speicher-Partitionierung.

Verifiziert am 2026-10-31 gegen eine simulierte Moodle-Plattform (`e2e/mock_moodle.py`):

- API-Tests 22/22, unter anderem:
  - Signatur, Audience, Issuer, `nonce`, Deployment, Version und Nachrichtentyp;
  - Replay;
  - Deep-Link-Sperren;
  - gefälschtes Sitzungstoken.
- Browser-E2E 10/10 (`e2e/lti_flow.py`).
- Migration 0002 up/down/up.

Der Test gegen das echte Moodle steht aus (Staging).

## 5. Sicherheitsregeln (beim Start erzwungen)

- `PHARMA_ENV=production` mit `AUTH_MODE=local` → Start verweigert.
- `PHARMA_ENV=production` mit `PHARMA_SHOW_UNREVIEWED=true` → Start verweigert.
- `LTI_ENABLED` ohne Schlüsseldatei, ohne Plattform oder (in Produktion) ohne `https`-`PHARMA_PUBLIC_URL` → Start verweigert.
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

- SPA-Login (OIDC/PKCE) ist gebaut, aber noch nicht gegen das echte Authentik getestet (Staging).
- PNG/PDF-Downloads starten je Anfrage einen Chromium-Prozess. Das reicht für Einzelkarten. Für
  große Exporte ist die Druckpipeline (`make ph-print`) gedacht.
- Annotationen: Datenmodell und API speichern `annotation_data` (JSON-Overlay). Die
  Zeichenwerkzeuge in der Oberfläche folgen.
- Editor für Karten in der App: bewusst nicht enthalten. Karten werden im Repository gepflegt
  (Review per Pull Request).
- Moodle LTI 1.3: Launch und Deep Linking sind gebaut (Abschnitt 4a). Keine Notenrückgabe (AGS) und
  noch nicht gegen das echte Moodle getestet.
