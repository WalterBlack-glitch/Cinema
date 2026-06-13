#!/usr/bin/env python3
"""Animate a still image into a short clip with a camera move (Ken Burns).

A free, offline fallback when AI video generation isn't available (e.g. Higgsfield
free plan blocks video): give it a generated still and it produces a moving short by
cropping/zooming/panning across the frame. Not AI motion — a digital camera move over
a static image — but it yields a real cinematic short instantly.

Moves: push-in, pull-out, pan-left, pan-right, pan-up, pan-down, orbit-ish (zoom+pan).

Usage:
  python still_to_short.py img.png -o short.mp4 --move push-in --seconds 6
  python still_to_short.py img.png -o short.mp4 --move pan-right --zoom 1.15 --fps 30 --size 1280x720

Requires opencv-python + numpy (already used by the other scripts). No ffmpeg needed.
"""
import argparse
import sys
from pathlib import Path


def lerp(a, b, t):
    return a + (b - a) * t


def crop_resize(img, cx, cy, zoom, out_w, out_h, cv2):
    """Crop a window centered at (cx,cy) sized by zoom, resize to out dims."""
    h, w = img.shape[:2]
    win_w, win_h = w / zoom, h / zoom
    x0 = min(max(cx - win_w / 2, 0), w - win_w)
    y0 = min(max(cy - win_h / 2, 0), h - win_h)
    crop = img[int(y0):int(y0 + win_h), int(x0):int(x0 + win_w)]
    return cv2.resize(crop, (out_w, out_h), interpolation=cv2.INTER_CUBIC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("-o", "--out", default="short.mp4")
    ap.add_argument("--move", default="push-in",
                    choices=["push-in", "pull-out", "pan-left", "pan-right",
                             "pan-up", "pan-down"])
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--zoom", type=float, default=1.25, help="max zoom factor")
    ap.add_argument("--size", default="1280x720", help="output WxH")
    a = ap.parse_args()

    try:
        import cv2
        import numpy as np  # noqa: F401
    except ImportError:
        print("ERROR: needs opencv-python + numpy.", file=sys.stderr)
        sys.exit(1)

    img = cv2.imread(a.image)
    if img is None:
        print(f"ERROR: cannot read {a.image}", file=sys.stderr)
        sys.exit(1)
    h, w = img.shape[:2]
    out_w, out_h = (int(x) for x in a.size.lower().split("x"))
    # upscale source so the crop never runs out of pixels
    target = max(out_w, out_h) * max(2, int(a.zoom) + 2)
    if max(w, h) < target:
        s = target / max(w, h)
        img = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_CUBIC)
        h, w = img.shape[:2]

    n = max(1, int(a.seconds * a.fps))
    z, pan = a.zoom, 0.18  # pan amplitude as fraction of width/height

    # Salida H.264 (avc1) + yuv420p + faststart vía ffmpeg, así reproduce en
    # navegadores/WebView2. OpenCV `mp4v` (MPEG-4 Part 2) NO lo decodifica
    # Chromium. Si ffmpeg no está, fallback a OpenCV avc1, y si no, mp4v.
    import subprocess, shutil
    ffmpeg = None
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg = shutil.which("ffmpeg")

    def frames():
        for i in range(n):
            t = i / (n - 1) if n > 1 else 1.0
            cx, cy, zoom = w / 2, h / 2, z
            if a.move == "push-in":
                zoom = lerp(1.0, z, t)
            elif a.move == "pull-out":
                zoom = lerp(z, 1.0, t)
            elif a.move == "pan-left":
                zoom = z; cx = lerp(w * (0.5 + pan), w * (0.5 - pan), t)
            elif a.move == "pan-right":
                zoom = z; cx = lerp(w * (0.5 - pan), w * (0.5 + pan), t)
            elif a.move == "pan-up":
                zoom = z; cy = lerp(h * (0.5 + pan), h * (0.5 - pan), t)
            elif a.move == "pan-down":
                zoom = z; cy = lerp(h * (0.5 - pan), h * (0.5 + pan), t)
            yield crop_resize(img, cx, cy, zoom, out_w, out_h, cv2)

    if ffmpeg:
        NO_WIN = 0x08000000 if sys.platform == "win32" else 0
        cmd = [ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
               "-pix_fmt", "bgr24", "-s", f"{out_w}x{out_h}", "-r", str(a.fps),
               "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart",
               a.out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, creationflags=NO_WIN)
        for f in frames():
            p.stdin.write(f.tobytes())
        p.stdin.close(); p.wait()
        if p.returncode != 0:
            print("ERROR: ffmpeg falló.", file=sys.stderr); sys.exit(1)
        print(f"Wrote {a.out} ({a.seconds}s @ {a.fps}fps, {a.move}, H.264).")
        return

    # fallback sin ffmpeg
    for cc in ("avc1", "H264", "mp4v"):
        vw = cv2.VideoWriter(a.out, cv2.VideoWriter_fourcc(*cc), a.fps, (out_w, out_h))
        if vw.isOpened():
            break
    if not vw.isOpened():
        print("ERROR: VideoWriter no abre.", file=sys.stderr); sys.exit(1)
    for f in frames():
        vw.write(f)
    vw.release()
    print(f"Wrote {a.out} ({a.seconds}s @ {a.fps}fps, {a.move}, {cc}).")


if __name__ == "__main__":
    main()
