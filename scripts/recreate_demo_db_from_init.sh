#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ "${1:-}" != "--yes" ]]; then
  echo "This will drop and recreate the aic_db database from init.sql."
  echo "Type RESET to continue:"
  read -r confirm
  if [[ "$confirm" != "RESET" ]]; then
    echo "Canceled."
    exit 0
  fi
fi

if [[ ! -f ".env" ]]; then
  echo "Missing .env in $ROOT_DIR" >&2
  exit 1
fi

if [[ ! -f "init.sql" ]]; then
  echo "Missing init.sql in $ROOT_DIR" >&2
  exit 1
fi

if ! docker compose ps db >/dev/null 2>&1; then
  echo "Docker Compose db service is not available. Start the stack first." >&2
  exit 1
fi

echo "Recreating aic_db from init.sql"
docker compose exec -T db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' <<'SQL'
DROP DATABASE IF EXISTS aic_db;
CREATE DATABASE aic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL

docker compose exec -T db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" aic_db' < init.sql

if docker compose ps --services --filter "status=running" | grep -qx "backend"; then
  echo "Restarting backend so it reconnects cleanly"
  docker compose restart backend
else
  echo "Backend is not running. Start the full stack with: docker compose up --build -d"
fi

echo "Done. aic_db was recreated from init.sql."
