#!/usr/bin/env python3
"""
Content Empire — Clip Processor
Downloads, trims, and formats clips for all 3 platforms.

Usage:
  python3 clip-processor.py --url <url> [--trim 0:10-1:00] [--platform all]
  python3 clip-processor.py --file video.mp4 [--trim 0:10-1:00] [--platform all]
  python3 clip-processor.py --batch urls.txt

Outputs (per platform):
  clips/output/youtube/  — 1080x1920 (vertical), max 60s
  clips/output/instagram/ — 1080x1920, max 90s
  clips/output/tiktok/   — 1080x1920, max 60s

Requirements:
  pip install yt-dlp
  apt install ffmpeg  (or brew install ffmpeg)
"""

import sys
import os
import json
import subprocess
import argparse
import re
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR   = PROJECT_ROOT / "clips" / "output"
LOG_FILE     = PROJECT_ROOT / "clips" / "process-log.jsonl"

PLATFORM_SPECS = {
    "youtube": {
        "width": 1080,
        "height": 1920,
        "max_duration_s": 60,
        "fps": 30,
        "format": "mp4",
        "output_dir": OUTPUT_DIR / "youtube"
    },
    "instagram": {
        "width": 1080,
        "height": 1920,
        "max_duration_s": 90,
        "fps": 30,
        "format": "mp4",
        "output_dir": OUTPUT_DIR / "instagram"
    },
    "tiktok": {
        "width": 1080,
        "height": 1920,
        "max_duration_s": 60,
        "fps": 30,
        "format": "mp4",
        "output_dir": OUTPUT_DIR / "tiktok"
    }
}


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def log_result(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def check_ytdlp() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def download_video(url: str, output_path: Path) -> Path | None:
    """Download video using yt-dlp. Returns path to downloaded file."""
    output_template = str(output_path / "%(title)s.%(ext)s")
    cmd = [
        "yt-dlp",
        "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--output", output_template,
        "--no-playlist",
        url
    ]
    print(f"[download] Fetching: {url}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[download] Error: {result.stderr[:500]}")
        return None

    # Find the downloaded file
    for f in output_path.iterdir():
        if f.suffix in (".mp4", ".mkv", ".webm", ".mov"):
            print(f"[download] Got: {f.name}")
            return f
    return None


def parse_trim(trim_str: str) -> tuple[float, float] | None:
    """Parse '0:10-1:00' → (10.0, 60.0) seconds."""
    if not trim_str:
        return None
    parts = trim_str.split("-")
    if len(parts) != 2:
        return None

    def to_seconds(t: str) -> float:
        segments = t.strip().split(":")
        if len(segments) == 2:
            return float(segments[0]) * 60 + float(segments[1])
        elif len(segments) == 3:
            return float(segments[0]) * 3600 + float(segments[1]) * 60 + float(segments[2])
        return float(segments[0])

    return to_seconds(parts[0]), to_seconds(parts[1])


def process_for_platform(input_file: Path, platform: str, trim: tuple | None, title: str) -> Path | None:
    """Convert video to platform spec using ffmpeg."""
    spec = PLATFORM_SPECS[platform]
    spec["output_dir"].mkdir(parents=True, exist_ok=True)

    safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip().replace(' ', '_')
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    output_file = spec["output_dir"] / f"{ts}-{safe_title}.mp4"

    cmd = ["ffmpeg", "-y"]

    if trim:
        start, end = trim
        duration = min(end - start, spec["max_duration_s"])
        cmd += ["-ss", str(start), "-t", str(duration)]

    cmd += ["-i", str(input_file)]

    # Scale + pad to vertical 9:16
    vf = (
        f"scale={spec['width']}:{spec['height']}:force_original_aspect_ratio=decrease,"
        f"pad={spec['width']}:{spec['height']}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={spec['fps']}"
    )

    cmd += [
        "-vf", vf,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        str(output_file)
    ]

    print(f"[process] {platform}: {output_file.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[process] ffmpeg error for {platform}:\n{result.stderr[-500:]}")
        return None

    size_mb = output_file.stat().st_size / 1024 / 1024
    print(f"[process] {platform} ✓ — {size_mb:.1f} MB")
    return output_file


def process_clip(source: str, trim_str: str | None, platforms: list[str], title: str = "") -> dict:
    """Main processing pipeline — source can be URL or local file path."""
    results = {"source": source, "outputs": {}, "processed_at": utcnow()}

    if not check_ffmpeg():
        print("[error] ffmpeg not found. Install: apt install ffmpeg")
        results["error"] = "ffmpeg not found"
        return results

    temp_dir = PROJECT_ROOT / "clips" / "_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Download if URL
    if source.startswith("http"):
        if not check_ytdlp():
            print("[error] yt-dlp not found. Install: pip install yt-dlp")
            results["error"] = "yt-dlp not found"
            return results
        input_file = download_video(source, temp_dir)
        if not input_file:
            results["error"] = "download failed"
            return results
        if not title:
            title = input_file.stem
    else:
        input_file = Path(source)
        if not input_file.exists():
            print(f"[error] File not found: {source}")
            results["error"] = f"file not found: {source}"
            return results
        if not title:
            title = input_file.stem

    trim = parse_trim(trim_str) if trim_str else None

    for platform in platforms:
        if platform not in PLATFORM_SPECS:
            print(f"[skip] Unknown platform: {platform}")
            continue
        out = process_for_platform(input_file, platform, trim, title)
        results["outputs"][platform] = str(out) if out else "failed"

    log_result(results)
    return results


def batch_process(batch_file: str, trim_str: str | None, platforms: list[str]):
    """Process a list of URLs from a file, one per line."""
    lines = Path(batch_file).read_text().strip().splitlines()
    urls = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
    print(f"[batch] Processing {len(urls)} sources")
    for i, url in enumerate(urls, 1):
        print(f"\n[batch] {i}/{len(urls)}: {url}")
        process_clip(url, trim_str, platforms)


def main():
    parser = argparse.ArgumentParser(description="Content Empire Clip Processor")
    parser.add_argument("--url",      help="Video URL to download and process")
    parser.add_argument("--file",     help="Local video file to process")
    parser.add_argument("--batch",    help="Text file with one URL per line")
    parser.add_argument("--trim",     help="Trim range e.g. '0:10-1:00'")
    parser.add_argument("--platform", default="all", help="all | youtube | instagram | tiktok")
    parser.add_argument("--title",    default="", help="Output title (auto-detected if omitted)")
    args = parser.parse_args()

    platforms = list(PLATFORM_SPECS.keys()) if args.platform == "all" else [args.platform]

    if args.batch:
        batch_process(args.batch, args.trim, platforms)
    elif args.url:
        results = process_clip(args.url, args.trim, platforms, args.title)
        print(f"\n[done] Results: {json.dumps(results['outputs'], indent=2)}")
    elif args.file:
        results = process_clip(args.file, args.trim, platforms, args.title)
        print(f"\n[done] Results: {json.dumps(results['outputs'], indent=2)}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
