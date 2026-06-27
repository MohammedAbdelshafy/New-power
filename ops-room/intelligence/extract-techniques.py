#!/usr/bin/env python3
"""
Technique Extractor — deeper pass on a queued analysis file.
Takes a queue JSON file path and produces a ranked technique brief
optimized for direct implementation in sessions/projects.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parents[2]


def rank_techniques(analysis: dict) -> list:
    """Score and rank all detected techniques by implementation impact."""
    ranked = []
    tasks = analysis.get("implementation_tasks", [])

    priority_score = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    for task in tasks:
        ranked.append({
            "score": priority_score.get(task.get("priority", "LOW"), 1),
            "task": task["task"],
            "detail": task["detail"],
            "priority": task.get("priority", "LOW"),
        })

    # Add structural techniques as LOW-scored items
    for t in analysis.get("structural_techniques", []):
        ranked.append({
            "score": 1,
            "task": f"Structural pattern: {t}",
            "detail": "Replicate this structural element in your content.",
            "priority": "LOW",
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


def generate_session_patch(meta: dict, ranked: list) -> str:
    """Generate a CLAUDE.md patch snippet for the target session."""
    title = meta.get("metadata", {}).get("title", "Unknown content")
    url = meta.get("url", "")
    platform = meta.get("platform", "")

    lines = [
        f"\n## Viral Technique Import — {platform.title()}",
        f"Source: [{title}]({url})",
        f"Imported: {datetime.utcnow().strftime('%Y-%m-%d')}",
        "",
        "### Priority Implementation Tasks",
    ]
    for item in ranked[:5]:
        lines.append(f"- **[{item['priority']}]** {item['task']}")
        lines.append(f"  - {item['detail']}")

    hooks = meta.get("analysis", {}).get("hooks_detected", [])
    if hooks:
        lines.append("\n### Hook Templates to Apply")
        for h in hooks:
            lines.append(f"- {h}")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        # Find the most recent queued file
        queue_dir = REPO_ROOT / "ops-room" / "operations" / "queue"
        files = sorted(queue_dir.glob("*.json"), reverse=True)
        if not files:
            print("No queued analyses found. Run analyze-content.py first.")
            sys.exit(1)
        target = files[0]
        print(f"[extract] Using most recent: {target.name}")
    else:
        target = Path(sys.argv[1])

    data = json.loads(target.read_text())
    ranked = rank_techniques(data.get("analysis", {}))
    patch = generate_session_patch(data, ranked)

    print("\n=== RANKED IMPLEMENTATION BRIEF ===")
    for i, item in enumerate(ranked, 1):
        print(f"\n{i}. [{item['priority']}] {item['task']}")
        print(f"   {item['detail']}")

    print("\n=== CLAUDE.md PATCH SNIPPET ===")
    print(patch)

    # Save the patch
    patch_dir = REPO_ROOT / "ops-room" / "operations" / "queue"
    patch_file = patch_dir / (target.stem + "-patch.md")
    patch_file.write_text(patch)
    print(f"\nPatch saved to: {patch_file.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
