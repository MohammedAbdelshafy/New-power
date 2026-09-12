"""Stage 07 - Publishing Package: per-clip bundle a human can post in minutes.

publish/clip_NN/ contains final.mp4, cover.jpg and meta.json (title, hook,
description, hashtags, predicted scores, platform hints). Publishing itself is
HUMAN-GATED (Article 5): this stage prepares, a person posts. The package
ledger is mirrored into the CRM content tree - no parallel storage.
"""
import shutil
from pathlib import Path
from . import common

TAGS = {"ar": ["#ريلز", "#مصر", "#السعودية", "#محتوى"],
        "en": ["#shorts", "#reels", "#viral", "#clip"]}


def stage(job_dir: Path, out: Path):
    job = common.load(job_dir / "job.json")
    tr_lang = common.load(job_dir / "transcript.json")["language"]
    sel = common.load(job_dir / "selected.json")["selected"]
    outdir = out.parent  # out is the .done sentinel; artifacts live beside it
    outdir.mkdir(parents=True, exist_ok=True)
    ledger = []
    for i, c in enumerate(sel, 1):
        d = outdir / f"clip_{i:02d}"
        d.mkdir(exist_ok=True)
        shutil.copy(job_dir / "clips_captioned" / f"clip_{i:02d}.mp4", d / "final.mp4")
        shutil.copy(job_dir / "covers" / f"clip_{i:02d}.jpg", d / "cover.jpg")
        meta = {"title": c["hook_line"][:90], "hook": c["hook_line"],
                "description": c["text"][:300],
                "hashtags": TAGS.get(tr_lang, TAGS["en"]),
                "duration_s": round(c["end"] - c["start"], 1),
                "predicted_scores": c.get("predicted", {}),
                "platforms": ["tiktok", "youtube-shorts", "instagram-reels"],
                "publishing": "HUMAN-GATED per Constitution Article 5"}
        common.save(d / "meta.json", meta)
        ledger.append({"clip": f"clip_{i:02d}", **meta})
    crm = common.REPO / "MBM" / "CRM" / "content" / "clips"
    crm.mkdir(parents=True, exist_ok=True)
    common.save(crm / f"{job_dir.name}-ledger.json",
                {"job": job_dir.name, "source": job["source"], "clips": ledger})
    out.touch()
