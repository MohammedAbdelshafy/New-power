#!/usr/bin/env bash
# clone-and-map.sh — Clone a repo and build a feature/structure map.
# Usage: ./clone-and-map.sh <repo-url> [--depth <n>]
#
# Outputs: a JSON feature map saved to ops-room/operations/queue/

set -euo pipefail

REPO_URL="${1:-}"
DEPTH="${3:-1}"

if [[ -z "$REPO_URL" ]]; then
  echo "Usage: $0 <repo-url> [--depth <n>]"
  exit 1
fi

REPO_NAME=$(basename "$REPO_URL" .git)
CLONE_DIR="/tmp/ops-room-clone-$REPO_NAME"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "$(dirname "$0")/../..")"
QUEUE_DIR="$REPO_ROOT/ops-room/operations/queue"
mkdir -p "$QUEUE_DIR"

echo "[ops-room] Cloning $REPO_URL (depth=$DEPTH)..."
rm -rf "$CLONE_DIR"
git clone --depth "$DEPTH" --quiet "$REPO_URL" "$CLONE_DIR"

echo "[ops-room] Building feature map..."

python3 - "$CLONE_DIR" "$REPO_URL" "$QUEUE_DIR" "$REPO_NAME" <<'PYEOF'
import sys, json, os
from pathlib import Path
from datetime import datetime

clone_dir = Path(sys.argv[1])
repo_url  = sys.argv[2]
queue_dir = Path(sys.argv[3])
repo_name = sys.argv[4]

# File type categories
CATEGORIES = {
    "frontend":  [".html", ".css", ".scss", ".jsx", ".tsx", ".vue", ".svelte"],
    "backend":   [".py", ".js", ".ts", ".go", ".rb", ".php", ".java", ".rs", ".cs"],
    "config":    [".json", ".yaml", ".yml", ".toml", ".env.example", ".ini"],
    "docs":      [".md", ".rst", ".txt"],
    "infra":     ["Dockerfile", ".dockerignore", "docker-compose.yml", ".github/workflows"],
    "data":      [".sql", ".csv", ".parquet"],
    "tests":     ["test_", "_test.", ".spec.", "_spec."],
}

file_map = {}
tech_stack = set()
key_files = []

for f in clone_dir.rglob("*"):
    if f.is_file() and ".git" not in str(f):
        rel = str(f.relative_to(clone_dir))
        size = f.stat().st_size
        ext = f.suffix.lower()
        name = f.name

        # Categorize
        cat = "other"
        for c, patterns in CATEGORIES.items():
            if any(rel.endswith(p) or p in rel for p in patterns):
                cat = c
                break

        file_map.setdefault(cat, []).append({"path": rel, "size_bytes": size})

        # Detect tech stack
        if ext == ".py": tech_stack.add("Python")
        elif ext in (".js", ".jsx"): tech_stack.add("JavaScript")
        elif ext in (".ts", ".tsx"): tech_stack.add("TypeScript")
        elif ext == ".go": tech_stack.add("Go")
        elif ext == ".rs": tech_stack.add("Rust")
        elif ext == ".rb": tech_stack.add("Ruby")
        elif ext == ".vue": tech_stack.add("Vue.js")
        elif ext == ".svelte": tech_stack.add("Svelte")
        elif name == "Dockerfile": tech_stack.add("Docker")
        elif name == "docker-compose.yml": tech_stack.add("Docker Compose")

        # Key files
        if name.lower() in ("readme.md", "package.json", "pyproject.toml",
                             "requirements.txt", "setup.py", "cargo.toml",
                             "go.mod", "gemfile", "pom.xml"):
            try:
                content = f.read_text(errors="ignore")[:1000]
            except:
                content = ""
            key_files.append({"file": rel, "preview": content})

# Summary stats
total_files = sum(len(v) for v in file_map.values())
largest_files = sorted(
    [{"path": item["path"], "size_bytes": item["size_bytes"]}
     for items in file_map.values() for item in items],
    key=lambda x: x["size_bytes"], reverse=True
)[:10]

# Read README for description
readme_content = ""
for candidate in ["README.md", "readme.md", "README.rst", "README"]:
    p = clone_dir / candidate
    if p.exists():
        readme_content = p.read_text(errors="ignore")[:3000]
        break

report = {
    "repo_url": repo_url,
    "repo_name": repo_name,
    "analyzed_at": datetime.utcnow().isoformat(),
    "status": "queued",
    "summary": {
        "total_files": total_files,
        "tech_stack": sorted(tech_stack),
        "categories": {k: len(v) for k, v in file_map.items()},
        "largest_files": largest_files,
    },
    "readme_preview": readme_content,
    "key_files": key_files,
    "file_map": {k: v[:50] for k, v in file_map.items()},  # cap per category
    "implementation_tasks": [
        {
            "priority": "HIGH",
            "task": f"Study {repo_name} architecture",
            "detail": f"Tech stack: {', '.join(sorted(tech_stack))}. Review key files and adapt patterns.",
        },
        {
            "priority": "MEDIUM",
            "task": "Extract reusable components / patterns",
            "detail": f"Focus on {', '.join(list(file_map.keys())[:3])} directories for reusable logic.",
        },
    ],
}

ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
out = queue_dir / f"{ts}-repo-{repo_name}.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False))

print(f"\n[ops-room] Feature map saved to: {out}")
print(f"\n=== REPO SUMMARY: {repo_name} ===")
print(f"  Tech stack: {', '.join(sorted(tech_stack)) or 'unknown'}")
print(f"  Total files: {total_files}")
for cat, count in sorted(report['summary']['categories'].items(), key=lambda x: -x[1]):
    print(f"    {cat:<12}: {count} files")
print(f"\n  README preview:\n  {readme_content[:300].replace(chr(10), chr(10)+'  ')}")
PYEOF

echo ""
echo "[ops-room] Clone directory retained at: $CLONE_DIR"
echo "           Remove when done: rm -rf $CLONE_DIR"
