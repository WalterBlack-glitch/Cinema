#!/usr/bin/env python3
"""Download Higgsfield result URLs to a local folder.

The `higgsfield ... --wait` CLI prints result URL(s) but does not save the file.
This pulls those URLs into a destination folder (default: ~/Videos/Higgsfield),
naming each file by timestamp + a slug so videos/images land tidily in one place.

Usage:
  python save_result.py "https://.../clip.mp4"                 # one or more URLs
  python save_result.py --from-log angels_shot.log             # extract URLs from a log
  python save_result.py --from-log run --dir "D:/renders"      # custom folder
"""
import argparse
import datetime
import os
import re
import sys
import urllib.request
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s\"'<>]+")
DEFAULT_DIR = Path.home() / "Videos" / "Higgsfield"


def ext_from(url):
    m = re.search(r"\.(mp4|mov|webm|mkv|png|jpg|jpeg|webp)(?:\?|$)", url, re.I)
    return "." + m.group(1).lower() if m else ".bin"


def download(url, dest_dir, slug=""):
    dest_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{ts}{('_' + slug) if slug else ''}{ext_from(url)}"
    out = dest_dir / name
    urllib.request.urlretrieve(url, out)
    print(f"saved {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*", help="result URLs")
    ap.add_argument("--from-log", help="file to scan for result URLs")
    ap.add_argument("--dir", default=str(DEFAULT_DIR), help="destination folder")
    ap.add_argument("--slug", default="", help="optional name tag")
    a = ap.parse_args()

    urls = list(a.urls)
    if a.from_log:
        text = Path(a.from_log).read_text(encoding="utf-8", errors="ignore")
        urls += URL_RE.findall(text)
    # keep only media URLs, de-dupe, preserve order
    seen, media = set(), []
    for u in urls:
        if ext_from(u) != ".bin" and u not in seen:
            seen.add(u); media.append(u)
    if not media:
        print("No media URLs found.", file=sys.stderr)
        sys.exit(1)
    dest = Path(os.path.expanduser(a.dir))
    for u in media:
        try:
            download(u, dest, a.slug)
        except Exception as e:
            print(f"FAILED {u}: {e}", file=sys.stderr)
    print(f"Done -> {dest}")


if __name__ == "__main__":
    main()
