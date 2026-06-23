#!/usr/bin/env bash
# Runs when the session ends. Saves state, sends WhatsApp summary, commits state files.
# No set -e — must reach the git commit even if earlier steps fail.

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
LOG="$REPO/.claude/hook-debug.log"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

log() { echo "[$TIMESTAMP][stop] $*" >> "$LOG" 2>/dev/null || true; }

log "on-session-stop.sh started (PWD=$PWD)"

# --- Save state and build summary ---
SUMMARY=$(python3 - 2>&1 <<PYEOF || echo "Session ended."
import json, datetime, sys

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
summary = d.get('last_session_summary', 'Session ended.')

log(f"session_id={session_id!r}, start_time={start_time!r}")

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
    done = sum(1 for t in tasks if t.get('status') == 'complete')
    total = len(tasks)
    blocked = sum(1 for t in tasks if t.get('status') == 'blocked')
    in_prog = sum(1 for t in tasks if t.get('status') == 'in_progress')
    stats = f"Tasks: {done}/{total} done"
    if blocked: stats += f", {blocked} blocked"
    if in_prog: stats += f", {in_prog} in progress"
except Exception as e:
    log(f"Registry read error: {e}")
    stats = ""

# Update state
if session_id:
    d['last_session_id'] = session_id
    log(f"Set last_session_id={session_id}")
else:
    log("WARNING: session_id is empty, not updating last_session_id")

d['last_session_timestamp'] = TIMESTAMP
d['current_session_id'] = None
d['current_session_start'] = None

try:
    with open(STATE, 'w') as f:
        json.dump(d, f, indent=2)
        f.write('\n')
    log("State file written.")
except Exception as e:
    log(f"Failed to write state: {e}")

msg = f"Session ended{duration_str}. {summary}"
if stats:
    msg += f" | {stats}"
log(f"Summary: {msg}")
print(msg)
PYEOF
)

log "Python block done. SUMMARY=$SUMMARY"
echo "[Coordinator] $SUMMARY"

# --- WhatsApp notification (non-fatal) ---
bash "$REPO/agent/notify-whatsapp.sh" "$SUMMARY" "session_stop" 2>/dev/null || true
log "WhatsApp notification attempted."

# --- Auto-commit state files (always runs) ---
cd "$REPO" || { log "FAIL: cd $REPO"; exit 0; }

# Remove any stale git lock
[ -f ".git/index.lock" ] && rm -f ".git/index.lock" && log "Removed stale index.lock"

git add \
  .claude/session-state.json \
  .claude/project-registry.json \
  .claude/kickback-registry.json \
  .claude/decision-log.json \
  .claude/whatsapp-config.json \
  .claude/whatsapp-log.json \
  .claude/hook-debug.log 2>/dev/null || true

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
log "Staged files: $STAGED"

if [ -n "$STAGED" ]; then
  COMMIT_OUT=$(git commit -m "Auto-save agent state [$TIMESTAMP]" 2>&1)
  COMMIT_EXIT=$?
  log "git commit exit=$COMMIT_EXIT: $COMMIT_OUT"

  PUSH_OUT=$(git push -u origin claude/chat-session-agent-cfzivv 2>&1)
  PUSH_EXIT=$?
  log "git push exit=$PUSH_EXIT: $PUSH_OUT"
  echo "[Coordinator] State committed and pushed."
else
  log "Nothing staged to commit."
  echo "[Coordinator] No state changes to commit."
fi

log "on-session-stop.sh finished."
