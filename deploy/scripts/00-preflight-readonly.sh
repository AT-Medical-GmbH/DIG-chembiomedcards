#!/usr/bin/env bash
# Phase 0 – Read-only-Vorabprüfung für den Umzug von ChemBioMed Cards auf ATMED-core (ADR-024).
#
# Auf dem eigenen Rechner (mit den freigegebenen SSH-Aliasen) ausführen:
#   bash deploy/scripts/00-preflight-readonly.sh | tee preflight-$(date +%F).txt
# Die Ausgabe vollständig an Claude zurückgeben. Es werden KEINE Änderungen vorgenommen:
# nur Anzeigen, Auflisten und Lesen. Secrets werden nicht ausgegeben (nur Dateinamen).
set -uo pipefail

CORE="${CORE_ALIAS:-ATMED-core}"
BACKUP="${BACKUP_ALIAS:-ATINFRA-backup}"
HOSTS="${CHECK_HOSTS:-git.at-medical.de staging.chembiomed-cards.de releases.chembiomed-cards.de chembiomed-cards.de}"

run() {  # run <alias> <titel> <befehl>
  printf '\n=== [%s] %s ===\n' "$1" "$2"
  ssh -n -T -o BatchMode=yes -o ConnectTimeout=8 "$1" "$3" 2>&1
}

run "$CORE" "Identität" "hostname; hostname -I | cut -d' ' -f1; uptime"
run "$CORE" "Ressourcen" "nproc; free -h; df -h /srv /var/lib/docker 2>/dev/null"
run "$CORE" "Docker" "docker version --format '{{.Server.Version}}'; docker compose version --short"
run "$CORE" "Laufende Container" "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"
run "$CORE" "Speicher/CPU je Container" "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"
run "$CORE" "Netz traefik_web" "docker network ls --format '{{.Name}}' | grep -iE 'traefik|forgejo'; docker network inspect traefik_web --format '{{.Name}} {{.Driver}} Container: {{len .Containers}}'"
run "$CORE" "Traefik-Start-Argumente" "t=\$(docker ps --format '{{.Names}}' | grep -i traefik | head -1); echo \"Container: \${t:-nicht gefunden}\"; [ -n \"\$t\" ] || exit 0; docker inspect \"\$t\" --format '{{.Config.Image}}'; docker inspect \"\$t\" --format '{{range .Args}}{{println .}}{{end}}' | grep -iE 'entrypoints|certificatesresolvers\\.[a-z]+\\.|providers' | sed -E 's/(email|token|key)=.*/\\1=<ausgeblendet>/I'"
run "$CORE" "Traefik-Konfigurationsorte" "ls -ld /srv/atmed/traefik /srv/atmed/stacks/traefik 2>&1; ls /srv/atmed/traefik/dynamic /srv/atmed/stacks/traefik/config/middlewares 2>/dev/null"
run "$CORE" "Middleware-Namen (Forward-Auth)" "grep -rhoE '^ *[A-Za-z0-9_-]*(auth|Auth|secureHeaders)[A-Za-z0-9_-]*:' /srv/atmed/traefik/dynamic /srv/atmed/stacks/traefik/config 2>/dev/null | sort -u; docker ps --format '{{.Names}}' | xargs -r -n1 docker inspect --format '{{.Name}} {{index .Config.Labels \"traefik.http.routers.moodle.middlewares\"}}' 2>/dev/null | grep -v ' $' | head"
run "$CORE" "Ablage-Konvention" "ls -ld /srv/atmed/stacks /srv/atmed/vault/services /srv/atmed/backups 2>&1; ls /srv/atmed/stacks 2>&1"
run "$CORE" "Zielpfade frei?" "for p in /srv/atmed/stacks/forgejo /srv/atmed/stacks/chembiomed-cards /srv/atmed/vault/services/chembiomed-cards /srv/atmed/backups/forgejo; do test -e \$p && echo \"BELEGT  \$p\" || echo \"frei    \$p\"; done"
run "$CORE" "Containernamen frei?" "for n in forgejo chembiomed-runner chembiomed-sites; do docker ps -a --format '{{.Names}}' | grep -qx \$n && echo \"BELEGT  \$n\" || echo \"frei    \$n\"; done"
run "$CORE" "DNS-Auflösung" "for h in $HOSTS; do printf '%-34s ' \$h; getent hosts \$h || echo 'kein Eintrag'; done"
run "$CORE" "Backup-Timer" "systemctl list-timers --all --no-pager | grep -iE 'restic|backup|forgejo' || echo 'keine'"
run "$CORE" "Zeitzone" "timedatectl show -p Timezone --value 2>/dev/null; ls -l /etc/timezone /etc/localtime 2>&1"
run "$CORE" "Moodle (Importformat)" "docker ps --format '{{.Names}}' | grep -i moodle; ls /srv/atmed/moodle-src/mod /srv/atmed/moodle-src/question/type 2>/dev/null | tr '\n' ' '"
run "$BACKUP" "Backup-Kette: erfasste Pfade von ATMED-core" "ls /etc/atmed-backup 2>&1; grep -rnE 'ATMED-core|/srv/atmed' /etc/atmed-backup 2>/dev/null | grep -viE 'pass|token|key|secret' | head -30"

printf '\n=== Ende der Read-only-Prüfung ===\n'
