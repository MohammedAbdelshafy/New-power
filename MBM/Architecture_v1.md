# MBM Architecture v1 — FROZEN 2026-07-04

This is the official architecture of the MBM Operating System. It is **complete and frozen**: no new frameworks, no new orchestration layers, no redesigns. Any change to this document requires an **Architecture Decision Record** — a `DL-###` entry in `MissionControl/Decision_Log/DECISIONS.md` (date, decision, rationale, alternatives rejected) plus a reviewed commit that updates this file. ADRs DL-001…DL-009 are the founding records.

Version: **v1.0.0** (see `Release/VERSION`). Release gates: `Release/RELEASE_CHECKLIST.md`.

## The system in one diagram

```
                              ┌────────────────────────────────────────────────────┐
                              │                  MISSION CONTROL                   │
              QUEUE ────────▶ │ Inbox → Claimed → InProgress → Review → Completed  │
        (Missions/Inbox)      │      → Archive          (+ Blocked, Templates, SOPs)│
                              └──────┬──────────────────────────────────┬──────────┘
          INTELLIGENCE               │ what to do                       │ every transition
     ┌───────────────────┐    ┌──────▼──────┐                    ┌──────▼──────┐
     │ ROUTING           │◀──▶│ ROLES       │                    │ EVENT BUS   │
     │ mbm.sh route      │    │ Workers/*.md│                    │ events.jsonl│
     └────────┬──────────┘    └──────┬──────┘                    └─────────────┘
              │ who does it          │ outputs
     ┌────────▼──────────┐    ┌──────▼──────────────────────────────────────┐
     │ REGISTRY (MODELS/ │    │ MEMORY: CRM (leads, intel, proposals,       │
     │ WORKERS/PLUGINS)  │    │ content) + Knowledge_Base (offer, playbooks,│
     │ Registry/workers/ │    │ LESSONS.md) + Decision_Log (ADRs)           │
     └───────────────────┘    └──────┬──────────────────────────────────────┘
                                     ▼
                              DASHBOARDS: Dashboard/index.html ◀ metrics.json ◀ mbm.sh metrics
```

## Component register (the frozen vocabulary)

| Concept | Implementation in v1 | Frozen contract |
|---|---|---|
| **Missions** | `MissionControl/Missions/` — 7-state lifecycle, schema v2 (`Templates/mission-template.md`) | State moves only via `scripts/mbm.sh`; schema changes need an ADR |
| **Queue** | `Missions/Inbox/` — the universal work queue | Claim-based dequeue (Article 3); git push is the lock (DL-007) |
| **Workers / Factories** | `Workers/*.md` — 9 revenue **roles** (role = a production unit: defined inputs → SOP → defined outputs). MBM-Social pipeline stages, when built, join this same namespace as roles — not a new "factory" framework (Article 6) | Role files are simultaneously system prompt, SOP, and output contract |
| **Models / Registries** | `Registry/workers/*.json` — 9 executors (LLMs, IDE agents, local models, scripts, humans) publishing skills, cost, speed, confidence, context size, tools, availability, MCP/git/web support | Plug-and-play: joining = one JSON file (DL-008: roles ≠ executors) |
| **Intelligence** | `mbm.sh route` — skills × confidence × cost × speed × workload × availability × event-history performance, with preferred/fallback and auto-fallback on unavailability | Advisory for humans, binding for autonomous loops (DL-009) |
| **Event Bus** | `EventBus/events.jsonl` — append-only JSONL, 10-event vocabulary, auto-emitted by every CLI transition | No hidden state (Article 4); JSONL-in-git, not a broker (DL-006) |
| **Memory** | Three tiers: `CRM/` (operational: leads/intel/proposals/content, schema in `CRM/README.md`) · `Knowledge_Base/` (durable: offer, playbooks, auto-mirrored LESSONS.md) · `Decision_Log/` (ADRs) | Knowledge capture is mechanically enforced at completion (Article 7) |
| **Dashboards** | `Dashboard/index.html` + `metrics.json`, recomputed deterministically by `mbm.sh metrics` | The dashboard never computes — it renders what the script computed |
| **Plugins** | Two plug surfaces: registry entries (new executors) and `.claude/skills/` (thin wrappers over role SOPs — other agent platforms wrap the same role files their own way) | A plugin never bypasses the mission lifecycle |
| **Governance** | `CONSTITUTION.md` (10 articles) + this document + ADRs | Amendments: ADR + reviewed commit, never silent |

## Boundaries (what v1 deliberately does NOT have)

- **No message broker, no database server, no job runner.** Git is state, lock, and transport (DL-006, DL-007). Revisit only via ADR when scale demands it (>~500 leads or missions/minute).
- **No autonomous outreach/publishing.** Article 5 — humans release anything customer-facing.
- **No orchestrator daemon in v1.** Jarvis (watcher that routes Inbox and notifies workers) is registered but `offline`; it is roadmap v2.1, an *addition inside this architecture*, not a new layer.
- **The MBM-Social clipping pipeline is not part of v1.** It is a product to be built *on* this OS (stages = roles, jobs = missions, clips = artifacts, learning = Knowledge_Base). See `Artifacts/2026-07-04-clipping-pipeline-audit.md` and missions M-008…M-010.

## Quality gates

Every release must pass `scripts/smoke-test.sh` (mission lifecycle, guards, routing, CRM validate/metrics) and the checklist in `Release/RELEASE_CHECKLIST.md`. Every architecture-touching change must cite its ADR in the commit message.
