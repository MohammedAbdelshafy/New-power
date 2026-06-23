#!/usr/bin/env bash
# Health-checks all kickback endpoints, updates status, and sends WhatsApp alerts.

set -euo pipefail

REPO="/home/user/New-power"
KICKBACKS="$REPO/.claude/kickback-registry.json"

echo "=== Kickback Health Check ==="

python3 - <<'PYEOF'
import json, urllib.request, urllib.error, datetime, subprocess, sys

KICKBACKS = "/home/user/New-power/.claude/kickback-registry.json"
REPO = "/home/user/New-power"

try:
    d = json.load(open(KICKBACKS))
except Exception as e:
    print(f"Could not read kickback registry: {e}")
    sys.exit(1)

kickbacks = d.get("kickbacks", [])
timestamp = datetime.datetime.utcnow().isoformat() + "Z"
failures = []
recovered = []

if not kickbacks:
    print("No kickbacks registered.")
else:
    for kb in kickbacks:
        name = kb.get("name", "?")
        url = kb.get("health_check_url") or kb.get("endpoint_url", "")
        prev_status = kb.get("status", "unknown")

        if not url:
            print(f"  [SKIP] {name} — no URL configured")
            continue

        try:
            req = urllib.request.urlopen(url, timeout=8)
            code = req.status
            kb["last_status_code"] = code
            kb["last_checked"] = timestamp
            kb["status"] = "healthy"

            if prev_status in ("unreachable", "degraded"):
                recovered.append(name)
                print(f"  [RECOVERED {code}] {name}")
            else:
                print(f"  [OK {code}] {name}")

        except urllib.error.HTTPError as e:
            kb["last_status_code"] = e.code
            kb["last_checked"] = timestamp
            kb["status"] = "degraded"
            failures.append((name, f"HTTP {e.code}"))
            print(f"  [HTTP {e.code}] {name} — DEGRADED")

        except Exception as e:
            kb["last_status_code"] = None
            kb["last_checked"] = timestamp
            kb["status"] = "unreachable"
            failures.append((name, str(e)))
            print(f"  [FAIL] {name} — {e}")

d["last_health_check"] = timestamp
json.dump(d, open(KICKBACKS, "w"), indent=2)

# Send WhatsApp alerts
for name, reason in failures:
    msg = f"KICKBACK DOWN: {name} — {reason}"
    subprocess.run(
        ["bash", f"{REPO}/agent/notify-whatsapp.sh", msg, "kickback_failure"],
        capture_output=True
    )

for name in recovered:
    msg = f"Kickback RECOVERED: {name} is back online."
    subprocess.run(
        ["bash", f"{REPO}/agent/notify-whatsapp.sh", msg, "kickback_recovered"],
        capture_output=True
    )

if failures:
    print(f"\nWARNING: {len(failures)} kickback(s) failing — WhatsApp alert sent.")
    sys.exit(2)
else:
    print("\nAll kickbacks healthy.")
PYEOF
