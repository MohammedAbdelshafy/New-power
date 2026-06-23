#!/usr/bin/env bash
# Runs at the start of every Claude Code session.

set -euo pipefail

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
KICKBACKS="$REPO/.claude/kickback-registry.json"

SESSION_ID="session-$(date +%Y%m%d-%H%M%S)-$$"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

echo "=== NEW-POWER COORDINATOR AGENT STARTING ==="
echo "Session ID: $SESSION_ID"
echo "Time: $TIMESTAMP"
echo ""

# --- Load + display last session ---
LAST_SUMMARY="Initial startup"
LAST_ID="(none)"
NEXT_STEPS_TEXT=""

if [ -f "$STATE" ]; then
  LAST_SUMMARY=$(python3 -c "
import json,sys
d=json.load(open('$STATE'))
print(d.get('last_session_summary','(none)'))
" 2>/dev/null || echo "(could not read)")

  LAST_ID=$(python3 -c "
import json,sys
d=json.load(open('$STATE'))
print(d.get('last_session_id') or '(first session)')
" 2>/dev/null || echo "unknown")

  echo "--- Resuming from: $LAST_ID ---"
  echo "Last summary: $LAST_SUMMARY"
  echo ""

  NEXT_STEPS_TEXT=$(python3 -c "
import json
d = json.load(open('$STATE'))
steps = d.get('next_steps', [])
for i, s in enumerate(steps, 1):
    print(f'  {i}. {s}')
" 2>/dev/null || echo "")
  if [ -n "$NEXT_STEPS_TEXT" ]; then
    echo "Next steps carried over:"
    echo "$NEXT_STEPS_TEXT"
    echo ""
  fi
fi

# --- Project status ---
OPEN_TASKS=0
BLOCKED_TASKS=0
COMPLETE_TASKS=0
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
        icon = {'complete':'✓','in_progress':'⏳','blocked':'🚧','not_started':'○'}.get(status,'?')
        print(f'  {icon} {name} [{status}]')
        for t in p.get('tasks', []):
            ts = t.get('status', '?')
            tn = t.get('name', '?')
            ti = {'complete':'  ✓','in_progress':'  ▶','blocked':'  🚧','not_started':'  ○'}.get(ts,'  ?')
            print(f'{ti} {tn}')
" 2>/dev/null || echo "  (could not read registry)"

  read OPEN_TASKS BLOCKED_TASKS COMPLETE_TASKS < <(python3 -c "
import json
d = json.load(open('$REGISTRY'))
tasks = [t for p in d.get('projects',[]) for t in p.get('tasks',[])]
open_t = sum(1 for t in tasks if t.get('status') in ('in_progress','not_started'))
blocked = sum(1 for t in tasks if t.get('status') == 'blocked')
done = sum(1 for t in tasks if t.get('status') == 'complete')
print(open_t, blocked, done)
" 2>/dev/null || echo "0 0 0")
  echo ""
fi

# --- Kickback health check ---
KB_STATUS="OK"
KB_FAILURES=""
if [ -f "$KICKBACKS" ]; then
  echo "--- Kickback Health ---"
  KB_STATUS=$(python3 - <<'PYEOF'
import json, urllib.request, urllib.error, datetime, sys

KICKBACKS = "/home/user/New-power/.claude/kickback-registry.json"
d = json.load(open(KICKBACKS))
kickbacks = d.get("kickbacks", [])
timestamp = datetime.datetime.utcnow().isoformat() + "Z"
failures = []

if not kickbacks:
    print("NONE")
    sys.exit(0)

for kb in kickbacks:
    name = kb.get("name", "?")
    url = kb.get("health_check_url") or kb.get("endpoint_url", "")
    if not url:
        continue
    try:
        req = urllib.request.urlopen(url, timeout=6)
        kb["last_status_code"] = req.status
        kb["last_checked"] = timestamp
        prev = kb.get("status","")
        kb["status"] = "healthy"
        icon = "✓"
        if prev in ("unreachable","degraded"):
            kb["recovered"] = True
        print(f"  {icon} {name}")
    except Exception as e:
        kb["last_checked"] = timestamp
        kb["status"] = "unreachable"
        failures.append(name)
        print(f"  ✗ {name} — FAILED: {e}")

d["last_health_check"] = timestamp
json.dump(d, open(KICKBACKS, "w"), indent=2)

if failures:
    print("FAIL:" + ",".join(failures))
else:
    print("OK")
PYEOF
  2>/dev/null || echo "SKIP")

  KB_FAILURES=$(echo "$KB_STATUS" | grep '^FAIL:' | sed 's/^FAIL://' || true)
  echo ""
fi

# --- Save session start to state ---
python3 - <<PYEOF2
import json, datetime
STATE = "$STATE"
SESSION_ID = "$SESSION_ID"
TIMESTAMP = "$TIMESTAMP"
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
d['current_session_start'] = TIMESTAMP
json.dump(d, open(STATE, 'w'), indent=2)
PYEOF2

# --- Build WhatsApp notification ---
WA_MSG="Session started."
if [ "$OPEN_TASKS" -gt 0 ] 2>/dev/null || [ "$BLOCKED_TASKS" -gt 0 ] 2>/dev/null; then
  WA_MSG="Session started. Open: ${OPEN_TASKS} tasks, Blocked: ${BLOCKED_TASKS}, Done: ${COMPLETE_TASKS}."
fi
if [ -n "$KB_FAILURES" ]; then
  WA_MSG="$WA_MSG KICKBACK ALERT: ${KB_FAILURES} is DOWN."
fi
FIRST_STEP=$(echo "$NEXT_STEPS_TEXT" | head -1 | sed 's/^[[:space:]]*//')
if [ -n "$FIRST_STEP" ]; then
  WA_MSG="$WA_MSG Next: $FIRST_STEP"
fi

bash "$REPO/agent/notify-whatsapp.sh" "$WA_MSG" "session_start" 2>/dev/null || true

# --- Alert on kickback failures ---
if [ -n "$KB_FAILURES" ]; then
  bash "$REPO/agent/notify-whatsapp.sh" "ALERT: Kickback(s) DOWN: $KB_FAILURES — fixing before other work." "kickback_failure" 2>/dev/null || true
fi

echo "=== AGENT READY — continuing from last session ==="
