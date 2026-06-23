#!/usr/bin/env bash
# Usage: bash agent/notify-whatsapp.sh "Your message" [event_type]
# Sends via Green API (https://green-api.com)

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

python3 - <<PYEOF
import json, urllib.request, urllib.error, urllib.parse, datetime, sys

CONFIG = "$CONFIG"
LOG_FILE = "$LOG"
MESSAGE = """$MESSAGE"""
EVENT_TYPE = "$EVENT_TYPE"

try:
    cfg = json.load(open(CONFIG))
except Exception as e:
    print(f"[WhatsApp] Cannot read config: {e}", file=sys.stderr)
    sys.exit(1)

if not cfg.get("enabled", False):
    print("[WhatsApp] Notifications disabled. Set up credentials and set 'enabled': true in .claude/whatsapp-config.json")
    sys.exit(0)

notify_on = cfg.get("notify_on", {})
if EVENT_TYPE and not notify_on.get(EVENT_TYPE, True):
    sys.exit(0)

phone      = cfg.get("phone", "").strip().lstrip("+")
instance   = cfg.get("instance_id", "").strip()
api_token  = cfg.get("api_token", "").strip()

if not phone or not instance or not api_token:
    print("[WhatsApp] ERROR: phone, instance_id, and api_token must be set in .claude/whatsapp-config.json", file=sys.stderr)
    sys.exit(1)

# Green API chatId format: {phone}@c.us  (no + prefix)
chat_id = f"{phone}@c.us"
full_message = f"[New-Power] {MESSAGE}"
timestamp = datetime.datetime.utcnow().isoformat() + "Z"

url = f"https://api.green-api.com/waInstance{instance}/sendMessage/{api_token}"
payload = json.dumps({"chatId": chat_id, "message": full_message}).encode("utf-8")

req = urllib.request.Request(
    url,
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST"
)

success = False
status = None
error_msg = None

try:
    resp = urllib.request.urlopen(req, timeout=15)
    body = resp.read().decode("utf-8", errors="replace")
    status = resp.status
    print(f"[WhatsApp] Sent (HTTP {status}): {full_message[:80]}")
    success = True
except urllib.error.HTTPError as e:
    body = e.read().decode("utf-8", errors="replace")
    status = e.code
    error_msg = f"HTTP {status}: {body[:200]}"
    print(f"[WhatsApp] Error {status}: {body[:200]}", file=sys.stderr)
except Exception as e:
    error_msg = str(e)
    print(f"[WhatsApp] Failed: {e}", file=sys.stderr)

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
    log["messages"] = log["messages"][-200:]
    json.dump(log, open(LOG_FILE, "w"), indent=2)
except Exception:
    pass

if not success:
    sys.exit(1)
PYEOF
