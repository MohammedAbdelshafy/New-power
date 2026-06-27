#!/usr/bin/env python3
"""
Ops Room Status Dashboard — prints a live summary of all queued, active, and completed operations.
Usage: python3 status.py [--json]
"""

import json
import sys
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]
OPS_ROOT  = REPO_ROOT / "ops-room"

def load_ops(status_dir: Path) -> list:
    ops = []
    if not status_dir.exists():
        return ops
    for f in sorted(status_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            data["_file"] = f.name
            ops.append(data)
        except Exception:
            pass
    return ops

def fmt_time(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return iso or "unknown"

def print_dashboard():
    queued    = load_ops(OPS_ROOT / "operations" / "queue")
    active    = load_ops(OPS_ROOT / "operations" / "active")
    completed = load_ops(OPS_ROOT / "operations" / "completed")

    manifest_file = OPS_ROOT / "sessions" / "manifest.json"
    sessions = []
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text())
        sessions = manifest.get("sessions", [])

    print("=" * 60)
    print("  MASTER OPERATIONS ROOM — STATUS")
    print(f"  {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    print(f"\n[ SESSIONS ] ({len(sessions)} registered)")
    for s in sessions:
        icon = "●" if s.get("status") == "active" else "○"
        print(f"  {icon} {s['name']} [{s.get('role','?')}] — {s.get('branch','?')}")
        if s.get("notes"):
            print(f"    {s['notes']}")

    print(f"\n[ OPERATIONS QUEUE ] ({len(queued)} pending)")
    for op in queued[:10]:
        platform = op.get("platform", op.get("repo_name", "?"))
        url      = op.get("url", op.get("repo_url", ""))
        ts       = fmt_time(op.get("queued_at", op.get("analyzed_at", "")))
        title    = op.get("metadata", {}).get("title") or op.get("repo_name") or url[:60]
        print(f"  → [{platform.upper()}] {title}")
        print(f"       Queued: {ts}  |  File: {op['_file']}")
        tasks = op.get("analysis", {}).get("implementation_tasks", [])
        if tasks:
            print(f"       Top task: [{tasks[0]['priority']}] {tasks[0]['task']}")

    print(f"\n[ ACTIVE OPERATIONS ] ({len(active)} running)")
    for op in active[:5]:
        print(f"  ▶ {op.get('_file')} — {op.get('status','?')}")

    print(f"\n[ COMPLETED OPERATIONS ] ({len(completed)} done)")
    for op in completed[:5]:
        print(f"  ✓ {op.get('_file')}")

    print("\n" + "=" * 60)
    print("  COMMANDS")
    print("  Analyze URL:    python3 intelligence/analyze-content.py <url>")
    print("  Find repos:     bash sources/find-repos.sh \"<query>\"")
    print("  Clone + map:    bash sources/clone-and-map.sh <repo-url>")
    print("  Read session:   bash enhancer/read-session.sh <path>")
    print("  Patch session:  bash enhancer/patch-session.sh <path> <patch.md>")
    print("=" * 60)

def main():
    if "--json" in sys.argv:
        queued    = load_ops(OPS_ROOT / "operations" / "queue")
        active    = load_ops(OPS_ROOT / "operations" / "active")
        completed = load_ops(OPS_ROOT / "operations" / "completed")
        manifest  = json.loads((OPS_ROOT / "sessions" / "manifest.json").read_text())
        print(json.dumps({
            "sessions":  manifest.get("sessions", []),
            "queue":     queued,
            "active":    active,
            "completed": completed,
        }, indent=2))
    else:
        print_dashboard()

if __name__ == "__main__":
    main()
