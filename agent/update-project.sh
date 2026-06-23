#!/usr/bin/env bash
# Usage: ./agent/update-project.sh <project-name> <task-name> <status>
# Status: not_started | in_progress | blocked | complete
# Example: ./agent/update-project.sh "My App" "Build login page" complete

set -euo pipefail

REPO="/home/user/New-power"
REGISTRY="$REPO/.claude/project-registry.json"

PROJECT_NAME="${1:-}"
TASK_NAME="${2:-}"
TASK_STATUS="${3:-in_progress}"

if [ -z "$PROJECT_NAME" ] || [ -z "$TASK_NAME" ]; then
  echo "Usage: $0 <project-name> <task-name> <status>"
  echo "Status values: not_started | in_progress | blocked | complete"
  exit 1
fi

TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

python3 - <<PYEOF
import json

REGISTRY = "$REGISTRY"
PROJECT_NAME = """$PROJECT_NAME"""
TASK_NAME = """$TASK_NAME"""
TASK_STATUS = "$TASK_STATUS"
TIMESTAMP = "$TIMESTAMP"

try:
    d = json.load(open(REGISTRY))
except Exception:
    d = {"projects": [], "last_updated": None, "completion_summary": {}}

projects = d.get("projects", [])

# Find or create project
proj = next((p for p in projects if p["name"] == PROJECT_NAME), None)
if proj is None:
    proj = {"name": PROJECT_NAME, "status": "in_progress", "created": TIMESTAMP, "tasks": []}
    projects.append(proj)

# Find or create task
tasks = proj.get("tasks", [])
task = next((t for t in tasks if t["name"] == TASK_NAME), None)
if task is None:
    task = {"name": TASK_NAME, "status": TASK_STATUS, "created": TIMESTAMP, "updated": TIMESTAMP}
    tasks.append(task)
else:
    task["status"] = TASK_STATUS
    task["updated"] = TIMESTAMP

proj["tasks"] = tasks

# Roll up project status
statuses = [t["status"] for t in tasks]
if all(s == "complete" for s in statuses):
    proj["status"] = "complete"
elif any(s == "blocked" for s in statuses):
    proj["status"] = "blocked"
elif any(s == "in_progress" for s in statuses):
    proj["status"] = "in_progress"
else:
    proj["status"] = "not_started"

d["projects"] = projects
d["last_updated"] = TIMESTAMP

# Recompute summary
all_tasks = [t for p in projects for t in p.get("tasks", [])]
d["completion_summary"] = {
    "total": len(all_tasks),
    "complete": sum(1 for t in all_tasks if t["status"] == "complete"),
    "in_progress": sum(1 for t in all_tasks if t["status"] == "in_progress"),
    "not_started": sum(1 for t in all_tasks if t["status"] == "not_started"),
    "blocked": sum(1 for t in all_tasks if t["status"] == "blocked"),
}

json.dump(d, open(REGISTRY, "w"), indent=2)
print(f"Updated: [{TASK_STATUS}] {TASK_NAME} in project '{PROJECT_NAME}'")
PYEOF
