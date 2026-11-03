# Umzug auf eigene Server – Runbook

ChemBioMed Cards zieht von GitHub auf die Server der AT Medical GmbH. Quellcode, Kartenproduktion und
Auslieferung laufen danach vollständig auf **ATMED-core**. Entscheidung und Begründung:
[ADR-024](../docs/concept/decision-log.md).

| Entscheidung (Andreas, 2026-11-03) | Umsetzung |
|---|---|
| Eigener Git-Server | **Forgejo v15 (LTS)** mit Forgejo Actions |
| Zielserver | **ATMED-core**, Stacks unter `/srv/atmed/stacks/`, hinter dem bestehenden Traefik |
| GitHub danach | **nicht mehr weiterbetreiben**: archivieren, sobald Staging aus Forgejo läuft (G4), ohne Wartezeit und umkehrbar |
| Automatik | Jede Änderung auf `main` → **Staging automatisch**; **Produktion nur per Freigabe** und nur Karten mit `approved` |

> **Ergebnis Phase 0 (claude-code-atmed-core, 03.11.2026 18:34):**
> - **Ressourcen:** 12 CPU, 11 GB RAM frei; Swap fast voll, deshalb Runner mit Speicherlimit und nur ein Lauf gleichzeitig. Auf /srv sind 84 GB frei.
> - **Traefik:** `traefik_web`, Entrypoint `websecure` (Middleware `haertung-grundkopf@file`), Certresolver `letsencrypt` per DNS-Challenge.
> - **Keine Authentik-Forward-Auth auf core:** Staging und Produktion werden daher zunächst per Kennwort in nginx geschützt, Forgejo über Authentik-OIDC.
> - **Sicherung:** Restic sichert `/srv/atmed` komplett, **ohne** `/srv/atmed/backups`. Der Forgejo-Dump liegt deshalb unter `/srv/atmed/stacks/forgejo/sicherung`.
> - **Zielpfade, Containernamen und Hostnamen:** alle frei.
> - **Zeitfenster:** nicht während des LearningOS-Einbaus und nicht in den Live-Zeiten (Mo–Fr 17:45–20:15, Sa/So 07:45–10:00 und 12:30–14:00).

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
                     (GitHub: archiviert nach G4)             ▼
                                              chembiomed-sites (nginx, Anmeldung) ◀─ Traefik
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
| Forgejo-Sicherung (Ablage) | – | `/srv/atmed/stacks/forgejo/sicherung/` (von Restic erfasst) |

**Ressourcen:** Forgejo ≈ 300 MB RAM (Limit 1 GB). Runner im Leerlauf ≈ 300 MB, beim Rendern bis
etwa 2 GB (Limit 3 GB, 2 CPUs). nginx < 20 MB. Ein voller Build aller 116 Karten dauert etwa 75 s.

**Lokal getestet (2026-11-03, Docker):** Build-Image, Forgejo 15.0.11, Runner 13.2.1 und nginx
1.28. Der Push auf `main` lief grün und hat Staging veröffentlicht (116 Karten, 0 Layoutfehler).
Die Produktion lehnte einen Lauf ohne „FREIGABE“ und einen Lauf ohne `approved`-Karten jeweils ab.
Mit einer freigegebenen Testkarte enthielt die Produktion genau diese eine Karte. Rollback vor und
zurück sowie `forgejo dump` samt Prüfsumme funktionierten.
Nach Phase 0 ebenfalls lokal geprüft: Der Kennwortschutz von nginx antwortet ohne oder mit
falschem Kennwort mit 401, mit richtigem Kennwort mit 200.
**Nicht getestet:** die Live-Migration von GitHub (`10-migrate-from-github.sh`, dafür ist ein
GitHub-Token nötig), Traefik, Authentik und DNS auf ATMED-core.

---

## Phase 0 – Read-only-Vorabprüfung

**Wo:** eigener Rechner mit den SSH-Aliasen (`docs/operations/claude-server-access.md` in ATMED-docs).

```bash
bash deploy/scripts/00-preflight-readonly.sh | tee preflight-$(date +%F).txt
```

Die Ausgabe vollständig zurückgeben. Sie liefert die Werte für die `.env`-Dateien.

**Erledigt am 03.11.2026, Ergebnis oben.** **Gate G0:**
- frei: ≥ 3 GB RAM, ≥ 20 GB auf `/srv`;
- `traefik_web` vorhanden;
- Entrypoint, Certresolver und **Name der Authentik-Middleware** bestätigt;
- Zielpfade und Containernamen frei;
- bekannt, ob die Backup-Kette `/srv/atmed/backups/` von ATMED-core erfasst.

## Phase 1 – DNS (Cloudflare)

| Name | Typ | Ziel | Proxy |
|---|---|---|---|
| `git.at-medical.de` | A | `91.99.60.101` | **Proxy an** |
| `staging.chembiomed-cards.de` | A | `91.99.60.101` | Proxy an |
| `releases.chembiomed-cards.de` | A | `91.99.60.101` | Proxy an |

Der Proxy bleibt an, damit die Server-IP verdeckt bleibt (Hinweis aus Phase 0). Er bricht Anfragen
über 100 MB ab; das Repository hat etwa 32 MB, und Build-Artefakte werden nicht versioniert. Die
Zertifikate kommen per DNS-Challenge und funktionieren deshalb auch mit Proxy. Zuständig ist
`claude-code-atinfra-gateway` (Cloudflare).

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
8. Anmeldung über Authentik (OIDC) direkt hier einrichten, nicht erst in Phase 6, weil der Dienst
   öffentlich erreichbar ist. In Authentik (über `claude-code-atinfra-gateway`) die Application
   `forgejo` anlegen; Redirect `https://git.at-medical.de/user/oauth2/authentik/callback`. Dann:
   ```bash
   docker exec -u git forgejo forgejo admin auth add-oauth --name authentik --provider openidConnect --key forgejo --secret "$(cat /srv/atmed/vault/services/forgejo/oidc-secret)" --auto-discover-url https://<authentik-host>/application/o/forgejo/.well-known/openid-configuration
   ```
   Das Client-Secret wird nur aus der Vault-Datei gelesen.

**Gate G2:** Anmeldung per HTTPS mit gültigem Zertifikat funktioniert, 2FA ist aktiv, und
Registrierung ist nicht möglich (`/user/sign_up` zeigt „deaktiviert“). Die Anmeldung über
Authentik funktioniert.

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
4. **Ohne GitHub-Token** (falls keins erzeugt werden soll): eine vollständige Git-Kopie aller
   Branches und Tags über einen vorhandenen Lesezugang
   (`git clone --mirror`, danach `git push --mirror` nach Forgejo). Damit fehlen Issues und PRs.
   PR #8 (Pharma) dann als Issue in Forgejo mit Verweis auf GitHub vermerken.
5. Ab jetzt **nur noch in Forgejo arbeiten**. Auf GitHub wird nichts mehr gepusht. Kein
   Push-Spiegel, weil GitHub nach G4 archiviert wird.

**Gate G3:** Das Skript meldet „identisch“ (oder `git ls-remote` stimmt bei der Spiegelkopie
überein). Issues und PRs sind in Forgejo sichtbar.

**Rollback:** Repo in Forgejo löschen (Freigabe Andreas). GitHub ist unverändert die Quelle.

## Phase 4 – Kartenproduktion einrichten (Runner, Staging)

**Wo:** Forgejo-Weboberfläche, dann ATMED-core.

1. In Forgejo einen Pull Request `claude/chembio-cards-planning-c5l2ub` → `main` anlegen, prüfen
   und mergen. Danach enthält `main` die 116 Karten und die Pipeline. Der erste Workflow-Lauf
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
9. Kennwortdatei für Staging/Produktion anlegen. Das Kennwort wird abgefragt und landet in
   Vaultwarden, nicht im Verlauf:
   ```bash
   read -rs -p "Kennwort: " pw; echo; printf 'redaktion:%s\n' "$(openssl passwd -apr1 "$pw")" | sudo tee /srv/atmed/vault/services/chembiomed-cards/sites.htpasswd >/dev/null; unset pw
   ```
10. `compose.yaml`, `nginx/` und `.env` übernehmen. In `.env` stehen `BUILDER_TAG` aus Schritt 5
   und die Hostnamen. Dann prüfen:
   ```bash
   docker compose config --quiet && echo ok
   ```
11. Starten:
    ```bash
    docker compose up -d && docker logs --tail 20 chembiomed-runner
    ```
    Erwartet: `declared successfully`, danach `task … repo is AT-Medical-GmbH/DIG-chembiomedcards`.

**Gate G4:** Der Workflow-Lauf in Forgejo (Actions) ist grün und meldet 0 Layoutfehler.
`https://staging.chembiomed-cards.de` verlangt eine Anmeldung und zeigt danach 116 Karten mit
Prüfstatus. Ohne Anmeldung kommt 401.

**Rollback:** `docker compose down` (Stack chembiomed-cards). Für Staging/Produktion einen
früheren Stand aktivieren:
```bash
SITES_DIR=/srv/atmed/stacks/chembiomed-cards/sites src/deploy/scripts/rollback-release.sh staging
```

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
2. Laut Phase 0 sind `/srv/atmed/stacks/forgejo/sicherung` und
   `/srv/atmed/stacks/chembiomed-cards/sites` von Restic erfasst. Nach dem ersten nächtlichen Lauf
   bei `claude-code-atinfra-backup` bestätigen lassen, dass der Dump im Snapshot liegt.
3. **Wiederherstellungstest:** einen Dump in einem Wegwerf-Container auf einem anderen Pfad
   entpacken und starten. Repositories und Datenbank müssen vollständig sein; danach den Container
   entfernen.
4. Uptime Kuma (ATINFRA-control): Monitore für `https://git.at-medical.de/api/healthz` und
   `https://staging.chembiomed-cards.de` (Statuscode 401 = Schutz aktiv).

**Gate G5:** Ein Dump liegt vor und ist in der Restic-Kette nachweisbar. Der
Wiederherstellungstest war erfolgreich. Die Monitore sind grün.

## Phase 6 – Produktion und Anmeldung

1. Optional: Staging und Produktion von Kennwort auf Authentik umstellen. Dafür braucht core einen
   Authentik-Outpost bzw. eine Forward-Auth-Middleware, die es dort noch nicht gibt (eigener
   Auftrag an gateway).
2. **Produktion freigeben** (sobald Karten fachlich geprüft sind):
   - Karte in Forgejo bearbeiten: `review_status: approved`, `reviewer`, `references`. PR stellen
     und mergen; Staging zeigt die Karte als „freigegeben“.
   - Actions → Workflow „Karten“ → „Workflow ausführen“ mit Kanal `production`, Bestätigung
     `FREIGABE`.
   - Ohne Bestätigung oder ohne freigegebene Karten bricht der Lauf ab, und die Produktion bleibt
     unverändert.

**Gate G6:** Der erste Produktionsstand ist veröffentlicht und unter `releases.…` erreichbar,
`release.json` nennt den Git-Stand. 

## Phase 7 – GitHub stilllegen (direkt nach G4)

1. Letzter Abgleich: `git ls-remote` von GitHub und Forgejo vergleichen. Alles auf GitHub muss
   auch in Forgejo sein.
2. Auf GitHub in der README einen Hinweis auf den neuen Ort ergänzen. Das ist der letzte Commit auf
   GitHub.
3. GitHub → Settings → **Archive this repository** (umkehrbar über „Unarchive“).
4. Das GitHub-Token widerrufen, falls eins erzeugt wurde.
5. Dokumentation nachziehen:
   - ATMED-infrastructure `inventory/service-catalog.json` (Forgejo, chembiomed-cards);
   - Rolle von ATMED-core in `host-lifecycle.json`;
   - Runbook in ATMED-docs `runbooks/`.

**Gate G7:** Das GitHub-Repo ist als archiviert markiert, das Token ist widerrufen und das
Inventar ist aktualisiert.

> **Folge für KI-Sitzungen:** Cloud-Sitzungen von Claude Code (claude.ai/code) arbeiten nur mit
> GitHub-Repositories. Nach der Archivierung wird ChemBioMed Cards in einer Claude-Code-Sitzung auf
> dem Server (z. B. `claude-code-atmed-core`) oder lokal mit Zugang zu Forgejo weiterentwickelt.

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
  dem letzten `forgejo dump` in `/srv/atmed/stacks/forgejo/sicherung/`.
- **Runner hängt:** `docker restart chembiomed-runner`. Den Lauf in Forgejo neu starten.

### Sicherheitshinweise

- Der Runner führt Workflows dieses Repositorys im Host-Modus aus und darf nach `sites/` schreiben.
  Schreibrecht auf das Repository bedeutet deshalb, Staging und Produktion verändern zu können.
  Darum gelten Branchschutz und ein kleiner Kreis von Schreibberechtigten. Der Runner ist an dieses
  eine Repository gebunden.
- Kein Docker-Socket, kein privilegierter Container, Runner ohne Root, Speicher und CPU begrenzt.
- Forgejo ist ohne eigenen SSH-Port erreichbar (nur HTTPS), die Registrierung ist gesperrt und
  Lesen erfordert eine Anmeldung.
