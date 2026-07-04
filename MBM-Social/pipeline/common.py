"""Shared plumbing for MBM-Social pipeline stages.

A job is a directory under MBM-Social/jobs/<job-id>/ containing job.json and
stage outputs. Stages are restartable: each declares its output artifact and is
skipped when that artifact already exists (unless --force). Every stage run is
timed, memory-measured, and recorded in state.json; lifecycle emits go to the
existing MBM event bus via scripts/mbm.sh emit (Article 4 - no hidden state).
"""
import json, os, resource, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MBM_SH = REPO / "scripts" / "mbm.sh"
ACTOR = os.environ.get("MBM_WORKER", "unknown")


def load(p):
    return json.loads(Path(p).read_text())


def save(p, obj):
    Path(p).write_text(json.dumps(obj, indent=2, ensure_ascii=False))


def emit(event, job_id, note=""):
    subprocess.run(["bash", str(MBM_SH), "emit", event, job_id, ACTOR, note],
                   capture_output=True)


def ffmpeg(*args):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *[str(a) for a in args]]
    subprocess.run(cmd, check=True)


def ffprobe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def run_stage(job_dir, name, output_rel, fn, force=False):
    """Execute one stage with skip-if-done, timing, RSS and event emission."""
    job_dir = Path(job_dir)
    job_id = job_dir.name
    out_path = job_dir / output_rel
    state_p = job_dir / "state.json"
    state = load(state_p) if state_p.exists() else {"stages": {}}

    if out_path.exists() and not force:
        print(f"[{name}] SKIP (output exists: {output_rel})")
        return out_path

    emit("StageStarted", job_id, name)
    t0 = time.time()
    try:
        fn(job_dir, out_path)
    except Exception as e:
        emit("StageFailed", job_id, f"{name}: {e}")
        state["stages"][name] = {"status": "failed", "error": str(e)[:300]}
        save(state_p, state)
        raise
    wall = round(time.time() - t0, 2)
    rss_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
                   + resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024)
    state["stages"][name] = {"status": "ok", "wall_s": wall, "max_rss_mb": rss_mb,
                             "output": str(output_rel)}
    save(state_p, state)
    emit("StageCompleted", job_id, f"{name} {wall}s")
    print(f"[{name}] OK {wall}s (~{rss_mb}MB peak) -> {output_rel}")
    return out_path
