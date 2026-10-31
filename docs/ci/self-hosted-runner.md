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
| Eigene, isolierte VM nur für CI | kein Zugriff auf Produktivdaten, -netze oder -schlüssel |
| Runner nur für dieses Repo (Repo-Runner, Label `chembiomed`) | andere Repos können ihn nicht nutzen |
| Jeder Job in einem frischen Container (`python:3.12-slim`, `node:22-bookworm-slim`) | Jobs hinterlassen nichts auf dem Host |
| `permissions: contents: read`, `persist-credentials: false` | Jobs bekommen kein Schreib-Token |
| keine Repository-Secrets für die CI | es gibt nichts abzugreifen |
| VM regelmäßig neu aufsetzen (z. B. monatlich, und sofort bei Verdacht) | begrenzt Persistenz |

Restrisiko: Wer Schreibrechte am Repo hat, kann Code auf der VM ausführen. Die Docker-Gruppe ist auf
der VM root-gleich. Deshalb gehört **nichts anderes** auf diese VM.

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

## 3. VM einrichten (Server-Sitzung, nach Freigabe)

Empfehlung:

- neue Hetzner-Cloud-VM (z. B. CX32, Ubuntu 24.04), Name `atinfra-ci-1`;
- **keine** bestehende Produktivmaschine;
- Firewall: eingehend nur SSH von Admin-IPs, ausgehend HTTPS.

```bash
# als root auf der neuen VM
apt-get update && apt-get -y upgrade && apt-get -y install docker.io curl jq
useradd -m -s /bin/bash runner && usermod -aG docker runner
# Aktuelle Runner-Version und SHA256 von github.com/actions/runner/releases übernehmen (nicht raten):
su - runner -c 'mkdir actions-runner && cd actions-runner && curl -fsSLO <URL actions-runner-linux-x64-<VERSION>.tar.gz>'
su - runner -c 'cd actions-runner && echo "<SHA256>  actions-runner-linux-x64-<VERSION>.tar.gz" | sha256sum -c && tar xzf actions-runner-linux-x64-*.tar.gz'
su - runner -c 'cd actions-runner && ./config.sh --unattended --url https://github.com/AT-Medical-GmbH/DIG-chembiomedcards \
  --token <REGISTRIERUNGSTOKEN> --name atinfra-ci-1 --labels chembiomed --work _work --replace'
cd /home/runner/actions-runner && ./svc.sh install runner && ./svc.sh start
```

Prüfen:

- `./svc.sh status` meldet `active (running)`.
- In GitHub steht der Runner auf „Idle“ mit den Labels `self-hosted`, `Linux`, `X64` und
  `chembiomed`.
- `docker run --rm hello-world` läuft als Benutzer `runner`.

Wartung:

- Ein Cron-Job räumt wöchentlich mit `docker system prune -af --filter "until=168h"` auf.
- Updates installiert `unattended-upgrades`.
- Den Runner aktualisiert GitHub selbst.

Rückweg:

- `./svc.sh stop && ./svc.sh uninstall`;
- `./config.sh remove --token <Entfernungs-Token aus GitHub>`;
- VM löschen.
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
