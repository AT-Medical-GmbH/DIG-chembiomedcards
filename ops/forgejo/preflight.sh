#!/usr/bin/env bash
# Forgejo/CI auf ATMED-core – Vorabprüfung. NUR LESEND: ändert nichts am Host.
#   bash ops/forgejo/preflight.sh [forgejo-host] [traefik-netz]
#   bash ops/forgejo/preflight.sh git.at-medical.de proxy
set -u
HOST="${1:-git.at-medical.de}"
NET="${2:-proxy}"
fail=0
ok()   { printf 'OK    %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*"; }
bad()  { printf 'FEHL  %s\n' "$*"; fail=1; }

echo "== Host"; hostname; uname -sr; . /etc/os-release 2>/dev/null && echo "$PRETTY_NAME"
[ "$(hostname)" = "core.at-medical.de" ] || [ "$(hostname -s)" = "core" ] || warn "Hostname ist nicht core.at-medical.de – richtiger Server?"

echo "== Ressourcen"
avail=$(df -Pk /var/lib/docker 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
[ "${avail:-0}" -ge 20 ] && ok "frei /var/lib/docker: ${avail} GB" || bad "weniger als 20 GB frei auf /var/lib/docker (${avail:-?} GB)"
home=$(df -Pk /home 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
[ "${home:-0}" -ge 15 ] && ok "frei /home (rootless Docker des Runners): ${home} GB" || bad "weniger als 15 GB frei auf /home (${home:-?} GB)"
mem=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
[ "${mem:-0}" -ge 4000 ] && ok "RAM verfügbar: ${mem} MB" || warn "RAM verfügbar nur ${mem} MB (Forgejo 1 GB + CI-Job bis 3 GB)"
echo "Last: $(cut -d' ' -f1-3 /proc/loadavg) bei $(nproc) CPUs"

echo "== Docker und Traefik"
if docker info >/dev/null 2>&1; then
  ok "Docker $(docker version --format '{{.Server.Version}}')"
  docker network inspect "$NET" >/dev/null 2>&1 && ok "Traefik-Netz '$NET' vorhanden" || bad "Traefik-Netz '$NET' fehlt"
  docker ps --format '{{.Names}}' | grep -qi traefik && ok "Traefik läuft" || warn "kein Traefik-Container gefunden"
  docker ps -a --format '{{.Names}}' | grep -qiE 'forgejo|gitea' && warn "es gibt bereits forgejo/gitea-Container" || ok "kein bestehender Forgejo-Container"
  echo "Laufende Compose-Projekte:"; docker compose ls 2>/dev/null | sed 's/^/  /'
else
  bad "Docker nicht erreichbar"
fi

echo "== Rootless-Docker-Voraussetzungen (Runner)"
for c in newuidmap newgidmap; do command -v $c >/dev/null && ok "$c vorhanden" || warn "$c fehlt (Paket uidmap)"; done
command -v slirp4netns >/dev/null || command -v pasta >/dev/null && ok "Netzwerk für rootless vorhanden" || warn "slirp4netns/pasta fehlt"
id forgejo-runner >/dev/null 2>&1 && warn "Benutzer forgejo-runner existiert bereits" || ok "Benutzer forgejo-runner noch nicht angelegt"
[ -e /usr/local/sbin/pharma-deploy ] && warn "/usr/local/sbin/pharma-deploy existiert bereits" || ok "pharma-deploy noch nicht installiert"
[ -d /srv/pharma-cards ] && warn "/srv/pharma-cards existiert bereits" || ok "/srv/pharma-cards frei"

echo "== DNS und Erreichbarkeit"
getent hosts "$HOST" >/dev/null && ok "DNS $HOST -> $(getent hosts "$HOST" | awk '{print $1}' | head -1)" || bad "DNS-Eintrag für $HOST fehlt"
for u in https://codeberg.org https://code.forgejo.org https://data.forgejo.org https://api.github.com; do
  c=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "$u"); [ "$c" != 000 ] && ok "$u erreichbar ($c)" || bad "$u nicht erreichbar"
done

echo
[ $fail -eq 0 ] && echo "Vorabprüfung bestanden (Warnungen beachten)." || echo "Vorabprüfung NICHT bestanden – erst Fehler beheben."
exit $fail
