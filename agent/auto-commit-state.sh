#!/usr/bin/env bash
# Called by PostToolUse hook after any Write/Edit to .claude/ files.
# Keeps state files committed so the global git check never sees dirty state.

REPO="/home/user/New-power"
cd "$REPO" || exit 0

CHANGED=$(git status --porcelain .claude/ 2>/dev/null || true)
[ -z "$CHANGED" ] && exit 0

git add .claude/ 2>/dev/null || exit 0
STAGED=$(git diff --cached --name-only 2>/dev/null || true)
[ -z "$STAGED" ] && exit 0

git commit -m "Auto-save agent state [$(date -u '+%Y-%m-%dT%H:%M:%SZ')]" --quiet 2>/dev/null || exit 0
git push -u origin claude/chat-session-agent-cfzivv --quiet 2>/dev/null || true
