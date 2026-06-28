#!/usr/bin/env python3
"""
Content Empire — Status Reporter
Reads account registry, campaign milestones, and clip log.
Writes a summary JSON to ops-room so JARVIS OPS can monitor this project.

Usage:
  python3 status-report.py             # print status to terminal
  python3 status-report.py --push      # also write to ops-room/jarvis/project-intel.json
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT    = PROJECT_ROOT.parents[1]
OPS_ROOM     = REPO_ROOT / "ops-room"

REGISTRY_FILE    = PROJECT_ROOT / "accounts" / "registry.json"
MONETIZATION_FILE = PROJECT_ROOT / "campaigns" / "monetization.json"
CLIP_LOG_FILE    = PROJECT_ROOT / "clips" / "process-log.jsonl"
INTEL_FILE       = OPS_ROOM / "jarvis" / "project-intel.json"


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def count_clips_processed() -> int:
    if not CLIP_LOG_FILE.exists():
        return 0
    return sum(1 for line in CLIP_LOG_FILE.read_text().strip().splitlines() if line.strip())


def build_status() -> dict:
    registry = load_json(REGISTRY_FILE)
    monetization = load_json(MONETIZATION_FILE)

    accounts = registry.get("accounts", {})
    yt_accounts  = accounts.get("youtube", [])
    ig_accounts  = accounts.get("instagram", [])
    tt_accounts  = accounts.get("tiktok", [])

    def monetized_count(accs: list, platform: str) -> int:
        if platform == "youtube":
            return sum(1 for a in accs if a.get("monetization", {}).get("adsense_active"))
        elif platform == "instagram":
            return sum(1 for a in accs if a.get("monetization", {}).get("reels_bonus_active"))
        elif platform == "tiktok":
            return sum(1 for a in accs if a.get("monetization", {}).get("creator_rewards_active"))
        return 0

    yt_ready  = monetized_count(yt_accounts, "youtube")
    ig_ready  = monetized_count(ig_accounts, "instagram")
    tt_ready  = monetized_count(tt_accounts, "tiktok")

    total_monetized = yt_ready + ig_ready + tt_ready
    total_accounts  = 15

    pct = int((total_monetized / total_accounts) * 100)

    clips_processed = count_clips_processed()

    return {
        "project_id": "content-empire",
        "name": "Content Empire — 15-Account Viral Machine",
        "last_checked": utcnow(),
        "milestone": "Phase 1 — Account Setup & Daily Posting",
        "milestone_completion_pct": pct,
        "accounts": {
            "youtube": {"total": len(yt_accounts), "monetized": yt_ready},
            "instagram": {"total": len(ig_accounts), "monetized": ig_ready},
            "tiktok": {"total": len(tt_accounts), "monetized": tt_ready},
            "total_monetized": total_monetized,
            "total": total_accounts
        },
        "clips_processed": clips_processed,
        "blockers": [
            {
                "severity": "HIGH",
                "description": f"Instagram accounts need to be created — 5 accounts at setup_needed status"
            } if any(a.get("status") == "setup_needed" for a in ig_accounts) else None,
            {
                "severity": "HIGH",
                "description": f"TikTok accounts need to be created — 5 accounts at setup_needed status"
            } if any(a.get("status") == "setup_needed" for a in tt_accounts) else None,
            {
                "severity": "MEDIUM",
                "description": "YouTube channel handles/URLs not yet added to registry.json"
            } if any(not a.get("handle") for a in yt_accounts) else None,
        ],
        "next_priorities": [
            {
                "priority": "HIGH",
                "task": "Fill in YouTube channel handles and URLs in accounts/registry.json",
                "detail": "Open accounts/registry.json and add your 5 YouTube channel handles and URLs"
            },
            {
                "priority": "HIGH",
                "task": "Create 5 Instagram accounts and 5 TikTok accounts",
                "detail": "Create fresh accounts. Enable Instagram Business/Creator mode. Set up ManyChat immediately on all 5 IG accounts."
            },
            {
                "priority": "HIGH",
                "task": "Start daily posting per schedules/posting-schedule.json",
                "detail": "Target US peak windows: YouTube 7:30 EST + 17:30 EST, Instagram 11:30 EST + 19:30 EST, TikTok 7:00 EST + 12:30 EST + 20:00 EST"
            },
            {
                "priority": "MEDIUM",
                "task": "Add affiliate links to all bio/description fields",
                "detail": "Amazon Associates + AI tool affiliate programs. Zero threshold — starts earning Day 1."
            },
            {
                "priority": "MEDIUM",
                "task": "Set up Later.com or Buffer for scheduled posting",
                "detail": "Connect all accounts. Schedule clips during US peak windows automatically."
            }
        ]
    }


def push_to_ops_room(status: dict):
    """Write content-empire status into project-intel.json so JARVIS OPS sees it."""
    intel = load_json(INTEL_FILE)
    if "projects" not in intel:
        intel["projects"] = {}

    intel["projects"]["content-empire"] = {
        "name": status["name"],
        "milestone": status["milestone"],
        "milestone_completion_pct": status["milestone_completion_pct"],
        "blockers": [b for b in status.get("blockers", []) if b],
        "high_priority_bugs": [],
        "missing_features": [],
        "performance_regressions": [],
        "security_issues": [],
        "documentation_gaps": [],
        "next_priorities": status.get("next_priorities", []),
        "accounts_summary": status.get("accounts", {}),
        "clips_processed": status.get("clips_processed", 0),
        "last_checked": status["last_checked"]
    }
    intel["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    INTEL_FILE.write_text(json.dumps(intel, indent=2))
    print(f"[push] project-intel.json updated — JARVIS OPS can now monitor content-empire")


def main():
    parser = argparse.ArgumentParser(description="Content Empire Status Reporter")
    parser.add_argument("--push", action="store_true", help="Push status to ops-room project-intel.json")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    status = build_status()

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  CONTENT EMPIRE STATUS")
        print(f"{'='*55}")
        print(f"  Milestone: {status['milestone']}")
        print(f"  Progress:  {status['milestone_completion_pct']}%")
        print(f"  Accounts:  {status['accounts']['total_monetized']}/15 monetized")
        print(f"             YT {status['accounts']['youtube']['monetized']}/5  "
              f"IG {status['accounts']['instagram']['monetized']}/5  "
              f"TT {status['accounts']['tiktok']['monetized']}/5")
        print(f"  Clips Processed: {status['clips_processed']}")
        print()

        blockers = [b for b in status.get("blockers", []) if b]
        if blockers:
            print("  BLOCKERS:")
            for b in blockers:
                print(f"    [{b['severity']}] {b['description']}")
            print()

        print("  NEXT PRIORITIES:")
        for p in status.get("next_priorities", [])[:3]:
            print(f"    [{p['priority']}] {p['task']}")
        print(f"{'='*55}\n")

    if args.push:
        push_to_ops_room(status)


if __name__ == "__main__":
    main()
