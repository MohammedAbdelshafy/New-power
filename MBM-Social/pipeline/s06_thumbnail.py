"""Stage 06 - Thumbnail Generation: mid-hook frame + hook-line overlay -> covers/clip_NN.jpg."""
from pathlib import Path
from . import common


def stage(job_dir: Path, out: Path):
    sel = common.load(job_dir / "selected.json")["selected"]
    outdir = out.parent  # out is the .done sentinel; artifacts live beside it
    outdir.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(sel, 1):
        title = c["hook_line"].replace("'", "").replace(":", " ").replace('"', "")[:60]
        common.ffmpeg(
            "-ss", round(c["start"] + 1.0, 2), "-i", job_dir / "source.mp4",
            "-frames:v", "1",
            "-vf", ("crop=ih*9/16:ih,scale=1080:1920,"
                    f"drawtext=text='{title}':fontcolor=white:fontsize=72:borderw=4:"
                    "bordercolor=black:x=(w-text_w)/2:y=h*0.12:font=DejaVu Sans"),
            "-q:v", "3", outdir / f"clip_{i:02d}.jpg",
        )
    out.touch()
