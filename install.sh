#!/usr/bin/env bash
# Install Claude Code cost guardrails into a target repository.
# Usage: bash install.sh [/path/to/target/repo]
# If no path given, installs into the current directory.

set -euo pipefail

TARGET_REPO="${1:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GUARDRAILS_DIR="$HOME/.claude/cost-guardrails"
BUDGET_FILE="$GUARDRAILS_DIR/budget.json"
TARGET_CLAUDE_DIR="$TARGET_REPO/.claude"
TARGET_SETTINGS="$TARGET_CLAUDE_DIR/settings.json"
DAILY_LIMIT="${CLAUDE_DAILY_LIMIT:-10.00}"

echo "Installing Claude Code cost guardrails..."
echo "  Target repo  : $TARGET_REPO"
echo "  Scripts dir  : $GUARDRAILS_DIR"
echo "  Daily limit  : \$$DAILY_LIMIT (set CLAUDE_DAILY_LIMIT env var to override)"
echo ""

# ── 1. Install scripts into ~/.claude/cost-guardrails/ ──────────────────────
mkdir -p "$GUARDRAILS_DIR"
cp "$SCRIPT_DIR/scripts/check-budget.sh"  "$GUARDRAILS_DIR/check-budget.sh"
cp "$SCRIPT_DIR/scripts/update-budget.sh" "$GUARDRAILS_DIR/update-budget.sh"
chmod +x "$GUARDRAILS_DIR/check-budget.sh" "$GUARDRAILS_DIR/update-budget.sh"
echo "[1/3] Scripts installed to $GUARDRAILS_DIR"

# ── 2. Initialise budget file ────────────────────────────────────────────────
TODAY=$(date +%Y-%m-%d)
if [ ! -f "$BUDGET_FILE" ]; then
  printf '{"daily_limit": %s, "today": "%s", "spent": 0.00}\n' \
    "$DAILY_LIMIT" "$TODAY" > "$BUDGET_FILE"
  echo "[2/3] Budget file created: \$$DAILY_LIMIT/day"
else
  echo "[2/3] Budget file already exists (not overwritten)"
fi

# ── 3. Merge hook into target repo's .claude/settings.json ──────────────────
mkdir -p "$TARGET_CLAUDE_DIR"

HOOK_COMMAND="$GUARDRAILS_DIR/check-budget.sh"

if [ -f "$TARGET_SETTINGS" ]; then
  # Merge: append the hook to any existing UserPromptSubmit array
  python3 - <<PYEOF
import json, sys

settings_path = "$TARGET_SETTINGS"
hook_cmd = "$HOOK_COMMAND"

with open(settings_path) as f:
    settings = json.load(f)

new_hook_entry = {
    "hooks": [
        {
            "type": "command",
            "command": hook_cmd,
            "timeout": 10,
            "statusMessage": "Checking cost budget..."
        }
    ]
}

hooks = settings.setdefault("hooks", {})
existing = hooks.get("UserPromptSubmit", [])

# Avoid duplicate installation
for entry in existing:
    for h in entry.get("hooks", []):
        if h.get("command") == hook_cmd:
            print("[3/3] Hook already present in $TARGET_SETTINGS (skipped)")
            sys.exit(0)

existing.append(new_hook_entry)
hooks["UserPromptSubmit"] = existing

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print("[3/3] Hook merged into existing $TARGET_SETTINGS")
PYEOF
else
  # Write fresh settings file
  python3 - <<PYEOF
import json

settings_path = "$TARGET_SETTINGS"
hook_cmd = "$HOOK_COMMAND"

settings = {
    "hooks": {
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": hook_cmd,
                        "timeout": 10,
                        "statusMessage": "Checking cost budget..."
                    }
                ]
            }
        ]
    }
}

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

print("[3/3] Created $TARGET_SETTINGS")
PYEOF
fi

echo ""
echo "Done!  Cost guardrails are active for: $TARGET_REPO"
echo ""
echo "Manage your budget:"
echo "  $GUARDRAILS_DIR/update-budget.sh status"
echo "  $GUARDRAILS_DIR/update-budget.sh add <amount>       # record spending"
echo "  $GUARDRAILS_DIR/update-budget.sh set-limit <amt>    # change daily cap"
echo "  $GUARDRAILS_DIR/update-budget.sh reset              # reset today"
echo ""
echo "After each Claude Code session, check the cost shown in the UI and run"
echo "  update-budget.sh add <cost> to keep the tracker accurate."
