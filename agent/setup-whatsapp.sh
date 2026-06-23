#!/usr/bin/env bash
# Interactive setup for Green API WhatsApp notifications.

set -euo pipefail

REPO="/home/user/New-power"
CONFIG="$REPO/.claude/whatsapp-config.json"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   WhatsApp Notification Setup (Green API)        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "STEP 1 — Create a free Green API account:"
echo "  https://console.green-api.com"
echo ""
echo "STEP 2 — Create a new instance (choose Developer / free plan)"
echo ""
echo "STEP 3 — From the instance dashboard, copy:"
echo "  • Instance ID  (a number like 1101234567)"
echo "  • API Token    (a long string)"
echo ""
echo "STEP 4 — Click 'Scan QR code' and scan with WhatsApp on your phone"
echo ""

read -rp "Press ENTER once your instance is active and QR is scanned... "
echo ""

read -rp "Enter your WhatsApp phone number (e.g. +201001234567): " PHONE
read -rp "Enter your Green API Instance ID: " INSTANCE_ID
read -rp "Enter your Green API API Token: " API_TOKEN

if [ -z "$PHONE" ] || [ -z "$INSTANCE_ID" ] || [ -z "$API_TOKEN" ]; then
  echo "All fields are required. Aborting."
  exit 1
fi

python3 - <<PYEOF
import json

CONFIG = "$CONFIG"
try:
    d = json.load(open(CONFIG))
except Exception:
    d = {}

d["provider"]     = "greenapi"
d["phone"]        = "$PHONE"
d["instance_id"]  = "$INSTANCE_ID"
d["api_token"]    = "$API_TOKEN"
d["enabled"]      = True

json.dump(d, open(CONFIG, "w"), indent=2)
print("Config saved.")
PYEOF

echo ""
echo "Sending test message..."
bash "$REPO/agent/notify-whatsapp.sh" "Setup complete! New-Power agent will now send you WhatsApp updates via Green API." "manual"

echo ""
echo "Done! WhatsApp notifications are now active."
