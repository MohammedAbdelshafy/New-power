#!/usr/bin/env bash
# Cost guardrail: checks daily budget before each Claude Code prompt.
# Reads ~/.claude/cost-guardrails/budget.json and blocks or warns as needed.
# Returns JSON that Claude Code's UserPromptSubmit hook understands.

BUDGET_FILE="$HOME/.claude/cost-guardrails/budget.json"
TODAY=$(date +%Y-%m-%d)

# Bootstrap the budget file if it doesn't exist
if [ ! -f "$BUDGET_FILE" ]; then
  mkdir -p "$(dirname "$BUDGET_FILE")"
  printf '{"daily_limit": 10.00, "today": "%s", "spent": 0.00}\n' "$TODAY" > "$BUDGET_FILE"
fi

python3 - <<'PYEOF'
import json, os, sys
from datetime import date

budget_file = os.path.expanduser("~/.claude/cost-guardrails/budget.json")
today = date.today().isoformat()

with open(budget_file) as f:
    data = json.load(f)

# Reset counter when the calendar day rolls over
if data.get("today") != today:
    data["today"] = today
    data["spent"] = 0.0
    with open(budget_file, "w") as f:
        json.dump(data, f, indent=2)

limit = float(data.get("daily_limit", 10.00))
spent = float(data.get("spent", 0.0))

if spent >= limit:
    print(json.dumps({
        "continue": False,
        "stopReason": (
            f"Daily cost limit of ${limit:.2f} reached "
            f"(${spent:.2f} recorded today). "
            "Run: ~/.claude/cost-guardrails/update-budget.sh reset"
        )
    }))
elif spent >= limit * 0.8:
    print(json.dumps({
        "systemMessage": (
            f"Cost warning: ${spent:.2f} of ${limit:.2f} daily limit used "
            f"({spent/limit*100:.0f}%)."
        )
    }))
PYEOF
