#!/usr/bin/env bash
# Usage: bash agent/notify-whatsapp.sh "Your message here" [event_type]
# event_type: session_start | session_stop | kickback_failure | kickback_recovered
#             task_complete | task_blocked | project_complete | (omit for always-send)

set -euo pipefail

REPO="/home/user/New-power"
CONFIG="$REPO/.claude/whatsapp-config.json"
LOG="$REPO/.claude/whatsapp-log.json"

MESSAGE="${1:-}"
EVENT_TYPE="${2:-}"

if [ -z "$MESSAGE" ]; then
  echo "[WhatsApp] No message provided." >&2
  exit 1
fi

if [ ! -f "$CONFIG" ]; then
  echo "[WhatsApp] Config not found at $CONFIG" >&2
  exit 1
fi

python3 - <<PYEOF
import json, urllib.request, urllib.parse, urllib.error, datetime, sys, os

CONFIG = "$CONFIG"
LOG_FILE = "$LOG"
MESSAGE = """$MESSAGE"""
EVENT_TYPE = "$EVENT_TYPE"

try:
    cfg = json.load(open(CONFIG))
except Exception as e:
    print(f"[WhatsApp] Cannot read config: {e}", file=sys.stderr)
    sys.exit(1)

enabled = cfg.get("enabled", False)
if not enabled:
    print("[WhatsApp] Notifications disabled. Set 'enabled': true in .claude/whatsapp-config.json")
    sys.exit(0)

# Check if this event type is enabled
notify_on = cfg.get("notify_on", {})
if EVENT_TYPE and not notify_on.get(EVENT_TYPE, True):
    print(f"[WhatsApp] Event '{EVENT_TYPE}' notifications are off in config.")
    sys.exit(0)

phone = cfg.get("phone", "").strip()
apikey = cfg.get("apikey", "").strip()

if not phone or not apikey:
    print("[WhatsApp] ERROR: phone and apikey must be set in .claude/whatsapp-config.json", file=sys.stderr)
    sys.exit(1)

# Prefix every message with the project name
full_message = f"[New-Power] {MESSAGE}"
timestamp = datetime.datetime.utcnow().isoformat() + "Z"

url = (
    "https://api.callmebot.com/whatsapp.php?"
    + urllib.parse.urlencode({
        "phone": phone,
        "text": full_message,
        "apikey": apikey
    })
)

try:
    req = urllib.request.urlopen(url, timeout=15)
    body = req.read().decode("utf-8", errors="replace")
    status = req.status
    print(f"[WhatsApp] Sent (HTTP {status}): {full_message[:80]}")
    success = True
    error_msg = None
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    status = e.code
    print(f"[WhatsApp] HTTP {status} error: {body[:200]}", file=sys.stderr)
    success = False
    error_msg = f"HTTP {status}: {body[:200]}"
except Exception as e:
    status = None
    body = str(e)
    print(f"[WhatsApp] Failed to send: {e}", file=sys.stderr)
    success = False
    error_msg = str(e)

# Append to log
try:
    try:
        log = json.load(open(LOG_FILE))
    except Exception:
        log = {"messages": []}
    log["messages"].append({
        "timestamp": timestamp,
        "event": EVENT_TYPE or "manual",
        "message": full_message,
        "success": success,
        "status_code": status,
        "error": error_msg
    })
    # Keep last 200 entries
    log["messages"] = log["messages"][-200:]
    json.dump(log, open(LOG_FILE, "w"), indent=2)
except Exception:
    pass

if not success:
    sys.exit(1)
PYEOF
