#!/usr/bin/env python3
"""
JARVIS OPS — Notification Sender
Sends alerts and reports to configured channels (Discord, Slack, Email).
Usage: python3 notify.py --event <event_type> --message "text" [--title "title"]
       python3 notify.py --test discord
       python3 notify.py --test slack

Events: build_failure, deployment, critical_alert, daily_report, weekly_report,
        pr_merged, ci_failure, security_alert, custom
"""

import sys
import json
import urllib.request
import urllib.parse
import os
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT    = Path(__file__).resolve().parents[2]
CHANNELS_CFG = REPO_ROOT / "ops-room" / "comms" / "channels.json"

def load_channels() -> dict:
    if not CHANNELS_CFG.exists():
        return {}
    return json.loads(CHANNELS_CFG.read_text()).get("channels", {})

def load_rules() -> dict:
    if not CHANNELS_CFG.exists():
        return {}
    return json.loads(CHANNELS_CFG.read_text()).get("notification_rules", {})

def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# ── Discord ────────────────────────────────────────────────────────────────────

def send_discord(webhook_url: str, title: str, message: str, event: str, color: int = 0x7C3AED) -> bool:
    payload = json.dumps({
        "embeds": [{
            "title": f"JARVIS OPS | {title}",
            "description": message,
            "color": color,
            "footer": {"text": f"Event: {event} • {utcnow()}"},
            "thumbnail": {"url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"}
        }]
    }).encode()

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204)
    except Exception as e:
        print(f"[discord] Error: {e}")
        return False


# ── Slack ──────────────────────────────────────────────────────────────────────

def send_slack(webhook_url: str, title: str, message: str, event: str) -> bool:
    icon = {
        "critical_alert":  ":rotating_light:",
        "build_failure":   ":x:",
        "deployment":      ":rocket:",
        "pr_merged":       ":white_check_mark:",
        "ci_failure":      ":warning:",
        "daily_report":    ":bar_chart:",
        "weekly_report":   ":calendar:",
        "security_alert":  ":lock:",
    }.get(event, ":robot_face:")

    payload = json.dumps({
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{icon} JARVIS OPS | {title}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            },
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Event: `{event}` • {utcnow()}"}]
            }
        ]
    }).encode()

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[slack] Error: {e}")
        return False


# ── Email (SendGrid) ───────────────────────────────────────────────────────────

def send_email(api_key: str, from_addr: str, to_addr: str, title: str, message: str) -> bool:
    payload = json.dumps({
        "personalizations": [{"to": [{"email": to_addr}]}],
        "from": {"email": from_addr, "name": "JARVIS OPS"},
        "subject": f"JARVIS OPS | {title}",
        "content": [
            {"type": "text/plain", "value": message},
            {"type": "text/html",  "value": f"<pre style='font-family:monospace'>{message}</pre>"}
        ]
    }).encode()

    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 202
    except Exception as e:
        print(f"[email] Error: {e}")
        return False


# ── Router ─────────────────────────────────────────────────────────────────────

def route_event(event: str, title: str, message: str) -> dict:
    channels = load_channels()
    rules    = load_rules()
    results  = {}

    target_channels = rules.get(event, [])
    if target_channels == "all enabled channels":
        target_channels = list(channels.keys())

    for ch_name in target_channels:
        ch = channels.get(ch_name, {})
        if not ch.get("enabled"):
            results[ch_name] = "skipped (disabled)"
            continue

        if ch_name == "discord":
            color = 0xEF4444 if "critical" in event or "failure" in event else 0x22C55E
            ok = send_discord(ch["webhook_url"], title, message, event, color)
            results["discord"] = "sent" if ok else "failed"

        elif ch_name == "slack":
            ok = send_slack(ch["webhook_url"], title, message, event)
            results["slack"] = "sent" if ok else "failed"

        elif ch_name == "email":
            api_key = ch.get("api_key") or os.environ.get("SENDGRID_API_KEY", "")
            if not api_key:
                results["email"] = "skipped (no api_key)"
                continue
            ok = send_email(api_key, ch["from"], ch["to"], title, message)
            results["email"] = "sent" if ok else "failed"

        else:
            results[ch_name] = f"skipped (handler not implemented)"

    return results


def test_channel(channel_name: str) -> None:
    channels = load_channels()
    ch = channels.get(channel_name, {})

    if not ch:
        print(f"[notify] Channel '{channel_name}' not found in channels.json")
        return

    if not ch.get("enabled"):
        print(f"[notify] Channel '{channel_name}' is DISABLED.")
        print(f"  Set enabled: true in ops-room/comms/channels.json and add webhook_url.")
        return

    print(f"[notify] Sending test message to {channel_name}...")
    results = route_event(
        event="custom",
        title="Test Notification",
        message=f"JARVIS OPS comms test. If you see this, {channel_name} is working correctly.\nTimestamp: {utcnow()}"
    )
    print(f"[notify] Result: {results}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if "--test" in sys.argv:
        idx = sys.argv.index("--test")
        channel = sys.argv[idx+1] if idx+1 < len(sys.argv) else "discord"
        test_channel(channel)
        return

    event   = "custom"
    title   = "JARVIS OPS Notification"
    message = ""

    for i, arg in enumerate(sys.argv):
        if arg == "--event"   and i+1 < len(sys.argv): event   = sys.argv[i+1]
        if arg == "--title"   and i+1 < len(sys.argv): title   = sys.argv[i+1]
        if arg == "--message" and i+1 < len(sys.argv): message = sys.argv[i+1]

    if not message:
        print("[notify] --message is required")
        sys.exit(1)

    results = route_event(event, title, message)
    print(f"[notify] Dispatch results: {json.dumps(results, indent=2)}")

    # Log it
    log_dir  = REPO_ROOT / "ops-room" / "comms"
    log_file = log_dir / "send-log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps({
            "sent_at": utcnow(),
            "event":   event,
            "title":   title,
            "message": message[:200],
            "results": results
        }) + "\n")


if __name__ == "__main__":
    main()
