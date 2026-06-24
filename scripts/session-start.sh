#!/usr/bin/env bash
# SessionStart hook: verifies cost guardrails are in place and reports status.
# Warns loudly if any component is missing so issues are caught immediately.

GUARDRAILS_DIR="$HOME/.claude/cost-guardrails"
BUDGET_FILE="$GUARDRAILS_DIR/budget.json"
CHECK_SCRIPT="$GUARDRAILS_DIR/check-budget.sh"
STOP_SCRIPT="$GUARDRAILS_DIR/session-end.sh"

python3 - <<'PYEOF'
import json, os
from datetime import date

guardrails_dir  = os.path.expanduser("~/.claude/cost-guardrails")
budget_file     = os.path.join(guardrails_dir, "budget.json")
check_script    = os.path.join(guardrails_dir, "check-budget.sh")
stop_script     = os.path.join(guardrails_dir, "session-end.sh")
global_settings = os.path.expanduser("~/.claude/settings.json")

missing = []

if not os.path.isfile(check_script):
    missing.append("check-budget.sh missing")
if not os.path.isfile(stop_script):
    missing.append("session-end.sh missing")
if not os.path.isfile(budget_file):
    missing.append("budget.json missing")

# Verify global settings has both hooks wired
if os.path.isfile(global_settings):
    with open(global_settings) as f:
        cfg = json.load(f)
    hooks = cfg.get("hooks", {})

    has_pre  = any(h.get("command", "").endswith("check-budget.sh")
                   for e in hooks.get("UserPromptSubmit", [])
                   for h in e.get("hooks", []))
    has_stop = any(h.get("command", "").endswith("session-end.sh")
                   for e in hooks.get("Stop", [])
                   for h in e.get("hooks", []))
    if not has_pre:
        missing.append("UserPromptSubmit hook not wired in ~/.claude/settings.json")
    if not has_stop:
        missing.append("Stop hook not wired in ~/.claude/settings.json")
else:
    missing.append("~/.claude/settings.json not found")

if missing:
    print(json.dumps({
        "systemMessage": (
            "⚠ Cost guardrails issue(s) detected:\n"
            + "\n".join(f"  • {m}" for m in missing)
            + "\nRun: bash install.sh to repair."
        )
    }))
else:
    today = date.today().isoformat()
    with open(budget_file) as f:
        data = json.load(f)

    if data.get("today") != today:
        spent, limit = 0.0, float(data.get("daily_limit", 10.0))
    else:
        spent = float(data.get("spent", 0.0))
        limit = float(data.get("daily_limit", 10.0))

    pct = spent / limit * 100 if limit else 0
    print(json.dumps({
        "systemMessage": (
            f"Cost guardrails ON — ${spent:.4f} / ${limit:.2f} used today ({pct:.1f}%)."
        )
    }))
PYEOF
