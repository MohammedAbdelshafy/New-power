"""Stage 02 - Hook Factory: transcript -> candidate clip windows with hook lines.

Two modes, by design (see docs/ARCHITECTURE_UPDATE.md):
- agent mode: if hooks_override.json exists in the job dir, an LLM worker
  (Claude/Fabel following prompts/hook-prompt.md) proposed the hooks. This is
  the production-quality path - the agent IS the hook model in this OS.
- heuristic mode: fallback scoring so the pipeline never stalls without an
  agent: hook-word hits (AR+EN), questions, numbers, speech density, and an
  earliness bonus, over sentence-aligned windows of min-max clip length.
"""
from pathlib import Path
from . import common

HOOK_WORDS_EN = {"secret", "mistake", "never", "why", "how", "money", "free", "stop",
                 "truth", "nobody", "biggest", "wrong", "before", "warning", "proof"}
HOOK_WORDS_AR = {"سر", "خطأ", "أبدا", "ليه", "لماذا", "إزاي", "كيف", "فلوس", "مجانا",
                 "الحقيقة", "أكبر", "غلط", "قبل", "تحذير", "محدش"}


def _score(text, start, total_dur, words_per_s):
    t = text.lower()
    toks = set(t.replace("؟", " ").replace("?", " ").split())
    hits = len(toks & HOOK_WORDS_EN) + len(toks & HOOK_WORDS_AR)
    score = 30 * min(hits, 3) / 3
    if "?" in text or "؟" in text: score += 20
    if any(c.isdigit() for c in text): score += 15
    score += 15 * min(words_per_s / 3.0, 1.0)          # energetic delivery
    score += 20 * (1 - start / max(total_dur, 1))       # earlier material self-contains better
    return round(min(score, 100), 1)


def stage(job_dir: Path, out: Path):
    override = job_dir / "hooks_override.json"
    if override.exists():
        data = common.load(override)
        data["mode"] = "agent"
        common.save(out, data)
        return
    job = common.load(job_dir / "job.json")
    tr = common.load(job_dir / "transcript.json")
    segs = tr["segments"]
    total = common.load(job_dir / "source_meta.json")["duration_s"]
    lo, hi = job.get("clip_len", [20, 60])
    cands = []
    for i, s in enumerate(segs):
        # grow a window from segment i to reach at least lo seconds
        j, end = i, segs[i]["end"]
        while end - s["start"] < lo and j + 1 < len(segs):
            j += 1; end = segs[j]["end"]
        dur = end - s["start"]
        if not (lo <= dur <= hi):
            continue
        text = " ".join(x["text"] for x in segs[i:j + 1])
        nwords = sum(len(x["words"]) or len(x["text"].split()) for x in segs[i:j + 1])
        cands.append({"start": round(s["start"], 2), "end": round(end, 2),
                      "hook_line": s["text"][:120],
                      "hook_score": _score(text, s["start"], total, nwords / max(dur, 1)),
                      "text": text})
    if not cands:
        raise RuntimeError(f"no windows of {lo}-{hi}s fit this transcript")
    cands.sort(key=lambda c: -c["hook_score"])
    common.save(out, {"mode": "heuristic", "candidates": cands[:12]})
