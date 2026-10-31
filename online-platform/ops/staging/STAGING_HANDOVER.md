# Pharma Cards – Übergabe Staging-Deployment

Empfänger: Server-Sitzung `claude-code-atmed-core` (Atlas). Freigabe und Zielentscheidung: Andreas Tremml.
Stand: 2026-10-31. Quelle: `AT-Medical-GmbH/DIG-chembiomedcards`, Branch `claude/pharma-cards-staging-handover-apbnpz`.

> Ausbildungs- und Lernmaterial, keine Therapieanweisung. Staging zeigt Lernenden **nur freigegebene**
> Karten; derzeit ist keine Karte freigegeben (Fachreview läuft). Reviewer sehen Entwürfe mit Banner.

## 1. Ziel und Abgrenzung

- Ziel: Pharma Cards (API, Web, PostgreSQL) als **Staging** hinter Traefik, mit Anmeldung über
  Authentik. Danach folgt optional die Moodle-Anbindung (LTI 1.3) gegen einen Test-Kurs.
- **Nicht** Teil dieser Übergabe:
  - Produktion;
  - Änderungen an Authentik-Produktivprovidern, Moodle-Produktivkursen, Traefik-Basiskonfiguration
    oder Mail;
  - Datenmigration.
- Staging-first: keine experimentellen Änderungen an bestehenden produktiven Diensten.

## 2. Offene Entscheidungen (vor Schritt 3, durch Andreas)

| Punkt | Vorschlag | Status |
|---|---|---|
| Zielhost | eigener Staging-Host oder isoliertes Compose-Projekt auf einem Host mit Traefik; **nicht** ATINFRA-backup/-mail | offen |
| Hostname | z. B. `pharma-staging.at-medical.de` (DNS-Eintrag nötig) | offen |
| Authentik | eigener Provider `pharma-cards-staging` (Public Client) | offen |
| Moodle | Test-Kurs auf `moodle.at-medical.de` oder Moodle-Staging | offen |
| Zusätzlicher Zugangsschutz | `TRAEFIK_MIDDLEWARES` (z. B. IP-Allowlist) während Staging | optional |

## 3. Ablauf

Jeder Schritt einzeln, Ausgabe prüfen, erst dann weiter. Zuerst nur lesen.

1. **Lesend prüfen:**
   - Repo auf dem Zielhost auschecken, Branch dieser Übergabe;
   - `bash online-platform/ops/staging/preflight.sh <staging-host> <traefik-netz>`;
   - Docker/Compose, freien Platz, Traefik-Netz, DNS, Authentik-Discovery und bestehende Container
     prüfen.
2. **Authentik** (Freigabe durch Andreas):
   - Provider `pharma-cards-staging`: Public, Redirect `https://<host>/auth/callback`, RS256, Scopes
     `openid profile email offline_access`, Gruppen-Claim;
   - die Gruppen `pharma-*` anlegen; Andreas in `pharma-admin` und `pharma-reviewer-tox` aufnehmen.
3. **Konfiguration:**
   - `cp online-platform/ops/staging/staging.env.example online-platform/.env` und `chmod 600`;
   - Platzhalter ersetzen;
   - das Datenbank-Passwort neu in Vaultwarden anlegen, **nicht** ins Repo.
4. **Start:**
   ```bash
   docker compose -p pharma-cards-staging -f online-platform/docker-compose.yml \
     -f online-platform/docker-compose.traefik.yml --env-file online-platform/.env up -d --build
   ```
   Beim Start laufen Konfigurationsprüfung, `alembic upgrade head` und der Seed automatisch. Eine
   unsichere Konfiguration beendet den Container mit Exit 1.
5. **Ergebnis prüfen:**
   - `docker compose -p pharma-cards-staging ps`: alle drei Dienste `healthy`;
   - `curl -s https://<host>/api/health`: `"auth_mode":"oidc"`;
   - `curl -s https://<host>/api/auth/config`: `authorization_endpoint` von Authentik;
   - API (8000) und PostgreSQL von außen **nicht** erreichbar (`ss -tlnp`, kein veröffentlichter Port);
   - im Browser: Anmeldung über Authentik, Rücksprung, Rolle sichtbar;
   - Lernende sehen „Noch keine freigegebenen Karten“, Reviewer sehen Entwürfe mit Banner.
6. **Backup einrichten:** täglicher `pg_dump` (siehe `README_DEPLOYMENT.md` Abschnitt 6) in den
   bestehenden Restic-Ablauf. Eine Wiederherstellung einmal üben.
7. **Optional: LTI gegen einen Moodle-Testkurs** (`README_DEPLOYMENT.md` Abschnitt 4a):
   - Schlüssel erzeugen: `openssl genpkey …`, `chown 10001:10001`, `chmod 400`; das Backup kommt in
     Vaultwarden;
   - in Moodle das Tool anlegen und `LTI_PLATFORMS` füllen;
   - mit dem zusätzlichen Overlay `-f online-platform/docker-compose.lti.yml` neu starten;
   - als Lehrende eine Aktivität per Deep Linking anlegen, als Lernende starten.

## 4. Rückweg

- Stoppen ohne Datenverlust: `docker compose -p pharma-cards-staging … down`. Das Volume bleibt.
- Vollständig entfernen ist **nur nach Freigabe** erlaubt: `down -v` löscht die Staging-Datenbank.
  Danach den DNS-Eintrag und den Authentik-Provider entfernen.
- Eine fehlerhafte Version wird nicht direkt korrigiert: das vorheriges Image-Tag (`PHARMA_VERSION`)
  starten. Bei Schemaänderung vorher den Dump sichern.

## 5. Rückmeldung an Andreas (per Atlas, ohne Secrets)

- Host, Hostname, Commit, Compose-Projekt;
- Ergebnis der Vorabprüfung, mit Warnungen;
- Ergebnis von Schritt 5, Punkt für Punkt;
- Abweichungen von dieser Anleitung mit Begründung;
- offene Punkte.
