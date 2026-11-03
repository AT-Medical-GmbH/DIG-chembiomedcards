#!/usr/bin/env bash
# Pharma Cards – Staging-Vorabprüfung. NUR LESEND: ändert nichts am Host.
# Aufruf auf dem Zielhost aus dem Repo-Checkout:  bash online-platform/ops/staging/preflight.sh <host> [traefik-netz]
# Beispiel:  bash online-platform/ops/staging/preflight.sh pharma-staging.at-medical.de proxy
# Optional:  AUTH_HOST=auth.at-medical.de AUTH_SLUG=pharma-cards-staging MOODLE_HOST=moodle.at-medical.de
set -u
HOST="${1:?Hostname angeben, z. B. pharma-staging.at-medical.de}"
NET="${2:-proxy}"
AUTH_HOST="${AUTH_HOST:-auth.at-medical.de}"
AUTH_SLUG="${AUTH_SLUG:-pharma-cards-staging}"   # Authentik-Provider
MOODLE_HOST="${MOODLE_HOST:-}"
fail=0
ok()   { printf 'OK    %s\n' "$*"; }
warn() { printf 'WARN  %s\n' "$*"; }
bad()  { printf 'FEHL  %s\n' "$*"; fail=1; }

echo "== Host"; hostname; uname -sr
echo "== Werkzeuge"
command -v docker >/dev/null && ok "docker $(docker version --format '{{.Server.Version}}' 2>/dev/null)" || bad "docker fehlt"
docker compose version >/dev/null 2>&1 && ok "$(docker compose version --short 2>/dev/null | sed 's/^/compose /')" || bad "docker compose fehlt"
command -v openssl >/dev/null && ok "openssl vorhanden" || warn "openssl fehlt (für LTI-Schlüssel)"

echo "== Ressourcen"
avail=$(df -Pk /var/lib/docker 2>/dev/null | awk 'NR==2{print int($4/1024/1024)}')
[ "${avail:-0}" -ge 10 ] && ok "freier Platz /var/lib/docker: ${avail} GB" || bad "weniger als 10 GB frei auf /var/lib/docker (${avail:-?} GB)"
mem=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)
[ "${mem:-0}" -ge 1500 ] && ok "RAM verfügbar: ${mem} MB" || warn "wenig RAM verfügbar: ${mem} MB (PDF-Downloads starten Chromium)"

echo "== Docker-Umgebung"
if ! docker info >/dev/null 2>&1; then
  bad "Docker-Daemon nicht erreichbar (läuft er? Rechte für /var/run/docker.sock?)"
else
docker network inspect "$NET" >/dev/null 2>&1 && ok "Traefik-Netz '$NET' vorhanden" || bad "Traefik-Netz '$NET' fehlt – Netzname mit ATMED-traefik abgleichen"
if docker ps --format '{{.Names}}' | grep -qi traefik; then ok "Traefik-Container läuft"; else warn "kein laufender Container mit 'traefik' im Namen gefunden"; fi
if docker ps -a --format '{{.Names}}' | grep -q '^pharma-cards'; then warn "es existieren bereits pharma-cards-Container (Update statt Neuinstallation?)"; else ok "keine bestehenden pharma-cards-Container"; fi
fi

echo "== DNS und Erreichbarkeit"
getent hosts "$HOST" >/dev/null && ok "DNS $HOST -> $(getent hosts "$HOST" | awk '{print $1}' | head -1)" || bad "DNS-Eintrag für $HOST fehlt"
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "https://$AUTH_HOST/application/o/$AUTH_SLUG/.well-known/openid-configuration")
[ "$code" = 200 ] && ok "Authentik-Provider $AUTH_SLUG erreichbar" || warn "Authentik-Discovery liefert $code (Provider $AUTH_SLUG angelegt?)"
if [ -n "$MOODLE_HOST" ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "https://$MOODLE_HOST/mod/lti/certs.php")
  [ "$code" = 200 ] && ok "Moodle-JWKS erreichbar" || warn "Moodle-JWKS liefert $code"
fi

echo "== Repository-Checkout"
[ -f online-platform/docker-compose.yml ] && ok "im Repo-Wurzelverzeichnis" || bad "bitte aus dem Repo-Wurzelverzeichnis aufrufen"
[ -f online-platform/.env ] && { ok ".env vorhanden"; perm=$(stat -c %a online-platform/.env); [ "$perm" -le 640 ] && ok ".env Rechte $perm" || warn ".env Rechte $perm (empfohlen 600)"; } || warn ".env fehlt noch (aus ops/staging/staging.env.example anlegen)"
git status --porcelain 2>/dev/null | grep -q . && warn "Checkout hat lokale Änderungen" || ok "Checkout sauber ($(git rev-parse --short HEAD 2>/dev/null))"

echo
[ $fail -eq 0 ] && echo "Vorabprüfung bestanden (Warnungen beachten)." || echo "Vorabprüfung NICHT bestanden – erst Fehler beheben."
exit $fail
