# Umzug auf eigene Server – Runbook

ChemBioMed Cards zieht von GitHub auf die Server der AT Medical GmbH. Quellcode, Kartenproduktion und
Auslieferung laufen danach vollständig auf **ATMED-core**. Entscheidung und Begründung:
[ADR-024](../docs/concept/decision-log.md).

| Entscheidung (Andreas, 2026-11-03) | Umsetzung |
|---|---|
| Eigener Git-Server | **Forgejo v15 (LTS)** mit Forgejo Actions |
| Zielserver | **ATMED-core**, Stacks unter `/srv/atmed/stacks/`, hinter dem bestehenden Traefik |
| GitHub danach | **archivieren** (schreibgeschützt, umkehrbar), bis dahin Push-Spiegel |
| Automatik | Jede Änderung auf `main` → **Staging automatisch**; **Produktion nur per Freigabe** und nur Karten mit `approved` |

> **Regeln für jeden Schritt:** Read-only zuerst · ein Befehl nach dem anderen, Ausgabe prüfen ·
> keine Secrets in Dateien des Repos, im Chat oder in Logs · nichts löschen ohne Freigabe von Andreas ·
> jede Phase endet an einem **Gate**. Ist es nicht erfüllt, geht es nicht weiter.

## Überblick

```
 Autor (Browser/Git) ──push/PR──▶ Forgejo (git.…) ──Job──▶ chembiomed-runner (Build-Image)
                                    │                         │ make build · release_cards.py
                                    │                         ▼
                                    │              /srv/atmed/stacks/chembiomed-cards/sites
                                    │                 ├─ staging/current     ◀── jeder Push auf main
                                    │                 └─ production/current  ◀── nur „FREIGABE“ + approved
                                    ▼                         │
                     Push-Spiegel → GitHub (bis Phase 7)      ▼
                                              chembiomed-sites (nginx) ◀─ Traefik + Authentik
```

| Komponente | Datei im Repo | Ziel auf ATMED-core |
|---|---|---|
| Forgejo | `deploy/atmed-core/forgejo/` | `/srv/atmed/stacks/forgejo/` |
| Runner + Auslieferung | `deploy/atmed-core/chembiomed-cards/` | `/srv/atmed/stacks/chembiomed-cards/` |
| Build-/Runner-Image | `deploy/builder/Dockerfile` | lokal gebaut: `chembiomed-builder:<sha>` |
| CI-Workflow | `.forgejo/workflows/cards.yml` | – |
| Paket für Staging/Produktion | `scripts/release_cards.py` | – |
| Veröffentlichen / Rollback | `deploy/scripts/publish-release.sh`, `rollback-release.sh` | – |
| Forgejo-Sicherung | `deploy/atmed-core/forgejo/backup/` | systemd-Timer |
| Secrets (nur dort!) | – | `/srv/atmed/vault/services/{forgejo,chembiomed-cards}/` |

**Ressourcen:** Forgejo ≈ 300 MB RAM (Limit 1 GB). Runner im Leerlauf ≈ 300 MB, beim Rendern bis
etwa 2 GB (Limit 3 GB, 2 CPUs). nginx < 20 MB. Ein voller Build aller 116 Karten dauert etwa 75 s.

**Lokal getestet (2026-11-03, Docker):** Build-Image, Forgejo 15.0.11, Runner 13.2.1 und nginx
1.28. Der Push auf `main` lief grün und hat Staging veröffentlicht (116 Karten, 0 Layoutfehler).
Die Produktion lehnte einen Lauf ohne „FREIGABE“ und einen Lauf ohne `approved`-Karten jeweils ab.
Mit einer freigegebenen Testkarte enthielt die Produktion genau diese eine Karte. Rollback vor und
zurück sowie `forgejo dump` samt Prüfsumme funktionierten.
**Nicht getestet:** die Live-Migration von GitHub (`10-migrate-from-github.sh`, dafür ist ein
GitHub-Token nötig), Traefik, Authentik und DNS auf ATMED-core.

## Gemeinsamer Plan: Projekt 16 + Pharma Cards (Stand 2026-11-03)

Andreas hat entschieden, beide Umzugspakete zu **einem** Plan zusammenzuführen. Grundlage ist dieses
Runbook (Projekt 16, ADR-024). Ergänzt wurden die Pharma Cards (Modul PH) und die Lernplattform
„Pharma Cards online“ (`online-platform/`) aus dem früheren Paket (GitHub-PR #25, abgelöst).

| Baustein | Projekt 16 | Ergänzung Pharma Cards |
|---|---|---|
| Git-Server | Forgejo 15 LTS, `/srv/atmed/stacks/forgejo` | – |
| Runner | `chembiomed-runner`, Host-Modus im Build-Image | Build-Image zusätzlich mit pytest, API-venv (`/opt/api-venv`) und Node 22 LTS |
| CI | `.forgejo/workflows/cards.yml` (Kernkarten) | `.forgejo/workflows/pharma.yml`: PH-Prüfungen, Layout, API-Tests, Web-Build |
| Karten-Releases | `sites/<kanal>/current`, nginx `chembiomed-sites` | PH-Moodle-/Druckpakete im Release unter `pharma/` (`scripts/pharma/add_to_release.py`), Vorschau und Review-PDF nur in Staging |
| Lernplattform | – | Compose-Projekt `pharma-cards-staging` (API, Web, PostgreSQL) über `pharma-deploy` auf dem Host, Antrag des Runners in `requests/` (Phase 4b) |

**Ergebnis Phase 0 (claude-code-atmed-core, 03.11. 18:34) – in diesem Plan berücksichtigt:**

- Ressourcen:
  - 12 CPU, RAM 11 GB frei;
  - **Swap 7,1/8 GB belegt**, deshalb nur ein Job gleichzeitig mit Speicherlimit;
  - `/srv` 84 GB frei.
- Traefik:
  - Netz `traefik_web`, Entrypoint `websecure` mit Standard-Middleware `haertung-grundkopf@file`;
  - Certresolver `letsencrypt` (DNS-Challenge über Cloudflare).
- **Eine Authentik-Forward-Auth-Middleware gibt es auf ATMED-core nicht.** Sowohl
  `authentik-forwardauth@file` als auch `forwardauth@file` fehlen. `AUTH_MIDDLEWARE` in
  `chembiomed-cards/.env` kann deshalb so nicht gesetzt werden. Entscheidung offen (siehe unten).
- Restic sichert `/srv/atmed` vollständig, **schließt aber `/srv/atmed/backups/*`** sowie `*/logs/*`,
  `*/tmp/*`, `*/cache/*` und `*.log` aus. Die Forgejo-Sicherung schreibt deshalb nach
  `/srv/atmed/stacks/forgejo/sicherung/` (korrigiert in `forgejo-backup.sh`).
- Zeitfenster: nicht während des LearningOS-Einbaus (codex) und nicht in den Live-Zeiten
  (Mo–Fr 17:45–20:15, Sa/So 07:45–10:00 und 12:30–14:00).
- Zielpfade, Containernamen und Hostnamen sind frei.

**Offene Entscheidungen (Andreas, vor Phase 1):**

| Punkt | Vorschlag |
|---|---|
| Zugangsschutz für `staging.`/`releases.chembiomed-cards.de` | Eine Authentik-Forward-Auth (Outpost und Middleware) neu einrichten ist ein Eingriff in zentrale Dienste und braucht eigene Freigabe. Bis dahin vorschlagsweise eine IP-Allowlist- oder Basic-Auth-Middleware in `/srv/atmed/traefik/dynamic`. |
| Hostname der Lernplattform-Staging | `pharma-staging.at-medical.de` (Entscheidung 31.10.) beibehalten oder auf `lernen-staging.chembiomed-cards.de` vereinheitlichen. Die Lernplattform hat eigene Anmeldung über Authentik/OIDC und braucht keine Forward-Auth. |
| Authentik-Provider der Lernplattform | `pharma-cards-staging` (Public Client, PKCE) laut `online-platform/ops/staging/STAGING_HANDOVER.md` |

---

## Phase 0 – Read-only-Vorabprüfung

**Status: erledigt** (claude-code-atmed-core, 03.11. 18:34; Ergebnis im Abschnitt „Gemeinsamer Plan“). G0 ist erfüllt bis auf die Authentik-Middleware (offene Entscheidung).

**Wo:** eigener Rechner mit den SSH-Aliasen (`docs/operations/claude-server-access.md` in ATMED-docs).

```bash
bash deploy/scripts/00-preflight-readonly.sh | tee preflight-$(date +%F).txt
```

Die Ausgabe vollständig zurückgeben. Sie liefert die Werte für die `.env`-Dateien.

**Gate G0:**
- frei: ≥ 3 GB RAM, ≥ 20 GB auf `/srv`;
- `traefik_web` vorhanden;
- Entrypoint, Certresolver und **Name der Authentik-Middleware** bestätigt;
- Zielpfade und Containernamen frei;
- bekannt, ob die Backup-Kette `/srv/atmed/backups/` von ATMED-core erfasst.

## Phase 1 – DNS (Cloudflare)

| Name | Typ | Ziel | Proxy |
|---|---|---|---|
| `git.at-medical.de` | A | `91.99.60.101` | **nur DNS** (graue Wolke) |
| `staging.chembiomed-cards.de` | A | `91.99.60.101` | nach Traefik-Konfiguration |
| `releases.chembiomed-cards.de` | A | `91.99.60.101` | nach Traefik-Konfiguration |

Für den Git-Host gilt „nur DNS“, weil der Cloudflare-Proxy Anfragen über 100 MB abbricht, und
große Git-Pushes würden scheitern. Die Hostnamen sind Vorschläge; abweichende Namen in beiden
`.env`-Dateien eintragen.

**Gate G1:** `getent hosts <name>` auf ATMED-core liefert die erwartete Adresse für alle drei Namen
(siehe Preflight-Abschnitt „DNS-Auflösung“).

## Phase 2 – Forgejo bereitstellen

**Wo:** ATMED-core. Ein Befehl pro Schritt.

1. Verzeichnisse anlegen:
   ```bash
   sudo install -d -m 0750 /srv/atmed/stacks/forgejo /srv/atmed/stacks/forgejo/backup
   sudo install -d -m 0700 /srv/atmed/vault/services/forgejo
   ```
2. Dateien aus dem Repo übernehmen: `compose.yaml`, `.env.example` als `.env`, `backup/*`. Bis zur
   Migration kommen sie aus dem GitHub-Branch, danach aus Forgejo. Werte in `.env` aus G0 eintragen.
3. Konfiguration prüfen (ändert nichts):
   ```bash
   cd /srv/atmed/stacks/forgejo && docker compose config --quiet && echo ok
   ```
4. Starten:
   ```bash
   docker compose up -d && docker compose ps
   ```
5. Gesundheit prüfen:
   ```bash
   curl -fsS https://git.at-medical.de/api/healthz
   ```
6. Admin-Konto anlegen. Das zufällige Passwort erscheint **nur einmal**: direkt in Vaultwarden
   ablegen, nicht kopieren oder speichern.
   ```bash
   docker exec -u git forgejo forgejo admin user create --admin --username andreas --email <e-mail-adresse> --random-password --must-change-password
   ```
7. Im Browser anmelden, Passwort ändern und **2FA aktivieren**.

**Gate G2:** Anmeldung per HTTPS mit gültigem Zertifikat funktioniert, 2FA ist aktiv, und
Registrierung ist nicht möglich (`/user/sign_up` zeigt „deaktiviert“).

**Rollback:** `docker compose down` im Stack-Verzeichnis. Daten in `./data` bleiben erhalten.
DNS-Eintrag entfernen.

## Phase 3 – Repository von GitHub übernehmen

**Wo:** eigener Rechner.

1. Auf GitHub ein **fein granuliertes Token nur mit Lesezugriff** auf
   `AT-Medical-GmbH/DIG-chembiomedcards` erzeugen (Contents, Issues, Pull requests, Metadata).
   Ablaufdatum 7 Tage, als Datei mit `chmod 600` speichern.
2. In Forgejo ein Zugriffstoken für das Admin-Konto erzeugen (Einstellungen → Anwendungen) und
   ebenso als Datei speichern.
3. Migration starten. Sie übernimmt Code, alle Branches und Tags, Issues, Pull Requests (auch
   PR #8), Labels und Releases und vergleicht danach alle Branches und Tags:
   ```bash
   FORGEJO_URL=https://git.at-medical.de FORGEJO_TOKEN_FILE=… GITHUB_TOKEN_FILE=… bash deploy/scripts/10-migrate-from-github.sh
   ```
4. **Push-Spiegel nach GitHub** für die Übergangszeit: in Forgejo unter Repository →
   Einstellungen → Spiegel → Push-Spiegel. Ziel ist die GitHub-URL; dazu ein **zweites** GitHub-Token
   mit Schreibrecht nur auf dieses Repo (Contents). Synchronisation „bei Push“. So bleibt GitHub
   aktuell, bis es archiviert wird.
5. Ab jetzt **nur noch in Forgejo arbeiten**. Auf GitHub nicht mehr pushen, sonst überschreibt der
   Spiegel diese Änderungen.

**Gate G3:** Das Skript meldet „identisch“. Issues und PRs sind in Forgejo sichtbar. Ein
Test-Push in Forgejo erscheint über den Spiegel auf GitHub.

**Rollback:** Repo in Forgejo löschen (Freigabe Andreas). GitHub ist unverändert die Quelle.

## Phase 4 – Kartenproduktion einrichten (Runner, Staging)

**Wo:** Forgejo-Weboberfläche, dann ATMED-core.

1. In Forgejo einen Pull Request `claude/pharma-cards-umzug-gemeinsam-apbnpz` → `main` anlegen
   (gemeinsamer Plan, enthält `claude/chembio-cards-planning-c5l2ub`), prüfen und mergen. Danach
   enthält `main` die 116 Kernkarten, die 110 PH-Karten, die Lernplattform und beide Workflows. Der erste Workflow-Lauf
   wartet, bis der Runner läuft.
2. Schutz für `main`: Einstellungen → Branches → Schutzregel. Kein direkter Push, Merge nur per
   PR, Schreibrecht nur für Andreas und die Redaktion.
3. Stack-Verzeichnisse auf ATMED-core anlegen:
   ```bash
   sudo install -d -o 1001 -g 1001 -m 0750 /srv/atmed/stacks/chembiomed-cards/runner /srv/atmed/stacks/chembiomed-cards/sites
   sudo install -d -m 0700 -o 1001 -g 1001 /srv/atmed/vault/services/chembiomed-cards
   ```
4. Quellstand für das Image holen. Dafür in Forgejo ein Token mit Lesezugriff auf das Repository
   erzeugen und als Datei speichern (`chmod 600`). Es wird nur als Header übergeben und nicht in
   `.git/config` gespeichert:
   ```bash
   git -c http.extraHeader="Authorization: Basic $(printf 'andreas:%s' "$(cat ~/.forgejo-read-token)" | base64 -w0)" clone https://git.at-medical.de/AT-Medical-GmbH/DIG-chembiomedcards.git /srv/atmed/stacks/chembiomed-cards/src
   ```
5. Build-Image bauen. Es lädt Pakete von mcr.microsoft.com, PyPI, Ubuntu und code.forgejo.org;
   die Prüfsumme des Runners wird kontrolliert.
   ```bash
   cd /srv/atmed/stacks/chembiomed-cards/src && docker build -f deploy/builder/Dockerfile -t chembiomed-builder:$(git rev-parse --short HEAD) .
   ```
6. Runner-Secret erzeugen, direkt in die Vault-Datei schreiben, nicht anzeigen:
   ```bash
   sudo sh -c 'umask 077; docker exec -u git forgejo forgejo forgejo-cli actions generate-secret | tr -d "\n" > /srv/atmed/vault/services/chembiomed-cards/runner-token; chown 1001:1001 /srv/atmed/vault/services/chembiomed-cards/runner-token'
   ```
7. Runner registrieren, nur für dieses Repository. Die Ausgabe ist die **UUID**:
   ```bash
   sudo docker cp /srv/atmed/vault/services/chembiomed-cards/runner-token forgejo:/tmp/rt && sudo docker exec forgejo chown git /tmp/rt && sudo docker exec -u git forgejo forgejo forgejo-cli actions register --name chembiomed-builder --scope AT-Medical-GmbH/DIG-chembiomedcards --secret-file /tmp/rt; sudo docker exec forgejo rm /tmp/rt
   ```
8. Runner-Konfiguration ablegen, dabei die UUID einsetzen:
   ```bash
   cd /srv/atmed/stacks/chembiomed-cards && sudo sed "s/__RUNNER_UUID__/<UUID>/" src/deploy/atmed-core/chembiomed-cards/runner-config.yaml > runner/config.yaml && sudo chown 1001:1001 runner/config.yaml
   ```
9. `compose.yaml`, `nginx/` und `.env` übernehmen. In `.env` stehen `BUILDER_TAG` aus Schritt 5
   und die Hostnamen bzw. die Middleware aus G0. Dann prüfen:
   ```bash
   docker compose config --quiet && echo ok
   ```
10. Starten:
    ```bash
    docker compose up -d && docker logs --tail 20 chembiomed-runner
    ```
    Erwartet: `declared successfully`, danach `task … repo is AT-Medical-GmbH/DIG-chembiomedcards`.

**Gate G4:** Der Workflow-Lauf in Forgejo (Actions) ist grün und meldet 0 Layoutfehler.
`https://staging.chembiomed-cards.de` fragt nach dem Authentik-Login und zeigt danach 116 Karten
mit Prüfstatus. Ohne Anmeldung ist kein Zugriff möglich.

**Rollback:** `docker compose down` (Stack chembiomed-cards). Für Staging/Produktion einen
früheren Stand aktivieren:
```bash
SITES_DIR=/srv/atmed/stacks/chembiomed-cards/sites src/deploy/scripts/rollback-release.sh staging
```

## Phase 4b – Lernplattform „Pharma Cards online“ (Staging)

**Voraussetzung:**
- G4 erfüllt;
- Authentik-Provider und DNS der Lernplattform stehen (offene Entscheidungen oben);
- die Schritte 2–3 aus `online-platform/ops/staging/STAGING_HANDOVER.md`, wobei die `.env` hier im
  Vault liegt.

Der Runner hat bewusst keinen Docker-Socket. Er legt deshalb nur einen **Antrag** ab (`staging <sha>`).
`pharma-deploy` auf dem Host prüft ihn:
- der Commit muss auf `main` liegen;
- für Produktion muss zusätzlich `/etc/pharma-deploy/production.enabled` existieren.

Danach holt `pharma-deploy` den Stand frisch aus Forgejo und rollt das Compose-Projekt
`pharma-cards-staging` aus. Wird ein Dienst nicht gesund, kehrt es automatisch zum vorherigen Stand
zurück.

1. Verzeichnisse anlegen. Der Runner darf nur Anträge ablegen und Ergebnisse lesen:
   ```bash
   sudo install -d -o root -g 1001 -m 1770 /srv/atmed/stacks/chembiomed-cards/requests
   sudo install -d -o root -g 1001 -m 2750 /srv/atmed/stacks/chembiomed-cards/requests/ergebnis
   sudo install -d -o root -g root -m 0700 /srv/atmed/stacks/chembiomed-cards/requests/done
   sudo install -d -m 0750 /srv/atmed/stacks/chembiomed-cards/online
   ```
2. Konfiguration ablegen. Die `.env` kommt aus der Staging-Vorlage, Passwort neu erzeugen und in
   Vaultwarden ablegen:
   ```bash
   sudo install -m 600 src/online-platform/ops/staging/staging.env.example /srv/atmed/vault/services/chembiomed-cards/online-staging.env
   ```
3. Lese-Token: in Forgejo einen Bot oder ein Token nur mit Lesezugriff auf dieses Repository anlegen,
   nach `/srv/atmed/vault/services/chembiomed-cards/online-deploy-read.token` schreiben
   (root, 0600), nicht anzeigen.
4. `pharma-deploy` installieren:
   ```bash
   sudo install -m 755 src/deploy/atmed-core/pharma-online/pharma-deploy /usr/local/sbin/pharma-deploy
   sudo install -d -m 700 /etc/pharma-deploy && sudo install -m 600 src/deploy/atmed-core/pharma-online/pharma-deploy.conf.example /etc/pharma-deploy/pharma-deploy.conf
   sudo install -m 644 src/deploy/atmed-core/pharma-online/pharma-deploy.{path,service} /etc/systemd/system/ && sudo systemctl daemon-reload
   ```
5. Erster Lauf von Hand, außerhalb der Live-Zeiten:
   ```bash
   sudo pharma-deploy staging "$(git -C src rev-parse origin/main)" && sudo pharma-deploy status
   ```
6. Automatik einschalten:
   - `sudo systemctl enable --now pharma-deploy.path`;
   - in Forgejo die Repo-Variable `PHARMA_ONLINE_STAGING=true` setzen.

**Gate G4b:**
- Die Prüfpunkte aus STAGING_HANDOVER Schritt 5 sind erfüllt: drei Dienste `healthy`,
  `auth_mode: oidc`, keine offenen Ports.
- Ein Test-Merge auf `main` rollt automatisch aus, und der Job „lernplattform“ meldet `ok staging <sha>`.

**Rollback:** `sudo pharma-deploy rollback staging`. Zum Abschalten
`systemctl disable --now pharma-deploy.path` und die Variable `PHARMA_ONLINE_STAGING` entfernen.

## Phase 5 – Sicherung und Überwachung

1. Sicherung einrichten (Zeitpunkt in `forgejo-backup.timer` vor den nächtlichen Restic-Lauf legen,
   siehe Preflight „Backup-Timer“):
   ```bash
   sudo cp /srv/atmed/stacks/forgejo/backup/forgejo-backup.{service,timer} /etc/systemd/system/ && sudo systemctl daemon-reload
   ```
   ```bash
   sudo systemctl start forgejo-backup.service && sudo journalctl -u forgejo-backup -n 5 --no-pager
   ```
   ```bash
   sudo systemctl enable --now forgejo-backup.timer
   ```
2. Sicherstellen, dass `/srv/atmed/stacks/forgejo/sicherung` und `/srv/atmed/stacks/chembiomed-cards/sites`
   in der Restic-Kette von ATINFRA-backup enthalten sind (laut Phase 0: ja, `/srv/atmed` komplett).
   Zusätzlich `/srv/atmed/vault/services/chembiomed-cards/` und den täglichen `pg_dump` der
   Lernplattform (`online-platform/README_DEPLOYMENT.md` Abschnitt 6) unter `/srv/atmed/stacks/chembiomed-cards/online/sicherung/`. Falls nicht, mit Freigabe aufnehmen
   (`parked-hosts.conf` ist davon nicht betroffen).
3. **Wiederherstellungstest:** einen Dump in einem Wegwerf-Container auf einem anderen Pfad
   entpacken und starten. Repositories und Datenbank müssen vollständig sein; danach den Container
   entfernen.
4. Uptime Kuma (ATINFRA-control): Monitore für `https://git.at-medical.de/api/healthz` und
   `https://staging.chembiomed-cards.de` (Statuscode 302/401 = Authentik aktiv).

**Gate G5:** Ein Dump liegt vor und ist in der Restic-Kette nachweisbar. Der
Wiederherstellungstest war erfolgreich. Die Monitore sind grün.

## Phase 6 – Produktion und Anmeldung

1. Forgejo an Authentik anbinden: OIDC-Application `forgejo` in Authentik, dann
   `forgejo admin auth add-oauth` (Client-Secret aus Vaultwarden über eine Datei bzw.
   Umgebungsvariable, nicht auf der Kommandozeile).
2. **Produktion freigeben** (sobald Karten fachlich geprüft sind):
   - Karte in Forgejo bearbeiten: `review_status: approved`, `reviewer`, `references`. PR stellen
     und mergen; Staging zeigt die Karte als „freigegeben“.
   - Actions → Workflow „Karten“ → „Workflow ausführen“ mit Kanal `production`, Bestätigung
     `FREIGABE`.
   - Ohne Bestätigung oder ohne freigegebene Karten bricht der Lauf ab, und die Produktion bleibt
     unverändert.

**Gate G6:** Der erste Produktionsstand ist veröffentlicht und unter `releases.…` erreichbar,
`release.json` nennt den Git-Stand. Die Anmeldung an Forgejo über Authentik funktioniert.

## Phase 7 – GitHub archivieren (frühestens 14 Tage nach G5)

1. Push-Spiegel in Forgejo entfernen. Ein archiviertes Repo nimmt keine Pushes an.
2. Auf GitHub in der README einen Hinweis auf den neuen Ort ergänzen. Das ist der letzte Commit auf
   GitHub.
3. GitHub → Settings → **Archive this repository** (umkehrbar über „Unarchive“).
4. Beide GitHub-Tokens widerrufen.
5. Dokumentation nachziehen:
   - ATMED-infrastructure `inventory/service-catalog.json` (Forgejo, chembiomed-cards);
   - Rolle von ATMED-core in `host-lifecycle.json`;
   - Runbook in ATMED-docs `runbooks/`.

**Gate G7:** Das GitHub-Repo ist als archiviert markiert, die Tokens sind widerrufen und das
Inventar ist aktualisiert.

---

## Betrieb

### Karten produzieren (Redaktion)

1. Karte ändern oder anlegen: `data/cards/<card_id>.yaml`, im Browser über Forgejo oder lokal per
   Git (`templates/README.md`).
2. PR auf `main` stellen. Der Workflow prüft und rendert, veröffentlicht aber nichts.
3. Merge: Staging wird automatisch aktualisiert (≈ 2 min).
4. Fachreview: `approved` setzen, PR und Merge, dann die Produktion freigeben (Phase 6).

### Updates

| Was | Wie |
|---|---|
| Forgejo (Patch innerhalb v15) | Sicherung starten → `FORGEJO_VERSION` in `.env` erhöhen → `docker compose pull && docker compose up -d` → healthz |
| Build-Image / Runner | `src` aktualisieren → Image mit neuem Tag bauen → `BUILDER_TAG` → `docker compose up -d runner` → Workflow manuell (Staging) starten |
| Rückweg | vorherigen Tag in `.env` eintragen → `docker compose up -d` |

### Notfall

- **Produktion zurücksetzen:** `rollback-release.sh production` (siehe Phase 4). Es bleiben die
  letzten 5 Stände je Kanal.
- **Forgejo ausgefallen:** Die Auslieferung (nginx) läuft unabhängig weiter. Wiederherstellung aus
  dem letzten `forgejo dump`.
- **Runner hängt:** `docker restart chembiomed-runner`. Den Lauf in Forgejo neu starten.

### Sicherheitshinweise

- Der Runner führt Workflows dieses Repositorys im Host-Modus aus und darf nach `sites/` schreiben.
  Schreibrecht auf das Repository bedeutet deshalb, Staging und Produktion verändern zu können.
  Darum gelten Branchschutz und ein kleiner Kreis von Schreibberechtigten. Der Runner ist an dieses
  eine Repository gebunden.
- Kein Docker-Socket, kein privilegierter Container, Runner ohne Root, Speicher und CPU begrenzt.
- Forgejo ist ohne eigenen SSH-Port erreichbar (nur HTTPS), die Registrierung ist gesperrt und
  Lesen erfordert eine Anmeldung.
