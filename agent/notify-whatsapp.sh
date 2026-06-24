#!/usr/bin/env bash
# Queues a WhatsApp notification for delivery via GitHub Actions.
# Direct send is not used — the proxy in this environment blocks api.green-api.com.
# GitHub Actions (whatsapp-notify.yml) reads the queue on each push and delivers.
#
# Usage: bash agent/notify-whatsapp.sh "message text" [event_type]

REPO="/home/user/New-power"
CONFIG="$REPO/.claude/whatsapp-config.json"
QUEUE="$REPO/.claude/notification-queue.json"
LOG="$REPO/.claude/whatsapp-log.json"

MESSAGE="${1:-}"
EVENT_TYPE="${2:-}"

[ -z "$MESSAGE" ] && { echo "[WhatsApp] No message provided." >&2; exit 1; }

python3 - <<PYEOF
import json, datetime, sys

CONFIG     = "$CONFIG"
QUEUE_FILE = "$QUEUE"
LOG_FILE   = "$LOG"
MESSAGE    = """$MESSAGE"""
EVENT_TYPE = "$EVENT_TYPE"

# Check config
try:
    cfg = json.load(open(CONFIG))
except Exception:
    # No config — create a default enabled one
    cfg = {"enabled": True, "notify_on": {}}

if not cfg.get("enabled", True):
    print("[WhatsApp] Notifications disabled in config.")
    sys.exit(0)

notify_on = cfg.get("notify_on", {})
if EVENT_TYPE and not notify_on.get(EVENT_TYPE, True):
    sys.exit(0)

full_message = f"[New-Power] {MESSAGE}"
timestamp    = datetime.datetime.utcnow().isoformat() + "Z"

# Always queue — delivery is via GitHub Actions
try:
    try:
        q = json.load(open(QUEUE_FILE))
    except Exception:
        q = {"messages": []}

    q["messages"].append({
        "timestamp": timestamp,
        "event":     EVENT_TYPE or "manual",
        "text":      full_message,
    })
    q["messages"] = q["messages"][-100:]
    json.dump(q, open(QUEUE_FILE, "w"), indent=2)
    print(f"[WhatsApp] Queued: {full_message[:80]}")
except Exception as e:
    print(f"[WhatsApp] Queue write failed: {e}", file=sys.stderr)
    sys.exit(1)

# Log
try:
    try:
        log = json.load(open(LOG_FILE))
    except Exception:
        log = {"messages": []}
    log["messages"].append({
        "timestamp": timestamp,
        "event":     EVENT_TYPE or "manual",
        "message":   full_message,
        "queued":    True,
    })
    log["messages"] = log["messages"][-200:]
    json.dump(log, open(LOG_FILE, "w"), indent=2)
except Exception:
    pass
PYEOF
