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
status: review
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
artifacts:
  - MBM-Social/ (pipeline, runner, prompts, thresholds, docs)
  - MBM-Social/jobs/test-001/publish/ (2 verified packages)
  - MBM/CRM/content/clips/test-001-ledger.json
---

## Context
See Artifacts/Clipping_Pipeline_Audit.md. Critical path is hook quality, not rendering. Arabic support is the wedge (Competitive_Analysis.md) — test with one AR and one EN video.

## Instructions
Build inside `MBM-Social/` at repo root as stage scripts + a thin runner reading a job file. Reuse the event bus via `scripts/mbm.sh emit`. Do NOT build a queue/orchestrator — Mission Control is the orchestrator (Article 6).

## Lessons Learned
- Environment network policy is a first-class dependency: all whisper model CDNs are blocked in this container (BLOCKERS B-1). Designing s01 with an injectable-transcript path kept the whole pipeline testable anyway - build every external-model stage with an injection seam.
- The `.done`-sentinel convention needs one owner: stages treated the sentinel path as their output dir (4 identical bugs). Caught only because the first run was end-to-end, not per-stage - always integration-test the seam between runner and stages first.
- ffmpeg silencedetect gives good-enough segment timing to validate captions without any ASR - useful permanently as a cheap sanity layer.
- QC returning 2 clips instead of the requested 3 from a 66s source was correct behavior; resist the urge to lower thresholds to hit a count.
- espeak-ng + drawtext makes a fully self-contained speech test video - now a reusable pattern for the smoke suite (T-5).

## Log
- 2026-07-04 created by fabel per M-011 pipeline audit
- 2026-07-04 claimed by fabel
- 2026-07-04 started
- 2026-07-04 moved to review
