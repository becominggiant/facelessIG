#!/usr/bin/env python3
"""Render planned excerpts from a master video into vertical Shorts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPISODE_DIR = ROOT / "episodes" / "current"
SOURCE = EPISODE_DIR / "source.mp4"
PLAN = EPISODE_DIR / "clips.json"
OUT = ROOT / "output" / "shorts"


def safe_name(value: str) -> str:
    name = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return name[:70] or "short"


def run() -> int:
    if not SOURCE.is_file():
        print(f"Missing source video: {SOURCE}", file=sys.stderr)
        print("Add a test MP4 at episodes/current/source.mp4 (do not commit large/private footage).", file=sys.stderr)
        return 2
    if not PLAN.is_file():
        print(f"Missing clip plan: {PLAN}", file=sys.stderr)
        return 2

    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    clips = plan.get("clips", [])
    if not clips:
        print("Clip plan contains no clips.", file=sys.stderr)
        return 2

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for index, clip in enumerate(clips, start=1):
        start = float(clip["start"])
        end = float(clip["end"])
        title = str(clip.get("title", f"Clip {index}")).strip()
        description = str(clip.get("description", "")).strip()
        duration = end - start
        if start < 0 or duration <= 0:
            raise ValueError(f"Invalid start/end for clip {index}: {start}, {end}")
        if duration > 90:
            print(f"Warning: clip {index} is {duration:.1f}s; consider keeping Shorts under 60s for this first version.")

        filename = f"{index:02d}-{safe_name(title)}.mp4"
        target = OUT / filename
        vf = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,setsar=1,fps=30,format=yuv420p"
        )
        command = [
            "ffmpeg", "-hide_banner", "-y",
            "-ss", str(start), "-i", str(SOURCE),
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
            str(target),
        ]
        print(f"Rendering {filename} ({start:.1f}s–{end:.1f}s)")
        subprocess.run(command, check=True)
        manifest.append({
            "file": filename,
            "title": title,
            "description": description,
            "start_seconds": start,
            "end_seconds": end,
            "duration_seconds": round(duration, 2),
            "aspect_ratio": "9:16",
            "upload_status": "not_uploaded",
        })

    (OUT / "metadata.json").write_text(
        json.dumps({"episode_title": plan.get("episode_title", ""), "clips": manifest}, indent=2),
        encoding="utf-8",
    )
    checklist = "# Shorts upload checklist\n\n"
    checklist += "".join(f"- [ ] {item['title']} — {item['file']}\n" for item in manifest)
    checklist += "\nConfirm rights, captions, title, and destination before publishing.\n"
    (OUT / "UPLOAD_CHECKLIST.md").write_text(checklist, encoding="utf-8")
    print(f"Rendered {len(manifest)} Shorts to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
