---
id: M-004
title: "Outreach wave 1: sequences for 10 researched leads, human-sent"
objective: "Ten personalized sequences sent by the founder, every lead moved to contacted with follow-up dates set"
priority: P1
phase: 1
dependencies:
  - M-003
role: outreach-agent
required_skills:
  - writing
  - arabic
  - sales
preferred_worker: fabel
fallback_workers:
  - claude
  - chatgpt
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: 2026-07-14
outputs:
  - MBM/CRM/content/outreach/
acceptance_criteria:
  - 10 sequence files in CRM/content/outreach/ marked READY FOR HUMAN REVIEW
  - every first line cites a lead-specific intel fact
  - human has sent email 1 + LinkedIn note for all 10; stages set to contacted
  - follow-up dates set on every lead
artifacts: []
---

## Context
Depends on M-003. Wave 1 goal is replies and meetings, but equally: learning which angle resonates. Follow-up Manager owns the cadence after send.

## Instructions
Execute `Workers/04-outreach-agent.md`. Human review is the hard gate (Decision DL-003). In Claude Code: `/mbm-outreach <lead-id>`.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by CRO
- 2026-07-04 migrated to mission schema v2
