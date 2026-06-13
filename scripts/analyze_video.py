#!/usr/bin/env python3
"""Analyze a reference video for cinematography cues.

Outputs, into --out:
  - keyframes/        evenly-sampled JPGs to VIEW (composition, lens, light)
  - shot keyframes    one frame near the middle of each detected shot
  - analysis.json     fps, resolution, aspect, duration, shot boundaries + durations,
                      per-shot dominant color palette, overall pacing (ASL)
  - report.md         human-readable summary to fold into the Look Recipe

Prefers OpenCV (pip install opencv-python numpy). Falls back to ffmpeg/ffprobe for
metadata + sampled frames if OpenCV is unavailable. Never hard-fails on the optional
palette step.

Usage:
  python analyze_video.py path/to/video.mp4 --out analysis_dir [--samples 12] [--cut-threshold 0.45]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def ffprobe_meta(video):
    if not shutil.which("ffprobe"):
        return None
    r = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration",
        "-show_entries", "format=duration", "-of", "json", str(video),
    ])
    if r.returncode != 0:
        return None
    try:
        data = json.loads(r.stdout)
        st = data.get("streams", [{}])[0]
        num, _, den = st.get("r_frame_rate", "0/1").partition("/")
        fps = float(num) / float(den) if den and float(den) else 0.0
        dur = float(st.get("duration") or data.get("format", {}).get("duration") or 0)
        w, h = int(st.get("width", 0)), int(st.get("height", 0))
        return {"fps": round(fps, 3), "width": w, "height": h, "duration_s": round(dur, 2),
                "aspect": round(w / h, 3) if h else None}
    except Exception:
        return None


def ffmpeg_sample(video, out_dir, samples, duration):
    """Fallback: evenly sample N frames via ffmpeg."""
    if not shutil.which("ffmpeg") or not duration:
        return []
    frames = []
    for i in range(samples):
        t = duration * (i + 0.5) / samples
        fp = out_dir / f"key_{i:03d}.jpg"
        r = run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video),
                 "-frames:v", "1", "-q:v", "3", str(fp)])
        if r.returncode == 0 and fp.exists():
            frames.append(str(fp))
    return frames


def palette_from_frame(frame, k=5):
    """Dominant colors via OpenCV k-means. frame: BGR ndarray. Returns list of #hex."""
    import numpy as np
    import cv2
    small = cv2.resize(frame, (80, 45))
    data = small.reshape(-1, 3).astype("float32")
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    counts = [int((labels == i).sum()) for i in range(k)]
    order = sorted(range(k), key=lambda i: counts[i], reverse=True)
    hexes = []
    for i in order:
        b, g, r = centers[i]
        hexes.append("#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b)))
    return hexes


def analyze_opencv(video, out_dir, samples, cut_threshold):
    import numpy as np
    import cv2

    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = total / fps if fps else 0

    kf_dir = out_dir / "keyframes"
    kf_dir.mkdir(parents=True, exist_ok=True)

    # Shot detection via histogram-correlation drops + evenly sampled keyframes.
    prev_hist = None
    shot_bounds = [0]
    step = max(1, total // 600) if total else 1  # cap work on long clips
    frame_idx = 0
    palettes = []
    keyframes = []
    sample_every = max(1, total // samples) if total else 1

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_idx % step == 0:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            cv2.normalize(hist, hist)
            if prev_hist is not None:
                corr = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                if corr < (1 - cut_threshold):
                    shot_bounds.append(frame_idx)
            prev_hist = hist
        if frame_idx % sample_every == 0 and len(keyframes) < samples:
            fp = kf_dir / f"key_{len(keyframes):03d}.jpg"
            cv2.imwrite(str(fp), frame)
            keyframes.append(str(fp))
            try:
                palettes.append({"t_s": round(frame_idx / fps, 2) if fps else None,
                                 "colors": palette_from_frame(frame)})
            except Exception:
                pass
        frame_idx += 1
    cap.release()

    shot_bounds.append(total)
    shots = []
    for i in range(len(shot_bounds) - 1):
        start_f, end_f = shot_bounds[i], shot_bounds[i + 1]
        if fps:
            shots.append({"index": i, "start_s": round(start_f / fps, 2),
                          "end_s": round(end_f / fps, 2),
                          "duration_s": round((end_f - start_f) / fps, 2)})
    durations = [s["duration_s"] for s in shots if s["duration_s"] > 0]
    asl = round(sum(durations) / len(durations), 2) if durations else None

    return {
        "fps": round(fps, 3), "width": w, "height": h,
        "aspect": round(w / h, 3) if h else None,
        "duration_s": round(duration, 2),
        "shot_count": len(shots), "average_shot_length_s": asl,
        "shots": shots, "keyframes": keyframes, "palettes": palettes,
    }


def write_report(meta, out_dir):
    lines = ["# Reference analysis\n"]
    if meta:
        ar = meta.get("aspect")
        ar_name = ""
        if ar:
            ar_name = ("~2.39:1 (anamorphic)" if ar >= 2.3 else
                       "16:9" if abs(ar - 1.778) < 0.06 else
                       "9:16 vertical" if ar < 0.7 else
                       "1:1" if abs(ar - 1) < 0.06 else f"{ar}:1")
        lines += [
            f"- Resolution: {meta.get('width')}x{meta.get('height')}",
            f"- FPS: {meta.get('fps')}",
            f"- Duration: {meta.get('duration_s')} s",
            f"- Aspect: {ar} {ar_name}",
        ]
        if meta.get("shot_count") is not None:
            lines += [
                f"- Shots detected: {meta.get('shot_count')}",
                f"- Average shot length (ASL): {meta.get('average_shot_length_s')} s "
                f"({'fast cutting' if (meta.get('average_shot_length_s') or 9) < 2 else 'moderate' if (meta.get('average_shot_length_s') or 9) < 5 else 'long takes'})",
            ]
        if meta.get("palettes"):
            lines.append("\n## Sampled palettes (dominant first)")
            for p in meta["palettes"]:
                lines.append(f"- t={p.get('t_s')}s: {'  '.join(p.get('colors', []))}")
    lines += [
        "\n## Next steps",
        "1. VIEW the keyframes in `keyframes/` (Read tool) and score the seven craft axes.",
        "2. Fill `assets/shot_brief_template.md` with the Look Recipe.",
        "3. Map shots to higgsfield CLI commands (references/higgsfield.md + camera_motion.md).",
    ]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", default="analysis")
    ap.add_argument("--samples", type=int, default=12)
    ap.add_argument("--cut-threshold", type=float, default=0.45,
                    help="0-1; higher = fewer cuts detected")
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        print(f"ERROR: not found: {video}", file=sys.stderr)
        sys.exit(1)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = None
    try:
        import cv2  # noqa: F401
        meta = analyze_opencv(video, out_dir, args.samples, args.cut_threshold)
    except ImportError:
        print("OpenCV not installed; falling back to ffmpeg metadata + sampling.", file=sys.stderr)
    except Exception as e:
        print(f"OpenCV analysis failed ({e}); falling back to ffmpeg.", file=sys.stderr)

    if meta is None:
        meta = ffprobe_meta(video) or {}
        kf_dir = out_dir / "keyframes"
        kf_dir.mkdir(parents=True, exist_ok=True)
        meta["keyframes"] = ffmpeg_sample(video, kf_dir, args.samples, meta.get("duration_s", 0))
        meta.setdefault("shot_count", None)

    (out_dir / "analysis.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    write_report(meta, out_dir)
    print(f"Done. Wrote {out_dir}/analysis.json, report.md, and "
          f"{len(meta.get('keyframes', []))} keyframes. VIEW the keyframes next.")


if __name__ == "__main__":
    main()
