#!/usr/bin/env bash
# Print a full status dashboard: sessions, projects, and kickbacks.

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     NEW-POWER COORDINATOR  STATUS        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Session state
echo "─── SESSION ───────────────────────────────"
python3 -c "
import json
try:
    d = json.load(open('$REPO/.claude/session-state.json'))
    print(f\"  Current : {d.get('current_session_id') or '(none)'}\")
    print(f\"  Last    : {d.get('last_session_id') or '(none)'}\")
    print(f\"  Summary : {d.get('last_session_summary') or '(none)'}\")
    linked = d.get('linked_sessions', [])
    if linked:
        print(f\"  Linked  : {', '.join(linked[-5:])}\")
    steps = d.get('next_steps', [])
    if steps:
        print('  Next steps:')
        for s in steps:
            print(f'    • {s}')
except Exception as e:
    print(f'  (error: {e})')
" 2>/dev/null
echo ""

# Projects
echo "─── PROJECTS ──────────────────────────────"
python3 -c "
import json
try:
    d = json.load(open('$REPO/.claude/project-registry.json'))
    projects = d.get('projects', [])
    summary = d.get('completion_summary', {})
    if not projects:
        print('  No projects registered.')
    else:
        print(f\"  Total tasks: {summary.get('total',0)}  |  Done: {summary.get('complete',0)}  |  In Progress: {summary.get('in_progress',0)}  |  Blocked: {summary.get('blocked',0)}\")
        print()
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

# Kickbacks
echo "─── KICKBACKS ─────────────────────────────"
python3 -c "
import json
try:
    d = json.load(open('$REPO/.claude/kickback-registry.json'))
    kbs = d.get('kickbacks', [])
    last = d.get('last_health_check', 'never')
    if not kbs:
        print('  No kickbacks registered.')
    else:
        print(f'  Last health check: {last}')
        for kb in kbs:
            status = kb.get('status','unknown')
            icon = {'healthy':'✓','degraded':'⚠','unreachable':'✗','registered':'?'}.get(status,'?')
            code = kb.get('last_status_code','')
            code_str = f' ({code})' if code else ''
            print(f\"  {icon} {kb['name']}{code_str} — {status}\")
except Exception as e:
    print(f'  (error: {e})')
" 2>/dev/null
echo ""
echo "───────────────────────────────────────────"
