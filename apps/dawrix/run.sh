#!/usr/bin/env bash
# Dawrix — run the app locally. Zero dependencies (Python stdlib + SQLite).
set -euo pipefail
cd "$(dirname "$0")"
export DAWRIX_PORT="${DAWRIX_PORT:-8080}"
echo "Starting Dawrix on http://127.0.0.1:${DAWRIX_PORT}"
exec python3 -m dawrix.server
