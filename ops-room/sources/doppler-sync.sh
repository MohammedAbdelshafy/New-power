#!/usr/bin/env bash
# doppler-sync.sh — Pull secrets from Doppler into a .env file or export them.
# Usage: ./doppler-sync.sh [--project <name>] [--config <dev|stg|prd>] [--export | --env-file <path>]
#
# Requires: doppler CLI (https://docs.doppler.com/docs/cli)

set -euo pipefail

PROJECT=""
CONFIG="dev"
MODE="export"
ENV_FILE=".env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)  PROJECT="$2"; shift 2 ;;
    --config)   CONFIG="$2"; shift 2 ;;
    --export)   MODE="export"; shift ;;
    --env-file) MODE="file"; ENV_FILE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if ! command -v doppler &>/dev/null; then
  echo "[doppler] Doppler CLI not installed."
  echo "  Install: curl -Ls --tlsv1.2 --proto \"=https\" -o /tmp/install.sh https://cli.doppler.com/install.sh && sh /tmp/install.sh"
  exit 1
fi

PROJECT_FLAG=""
if [[ -n "$PROJECT" ]]; then
  PROJECT_FLAG="--project $PROJECT"
fi

echo "[doppler] Syncing secrets (config=$CONFIG)..."

if [[ "$MODE" == "export" ]]; then
  doppler secrets download --no-file --format env $PROJECT_FLAG --config "$CONFIG" 2>/dev/null \
    | while IFS='=' read -r key value; do
        echo "export $key=\"$value\""
      done
  echo "[doppler] Secrets exported to current shell. Source this script to apply."
else
  doppler secrets download --no-file --format env $PROJECT_FLAG --config "$CONFIG" > "$ENV_FILE"
  echo "[doppler] Secrets written to: $ENV_FILE"
  echo "  IMPORTANT: Add $ENV_FILE to .gitignore — never commit secrets."
fi
