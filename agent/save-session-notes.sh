#!/usr/bin/env bash
# Usage: ./agent/save-session-notes.sh "Summary of what was done" "next step 1" "next step 2"
# Call this at the end of any significant work to preserve context for the next session.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="$REPO/.claude/session-state.json"

SUMMARY="${1:-}"
shift || true
NEXT_STEPS=("$@")

if [ -z "$SUMMARY" ]; then
  echo "Usage: $0 \"summary\" \"next step 1\" \"next step 2\" ..."
  exit 1
fi

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

python3 - <<PYEOF
import json

STATE = "$STATE"
SUMMARY = """$SUMMARY"""
NEXT_STEPS = [s for s in """${NEXT_STEPS[*]:-}""".split('\n') if s.strip()] if """${NEXT_STEPS[*]:-}""" else []
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(STATE))
except Exception:
    d = {}

d["last_session_summary"] = SUMMARY
d["next_steps"] = NEXT_STEPS
d["last_updated"] = TIMESTAMP

json.dump(d, open(STATE, "w"), indent=2)
print(f"Session notes saved: {SUMMARY}")
if NEXT_STEPS:
    print("Next steps:")
    for s in NEXT_STEPS:
        print(f"  - {s}")
PYEOF
