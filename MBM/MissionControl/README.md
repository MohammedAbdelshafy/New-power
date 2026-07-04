# Mission Control — Protocol (v2)

Every unit of work in the MBM Operating System is a **mission file** moving through folders. Constitution Article 1: everything is a mission — no direct prompting, no isolated workflows.

```
Inbox ──claim──▶ Claimed ──start──▶ InProgress ──review──▶ Review ──complete──▶ Completed ──archive──▶ Archive
                    │                   │
                    └───────block───────┴──▶ Blocked ──unblock──▶ Claimed
```

All moves go through `scripts/mbm.sh mission <claim|start|block|unblock|review|complete|fail|archive> <id>`, which validates the transition, updates `status:`, appends to the mission log, and **emits the matching event** to `MBM/EventBus/events.jsonl` (MissionCreated, MissionClaimed, MissionStarted, MissionBlocked, MissionCompleted, MissionReviewed, MissionArchived, MissionFailed, MissionEscalated).

## Folders

| Folder | Meaning |
|---|---|
| `Missions/Inbox/` | Universal queue. Readable/claimable by every registered worker — Claude, Fabel, ChatGPT, Jarvis, Antigravity, OpenCode, local models, scripts, humans |
| `Missions/Claimed/` | Claimed but not started. **Claiming prevents duplicate execution** (Article 3): pull → claim → push immediately; rejected push = already claimed |
| `Missions/InProgress/` | Being executed by its single owner |
| `Missions/Review/` | Awaiting the named reviewer (never the owner) — binary acceptance-criteria check |
| `Missions/Completed/` | Done; knowledge captured (CLI blocks completion with empty Lessons Learned) |
| `Missions/Blocked/` | Stuck, with a logged reason. Blocked > 7 days → CRO escalates |
| `Missions/Archive/` | Terminal storage for completed + failed missions |
| `Missions/Templates/` | `mission-template.md` — the schema v2 source of truth |
| `Missions/SOPs/` | The procedure library: lifecycle, adding workers, knowledge capture |

## Mission schema (v2)

See `Missions/Templates/mission-template.md`. Front-matter fields: `id, title, objective, priority, phase, dependencies, role, required_skills, preferred_worker, fallback_workers, status, owner, reviewer, created, due, outputs, acceptance_criteria, artifacts` + body sections `Context, Instructions, Lessons Learned (required), Log`.

`role` names the `MBM/Workers/*.md` file whose SOP governs execution (*what* to do). `preferred_worker`/`fallback_workers`/`owner` are `MBM/Registry/` ids (*who* does it). Routing (`mbm.sh route <id>`) recommends the executor.

## Rules

1. One owner per mission; claim before executing (Article 3).
2. Acceptance criteria are binary and stranger-verifiable (Article 10). Rewrite before starting if they aren't.
3. Outputs live in `CRM/` or `Artifacts/`, never in the mission file; the mission lists them in `artifacts:`.
4. Dependencies must be Completed before a mission is claimable.
5. Review is a real gate for anything customer-facing; the reviewer is never the owner.
6. Completed missions are immutable — follow-up work is a new mission.
7. Anyone can file to Inbox (humans, workers, scheduled jobs). The CRO triages weekly.
8. Every completion runs `SOPs/SOP-knowledge-capture.md` (Article 7).

## Artifacts/ · Knowledge_Base/ · Decision_Log/

Unchanged in role: deliverables → `Artifacts/` (dated names, series subfolders); durable company knowledge, playbooks, and auto-mirrored `LESSONS.md` → `Knowledge_Base/`; dated decision paragraphs → `Decision_Log/DECISIONS.md`.
