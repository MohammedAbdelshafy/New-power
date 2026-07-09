# MBM — OS layer (New-power)

Governance and shared capability for the MBM real-estate lead-intelligence business.
The day-to-day operations repo is [`jarvis-mbm`](https://github.com/mohammedabdelshafy/jarvis-mbm);
this is the OS/master layer it points at (Constitution, registry, shared code — Article 6:
content lives once, here).

## Contents

| Path | What |
|---|---|
| `Registry/workers/` | Capability registry — which agents/tools exist, who owns them, license status, adoption gates. Referenced by `jarvis-mbm/AGENTS.md` and `ROSTER.md`. |
| `Hunter/` | The runnable lead-hunting stack: fetch → parse → enrich → grade → dedup → ledger/LeadPack CSV. Tier-1 web-agent tooling (Playwright + Scrapling + MCP) wired to the pipeline. |

## Web-agent tooling — what landed here

Fifteen external agent/web-automation frameworks were evaluated and **registered**
(`Registry/workers/web-agent-tools.md`). Rather than vendoring 15 large repos, they are
cataloged with an owner, a pipeline stage, a license check, and an adoption gate — and the
**Tier-1 set is actually wired and running** in `Hunter/`:

- **Playwright** — default fetch backend (verified end-to-end against a live browser).
- **Scrapling** — resilient structured-scrape adapter (enable with `pip install scrapling`).
- **modelcontextprotocol** — the hunter exposes its tools over MCP for any agent to call.

Tier-2 (browser-use, stagehand, skyvern¹), Tier-3 orchestration (langgraph, crewAI,
autogen, OpenHands, OpenManus), and Tier-4 reference catalogs are registered but **not**
wired — each waits on its Backlog trigger. ¹ Skyvern is **AGPL — quarantined** for
commercial use; see `Registry/workers/LICENSE-NOTES.md`.

## Prove it runs

```bash
cd MBM/Hunter && ./run_smoke.sh
```
