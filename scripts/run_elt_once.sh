#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="${AIC_ELT_LOG_DIR:-$ROOT_DIR/logs/elt}"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
LOG_FILE="$LOG_DIR/elt-$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

if [[ ! -f ".env" ]]; then
  echo "Missing .env in $ROOT_DIR" >&2
  exit 1
fi

COMPOSE_FILES=("-f" "docker-compose.yml")
if [[ "${AIC_ELT_USE_PROD_COMPOSE:-0}" == "1" ]]; then
  COMPOSE_FILES+=("-f" "docker-compose.prod.yml")
fi

{
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting AIC ELT"
  echo "Root: $ROOT_DIR"
  echo "Log: $LOG_FILE"
  docker compose "${COMPOSE_FILES[@]}" run --rm elt
  echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] AIC ELT completed successfully"
} 2>&1 | tee "$LOG_FILE"
