#!/usr/bin/env python3
"""Create first-pass Shorts candidates from a video's transcript using faster-whisper."""
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "episodes/current/source.mp4"
DEFAULT_OUTPUT = ROOT / "episodes/current/auto_clips.json"
HOOKS = {"why","how","what","future","risk","danger","change","control","truth","because","imagine","privacy","humanity","ai","biology","brain","data"}

def score(text):
    words = re.findall(r"[A-Za-z0-9']+", text.lower())
    if not words: return -99
    return sum(w in HOOKS for w in words)*0.35 + ("?" in text)*1.4 + bool(re.search(r"\b(but|however|instead|yet)\b", text, re.I))*0.8 - abs(len(words)-65)/65

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--model", choices=["tiny","base","small"], default="base")
    p.add_argument("--count", type=int, default=6)
    p.add_argument("--min-seconds", type=float, default=20)
    p.add_argument("--max-seconds", type=float, default=58)
    a=p.parse_args()
    if not a.source.is_file(): p.error(f"source video not found: {a.source}")
    from faster_whisper import WhisperModel
    model=WhisperModel(a.model, device="cpu", compute_type="int8")
    segments, info=model.transcribe(str(a.source), vad_filter=True)
    segs=[{"start":float(s.start),"end":float(s.end),"text":s.text.strip()} for s in segments if s.text.strip()]
    candidates=[]
    for i, first in enumerate(segs):
        pieces=[]
        for s in segs[i:]:
            if s["end"]-first["start"] > a.max_seconds: break
            pieces.append(s["text"]); duration=s["end"]-first["start"]
            if duration < a.min_seconds: continue
            excerpt=" ".join(pieces).strip()
            candidates.append({"start":round(first["start"],2),"end":round(s["end"],2),"transcript_excerpt":excerpt,"score":score(excerpt)+(0.4 if 28<=duration<=48 else 0)})
    candidates.sort(key=lambda c:c["score"], reverse=True)
    chosen=[]
    for c in candidates:
        if not any(min(c["end"],x["end"])-max(c["start"],x["start"]) > .35*min(c["end"]-c["start"],x["end"]-x["start"]) for x in chosen):
            words=c["transcript_excerpt"].split()
            c["title"]=" ".join(words[:9]).strip(" ,.!?:;—-")[:75] or f"Becoming Giant Short {len(chosen)+1}"
            c["description"]="Excerpt from Becoming Giant. Review context and add episode-specific details before publishing."
            c.pop("score",None); chosen.append(c)
        if len(chosen)>=a.count: break
    chosen.sort(key=lambda c:c["start"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"episode_title":"Becoming Giant","source_file":a.source.name,"language":getattr(info,"language",None),"candidate_count":len(chosen),"clips":chosen,"review_required":True},indent=2),encoding="utf-8")
    print(f"Wrote {len(chosen)} candidate clips to {a.output}")

if __name__=="__main__": main()
