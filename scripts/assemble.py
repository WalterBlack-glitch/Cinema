#!/usr/bin/env python3
"""Assemble Higgsfield clips into one sequence with ffmpeg.

Hard cuts by default; optional crossfade and music bed. Normalizes all clips to a
common resolution/fps so concat is safe across mixed outputs.

Usage:
  # hard cuts, in the given order
  python assemble.py shot1.mp4 shot2.mp4 shot3.mp4 -o out.mp4

  # from a folder (natural sort), 0.5s crossfades, music trimmed to length
  python assemble.py --dir clips -o out.mp4 --crossfade 0.5 --music track.mp3 --fps 24 --size 1920x1080

Requires ffmpeg on PATH.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(p))]


def collect_clips(args):
    if args.clips:
        return [Path(c) for c in args.clips]
    if args.dir:
        d = Path(args.dir)
        vids = [p for p in d.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}]
        return sorted(vids, key=natural_key)
    return []


def probe_duration(clip):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nk=1:nw=1", str(clip)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def hard_cut(clips, out, w, h, fps, music):
    """Re-encode each clip to common spec, then concat via filter."""
    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    n = len(clips)
    parts = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[v{i}];"
        )
    concat_in = "".join(f"[v{i}]" for i in range(n))
    filt = "".join(parts) + f"{concat_in}concat=n={n}:v=1:a=0[vout]"
    cmd = ["ffmpeg", "-y"] + inputs
    if music:
        cmd += ["-i", str(music)]
    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    if music:
        cmd += ["-map", f"{n}:a", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)]
    return cmd


def crossfade(clips, out, w, h, fps, dur, music):
    """Chain xfade between consecutive clips."""
    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    n = len(clips)
    norm = [
        f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}[n{i}];"
        for i in range(n)
    ]
    durations = [probe_duration(c) for c in clips]
    chain = []
    prev = "n0"
    offset = 0.0
    for i in range(1, n):
        offset += durations[i - 1] - dur
        label = "vout" if i == n - 1 else f"x{i}"
        chain.append(
            f"[{prev}][n{i}]xfade=transition=fade:duration={dur}:offset={offset:.3f}[{label}];"
        )
        prev = label
    filt = "".join(norm) + "".join(chain).rstrip(";")
    cmd = ["ffmpeg", "-y"] + inputs
    if music:
        cmd += ["-i", str(music)]
    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    if music:
        cmd += ["-map", f"{n}:a", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)]
    return cmd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*", help="clip files in order")
    ap.add_argument("--dir", help="folder of clips (natural sort) instead of listing them")
    ap.add_argument("-o", "--out", default="sequence.mp4")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--crossfade", type=float, default=0.0, help="crossfade seconds (0 = hard cuts)")
    ap.add_argument("--music", help="audio bed; trimmed to video length")
    args = ap.parse_args()

    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not found on PATH.", file=sys.stderr)
        sys.exit(1)
    clips = collect_clips(args)
    if len(clips) < 1:
        print("ERROR: no clips. Pass files or --dir.", file=sys.stderr)
        sys.exit(1)
    missing = [c for c in clips if not c.exists()]
    if missing:
        print(f"ERROR: missing clips: {missing}", file=sys.stderr)
        sys.exit(1)
    w, h = args.size.lower().split("x")

    if args.crossfade > 0 and len(clips) > 1:
        cmd = crossfade(clips, args.out, w, h, args.fps, args.crossfade, args.music)
    else:
        cmd = hard_cut(clips, args.out, w, h, args.fps, args.music)

    print("Running ffmpeg on", len(clips), "clips ->", args.out)
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
