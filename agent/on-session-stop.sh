#!/usr/bin/env bash
# Stop hook: sends WhatsApp summary only.
# NO file writes, NO git operations — state is written at next SessionStart instead.
# This keeps the repo clean when the global git check runs at session end.

REPO="/home/user/New-power"
STATE="$REPO/.claude/session-state.json"
REGISTRY="$REPO/.claude/project-registry.json"

SUMMARY=$(python3 - 2>/dev/null <<'PYEOF'
import json
try:
    d    = json.load(open("/home/user/New-power/.claude/session-state.json"))
    reg  = json.load(open("/home/user/New-power/.claude/project-registry.json"))
    tasks = [t for p in reg.get("projects",[]) for t in p.get("tasks",[])]
    done  = sum(1 for t in tasks if t.get("status")=="complete")
    total = len(tasks)
    summ  = d.get("last_session_summary","Session ended.")
    print(f"{summ} | Tasks: {done}/{total} done")
except Exception:
    print("Session ended.")
PYEOF
)

bash "$REPO/agent/notify-whatsapp.sh" "$SUMMARY" "session_stop" 2>/dev/null || true

echo "[Coordinator] Session ended. State will be finalised on next session start."
