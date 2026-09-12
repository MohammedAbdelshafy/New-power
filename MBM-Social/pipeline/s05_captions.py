"""Stage 05 - Caption Generation: per-clip styled burned-in captions.

Builds an ASS subtitle track from transcript segments inside each clip window
(shifted to clip time), bottom-third, bold outline - readable on mobile. ASS
handles RTL Arabic shaping via libass. Output: clips_captioned/clip_NN.mp4.
"""
from pathlib import Path
from . import common

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginL, MarginR, MarginV
Style: Cap,DejaVu Sans,64,&H00FFFFFF,&H00101010,&H80000000,-1,3,1,2,60,60,260

[Events]
Format: Layer, Start, End, Style, Text
"""


def _ts(t):
    h, rem = divmod(max(t, 0), 3600); m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def stage(job_dir: Path, out: Path):
    tr = common.load(job_dir / "transcript.json")["segments"]
    sel = common.load(job_dir / "selected.json")["selected"]
    outdir = out.parent  # out is the .done sentinel; artifacts live beside it
    outdir.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(sel, 1):
        lines = [ASS_HEADER]
        for s in tr:
            if s["end"] <= c["start"] or s["start"] >= c["end"]:
                continue
            a = max(s["start"], c["start"]) - c["start"]
            b = min(s["end"], c["end"]) - c["start"]
            text = s["text"].replace("\n", " ").strip()
            lines.append(f"Dialogue: 0,{_ts(a)},{_ts(b)},Cap,{text}")
        ass = job_dir / f"cap_{i:02d}.ass"
        ass.write_text("\n".join(lines), encoding="utf-8")
        common.ffmpeg("-i", job_dir / "clips" / f"clip_{i:02d}.mp4",
                      "-vf", f"subtitles={ass}",
                      "-c:v", "libx264", "-preset", "fast", "-crf", "21",
                      "-c:a", "copy", outdir / f"clip_{i:02d}.mp4")
    out.touch()
