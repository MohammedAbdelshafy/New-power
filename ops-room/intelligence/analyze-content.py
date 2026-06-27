#!/usr/bin/env python3
"""
Content Intelligence Analyzer
Accepts a YouTube or Instagram URL and extracts full strategic DNA:
hooks, structure, pacing, techniques, CTAs, engagement signals.
Outputs a structured JSON report saved to ops-room/operations/queue/.
"""

import sys
import json
import re
import subprocess
import hashlib
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = REPO_ROOT / "ops-room" / "operations" / "queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "youtube" in host or "youtu.be" in host:
        return "youtube"
    if "instagram" in host:
        return "instagram"
    if "tiktok" in host:
        return "tiktok"
    return "unknown"


def extract_youtube(url: str) -> dict:
    """Use yt-dlp to pull full metadata + auto-generated transcript."""
    print(f"[youtube] Fetching metadata for: {url}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--skip-download", url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip(), "raw": None}
        data = json.loads(result.stdout)
    except FileNotFoundError:
        print("[youtube] yt-dlp not installed. Falling back to metadata-only mode.")
        return {"error": "yt-dlp not available", "raw": None}
    except subprocess.TimeoutExpired:
        return {"error": "yt-dlp timed out", "raw": None}

    # Pull subtitles/transcript if available
    transcript_text = ""
    try:
        sub_result = subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--sub-lang", "en",
             "--skip-download", "--output", "/tmp/yt-transcript", url],
            capture_output=True, text=True, timeout=90
        )
        vtt_files = list(Path("/tmp").glob("yt-transcript*.vtt"))
        srt_files = list(Path("/tmp").glob("yt-transcript*.srt"))
        for f in vtt_files + srt_files:
            raw = f.read_text(errors="ignore")
            # Strip VTT/SRT timestamps
            clean = re.sub(r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}", "", raw)
            clean = re.sub(r"WEBVTT.*?\n\n", "", clean, flags=re.DOTALL)
            clean = re.sub(r"<[^>]+>", "", clean)
            transcript_text = " ".join(clean.split())
            f.unlink()
    except Exception:
        pass

    return {
        "id": data.get("id"),
        "title": data.get("title"),
        "channel": data.get("uploader"),
        "duration_seconds": data.get("duration"),
        "view_count": data.get("view_count"),
        "like_count": data.get("like_count"),
        "upload_date": data.get("upload_date"),
        "description": data.get("description", "")[:2000],
        "tags": data.get("tags", [])[:30],
        "categories": data.get("categories", []),
        "transcript": transcript_text[:8000] if transcript_text else "",
        "thumbnail": data.get("thumbnail"),
    }


def extract_instagram(url: str) -> dict:
    """Fetch Instagram public post metadata via web."""
    print(f"[instagram] Fetching public data for: {url}")
    # Try yt-dlp first (works for reels)
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--skip-download", url],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "description": data.get("description", "")[:2000],
                "duration_seconds": data.get("duration"),
                "view_count": data.get("view_count"),
                "like_count": data.get("like_count"),
                "uploader": data.get("uploader"),
                "tags": data.get("tags", [])[:20],
                "thumbnail": data.get("thumbnail"),
            }
    except Exception:
        pass
    return {"error": "Could not fetch Instagram data — ensure yt-dlp is installed and the post is public."}


def analyze_techniques(meta: dict, platform: str) -> dict:
    """Extract strategic techniques from the content metadata."""
    techniques = []
    hooks = []
    ctas = []

    title = meta.get("title", "")
    description = meta.get("description", "")
    transcript = meta.get("transcript", "")
    full_text = f"{title}\n{description}\n{transcript}".lower()

    # Hook patterns
    hook_patterns = [
        (r"\b(wait|stop|before you|secret|nobody tells|most people don't|truth about|i tried|what if|here's why)\b", "Curiosity / Pattern Interrupt Hook"),
        (r"\b(in \d+ (seconds|minutes|days|weeks)|step \d+|number \d+)\b", "Numbered / Timed Promise Hook"),
        (r"\b(mistake|wrong|failed|i was wrong|don't do this)\b", "Anti-advice / Failure Hook"),
        (r"\b(how (i|we|you) (made|earned|built|grew|scaled|went from))\b", "Transformation Story Hook"),
        (r"\b(this changed everything|game changer|changed my life|blew my mind)\b", "Revelation Hook"),
    ]
    for pattern, label in hook_patterns:
        if re.search(pattern, full_text):
            hooks.append(label)

    # CTA patterns
    cta_patterns = [
        (r"\b(subscribe|follow|like|comment|share|save this)\b", "Subscribe / Engage CTA"),
        (r"\b(link in (bio|description)|check out|click here|swipe up)\b", "Link / Navigate CTA"),
        (r"\b(free|download|get|grab|join|sign up)\b", "Lead-gen CTA"),
        (r"\b(drop (a|your)|let me know|tell me)\b", "Comment Bait CTA"),
    ]
    for pattern, label in cta_patterns:
        if re.search(pattern, full_text):
            ctas.append(label)

    # Structure techniques
    duration = meta.get("duration_seconds", 0) or 0
    if duration < 60:
        techniques.append("Short-form: sub-60s optimized for retention loops")
    elif duration < 600:
        techniques.append("Mid-form: 1-10min value-dense format")
    else:
        techniques.append("Long-form: deep-dive authority content")

    if len(meta.get("tags", [])) > 10:
        techniques.append("Tag-heavy SEO strategy")

    views = meta.get("view_count") or 0
    likes = meta.get("like_count") or 0
    if views > 0 and likes > 0:
        engagement_rate = (likes / views) * 100
        techniques.append(f"Engagement rate: {engagement_rate:.2f}% likes/views")
        if engagement_rate > 5:
            techniques.append("High engagement — strong audience-to-creator connection signal")

    # Transcript-based techniques
    if transcript:
        word_count = len(transcript.split())
        words_per_min = (word_count / duration * 60) if duration > 0 else 0
        if words_per_min > 150:
            techniques.append(f"Fast pacing: ~{int(words_per_min)} words/min (high energy delivery)")
        elif words_per_min > 0:
            techniques.append(f"Measured pacing: ~{int(words_per_min)} words/min")

        # Storytelling signals
        if re.search(r"\b(i remember|one day|back when|story|imagine)\b", transcript.lower()):
            techniques.append("Storytelling / Narrative structure")
        if re.search(r"\b(step \d|first|second|third|finally|next)\b", transcript.lower()):
            techniques.append("Sequential / Step-by-step structure")
        if re.search(r"\b(data|study|research|statistics|percent)\b", transcript.lower()):
            techniques.append("Authority via data / research citations")

    return {
        "hooks_detected": list(set(hooks)),
        "ctas_detected": list(set(ctas)),
        "structural_techniques": techniques,
        "implementation_tasks": build_implementation_tasks(hooks, ctas, techniques, meta),
    }


def build_implementation_tasks(hooks, ctas, techniques, meta) -> list:
    """Convert detected patterns into concrete implementation tasks."""
    tasks = []
    if hooks:
        tasks.append({
            "priority": "HIGH",
            "task": "Apply detected hook pattern to your content/copy",
            "detail": f"Use: {hooks[0]} — rewrite your opening line to match this pattern.",
        })
    if ctas:
        tasks.append({
            "priority": "HIGH",
            "task": "Integrate CTAs into your funnel",
            "detail": f"Detected CTAs: {', '.join(ctas)}. Add equivalent touchpoints to your project.",
        })
    for t in techniques:
        if "engagement rate" in t.lower() and "high" in t.lower():
            tasks.append({
                "priority": "MEDIUM",
                "task": "Replicate high-engagement content structure",
                "detail": "This piece has >5% engagement. Study its comment section for community-building cues.",
            })
        if "storytelling" in t.lower():
            tasks.append({
                "priority": "MEDIUM",
                "task": "Add a personal story arc to your next content piece",
                "detail": "Use: situation → conflict → resolution structure.",
            })
        if "step-by-step" in t.lower():
            tasks.append({
                "priority": "LOW",
                "task": "Restructure your tutorial/guide content into numbered steps",
                "detail": "Numbered lists increase scannability and completion rate.",
            })
    return tasks


def save_to_queue(url: str, platform: str, meta: dict, analysis: dict) -> Path:
    slug = hashlib.md5(url.encode()).hexdigest()[:8]
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = QUEUE_DIR / f"{ts}-{platform}-{slug}.json"
    payload = {
        "url": url,
        "platform": platform,
        "queued_at": datetime.utcnow().isoformat(),
        "status": "queued",
        "metadata": meta,
        "analysis": analysis,
    }
    filename.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return filename


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze-content.py <youtube-or-instagram-url>")
        sys.exit(1)

    url = sys.argv[1]
    platform = detect_platform(url)
    print(f"[ops-room] Platform detected: {platform}")

    if platform == "youtube":
        meta = extract_youtube(url)
    elif platform in ("instagram", "tiktok"):
        meta = extract_instagram(url)
    else:
        print(f"[ops-room] Unsupported platform. Supported: YouTube, Instagram, TikTok.")
        sys.exit(1)

    if "error" in meta and meta["error"]:
        print(f"[ops-room] Warning: {meta['error']}")

    analysis = analyze_techniques(meta, platform)
    out_file = save_to_queue(url, platform, meta, analysis)

    print(f"\n[ops-room] Analysis complete. Saved to: {out_file.relative_to(REPO_ROOT)}")
    print("\n=== TECHNIQUES DETECTED ===")
    for h in analysis["hooks_detected"]:
        print(f"  HOOK: {h}")
    for t in analysis["structural_techniques"]:
        print(f"  TECH: {t}")
    for c in analysis["ctas_detected"]:
        print(f"  CTA:  {c}")
    print("\n=== IMPLEMENTATION TASKS ===")
    for task in analysis["implementation_tasks"]:
        print(f"  [{task['priority']}] {task['task']}")
        print(f"         → {task['detail']}")
    print(f"\nFull report: {out_file}")


if __name__ == "__main__":
    main()
