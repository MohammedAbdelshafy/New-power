#!/usr/bin/env python3
"""
JARVIS OPS — Operations Center
Generates a live summary of all registered projects: GitHub health, CI status,
open issues, open PRs, blockers, and next recommended priorities.
Usage: python3 ops-center.py [--json] [--project <id>]
"""

import json
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[2]
OPS_ROOT  = REPO_ROOT / "ops-room"

def utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

def load_manifest():
    f = OPS_ROOT / "sessions" / "manifest.json"
    if f.exists():
        return json.loads(f.read_text()).get("sessions", [])
    return []

def load_intel():
    f = OPS_ROOT / "jarvis" / "project-intel.json"
    if f.exists():
        return json.loads(f.read_text())
    return {}

def load_ops_queue():
    counts = {}
    for status in ("queue", "active", "completed"):
        d = OPS_ROOT / "operations" / status
        counts[status] = len(list(d.glob("*.json"))) if d.exists() else 0
    return counts

def load_pending_approvals():
    f = OPS_ROOT / "jarvis" / "approvals" / "pending.json"
    if f.exists():
        data = json.loads(f.read_text())
        return data.get("pending", [])
    return []

def load_discoveries():
    f = OPS_ROOT / "jarvis" / "research" / "discoveries.json"
    if f.exists():
        data = json.loads(f.read_text())
        return data.get("discoveries", [])
    return []

def git_status(local_path: str):
    try:
        result = subprocess.run(
            ["git", "-C", local_path, "status", "--short"],
            capture_output=True, text=True, timeout=10
        )
        lines = [l for l in result.stdout.strip().splitlines() if l]
        return {"uncommitted": len(lines), "files": lines[:5]}
    except Exception:
        return {"uncommitted": 0, "files": []}

def git_branch(local_path: str):
    try:
        result = subprocess.run(
            ["git", "-C", local_path, "branch", "--show-current"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"

def recent_commits(local_path: str, n=3):
    try:
        result = subprocess.run(
            ["git", "-C", local_path, "log", f"-{n}", "--oneline", "--no-decorate"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip().splitlines()
    except Exception:
        return []

def print_dashboard(sessions, intel, ops_counts, approvals, discoveries):
    SEP = "=" * 64

    print(SEP)
    print("  JARVIS OPS — OPERATIONS CENTER")
    print(f"  {utcnow()}")
    print(SEP)

    # Pending approvals — always first
    if approvals:
        print(f"\n[ ⚠ PENDING APPROVALS ] ({len(approvals)} waiting)")
        for a in approvals:
            print(f"  • [{a.get('risk','?')}] {a.get('action','?')}")
            print(f"    Target: {a.get('target','?')}")
            print(f"    Reason: {a.get('reason','?')}")
    else:
        print(f"\n[ ✓ APPROVALS ] No actions pending owner approval.")

    # Sessions / Projects
    print(f"\n[ REGISTERED PROJECTS ] ({len(sessions)})")
    for s in sessions:
        icon = "●" if s.get("status") == "active" else "○"
        role_icon = "★" if s.get("role") == "master" else "◦"
        print(f"\n  {icon} {role_icon} {s['name']}")
        print(f"    Repo:   {s.get('repo','?')}")
        print(f"    Branch: {s.get('branch','?')}")

        local = s.get("local_path", "")
        if local and os.path.isdir(local):
            gs = git_status(local)
            branch = git_branch(local)
            commits = recent_commits(local)
            uncommitted = gs["uncommitted"]
            status_str = f"{'⚠ ' + str(uncommitted) + ' uncommitted' if uncommitted else '✓ clean'}"
            print(f"    Git:    [{branch}] {status_str}")
            for c in commits:
                print(f"             {c}")

        # Project intel for this session
        proj_intel = intel.get("projects", {}).get(s.get("id", ""), {})
        if proj_intel:
            blockers = proj_intel.get("blockers", [])
            if blockers:
                print(f"    Blockers: {len(blockers)}")
                for b in blockers[:2]:
                    print(f"      [{b.get('severity','?')}] {b.get('description','?')}")

    # Operations pipeline
    print(f"\n[ OPERATIONS PIPELINE ]")
    print(f"  Queue:     {ops_counts.get('queue',0)} pending")
    print(f"  Active:    {ops_counts.get('active',0)} in progress")
    print(f"  Completed: {ops_counts.get('completed',0)} done")

    # AI Research
    if discoveries:
        recent = discoveries[-3:]
        print(f"\n[ AI RESEARCH ] ({len(discoveries)} total discoveries)")
        for d in reversed(recent):
            status_tag = f"[{d.get('status','?').upper()}]"
            print(f"  {status_tag} {d.get('name','?')} — {d.get('category','?')}")
            print(f"    {d.get('why_it_matters','')[:80]}")

    # Next priorities
    all_tasks = []
    for proj in intel.get("projects", {}).values():
        for t in proj.get("next_priorities", []):
            all_tasks.append(t)
    all_tasks.sort(key=lambda x: {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3}.get(x.get("priority","LOW"),3))

    if all_tasks:
        print(f"\n[ NEXT HIGHEST-VALUE TASKS ]")
        for t in all_tasks[:5]:
            print(f"  [{t.get('priority','?')}] {t.get('task','?')}")
            print(f"    → {t.get('detail','')}")

    print(f"\n{SEP}")
    print("  JARVIS OPS COMMANDS")
    print("  ops-center:         python3 ops-room/jarvis/ops-center.py")
    print("  analyze url:        python3 ops-room/intelligence/analyze-content.py <url>")
    print("  find repos:         bash ops-room/sources/find-repos.sh \"<query>\"")
    print("  read session:       bash ops-room/enhancer/read-session.sh <path>")
    print("  full dashboard:     python3 ops-room/dashboard/status.py")
    print(SEP)


def main():
    sessions    = load_manifest()
    intel       = load_intel()
    ops_counts  = load_ops_queue()
    approvals   = load_pending_approvals()
    discoveries = load_discoveries()

    project_filter = None
    if "--project" in sys.argv:
        idx = sys.argv.index("--project")
        project_filter = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        sessions = [s for s in sessions if s.get("id") == project_filter]

    if "--json" in sys.argv:
        print(json.dumps({
            "generated_at": utcnow(),
            "sessions":     sessions,
            "ops":          ops_counts,
            "approvals":    approvals,
            "discoveries":  discoveries,
            "intel":        intel,
        }, indent=2))
    else:
        print_dashboard(sessions, intel, ops_counts, approvals, discoveries)


if __name__ == "__main__":
    main()
