# Pharma Cards – Umzug von GitHub auf AT-Medical-Server (Forgejo auf ATMED-core)

Empfänger: Server-Sitzung `claude-code-atmed-core` (Atlas) bzw. Andreas Tremml am Terminal.
Freigabe: Andreas Tremml. Stand: 2026-11-03.

> Ausbildungs- und Lernmaterial, keine Therapieanweisung. Die Automatisierung ändert nichts am
> Fachreview: Lernende sehen nur freigegebene Karten, Moodle- und Druckpakete enthalten nur
> freigegebene Karten. Entwürfe erscheinen ausschließlich mit ENTWURF-Kennzeichnung.

## 1. Ziel

Das Projekt `DIG-chembiomedcards` läuft künftig vollständig auf eigenen Servern:

| Baustein | Wo | Zweck |
|---|---|---|
| **Forgejo 15 LTS** | ATMED-core, Compose-Projekt `forgejo`, `https://git.at-medical.de` | Git, Pull Requests, Reviews, Issues; führend nach dem Umzug |
| **Forgejo-Runner** | ATMED-core, Benutzer `forgejo-runner`, rootless Docker | CI für jeden PR: Kartenvalidierung, Layout im Browser, API-Tests, Web-Build |
| **pharma-deploy** | ATMED-core, `/usr/local/sbin/pharma-deploy` | einziger Weg von der CI auf den Server: Staging, Produktion (Tag), Inhaltsbau |
| **Staging** | `pharma-staging.at-medical.de`, Compose-Projekt `pharma-cards-staging` | automatisch nach jedem grünen Merge auf main |
| **Inhaltsbau** | `/srv/pharma-cards/exports/<datum>-<sha>/` | jede Nacht Moodle-/Druckpakete (nur freigegeben), Review-PDF, Vorschauen |
| **GitHub** | – | nach erfolgreichem Umzug privat und **archiviert** (nur lesen), nicht gelöscht |

Ablauf eines neuen Inhalts danach:

```text
Entwurf (Branch, z. B. aus einer Claude-Sitzung)  ->  PR in Forgejo  ->  CI grün (Schema, QR, Layout, Tests)
  ->  Fachreview + Merge durch Andreas  ->  Staging automatisch  ->  Inhaltsbau nachts
  ->  Freigabe einzelner Karten (review_status)  ->  Tag vX.Y.Z  ->  Produktion
```

## 2. Entscheidungen

| Punkt | Festlegung | Status |
|---|---|---|
| Software | Forgejo (LTS 15.0.x), Runner v13.2.x | entschieden (Andreas, 2026-11-03) |
| Server | ATMED-core | entschieden (Andreas, 2026-11-03) |
| GitHub danach | privat + archiviert, nur lesen | entschieden (Andreas, 2026-11-03) |
| Hostname | `git.at-medical.de` (DNS-A-Eintrag auf ATMED-core nötig) | Vorschlag |
| Anmeldung | Authentik-Provider `forgejo` (OAuth2/OIDC), lokaler Admin nur als Notzugang | Vorschlag |
| Git über SSH | aus; nur HTTPS über Traefik (kein zusätzlicher offener Port) | Vorschlag |
| Benachrichtigung | ntfy auf ATINFRA-gateway (Thema mit Zugriffsschutz) | optional |

### Auflagen, weil ATMED-core ein Produktivserver ist

Es gelten dieselben Auflagen wie in `online-platform/ops/staging/STAGING_HANDOVER.md`:

- Nur die eigenen Compose-Projekte `forgejo`, `pharma-cards-staging` und später
  `pharma-cards-production` anlegen. Bestehende Container, Projekte, Volumes und die
  Traefik-Basiskonfiguration **nicht** ändern oder neu starten.
- Keine veröffentlichten Ports; alles läuft über Traefik-Labels.
- Ressourcen begrenzen:
  - Forgejo 1 GB / 1,5 CPU;
  - DB 512 MB;
  - Runner höchstens 1 Job gleichzeitig, 3 GB / 2 CPU je Job, systemd-Grenze 4 GB.
- CI-Jobs laufen im **rootless Docker** des Benutzers `forgejo-runner`. Sie haben keinen Zugriff auf
  den System-Docker, auf Moodle, WordPress oder Traefik.
- `docker system prune`, `docker compose down` ohne `-p <eigenes Projekt>` und ähnliche hostweite
  Befehle sind **verboten**.
- Vor jeder Phase lesend prüfen. Bei < 20 GB frei auf `/var/lib/docker`, < 15 GB auf `/home` oder
  dauerhaft hoher Last abbrechen und Andreas melden.

## 3. Ablauf

Jeder Schritt einzeln ausführen, Ausgabe prüfen, erst dann weiter. Jede Phase endet mit einer
Rückmeldung an Andreas. Eine neue Phase beginnt erst nach seinem „weiter“.

### Phase 1 – Lesend prüfen

```bash
git clone https://github.com/AT-Medical-GmbH/DIG-chembiomedcards.git /root/pharma-cards-bootstrap
cd /root/pharma-cards-bootstrap && git checkout main
bash ops/forgejo/preflight.sh git.at-medical.de <traefik-netz>
```

Rückmeldung: Ausgabe der Vorabprüfung. Zusätzlich die Ausgaben von `docker compose ls`, `df -h` und
`free -m`.

### Phase 2 – Forgejo starten

1. DNS: `git.at-medical.de` → ATMED-core (Andreas bzw. ATMED-cloudflare).
2. Konfiguration:
   ```bash
   install -d -m 700 /srv/forgejo
   cp ops/forgejo/forgejo.env.example /srv/forgejo/forgejo.env && chmod 600 /srv/forgejo/forgejo.env
   # FORGEJO_DB_PASSWORD: neu erzeugen (openssl rand -base64 32), in Vaultwarden ablegen, eintragen
   ```
3. Start:
   ```bash
   docker compose -p forgejo -f ops/forgejo/docker-compose.yml --env-file /srv/forgejo/forgejo.env up -d
   docker compose -p forgejo ps        # forgejo und db: healthy
   curl -fsS https://git.at-medical.de/api/healthz
   ```
4. Notzugang anlegen. Das Passwort wird erzeugt und nur in Vaultwarden abgelegt:
   ```bash
   docker compose -p forgejo exec forgejo forgejo admin user create --admin \
     --username atmed-admin --email <admin-adresse> --random-password --must-change-password=false
   ```
5. Authentik:
   - Provider `forgejo` anlegen, Redirect `https://git.at-medical.de/user/oauth2/authentik/callback`;
   - in Forgejo: Website-Administration → Authentifizierungsquellen → OAuth2 „OpenID Connect“, Name
     `authentik`, Discovery `https://auth.at-medical.de/application/o/forgejo/.well-known/openid-configuration`;
   - Andreas meldet sich über Authentik an; der Notzugang macht ihn zum Admin.
6. Organisation `at-medical` anlegen und den Bot-Benutzer `pharma-deploy` einrichten (keine Admin-Rechte).

Prüfen:
- Login über Authentik funktioniert;
- ohne Anmeldung ist nichts sichtbar (`REQUIRE_SIGNIN_VIEW`);
- keine Registrierung möglich;
- `ss -tlnp` zeigt keinen neuen offenen Port.

### Phase 3 – Repo von GitHub importieren

1. Andreas legt auf GitHub ein **fine-grained Token** an: nur dieses Repo, nur Lesen (Contents,
   Issues, Pull requests, Metadata), Ablauf nach 7 Tagen. Das Token kommt in Vaultwarden, nie ins Repo.
2. In Forgejo unter Neue Migration → GitHub:
   - Ziel `at-medical/DIG-chembiomedcards`, privat;
   - Issues, Pull Requests, Labels, Meilensteine und Releases mitnehmen;
   - **kein** Spiegel.
3. Prüfen, ob die Refs identisch sind:
   ```bash
   git ls-remote https://github.com/AT-Medical-GmbH/DIG-chembiomedcards.git | sort > /tmp/gh.refs
   git -c http.extraHeader="Authorization: token $(cat <lese-token-datei>)" \
     ls-remote https://git.at-medical.de/at-medical/DIG-chembiomedcards.git | sort > /tmp/fj.refs
   diff <(grep -E 'refs/(heads|tags)/' /tmp/gh.refs) <(grep -E 'refs/(heads|tags)/' /tmp/fj.refs) && echo identisch
   ```
4. Repo-Einstellungen in Forgejo:
   - Branch-Schutz `main`: nur per PR; Pflicht-Checks `CI / pipeline`, `CI / layout`, `CI / api`,
     `CI / web`; Merge nur durch Andreas;
   - Tag-Schutz `v*`: nur Andreas;
   - Actions aktivieren;
   - Bot `pharma-deploy`: Lesezugriff. Dessen Token (Bereich `read:repository`) kommt nach
     `/etc/pharma-deploy/forgejo-read.token` (root, 0600) und in Vaultwarden.
5. `FORGEJO_MIGRATION_DOMAINS=` leeren und Forgejo mit `up -d` neu starten.

### Phase 4 – Runner einrichten (rootless)

```bash
apt-get install -y uidmap dbus-user-session slirp4netns    # nur falls preflight sie als fehlend meldet
useradd -m -s /bin/bash forgejo-runner
loginctl enable-linger forgejo-runner
sudo -iu forgejo-runner dockerd-rootless-setuptool.sh install   # rootless Docker nur für diesen Benutzer
# Runner-Binary (Version und Prüfsumme von code.forgejo.org/forgejo/runner/releases):
curl -fsSLo /usr/local/bin/forgejo-runner https://code.forgejo.org/forgejo/runner/releases/download/v13.2.1/forgejo-runner-13.2.1-linux-amd64
sha256sum /usr/local/bin/forgejo-runner     # mit der veröffentlichten .sha256 vergleichen
chmod 755 /usr/local/bin/forgejo-runner
install -o forgejo-runner -g forgejo-runner -m 640 ops/forgejo/runner/config.yml /home/forgejo-runner/config.yml
# Registrierungs-Token: Forgejo → Organisation at-medical → Einstellungen → Actions → Runner
sudo -iu forgejo-runner forgejo-runner register --no-interactive \
  --instance https://git.at-medical.de --token <token> --name atmed-core-ci \
  --labels "docker:docker://python:3.12-bookworm,atmed-core-deploy:host"
# Weicht die Registrierung in v13 ab: `forgejo-runner register --help` bzw. Runner-Doku zu Rate ziehen.
sed "s/__UID__/$(id -u forgejo-runner)/" ops/forgejo/runner/forgejo-runner.service > /etc/systemd/system/forgejo-runner.service
systemctl daemon-reload && systemctl enable --now forgejo-runner
```

Prüfen:
- Runner „online“ in Forgejo;
- der PR dieses Pakets (bzw. `workflow_dispatch` von `CI`) läuft grün: pipeline, layout, api, web;
- `docker ps` (System-Docker) zeigt **keine** CI-Container, sie laufen nur im rootless Docker.

Hinweis: Jobs mit dem Label `atmed-core-deploy` laufen direkt als Benutzer `forgejo-runner` ohne
Container. Auf dem Server können sie nur `sudo pharma-deploy` (Phase 5) aufrufen.

### Phase 5 – Automatisches Staging

Setzt die Staging-Übergabe (`online-platform/ops/staging/STAGING_HANDOVER.md`, Schritte 2–3)
voraus: Authentik-Provider `pharma-cards-staging`, DNS und `.env`.

```bash
install -m 755 ops/deploy/pharma-deploy /usr/local/sbin/pharma-deploy
install -d -m 700 /etc/pharma-deploy
install -m 600 ops/deploy/pharma-deploy.conf.example /etc/pharma-deploy/pharma-deploy.conf   # Werte prüfen
visudo -cf ops/deploy/sudoers.pharma-deploy && install -m 440 ops/deploy/sudoers.pharma-deploy /etc/sudoers.d/pharma-deploy
install -d -m 750 /srv/pharma-cards/staging
cp online-platform/ops/staging/staging.env.example /srv/pharma-cards/staging/.env && chmod 600 /srv/pharma-cards/staging/.env
# Platzhalter ersetzen (PHARMA_ROUTER=pharma-cards-staging bleibt)
pharma-deploy staging "$(git rev-parse origin/main)"     # erster Lauf von Hand
pharma-deploy status
```

Danach in Forgejo die Repo-Variable `STAGING_DEPLOY=true` setzen. Ab dann rollt jeder grüne Merge
auf main automatisch auf Staging aus. Wird ein Dienst nicht gesund, kehrt `pharma-deploy` von selbst
zur vorherigen Version zurück und meldet einen Fehler.

Prüfen: die Punkte aus STAGING_HANDOVER Schritt 5, danach ein Test-Merge, der automatisch ausrollt.

### Phase 6 – Inhaltsbau automatisieren

```bash
pharma-deploy content "$(git rev-parse origin/main)"   # erster Lauf von Hand
ls /srv/pharma-cards/exports/latest/                   # preview/, review/, ggf. moodle/, print/
```

Danach die Repo-Variable `CONTENT_BUILD=true` setzen: Der Bau läuft dann jede Nacht um 02:17 UTC.
Solange keine Karte freigegeben ist, bleiben `moodle/` und `print/` leer. Das ist so gewollt.

### Phase 7 – Umschalten, GitHub archivieren

Erst wenn alle Punkte erfüllt sind:

- CI auf Forgejo ist zwei Wochen lang stabil grün;
- Staging rollt automatisch aus;
- Backup und Restore wurden einmal erfolgreich geübt (Abschnitt 4).

Dann:

1. Letzter Abgleich: `git ls-remote` GitHub gegen Forgejo (wie in Phase 3). Hat GitHub neuere Commits,
   diese zuerst nach Forgejo übernehmen.
2. Andreas:
   - GitHub → Settings → Change visibility → **Private**;
   - danach **Archive this repository**;
   - Dependabot und Actions sind damit ebenfalls stillgelegt.
3. Das GitHub-Token aus Phase 3 widerrufen.
4. `README.md` und `CONTRIBUTING`-Hinweise auf `git.at-medical.de` umstellen (eigener PR in Forgejo).

**Wichtig für die Zusammenarbeit mit Claude:** Claude-Code-Sitzungen im Web (claude.ai/code) arbeiten
mit GitHub-Repos. Nach der Archivierung arbeitet Claude an diesem Projekt nur noch über eine
Server-Sitzung auf ATMED-core oder über Remote Control mit einem Checkout aus Forgejo. Branches und
PRs gehen dann direkt an Forgejo.

### Phase 8 – Produktion (eigene Freigabe)

Nicht Teil dieser Übergabe. Sie braucht eigene Entscheidungen:
- Hostname;
- Authentik-Provider;
- Moodle-Produktivkurs;
- Freigabe der ersten Karten durch das Fachreview.

Technisch ist alles vorbereitet:
- `/srv/pharma-cards/production/.env` mit `PHARMA_ROUTER=pharma-cards-production`;
- `touch /etc/pharma-deploy/production.enabled`;
- Repo-Variable `PRODUCTION_DEPLOY=true`.

Danach rollt ein geschütztes Tag `vX.Y.Z` auf main die Produktion aus.

## 4. Backup und Restore

Täglich in den bestehenden Restic-Ablauf (ATINFRA-backup) aufnehmen:

```bash
docker compose -p forgejo exec -T db pg_dump -U forgejo -Fc forgejo > /srv/forgejo/backup/forgejo-db.dump
docker run --rm -v forgejo_forgejo-data:/d:ro -v /srv/forgejo/backup:/b alpine tar czf /b/forgejo-data.tgz -C /d .
docker run --rm -v forgejo_forgejo-config:/d:ro -v /srv/forgejo/backup:/b alpine tar czf /b/forgejo-config.tgz -C /d .
```

Außerdem sichern: `/srv/forgejo/forgejo.env`, `/etc/pharma-deploy/`, `/srv/pharma-cards/*/.env`,
`/srv/pharma-cards/*/secrets/` und den Pharma-Cards-Datenbank-Dump laut `README_DEPLOYMENT.md`
Abschnitt 6.

Restore einmal üben, auf einem Testsystem oder in einem eigenen Compose-Projekt `forgejo-restoretest`
ohne Traefik-Labels: DB einspielen, Daten-Volume entpacken, Repo klonen, Commit-Hash vergleichen.

## 5. Rückweg

- Forgejo stoppen, ohne Daten zu verlieren: `docker compose -p forgejo -f ops/forgejo/docker-compose.yml down`.
  Die Volumes bleiben erhalten.
- Runner stoppen: `systemctl disable --now forgejo-runner`. Die Deploy-Wege sind zusätzlich über die
  Repo-Variablen abschaltbar.
- Staging zurücksetzen: `pharma-deploy rollback staging`.
- Bis Phase 7 ist GitHub unverändert führend und kann jederzeit weiterverwendet werden.
- Nach Phase 7 kann Andreas die Archivierung auf GitHub jederzeit aufheben (Unarchive).
- Löschen ist **nur nach Freigabe** erlaubt: `down -v` entfernt die Forgejo-Daten.

## 6. Rückmeldung an Andreas (je Phase, per Atlas, ohne Secrets)

- Phase, Host, Commit des Pakets;
- Ergebnis jeder Prüfung, Punkt für Punkt;
- Abweichungen von dieser Anleitung mit Begründung;
- Ressourcenlage nach der Phase (`free -m`, `df -h /var/lib/docker /home`, Last);
- offene Punkte und die nächste benötigte Entscheidung.
