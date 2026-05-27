#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CHECK_SCRIPT="$ROOT_DIR/scripts/check_elt_health.sh"

read_env_value() {
  local key="$1"
  local file="$2"

  if [[ ! -f "$file" ]]; then
    return 0
  fi

  sed -n "s/^[[:space:]]*${key}[[:space:]]*=[[:space:]]*//p" "$file" \
    | sed -e 's/[[:space:]]*#.*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//" -e 's/\r$//' \
    | tail -n 1
}

WEBHOOK_URL="${DISCORD_WEBHOOK_URL:-}"
if [[ -z "$WEBHOOK_URL" ]]; then
  WEBHOOK_URL="$(read_env_value "DISCORD_WEBHOOK_URL" "$ROOT_DIR/.env")"
fi

if CHECK_OUTPUT="$("$CHECK_SCRIPT" 2>&1)"; then
  echo "$CHECK_OUTPUT"
  exit 0
else
  CHECK_STATUS=$?
fi

echo "$CHECK_OUTPUT" >&2

if [[ -z "$WEBHOOK_URL" ]]; then
  echo "Discord notification skipped: DISCORD_WEBHOOK_URL is not set." >&2
  exit "$CHECK_STATUS"
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Discord notification skipped: curl is not available." >&2
  exit "$CHECK_STATUS"
fi

HOSTNAME_VALUE="$(hostname 2>/dev/null || echo unknown-host)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
TRUNCATED_OUTPUT="${CHECK_OUTPUT:0:1200}"
MESSAGE="AIC ELT health check failed on ${HOSTNAME_VALUE} at ${TIMESTAMP}.

Exit code: ${CHECK_STATUS}

\`\`\`
${TRUNCATED_OUTPUT}
\`\`\`"

if curl -fsS -X POST -F "content=$MESSAGE" "$WEBHOOK_URL" >/dev/null; then
  echo "Discord notification sent for ELT health check failure." >&2
else
  echo "Discord notification failed to send." >&2
fi

exit "$CHECK_STATUS"
