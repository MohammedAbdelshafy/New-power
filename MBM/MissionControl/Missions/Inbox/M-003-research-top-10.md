---
id: M-003
title: "Intel reports for the 10 highest-scoring leads"
objective: "Ten outreach-ready intel reports on the highest-scoring leads"
priority: P1
phase: 1
dependencies:
  - M-002
role: company-researcher
required_skills:
  - web-search
  - research
  - writing
preferred_worker: claude
fallback_workers:
  - fabel
  - chatgpt
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: 2026-07-11
outputs:
  - MBM/CRM/intel/
acceptance_criteria:
  - 10 intel reports in CRM/intel/ meeting the worker's quality bar
  - each has a named entry contact and a specific recommended angle
  - lead files updated to stage researched
artifacts: []
---

## Context
Depends on M-002. Take the top 10 by fit_score; depth beats breadth for wave 1 — these 10 get the best outreach we can write.

## Instructions
Execute `Workers/03-company-researcher.md` per lead. In Claude Code: `/mbm-research <lead-id>`.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by CRO
- 2026-07-04 migrated to mission schema v2
