#!/usr/bin/env bash
# Runs when the session ends. Saves state, sends WhatsApp summary, and auto-commits state files.
# No set -e here — we must reach the git commit even if earlier steps fail.

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# --- Save state and build summary ---
SUMMARY=$(python3 - 2>/dev/null <<PYEOF || echo "Session ended."
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
        start = datetime.datetime.fromisoformat(start_time.replace('Z', ''))
        end = datetime.datetime.utcnow()
        mins = int((end - start).total_seconds() / 60)
        duration_str = f" ({mins}m)"
    except Exception:
        pass

try:
    reg = json.load(open(REGISTRY))
    tasks = [t for p in reg.get('projects', []) for t in p.get('tasks', [])]
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

if session_id and session_id != 'unknown':
    d['last_session_id'] = session_id
d['last_session_timestamp'] = TIMESTAMP
d['current_session_id'] = None
d['current_session_start'] = None

with open(STATE, 'w') as f:
    json.dump(d, f, indent=2)
    f.write('\n')

msg = f"Session ended{duration_str}. {summary}"
if stats:
    msg += f" | {stats}"
print(msg)
PYEOF
)

echo "[Coordinator] $SUMMARY"

# --- WhatsApp notification (non-fatal) ---
bash "$REPO/agent/notify-whatsapp.sh" "$SUMMARY" "session_stop" 2>/dev/null || true

# --- Auto-commit state files (always runs) ---
cd "$REPO" || exit 0

git add \
  .claude/session-state.json \
  .claude/project-registry.json \
  .claude/kickback-registry.json \
  .claude/decision-log.json \
  .claude/whatsapp-config.json \
  .claude/whatsapp-log.json 2>/dev/null || true

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
if [ -n "$STAGED" ]; then
  git commit -m "Auto-save agent state [$TIMESTAMP]" --quiet 2>/dev/null || true
  git push -u origin claude/chat-session-agent-cfzivv --quiet 2>/dev/null || true
  echo "[Coordinator] State committed and pushed."
else
  echo "[Coordinator] No state changes to commit."
fi
