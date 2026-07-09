# MBM Hunter

The lead-intelligence hunting stack — the runnable proof of the Tier-1 web-agent
tooling in `MBM/Registry/workers/web-agent-tools.md`.

```
fetch  ->  parse  ->  enrich  ->  grade (Platinum..Bronze)  ->  dedup  ->  ledger / LeadPack CSV
```

**Design rule:** the core (parse + grade + pipeline + CLI) runs on the Python standard
library — **no network, no API keys, no third-party packages**. Scrapling / Playwright /
MCP are optional adapters that light up when installed. This is what lets Hermes run the
hunter in any session and keeps the grading rubric auditable.

## Quick start (offline, zero deps)

```bash
cd MBM/Hunter
./run_smoke.sh                 # runs tests + a full pipeline against the fixture
```

Or drive it directly:

```bash
python3 -m hunter sources                                    # list registered sources
python3 -m hunter hunt fixture-county --print-csv             # enrich + grade + emit CSV
python3 -m hunter hunt fixture-county --csv leads.csv --sellable-only

# multiple sources are deduped by parcel/owner and their signals unioned:
python3 -m hunter hunt fixture-county fixture-marketplace --csv leads.csv

# merge a hunt into a persistent master ledger (tracks first_seen/last_seen):
python3 -m hunter hunt fixture-county fixture-marketplace --ledger master.csv
python3 -m hunter ledger master.csv                          # ledger stats
```

## What's proven to run today

| Path | Status | Notes |
|---|---|---|
| Core: parse → enrich → grade → dedup → CSV | ✅ 23/23 unit tests pass, offline | stdlib only |
| Enrichment (absentee detection, normalization) | ✅ | derives signals a raw page never labels |
| Dedup + multi-source merge | ✅ | collapses repeats, unions signals, backfills contacts |
| Persistent ledger (first/last-seen) | ✅ | never re-sell a duplicate; round-trips to CSV |
| Fetch backend: `urllib` | ✅ | static pages |
| Fetch backend: `playwright` | ✅ verified end-to-end | uses provisioned Chromium (see below) |
| Fetch backend: `scrapling` | ⚙️ adapter ready | `pip install scrapling` to enable |
| MCP server | ⚙️ adapter ready, degrades cleanly | `pip install "mcp[cli]"` to enable |

### Playwright note
Web sessions ship Chromium under `/opt/pw-browsers`. If the pip `playwright` version
pins a different build, point the adapter at the provisioned binary instead of
downloading:

```bash
export PLAYWRIGHT_CHROMIUM_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
python3 -m hunter hunt <source> --backend playwright
```

## Layout

```
hunter/
  models.py      Lead + Grade + weight tables (single source of truth for the rubric)
  parse.py       stdlib HTML -> Lead extractor (Scrapling is the live-page upgrade)
  fetch.py       scrapling -> playwright -> urllib, each optional
  enrich.py      derive signals (absentee-owner) + normalize; runs before grading
  grade.py       pure scoring/grading — Platinum..Bronze, REJECT gate
  dedup.py       merge duplicates by parcel/owner key; union signals + contacts
  ledger.py      persistent master LeadPack with first_seen/last_seen tracking
  sources.py     declarative source registry (add county/marketplace sources here)
  pipeline.py    hunt() / hunt_many(); to_csv()/write_csv() LeadPack output
  __main__.py    the CLI (python -m hunter ...)
  mcp_server.py  exposes list_sources/hunt/hunt_many/grade as MCP tools
tests/           offline unit + e2e tests (23)
fixtures/        synthetic county + marketplace pages for tests + smoke
```

## Grading rubric

Score = motivation signals + contactability, gated by a minimum-data check. Weights live
in `hunter/models.py` (`SIGNAL_WEIGHTS`, `CONTACT_WEIGHTS`); thresholds in
`hunter/grade.py` (`GRADE_RULES`). Every grade carries its `grade_reasons` so a buyer —
and a human QA — can see exactly why a lead scored what it did.

| Band | Score | Meaning |
|---|---|---|
| Platinum | ≥ 80 | high motivation + reachable |
| Gold | ≥ 55 | strong |
| Silver | ≥ 30 | workable |
| Bronze | < 30 | thin, still contactable |
| Reject | — | missing location or any contact path → not sellable |

## Onboarding a real source

1. Confirm the source against `jarvis-mbm/Knowledge/Seller_Source_Playbook.md`
   (legality, ToS, robots).
2. Add a `Source(...)` entry in `hunter/sources.py` (`live=True`, `render=True` if JS).
3. If the page resists scripted parsing, that's the Backlog trigger to wire Scrapling
   (structured) or browser-use (agentic) — see the registry adoption gates.

## Wiring into the ops loop

`jarvis-mbm/Scripts/hermes.sh` shells out to `$HERMES_EXECUTOR` per mission. A hunt
mission's executor is simply:

```bash
python3 -m hunter hunt <source> --csv Artifacts/LeadPacks/<date>-<source>.csv --sellable-only
```
