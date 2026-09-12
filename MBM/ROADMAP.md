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

## Platform track (the OS underneath the phases)

**v2 — SHIPPED 2026-07-04:** Constitution · 7-state claim-based mission lifecycle + Templates/SOPs · schema v2 · worker registry (9 executors, plug-and-play) · event bus · intelligent routing with fallback · enforced knowledge capture · Marketing Agent role. (See `AUDIT.md` v2 section; M-007.)

**v2.1 — next platform increment (build only when Phase 1–2 revenue work demands it):**
- GitHub Action: on push, run `mbm.sh validate + metrics` and surface Blocked>7d missions (auto-escalate).
- Jarvis v0: a watcher loop (local or Action) that reads Inbox, runs routing, and notifies the recommended worker via the existing Telegram/Discord bridge — brings `jarvis` registry entry online.
- NVIDIA local runner wired to the git bridge — brings `nvidia-local` online for zero-cost draft work.
- Recurring-mission generator (M-006 Sunday copies file themselves).

## Sprint plan (weekly sprints; numbering continues from the three build sprints of 2026-07-04)

Every sprint must move: revenue · automation · quality · subscribers/audience · views/reach · maintainability. Each sprint's missions are filed in Inbox at the preceding Sunday review.

| Sprint | Focus | Committed outcomes |
|---|---|---|
| **4** (Jul 6–12) | **First money motion** | M-001 signed; M-012 lead pack #1 built + priced; M-002/M-003 hunt & research running; founder pitches pack to 10 agencies. *Revenue target: first pack sold* |
| **5** (Jul 13–19) | **Outreach at volume** | M-004 wave-1 sent (10 sequences); M-005 ZWM case study + posts live; pack #2 in a second segment; follow-up sweeps daily. *Target: 5 replies, 2 meetings* |
| **6** (Jul 20–26) | **MBM-Social spine** | M-008 complete (video→3 clips, AR+EN test); quality thresholds tuned on real output; services pipeline keeps running via follow-up manager. *Target: 1 proposal out* |
| **7** (Jul 27–Aug 2) | **MBM-Social sellable** | M-009 packaging complete; first free pilot clips for one real creator/business; issue #notify wiring so blocked missions ping Telegram. *Target: first automation pilot signed OR 2 packs sold* |
| **8** (Aug 3–9) | **Validate & learn** | M-010 benchmarks + real reports; clipping go/no-go; CRO month-1 retro reprices all offers from actual win/loss data; Jarvis v0 watcher if capacity allows. *Target: $3–5k cumulative revenue* |

## Standing decision rules
Before building anything, ask: Can this be a reusable worker? An SOP? A Mission? A Skill? Can another agent reuse it? If all answers are no — don't build it.
