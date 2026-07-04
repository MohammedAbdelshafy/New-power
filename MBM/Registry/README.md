# Worker Registry (Article 8)

One JSON file per executor in `workers/`. The registry answers *who can do work*; role definitions in `MBM/Workers/` answer *what the work is*. A mission names a `role` (SOP) and routing picks the best registered executor for it.

**Plug-and-play:** joining = adding one file (see `Missions/SOPs/SOP-add-worker.md`). Leaving/pausing = editing `availability`. No integration code, ever.

## Capability schema
Every worker publishes: `id, name, kind, skills[], roles[], cost (low/medium/high), speed (fast/medium/slow), confidence (0–1), context_size (tokens), tools[], availability (available/busy/offline), mcp_support, git_support, web_support, notes`.

## Routing (`bash scripts/mbm.sh route M-012`)
Eligibility: not `offline`, and ≥ 50% of the mission's `required_skills` (100% scores higher). Score =

```
0.35·skill_match + 0.25·confidence + 0.15·cost_tier + 0.10·speed_tier + 0.15·performance
− 0.15·per_active_mission_workload − 0.30·if_busy + 0.25·if_preferred (+0.10·if_fallback)
```

`performance` comes from the event bus (MissionCompleted +1, MissionFailed −2, squashed to 0–1) — **real history outvotes self-declared confidence over time.** The CRO corrects registry `confidence` at weekly review when they diverge. Routing is advisory for humans and binding for autonomous claim loops.

## Current skill tags
`web-search, research, writing, arabic, sales, marketing, strategy, pricing, analysis, code, architecture, git, review, long-context, local-only, deterministic, orchestration`
Add tags as needed — but check this list first so missions and workers keep matching (Article 6).

## Registered workers
Run `bash scripts/mbm.sh workers` for the live table. Fabel/Claude (cloud agents), Jarvis (orchestrator, pending), ChatGPT (human-proxied), Antigravity & OpenCode (local IDE agents), NVIDIA local models (free/offline), mbm-scripts (deterministic), human-founder.
