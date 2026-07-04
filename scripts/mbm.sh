#!/usr/bin/env bash
# MBM Operating System CLI (v2) — mission lifecycle, event bus, registry,
# routing, CRM intake, integrity, metrics. Needs bash + python3 only.
#
#   mbm.sh status                            pipeline, missions, events, follow-ups
#   mbm.sh mission new "<title>" <role> [P0|P1|P2]
#   mbm.sh mission claim <id> <worker-id>    Inbox -> Claimed (duplicate-safe: push immediately)
#   mbm.sh mission start <id>                Claimed -> InProgress
#   mbm.sh mission block <id> "<reason>"     Claimed/InProgress -> Blocked
#   mbm.sh mission unblock <id>              Blocked -> Claimed
#   mbm.sh mission review <id>               InProgress -> Review
#   mbm.sh mission complete <id>             Review -> Completed (BLOCKS if Lessons Learned empty)
#   mbm.sh mission fail <id> "<reason>"      any active -> Archive (status: failed)
#   mbm.sh mission archive <id>              Completed -> Archive
#   mbm.sh mission escalate <id> "<note>"    emit MissionEscalated (no move)
#   mbm.sh route <id>                        rank registered workers for a mission
#   mbm.sh workers                           list the worker registry
#   mbm.sh events [N]                        tail the event bus (default 15)
#   mbm.sh emit <Event> <mission> <actor> [note]
#   mbm.sh lead add "<Company>" [--score N] [--industry X]
#   mbm.sh followups | validate | metrics
#
# Actor attribution: set MBM_WORKER=<registry-id> (defaults to "unknown").

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MBM="$ROOT/MBM"
MISSIONS="$MBM/MissionControl/Missions"
LEADS="$MBM/CRM/leads"
REGISTRY="$MBM/Registry/workers"
EVENTS="$MBM/EventBus/events.jsonl"
LESSONS="$MBM/MissionControl/Knowledge_Base/LESSONS.md"
METRICS="$MBM/Dashboard/metrics.json"
TODAY="$(date +%Y-%m-%d)"
ACTOR="${MBM_WORKER:-unknown}"
STATES=(Inbox Claimed InProgress Review Completed Blocked Archive)

die() { echo "error: $*" >&2; exit 1; }

find_mission() { # $1=id -> path or empty
  local d
  for d in "${STATES[@]}"; do
    local hit
    hit=$(find "$MISSIONS/$d" -maxdepth 1 -name "${1}-*.md" 2>/dev/null | head -1)
    [[ -n "$hit" ]] && { echo "$hit"; return; }
  done
}

mission_folder() { basename "$(dirname "$1")"; }

next_seq() { # $1=dir(s recursively) $2=prefix $3=width
  local max=0 n
  while IFS= read -r f; do
    n=$(basename "$f" | sed -E "s/^${2}-?([0-9]+).*/\1/") || continue
    [[ "$n" =~ ^[0-9]+$ ]] && (( 10#$n > max )) && max=$((10#$n))
  done < <(find "$1" -name "${2}*" 2>/dev/null)
  printf "%0${3}d" $((max + 1))
}

set_field() { # $1=file $2=key $3=value  (front-matter scalar)
  sed -i.bak -E "0,/^${2}: .*/s//${2}: ${3//\//\\/}/" "$1" && rm -f "$1.bak"
}

log_line() { printf -- "- %s %s\n" "$TODAY" "$2" >> "$1"; }

emit() { # $1=event $2=mission $3=actor $4=note
  EV="$1" MI="$2" AC="$3" NO="${4:-}" python3 -c '
import json, os, datetime
rec = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
       "event": os.environ["EV"], "mission": os.environ["MI"],
       "actor": os.environ["AC"], "note": os.environ["NO"]}
print(json.dumps(rec, ensure_ascii=False))' >> "$EVENTS"
  echo "event: $1 $2 (actor: $3)"
}

move_mission() { # $1=src-path $2=dest-state $3=new-status $4=event $5=lognote $6=note-for-event
  local src="$1"
  set_field "$src" status "$3"
  log_line "$src" "$5"
  git -C "$ROOT" mv "$src" "$MISSIONS/$2/" 2>/dev/null || mv "$src" "$MISSIONS/$2/"
  emit "$4" "$(basename "$src" .md | grep -oE '^M-[0-9]+')" "$ACTOR" "${6:-}"
}

require_state() { # $1=path $2=id $3=expected-states (space-sep)
  local cur; cur=$(mission_folder "$1")
  [[ " $3 " == *" $cur "* ]] || die "$2 is in $cur, expected: $3"
}

lessons_ok() { # $1=path -> 0 if Lessons Learned has real content
  python3 - "$1" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
m = re.search(r"## Lessons Learned\n(.*?)(?=\n## |\Z)", text, re.S)
body = (m.group(1) if m else "")
body = re.sub(r"\((?:fill before completion|REQUIRED before completion)[^)]*\)", "", body).strip()
sys.exit(0 if len(body) >= 20 else 1)
PY
}

cmd_mission() {
  local sub="${1:-}"; shift || true
  local id path
  case "$sub" in
    new)
      local title="${1:?title required}" role="${2:?role required}" prio="${3:-P1}"
      local seq slug
      seq=$(next_seq "$MISSIONS" "M" 3)
      id="M-$seq"
      slug=$(echo "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-|-$//g' | cut -c1-40)
      path="$MISSIONS/Inbox/$id-$slug.md"
      sed -e "s/^id: M-XXX.*/id: $id/" \
          -e "s/^title: \"\"/title: \"${title//\//\\/}\"/" \
          -e "s/^role: \"\"/role: $role/" \
          -e "s/^priority: P1.*/priority: $prio/" \
          -e "s/^created: YYYY-MM-DD/created: $TODAY/" \
          -e "s/^- YYYY-MM-DD created by <actor>/- $TODAY created by $ACTOR/" \
          "$MISSIONS/Templates/mission-template.md" > "$path"
      emit MissionCreated "$id" "$ACTOR" "$title"
      echo "created $path" ;;
    claim)
      id="${1:?mission id}" ; local worker="${2:?worker registry id}"
      path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Inbox"
      [[ -f "$REGISTRY/$worker.json" ]] || echo "warning: $worker has no registry entry ($REGISTRY/$worker.json)" >&2
      # dependency gate
      local dep deps
      deps=$(sed -n '/^dependencies:/,/^[a-z_]*:/p' "$path" | grep -oE 'M-[0-9]+' || true)
      for dep in $deps; do
        [[ "$(mission_folder "$(find_mission "$dep")")" =~ ^(Completed|Archive)$ ]] || die "dependency $dep is not Completed"
      done
      set_field "$path" owner "$worker"
      ACTOR="$worker" move_mission "$path" Claimed claimed MissionClaimed "claimed by $worker" ""
      echo "REMINDER (Article 3): commit and push this claim NOW. A rejected push means someone else owns it." ;;
    start)
      id="${1:?mission id}"; path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Claimed"
      move_mission "$path" InProgress in_progress MissionStarted "started" "" ;;
    block)
      id="${1:?mission id}"; local reason="${2:?reason required}"
      path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Claimed InProgress"
      move_mission "$path" Blocked blocked MissionBlocked "BLOCKED: $reason" "$reason" ;;
    unblock)
      id="${1:?mission id}"; path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Blocked"
      move_mission "$path" Claimed claimed MissionUnblocked "unblocked" "" ;;
    review)
      id="${1:?mission id}"; path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "InProgress"
      move_mission "$path" Review review MissionReviewed "moved to review" "" ;;
    complete)
      id="${1:?mission id}"; path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Review"
      lessons_ok "$path" || die "$id has an empty Lessons Learned section — Article 7 blocks completion. Fill it, then retry."
      # mirror lessons to Knowledge_Base/LESSONS.md
      { echo ""; echo "## $id — $(sed -nE 's/^title: \"?([^\"]*)\"?/\1/p' "$path" | head -1) ($TODAY)";
        python3 - "$path" <<'PY'
import re, sys
text = open(sys.argv[1]).read()
m = re.search(r"## Lessons Learned\n(.*?)(?=\n## |\Z)", text, re.S)
print(re.sub(r"\(fill before completion[^)]*\)", "", m.group(1)).strip())
PY
      } >> "$LESSONS"
      move_mission "$path" Completed completed MissionCompleted "completed; lessons mirrored to Knowledge_Base/LESSONS.md" ""
      echo "Run the knowledge-capture checklist: MBM/MissionControl/Missions/SOPs/SOP-knowledge-capture.md" ;;
    fail)
      id="${1:?mission id}"; local why="${2:?reason required}"
      path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Inbox Claimed InProgress Review Blocked"
      move_mission "$path" Archive failed MissionFailed "FAILED: $why" "$why" ;;
    archive)
      id="${1:?mission id}"; path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      require_state "$path" "$id" "Completed"
      move_mission "$path" Archive archived MissionArchived "archived" "" ;;
    escalate)
      id="${1:?mission id}"; local note="${2:?note required}"
      path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
      log_line "$path" "ESCALATED: $note"
      emit MissionEscalated "$id" "$ACTOR" "$note" ;;
    *) die "usage: mbm.sh mission new|claim|start|block|unblock|review|complete|fail|archive|escalate ..." ;;
  esac
}

cmd_route() {
  local id="${1:?mission id}" path
  path=$(find_mission "$id"); [[ -n "$path" ]] || die "$id not found"
  MISSION_PATH="$path" REGISTRY_DIR="$REGISTRY" EVENTS_FILE="$EVENTS" MISSIONS_DIR="$MISSIONS" python3 <<'PY'
import json, os, re, glob

mpath, rdir = os.environ["MISSION_PATH"], os.environ["REGISTRY_DIR"]

def frontmatter(path):
    text = open(path).read()
    fm = re.match(r"^---\n(.*?)\n---", text, re.S).group(1)
    data, key = {}, None
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            val = re.sub(r"\s+#.*$", "", val).strip()  # drop inline comments
            if val in ("", "[]"): data[key] = [] if val == "[]" else ""
            else: data[key] = val.strip('"')
        elif re.match(r"^\s+- ", line) and key:
            if not isinstance(data.get(key), list): data[key] = []
            data[key].append(line.strip()[2:].strip())
    return data

mission = frontmatter(mpath)
required = set(mission.get("required_skills") or [])
preferred = mission.get("preferred_worker", "")
fallbacks = mission.get("fallback_workers") or []

# performance + workload from the event bus and mission folders
perf = {}
for line in open(os.environ["EVENTS_FILE"]).read().splitlines() if os.path.exists(os.environ["EVENTS_FILE"]) else []:
    try: e = json.loads(line)
    except Exception: continue
    a = e.get("actor", "")
    if e.get("event") == "MissionCompleted": perf[a] = perf.get(a, 0) + 1
    if e.get("event") == "MissionFailed":    perf[a] = perf.get(a, 0) - 2

workload = {}
for st in ("Claimed", "InProgress"):
    for f in glob.glob(os.path.join(os.environ["MISSIONS_DIR"], st, "M-*.md")):
        o = frontmatter(f).get("owner", "")
        if o: workload[o] = workload.get(o, 0) + 1

COST = {"low": 1.0, "medium": 0.6, "high": 0.3}
SPEED = {"fast": 1.0, "medium": 0.7, "slow": 0.4}
rows, skipped = [], []
for wf in sorted(glob.glob(os.path.join(rdir, "*.json"))):
    w = json.load(open(wf))
    wid, skills = w["id"], set(w.get("skills", []))
    if w.get("availability") == "offline":
        skipped.append((wid, "offline")); continue
    match = 1.0 if not required else len(required & skills) / len(required)
    if match < 0.5:
        skipped.append((wid, "skills " + str(sorted(required - skills)) + " missing")); continue
    score = (0.35 * match + 0.25 * float(w.get("confidence", 0.5))
             + 0.15 * COST.get(w.get("cost", "medium"), 0.6)
             + 0.10 * SPEED.get(w.get("speed", "medium"), 0.7)
             + 0.15 * max(0.0, min(1.0, 0.5 + 0.1 * perf.get(wid, 0))))
    score -= 0.15 * workload.get(wid, 0)
    if w.get("availability") == "busy": score -= 0.30
    if wid == preferred: score += 0.25
    elif wid in fallbacks: score += 0.10
    rows.append((round(score, 3), wid, match, workload.get(wid, 0), perf.get(wid, 0), w.get("availability")))

rows.sort(reverse=True)
print("Routing %s (role: %s, required: %s, preferred: %s)" %
      (mission["id"], mission.get("role", "?"), sorted(required) or "none", preferred or "none"))
if not rows:
    print("  NO ELIGIBLE WORKER — check registry skills/availability"); raise SystemExit(1)
print("  %-6s %-14s %-6s %-9s %-5s %s" % ("score", "worker", "skill", "workload", "perf", "availability"))
for s, wid, m, wl, p, av in rows:
    print("  %-6s %-14s %-6s %-9s %-5s %s" % (s, wid, round(m, 2), wl, p, av))
for wid, why in skipped:
    print("  (skipped %s: %s)" % (wid, why))
print("RECOMMENDED: " + rows[0][1])
PY
}

cmd_workers() {
  [[ -d "$REGISTRY" ]] || die "no registry at $REGISTRY"
  REGISTRY_DIR="$REGISTRY" python3 <<'PY'
import json, glob, os
print("%-14s %-12s %-10s %-7s %-7s %-5s %-4s %-4s %-4s %s" %
      ("id", "kind", "avail", "cost", "speed", "conf", "mcp", "git", "web", "skills"))
for wf in sorted(glob.glob(os.path.join(os.environ["REGISTRY_DIR"], "*.json"))):
    w = json.load(open(wf))
    print("%-14s %-12s %-10s %-7s %-7s %-5s %-4s %-4s %-4s %s" %
          (w["id"], w.get("kind",""), w.get("availability",""), w.get("cost",""), w.get("speed",""),
           w.get("confidence",""), "y" if w.get("mcp_support") else "n",
           "y" if w.get("git_support") else "n", "y" if w.get("web_support") else "n",
           ",".join(w.get("skills", []))))
PY
}

cmd_events() {
  local n="${1:-15}"
  [[ -f "$EVENTS" ]] || { echo "no events yet"; return; }
  tail -n "$n" "$EVENTS" | python3 -c '
import json, sys
for line in sys.stdin:
    try: e = json.loads(line)
    except Exception: continue
    print("%s  %-18s %-7s %-14s %s" % (e["ts"], e["event"], e["mission"], e["actor"], e.get("note","")))'
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
  COMPANY="$company" ID="$id" IND="$industry" SCORE="$score" TODAY="$TODAY" ACTOR="$ACTOR" python3 - "$path" <<'PY'
import json, os, sys
lead = {
  "id": os.environ["ID"], "company": os.environ["COMPANY"], "domain": "", "website": "",
  "industry": os.environ["IND"], "geography": "", "size": "", "language": "en", "source": "",
  "signals": [], "contacts": [], "pain_points": [],
  "fit_score": int(os.environ["SCORE"]), "stage": "new", "owner": "",
  "next_action": {"date": os.environ["TODAY"], "action": "complete lead record (signals, contacts, source)"},
  "estimated_value": 0, "won": None, "lost_reason": None, "relationships": [],
  "history": [{"date": os.environ["TODAY"], "actor": os.environ["ACTOR"], "event": "created", "note": ""}],
}
json.dump(lead, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
PY
  echo "created $path"
  if (( score >= 60 )); then
    cmd_mission new "Research $company ($id)" company-researcher P1 >/dev/null
    echo "qualified (score $score) -> research mission filed in Inbox"
  fi
}

py_leads() { find "$LEADS" -name '*.json' -print0 | python3 -c "$1"; }

cmd_validate() {
  py_leads '
import json, sys, os
REQ = ["id","company","industry","stage","fit_score","next_action","history"]
STAGES = {"new","researched","contacted","replied","meeting","proposal","won","lost"}
IND = {"construction","industrial","recycling","ports","manufacturing","ai-automation","b2b-services"}
bad = 0
files = [x for x in sys.stdin.buffer.read().split(b"\0") if x]
for f in files:
    f = f.decode()
    try:
        d = json.load(open(f))
    except Exception as e:
        print("INVALID JSON %s: %s" % (f, e)); bad += 1; continue
    errs = [k for k in REQ if k not in d]
    if d.get("stage") not in STAGES: errs.append("bad stage %r" % d.get("stage"))
    if d.get("industry") not in IND: errs.append("bad industry %r" % d.get("industry"))
    if not isinstance(d.get("fit_score"), int) or not 0 <= d.get("fit_score", -1) <= 100: errs.append("fit_score not 0-100 int")
    if d.get("stage") not in ("won","lost") and not (d.get("next_action") or {}).get("date"): errs.append("active lead missing next_action.date")
    if errs: print(os.path.basename(f) + ": " + "; ".join(errs)); bad += 1
print(("FAIL" if bad else "OK") + ": %d lead(s) checked, %d problem(s)" % (len(files), bad))
sys.exit(1 if bad else 0)
'
}

cmd_followups() {
  py_leads '
import json, sys, datetime
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
    print("%d lead(s) need action:" % len(rows))
    for r in sorted(rows, key=lambda r: r[2]):
        print("  %s  %-30s  due %-10s  %s" % (r[0], r[1][:30], r[2], r[3]))
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
  echo "=== MBM Operating System — $TODAY (actor: $ACTOR) ==="
  echo
  if [[ -f "$METRICS" ]]; then
    python3 -c '
import json, sys
m = json.load(open(sys.argv[1]))
print("  Revenue $%s / $%s   MRR $%s   Pipeline $%s" % (format(m["revenue"], ","), format(m["goal_usd"], ","), format(m["mrr"], ","), format(m["pipeline_value"], ",")))
print("  Leads %d (qualified %d)  Outreach %d  Meetings %d  Proposals %d  Close rate %.0f%%" % (m["leads_found"], m["qualified_leads"], m["outreach_sent"], m["meetings_booked"], m["proposals_sent"], m["close_rate"] * 100))' "$METRICS"
  fi
  echo
  local d n
  for d in Inbox Claimed InProgress Review Blocked; do
    n=$(find "$MISSIONS/$d" -name 'M-*.md' 2>/dev/null | wc -l | tr -d ' ')
    echo "  Missions/$d: $n"
    find "$MISSIONS/$d" -name 'M-*.md' 2>/dev/null | sort | while IFS= read -r f; do
      echo "    - $(basename "$f" .md)"
    done
  done
  echo
  echo "  Recent events:"
  cmd_events 5 | sed 's/^/    /'
  echo
  cmd_followups
}

case "${1:-}" in
  status)    cmd_status ;;
  mission)   shift; cmd_mission "$@" ;;
  route)     shift; cmd_route "$@" ;;
  workers)   cmd_workers ;;
  events)    shift || true; cmd_events "${1:-15}" ;;
  emit)      shift; emit "${1:?event}" "${2:?mission}" "${3:?actor}" "${4:-}" ;;
  lead)      shift; [[ "${1:-}" == "add" ]] || die "usage: mbm.sh lead add \"<Company>\" [--score N] [--industry X]"; shift; cmd_lead_add "$@" ;;
  followups) cmd_followups ;;
  validate)  cmd_validate ;;
  metrics)   cmd_metrics ;;
  *) sed -n '2,26p' "$0"; exit 1 ;;
esac
