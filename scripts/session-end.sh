#!/usr/bin/env bash
# Stop hook: reminds the user to record session cost after Claude Code finishes.
# Outputs a systemMessage that appears in the Claude Code UI at session end.

BUDGET_FILE="$HOME/.claude/cost-guardrails/budget.json"

python3 - <<'PYEOF'
import json, os
from datetime import date

budget_file = os.path.expanduser("~/.claude/cost-guardrails/budget.json")

if not os.path.exists(budget_file):
    exit(0)

with open(budget_file) as f:
    data = json.load(f)

today = date.today().isoformat()
if data.get("today") != today:
    spent = 0.0
else:
    spent = float(data.get("spent", 0.0))

limit = float(data.get("daily_limit", 10.00))
pct = spent / limit * 100 if limit else 0

print(json.dumps({
    "systemMessage": (
        f"Session ended. Today's recorded spend: ${spent:.4f} / ${limit:.2f} ({pct:.1f}%). "
        "If Claude Code showed a cost, run: "
        "~/.claude/cost-guardrails/update-budget.sh add <amount>"
    )
}))
PYEOF
