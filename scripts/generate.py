#!/usr/bin/env python3
"""Engine-agnostic generator: one prompt, pick the backend.

The cinematography brief (prompt + params) is portable; this routes it to whatever
generator is available so you are not locked to Higgsfield.

Engines:
  higgsfield  -> the `higgsfield` CLI (cloud, costs credits). Video or stills.
  comfyui     -> a local ComfyUI server (free, unlimited) over its HTTP API.
                 SDXL txt2img, or img2img when --image is given. Stills only.

Examples:
  # free local still on your own GPU
  python generate.py --engine comfyui --prompt "rain-slick neon alley, 85mm, cyan-magenta" --out shot.png
  # same prompt, cloud video
  python generate.py --engine higgsfield --hf-model seedance_2_0 --prompt "...slow dolly push-in" \
      --duration 4 --aspect 16:9
  # local img2img refine of a start frame
  python generate.py --engine comfyui --prompt "..." --image start.png --denoise 0.55 --out v2.png

ComfyUI must be running (default http://127.0.0.1:8188). If it isn't, the script says so
and exits 2 — never silently fail. Higgsfield must be installed + authed (references/higgsfield.md).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ASPECT_WH = {  # SDXL-friendly buckets for the local engine
    "16:9": (1344, 768), "9:16": (768, 1344), "1:1": (1024, 1024),
    "4:3": (1152, 896), "3:4": (896, 1152), "21:9": (1536, 640),
}


URL_RE = re.compile(r"https?://[^\s\"'<>]+\.(?:mp4|mov|webm|mkv|png|jpg|jpeg|webp)(?:\?[^\s\"'<>]*)?")
DEFAULT_SAVE = Path.home() / "Videos" / "Higgsfield"


def save_urls(text, dest):
    import datetime
    dest = Path(os.path.expanduser(dest))
    dest.mkdir(parents=True, exist_ok=True)
    saved = []
    for u in dict.fromkeys(URL_RE.findall(text)):
        ext = re.search(r"\.(\w+)(?:\?|$)", u).group(1).lower()
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out = dest / f"{ts}.{ext}"
        try:
            urllib.request.urlretrieve(u, out)
            print(f"saved {out}")
            saved.append(out)
        except Exception as e:
            print(f"FAILED to save {u}: {e}", file=sys.stderr)
    if not saved:
        print(f"(no media URL found to save to {dest})", file=sys.stderr)
    return saved


# ----------------------------- Higgsfield (cloud) -----------------------------
def run_higgsfield(a):
    model = a.hf_model or ("seedance_2_0" if a.duration else "gpt_image_2")
    cmd = ["higgsfield", "generate", "create", model, "--prompt", a.prompt,
           "--aspect_ratio", a.aspect, "--wait"]
    if a.image:
        cmd += ["--start-image", a.image]
    if a.duration:
        cmd += ["--duration", str(a.duration)]
    print(f"$ {' '.join(cmd)}")
    if a.dry_run:
        return 0
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    print(out)
    if r.returncode == 0 and not a.no_save:
        save_urls(out, a.save_dir)
    return r.returncode


# ----------------------------- ComfyUI (local) --------------------------------
def comfy_workflow(a, w, h):
    """Minimal SDXL graph: txt2img, or img2img if --image. Returns API-format dict."""
    pos = {"3": {"class_type": "CheckpointLoaderSimple",
                 "inputs": {"ckpt_name": a.ckpt}},
           "4": {"class_type": "CLIPTextEncode",
                 "inputs": {"text": a.prompt, "clip": ["3", 1]}},
           "5": {"class_type": "CLIPTextEncode",
                 "inputs": {"text": a.negative, "clip": ["3", 1]}}}
    if a.image:
        pos["6"] = {"class_type": "LoadImage", "inputs": {"image": Path(a.image).name}}
        pos["7"] = {"class_type": "VAEEncode",
                    "inputs": {"pixels": ["6", 0], "vae": ["3", 2]}}
        latent, denoise = ["7", 0], a.denoise
    else:
        pos["6"] = {"class_type": "EmptyLatentImage",
                    "inputs": {"width": w, "height": h, "batch_size": 1}}
        latent, denoise = ["6", 0], 1.0
    pos["10"] = {"class_type": "KSampler",
                 "inputs": {"seed": a.seed, "steps": a.steps, "cfg": a.cfg,
                            "sampler_name": "dpmpp_2m", "scheduler": "karras",
                            "denoise": denoise, "model": ["3", 0],
                            "positive": ["4", 0], "negative": ["5", 0],
                            "latent_image": latent}}
    pos["11"] = {"class_type": "VAEDecode",
                 "inputs": {"samples": ["10", 0], "vae": ["3", 2]}}
    pos["12"] = {"class_type": "SaveImage",
                 "inputs": {"filename_prefix": "cine", "images": ["11", 0]}}
    return pos


def comfy_post(url, path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url + path, data=data,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def run_comfyui(a):
    url = a.comfy_url.rstrip("/")
    w, h = ASPECT_WH.get(a.aspect, (1024, 1024))
    if a.dry_run:
        print(json.dumps(comfy_workflow(a, w, h), indent=2))
        return 0
    try:
        urllib.request.urlopen(url + "/system_stats", timeout=5)
    except Exception:
        print(f"ERROR: ComfyUI not reachable at {url}. Start it (run_nvidia_gpu.bat / "
              "`python main.py`) then retry. Install: github.com/comfyanonymous/ComfyUI",
              file=sys.stderr)
        sys.exit(2)
    if a.image:  # ComfyUI loads inputs by filename from its input/ dir
        print(f"NOTE: copy '{a.image}' into ComfyUI's input/ folder if img2img can't find it.")

    cid = uuid.uuid4().hex
    res = comfy_post(url, "/prompt", {"prompt": comfy_workflow(a, w, h), "client_id": cid})
    pid = res.get("prompt_id")
    if not pid:
        print(f"ERROR: ComfyUI rejected the job: {res}", file=sys.stderr)
        return 1
    print(f"queued {pid}; waiting...")
    img = None
    for _ in range(a.timeout):
        time.sleep(1)
        hist = json.load(urllib.request.urlopen(f"{url}/history/{pid}", timeout=15))
        if pid in hist:
            for node in hist[pid].get("outputs", {}).values():
                for im in node.get("images", []):
                    img = im
            break
    if not img:
        print("ERROR: timed out waiting for ComfyUI output.", file=sys.stderr)
        return 1
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""),
                                "type": img.get("type", "output")})
    out = a.out or "comfy_out.png"
    urllib.request.urlretrieve(f"{url}/view?{q}", out)
    print(f"Done. Saved {out}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True, choices=["higgsfield", "comfyui"])
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default="blurry, low quality, deformed, watermark, text")
    ap.add_argument("--image", help="start/source image (img2video cloud, img2img local)")
    ap.add_argument("--aspect", default="16:9", help="16:9 9:16 1:1 4:3 3:4 21:9")
    ap.add_argument("--out", help="output file (comfyui)")
    ap.add_argument("--dry-run", action="store_true")
    # higgsfield
    ap.add_argument("--hf-model", help="default gpt_image_2 (still) / seedance_2_0 (if --duration)")
    ap.add_argument("--duration", type=int, help="seconds -> video (higgsfield)")
    ap.add_argument("--save-dir", default=str(DEFAULT_SAVE),
                    help="folder to download results into (default ~/Videos/Higgsfield)")
    ap.add_argument("--no-save", action="store_true", help="don't auto-download the result")
    # comfyui
    ap.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    ap.add_argument("--ckpt", default="sd_xl_base_1.0.safetensors", help="SDXL checkpoint filename")
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--cfg", type=float, default=6.5)
    ap.add_argument("--denoise", type=float, default=0.6, help="img2img strength")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=300)
    a = ap.parse_args()
    rc = run_higgsfield(a) if a.engine == "higgsfield" else run_comfyui(a)
    sys.exit(rc)


if __name__ == "__main__":
    main()
