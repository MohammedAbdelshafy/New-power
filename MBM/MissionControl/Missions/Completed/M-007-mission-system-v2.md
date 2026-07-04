---
id: M-007
title: "Mission System v2: claim lifecycle, worker registry, event bus, routing, governance"
objective: "Transform the mission system into a production-grade multi-agent OS where any registered worker can claim, execute, and complete missions without duplicate execution or knowledge loss"
priority: P0
phase: 1
dependencies: []
role: crm-brain
required_skills:
  - code
  - architecture
  - git
preferred_worker: fabel
fallback_workers:
  - claude
  - opencode
status: completed
owner: fabel
reviewer: human-founder
created: 2026-07-04
due: 2026-07-04
outputs:
  - MBM/CONSTITUTION.md
  - MBM/MissionControl/Missions/ (Claimed, Blocked, Archive, Templates, SOPs)
  - MBM/Registry/
  - MBM/EventBus/
  - scripts/mbm.sh (v2)
acceptance_criteria:
  - all 9 mission folders exist with documented lifecycle and SOPs
  - existing missions migrated to schema v2 and validate
  - worker registry holds >=8 workers with the full capability schema
  - mbm.sh supports claim/block/unblock/fail/archive/route/emit/events/workers and emits events on every transition
  - completion is mechanically blocked when Lessons Learned is empty
  - routing ranks eligible workers for any mission using skills, confidence, cost, workload, availability and event-log performance
artifacts:
  - MBM/CONSTITUTION.md
  - MBM/MissionControl/Missions/Templates/mission-template.md
  - MBM/MissionControl/Missions/SOPs/
  - MBM/Registry/
  - MBM/EventBus/events.jsonl
  - MBM/Workers/09-marketing-agent.md
  - scripts/mbm.sh
---

## Context
Ordered by the founder: every AI worker must operate through the Mission System — no direct prompting, no isolated workflows. v1 (built earlier today) had a 4-state lifecycle, no claim step, no registry, no events, no routing, and convention-only knowledge capture.

## Instructions
Extend, never duplicate (Article 6): upgrade the existing MissionControl/CLI in place. Commit per milestone.

## Lessons Learned
- Git-native primitives covered every requirement: file moves = state machine, push conflicts = claim locks, JSONL in git = event bus. Zero new infrastructure; every worker that can `git pull` can participate.
- Embedding python3 heredocs in bash demands strict quoting discipline: double quotes only inside single-quoted heredocs, no f-strings with nested quotes. Cost three debug cycles in v1; v2 written to that rule from the start.
- Migration scripts that strip quotes naively will mangle YAML values containing quotes — three acceptance criteria needed manual repair. Next schema migration: parse, don't regex-strip.
- The role/executor split (Workers/ vs Registry/) dissolved an apparent requirements conflict: "Sales Agent" and "Revenue Dashboard" became role+executor pairings instead of duplicate systems (DL-008).
- Enforcement beats convention: making `mission complete` refuse on empty lessons turned Article 7 from a hope into a property. Wherever possible, encode constitution articles into the CLI.

## Log
- 2026-07-04 created by fabel (this upgrade dogfoods the system it builds)
- 2026-07-04 claimed by fabel
- 2026-07-04 started
- 2026-07-04 BLOCKED: testing blocked state
- 2026-07-04 unblocked
- 2026-07-04 started
- 2026-07-04 moved to review
- 2026-07-04 completed; lessons mirrored to Knowledge_Base/LESSONS.md
- 2026-07-04 completion executed in-session; founder acceptance = review of milestone commits bd7857f..HEAD
