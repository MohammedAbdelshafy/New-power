#!/usr/bin/env bash
# Runs when the session ends. Saves state and sends WhatsApp summary.

set -euo pipefail

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Build summary from project state
SUMMARY=$(python3 - <<PYEOF
import json, datetime

STATE = "$STATE"
REGISTRY = "$REGISTRY"
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(STATE))
except Exception:
    d = {}

session_id = d.get('current_session_id', 'unknown')
start_time = d.get('current_session_start', '')
summary = d.get('last_session_summary', 'Session ended.')

# Compute duration
duration_str = ""
if start_time:
    try:
        start = datetime.datetime.fromisoformat(start_time.replace('Z',''))
        end = datetime.datetime.utcnow()
        mins = int((end - start).total_seconds() / 60)
        duration_str = f" ({mins}m)"
    except Exception:
        pass

# Get project completion stats
try:
    reg = json.load(open(REGISTRY))
    tasks = [t for p in reg.get('projects',[]) for t in p.get('tasks',[])]
    done = sum(1 for t in tasks if t.get('status') == 'complete')
    total = len(tasks)
    blocked = sum(1 for t in tasks if t.get('status') == 'blocked')
    in_progress = sum(1 for t in tasks if t.get('status') == 'in_progress')
    stats = f"Tasks: {done}/{total} done"
    if blocked:
        stats += f", {blocked} blocked"
    if in_progress:
        stats += f", {in_progress} in progress"
except Exception:
    stats = ""

# Update state
d['last_session_id'] = session_id
d['last_session_timestamp'] = TIMESTAMP
d['current_session_id'] = None
d['current_session_start'] = None

json.dump(d, open(STATE, 'w'), indent=2)

msg = f"Session ended{duration_str}. {summary}"
if stats:
    msg += f" | {stats}"
print(msg)
PYEOF
)

echo "[Coordinator] $SUMMARY"

bash "$REPO/agent/notify-whatsapp.sh" "$SUMMARY" "session_stop" 2>/dev/null || true
