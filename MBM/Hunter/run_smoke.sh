#!/usr/bin/env bash
# Offline smoke test for the MBM Hunter — no network, no API keys.
# Runs unit tests, then exercises single-source, multi-source dedup, and the ledger.
set -euo pipefail
cd "$(dirname "$0")"

echo "== unit tests =="
for t in tests/test_*.py; do python3 "$t"; done

echo
echo "== sources =="
python3 -m hunter sources

echo
echo "== hunt fixture-county (single source, offline) =="
python3 -m hunter hunt fixture-county --backend urllib

echo
echo "== hunt county + marketplace (multi-source dedup) -> ledger =="
LEDGER=/tmp/mbm_ledger_smoke.csv
rm -f "$LEDGER"
python3 -m hunter hunt fixture-county fixture-marketplace --backend urllib \
  --csv /tmp/mbm_leadpack_smoke.csv --sellable-only --ledger "$LEDGER"

echo
echo "== ledger stats =="
python3 -m hunter ledger "$LEDGER"

echo
echo "== LeadPack CSV head =="
head -3 /tmp/mbm_leadpack_smoke.csv

echo
echo "== find wholesalers (buyer finder) =="
python3 -m hunter buyers fixture-wholesalers --backend urllib

echo
echo "== outreach drafts (soft tone, HUMAN SENDS — never auto-sent) =="
python3 -m hunter outreach fixture-wholesalers --backend urllib --out /tmp/mbm_drafts

echo
echo "SMOKE OK"
