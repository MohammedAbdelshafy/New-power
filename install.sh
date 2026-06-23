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
cp "$SCRIPT_DIR/scripts/session-end.sh"   "$GUARDRAILS_DIR/session-end.sh"
chmod +x "$GUARDRAILS_DIR/check-budget.sh" "$GUARDRAILS_DIR/update-budget.sh" "$GUARDRAILS_DIR/session-end.sh"
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

CHECK_CMD="$GUARDRAILS_DIR/check-budget.sh"
STOP_CMD="$GUARDRAILS_DIR/session-end.sh"

python3 - <<PYEOF
import json, sys, os

settings_path = "$TARGET_SETTINGS"
check_cmd = "$CHECK_CMD"
stop_cmd  = "$STOP_CMD"

# Load or create settings
if os.path.exists(settings_path):
    with open(settings_path) as f:
        settings = json.load(f)
else:
    settings = {}

hooks = settings.setdefault("hooks", {})
added = []

# ── UserPromptSubmit (pre-prompt budget check) ───────────────────────────────
ups = hooks.get("UserPromptSubmit", [])
already = any(h.get("command") == check_cmd
              for e in ups for h in e.get("hooks", []))
if not already:
    ups.append({"hooks": [{"type": "command", "command": check_cmd,
                            "timeout": 10, "statusMessage": "Checking cost budget..."}]})
    hooks["UserPromptSubmit"] = ups
    added.append("UserPromptSubmit")

# ── Stop (post-session reminder) ─────────────────────────────────────────────
stop = hooks.get("Stop", [])
already = any(h.get("command") == stop_cmd
              for e in stop for h in e.get("hooks", []))
if not already:
    stop.append({"hooks": [{"type": "command", "command": stop_cmd, "timeout": 10}]})
    hooks["Stop"] = stop
    added.append("Stop")

with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)

if added:
    print(f"[3/3] Hooks added ({', '.join(added)}): $TARGET_SETTINGS")
else:
    print("[3/3] Hooks already present (skipped)")
PYEOF

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
