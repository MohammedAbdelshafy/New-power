#!/usr/bin/env bash
# patch-session.sh — Apply an ops-room enhancement patch to another session's CLAUDE.md.
# Usage: ./patch-session.sh <session-path> <patch-file.md> [--create-if-missing]
#
# The patch file is a Markdown snippet appended (or merged) into the target CLAUDE.md.

set -euo pipefail

SESSION_PATH="${1:-}"
PATCH_FILE="${2:-}"
CREATE_IF_MISSING=false

if [[ "${3:-}" == "--create-if-missing" ]]; then
  CREATE_IF_MISSING=true
fi

if [[ -z "$SESSION_PATH" || -z "$PATCH_FILE" ]]; then
  echo "Usage: $0 <session-path> <patch-file.md> [--create-if-missing]"
  exit 1
fi

if [[ ! -f "$PATCH_FILE" ]]; then
  echo "[patch-session] Patch file not found: $PATCH_FILE"
  exit 1
fi

TARGET_CLAUDE="$SESSION_PATH/CLAUDE.md"

if [[ ! -f "$TARGET_CLAUDE" ]]; then
  if $CREATE_IF_MISSING; then
    echo "[patch-session] Creating new CLAUDE.md at $TARGET_CLAUDE"
    echo "# Session Configuration" > "$TARGET_CLAUDE"
  else
    echo "[patch-session] CLAUDE.md not found at $TARGET_CLAUDE"
    echo "  Use --create-if-missing to create it."
    exit 1
  fi
fi

echo "==================================================="
echo "  OPS-ROOM SESSION PATCHER"
echo "  Target:  $TARGET_CLAUDE"
echo "  Patch:   $PATCH_FILE"
echo "==================================================="

echo ""
echo "[ PATCH CONTENT ]"
cat "$PATCH_FILE"
echo ""

# Check if this patch was already applied (by checking for a marker)
PATCH_MARKER="Imported: $(date +%Y-%m-%d)"
if grep -qF "$(head -1 "$PATCH_FILE")" "$TARGET_CLAUDE" 2>/dev/null; then
  echo "[patch-session] WARNING: A similar patch may already be applied."
  echo "  Check $TARGET_CLAUDE before re-applying."
  read -r -p "Continue anyway? [y/N] " confirm
  [[ "$confirm" =~ ^[Yy]$ ]] || exit 0
fi

# Apply: append patch to CLAUDE.md with a separator
{
  echo ""
  echo "---"
  echo "<!-- ops-room patch applied: $(date -u +%Y-%m-%dT%H:%M:%SZ) -->"
  cat "$PATCH_FILE"
} >> "$TARGET_CLAUDE"

echo "[patch-session] Patch applied to: $TARGET_CLAUDE"

# If it's a git repo, show the diff
if [[ -d "$SESSION_PATH/.git" ]]; then
  echo ""
  echo "[ Git Diff ]"
  git -C "$SESSION_PATH" diff CLAUDE.md 2>/dev/null || true
fi
