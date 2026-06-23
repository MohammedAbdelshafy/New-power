#!/usr/bin/env bash
# Runs when the session ends. Saves state so the next session can resume instantly.

set -euo pipefail

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

python3 -c "
import json, datetime, sys

STATE = '$STATE'
TIMESTAMP = '$TIMESTAMP'

try:
    d = json.load(open(STATE))
except Exception:
    d = {}

session_id = d.get('current_session_id', 'unknown')

d['last_session_id'] = session_id
d['last_session_timestamp'] = TIMESTAMP
d['current_session_id'] = None
d['current_session_start'] = None

# Preserve next_steps if not already updated by the agent during this session
if 'next_steps' not in d:
    d['next_steps'] = []

json.dump(d, open(STATE, 'w'), indent=2)
print(f'[Coordinator] Session {session_id} state saved at {TIMESTAMP}')
" 2>/dev/null || echo "[Coordinator] Could not save session state"
