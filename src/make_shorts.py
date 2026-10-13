#!/usr/bin/env python3
"""Render planned excerpts from a master video into vertical Shorts."""
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EPISODE=ROOT/"episodes/current"
def safe_name(value):
    name=re.sub(r"[^a-zA-Z0-9_-]+","-",value.strip()).strip("-").lower()
    return name[:70] or "short"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=EPISODE/"source.mp4")
    p.add_argument("--plan",type=Path,default=EPISODE/"clips.json")
    p.add_argument("--output",type=Path,default=ROOT/"output/shorts")
    a=p.parse_args()
    if not a.source.is_file(): print(f"Missing source video: {a.source}",file=sys.stderr); return 2
    if not a.plan.is_file(): print(f"Missing clip plan: {a.plan}",file=sys.stderr); return 2
    plan=json.loads(a.plan.read_text(encoding="utf-8")); clips=plan.get("clips",[])
    if not clips: print("Clip plan contains no clips.",file=sys.stderr); return 2
    a.output.mkdir(parents=True,exist_ok=True); manifest=[]
    for i,c in enumerate(clips,1):
        start,end=float(c["start"]),float(c["end"]); duration=end-start
        if start<0 or duration<=0: raise ValueError(f"Invalid start/end for clip {i}")
        title=str(c.get("title",f"Clip {i}")).strip(); desc=str(c.get("description","")).strip()
        filename=f"{i:02d}-{safe_name(title)}.mp4"; target=a.output/filename
        vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p"
        cmd=["ffmpeg","-hide_banner","-y","-ss",str(start),"-i",str(a.source),"-t",str(duration),"-vf",vf,"-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-movflags","+faststart",str(target)]
        print(f"Rendering {filename} ({start:.1f}s–{end:.1f}s)"); subprocess.run(cmd,check=True)
        manifest.append({"file":filename,"title":title,"description":desc,"start_seconds":start,"end_seconds":end,"duration_seconds":round(duration,2),"aspect_ratio":"9:16","upload_status":"not_uploaded"})
    (a.output/"metadata.json").write_text(json.dumps({"episode_title":plan.get("episode_title",""),"clips":manifest},indent=2),encoding="utf-8")
    (a.output/"UPLOAD_CHECKLIST.md").write_text("# Shorts upload checklist\n\n"+"".join(f"- [ ] {x['title']} — {x['file']}\n" for x in manifest)+"\nConfirm rights, captions, title, and destination before publishing.\n",encoding="utf-8")
    print(f"Rendered {len(manifest)} Shorts to {a.output}"); return 0
if __name__=="__main__": raise SystemExit(main())
