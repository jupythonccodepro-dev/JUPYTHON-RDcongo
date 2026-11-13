#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/deploy/production.env"
COMPOSE_FILE="$ROOT_DIR/deploy/docker-compose.yml"
BACKUP_DIR="/var/backups/jupython"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE; copy production.example.env and configure it first." >&2
  exit 2
fi
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DB_OUTPUT="$BACKUP_DIR/jupython-postgres-$STAMP.sql.gz"
MEDIA_OUTPUT="$BACKUP_DIR/jupython-media-$STAMP.tar.gz"
DB_TEMP="$DB_OUTPUT.partial"
MEDIA_TEMP="$MEDIA_OUTPUT.partial"
trap 'rm -f "$DB_TEMP" "$MEDIA_TEMP"' EXIT

cd "$ROOT_DIR"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip -9 > "$DB_TEMP"
gzip -t "$DB_TEMP"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T app \
  tar -C /app -czf - media > "$MEDIA_TEMP"
tar -tzf "$MEDIA_TEMP" >/dev/null
mv "$DB_TEMP" "$DB_OUTPUT"
mv "$MEDIA_TEMP" "$MEDIA_OUTPUT"
chmod 600 "$DB_OUTPUT" "$MEDIA_OUTPUT"
printf 'Created database and media backups in %s\n' "$BACKUP_DIR"

BACKUP_CONFIG="$ROOT_DIR/deploy/backup.env"
if [[ -f "$BACKUP_CONFIG" ]]; then
  # This config contains only the OCI bucket name and region, never credentials.
  # shellcheck disable=SC1090
  source "$BACKUP_CONFIG"
fi
if [[ -n "${OCI_BUCKET_NAME:-}" ]]; then
  : "${OCI_REGION:?Set OCI_REGION in deploy/backup.env}"
  command -v oci >/dev/null || { echo "Install OCI CLI to upload off-site backups." >&2; exit 2; }
  for file in "$DB_OUTPUT" "$MEDIA_OUTPUT"; do
    oci os object put \
      --auth instance_principal \
      --region "$OCI_REGION" \
      --bucket-name "$OCI_BUCKET_NAME" \
      --name "$(basename "$file")" \
      --file "$file" \
      --force
  done
  echo "Uploaded both backups to OCI Object Storage."
fi

find "$BACKUP_DIR" -maxdepth 1 -type f \
  \( -name 'jupython-postgres-*.sql.gz' -o -name 'jupython-media-*.tar.gz' \) \
  -mtime +30 -delete
