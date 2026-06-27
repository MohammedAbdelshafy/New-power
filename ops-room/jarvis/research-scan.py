#!/usr/bin/env python3
"""
JARVIS OPS — AI Research Scanner
Searches GitHub for high-value repos in AI, automation, and developer tooling.
Logs discoveries to jarvis/research/discoveries.json.
Usage: python3 research-scan.py [--query "search term"] [--min-stars 500]
"""

import sys
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT  = Path(__file__).resolve().parents[2]
RESEARCH_FILE = REPO_ROOT / "ops-room" / "jarvis" / "research" / "discoveries.json"

RESEARCH_CATEGORIES = [
    {"query": "AI agent framework",           "category": "Agent Framework",       "min_stars": 1000},
    {"query": "MCP server tools",             "category": "MCP / Tooling",          "min_stars": 200},
    {"query": "code automation AI",           "category": "Code Automation",        "min_stars": 500},
    {"query": "open source LLM deployment",   "category": "LLM Infrastructure",     "min_stars": 1000},
    {"query": "developer productivity AI",    "category": "Developer Tooling",      "min_stars": 500},
    {"query": "automated testing AI",         "category": "Testing Frameworks",     "min_stars": 300},
    {"query": "security scanning automation", "category": "Security Tools",         "min_stars": 300},
    {"query": "CI CD automation github",      "category": "CI/CD",                  "min_stars": 500},
]

def load_existing() -> dict:
    if RESEARCH_FILE.exists():
        return json.loads(RESEARCH_FILE.read_text())
    return {"last_scan": None, "discoveries": []}

def already_tracked(existing: dict, repo_url: str) -> bool:
    return any(d.get("source_url") == repo_url for d in existing.get("discoveries", []))

def search_github(query: str, min_stars: int, limit: int = 5) -> list:
    """Search GitHub via REST API — no gh CLI required."""
    import urllib.request
    import urllib.parse

    q = urllib.parse.quote(f"{query} stars:>={min_stars}")
    url = f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page={limit}"

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "jarvis-ops-research"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
            items = data.get("items", [])
            return [
                {
                    "fullName":       r.get("full_name"),
                    "description":    r.get("description", ""),
                    "stargazersCount": r.get("stargazers_count", 0),
                    "url":            r.get("html_url"),
                    "language":       r.get("language"),
                    "updatedAt":      r.get("updated_at"),
                    "licenseInfo":    {"name": (r.get("license") or {}).get("name", "unknown")},
                }
                for r in items
            ]
    except Exception as e:
        print(f"  [warn] GitHub API error: {e}")
        return []

def evaluate_risk(repo: dict) -> str:
    license_info = repo.get("licenseInfo") or {}
    license_name = license_info.get("name", "").lower() if isinstance(license_info, dict) else ""
    if "mit" in license_name or "apache" in license_name or "bsd" in license_name:
        return "low — permissive license"
    if "gpl" in license_name:
        return "medium — GPL copyleft, check compatibility"
    if not license_name:
        return "medium — no license detected, inspect before use"
    return f"low — {license_name}"

def estimate_effort(repo: dict) -> str:
    stars = repo.get("stargazersCount", 0)
    if stars > 10000:
        return "medium — mature project, likely well-documented"
    if stars > 2000:
        return "low-medium — decent adoption, evaluate API stability"
    return "medium — smaller project, audit code quality first"

def scan(custom_queries=None, min_stars_override=None) -> list:
    existing = load_existing()
    new_discoveries = []

    queries = custom_queries if custom_queries else RESEARCH_CATEGORIES

    for cat in queries:
        query     = cat["query"] if isinstance(cat, dict) else cat
        category  = cat.get("category", "General") if isinstance(cat, dict) else "General"
        min_stars = min_stars_override or (cat.get("min_stars", 500) if isinstance(cat, dict) else 500)

        print(f"[research] Scanning: {query} (min ⭐{min_stars})")
        repos = search_github(query, min_stars)

        for repo in repos:
            url = repo.get("url", "")
            if already_tracked(existing, url):
                continue

            disc_id = hashlib.md5(url.encode()).hexdigest()[:8]
            entry = {
                "id":                disc_id,
                "name":              repo.get("fullName", "?"),
                "category":          category,
                "status":            "discovered",
                "source_url":        url,
                "stars":             repo.get("stargazersCount", 0),
                "language":          repo.get("language", "?"),
                "license":           (repo.get("licenseInfo") or {}).get("name", "unknown") if isinstance(repo.get("licenseInfo"), dict) else "unknown",
                "why_it_matters":    f"Highly starred ({repo.get('stargazersCount',0)}⭐) repo in {category}. {repo.get('description','')[:120]}",
                "benefits":          [f"Active community ({repo.get('stargazersCount',0)} stars)", "Open source"],
                "risks":             [evaluate_risk(repo)],
                "integration_effort": estimate_effort(repo),
                "owner_approved":    False,
                "discovered_at":     datetime.now(timezone.utc).isoformat(),
                "description":       repo.get("description", ""),
            }
            new_discoveries.append(entry)
            print(f"  + DISCOVERED: {entry['name']} ({entry['stars']}⭐) — {entry['category']}")

    # Save
    existing["discoveries"].extend(new_discoveries)
    existing["last_scan"] = datetime.now(timezone.utc).isoformat()
    RESEARCH_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    return new_discoveries


def main():
    custom_query = None
    min_stars    = None

    if "--query" in sys.argv:
        idx = sys.argv.index("--query")
        custom_query = [{"query": sys.argv[idx+1], "category": "Custom Search", "min_stars": 100}]

    if "--min-stars" in sys.argv:
        idx = sys.argv.index("--min-stars")
        min_stars = int(sys.argv[idx+1])

    print("[JARVIS OPS] Starting AI Research Scan...")
    discovered = scan(custom_query, min_stars)

    print(f"\n[research] Scan complete. {len(discovered)} new discoveries.")
    if discovered:
        print("\n=== NEW DISCOVERIES ===")
        for d in discovered:
            print(f"\n  [{d['category']}] {d['name']} ({d['stars']}⭐)")
            print(f"  {d['description'][:100]}")
            print(f"  Risks: {', '.join(d['risks'])}")
            print(f"  Effort: {d['integration_effort']}")
        print(f"\nFull log: {RESEARCH_FILE.relative_to(REPO_ROOT)}")
    else:
        print("  No new discoveries (all results already tracked).")


if __name__ == "__main__":
    main()
