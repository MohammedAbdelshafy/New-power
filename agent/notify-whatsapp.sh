#!/usr/bin/env bash
# Sends a WhatsApp message via Green API.
# If the direct call is blocked (proxy restriction), queues the message
# in .claude/notification-queue.json for delivery via GitHub Actions.

set -euo pipefail

REPO="/home/user/New-power"
CONFIG="$REPO/.claude/whatsapp-config.json"
QUEUE="$REPO/.claude/notification-queue.json"
LOG="$REPO/.claude/whatsapp-log.json"

MESSAGE="${1:-}"
EVENT_TYPE="${2:-}"

[ -z "$MESSAGE" ] && { echo "[WhatsApp] No message." >&2; exit 1; }

python3 - <<PYEOF
import json, urllib.request, urllib.error, urllib.parse, datetime, sys, os

CONFIG     = "$CONFIG"
QUEUE_FILE = "$QUEUE"
LOG_FILE   = "$LOG"
MESSAGE    = """$MESSAGE"""
EVENT_TYPE = "$EVENT_TYPE"

try:
    cfg = json.load(open(CONFIG))
except Exception as e:
    print(f"[WhatsApp] Cannot read config: {e}", file=sys.stderr); sys.exit(0)

if not cfg.get("enabled", False):
    print("[WhatsApp] Notifications disabled.")
    sys.exit(0)

notify_on = cfg.get("notify_on", {})
if EVENT_TYPE and not notify_on.get(EVENT_TYPE, True):
    sys.exit(0)

phone     = cfg.get("phone","").strip().lstrip("+")
instance  = cfg.get("instance_id","").strip()
api_token = cfg.get("api_token","").strip()

if not phone or not instance or not api_token:
    print("[WhatsApp] Missing credentials.", file=sys.stderr); sys.exit(1)

chat_id      = f"{phone}@c.us"
full_message = f"[New-Power] {MESSAGE}"
timestamp    = datetime.datetime.utcnow().isoformat() + "Z"

url     = f"https://api.green-api.com/waInstance{instance}/sendMessage/{api_token}"
payload = json.dumps({"chatId": chat_id, "message": full_message}).encode("utf-8")
req     = urllib.request.Request(url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST")

success = False
error_msg = None

try:
    resp = urllib.request.urlopen(req, timeout=15)
    print(f"[WhatsApp] Sent (HTTP {resp.status}): {full_message[:80]}")
    success = True
except Exception as e:
    error_msg = str(e)
    print(f"[WhatsApp] Direct send failed ({e}). Queuing for GitHub Actions delivery.")

# --- Queue for GitHub Actions if direct send failed ---
if not success:
    try:
        try:
            q = json.load(open(QUEUE_FILE))
        except Exception:
            q = {"messages": []}
        q["messages"].append({
            "timestamp":  timestamp,
            "event":      EVENT_TYPE or "manual",
            "text":       full_message,
        })
        q["messages"] = q["messages"][-50:]   # keep last 50
        json.dump(q, open(QUEUE_FILE, "w"), indent=2)
        print(f"[WhatsApp] Queued. Will be sent via GitHub Actions on next push.")
    except Exception as qe:
        print(f"[WhatsApp] Queue write failed: {qe}", file=sys.stderr)

# --- Append to local log ---
try:
    try:
        log = json.load(open(LOG_FILE))
    except Exception:
        log = {"messages": []}
    log["messages"].append({
        "timestamp": timestamp,
        "event":     EVENT_TYPE or "manual",
        "message":   full_message,
        "success":   success,
        "error":     error_msg,
    })
    log["messages"] = log["messages"][-200:]
    json.dump(log, open(LOG_FILE, "w"), indent=2)
except Exception:
    pass

if not success:
    sys.exit(2)
PYEOF
