#!/usr/bin/env python3
"""Build a storyboard contact sheet from keyframes or generated clips.

Tiles images (or one frame per clip) into a labeled grid PNG so a whole sequence
can be eyeballed at once. Pairs with analyze_video.py output (keyframes/) and with
generated Higgsfield clips for a quick storyboard review.

Usage:
  python contact_sheet.py analysis/keyframes -o storyboard.png --cols 4
  python contact_sheet.py clips --from-video -o storyboard.png --label
  python contact_sheet.py analysis/keyframes --against gen_clips --from-video -o compare.png

--against pairs the two sources row by row (reference left, generated right) for
Phase-6 iteration; --from-video then applies to the --against side only when its
entries are clips.

Requires opencv-python + numpy.
"""
import argparse
import re
import sys
from pathlib import Path


def natural_key(p):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(p))]


VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
IMAGE_EXT = {".jpg", ".jpeg", ".png"}


def gather(src, from_video=None):
    """from_video True=clips only, False=images only, None=both (auto)."""
    p = Path(src)
    if from_video is True:
        exts = VIDEO_EXT
    elif from_video is False:
        exts = IMAGE_EXT
    else:
        exts = VIDEO_EXT | IMAGE_EXT
    return sorted([f for f in p.iterdir() if f.suffix.lower() in exts], key=natural_key)


def load_tile(path, cell_w, cell_h, label):
    import cv2
    if path.suffix.lower() in VIDEO_EXT:
        cap = cv2.VideoCapture(str(path))
        n = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n // 2))
        ok, img = cap.read()
        cap.release()
        if not ok:
            return None
    else:
        img = cv2.imread(str(path))
        if img is None:
            return None
    import numpy as np
    h, w = img.shape[:2]
    scale = min(cell_w / w, cell_h / h)
    img = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))))
    canvas = np.zeros((cell_h, cell_w, 3), dtype="uint8")
    y = (cell_h - img.shape[0]) // 2
    x = (cell_w - img.shape[1]) // 2
    canvas[y:y + img.shape[0], x:x + img.shape[1]] = img
    if label:
        cv2.putText(canvas, path.stem, (8, cell_h - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return canvas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="folder of images, or clips with --from-video")
    ap.add_argument("-o", "--out", default="contact_sheet.png")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", default="480x270", help="cell WxH")
    ap.add_argument("--from-video", action="store_true", help="grab mid-frame from each clip")
    ap.add_argument("--label", action="store_true", help="overlay filename on each tile")
    ap.add_argument("--against", help="second folder; pairs rows as reference|generated")
    args = ap.parse_args()

    try:
        import cv2  # noqa: F401
        import numpy as np
    except ImportError:
        print("ERROR: needs opencv-python + numpy.", file=sys.stderr)
        sys.exit(1)

    cw, ch = (int(x) for x in args.cell.lower().split("x"))

    if args.against:
        ref = gather(args.src)
        gen = gather(args.against)
        if not ref or not gen:
            print(f"ERROR: no inputs in {args.src} or {args.against}", file=sys.stderr)
            sys.exit(1)
        n = max(len(ref), len(gen))
        blank = np.zeros((ch, cw, 3), dtype="uint8")
        tiles = []
        for i in range(n):
            for side in (ref, gen):
                t = load_tile(side[i], cw, ch, args.label) if i < len(side) else None
                tiles.append(t if t is not None else blank.copy())
        cols, total = 2, 2 * n
    else:
        files = gather(args.src, args.from_video)
        if not files:
            print(f"ERROR: no inputs in {args.src}", file=sys.stderr)
            sys.exit(1)
        tiles = [t for t in (load_tile(f, cw, ch, args.label) for f in files) if t is not None]
        cols, total = max(1, args.cols), len(tiles)

    rows = (total + cols - 1) // cols
    sheet = np.zeros((rows * ch, cols * cw, 3), dtype="uint8")
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw] = t
    cv2.imwrite(args.out, sheet)
    print(f"Wrote {args.out} ({total} tiles, {cols}x{rows}). VIEW it to review"
          f"{' the ref|gen pairs' if args.against else ' the sequence'}.")


if __name__ == "__main__":
    main()
