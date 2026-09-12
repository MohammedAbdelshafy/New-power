"""Stage 00 - Source Intake: URL (yt-dlp) or local file -> source.mp4 + probe metadata."""
import shutil, subprocess
from pathlib import Path
from . import common


def stage(job_dir: Path, out: Path):
    job = common.load(job_dir / "job.json")
    src = job["source"]
    if src.startswith(("http://", "https://")):
        subprocess.run(["yt-dlp", "-f", "mp4/best", "-o", str(out), src], check=True)
    else:
        p = Path(src)
        if not p.is_absolute():
            p = common.REPO / p
        if not p.exists():
            raise FileNotFoundError(f"source not found: {p}")
        shutil.copy(p, out)
    meta = {"duration_s": common.ffprobe_duration(out), "origin": src}
    common.save(job_dir / "source_meta.json", meta)
