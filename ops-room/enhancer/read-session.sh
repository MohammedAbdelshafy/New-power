#!/usr/bin/env bash
# read-session.sh — Read another session's CLAUDE.md and settings.
# Usage: ./read-session.sh <path-to-session-repo-or-dir>
#
# Outputs a summary of the session's current config to stdout.

set -euo pipefail

TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 <path-to-session-repo-or-dir>"
  echo ""
  echo "Examples:"
  echo "  $0 /home/user/my-other-project"
  echo "  $0 /home/user/New-power"
  exit 1
fi

if [[ ! -d "$TARGET" ]]; then
  echo "[read-session] Directory not found: $TARGET"
  exit 1
fi

echo "==================================================="
echo "  OPS-ROOM SESSION READER"
echo "  Target: $TARGET"
echo "==================================================="

# CLAUDE.md locations to check
CLAUDE_LOCATIONS=(
  "$TARGET/CLAUDE.md"
  "$TARGET/.claude/CLAUDE.md"
  "$TARGET/ops-room/CLAUDE.md"
)

found_claude=false
for loc in "${CLAUDE_LOCATIONS[@]}"; do
  if [[ -f "$loc" ]]; then
    echo ""
    echo "[ CLAUDE.md → $loc ]"
    echo "---"
    cat "$loc"
    echo "---"
    found_claude=true
    break
  fi
done

if ! $found_claude; then
  echo ""
  echo "[ CLAUDE.md ] Not found in standard locations."
fi

# Settings
SETTINGS_LOCATIONS=(
  "$TARGET/.claude/settings.json"
  "$TARGET/.claude/settings.local.json"
)
for loc in "${SETTINGS_LOCATIONS[@]}"; do
  if [[ -f "$loc" ]]; then
    echo ""
    echo "[ Settings → $loc ]"
    echo "---"
    cat "$loc"
    echo "---"
  fi
done

# Git info
if [[ -d "$TARGET/.git" ]]; then
  echo ""
  echo "[ Git Status ]"
  git -C "$TARGET" log --oneline -5 2>/dev/null || true
  echo ""
  echo "[ Active Branch ]"
  git -C "$TARGET" branch --show-current 2>/dev/null || true
fi

echo ""
echo "=== To enhance this session: ==="
echo "  ./patch-session.sh $TARGET <patch-file.md>"
