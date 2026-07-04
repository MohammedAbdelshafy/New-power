"""Stage 04 - Clip Factory: cut + center-crop to 9:16 1080x1920 + loudness normalize."""
from pathlib import Path
from . import common


def stage(job_dir: Path, out: Path):
    sel = common.load(job_dir / "selected.json")["selected"]
    outdir = out.parent  # out is the .done sentinel; artifacts live beside it
    outdir.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(sel, 1):
        common.ffmpeg(
            "-ss", c["start"], "-to", c["end"], "-i", job_dir / "source.mp4",
            "-vf", "crop=ih*9/16:ih,scale=1080:1920,setsar=1",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            outdir / f"clip_{i:02d}.mp4",
        )
    out.touch()
