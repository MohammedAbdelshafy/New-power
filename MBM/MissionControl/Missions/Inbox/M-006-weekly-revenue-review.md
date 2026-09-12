---
id: M-006
title: "Weekly revenue review (recurring — every Sunday)"
objective: "A weekly review naming ONE bottleneck and filing next week's top-3 missions"
priority: P1
phase: 1
dependencies: []
role: chief-revenue-officer
required_skills:
  - strategy
  - analysis
preferred_worker: claude
fallback_workers:
  - fabel
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: 2026-07-06
outputs:
  - MBM/MissionControl/Artifacts/revenue-reviews/
acceptance_criteria:
  - review file in Artifacts/revenue-reviews/ per the CRO SOP
  - ONE bottleneck named
  - next week's top-3 missions filed in Inbox
artifacts: []
---

## Context
Recurring heartbeat. On completion, immediately file next Sunday's copy (increment the id). Phase 6 automates the trigger (cron/GitHub Action); until then any session on/after Sunday runs it.

## Instructions
Execute the Weekly Revenue Review SOP in `Workers/01-chief-revenue-officer.md`. In Claude Code: `/mbm-revenue-review`.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by CRO
- 2026-07-04 migrated to mission schema v2
