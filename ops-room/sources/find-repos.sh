#!/usr/bin/env bash
# find-repos.sh — Search GitHub and GitLab for repos matching a query.
# Usage: ./find-repos.sh "query keywords" [--stars <min>] [--lang <language>]
#
# Requires: gh CLI (GitHub), curl (GitLab), jq

set -euo pipefail

QUERY="${1:-}"
MIN_STARS="${3:-0}"
LANG="${5:-}"

if [[ -z "$QUERY" ]]; then
  echo "Usage: $0 \"search query\" [--stars <min>] [--lang <language>]"
  exit 1
fi

# Parse optional flags
while [[ $# -gt 1 ]]; do
  case "$2" in
    --stars) MIN_STARS="$3"; shift 2 ;;
    --lang)  LANG="$3"; shift 2 ;;
    *) shift ;;
  esac
done

LANG_FILTER=""
if [[ -n "$LANG" ]]; then
  LANG_FILTER=" language:$LANG"
fi

echo "==================================================="
echo "  OPS-ROOM SOURCE INTELLIGENCE"
echo "  Query: $QUERY"
echo "  Min stars: $MIN_STARS  |  Lang: ${LANG:-any}"
echo "==================================================="

# ── GitHub ──────────────────────────────────────────────
echo ""
echo "[ GITHUB ]"
if command -v gh &>/dev/null; then
  GH_QUERY="$QUERY$LANG_FILTER stars:>=$MIN_STARS"
  gh search repos "$GH_QUERY" \
    --sort stars \
    --order desc \
    --limit 10 \
    --json fullName,description,stargazersCount,url,language,updatedAt \
    2>/dev/null | jq -r '.[] | "\(.stargazersCount) ⭐  \(.fullName)\n     \(.description // "no description")\n     \(.url)\n"' \
    || echo "  (gh CLI not authenticated or rate-limited)"
else
  echo "  gh CLI not installed — install from https://cli.github.com"
fi

# ── GitLab ──────────────────────────────────────────────
echo ""
echo "[ GITLAB ]"
ENCODED_QUERY=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$QUERY" 2>/dev/null || echo "$QUERY")
GL_URL="https://gitlab.com/api/v4/projects?search=${ENCODED_QUERY}&order_by=star_count&sort=desc&per_page=10"

if command -v curl &>/dev/null && command -v jq &>/dev/null; then
  GL_RESULT=$(curl -sf "$GL_URL" 2>/dev/null || echo "[]")
  if [[ "$GL_RESULT" != "[]" && -n "$GL_RESULT" ]]; then
    echo "$GL_RESULT" | jq -r '.[] | "\(.star_count) ⭐  \(.path_with_namespace)\n     \(.description // "no description")\n     \(.web_url)\n"' 2>/dev/null \
      || echo "  (no results)"
  else
    echo "  No GitLab results or rate-limited."
  fi
else
  echo "  curl/jq not available."
fi

echo ""
echo "=== To clone and map a repo: ==="
echo "  ./clone-and-map.sh <repo-url>"
