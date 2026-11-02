#!/bin/sh
set -eu
DB="${DATABASE_PATH:-./data/jobs.db}"
DEST="${BACKUP_DIR:-./data/backups}"
mkdir -p "$DEST"
STAMP=$(date +%Y%m%d_%H%M%S)
sqlite3 "$DB" ".backup '$DEST/jobs_$STAMP.db'"
ls -1t "$DEST"/jobs_*.db | tail -n +8 | xargs -r rm --
echo "Backup: $DEST/jobs_$STAMP.db"
