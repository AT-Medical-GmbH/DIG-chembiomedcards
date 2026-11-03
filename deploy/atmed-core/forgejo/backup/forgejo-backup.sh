#!/usr/bin/env bash
# Konsistente Sicherung von Forgejo (Repositories, Datenbank, Konfiguration) per `forgejo dump`.
# Läuft auf ATMED-core als systemd-Timer (forgejo-backup.timer). Ziel liegt bewusst NICHT unter
# /srv/atmed/backups: Diesen Pfad schließt die Restic-Abholung aus (Phase 0, 03.11.2026).
set -euo pipefail

dest="${FORGEJO_BACKUP_DIR:-/srv/atmed/stacks/forgejo/sicherung}"
keep_days="${FORGEJO_BACKUP_KEEP_DAYS:-14}"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
umask 077
mkdir -p "$dest"

tmp="$dest/.forgejo-dump-$ts.tar.gz.part"
docker exec -u git -w /tmp forgejo forgejo dump --type tar.gz --file - --quiet > "$tmp"
tar -tzf "$tmp" data/gitea.db >/dev/null   # Datenbank muss enthalten sein
mv "$tmp" "$dest/forgejo-dump-$ts.tar.gz"
(cd "$dest" && sha256sum "forgejo-dump-$ts.tar.gz" > "forgejo-dump-$ts.tar.gz.sha256")

find "$dest" -maxdepth 1 -name 'forgejo-dump-*' -mtime "+$keep_days" -delete
echo "forgejo-backup: $dest/forgejo-dump-$ts.tar.gz ($(du -h "$dest/forgejo-dump-$ts.tar.gz" | cut -f1))"
