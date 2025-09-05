#!/usr/bin/env bash
set -euo pipefail

# Set default search_path for a role in a database
# Usage:
#   DB_USER=ai_user DB_NAME=ai_agency DB_SCHEMA=my_schema ./scripts/db_set_search_path.sh

if [[ -z "${DB_USER:-}" || -z "${DB_NAME:-}" || -z "${DB_SCHEMA:-}" ]]; then
  echo "Usage: DB_USER=<user> DB_NAME=<db> DB_SCHEMA=<schema> $0"
  exit 1
fi

PSQL_OPTS=()
if [[ -n "${PGHOST:-}" ]]; then PSQL_OPTS+=("-h" "$PGHOST"); fi
if [[ -n "${PGPORT:-}" ]]; then PSQL_OPTS+=("-p" "$PGPORT"); fi
if [[ -n "${PGUSER:-}" ]]; then PSQL_OPTS+=("-U" "$PGUSER"); fi

echo "🔧 Setting default search_path for role '${DB_USER}' in database '${DB_NAME}' to '${DB_SCHEMA}, public'"
psql "${PSQL_OPTS[@]}" -d "$DB_NAME" -v ON_ERROR_STOP=1 -c \
  "ALTER ROLE \"${DB_USER}\" IN DATABASE \"${DB_NAME}\" SET search_path = ${DB_SCHEMA}, public;"

echo "✅ Done"

