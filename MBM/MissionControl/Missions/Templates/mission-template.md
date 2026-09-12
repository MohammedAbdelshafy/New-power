---
id: M-XXX                      # allocated by scripts/mbm.sh mission new
title: ""
objective: ""                  # ONE sentence: the outcome, not the activity
priority: P1                   # P0 revenue-blocking | P1 important | P2 nice-to-have
phase: 1                       # roadmap phase
dependencies: []               # mission ids that must be Completed first
role: ""                       # MBM/Workers/*.md role that defines the SOP
required_skills: []            # skill tags matching Registry entries (e.g. web-search, arabic, code)
preferred_worker: ""           # Registry id; routing honors this if eligible
fallback_workers: []           # Registry ids, in order
status: inbox                  # inbox|claimed|in_progress|review|completed|blocked|failed|archived
owner: ""                      # Registry id of the claimer (Article 3: one owner)
reviewer: ""                   # who approves Review→Completed; never the owner (Article 10)
created: YYYY-MM-DD
due: ""
outputs: []                    # expected artifact paths (CRM/..., Artifacts/...)
acceptance_criteria:
  - REPLACE with binary, stranger-verifiable criteria
artifacts: []                  # actual output paths, filled at completion
---

## Context
Why this mission exists. Links to leads, prior missions, decisions.

## Instructions
Anything beyond the role's standard SOP.

## Lessons Learned
(fill before completion — Article 7. What worked, what didn't, what the next worker should know. Durable lessons also go to Knowledge_Base/.)

## Log
- YYYY-MM-DD created by <actor>
