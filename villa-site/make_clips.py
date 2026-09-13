#!/usr/bin/env python3
"""Cut a villa tour video into scroll-scrubbable clips.

Only for REAL footage (drone, gimbal, an owner's reel). Photos do NOT need this: the page
animates the full-resolution stills in CSS, which is sharper, ~20x lighter and correct on
phones — encoding a still into 72 all-intra frames cost 2.5-9 MB per photo for no gain.

  python3 make_clips.py <slug> [--seconds 4] [--width 1280] [--only 0,1,3]

Ken Burns moves (zoom in / zoom out / pan) rendered with ffmpeg, one keyframe per
frame so the browser can seek to any scroll position instantly. Clips land in
villa-site/media/<slug>/clip-NN.mp4 and are written into villas/<slug>.json as
"tour_clips" (relative src, works on Vercel and locally). Re-run generate_villa.py after.

If the owner has a real video (drone, gimbal, Insta reel): drop it in media/<slug>/
and run  python3 make_clips.py <slug> --from-video path.mp4  (split into 4 s beats).
"""
import json, os, sys, pathlib, subprocess, argparse, shutil, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
FFMPEG = os.environ.get("FFMPEG") or next((p for p in [os.path.expanduser("~/.local/ffmpeg/ffmpeg"), shutil.which("ffmpeg"),
          os.path.expanduser("~/Claude/ac-instagram/machine/bin/ffmpeg")] if p and os.path.exists(p)), None)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"

MOVES = [  # zoompan expressions, N = frames
    "z='1+0.14*on/N':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",          # slow push in, centre
    "z='1.14-0.14*on/N':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",       # pull out
    "z='1.12':x='(iw-iw/zoom)*on/N':y='ih/2-(ih/zoom/2)'",                # pan left -> right
    "z='1.12':x='(iw-iw/zoom)*(1-on/N)':y='ih/2-(ih/zoom/2)'",            # pan right -> left
    "z='1+0.12*on/N':x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/N)'",     # push in, drifting up
]

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f: f.write(r.read())

def render(src_img, out_mp4, move, seconds=4, width=1600, fps=24):
    n = seconds * fps; h = round(width * 9 / 16 / 2) * 2
    vf = (f"scale=3840:-2,zoompan={move.replace('N', str(n))}:d={n}:s={width}x{h}:fps={fps},format=yuv420p")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-i", str(src_img), "-vf", vf, "-frames:v", str(n),
           "-c:v", "libx264", "-g", "1", "-keyint_min", "1", "-crf", "21", "-preset", "slow", "-profile:v", "high", "-movflags", "+faststart", "-an", str(out_mp4)]
    subprocess.run(cmd, check=True)

def split_video(video, out_dir, seconds=4, width=1280):
    """Owner video -> 4 s beats, re-encoded all-keyframes for scrubbing."""
    dur = float(subprocess.run([FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())
    clips = []
    for i, t in enumerate(range(0, int(dur), seconds)):
        out = out_dir / f"clip-{i+1:02d}.mp4"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(t), "-t", str(seconds), "-i", str(video), "-an", "-vf", f"scale={width}:-2,fps=24",
                        "-c:v", "libx264", "-g", "1", "-keyint_min", "1", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], check=True)
        clips.append(out)
    return clips

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("--seconds", type=int, default=3); ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--only", help="comma-separated photo indexes"); ap.add_argument("--from-video")
    a = ap.parse_args()
    if not FFMPEG: sys.exit("ffmpeg not found (set FFMPEG=/path/to/ffmpeg)")
    if not a.from_video:
        sys.exit("Photos are animated in CSS by the page itself — no clips needed.\n"
                 "Use this only for real footage:  make_clips.py <slug> --from-video tour.mp4")
    cfg_path = HERE / "villas" / f"{a.slug}.json"; cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    media = HERE / "media" / a.slug; media.mkdir(parents=True, exist_ok=True)
    clips = []
    if a.from_video:
        for i, out in enumerate(split_video(pathlib.Path(a.from_video), media, a.seconds, a.width)):
            cap = cfg["photos"][i]["caption"] if i < len(cfg["photos"]) else ""
            clips.append({"src": f"media/{a.slug}/{out.name}", "caption": cap})
    else:
        idx = [int(i) for i in a.only.split(",")] if a.only else list(range(len(cfg["photos"])))
        tmp = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / f"clips-{a.slug}"; tmp.mkdir(parents=True, exist_ok=True)
        for k, i in enumerate(idx):
            p = cfg["photos"][i]; src = tmp / f"{i:02d}.jpg"
            if not src.exists(): download((p.get("url_hd") or p["url"]).replace("im_w=1920", "im_w=2560").replace("im_w=1440", "im_w=2560"), src)
            out = media / f"clip-{k+1:02d}.mp4"
            render(src, out, MOVES[k % len(MOVES)], a.seconds, a.width)
            clips.append({"src": f"media/{a.slug}/{out.name}", "caption": p.get("caption", ""), "poster": p["url"]})
            print("clip", out.name, f"{out.stat().st_size/1e6:.1f} MB", p.get("caption", ""))
    cfg["tour_clips"] = clips
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(clips)} clips -> {media.relative_to(HERE.parent)}, tour_clips written to {cfg_path.name}. Now: python3 generate_villa.py villas/{a.slug}.json")

if __name__ == "__main__":
    main()
