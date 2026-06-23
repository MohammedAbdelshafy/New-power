#!/usr/bin/env bash
# Runs when the session ends. Writes state files and sends WhatsApp summary.
# Does NOT commit — auto-commit-state.sh on the next SessionStart handles that,
# avoiding a git ref CAS race with commits made during the session.

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
LOG="$REPO/.claude/hook-debug.log"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

log() { echo "[$TIMESTAMP][stop] $*" >> "$LOG" 2>/dev/null || true; }

log "on-session-stop.sh started (PWD=$PWD)"

python3 - 2>&1 <<PYEOF | tee -a "$LOG" || true
import json, datetime

STATE = "$STATE"
REGISTRY = "$REGISTRY"
TIMESTAMP = "$TIMESTAMP"
LOG = "$LOG"

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f"[$TIMESTAMP][stop-py] {msg}\n")

try:
    d = json.load(open(STATE))
    log(f"Loaded state. current_session_id={d.get('current_session_id')}")
except Exception as e:
    log(f"Failed to load state: {e}")
    d = {}

session_id = d.get('current_session_id') or ''
start_time = d.get('current_session_start', '')
summary_text = d.get('last_session_summary', 'Session ended.')

duration_str = ""
if start_time:
    try:
        start = datetime.datetime.fromisoformat(start_time.replace('Z', ''))
        end = datetime.datetime.utcnow()
        mins = int((end - start).total_seconds() / 60)
        duration_str = f" ({mins}m)"
    except Exception as e:
        log(f"Duration calc error: {e}")

try:
    reg = json.load(open(REGISTRY))
    tasks = [t for p in reg.get('projects', []) for t in p.get('tasks', [])]
    done  = sum(1 for t in tasks if t.get('status') == 'complete')
    total = len(tasks)
    blocked = sum(1 for t in tasks if t.get('status') == 'blocked')
    in_prog = sum(1 for t in tasks if t.get('status') == 'in_progress')
    stats = f"Tasks: {done}/{total} done"
    if blocked: stats += f", {blocked} blocked"
    if in_prog: stats += f", {in_prog} in progress"
except Exception as e:
    log(f"Registry read error: {e}")
    stats = ""

if session_id:
    d['last_session_id'] = session_id
    log(f"Set last_session_id={session_id}")
else:
    log("WARNING: session_id empty, skipping last_session_id update")

d['last_session_timestamp'] = TIMESTAMP
d['current_session_id'] = None
d['current_session_start'] = None

try:
    with open(STATE, 'w') as f:
        json.dump(d, f, indent=2)
        f.write('\n')
    log("State file written successfully.")
except Exception as e:
    log(f"Failed to write state: {e}")

msg = f"Session ended{duration_str}. {summary_text}"
if stats:
    msg += f" | {stats}"
log(f"Summary: {msg}")
print(msg)
PYEOF

SUMMARY=$(python3 -c "
import json
d = json.load(open('$STATE'))
print(d.get('last_session_summary','Session ended.'))
" 2>/dev/null || echo "Session ended.")

log "Sending WhatsApp notification..."
bash "$REPO/agent/notify-whatsapp.sh" \
  "Session ended. $SUMMARY" "session_stop" 2>/dev/null || true

log "on-session-stop.sh finished. State written; next SessionStart will commit."
echo "[Coordinator] Session state saved. Will be committed on next session start."
