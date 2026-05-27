#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MAX_SUCCESS_AGE_HOURS="${AIC_ELT_MAX_SUCCESS_AGE_HOURS:-25}"

COMPOSE_FILES=("-f" "docker-compose.yml")
if [[ "${AIC_ELT_USE_PROD_COMPOSE:-0}" == "1" ]]; then
  COMPOSE_FILES+=("-f" "docker-compose.prod.yml")
fi

if [[ ! "$MAX_SUCCESS_AGE_HOURS" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "ELT health check failed: AIC_ELT_MAX_SUCCESS_AGE_HOURS must be numeric." >&2
  exit 2
fi

QUERY="
WITH latest AS (
  SELECT status, started_at, error_message
  FROM elt_run_history
  ORDER BY started_at DESC
  LIMIT 1
),
last_success AS (
  SELECT started_at
  FROM elt_run_history
  WHERE status = 'success'
  ORDER BY started_at DESC
  LIMIT 1
)
SELECT
  COALESCE(latest.status, 'none') AS latest_status,
  COALESCE(latest.started_at::text, '') AS latest_started_at,
  COALESCE(latest.error_message, '') AS latest_error_message,
  COALESCE(last_success.started_at::text, '') AS last_success_started_at,
  COALESCE(ROUND((EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - last_success.started_at)) / 3600.0)::numeric, 2)::text, '') AS success_age_hours
FROM (SELECT 1) seed
LEFT JOIN latest ON TRUE
LEFT JOIN last_success ON TRUE;
"

RESULT="$(
  docker compose "${COMPOSE_FILES[@]}" exec -T warehouse \
    psql -U warehouse_user -d aic_warehouse -At -F '|' -c "$QUERY"
)"

IFS='|' read -r latest_status latest_started_at latest_error_message last_success_started_at success_age_hours <<< "$RESULT"

if [[ "$latest_status" == "none" ]]; then
  echo "ELT health check failed: no rows found in elt_run_history." >&2
  exit 1
fi

if [[ "$latest_status" != "success" ]]; then
  echo "ELT health check failed: latest run status is '$latest_status' at $latest_started_at." >&2
  if [[ -n "$latest_error_message" ]]; then
    echo "Latest error: $latest_error_message" >&2
  fi
  exit 1
fi

if [[ -z "$last_success_started_at" || -z "$success_age_hours" ]]; then
  echo "ELT health check failed: no successful run found in elt_run_history." >&2
  exit 1
fi

if ! awk -v age="$success_age_hours" -v max="$MAX_SUCCESS_AGE_HOURS" 'BEGIN { exit !(age <= max) }'; then
  echo "ELT health check failed: last success is ${success_age_hours}h old, threshold is ${MAX_SUCCESS_AGE_HOURS}h." >&2
  echo "Last success: $last_success_started_at" >&2
  exit 1
fi

echo "ELT health check passed: latest run is success and last success is ${success_age_hours}h old."
echo "Latest run: $latest_started_at"
