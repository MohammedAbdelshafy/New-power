#!/usr/bin/env bash
# MBM version manager + changelog generator.
# Usage: release.sh <major|minor|patch> ["summary line"]
# Runs the quality gates (smoke suite, CRM validate), bumps Release/VERSION,
# prepends a changelog section generated from git log, and creates the tag.
# Push is manual and deliberate: git push --follow-tags

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VFILE="$ROOT/Release/VERSION"
CHANGELOG="$ROOT/Release/CHANGELOG.md"
BUMP="${1:?usage: release.sh <major|minor|patch> [summary]}"
SUMMARY="${2:-}"
TODAY="$(date +%Y-%m-%d)"

echo "== Gate 1: smoke & regression suite =="
bash "$ROOT/scripts/smoke-test.sh" || { echo "ABORT: smoke suite failed"; exit 1; }
echo "== Gate 2: CRM integrity =="
bash "$ROOT/scripts/mbm.sh" validate || { echo "ABORT: CRM validation failed"; exit 1; }

OLD="$(cat "$VFILE")"
IFS=. read -r MA MI PA <<< "$OLD"
case "$BUMP" in
  major) MA=$((MA+1)); MI=0; PA=0 ;;
  minor) MI=$((MI+1)); PA=0 ;;
  patch) PA=$((PA+1)) ;;
  *) echo "ABORT: bump must be major|minor|patch"; exit 1 ;;
esac
NEW="$MA.$MI.$PA"

LAST_TAG="$(git -C "$ROOT" describe --tags --abbrev=0 2>/dev/null || true)"
RANGE="${LAST_TAG:+$LAST_TAG..HEAD}"
COMMITS="$(git -C "$ROOT" log ${RANGE:-} --no-merges --pretty='- %s' | head -40)"

echo "$NEW" > "$VFILE"
TMP="$(mktemp)"
{
  echo "# Changelog"
  echo
  echo "## v$NEW — $TODAY"
  [[ -n "$SUMMARY" ]] && { echo; echo "$SUMMARY"; }
  echo
  echo "$COMMITS"
  echo
  tail -n +2 "$CHANGELOG" 2>/dev/null || true
} > "$TMP"
mv "$TMP" "$CHANGELOG"

git -C "$ROOT" add "$VFILE" "$CHANGELOG"
git -C "$ROOT" commit -m "Release v$NEW${SUMMARY:+: $SUMMARY}"
git -C "$ROOT" tag -a "v$NEW" -m "v$NEW${SUMMARY:+: $SUMMARY}"
echo "Tagged v$NEW (was $OLD). Review Release/CHANGELOG.md wording, then: git push --follow-tags"
