#!/usr/bin/env bash
# SessionStart hook: finalise previous session state, open new session, commit everything.
# File writes happen HERE (start), not at stop — keeps stop hook git-clean.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"
KICKBACKS="$REPO/.claude/kickback-registry.json"
LOG="$REPO/.claude/hook-debug.log"

SESSION_ID="session-$(date +%Y%m%d-%H%M%S)-$$"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

echo "=== NEW-POWER COORDINATOR AGENT STARTING ==="
echo "Session ID: $SESSION_ID"
echo "Time: $TIMESTAMP"
echo ""

python3 - <<PYEOF
import json, datetime, sys

STATE     = "$STATE"
REGISTRY  = "$REGISTRY"
SESSION_ID = "$SESSION_ID"
TIMESTAMP  = "$TIMESTAMP"
LOG        = "$LOG"

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f"[$TIMESTAMP][start] {msg}\n")

# Load state
try:
    d = json.load(open(STATE))
except Exception:
    d = {}

# ── Finalise previous session ──────────────────────────────────────────────
prev_session = d.get('current_session_id') or d.get('last_session_id')
if prev_session:
    d['last_session_id'] = prev_session
    log(f"Closed previous session: {prev_session}")

# ── Link sessions ──────────────────────────────────────────────────────────
linked = d.get('linked_sessions', [])
if prev_session and prev_session not in linked:
    linked.append(prev_session)
d['linked_sessions'] = linked

# ── Open new session ───────────────────────────────────────────────────────
d['current_session_id']    = SESSION_ID
d['current_session_start'] = TIMESTAMP
d['last_session_timestamp'] = TIMESTAMP

# Write state
with open(STATE, 'w') as f:
    json.dump(d, f, indent=2); f.write('\n')
log(f"Opened session {SESSION_ID}")

# ── Print resume briefing ──────────────────────────────────────────────────
last_id      = d.get('last_session_id', '(first session)')
last_summary = d.get('last_session_summary', '(none)')
print(f"--- Resuming from: {last_id} ---")
print(f"Last summary: {last_summary}")

steps = d.get('next_steps', [])
if steps:
    print("Next steps carried over:")
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")
print()
PYEOF

# ── Project status ─────────────────────────────────────────────────────────
echo "--- Project Status ---"
python3 -c "
import json
try:
    d = json.load(open('$REGISTRY'))
    projects = d.get('projects', [])
    if not projects:
        print('  No projects registered yet.')
    else:
        for p in projects:
            icon = {'complete':'✓','in_progress':'⏳','blocked':'🚧','not_started':'○'}.get(p.get('status',''),'?')
            print(f\"  {icon} {p['name']} [{p.get('status','?')}]\")
            for t in p.get('tasks', []):
                ti = {'complete':'  ✓','in_progress':'  ▶','blocked':'  🚧','not_started':'  ○'}.get(t.get('status',''),'  ?')
                print(f\"{ti} {t['name']}\")
except Exception as e:
    print(f'  (error: {e})')
" 2>/dev/null
echo ""

# ── Kickback health ────────────────────────────────────────────────────────
echo "--- Kickback Health ---"
KICKBACKS="$KICKBACKS" python3 - <<'PYEOF2'
import json, urllib.request, urllib.error, datetime, os

KICKBACKS = os.environ["KICKBACKS"]
try:
    d = json.load(open(KICKBACKS))
except Exception:
    print("  (cannot read registry)")
    exit()

kbs = d.get("kickbacks", [])
ts  = datetime.datetime.utcnow().isoformat() + "Z"
if not kbs:
    print("  No kickbacks registered.")
else:
    for kb in kbs:
        name = kb.get("name", "?")
        url  = kb.get("health_check_url") or kb.get("endpoint_url", "")
        if not url:
            print(f"  [SKIP] {name}")
            continue
        try:
            code = urllib.request.urlopen(url, timeout=6).status
            kb["status"] = "healthy"; kb["last_status_code"] = code; kb["last_checked"] = ts
            print(f"  [OK {code}] {name}")
        except Exception as e:
            kb["status"] = "unreachable"; kb["last_checked"] = ts
            print(f"  [FAIL] {name} — {e}")
    d["last_health_check"] = ts
    json.dump(d, open(KICKBACKS, "w"), indent=2)
PYEOF2
echo ""

# ── WhatsApp session-start notification ────────────────────────────────────
bash "$REPO/agent/notify-whatsapp.sh" \
  "Session started ($SESSION_ID). Coordinator ready." \
  "session_start" 2>/dev/null || true

echo "=== AGENT READY — continuing from last session ==="
