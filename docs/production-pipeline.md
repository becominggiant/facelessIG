# Becoming Giant Studio — Shorts renderer

This repository now contains the first stages of a cloud Shorts pipeline.

## Implemented

- A speech-to-text candidate finder using faster-whisper. It proposes non-overlapping moments from a master video.
- An FFmpeg renderer that center-crops selected moments to 1080×1920 vertical MP4.
- A GitHub Actions workflow that runs candidate detection, renders clips, and packages the output as a short-lived artifact.

## Important limitations

The candidate finder is a first pass, not an editor: inspect clips for context, accurate cuts, and useful standalone meaning. Captions, smart reframing, full episode creation, automated research/script/narration, and direct Rumble upload are not yet implemented. Use Rumble's supported interface until an official supported upload route is verified; never store a Rumble password or session cookie in this repository.

## Run it

The workflow expects a source video at `episodes/current/source.mp4`. Because this repository is public, do not commit private footage or large media files. Before unattended cloud runs, we must connect access-controlled media storage and retrieve the source safely. Avoid putting signed private URLs in workflow inputs or logs.

For local testing, install FFmpeg and run `pip install -r requirements.txt`, then `python3 src/find_short_candidates.py`, followed by `python3 src/make_shorts.py --plan episodes/current/auto_clips.json`.

## Rights and review

Only use footage, images, music, and audio you created or have permission to use. Generated clip titles are drafts and should be reviewed before publishing.

## Next stages

1. Connect access-controlled media storage.
2. Add animated captions and smart reframing.
3. Add long-form assembly, narration, licensed visuals, and episode metadata.
4. Add an upload adapter only after verifying a supported publishing method.
