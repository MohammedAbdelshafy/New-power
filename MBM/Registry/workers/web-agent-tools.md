# Worker Registry — Web-Agent & Automation Tooling

**Canonical capability registry** for external agent / web-automation frameworks the
MBM fleet may adopt. This is the "what exists and who owns it" ledger; runnable code
lands under `MBM/Hunter/`. Adoption is gated — nothing here is a dependency until a
Backlog trigger promotes it (Constitution Article on gated future work).

> **License discipline (read first).** MBM sells data commercially. Before any tool
> below is wired into a revenue path, its license must be confirmed against
> `MBM/Registry/workers/LICENSE-NOTES.md`. **AGPL-3.0 tools (Skyvern) are quarantined**
> — network/SaaS use triggers copyleft obligations. Licenses listed below are
> best-effort and MUST be re-verified at adoption time, not trusted from this table.

## Pipeline map

```
County / public records ─┐
Marketplaces, FSBO feeds ─┤→ [FETCH] → [PARSE] → [GRADE Platinum→Bronze] → LeadPacks
Buyer directories ────────┘     ▲          ▲            ▲                        │
                                │          │            │                        ▼
                          scrape stack  parse stack  grade rules            CRM / Sales
```

Each tool below is tagged with the pipeline stage it serves and the MBM agent that
would own it (see `jarvis-mbm/Agents/ROSTER.md`).

---

## Tier 1 — Foundation (adopt first, low risk)

| Tool | Lang | License* | Stage | Owner | Why it's here |
|---|---|---|---|---|---|
| **microsoft/playwright** | TS/Py | Apache-2.0 | FETCH | Hermes | Browser engine under every web-agent tool. Already provisioned in web sessions (`/opt/pw-browsers`). Deterministic, scriptable, no LLM cost. **Default fetch backend for the Hunter stack.** |
| **D4Vinci/Scrapling** | Py | BSD-3 | FETCH+PARSE | Hermes | Adaptive HTML fetch/parse that survives markup drift — ideal for brittle county-records pages. Cheap, no LLM. **Primary structured-scrape backend.** |
| **modelcontextprotocol** | multi | MIT | INTEGRATION | Jarvis | The wire protocol. The Hunter exposes its `hunt`/`grade` tools as an MCP server so any agent (Claude, Hermes, external) calls them identically. |

## Tier 2 — Agentic web navigation (adopt when a source resists scripting)

| Tool | Lang | License* | Stage | Owner | Why it's here |
|---|---|---|---|---|---|
| **browser-use/browser-use** | Py | MIT | FETCH | Hermes | LLM-driven browser agent. Use for sources that need reasoning to navigate (login walls, search forms, pagination that changes). Falls back from the deterministic Playwright path. |
| **browserbase/stagehand** | TS | MIT | FETCH | Hermes | Same niche as browser-use, TS-side. Keep as an alternative if the stack goes Node; do not run both. |
| **openai/openai-cua-sample-app** | Py | MIT | FETCH | Hermes | Reference implementation of computer-use navigation. Study, don't vendor. |
| **Skyvern-AI/skyvern** | Py | **AGPL-3.0** | FETCH | ⛔ quarantined | Vision+LLM browser automation. Capable, but **AGPL blocks commercial SaaS use** — reference only until relicensed or air-gapped. |

## Tier 3 — Orchestration (adopt only when >1 agent runs concurrently)

| Tool | Lang | License* | Stage | Owner | Why it's here |
|---|---|---|---|---|---|
| **langchain-ai/langgraph** | Py | MIT | ORCHESTRATION | Jarvis | Stateful agent graphs. Best fit if Jarvis's planner→hunt→grade→report loop outgrows `hermes.sh`. Lowest lock-in of the orchestration set. |
| **crewAIInc/crewAI** | Py | MIT | ORCHESTRATION | Jarvis | Role-based multi-agent ("crew"). Maps cleanly onto the ROSTER (Hermes/DeepSeek/Ollama). |
| **microsoft/autogen** | Py | MIT/CC-BY | ORCHESTRATION | Jarvis | Conversational multi-agent. Heavier; evaluate against langgraph before adopting. |
| **All-Hands-AI/OpenHands** | Py | MIT | ORCHESTRATION | Jarvis | Autonomous software-engineering agent. Candidate for the *engineering* lane (repo maintenance), not the lead lane. |
| **mannaandpoem/OpenManus** | Py | MIT | ORCHESTRATION | Jarvis | General autonomous agent. Reference for planning patterns; not a near-term dependency. |

## Tier 4 — Reference catalogs (never vendored)

| Tool | License* | Use |
|---|---|---|
| **punkpeye/awesome-mcp-servers** | CC/MIT | Shop here first before building any MCP server (CRM, Telegram, records APIs). |
| **steel-dev/awesome-web-agents** | CC/MIT | Landscape scan when re-evaluating the Tier-2 choice. |
| **anthropics/anthropic-quickstarts** | MIT | Computer-use + agent quickstarts; canonical patterns for the Claude executor. |

\* Licenses are best-effort and re-verified at adoption — see `LICENSE-NOTES.md`.

---

## Adoption gates (Backlog triggers)

A tool moves from "registered" to "wired" only when its trigger fires:

| Trigger | Promotes | Rationale |
|---|---|---|
| First county source needs JS rendering | Playwright fetch backend (already scaffolded) | Deterministic path is cheapest |
| A source blocks scripted fetch (bot wall) | browser-use fallback | Pay LLM cost only when forced |
| Two+ agents run the pipeline at once | langgraph **or** crewAI (pick one) | Don't add orchestration before concurrency exists |
| An external system needs a stable tool API | MCP server (already scaffolded) | Standard beats bespoke glue |
| Skyvern relicensed OR air-gapped deployment | Skyvern un-quarantine | AGPL obligation removed |

## Status

- **2026-07-07** — Registry created. Tier-1 (Playwright + Scrapling + MCP) scaffolded and
  running in `MBM/Hunter/`. All Tier-2/3/4 entries registered but **not** wired.
- **2026-07-09** — Hunter enhanced: enrichment (absentee-owner detection + normalization),
  cross-source/repeat **dedup** (union signals, backfill contacts), and a persistent
  **ledger** with first/last-seen tracking. 23/23 offline tests pass; multi-source hunt
  exposed over MCP (`hunt_many`).
- **2026-07-09** — Demand side added: **buyer/wholesaler finder** (rank Hot/Warm/Cold on
  CEO-REVIEW-001 axes) + **outreach draft generator** (free-pack + Google Meet invite,
  CAN-SPAM footer, refuses unfilled personalization) — **prepares drafts only, never
  sends** (FD-001 Art. 5). Commercial/ToS-restricted sites (auction.com, zillow,
  realtor.com, biggerpockets) registered as **GATED_SOURCES — disabled** pending
  compliance/ToS clearance. 33/33 offline tests pass.
- Runnable proof: `MBM/Hunter/` produces enriched, deduped, graded seller leads AND
  ranked buyers + review-ready outreach drafts offline today (Playwright/Scrapling used
  when installed, stdlib fallback otherwise).
