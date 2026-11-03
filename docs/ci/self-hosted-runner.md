# Eigener GitHub-Actions-Runner für DIG-chembiomedcards

Stand 2026-10-31. Entscheidung von Andreas Tremml: Das Repo wird privat gestellt, und die CI läuft auf
einem eigenen Runner. Anlass: Die GitHub-Runner sind organisationsweit wegen Billing gesperrt.

> **Reihenfolge ist Pflicht:** Das Repo erst **privat** stellen, dann den Runner registrieren. Ein
> eigener Runner an einem öffentlichen Repo führt Code aus fremden Fork-PRs auf unserem Server aus.

## 1. Sicherheitsmodell

| Maßnahme | Wirkung |
|---|---|
| Repo privat | Fremde können keine PRs mit Workflow-Code einreichen |
| Fork-PRs gesperrt (Workflow-Bedingung **und** Repo-Einstellung) | doppelte Absicherung |
| Runner auf **ATINFRA-control** (Entscheidung Andreas, 2026-10-31) unter eigenem Benutzer `runner` mit **rootless Docker** | Jobs erhalten keine Root-Rechte auf dem Kontrollzentrum |
| Runner nur für dieses Repo (Repo-Runner, Label `chembiomed`) | andere Repos können ihn nicht nutzen |
| Jeder Job in einem frischen Container (`python:3.12-slim`, `node:22-bookworm-slim`) | Jobs hinterlassen nichts auf dem Host |
| `permissions: contents: read`, `persist-credentials: false` | Jobs bekommen kein Schreib-Token |
| keine Repository-Secrets für die CI | es gibt nichts abzugreifen |
| VM regelmäßig neu aufsetzen (z. B. monatlich, und sofort bei Verdacht) | begrenzt Persistenz |

Restrisiko: Wer Schreibrechte am Repo hat, kann Code als Benutzer `runner` auf ATINFRA-control ausführen
und dessen Netzzugang nutzen. Deshalb gilt verbindlich:

- `runner` ist **nicht** in der Gruppe `docker` und hat kein `sudo`; Jobs nutzen ausschließlich den
  rootless-Docker-Daemon dieses Benutzers (die root-gleiche System-Docker-Gruppe bleibt unberührt).
- `runner` hat keinen Lesezugriff auf `/srv`, Inventar, SSH-Schlüssel oder Konfigurationen des
  Kontrollzentrums (Rechte prüfen: `sudo -u runner ls /srv` muss scheitern).
- Bei Verdacht oder wenn das nicht einhaltbar ist: Runner entfernen und auf eine eigene VM umziehen
  (ursprüngliche Empfehlung, Abschnitt 3a).

## 2. Schritte für Andreas (GitHub)

1. Repo → Settings → General → Danger Zone → **Change visibility → Private**.
   - Folgen: Sterne und Beobachter gehen verloren.
   - Öffentliche Links auf Dateien funktionieren nicht mehr, etwa QR-Codes, die auf GitHub zeigen.
     Die Karten-QR-Codes zeigen auf `chembiomed-cards.de` und sind nicht betroffen.
2. Repo → Settings → Actions → General:
   - „Fork pull request workflows“: **nicht** ausführen.
   - „Workflow permissions“: **Read repository contents**.
3. Repo → Settings → Actions → Runners → **New self-hosted runner** (Linux x64). Den angezeigten
   Registrierungs-Token nur auf der VM verwenden. Er ist eine Stunde gültig. Nicht speichern, nicht
   per Chat oder Atlas senden.

## 3. Runner auf ATINFRA-control einrichten (Server-Sitzung, nach Freigabe)

Erst lesend prüfen: `hostname`, freier Platz, laufende Container, ob ein Benutzer `runner` schon
existiert. Bestehende Dienste und die System-Docker-Installation werden **nicht** verändert.

```bash
# als root auf ATINFRA-control
apt-get -y install uidmap dbus-user-session slirp4netns docker-ce-rootless-extras  # Paketname je nach Docker-Quelle prüfen
useradd -m -s /bin/bash runner            # NICHT in die Gruppe docker
loginctl enable-linger runner
su - runner -c 'dockerd-rootless-setuptool.sh install'
su - runner -c 'echo "export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock" >> ~/.bashrc'
# Aktuelle Runner-Version und SHA256 von github.com/actions/runner/releases übernehmen (nicht raten):
su - runner -c 'mkdir actions-runner && cd actions-runner && curl -fsSLO <URL actions-runner-linux-x64-<VERSION>.tar.gz>'
su - runner -c 'cd actions-runner && echo "<SHA256>  actions-runner-linux-x64-<VERSION>.tar.gz" | sha256sum -c && tar xzf actions-runner-linux-x64-*.tar.gz'
su - runner -c 'cd actions-runner && echo "DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock" >> .env'
su - runner -c 'cd actions-runner && ./config.sh --unattended --url https://github.com/AT-Medical-GmbH/DIG-chembiomedcards \
  --token <REGISTRIERUNGSTOKEN> --name atinfra-control-ci --labels chembiomed --work _work --replace'
cd /home/runner/actions-runner && ./svc.sh install runner && ./svc.sh start
```

### 3a. Alternative: eigene VM

Falls rootless Docker auf ATINFRA-control nicht sauber läuft: neue Hetzner-VM (z. B. CX32, Ubuntu
24.04, `atinfra-ci-1`), Firewall eingehend nur SSH von Admin-IPs; dort ist die normale Docker-Gruppe
vertretbar, weil nichts anderes auf der VM liegt.

Prüfen:

- `./svc.sh status` meldet `active (running)`.
- In GitHub steht der Runner auf „Idle“ mit den Labels `self-hosted`, `Linux`, `X64` und
  `chembiomed`.
- `docker run --rm hello-world` läuft als Benutzer `runner` gegen den rootless-Daemon
  (`docker info` zeigt `rootless`); `id runner` zeigt **keine** Gruppe `docker`.

Wartung:

- Ein Cron-Job des Benutzers `runner` räumt wöchentlich **nur dessen** rootless-Daemon auf
  (`docker system prune -af --filter "until=168h"` mit gesetztem `DOCKER_HOST`), nie die System-Docker-Instanz.
- Updates installiert `unattended-upgrades`.
- Den Runner aktualisiert GitHub selbst.

Rückweg:

- `./svc.sh stop && ./svc.sh uninstall`;
- `./config.sh remove --token <Entfernungs-Token aus GitHub>`;
- `loginctl disable-linger runner`, Benutzer `runner` samt Home entfernen (nur nach Freigabe).
- Ohne eigenen Runner bleiben die Jobs „queued“. Das ist harmlos, es läuft nichts.

## 4. Workflows

| Datei | Jobs |
|---|---|
| `.github/workflows/validate-metadata.yml` | Registry-Metadaten (bestehender Check) |
| `.github/workflows/pharma-ci.yml` | `pipeline` (PH-Validierung, Registry, Export-Tests), `api` (pytest), `web` (svelte-check, Build) |

Alle Jobs laufen mit `runs-on: [self-hosted, linux, chembiomed]` und nie für Fork-PRs. Schritte
für Teile, die es auf einem Stand noch nicht gibt, überspringen sich selbst (`hashFiles`).

**Wichtig für offene PRs:** Bei `pull_request` verwendet GitHub die Workflow-Dateien **des PR-Branches**.
Die PRs #8–#13 laufen deshalb erst dann auf dem eigenen Runner, wenn ihr Branch diesen Stand von
`main` übernommen hat. Das passiert nach dem Merge dieses PRs durch ein Merge oder Rebase der Kette.

## 5. Offen / zu prüfen

- Ob die Billing-Sperre der Organisation auch Jobs auf eigenen Runnern blockiert, ist **nicht
  verifiziert**. Prüfen mit einem manuellen Lauf (`workflow_dispatch`) nach der Registrierung.
- Das Chromium-basierte Layout-Gate (`make ph-layout-check`) und die PNG/PDF-Downloads laufen noch
  nicht in der CI. Dafür käme ein Playwright-Container (`mcr.microsoft.com/playwright/python:v1.56.0`)
  dazu, sobald der Runner steht.
