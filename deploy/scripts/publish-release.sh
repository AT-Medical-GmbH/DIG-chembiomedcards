#!/usr/bin/env bash
# Veröffentlicht ein mit scripts/release_cards.py erzeugtes Paket atomar.
# Läuft im CI-Job (Runner-Container), schreibt nur unter $SITES_DIR.
#
#   deploy/scripts/publish-release.sh <staging|production> <paketordner>
#
# Ablage: $SITES_DIR/<kanal>/releases/<UTC-Zeit>-<sha>/ ; $SITES_DIR/<kanal>/current → Symlink
# Es bleiben die letzten $KEEP Stände erhalten (Rollback: rollback-release.sh).
set -euo pipefail

channel="${1:?Kanal fehlt (staging|production)}"
src="${2:?Paketordner fehlt}"
sites="${SITES_DIR:?SITES_DIR fehlt}"
keep="${KEEP:-5}"

case "$channel" in staging|production) ;; *) echo "Unbekannter Kanal: $channel" >&2; exit 2 ;; esac
[ -f "$src/release.json" ] || { echo "Kein Release-Paket: $src/release.json fehlt" >&2; exit 2; }
(cd "$src" && sha256sum -c --quiet SHA256SUMS) || { echo "Prüfsummen stimmen nicht" >&2; exit 2; }

sha="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["git_revision"][:12])' "$src/release.json")"
base="$sites/$channel"
name="$(date -u +%Y%m%dT%H%M%SZ)-$sha"
mkdir -p "$base/releases"
cp -a "$src" "$base/releases/.$name.tmp"
mv "$base/releases/.$name.tmp" "$base/releases/$name"

# atomarer Wechsel: neuen Symlink anlegen und per rename über den alten schieben
ln -sfn "releases/$name" "$base/.current.tmp"
mv -T "$base/.current.tmp" "$base/current"
echo "✓ $channel → releases/$name"

# alte Stände aufräumen (nur innerhalb von releases/, der aktuelle bleibt immer erhalten)
ls -1d "$base"/releases/*/ 2>/dev/null | sort | head -n "-$keep" | while read -r old; do
  [ "$(readlink -f "$old")" = "$(readlink -f "$base/current")" ] && continue
  rm -rf -- "$old"
  echo "  entfernt: $(basename "$old")"
done
