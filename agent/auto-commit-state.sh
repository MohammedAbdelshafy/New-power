#!/usr/bin/env bash
# Called by PostToolUse (Write|Edit) and as second Stop hook.
# Commits any dirty .claude/ state files so the global git check passes.

REPO="/home/user/New-power"
LOG="$REPO/.claude/hook-debug.log"
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

log() { echo "[$TIMESTAMP] $*" >> "$LOG" 2>/dev/null || true; }

log "auto-commit-state.sh called (PWD=$PWD)"

cd "$REPO" || { log "FAIL: cd $REPO"; exit 0; }

# Remove any stale git lock that would block commit
if [ -f ".git/index.lock" ]; then
  log "Removing stale .git/index.lock"
  rm -f ".git/index.lock"
fi

CHANGED=$(git status --porcelain .claude/ 2>&1)
log "git status: $CHANGED"
[ -z "$CHANGED" ] && { log "Nothing to commit."; exit 0; }

git add .claude/ 2>&1 | while read -r line; do log "git add: $line"; done || true

STAGED=$(git diff --cached --name-only 2>/dev/null || true)
log "staged files: $STAGED"
[ -z "$STAGED" ] && { log "Nothing staged after add."; exit 0; }

COMMIT_OUT=$(git commit -m "Auto-save agent state [$TIMESTAMP]" 2>&1)
COMMIT_EXIT=$?
log "git commit exit=$COMMIT_EXIT output: $COMMIT_OUT"
[ $COMMIT_EXIT -ne 0 ] && exit 0

PUSH_OUT=$(git push -u origin claude/chat-session-agent-cfzivv 2>&1)
PUSH_EXIT=$?
log "git push exit=$PUSH_EXIT output: $PUSH_OUT"
