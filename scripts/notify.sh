#!/usr/bin/env bash
# notify.sh - send a one-line update to Telegram and/or Discord.
#
# Use it from Antigravity, opencode, or any local script/agent to push status
# updates to the same channels the GitHub Action uses.
#
# Reads channel config from the environment (or a .env you source first):
#   TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   -> Telegram
#   DISCORD_WEBHOOK_URL                    -> Discord
# A channel is used only if its variables are set. Missing ones are skipped.
#
# Usage:
#   ./scripts/notify.sh "Build finished ✅"
#   echo "done" | ./scripts/notify.sh          # message from stdin
#   TELEGRAM_CHAT_ID=123 ./scripts/notify.sh "hi"

set -euo pipefail

MSG="${1:-}"
if [ -z "$MSG" ] && [ ! -t 0 ]; then
  MSG="$(cat)"
fi
if [ -z "$MSG" ]; then
  echo "usage: notify.sh \"message\"  (or pipe text via stdin)" >&2
  exit 1
fi

sent_any=0

# --- Telegram ---
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  curl -sS --fail-with-body \
    "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
    --data-urlencode "text=${MSG}" \
    --data-urlencode "disable_web_page_preview=true" >/dev/null \
    && { echo "telegram: sent"; sent_any=1; } \
    || echo "telegram: failed" >&2
fi

# --- Discord ---
if [ -n "${DISCORD_WEBHOOK_URL:-}" ]; then
  if command -v jq >/dev/null 2>&1; then
    payload="$(jq -nc --arg c "$MSG" '{content:$c}')"
  else
    # Minimal escaping fallback if jq is unavailable.
    esc="${MSG//\\/\\\\}"; esc="${esc//\"/\\\"}"; esc="${esc//$'\n'/\\n}"
    payload="{\"content\":\"${esc}\"}"
  fi
  curl -sS --fail-with-body -H "Content-Type: application/json" \
    -d "$payload" "$DISCORD_WEBHOOK_URL" >/dev/null \
    && { echo "discord: sent"; sent_any=1; } \
    || echo "discord: failed" >&2
fi

if [ "$sent_any" -eq 0 ]; then
  echo "notify.sh: no channel configured (set TELEGRAM_* or DISCORD_WEBHOOK_URL)" >&2
  exit 1
fi
