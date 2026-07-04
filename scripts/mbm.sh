#!/usr/bin/env bash
# MBM Revenue Engine CLI — mission lifecycle, lead intake, integrity, metrics.
# Works anywhere in the repo; needs bash + python3 (no other deps).
#
#   mbm.sh status                        pipeline + open missions overview
#   mbm.sh mission new "<title>" <worker> [P0|P1|P2]
#   mbm.sh mission start|review|complete <id>        (e.g. M-003)
#   mbm.sh lead add "<Company>" [--score N] [--industry X]
#   mbm.sh followups                     leads with due/overdue/missing next_action
#   mbm.sh validate                      schema-check every lead file
#   mbm.sh metrics                       recompute Dashboard/metrics.json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MBM="$ROOT/MBM"
MISSIONS="$MBM/MissionControl/Missions"
LEADS="$MBM/CRM/leads"
METRICS="$MBM/Dashboard/metrics.json"
TODAY="$(date +%Y-%m-%d)"

die() { echo "error: $*" >&2; exit 1; }

find_mission() { # $1=id -> path or empty
  find "$MISSIONS" -name "${1}-*.md" -o -name "${1}.md" 2>/dev/null | head -1
}

next_seq() { # $1=dir $2=prefix $3=width
  local max=0 n
  while IFS= read -r f; do
    n=$(basename "$f" | sed -E "s/^${2}-?([0-9]+).*/\1/") || continue
    [[ "$n" =~ ^[0-9]+$ ]] && (( 10#$n > max )) && max=$((10#$n))
  done < <(find "$1" -name "${2}*" 2>/dev/null)
  printf "%0${3}d" $((max + 1))
}

cmd_mission() {
  local sub="${1:-}"; shift || true
  case "$sub" in
    new)
      local title="${1:?title required}" worker="${2:?worker required}" prio="${3:-P1}"
      local seq slug id path
      seq=$(next_seq "$MISSIONS" "M" 3)
      id="M-$seq"
      slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g' | cut -c1-40)
      path="$MISSIONS/Inbox/$id-$slug.md"
      cat > "$path" <<EOF
---
id: $id
title: $title
phase: 1
worker: $worker
priority: $prio
status: inbox
created: $TODAY
due: ""
owner: ""
success_criteria:
  - REPLACE with binary criteria
artifacts: []
---

## Context

## Instructions

## Log
- $TODAY created
EOF
      echo "created $path" ;;
    start|review|complete)
      local id="${1:?mission id required}" src dest st
      src=$(find_mission "$id"); [[ -n "$src" ]] || die "mission $id not found"
      case "$sub" in
        start)    dest="InProgress"; st="in_progress" ;;
        review)   dest="Review";     st="review" ;;
        complete) dest="Completed";  st="completed" ;;
      esac
      sed -i.bak -E "s/^status: .*/status: $st/" "$src" && rm -f "$src.bak"
      printf -- "- %s moved to %s\n" "$TODAY" "$dest" >> "$src"
      git -C "$ROOT" mv "$src" "$MISSIONS/$dest/" 2>/dev/null || mv "$src" "$MISSIONS/$dest/"
      echo "$id -> $dest" ;;
    *) die "usage: mbm.sh mission new|start|review|complete ..." ;;
  esac
}

cmd_lead_add() {
  local company="${1:?company name required}"; shift || true
  local score=0 industry="b2b-services"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --score)    score="$2"; shift 2 ;;
      --industry) industry="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  local year seq slug id path
  year=$(date +%Y)
  seq=$(next_seq "$LEADS" "L-$year" 4)
  id="L-$year-$seq"
  slug=$(echo "$company" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g' | cut -c1-30)
  path="$LEADS/$id-$slug.json"
  COMPANY="$company" ID="$id" IND="$industry" SCORE="$score" TODAY="$TODAY" python3 - "$path" <<'PY'
import json, os, sys
lead = {
  "id": os.environ["ID"], "company": os.environ["COMPANY"], "domain": "", "website": "",
  "industry": os.environ["IND"], "geography": "", "size": "", "language": "en", "source": "",
  "signals": [], "contacts": [], "pain_points": [],
  "fit_score": int(os.environ["SCORE"]), "stage": "new", "owner": "",
  "next_action": {"date": os.environ["TODAY"], "action": "complete lead record (signals, contacts, source)"},
  "estimated_value": 0, "won": None, "lost_reason": None, "relationships": [],
  "history": [{"date": os.environ["TODAY"], "actor": "lead-hunter", "event": "created", "note": ""}],
}
json.dump(lead, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
PY
  echo "created $path"
  if (( score >= 60 )); then
    cmd_mission new "Research $company ($id)" company-researcher P1 >/dev/null
    echo "qualified (score $score) -> research mission filed in Inbox"
  fi
}

py_leads() { # run python over all lead files; script on stdin
  find "$LEADS" -name '*.json' -print0 | python3 -c "$1"
}

cmd_validate() {
  local code
  code='
import json, sys, os, datetime
REQ = ["id","company","industry","stage","fit_score","next_action","history"]
STAGES = {"new","researched","contacted","replied","meeting","proposal","won","lost"}
IND = {"construction","industrial","recycling","ports","manufacturing","ai-automation","b2b-services"}
bad = 0
files = sys.stdin.buffer.read().split(b"\0")
for f in filter(None, files):
    f = f.decode()
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f"INVALID JSON {f}: {e}"); bad += 1; continue
    errs = [k for k in REQ if k not in d]
    if d.get("stage") not in STAGES: errs.append("bad stage %r" % d.get("stage"))
    if d.get("industry") not in IND: errs.append("bad industry %r" % d.get("industry"))
    if not isinstance(d.get("fit_score"), int) or not 0 <= d.get("fit_score", -1) <= 100: errs.append("fit_score not 0-100 int")
    if d.get("stage") not in ("won","lost") and not (d.get("next_action") or {}).get("date"): errs.append("active lead missing next_action.date")
    if errs: print(os.path.basename(f) + ": " + "; ".join(errs)); bad += 1
n = len([x for x in files if x])
print(("FAIL" if bad else "OK") + ": %d lead(s) checked, %d problem(s)" % (n, bad))
sys.exit(1 if bad else 0)
'
  py_leads "$code"
}

cmd_followups() {
  py_leads '
import json, sys, os, datetime
today = datetime.date.today().isoformat()
rows = []
for f in filter(None, sys.stdin.buffer.read().split(b"\0")):
    d = json.load(open(f.decode()))
    if d.get("stage") in ("won", "lost"): continue
    na = d.get("next_action") or {}
    date, action = na.get("date", ""), na.get("action", "")
    if not date: rows.append((d["id"], d["company"], "MISSING", "no next_action set"))
    elif date <= today: rows.append((d["id"], d["company"], date, action))
if not rows:
    print("No due or overdue follow-ups. Pipeline is current.")
else:
    print(f"{len(rows)} lead(s) need action:")
    for r in sorted(rows, key=lambda r: r[2]):
        print(f"  {r[0]}  {r[1][:30]:30}  due {r[2]:10}  {r[3]}")
'
}

cmd_metrics() {
  METRICS_OUT="$METRICS" TODAY="$TODAY" py_leads '
import json, sys, os
stages = ["new","researched","contacted","replied","meeting","proposal","won","lost"]
counts = {s: 0 for s in stages}
qualified = outreach_sent = meetings = proposals = 0
pipeline_value = revenue = mrr = 0
ORDER = {s: i for i, s in enumerate(stages)}
for f in filter(None, sys.stdin.buffer.read().split(b"\0")):
    d = json.load(open(f.decode()))
    st = d.get("stage", "new"); counts[st] = counts.get(st, 0) + 1
    reached = ORDER.get(st, 0)
    if d.get("fit_score", 0) >= 60: qualified += 1
    if reached >= ORDER["contacted"] and st != "lost": outreach_sent += 1
    if reached >= ORDER["meeting"] and st != "lost": meetings += 1
    if reached >= ORDER["proposal"] and st != "lost": proposals += 1
    if st in ("meeting", "proposal"): pipeline_value += d.get("estimated_value", 0)
    if st == "won" and d.get("won"):
        revenue += d["won"].get("value", 0); mrr += d["won"].get("recurring_monthly", 0)
closed = counts["won"] + counts["lost"]
m = {
  "updated": os.environ["TODAY"],
  "goal_usd": 100000,
  "leads_found": sum(counts.values()),
  "qualified_leads": qualified,
  "outreach_sent": outreach_sent,
  "meetings_booked": meetings,
  "proposals_sent": proposals,
  "close_rate": round(counts["won"] / closed, 3) if closed else 0,
  "pipeline_value": pipeline_value,
  "mrr": mrr,
  "revenue": revenue,
  "stages": counts,
}
json.dump(m, open(os.environ["METRICS_OUT"], "w"), indent=2)
print(json.dumps(m, indent=2))
'
}

cmd_status() {
  echo "=== MBM Revenue Engine — $TODAY ==="
  echo
  if [[ -f "$METRICS" ]]; then
    python3 -c '
import json, sys
m = json.load(open(sys.argv[1]))
print("  Revenue $%s / $%s   MRR $%s   Pipeline $%s" % (format(m["revenue"], ","), format(m["goal_usd"], ","), format(m["mrr"], ","), format(m["pipeline_value"], ",")))
print("  Leads %d (qualified %d)  Outreach %d  Meetings %d  Proposals %d  Close rate %.0f%%" % (m["leads_found"], m["qualified_leads"], m["outreach_sent"], m["meetings_booked"], m["proposals_sent"], m["close_rate"] * 100))
print("  (metrics as of %s — run mbm.sh metrics to refresh)" % m["updated"])' "$METRICS"
  else
    echo "  no metrics yet — run: mbm.sh metrics"
  fi
  echo
  for d in Inbox InProgress Review; do
    local n
    n=$(find "$MISSIONS/$d" -name 'M-*.md' 2>/dev/null | wc -l | tr -d ' ')
    echo "  Missions/$d: $n"
    find "$MISSIONS/$d" -name 'M-*.md' 2>/dev/null | sort | while IFS= read -r f; do
      echo "    - $(basename "$f" .md)"
    done
  done
  echo
  cmd_followups
}

case "${1:-}" in
  status)    cmd_status ;;
  mission)   shift; cmd_mission "$@" ;;
  lead)      shift; [[ "${1:-}" == "add" ]] || die "usage: mbm.sh lead add \"<Company>\" [--score N] [--industry X]"; shift; cmd_lead_add "$@" ;;
  followups) cmd_followups ;;
  validate)  cmd_validate ;;
  metrics)   cmd_metrics ;;
  *) sed -n '2,12p' "$0"; exit 1 ;;
esac
