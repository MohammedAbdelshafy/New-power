#!/usr/bin/env bash
# Manage the Claude Code daily cost budget.
# Usage:
#   update-budget.sh status              – show current state
#   update-budget.sh add <amount>        – record spending (e.g. add 1.23)
#   update-budget.sh reset               – zero out today's spending
#   update-budget.sh set-limit <amount>  – change the daily limit

BUDGET_FILE="$HOME/.claude/cost-guardrails/budget.json"
TODAY=$(date +%Y-%m-%d)

if [ ! -f "$BUDGET_FILE" ]; then
  echo "Budget file not found: $BUDGET_FILE"
  echo "Run install.sh first."
  exit 1
fi

case "${1:-status}" in
  add)
    AMOUNT="${2:?'Usage: update-budget.sh add <amount>'}"
    python3 -c "
import json
with open('$BUDGET_FILE') as f: d = json.load(f)
d['spent'] = round(float(d.get('spent', 0)) + float('$AMOUNT'), 6)
with open('$BUDGET_FILE', 'w') as f: json.dump(d, f, indent=2)
print(f\"Recorded \$$AMOUNT. Today's total: \${d['spent']:.4f} / \${d['daily_limit']:.2f}\")
"
    ;;
  reset)
    python3 -c "
import json
from datetime import date
with open('$BUDGET_FILE') as f: d = json.load(f)
d['today'] = date.today().isoformat()
d['spent'] = 0.0
with open('$BUDGET_FILE', 'w') as f: json.dump(d, f, indent=2)
print('Daily spending reset to \$0.00')
"
    ;;
  set-limit)
    LIMIT="${2:?'Usage: update-budget.sh set-limit <amount>'}"
    python3 -c "
import json
with open('$BUDGET_FILE') as f: d = json.load(f)
d['daily_limit'] = float('$LIMIT')
with open('$BUDGET_FILE', 'w') as f: json.dump(d, f, indent=2)
print(f\"Daily limit set to \${d['daily_limit']:.2f}\")
"
    ;;
  status)
    python3 -c "
import json
from datetime import date
with open('$BUDGET_FILE') as f: d = json.load(f)
today = date.today().isoformat()
if d.get('today') != today:
    print(f\"Today: {today} (no spending recorded yet)\")
else:
    spent = float(d.get('spent', 0))
    limit = float(d.get('daily_limit', 10))
    pct = spent / limit * 100 if limit else 0
    print(f\"Today ({today}): \${spent:.4f} / \${limit:.2f}  ({pct:.1f}%)\")
"
    ;;
  *)
    echo "Usage: update-budget.sh [status|add <amount>|reset|set-limit <amount>]"
    exit 1
    ;;
esac
