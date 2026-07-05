# Decision Log

Append-only. Newest at the bottom. One paragraph each: date, decision, rationale, alternatives rejected.

---

**DL-001 · 2026-07-04 · Git is the database.**
All revenue state (leads, missions, intel, metrics, decisions) lives as files in this repo. Rationale: every agent in the MBM ecosystem (Claude Code, Antigravity, opencode, ChatGPT, local models) already reads/writes files and syncs via git — see `docs/ANTIGRAVITY_SETUP.md`; we get versioning, audit trail, and multi-agent access with zero new infrastructure. Rejected: hosted CRM (HubSpot/Airtable) — adds cost, API keys per agent, and a parallel system outside Mission Control; revisit only past ~500 active leads or when a sales hire needs a GUI-first tool.

**DL-002 · 2026-07-04 · Workers are markdown SOPs, not code services.**
Each worker in `MBM/Workers/` is a role definition + SOP + output contract in one file. Rationale: it works as a system prompt for any LLM, as a checklist for a human, and as a spec for future code — maximum reuse, zero integration work. Rejected: Python microservices per worker — engineering is not the bottleneck; services would rot without users.

**DL-003 · 2026-07-04 · Humans send all outreach; agents only draft.**
Outreach Agent produces ready-to-send drafts (files + optional Gmail drafts); a human reviews and sends. Rationale: protects sender reputation and deliverability, keeps us compliant with anti-spam law, and keeps a quality gate on the one artifact prospects actually see. Rejected: fully automated sending — one bad batch can burn a domain permanently.

**DL-004 · 2026-07-04 · Phase order: meetings before automation.**
Phase 1 targets 3 booked meetings with mostly-manual worker execution before Phases 2–6 automate research/outreach/proposals/follow-up/reporting. Rationale: automating an unproven offer scales waste; the offer (`Knowledge_Base/offer.md`) must survive contact with real prospects first.

**DL-005 · 2026-07-04 · Anchor offer on the Zero Waste Misr proof point.**
Positioning leads with "we run our own recycling operation on this technology". Rationale: the strongest differentiator available today is a real deployed system in a hard industry, and it gives insider credibility in the recycling/industrial segments. Revisit when a paying client case study exists.

**DL-006 · 2026-07-04 · The event bus is a JSONL file in git, not a message broker.**
Workers coordinate via append-only `EventBus/events.jsonl` committed like any other file. Rationale: every current and future worker already reads files and pulls git; a broker (Redis/NATS/webhooks) adds infrastructure, credentials, and a non-versioned side channel that violates Article 2. Rejected: GitHub webhooks as the primary bus — kept as an optional notification layer (existing notify.yml), not the source of truth.

**DL-007 · 2026-07-04 · Claims are file moves; git push is the lock.**
A mission is claimed by moving it to `Claimed/` with `owner` set and pushing immediately; a rejected push means someone else won the race. Rationale: git's atomic ref updates give us distributed mutual exclusion for free at our scale (missions/day, not missions/second). Rejected: lock files and claim servers — more machinery for the same guarantee.

**DL-008 · 2026-07-04 · Roles and executors are separate namespaces.**
`Workers/*.md` define roles (what/how); `Registry/workers/*.json` define executors (who). A mission names a role and routing picks the executor. Rationale: the same role must be executable by Claude today, a local model tomorrow, and a human always — coupling them would break plug-and-play (Article 8). This also resolved the "Sales Agent"/"Revenue Dashboard" requests without duplicate systems: Sales = outreach-agent role + human-founder executor; Dashboard = revenue-dashboard role + mbm-scripts executor.

**DL-009 · 2026-07-04 · Routing is advisory for humans, binding for autonomous loops.**
`mbm.sh route` scores skills, confidence, cost, speed, workload, availability, and event-bus performance (completions +1, failures −2) with preferred/fallback bonuses. Real history outvotes self-declared confidence over time; the CRO reconciles registry confidence at weekly review. Rejected: hard-binding routing for humans — the founder may always claim anything.

**DL-010 · 2026-07-04 · MBM-Social is stages-on-the-OS, not a platform-within-the-platform.**
The clipping pipeline (MBM-Social/) is 8 restartable stage modules + a one-job runner. Mission Control is its queue, mission re-claim is its retry system, the event bus is its logging, job dirs + the CRM ledger are its asset manager, and publishing stays human-gated. Rationale: every "queue manager / retry system / workflow automation" request resolved to a system that already existed (Article 6); building them again would have doubled surface area with zero new capability. Rejected: a celery/redis job system, platform upload APIs in v1, a GPU dependency (CPU measured fast enough for pilot volume: 66s source → 2 finished packages in 21s).

**DL-011 · 2026-07-04 · Article 11: production requires measurable improvement.**
Founder amendment: completed missions must improve revenue, lead quality, customer satisfaction, automation, or operational speed — named explicitly at completion — or their output stays out of production. Rationale: after one day of heavy system-building, the failure mode to guard against is polished work that moves no business number. Also ratifies GitHub-as-work-queue across both repos (New-power = OS + revenue engine; jarvis-mbm = local-fleet dispatch, missions M-101–M-110). Rejected: a scoring rubric per mission — a named claim in Lessons Learned, checkable by the reviewer, is enough process.

**DL-012 · 2026-07-04 · FD-001: US real estate lead intelligence is the sole production market for 30 days.**
Founder directive. The Egypt/GCC B2B line (packs 001–003, campaigns A–C) is PARKED, not deleted — assets stay in the CRM, missions M-002/M-003/M-004/M-012 wait. All production capacity goes to US seller-lead inventory (jarvis-mbm M-101) and buyer acquisition (M-102). Rationale: focus beats parallel markets at one-founder scale; the US lead market has faster repeat-purchase cycles. Compliance boundary set: homeowner PII never enters git. Rejected: running both markets at reduced intensity — split attention was the #1 risk in the MBM-Social risk register and applies doubly here.

**DL-013 · 2026-07-04 · Implementation contract MBM-IMPLEMENTATION-v1: accepted with two documented blockers.**
(1) The contract's referenced specs (EXECUTION-OS.md, WORKFLOW-SYSTEM.md, WF-001/004/030-034, AI Matrix, Antigravity specs, Architecture Contracts) exist in no repository — spec-exact phases (M04, full M05, M07, M09 campaign layer) are blocked until DeepSeek/founder commit them (suggested home: MBM/Specs/). Implementing them from inference would violate the contract's own "do not invent". (2) FD-006 economics still govern sequencing — phases ship when they reduce founder work now or unblock revenue. Executed immediately: Phase-0 audit + migration plan, M01 standard files in both repos (thin pointers to canonical docs — no duplication, nothing overwritten), M05-partial as Registry/services.yaml (a config view over the existing registry+routing; a second routing.py was rejected as a DL-008 violation). M03 shared-library extraction rejected for now: the duplicate report shows only notify.sh + one doc duplicated — below the contract's own "duplicated, reusable, stable" threshold.
