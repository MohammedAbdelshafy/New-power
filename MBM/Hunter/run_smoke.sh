#!/usr/bin/env bash
# Offline smoke test for the MBM Hunter — no network, no API keys.
# Runs unit tests, then the full pipeline against the fixture, emitting a LeadPack CSV.
set -euo pipefail
cd "$(dirname "$0")"

echo "== unit tests =="
python3 tests/test_grade.py
python3 tests/test_pipeline.py

echo
echo "== sources =="
python3 -m hunter sources

echo
echo "== hunt fixture-county (urllib backend, offline) =="
python3 -m hunter hunt fixture-county --backend urllib --csv /tmp/mbm_leadpack_smoke.csv --sellable-only

echo
echo "== LeadPack CSV head =="
head -3 /tmp/mbm_leadpack_smoke.csv

echo
echo "SMOKE OK"
