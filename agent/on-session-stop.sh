#!/usr/bin/env bash
# Single Stop hook: writes state, sends WhatsApp, then commits — all in sequence.
# No set -e so the git commit always runs even if earlier steps fail.

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
LOG="$REPO/.claude/hook-debug.log"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

log() { echo "[$TIMESTAMP][stop] $*" >> "$LOG" 2>/dev/null || true; }
log "on-session-stop.sh started"

# ── 1. Write state ──────────────────────────────────────────────────────────
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

session_id  = d.get('current_session_id') or ''
start_time  = d.get('current_session_start', '')
summary_txt = d.get('last_session_summary', 'Session ended.')

duration_str = ""
if start_time:
    try:
        start = datetime.datetime.fromisoformat(start_time.replace('Z',''))
        mins  = int((datetime.datetime.utcnow() - start).total_seconds() / 60)
        duration_str = f" ({mins}m)"
    except Exception: pass

try:
    reg   = json.load(open(REGISTRY))
    tasks = [t for p in reg.get('projects',[]) for t in p.get('tasks',[])]
    done  = sum(1 for t in tasks if t.get('status')=='complete')
    total = len(tasks)
    blk   = sum(1 for t in tasks if t.get('status')=='blocked')
    inp   = sum(1 for t in tasks if t.get('status')=='in_progress')
    stats = f"Tasks: {done}/{total} done"
    if blk: stats += f", {blk} blocked"
    if inp:  stats += f", {inp} in progress"
except Exception as e:
    log(f"Registry error: {e}"); stats = ""

if session_id:
    d['last_session_id'] = session_id
    log(f"Set last_session_id={session_id}")

d['last_session_timestamp'] = TIMESTAMP
d['current_session_id']     = None
d['current_session_start']  = None

try:
    with open(STATE, 'w') as f:
        json.dump(d, f, indent=2); f.write('\n')
    log("State written.")
except Exception as e:
    log(f"Write failed: {e}")
PYEOF

log "State write done."

# ── 2. WhatsApp (non-fatal) ──────────────────────────────────────────────────
bash "$REPO/agent/notify-whatsapp.sh" \
  "Session ended. $(python3 -c "import json; d=json.load(open('$STATE')); print(d.get('last_session_summary',''))" 2>/dev/null)" \
  "session_stop" 2>/dev/null || true

# ── 3. Commit everything (runs unconditionally) ──────────────────────────────
cd "$REPO" || { log "cd failed"; exit 0; }

[ -f ".git/index.lock" ] && rm -f ".git/index.lock"

git add \
  .claude/session-state.json \
  .claude/project-registry.json \
  .claude/kickback-registry.json \
  .claude/decision-log.json \
  .claude/whatsapp-config.json \
  .claude/whatsapp-log.json \
  .claude/hook-debug.log 2>/dev/null || true

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
log "Staged: $STAGED"

if [ -n "$STAGED" ]; then
  OUT=$(git commit -m "Auto-save agent state [$TIMESTAMP]" 2>&1); EC=$?
  log "git commit exit=$EC: $OUT"
  if [ $EC -eq 0 ]; then
    OUT=$(git push -u origin claude/chat-session-agent-cfzivv 2>&1); EP=$?
    log "git push exit=$EP: $OUT"
  fi
else
  log "Nothing to commit."
fi

log "on-session-stop.sh done."
