---
id: M-002
title: "First lead hunt: 50 leads across recycling, construction, manufacturing (Egypt/GCC)"
objective: "50 scored, signal-backed lead records in the CRM with research missions filed for every qualified lead"
priority: P0
phase: 1
dependencies:
  - M-001
role: lead-hunter
required_skills:
  - web-search
  - research
preferred_worker: claude
fallback_workers:
  - fabel
  - antigravity
  - opencode
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: 2026-07-09
outputs:
  - MBM/CRM/leads/
acceptance_criteria:
  - 50 lead files in CRM/leads/, each with >=1 sourced signal
  - >=15 leads with fit_score >= 60
  - mbm.sh validate passes
  - research missions filed for every qualified lead
artifacts: []
---

## Context
The pipeline is empty. Segments chosen for round 1 play to existing credibility: recycling/waste (insider), construction (New Capital / giga-project activity), manufacturing (industrial zones). Egypt first, then GCC.

## Instructions
Execute `Workers/02-lead-hunter.md` SOP. Prioritize hiring-signal sources (Wuzzuf, LinkedIn Jobs) — they carry the pain signal built in. In Claude Code: `/mbm-lead-hunt`.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by CRO
- 2026-07-04 migrated to mission schema v2
