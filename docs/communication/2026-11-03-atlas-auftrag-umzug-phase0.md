# ATLAS-Auftrag: Umzug auf ATMED-core – Phase 0

- **An:** `claude-code-atmed-core`
- **Thema:** AUFTRAG: ChemBioMed Cards – Umzug auf ATMED-core, Phase 0 Read-only-Prüfung (Projekt 16)
- **Status:** gesendet am 03.11.2026 um 18:32 über ATLAS (ID `20261103T183221-andreas-mcp-22791`). Der erste Versuch um ca. 18:30 scheiterte, weil der Endpunkt „Not Found“ meldete.

## Nachricht

ZIEL: ChemBioMed Cards zieht von GitHub auf ATMED-core (ADR-024, Entscheidung Andreas vom
03.11.2026):

- eigenes Forgejo v15 LTS unter `/srv/atmed/stacks/forgejo`, nur HTTPS über den bestehenden
  Traefik (`traefik_web`);
- Kartenproduktion per Forgejo-Runner unter `/srv/atmed/stacks/chembiomed-cards` (Host-Modus im
  Build-Image, ohne Docker-Socket, ohne Root);
- Staging automatisch bei jedem Push auf `main`, Produktion nur mit „FREIGABE“ und nur Karten mit
  `approved`;
- GitHub später archivieren.

Paket: Repo `AT-Medical-GmbH/DIG-chembiomedcards`, Branch `claude/chembio-cards-planning-c5l2ub`.
Runbook: `deploy/README_MIGRATION.md`. Lokal von Anfang bis Ende getestet.

JETZT NUR PHASE 0 (read-only, von Andreas freigegeben):

- Die Befehle aus `deploy/scripts/00-preflight-readonly.sh` lokal auf core ausführen.
- Den Abschnitt zu ATINFRA-backup bei `claude-code-atinfra-backup` erfragen.
- Nichts anlegen, nichts starten, keine DNS-Änderung.

Bitte zurückmelden:

1. Freier RAM, CPU und Platte auf `/srv`; Last durch laufende Container (auch codex/LearningOS).
2. `traefik_web`, Entrypoint, Certresolver (HTTP- oder DNS-Challenge?) und der genaue Name der
   Authentik-Forward-Auth-Middleware (`authentik-forwardauth@file` oder `forwardauth@file`).
3. Sind die Zielpfade und die Containernamen `forgejo`, `chembiomed-runner` und `chembiomed-sites`
   frei?
4. Erfasst die Restic-Abholung `/srv/atmed/backups` und `/srv/atmed/stacks`?
5. Einwände: Ressourcen, das Konzept Moodle-Staging, LearningOS-Einbau, Zeitfenster.
6. Hostnamen `git.at-medical.de` (nur DNS), `staging.chembiomed-cards.de` und
   `releases.chembiomed-cards.de`: gibt es Konflikte?

Phasen 1–7 erst nach schriftlicher FREIGABE durch Andreas. Keine Secrets, keine Personendaten.
Rückmeldung an andreas mit Thema „ERGEBNIS: ChemBioMed Cards Phase 0“.
