# MBM_SOCIAL_AUDIT — 2026-07-04 (post-build)

Supersedes the "0% built" status in `MBM/MissionControl/Artifacts/Clipping_Pipeline_Audit.md` (kept as the pre-build record).

## What exists (after M-008 build, measured on test job `test-001`)

| Stage | Status | Evidence |
|---|---|---|
| s00 intake (yt-dlp/local) | ✅ built, tested (local path) | 66s test source ingested + probed |
| s01 transcribe (faster-whisper) | ✅ built, **untestable in this container** | model CDNs (huggingface.co, openaipublic, alphacephei) blocked by env network policy — see BLOCKERS.md B-1. Injectable-transcript path tested instead |
| s02 hooks (agent + heuristic) | ✅ built, tested | heuristic found 8 candidates; agent path via `hooks_override.json` |
| s03 rank + QC | ✅ built, tested | thresholds enforced; rejects emitted `ClipRejected` events |
| s04 render (9:16 1080×1920 + loudnorm) | ✅ built, tested | 2 clips, 9.4s wall for both |
| s05 captions (ASS burn-in) | ✅ built, tested | frame-verified visually; RTL-capable via libass (AR test pending — B-2) |
| s06 thumbnail | ✅ built, tested | hook-line overlay covers generated |
| s07 package + CRM ledger | ✅ built, tested | `publish/clip_NN/` bundles + `MBM/CRM/content/clips/test-001-ledger.json` |
| events / restartability | ✅ tested | every stage emits Started/Completed/Failed; skip-if-done re-run verified (s00/s01 SKIP on second run) |

## Measured (single run, 66s source, 4 CPU / 16GB container, no GPU)
Total pipeline (excl. transcribe): **21.1s wall**; peak RSS ~556MB (ffmpeg children); hooks/rank <0.3s; render 9.4s; captions 10.7s; thumbnails 0.3s. These are spot numbers — formal multi-video benchmarks are M-010's deliverable.

## Broken / missing / duplicated
- **Missing:** live whisper run (B-1), Arabic end-to-end test (B-2), real founder-approved source video (B-3), scheduling/analytics/creator-profiles/asset-manager (Post-v1 by Revenue-First rule — see SPRINT_PLAN).
- **Fixed during build:** `.done`-sentinel path bug in 4 stages (stages wrote into the sentinel path; caught by the first end-to-end run).
- **Duplicated:** nothing — reuses event bus, CRM, Mission Control; no queue manager built (Mission Control IS the queue), no retry system built (restartable stages + mission re-claim IS the retry system).
