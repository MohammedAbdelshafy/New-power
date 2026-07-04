# MBM Revenue Engine — Execution Roadmap

**Goal: first $100,000, and reusable assets that keep producing after every session ends.**
Success metrics: meetings booked · qualified opportunities · revenue · time saved · reusable capabilities added. Not lines of code.

## Phase 1 — Book qualified meetings (NOW)

The minimum system that turns effort into meetings. Everything here is live in this commit.

| # | Deliverable | Where | Status |
|---|---|---|---|
| 1 | Mission Control (Inbox→InProgress→Review→Completed, Artifacts, Knowledge_Base, Decision_Log) | `MBM/MissionControl/` | ✅ Built |
| 2 | 8 worker definitions (CRO, Lead Hunter, Researcher, Outreach, Content, Proposal, Follow-up, CRM Brain) | `MBM/Workers/` | ✅ Built |
| 3 | File-based CRM with lead schema | `MBM/CRM/` | ✅ Built |
| 4 | `mbm.sh` CLI (mission lifecycle, lead intake, metrics) | `scripts/mbm.sh` | ✅ Built |
| 5 | Marketing dashboard | `MBM/Dashboard/index.html` | ✅ Built |
| 6 | Claude Code skills wrapping the workers | `.claude/skills/` | ✅ Built |
| 7 | **Offer + ICP definition** (M-001) | `Knowledge_Base/offer.md` | ⚠️ Seeded — needs the human's pricing/positioning sign-off |
| 8 | First 50-lead list (M-002) | `CRM/leads/` | 🎯 Next session: run `/mbm-lead-hunt` |
| 9 | First outreach wave to top 20 (M-003/M-004) | `CRM/` | 🎯 After research |

**Phase 1 exit criterion: 3 qualified sales meetings booked.**

## Phase 2 — Automate research
- Run Company Researcher on every new lead automatically (mission auto-created on lead intake — `mbm.sh lead add` already drops a research mission in Inbox).
- Build `Knowledge_Base/research-sources.md` playbook per industry (construction, industrial, recycling, ports, manufacturing, AI buyers, B2B services).
- Exit: every contacted lead has an intel report in `CRM/intel/` first.

## Phase 3 — Automate outreach
- Sequence templates per industry + persona in `CRM/content/sequences/`.
- Gmail MCP integration for draft creation (drafts only — a human sends; protects deliverability and reputation).
- Exit: outreach wave of 20 personalized messages produced in < 1 hour of human time.

## Phase 4 — Automate proposals
- Proposal Generator produces proposal + ROI sheet from an intel report + meeting notes within one session.
- Reusable pricing calculator in `Knowledge_Base/pricing.md`.
- Exit: proposal turnaround < 24h from meeting.

## Phase 5 — Automate follow-up
- Follow-up Manager runs on a schedule (GitHub Action or Claude trigger) reading `next_action` dates from lead files, opening missions for due follow-ups.
- Exit: zero leads with an overdue `next_action`.

## Phase 6 — Automate reporting
- Weekly CRO revenue review auto-generated (Sunday cron): pipeline, close rate, bottleneck analysis → `Artifacts/revenue-reviews/`.
- Dashboard metrics recomputed on every push via GitHub Action.
- Exit: weekly review lands without being asked for.

## Standing decision rules
Before building anything, ask: Can this be a reusable worker? An SOP? A Mission? A Skill? Can another agent reuse it? If all answers are no — don't build it.
