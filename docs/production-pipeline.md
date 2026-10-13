# Becoming Giant Studio — Shorts renderer

This is the first production stage for the Becoming Giant content pipeline. It renders planned moments from a finished master video into vertical 9:16 clips using FFmpeg, then packages the MP4s and metadata as a GitHub Actions artifact.

## Current status

- Implemented: cloud-rendered vertical clips from a source MP4 and a JSON clip plan.
- Not yet implemented: automatic topic research, AI script generation, voice synthesis, visual asset acquisition, speech-aware moment selection, and direct Rumble upload.
- Publishing: use Rumble's supported interface until an official supported upload route is verified. Do not put a Rumble password or session cookie in this repository.

## Run a test

1. Put a source video at `episodes/current/source.mp4`.
2. Edit `episodes/current/clips.json` with the clip start/end times and titles. Keep clips within the source video's duration.
3. Open **Actions → Render Shorts → Run workflow**.
4. Download the `becoming-giant-shorts` artifact from the completed run.

The repository is currently public. **Do not commit API keys, passwords, private footage, or copyrighted assets you do not have permission to use.** Keep source videos out of Git history; for production, connect private object storage or a permitted media source.

## Clip plan format

```json

{
  "episode_title": "The Convergence: AI, Biology & the Future of Humanity",
  "clips": [
    {
      "start": 12.0,
      "end": 48.0,
      "title": "Are We Becoming Digital Biology?",
      "description": "A short excerpt exploring the convergence of AI and biology."
    }
  ]
}
```

Times are seconds. Aim for 20–60 seconds per clip initially. The renderer center-crops to 9:16; footage with important information near the edges may need a future smart-reframe stage.

## Next stages

1. Add speech-to-text and transcript-based candidate detection.
2. Add optional AI ranking for hooks, completeness, and factual/rights checks.
3. Add licensed visual sourcing, narration, and long-form assembly.
4. Add a publishing adapter only after confirming the platform's supported upload method.
