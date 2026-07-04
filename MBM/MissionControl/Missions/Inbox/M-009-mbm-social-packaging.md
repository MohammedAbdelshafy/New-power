---
id: M-009
title: "MBM-Social packaging: captions, thumbnails, QC gates, publish-ready bundles"
objective: "Every M-008 clip becomes a bundle a human can post in under 10 minutes: styled captions (AR/EN), thumbnail, title, tags, schedule slot"
priority: P1
phase: 2
dependencies:
  - M-008
role: content-engine
required_skills:
  - code
  - writing
  - arabic
preferred_worker: fabel
fallback_workers:
  - claude
status: inbox
owner: ""
reviewer: human-founder
created: 2026-07-04
due: ""
outputs:
  - MBM-Social/ (caption, thumbnail, packaging stages)
  - MBM/CRM/content/clips/ (publish packages ledger)
acceptance_criteria:
  - burned-in styled captions incl. correct RTL Arabic rendering
  - thumbnail per clip (frame pick + title overlay)
  - publish package folder per clip (mp4, cover, title, description, tags, target platform)
  - QC thresholds from quality-thresholds.json enforced; rejects emit ClipRejected with reason
  - publishing itself stays human-gated (Article 5)
artifacts: []
---

## Context
Turns M-008 output into sellable deliverables. Package ledger lives in the existing CRM content tree — no parallel storage.

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by fabel per M-011 pipeline audit
