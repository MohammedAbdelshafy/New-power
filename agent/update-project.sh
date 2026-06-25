#!/usr/bin/env bash
# Usage: ./agent/update-project.sh <project-name> <task-name> <status> [blocker-note]
# Status: not_started | in_progress | blocked | complete

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REGISTRY="$REPO/.claude/project-registry.json"

PROJECT_NAME="${1:-}"
TASK_NAME="${2:-}"
TASK_STATUS="${3:-in_progress}"
BLOCKER_NOTE="${4:-}"

if [ -z "$PROJECT_NAME" ] || [ -z "$TASK_NAME" ]; then
  echo "Usage: $0 <project-name> <task-name> <status> [blocker-note]"
  echo "Status values: not_started | in_progress | blocked | complete"
  exit 1
fi

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

RESULT=$(python3 - <<PYEOF
import json

REGISTRY = "$REGISTRY"
PROJECT_NAME = """$PROJECT_NAME"""
TASK_NAME = """$TASK_NAME"""
TASK_STATUS = "$TASK_STATUS"
BLOCKER_NOTE = """$BLOCKER_NOTE"""
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(REGISTRY))
except Exception:
    d = {"projects": [], "last_updated": None, "completion_summary": {}}

projects = d.get("projects", [])

proj = next((p for p in projects if p["name"] == PROJECT_NAME), None)
if proj is None:
    proj = {"name": PROJECT_NAME, "status": "in_progress", "created": TIMESTAMP, "tasks": []}
    projects.append(proj)

tasks = proj.get("tasks", [])
task = next((t for t in tasks if t["name"] == TASK_NAME), None)
old_status = task["status"] if task else None

if task is None:
    task = {"name": TASK_NAME, "status": TASK_STATUS, "created": TIMESTAMP, "updated": TIMESTAMP}
    tasks.append(task)
else:
    task["status"] = TASK_STATUS
    task["updated"] = TIMESTAMP

if BLOCKER_NOTE:
    task["blocker"] = BLOCKER_NOTE

proj["tasks"] = tasks

statuses = [t["status"] for t in tasks]
if all(s == "complete" for s in statuses):
    proj["status"] = "complete"
    proj_just_completed = True
elif any(s == "blocked" for s in statuses):
    proj["status"] = "blocked"
    proj_just_completed = False
elif any(s == "in_progress" for s in statuses):
    proj["status"] = "in_progress"
    proj_just_completed = False
else:
    proj["status"] = "not_started"
    proj_just_completed = False

d["projects"] = projects
d["last_updated"] = TIMESTAMP

all_tasks = [t for p in projects for t in p.get("tasks", [])]
d["completion_summary"] = {
    "total": len(all_tasks),
    "complete": sum(1 for t in all_tasks if t["status"] == "complete"),
    "in_progress": sum(1 for t in all_tasks if t["status"] == "in_progress"),
    "not_started": sum(1 for t in all_tasks if t["status"] == "not_started"),
    "blocked": sum(1 for t in all_tasks if t["status"] == "blocked"),
}

json.dump(d, open(REGISTRY, "w"), indent=2)

# Output notification info
print(f"UPDATED|{TASK_STATUS}|{TASK_NAME}|{PROJECT_NAME}|{proj_just_completed}")
PYEOF
)

echo "$RESULT" | grep -v '^UPDATED' || true

# Parse result for notifications
IFS='|' read -r _ STATUS TASK PROJ PROJ_DONE <<< "$(echo "$RESULT" | grep '^UPDATED' || echo 'UPDATED|unknown|unknown|unknown|False')"

case "$STATUS" in
  complete)
    MSG="Task done: \"$TASK\" in $PROJ."
    if [ "$PROJ_DONE" = "True" ]; then
      MSG="PROJECT COMPLETE: $PROJ — all tasks done!"
      bash "$REPO/agent/notify-whatsapp.sh" "$MSG" "project_complete" 2>/dev/null || true
    else
      bash "$REPO/agent/notify-whatsapp.sh" "$MSG" "task_complete" 2>/dev/null || true
    fi
    ;;
  blocked)
    NOTE=""
    [ -n "$BLOCKER_NOTE" ] && NOTE=" Blocker: $BLOCKER_NOTE"
    bash "$REPO/agent/notify-whatsapp.sh" "BLOCKED: \"$TASK\" in $PROJ.$NOTE" "task_blocked" 2>/dev/null || true
    ;;
  *)
    # in_progress / not_started — no notification by default
    ;;
esac

echo "Updated: [$STATUS] $TASK in '$PROJ'"
