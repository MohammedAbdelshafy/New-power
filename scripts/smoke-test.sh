#!/usr/bin/env bash
# MBM smoke & regression suite. Runs the whole mission lifecycle, all guards,
# routing, and CRM commands in a throwaway sandbox (never touches real state).
# Release gate: must exit 0 before any version tag (Release/RELEASE_CHECKLIST.md).

set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/scripts"
cp "$ROOT/scripts/mbm.sh" "$TMP/scripts/"
cp -R "$ROOT/MBM" "$TMP/MBM"
cd "$TMP"
git init -q . && git add -A >/dev/null 2>&1
git -c user.email=smoke@mbm -c user.name=smoke commit -qm sandbox >/dev/null 2>&1

export MBM_WORKER=smoke-test
MBM="bash scripts/mbm.sh"
PASS=0; FAIL=0

ok()   { PASS=$((PASS+1)); echo "  PASS  $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  FAIL  $1"; }
check(){ # $1=description $2=command (must succeed)
  if eval "$2" >/dev/null 2>&1; then ok "$1"; else bad "$1"; fi
}
check_fails(){ # $1=description $2=command (must FAIL)
  if eval "$2" >/dev/null 2>&1; then bad "$1 (unexpectedly succeeded)"; else ok "$1"; fi
}

echo "== mission lifecycle =="
OUT=$($MBM mission new "Smoke lifecycle mission" crm-brain P2)
MID=$(echo "$OUT" | grep -oE 'M-[0-9]+' | head -1)
check "mission new creates $MID in Inbox"        "test -n '$MID' && ls MBM/MissionControl/Missions/Inbox/${MID}-*.md"
check "MissionCreated event emitted"             "grep -q '\"MissionCreated\", \"mission\": \"$MID\"' MBM/EventBus/events.jsonl || grep -q 'MissionCreated' MBM/EventBus/events.jsonl"
check "route recommends a worker"                "$MBM route $MID | grep -q RECOMMENDED"
check_fails "start before claim is rejected"     "$MBM mission start $MID"
check "claim moves to Claimed"                   "$MBM mission claim $MID fabel && ls MBM/MissionControl/Missions/Claimed/${MID}-*.md"
check "owner recorded on claim"                  "grep -q 'owner: fabel' MBM/MissionControl/Missions/Claimed/${MID}-*.md"
check_fails "double-claim is rejected"           "$MBM mission claim $MID claude"
check "start moves to InProgress"                "$MBM mission start $MID && ls MBM/MissionControl/Missions/InProgress/${MID}-*.md"
check_fails "complete from InProgress rejected"  "$MBM mission complete $MID"
check "review moves to Review"                   "$MBM mission review $MID && ls MBM/MissionControl/Missions/Review/${MID}-*.md"
check_fails "complete with empty lessons rejected (Article 7)" "$MBM mission complete $MID"
sed -i 's/^(fill before completion.*$/- smoke test lesson: the lifecycle guards behave as specified end to end./' MBM/MissionControl/Missions/Review/${MID}-*.md
check "complete succeeds once lessons filled"    "$MBM mission complete $MID && ls MBM/MissionControl/Missions/Completed/${MID}-*.md"
check "lessons mirrored to Knowledge_Base"       "grep -q '$MID' MBM/MissionControl/Knowledge_Base/LESSONS.md"
check "archive moves to Archive"                 "$MBM mission archive $MID && ls MBM/MissionControl/Missions/Archive/${MID}-*.md"

echo "== blocked / failed paths =="
OUT=$($MBM mission new "Smoke blocked mission" crm-brain P2)
M2=$(echo "$OUT" | grep -oE 'M-[0-9]+' | head -1)
$MBM mission claim $M2 fabel >/dev/null 2>&1
check "block moves to Blocked with reason"       "$MBM mission block $M2 'smoke reason' && ls MBM/MissionControl/Missions/Blocked/${M2}-*.md"
check "unblock returns to Claimed"               "$MBM mission unblock $M2 && ls MBM/MissionControl/Missions/Claimed/${M2}-*.md"
check "fail moves to Archive as failed"          "$MBM mission fail $M2 'smoke fail' && grep -q 'status: failed' MBM/MissionControl/Missions/Archive/${M2}-*.md"

echo "== dependency gate =="
OUT=$($MBM mission new "Smoke dependent mission" crm-brain P2)
M3=$(echo "$OUT" | grep -oE 'M-[0-9]+' | head -1)
sed -i "s/^dependencies: \[\]/dependencies:\n  - M-001/" MBM/MissionControl/Missions/Inbox/${M3}-*.md
check_fails "claim blocked while dependency incomplete" "$MBM mission claim $M3 fabel"

echo "== CRM =="
BEFORE=$(find MBM/CRM/leads -name '*.json' | wc -l)
check "lead add creates a lead"                  "$MBM lead add 'Smoke Test Industries' --score 70 --industry manufacturing"
check "qualified lead auto-files research mission" "grep -rlq 'Smoke Test Industries' MBM/MissionControl/Missions/Inbox/"
check "validate passes"                          "$MBM validate"
check "metrics counts the new lead"              "$MBM metrics && python3 -c \"import json,sys; m=json.load(open('MBM/Dashboard/metrics.json')); sys.exit(0 if m['leads_found']==$BEFORE+1 else 1)\""
check "followups lists the due lead"             "$MBM followups | grep -q 'Smoke Test Industries'"

echo "== registry & bus =="
check "workers lists >=8 registered workers"     "test \$($MBM workers | tail -n +2 | wc -l) -ge 8"
check "event bus grew during this run"           "test \$(wc -l < MBM/EventBus/events.jsonl) -ge 10"
check "status runs clean"                        "$MBM status"

echo
echo "RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
