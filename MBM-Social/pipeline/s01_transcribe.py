"""Stage 01 - Speech Factory: faster-whisper (CPU) -> transcript.json.

Word timestamps kept per segment. Language from job.json ("ar"/"en") or
auto-detect. A pre-existing transcript can be injected by placing
transcript.json in the job dir (the stage then skips - restartability rule).
"""
from pathlib import Path
from . import common


def stage(job_dir: Path, out: Path):
    from faster_whisper import WhisperModel
    job = common.load(job_dir / "job.json")
    model = WhisperModel(job.get("whisper_model", "base"), device="cpu",
                         compute_type="int8", cpu_threads=4)
    segments, info = model.transcribe(str(job_dir / "source.mp4"),
                                      language=job.get("language") or None,
                                      word_timestamps=True, vad_filter=True)
    data = {"language": info.language, "language_prob": round(info.language_probability, 3),
            "segments": []}
    for s in segments:
        data["segments"].append({
            "start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
            "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)}
                      for w in (s.words or [])],
        })
    if not data["segments"]:
        raise RuntimeError("empty transcript - no speech detected")
    common.save(out, data)
