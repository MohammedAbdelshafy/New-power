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
