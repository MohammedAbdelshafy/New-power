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
status: inbox
owner: ""
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
artifacts: []
---

## Context
Ordered by the founder: every AI worker must operate through the Mission System — no direct prompting, no isolated workflows. v1 (built earlier today) had a 4-state lifecycle, no claim step, no registry, no events, no routing, and convention-only knowledge capture.

## Instructions
Extend, never duplicate (Article 6): upgrade the existing MissionControl/CLI in place. Commit per milestone.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by fabel (this upgrade dogfoods the system it builds)
