---
id: M-008
title: "MBM-Social MVP spine: 1 long video in, 3 watchable vertical clips out"
objective: "A runnable pipeline (intake → transcribe → hook-pick → rank → render) proving clip quality on real content"
priority: P1
phase: 2
dependencies: []
role: crm-brain
required_skills:
  - code
  - analysis
preferred_worker: fabel
fallback_workers:
  - claude
  - antigravity
status: in_progress
owner: fabel
reviewer: human-founder
created: 2026-07-04
due: ""
outputs:
  - MBM-Social/ (pipeline scripts, one module per stage)
  - MBM-Social/quality-thresholds.json
acceptance_criteria:
  - founder-approved test video produces >=3 clips of 20-60s, 9:16, normalized audio
  - hook selection is LLM-driven and each clip ships with its hook line + predicted scores
  - every stage emits events to the existing bus (StageStarted/StageCompleted/ClipRejected)
  - each stage restartable from its input artifacts; no monolith
  - no new frameworks - plain scripts (yt-dlp, faster-whisper, ffmpeg) driven as missions
artifacts: []
---

## Context
See Artifacts/Clipping_Pipeline_Audit.md. Critical path is hook quality, not rendering. Arabic support is the wedge (Competitive_Analysis.md) — test with one AR and one EN video.

## Instructions
Build inside `MBM-Social/` at repo root as stage scripts + a thin runner reading a job file. Reuse the event bus via `scripts/mbm.sh emit`. Do NOT build a queue/orchestrator — Mission Control is the orchestrator (Article 6).

## Lessons Learned
(fill before completion — Article 7)

## Log
- 2026-07-04 created by fabel per M-011 pipeline audit
- 2026-07-04 claimed by fabel
- 2026-07-04 started
