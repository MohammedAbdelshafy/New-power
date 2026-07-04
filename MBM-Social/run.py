#!/usr/bin/env python3
"""MBM-Social pipeline runner.

  python3 MBM-Social/run.py MBM-Social/jobs/<job-id> [--force] [--stages s00,s01,...]

A job dir needs job.json: {"source": "<url-or-path>", "language": "en"|"ar"|null,
"clips": 3, "clip_len": [20, 60], "whisper_model": "base"}.

Stages skip themselves when their output exists (restartable); state, timing
and peak RSS land in state.json; every transition emits to the MBM event bus.
Mission Control is the orchestrator - this runner only sequences one job.
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from pipeline import common
from pipeline import s00_intake, s01_transcribe, s02_hooks, s03_rank, s04_render, \
    s05_captions, s06_thumbnail, s07_package

STAGES = [
    ("s00_intake",     "source.mp4",              s00_intake.stage),
    ("s01_transcribe", "transcript.json",         s01_transcribe.stage),
    ("s02_hooks",      "hooks.json",              s02_hooks.stage),
    ("s03_rank",       "selected.json",           s03_rank.stage),
    ("s04_render",     "clips/.done",             s04_render.stage),
    ("s05_captions",   "clips_captioned/.done",   s05_captions.stage),
    ("s06_thumbnail",  "covers/.done",            s06_thumbnail.stage),
    ("s07_package",    "publish/.done",           s07_package.stage),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job_dir")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--stages", default="", help="comma list, e.g. s04_render,s05_captions")
    args = ap.parse_args()
    job_dir = Path(args.job_dir).resolve()
    if not (job_dir / "job.json").exists():
        sys.exit(f"no job.json in {job_dir}")
    only = set(args.stages.split(",")) if args.stages else None
    common.emit("PipelineStarted", job_dir.name, "")
    for name, out_rel, fn in STAGES:
        if only and name not in only:
            continue
        common.run_stage(job_dir, name, out_rel, fn, force=args.force)
    common.emit("PipelineCompleted", job_dir.name, "publish packages ready (human posts)")
    print(f"\nDONE: {job_dir / 'publish'}")


if __name__ == "__main__":
    main()
