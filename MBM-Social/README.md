# MBM-Social — AI clipping pipeline on the MBM OS

Long-form video in → publish-ready vertical clip packages out. Built as **stages on the existing Mission OS** (Architecture_v1): jobs are directories, stages are restartable modules, every transition emits to the MBM event bus, publishing is human-gated (Article 5).

## Run

```bash
mkdir -p MBM-Social/jobs/my-job
cat > MBM-Social/jobs/my-job/job.json <<'EOF'
{"source": "https://youtube.com/watch?v=...", "language": "ar",
 "clips": 3, "clip_len": [20, 60], "whisper_model": "base"}
EOF
export MBM_WORKER=<your-registry-id>
python3 MBM-Social/run.py MBM-Social/jobs/my-job
# output: MBM-Social/jobs/my-job/publish/clip_NN/{final.mp4, cover.jpg, meta.json}
```

Requirements: `ffmpeg`, `pip install faster-whisper yt-dlp`. Stages skip when their output exists — delete an artifact (or `--force --stages sNN_name`) to re-run from any point. A crashed job resumes exactly where it stopped.

## Stages
`s00_intake` (yt-dlp/local) → `s01_transcribe` (faster-whisper, AR/EN, injectable) → `s02_hooks` (agent via `prompts/hook-prompt.md`, heuristic fallback) → `s03_rank` (QC per `quality-thresholds.json`, rejects emit `ClipRejected`) → `s04_render` (9:16 1080×1920, loudnorm) → `s05_captions` (styled ASS burn-in, RTL-safe) → `s06_thumbnail` → `s07_package` (bundle + CRM ledger).

## Quality scores
`predicted_*` scores are heuristic/LLM estimates and stay labeled that way until M-010 calibrates them against real retention data. Tune `quality-thresholds.json` from measurement, not taste.

## Status & plans
`docs/` — audit, task graph, dependencies, sprint plan, architecture note, mission board, blockers, risk register. Missions: M-008 (spine — this code), M-009 (packaging polish), M-010 (validation + real benchmark reports).
