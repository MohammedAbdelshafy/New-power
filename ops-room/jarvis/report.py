#!/usr/bin/env python3
"""
JARVIS OPS — Task Report Generator
Generates a structured end-of-task report and saves it to jarvis/reports/.
Usage: python3 report.py --task "description" [--files "f1,f2"] [--blockers "b1,b2"] [--next "t1,t2"]
       python3 report.py --interactive
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT    = Path(__file__).resolve().parents[2]
REPORTS_DIR  = REPO_ROOT / "ops-room" / "jarvis" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_report(task, summary, files_changed=None, commands=None,
                    tests=None, deployment="not deployed", security="none",
                    blockers=None, next_priorities=None) -> str:
    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    tag = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")

    lines = [
        f"# JARVIS OPS — Task Report",
        f"",
        f"**Date**: {ts}",
        f"**Task**: {task}",
        f"**Session**: claude/master-operations-room-8349xd",
        f"",
        f"---",
        f"",
        f"## Summary",
        f"",
        summary or "(no summary provided)",
        f"",
        f"---",
        f"",
        f"## Files Changed",
        f"",
    ]

    if files_changed:
        lines.append("| File | Change |")
        lines.append("|------|--------|")
        for fc in (files_changed or []):
            if isinstance(fc, dict):
                lines.append(f"| `{fc.get('file','')}` | {fc.get('change','')} |")
            else:
                lines.append(f"| `{fc}` | — |")
    else:
        lines.append("No files changed.")

    lines += ["", "---", "", "## Commands Executed", "", "```"]
    for cmd in (commands or ["(none)"]):
        lines.append(f"# {cmd}")
    lines += ["```", "", "---", "", "## Tests Run", ""]

    if tests:
        lines.append("| Suite | Status | Notes |")
        lines.append("|-------|--------|-------|")
        for t in tests:
            lines.append(f"| {t.get('suite','')} | {t.get('status','')} | {t.get('notes','')} |")
    else:
        lines.append("No tests run.")

    lines += [
        "", "---", "",
        f"## Deployment Status",
        "",
        deployment,
        "", "---", "",
        "## Security Observations",
        "",
        security or "None.",
        "", "---", "",
        "## Remaining Blockers",
        "",
    ]

    if blockers:
        lines.append("| Blocker | Severity |")
        lines.append("|---------|----------|")
        for b in blockers:
            if isinstance(b, dict):
                lines.append(f"| {b.get('description','')} | {b.get('severity','?')} |")
            else:
                lines.append(f"| {b} | MEDIUM |")
    else:
        lines.append("No remaining blockers.")

    lines += ["", "---", "", "## Suggested Next Priorities", ""]
    for i, p in enumerate((next_priorities or []), 1):
        if isinstance(p, dict):
            lines.append(f"{i}. **[{p.get('priority','?')}]** {p.get('task','?')}")
            if p.get("detail"):
                lines.append(f"   - {p['detail']}")
        else:
            lines.append(f"{i}. {p}")

    return "\n".join(lines), tag


def save_report(content: str, tag: str, task_slug: str) -> Path:
    safe_slug = "".join(c if c.isalnum() or c in "-_" else "-" for c in task_slug)[:40]
    filename = REPORTS_DIR / f"{tag}-{safe_slug}.md"
    filename.write_text(content)
    return filename


def main():
    if "--interactive" in sys.argv or len(sys.argv) < 2:
        print("JARVIS OPS — Interactive Report Generator")
        task    = input("Task description: ").strip()
        summary = input("Summary (1-2 sentences): ").strip()
        files   = input("Files changed (comma-separated, or blank): ").strip()
        blockers_raw = input("Blockers (comma-separated, or blank): ").strip()
        next_raw     = input("Next priorities (comma-separated, or blank): ").strip()

        files_list    = [f.strip() for f in files.split(",") if f.strip()] if files else []
        blockers_list = [b.strip() for b in blockers_raw.split(",") if b.strip()] if blockers_raw else []
        next_list     = [n.strip() for n in next_raw.split(",") if n.strip()] if next_raw else []
    else:
        task    = ""
        summary = ""
        files_list    = []
        blockers_list = []
        next_list     = []

        for i, arg in enumerate(sys.argv):
            if arg == "--task"     and i+1 < len(sys.argv): task    = sys.argv[i+1]
            if arg == "--summary"  and i+1 < len(sys.argv): summary = sys.argv[i+1]
            if arg == "--files"    and i+1 < len(sys.argv): files_list    = [f.strip() for f in sys.argv[i+1].split(",")]
            if arg == "--blockers" and i+1 < len(sys.argv): blockers_list = [b.strip() for b in sys.argv[i+1].split(",")]
            if arg == "--next"     and i+1 < len(sys.argv): next_list     = [n.strip() for n in sys.argv[i+1].split(",")]

    content, tag = generate_report(
        task=task,
        summary=summary,
        files_changed=files_list,
        blockers=blockers_list,
        next_priorities=next_list,
    )
    out = save_report(content, tag, task or "task")
    print(f"\n[JARVIS OPS] Report saved: {out.relative_to(REPO_ROOT)}")
    print("\n" + "=" * 60)
    print(content)


if __name__ == "__main__":
    main()
