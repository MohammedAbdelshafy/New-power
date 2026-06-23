#!/usr/bin/env bash
# Runs when the session ends. Saves state, sends WhatsApp summary, and auto-commits state files.

set -euo pipefail

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Build summary and save state
SUMMARY=$(python3 - <<PYEOF
import json, datetime

STATE = "$STATE"
REGISTRY = "$REGISTRY"
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(STATE))
except Exception:
    d = {}

session_id = d.get('current_session_id') or 'unknown'
start_time = d.get('current_session_start', '')
summary = d.get('last_session_summary', 'Session ended.')

duration_str = ""
if start_time:
    try:
        start = datetime.datetime.fromisoformat(start_time.replace('Z',''))
        end = datetime.datetime.utcnow()
        mins = int((end - start).total_seconds() / 60)
        duration_str = f" ({mins}m)"
    except Exception:
        pass

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

# Only update last_session_id if we have a real session (not null)
if session_id and session_id != 'unknown':
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

# Auto-commit any changes to state files so the stop-hook git check passes
cd "$REPO"
CHANGED=$(git status --porcelain .claude/ 2>/dev/null || true)
if [ -n "$CHANGED" ]; then
  git add .claude/session-state.json .claude/project-registry.json .claude/kickback-registry.json .claude/decision-log.json .claude/whatsapp-log.json 2>/dev/null || true
  git add .claude/whatsapp-config.json 2>/dev/null || true
  STAGED=$(git diff --cached --name-only 2>/dev/null || true)
  if [ -n "$STAGED" ]; then
    git commit -m "Auto-save agent state [$(date -u '+%Y-%m-%dT%H:%M:%SZ')]" 2>/dev/null && \
    git push -u origin claude/chat-session-agent-cfzivv 2>/dev/null || true
    echo "[Coordinator] State committed and pushed."
  fi
fi
