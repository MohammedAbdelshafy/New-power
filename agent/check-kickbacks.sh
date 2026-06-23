#!/usr/bin/env bash
# Health-checks all registered kickback endpoints and updates their status.

set -euo pipefail

REPO="/home/user/New-power"
KICKBACKS="$REPO/.claude/kickback-registry.json"

echo "=== Kickback Health Check ==="

python3 - <<'PYEOF'
import json, urllib.request, urllib.error, datetime

KICKBACKS = "/home/user/New-power/.claude/kickback-registry.json"

try:
    d = json.load(open(KICKBACKS))
except Exception as e:
    print(f"Could not read kickback registry: {e}")
    exit(1)

kickbacks = d.get("kickbacks", [])
timestamp = datetime.datetime.utcnow().isoformat() + "Z"
all_ok = True

if not kickbacks:
    print("No kickbacks registered.")
else:
    for kb in kickbacks:
        name = kb.get("name", "?")
        url = kb.get("health_check_url") or kb.get("endpoint_url", "")
        if not url:
            print(f"  [SKIP] {name} — no URL")
            continue
        try:
            req = urllib.request.urlopen(url, timeout=8)
            code = req.status
            kb["last_status_code"] = code
            kb["last_checked"] = timestamp
            kb["status"] = "healthy"
            print(f"  [OK {code}] {name}")
        except urllib.error.HTTPError as e:
            kb["last_status_code"] = e.code
            kb["last_checked"] = timestamp
            kb["status"] = "degraded"
            all_ok = False
            print(f"  [HTTP {e.code}] {name} — DEGRADED")
        except Exception as e:
            kb["last_status_code"] = None
            kb["last_checked"] = timestamp
            kb["status"] = "unreachable"
            all_ok = False
            print(f"  [FAIL] {name} — {e}")

d["last_health_check"] = timestamp
json.dump(d, open(KICKBACKS, "w"), indent=2)

if not all_ok:
    print("\nWARNING: Some kickbacks are failing — investigate before proceeding.")
    exit(2)
else:
    print("\nAll kickbacks healthy.")
PYEOF
