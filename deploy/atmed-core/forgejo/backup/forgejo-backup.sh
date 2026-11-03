#!/usr/bin/env bash
# Konsistente Sicherung von Forgejo (Repositories, Datenbank, Konfiguration) per `forgejo dump`.
# Läuft auf ATMED-core als systemd-Timer (forgejo-backup.timer). Das Zielverzeichnis muss in der
# Restic-Kette von ATINFRA-backup enthalten sein (Runbook Phase 5, Gate G5).
set -euo pipefail

# /srv/atmed/backups/* ist von der Restic-Abholung ausgeschlossen (Phase 0, ATINFRA-backup 03.11.)
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
