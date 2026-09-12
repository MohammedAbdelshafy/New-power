# MBM Operating System

An AI Operating System for a revenue-generating company: file-based, git-first, agent-agnostic, governed by a Constitution. Built to coordinate unlimited specialized workers.

**Prime directive: fastest path to the first $100,000, while every action leaves behind a reusable asset.**

Read `CONSTITUTION.md` first — its 10 articles bind every worker. The three that matter most: **everything is a mission** (Art. 1), **git is the single source of truth** (Art. 2), **claim before you execute** (Art. 3).

## Architecture

```
                          ┌────────────────────────────────────────────────────┐
                          │                  MISSION CONTROL                   │
                          │ Inbox → Claimed → InProgress → Review → Completed  │
                          │        → Archive        (+ Blocked, Templates, SOPs)│
                          └──────┬─────────────────────────────────┬───────────┘
      claim/route                │ what to do                      │ every transition
 ┌───────────────┐        ┌──────▼──────┐                   ┌──────▼──────┐
 │   REGISTRY    │◀──────▶│    ROLES    │                   │  EVENT BUS  │
 │ who can work  │ route  │ Workers/*.md│                   │ events.jsonl│
 │ 9 executors   │        │ 9 revenue   │                   │ append-only │
 └───────────────┘        │   roles     │                   └─────────────┘
                          └──────┬──────┘
                                 │ outputs
              ┌──────────────────┼──────────────────────┐
              ▼                  ▼                      ▼
        CRM (leads, intel,   Artifacts +          Dashboard
        proposals, content)  Knowledge_Base       (metrics.json)
```

- **Missions** carry the work (schema v2: objective, dependencies, required skills, preferred/fallback workers, reviewer, acceptance criteria, lessons learned).
- **Roles** (`Workers/`) define *what* to do — SOPs any executor can follow.
- **Registry** (`Registry/`) defines *who* can do it — plug-and-play: one JSON file per worker (Claude, Fabel, ChatGPT, Jarvis, Antigravity, OpenCode, NVIDIA local, scripts, humans).
- **Routing** (`mbm.sh route M-012`) matches missions to executors by skills, confidence, cost, speed, workload, availability, and event-bus performance history, with automatic fallback.
- **Event bus** (`EventBus/events.jsonl`) is how workers communicate — never hidden state.
- **Knowledge capture** is mechanical: completion is blocked until Lessons Learned is filled; lessons auto-mirror to `Knowledge_Base/LESSONS.md`.

## Directory map

| Path | Purpose |
|---|---|
| `CONSTITUTION.md` | The 10 articles every worker operates under |
| `MissionControl/Missions/{Inbox,Claimed,InProgress,Review,Completed,Blocked,Archive}/` | The 7-state mission lifecycle |
| `MissionControl/Missions/Templates/` | `mission-template.md` — schema v2 source of truth |
| `MissionControl/Missions/SOPs/` | Lifecycle, worker onboarding, knowledge capture procedures |
| `MissionControl/{Artifacts,Knowledge_Base,Decision_Log}/` | Deliverables · company brain + LESSONS.md · decision record |
| `Workers/` | The 9 revenue roles (CRO, Lead Hunter, Researcher, Outreach, Content, Proposal, Follow-up, CRM Brain, Marketing) |
| `Registry/workers/` | Executor capability files — who can work, at what cost/speed/confidence |
| `EventBus/events.jsonl` | Append-only event log (MissionCreated…MissionEscalated) |
| `CRM/` | File-based CRM: leads, intel, proposals, content (schema in `CRM/README.md`) |
| `Dashboard/` | Revenue dashboard + `metrics.json` |
| `../scripts/mbm.sh` | The CLI — run `bash scripts/mbm.sh` for full usage |

## Operating it (any worker, any session)

```bash
export MBM_WORKER=<your-registry-id>       # actor attribution (Article 4)
git pull                                   # always
bash scripts/mbm.sh status                 # pipeline, missions, events, follow-ups
bash scripts/mbm.sh route M-012            # who should take it?
bash scripts/mbm.sh mission claim M-012 <your-id>
git add -A && git commit -m "claim M-012" && git push    # claim is not yours until pushed
bash scripts/mbm.sh mission start M-012
# ... execute per MBM/Workers/<role>.md ...
bash scripts/mbm.sh mission review M-012   # reviewer then runs: mission complete M-012
```

Full procedure: `MissionControl/Missions/SOPs/SOP-mission-lifecycle.md`. Joining as a new worker: `SOP-add-worker.md`. In Claude Code, `/mbm-lead-hunt`, `/mbm-research`, `/mbm-outreach`, `/mbm-content`, `/mbm-proposal`, `/mbm-followup`, `/mbm-revenue-review` wrap the roles.

## Ground rules (enforced, not aspirational)

- Humans send outreach, publish content, and sign pricing (Article 5).
- No invented facts in anything customer-facing — every claim traces to `CRM/intel/`.
- `mbm.sh validate && mbm.sh metrics` after CRM changes; the dashboard never lies.
- Extend, never duplicate (Article 6). Decisions with consequences → `Decision_Log/`.
