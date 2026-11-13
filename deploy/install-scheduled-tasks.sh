#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/deploy/production.env"
BACKUP_SCRIPT="$ROOT_DIR/deploy/backup-postgres.sh"
LOG_DIR="/var/log/jupython"
MARKER="# JUPYTHON_MANAGED_TASKS"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE; configure production settings first." >&2
  exit 2
fi
if [[ "$EUID" -ne 0 ]]; then
  echo "Run this installer with sudo so cron, logs, and backup permissions are set safely." >&2
  exit 2
fi
command -v crontab >/dev/null || { echo "Install cron before continuing." >&2; exit 2; }
mkdir -p "$LOG_DIR" /var/backups/jupython
install -m 644 "$ROOT_DIR/deploy/jupython.logrotate" /etc/logrotate.d/jupython
chmod 700 /var/backups/jupython

TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT
(crontab -l 2>/dev/null || true) | grep -v "$MARKER" > "$TMP_FILE" || true
printf '15 3 * * * /bin/bash %s >> %s/maintenance.log 2>&1 %s\n' \
  "$ROOT_DIR/deploy/run-maintenance-report.sh" "$LOG_DIR" "$MARKER" >> "$TMP_FILE"
printf '45 3 * * * /bin/bash %s >> %s/backup.log 2>&1 %s\n' \
  "$BACKUP_SCRIPT" "$LOG_DIR" "$MARKER" >> "$TMP_FILE"
crontab "$TMP_FILE"
echo "Installed daily maintenance report and database/media backup tasks (server local time)."
