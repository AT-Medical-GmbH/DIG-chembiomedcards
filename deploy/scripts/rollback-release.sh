#!/usr/bin/env bash
# Schaltet einen Kanal auf den vorherigen (oder einen benannten) Stand zurück.
# Auf ATMED-core im Checkout /srv/atmed/stacks/chembiomed-cards/src ausführen:
#   SITES_DIR=/srv/atmed/stacks/chembiomed-cards/sites deploy/scripts/rollback-release.sh production          # vorheriger Stand
#   SITES_DIR=/srv/atmed/stacks/chembiomed-cards/sites deploy/scripts/rollback-release.sh production <name>   # bestimmter Stand
set -euo pipefail

channel="${1:?Kanal fehlt (staging|production)}"
target="${2:-}"
base="${SITES_DIR:?SITES_DIR fehlt}/$channel"
current="$(basename "$(readlink "$base/current")")"

mapfile -t all < <(ls -1 "$base/releases" | sort)
echo "Vorhandene Stände ($channel), aktuell: $current"
printf '  %s\n' "${all[@]}"

if [ -z "$target" ]; then
  for i in "${!all[@]}"; do [ "${all[$i]}" = "$current" ] && idx=$i; done
  [ "${idx:-0}" -gt 0 ] || { echo "Kein älterer Stand vorhanden." >&2; exit 1; }
  target="${all[$((idx-1))]}"
fi
[ -d "$base/releases/$target" ] || { echo "Stand nicht gefunden: $target" >&2; exit 1; }

ln -sfn "releases/$target" "$base/.current.tmp"
mv -T "$base/.current.tmp" "$base/current"
echo "✓ $channel zurückgeschaltet: $current → $target"
