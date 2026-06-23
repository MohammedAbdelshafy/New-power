#!/usr/bin/env bash
# Interactive setup for CallMeBot WhatsApp notifications.

set -euo pipefail

REPO="/home/user/New-power"
CONFIG="$REPO/.claude/whatsapp-config.json"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   WhatsApp Notification Setup (CallMeBot)        ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "STEP 1 — Activate CallMeBot:"
echo "  • Open WhatsApp on your phone"
echo "  • Save this number as a contact: +34 644 59 66 20"
echo "  • Send it this exact message:"
echo ""
echo "      I allow callmebot to send me messages"
echo ""
echo "  • You will receive your API key back via WhatsApp (may take ~1 min)"
echo ""

read -rp "Press ENTER when you have received your API key... "
echo ""

read -rp "Enter your WhatsApp phone number (e.g. +201001234567): " PHONE
read -rp "Enter your CallMeBot API key: " APIKEY

if [ -z "$PHONE" ] || [ -z "$APIKEY" ]; then
  echo "Phone and API key are required. Aborting."
  exit 1
fi

python3 - <<PYEOF
import json

CONFIG = "$CONFIG"
PHONE = "$PHONE"
APIKEY = "$APIKEY"

try:
    d = json.load(open(CONFIG))
except Exception:
    d = {}

d["phone"] = PHONE
d["apikey"] = APIKEY
d["enabled"] = True

json.dump(d, open(CONFIG, "w"), indent=2)
print("Config saved.")
PYEOF

echo ""
echo "Sending test message..."
bash "$REPO/agent/notify-whatsapp.sh" "Setup complete! New-Power agent will now send you WhatsApp updates." "manual"

echo ""
echo "Done! WhatsApp notifications are now active."
echo "You can disable them anytime by setting 'enabled': false in .claude/whatsapp-config.json"
