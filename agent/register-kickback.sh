#!/usr/bin/env bash
# Usage: ./agent/register-kickback.sh <name> <endpoint-url> [health-check-url]
# Registers a kickback (webhook/callback/commission endpoint) so the agent monitors it.

set -euo pipefail

REPO="/home/user/New-power"
KICKBACKS="$REPO/.claude/kickback-registry.json"

NAME="${1:-}"
ENDPOINT="${2:-}"
HEALTH_URL="${3:-$ENDPOINT}"

if [ -z "$NAME" ] || [ -z "$ENDPOINT" ]; then
  echo "Usage: $0 <name> <endpoint-url> [health-check-url]"
  exit 1
fi

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

python3 - <<PYEOF
import json

KICKBACKS = "$KICKBACKS"
NAME = """$NAME"""
ENDPOINT = """$ENDPOINT"""
HEALTH_URL = """$HEALTH_URL"""
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(KICKBACKS))
except Exception:
    d = {"kickbacks": [], "last_health_check": None}

kickbacks = d.get("kickbacks", [])
kb = next((k for k in kickbacks if k["name"] == NAME), None)
if kb is None:
    kb = {
        "name": NAME,
        "endpoint_url": ENDPOINT,
        "health_check_url": HEALTH_URL,
        "status": "registered",
        "registered_at": TIMESTAMP,
        "last_checked": None,
        "last_status_code": None
    }
    kickbacks.append(kb)
    print(f"Registered kickback: {NAME} -> {ENDPOINT}")
else:
    kb["endpoint_url"] = ENDPOINT
    kb["health_check_url"] = HEALTH_URL
    kb["updated"] = TIMESTAMP
    print(f"Updated kickback: {NAME} -> {ENDPOINT}")

d["kickbacks"] = kickbacks
json.dump(d, open(KICKBACKS, "w"), indent=2)
PYEOF
