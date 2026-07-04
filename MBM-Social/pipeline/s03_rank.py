"""Stage 03 - Ranking + Quality Control: candidates -> selected.json.

Applies quality-thresholds.json (hook_min, overlap rules, count) and computes
the predicted score card per clip. All predictions are labeled predicted_* -
they become calibrated only after M-010 closes the analytics loop.
"""
from pathlib import Path
from . import common


def _overlaps(a, b, tol=5.0):
    return not (a["end"] <= b["start"] + tol or b["end"] <= a["start"] + tol)


def stage(job_dir: Path, out: Path):
    th = common.load(common.REPO / "MBM-Social" / "quality-thresholds.json")
    job = common.load(job_dir / "job.json")
    hooks = common.load(job_dir / "hooks.json")
    want = job.get("clips", 3)
    picked, rejected = [], []
    for c in hooks["candidates"]:
        if c["hook_score"] < th["hook_min"]:
            rejected.append({**c, "reject_reason": f"hook {c['hook_score']} < {th['hook_min']}"})
            continue
        if any(_overlaps(c, p) for p in picked):
            rejected.append({**c, "reject_reason": "overlaps a higher-ranked clip"})
            continue
        dur = c["end"] - c["start"]
        c["predicted"] = {
            "hook": c["hook_score"],
            "retention": round(min(100, 55 + c["hook_score"] * 0.3 - max(0, dur - 45)), 1),
            "ctr": round(min(100, 35 + c["hook_score"] * 0.4), 1),
        }
        picked.append(c)
        if len(picked) >= want:
            break
    for r in rejected:
        common.emit("ClipRejected", job_dir.name, r["reject_reason"])
    if not picked:
        raise RuntimeError("QC rejected every candidate - lower thresholds or improve hooks")
    common.save(out, {"selected": picked, "rejected_count": len(rejected),
                      "thresholds": th, "scores_are": "predicted (uncalibrated until M-010)"})
