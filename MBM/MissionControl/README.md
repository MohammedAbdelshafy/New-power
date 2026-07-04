# Mission Control — Protocol

Every unit of revenue work is a **mission file** that moves through four folders:

```
Missions/Inbox  →  Missions/InProgress  →  Missions/Review  →  Missions/Completed
 (queued)            (one owner)            (awaiting human       (done; outputs
                                             or CRO approval)      linked)
```

Moves are `git mv` (or `scripts/mbm.sh mission start|review|complete <id>`), so the git log is the audit trail.

## Mission file format

Filename: `M-###-short-slug.md`. YAML front-matter + body:

```markdown
---
id: M-007
title: Research top 20 construction leads
phase: 2                # roadmap phase
worker: company-researcher   # which Workers/*.md executes this
priority: P1            # P0 (revenue-blocking) / P1 / P2
status: inbox           # inbox | in_progress | review | completed
created: 2026-07-04
due: 2026-07-08
owner: ""               # agent/human who picked it up
success_criteria:
  - 20 intel reports in CRM/intel/
  - each report lists ≥1 named decision maker and ≥2 verified pain signals
artifacts: []           # filled on completion with paths to outputs
---

## Context
Why this mission exists, links to related leads/missions.

## Instructions
Anything beyond the worker's standard SOP.

## Log
- 2026-07-04 created by CRO
```

## Rules

1. **One owner per mission.** Set `owner` when moving to InProgress.
2. **Success criteria are binary.** If you can't verify them, rewrite them before starting.
3. **Outputs never live in the mission file.** They go to `CRM/` or `Artifacts/`; the mission links them in `artifacts:`.
4. **Review is not optional** for anything customer-facing (outreach copy, proposals, published content). A human approves before it leaves the building.
5. **Completed missions are immutable.** Follow-up work = new mission.
6. **Anyone can file to Inbox** — humans, workers, scheduled jobs. The CRO worker prioritizes Inbox during the weekly review.

## Artifacts/
Deliverables produced by missions: revenue reviews, research reports, decks. Name them `YYYY-MM-DD-description.md` (or a subfolder per recurring series, e.g. `revenue-reviews/`).

## Knowledge_Base/
The company's brain: `offer.md` (ICP + offers + pricing), playbooks, templates. Workers read it before acting; missions update it when learning something durable.

## Decision_Log/
Append entries to `DECISIONS.md`. One paragraph per decision: date, decision, why, alternatives rejected. If a future agent would ask "why is it like this?" — log it.
