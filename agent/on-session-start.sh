#!/usr/bin/env bash
# Runs at the start of every Claude Code session.
# Loads state and prints a resume briefing so the agent picks up mid-task.

set -euo pipefail

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
KICKBACKS="$REPO/.claude/kickback-registry.json"

SESSION_ID="session-$(date +%Y%m%d-%H%M%S)-$$"
echo "=== NEW-POWER COORDINATOR AGENT STARTING ==="
echo "Session ID: $SESSION_ID"
echo "Time: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

# --- Show last session summary ---
if [ -f "$STATE" ]; then
  LAST_SUMMARY=$(python3 -c "import json,sys; d=json.load(open('$STATE')); print(d.get('last_session_summary','(none)'))" 2>/dev/null || echo "(could not read)")
  LAST_ID=$(python3 -c "import json,sys; d=json.load(open('$STATE')); print(d.get('last_session_id') or '(first session)')" 2>/dev/null || echo "unknown")
  echo "--- Resuming from: $LAST_ID ---"
  echo "Last summary: $LAST_SUMMARY"
  echo ""

  NEXT_STEPS=$(python3 -c "
import json
d = json.load(open('$STATE'))
steps = d.get('next_steps', [])
for i, s in enumerate(steps, 1):
    print(f'  {i}. {s}')
" 2>/dev/null || echo "  (none)")
  echo "Next steps carried over:"
  echo "$NEXT_STEPS"
  echo ""
fi

# --- Show project status ---
if [ -f "$REGISTRY" ]; then
  echo "--- Project Status ---"
  python3 -c "
import json
d = json.load(open('$REGISTRY'))
projects = d.get('projects', [])
if not projects:
    print('  No projects registered yet.')
else:
    for p in projects:
        name = p.get('name', 'Unnamed')
        status = p.get('status', 'unknown')
        blocked = ' [BLOCKED]' if status == 'blocked' else ''
        print(f'  [{status.upper()}]{blocked} {name}')
        for t in p.get('tasks', []):
            ts = t.get('status', '?')
            tn = t.get('name', '?')
            print(f'      - [{ts}] {tn}')
" 2>/dev/null || echo "  (could not read registry)"
  echo ""
fi

# --- Check kickbacks ---
if [ -f "$KICKBACKS" ]; then
  echo "--- Kickback / Webhook Health ---"
  python3 -c "
import json, urllib.request, urllib.error
d = json.load(open('$KICKBACKS'))
kickbacks = d.get('kickbacks', [])
if not kickbacks:
    print('  No kickbacks registered yet.')
else:
    for kb in kickbacks:
        name = kb.get('name', '?')
        url = kb.get('health_check_url', '')
        if url:
            try:
                req = urllib.request.urlopen(url, timeout=5)
                status = req.status
                print(f'  [OK {status}] {name} -> {url}')
            except Exception as e:
                print(f'  [FAIL] {name} -> {url} : {e}')
        else:
            print(f'  [NO HEALTH CHECK] {name}')
" 2>/dev/null || echo "  (kickback check skipped)"
  echo ""
fi

# --- Save session start to state ---
python3 -c "
import json, datetime
STATE = '$STATE'
SESSION_ID = '$SESSION_ID'
try:
    d = json.load(open(STATE))
except:
    d = {}
linked = d.get('linked_sessions', [])
last = d.get('last_session_id')
if last and last not in linked:
    linked.append(last)
d['linked_sessions'] = linked
d['current_session_id'] = SESSION_ID
d['current_session_start'] = datetime.datetime.utcnow().isoformat() + 'Z'
json.dump(d, open(STATE, 'w'), indent=2)
" 2>/dev/null

echo "=== AGENT READY — continuing from last session ==="
