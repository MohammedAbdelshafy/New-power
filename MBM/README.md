# MBM Revenue Engine

The operating system for a revenue-generating company. File-based, git-first, agent-agnostic.

**Prime directive: fastest path to the first $100,000, while every action leaves behind a reusable asset.**

## How it works

```
                     ┌──────────────────────────────────────────┐
                     │              MISSION CONTROL             │
                     │  Inbox → InProgress → Review → Completed │
                     └───────────────────┬──────────────────────┘
                                         │ missions assign work to workers
     ┌─────────────┬─────────────┬───────┴──────┬──────────────┬─────────────┐
     ▼             ▼             ▼              ▼              ▼             ▼
 Lead Hunter → Researcher → Outreach Agent → Follow-up Mgr → Proposal Gen → CRO
     │             │             │              │              │             │
     └─────────────┴─────────────┴──────┬───────┴──────────────┴─────────────┘
                                        ▼
                              CRM (files, git-versioned)
                                        ▼
                              Dashboard + Weekly Review
```

- **Git is the database.** Leads, missions, intel, proposals, decisions — all files, all versioned, all readable by any agent.
- **Workers are markdown.** `MBM/Workers/*.md` are simultaneously system prompts, SOPs, and specs. Claude, ChatGPT, Antigravity, opencode, and local models all operate them the same way: read the worker file, follow its SOP, write its outputs.
- **No parallel systems.** All work flows through Mission Control. All state lives in the CRM. All irreversible choices go in the Decision Log.

## Directory map

| Path | Purpose |
|---|---|
| `MissionControl/Missions/{Inbox,InProgress,Review,Completed}/` | Mission lifecycle (see `MissionControl/README.md` for the protocol) |
| `MissionControl/Artifacts/` | Deliverables produced by missions (reports, reviews, decks) |
| `MissionControl/Knowledge_Base/` | Offer, ICP, pricing, playbooks — the company's brain |
| `MissionControl/Decision_Log/` | Append-only record of significant decisions |
| `Workers/` | The 8 revenue workers (role + SOP + output schema each) |
| `CRM/leads/` | One JSON file per lead (`schema` in `CRM/README.md`) |
| `CRM/intel/` | Company intelligence reports (Researcher output) |
| `CRM/proposals/` | Generated proposals & ROI sheets |
| `CRM/content/` | Outreach sequences, LinkedIn posts, case studies |
| `Dashboard/` | Marketing/revenue dashboard (`index.html` + `metrics.json`) |
| `../scripts/mbm.sh` | CLI: mission lifecycle, lead intake, metric recompute |

## Operating it (any agent, any session)

1. `bash scripts/mbm.sh status` — see pipeline + open missions.
2. Pick the top-priority mission in `Missions/Inbox/`, move it to `InProgress` (`mbm.sh mission start <id>`).
3. Open the worker file the mission names, follow its SOP.
4. Write outputs where the worker's contract says (CRM/Artifacts), move the mission to `Review`.
5. A human (or the CRO worker in weekly review) approves → `Completed`.
6. Commit and push. The commit **is** the status report.

In Claude Code, the skills `/mbm-lead-hunt`, `/mbm-research`, `/mbm-outreach`, `/mbm-proposal`, `/mbm-followup`, `/mbm-revenue-review` invoke workers directly.

## Ground rules

- **Humans send outreach.** Agents draft; a human reviews and hits send. Protects deliverability, reputation, and legality.
- **No invented facts in outreach or proposals.** Every claim traces to a research citation in `CRM/intel/`.
- **Update metrics after CRM changes:** `bash scripts/mbm.sh metrics`.
- **Decisions with consequences get a Decision Log entry** — one paragraph, dated, with alternatives considered.
