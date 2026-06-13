#!/usr/bin/env python3
"""Download a reference video (YouTube or any yt-dlp-supported URL) for analysis.

Wraps yt-dlp: caps at 1080p, prefers mp4, writes into --out (default refs/),
prints the downloaded path so it can be fed straight to analyze_video.py.

Tries the `yt-dlp` executable first, then `python -m yt_dlp`. If neither exists,
prints the install command and exits 2 (the skill should then ask the user for a
local file instead — never block the workflow on this).

Usage:
  python fetch_reference.py "https://youtube.com/watch?v=..." [--out refs] [--max-height 1080]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def ytdlp_cmd():
    if shutil.which("yt-dlp"):
        return ["yt-dlp"]
    probe = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                           capture_output=True, text=True)
    if probe.returncode == 0:
        return [sys.executable, "-m", "yt_dlp"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="refs")
    ap.add_argument("--max-height", type=int, default=1080)
    args = ap.parse_args()

    base = ytdlp_cmd()
    if base is None:
        print("ERROR: yt-dlp not available. Install it with:\n"
              f"  {sys.executable} -m pip install yt-dlp\n"
              "Or ask the user for a local video file instead.", file=sys.stderr)
        sys.exit(2)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    tpl = str(out_dir / "%(title).80s.%(ext)s")
    fmt = (f"bestvideo[height<={args.max_height}][ext=mp4]+bestaudio[ext=m4a]"
           f"/best[height<={args.max_height}][ext=mp4]/best[height<={args.max_height}]")
    cmd = base + ["-f", fmt, "--merge-output-format", "mp4", "--no-playlist",
                  "--restrict-filenames", "-o", tpl,
                  "--print", "after_move:filepath", "--no-simulate", args.url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-2000:], file=sys.stderr)
        sys.exit(1)
    path = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    print(f"Downloaded: {path}\nNext: python scripts/analyze_video.py \"{path}\" --out analysis")


if __name__ == "__main__":
    main()
