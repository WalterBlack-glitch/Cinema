#!/usr/bin/env python3
"""Extract a color grade reference from an image or video frame.

Outputs:
  - <stem>_swatch.png   horizontal bar of the dominant colors (drop into the brief)
  - <stem>_palette.json hex colors + temperature/saturation/contrast read

Use the swatch as a visual target and the JSON read to choose grade words
("cool teal shadows, warm skin", "desaturated, crushed blacks") for prompts.

Requires opencv-python + numpy. For a video, pass --time to grab a frame.

Usage:
  python extract_palette.py frame.jpg
  python extract_palette.py clip.mp4 --time 3.0 --colors 6 --out grade
"""
import argparse
import json
import sys
from pathlib import Path


def load_image(path, time):
    import cv2
    p = Path(path)
    if p.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}:
        cap = cv2.VideoCapture(str(p))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(time * fps))
        ok, frame = cap.read()
        cap.release()
        if not ok:
            print("ERROR: could not read frame at that time.", file=sys.stderr)
            sys.exit(1)
        return frame
    img = cv2.imread(str(p))
    if img is None:
        print(f"ERROR: could not read image: {p}", file=sys.stderr)
        sys.exit(1)
    return img


def analyze(frame, k):
    import numpy as np
    import cv2

    small = cv2.resize(frame, (160, 90))
    data = small.reshape(-1, 3).astype("float32")
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    counts = [int((labels == i).sum()) for i in range(k)]
    order = sorted(range(k), key=lambda i: counts[i], reverse=True)
    centers = centers[order]
    weights = [counts[i] / len(labels) for i in order]
    hexes = ["#{:02x}{:02x}{:02x}".format(int(c[2]), int(c[1]), int(c[0])) for c in centers]

    b, g, r = small[:, :, 0].mean(), small[:, :, 1].mean(), small[:, :, 2].mean()
    temp = "warm" if r > b + 8 else "cool" if b > r + 8 else "neutral"
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    sat = float(hsv[:, :, 1].mean())
    sat_word = "saturated" if sat > 120 else "muted" if sat > 60 else "desaturated"
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    lo, hi = float(np.percentile(gray, 5)), float(np.percentile(gray, 95))
    blacks = "crushed blacks" if lo < 18 else "lifted/faded blacks" if lo > 45 else "neutral blacks"
    contrast = "high contrast" if (hi - lo) > 170 else "low contrast" if (hi - lo) < 90 else "medium contrast"

    return {
        "colors": hexes, "weights": [round(w, 3) for w in weights], "centers_bgr": centers,
        "temperature": temp, "saturation_mean": round(sat, 1), "saturation_word": sat_word,
        "black_level": blacks, "contrast": contrast,
        "grade_phrase": f"{temp} tone, {sat_word}, {blacks}, {contrast}",
    }


def write_swatch(centers_bgr, weights, out_png):
    import numpy as np
    import cv2
    width, height = 900, 160
    bar = np.zeros((height, width, 3), dtype="uint8")
    x = 0
    for c, w in zip(centers_bgr, weights):
        seg = max(1, int(width * w))
        bar[:, x:x + seg] = [int(c[0]), int(c[1]), int(c[2])]
        x += seg
    bar[:, x:] = [int(centers_bgr[0][0]), int(centers_bgr[0][1]), int(centers_bgr[0][2])]
    cv2.imwrite(str(out_png), bar)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--time", type=float, default=1.0, help="seconds (video input only)")
    ap.add_argument("--colors", type=int, default=6)
    ap.add_argument("--out", help="output stem (default: input stem)")
    args = ap.parse_args()

    try:
        import cv2  # noqa: F401
        import numpy  # noqa: F401
    except ImportError:
        print("ERROR: needs opencv-python + numpy (pip install opencv-python numpy).", file=sys.stderr)
        sys.exit(1)

    frame = load_image(args.image, args.time)
    res = analyze(frame, args.colors)
    stem = Path(args.out) if args.out else Path(args.image).with_suffix("")
    swatch = Path(f"{stem}_swatch.png")
    write_swatch(res.pop("centers_bgr"), res["weights"], swatch)
    Path(f"{stem}_palette.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    print(f"Swatch: {swatch}")
    print(f"Palette: {res['colors']}")
    print(f"Grade read: {res['grade_phrase']}")


if __name__ == "__main__":
    main()
