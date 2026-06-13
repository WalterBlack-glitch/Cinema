#!/usr/bin/env python3
"""Generate video LOCALLY (free) via ComfyUI + LTX-Video.

LTX-Video 0.9.5 (Lightricks) es el modelo de video difusión más liviano y rápido
que rinde decente en una RTX 4050 6GB: ~24fps, hasta 257 frames, calidad cinemática
razonable. ComfyUI 0.3.10+ trae soporte nativo (no necesita custom nodes).

Auto-descarga el modelo (~9.3GB) la primera vez a:
    {ComfyUI}/models/checkpoints/ltx-video-2b-v0.9.5.safetensors
y el text encoder t5xxl_fp16 (~9GB) a {ComfyUI}/models/text_encoders/.

Uso:
  python generate_video_local.py --prompt "cinematic shot of..." --seconds 4 --out out.mp4
  python generate_video_local.py --prompt "..." --image start.png --seconds 5
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

COMFY = "http://127.0.0.1:8188"
PORTABLE = Path.home() / "CineStudioLocal" / "ComfyUI_windows_portable"
MODELS = PORTABLE / "ComfyUI" / "models"
INPUT_DIR = PORTABLE / "ComfyUI" / "input"

LTX_CKPT = "ltx-video-2b-v0.9.5.safetensors"
LTX_URL = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltx-video-2b-v0.9.5.safetensors"
T5_NAME = "t5xxl_fp16.safetensors"
T5_URL = "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors"


def dl(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        return
    tmp = dest.with_suffix(dest.suffix + ".part")
    print(f"Descargando {dest.name} (esto demora, varios GB)…", flush=True)
    urllib.request.urlretrieve(url, tmp)
    tmp.rename(dest)
    print(f"OK: {dest}", flush=True)


def ensure_models():
    dl(LTX_URL, MODELS / "checkpoints" / LTX_CKPT)
    dl(T5_URL, MODELS / "text_encoders" / T5_NAME)


def comfy_up():
    try:
        urllib.request.urlopen(COMFY + "/system_stats", timeout=2)
        return True
    except Exception:
        return False


def post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(COMFY + path, data=data,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def workflow(prompt, neg, w, h, length, fps, seed, steps, cfg, image_name=None):
    """LTX-Video workflow (ComfyUI nativo). image_name -> img2video si se provee."""
    g = {
        "ckpt":   {"class_type": "CheckpointLoaderSimple",
                   "inputs": {"ckpt_name": LTX_CKPT}},
        "t5":     {"class_type": "CLIPLoader",
                   "inputs": {"clip_name": T5_NAME, "type": "ltxv"}},
        "pos":    {"class_type": "CLIPTextEncode",
                   "inputs": {"text": prompt, "clip": ["t5", 0]}},
        "neg":    {"class_type": "CLIPTextEncode",
                   "inputs": {"text": neg, "clip": ["t5", 0]}},
    }
    if image_name:
        g["img"] = {"class_type": "LoadImage", "inputs": {"image": image_name}}
        g["lat"] = {"class_type": "LTXVImgToVideo",
                    "inputs": {"positive": ["pos", 0], "negative": ["neg", 0],
                               "vae": ["ckpt", 2], "image": ["img", 0],
                               "width": w, "height": h, "length": length,
                               "batch_size": 1}}
        pos_in, neg_in, lat_in = ["lat", 0], ["lat", 1], ["lat", 2]
    else:
        g["lat"] = {"class_type": "EmptyLTXVLatentVideo",
                    "inputs": {"width": w, "height": h, "length": length,
                               "batch_size": 1}}
        pos_in, neg_in, lat_in = ["pos", 0], ["neg", 0], ["lat", 0]
    g["cond"] = {"class_type": "LTXVConditioning",
                 "inputs": {"positive": pos_in, "negative": neg_in,
                            "frame_rate": fps}}
    g["sched"] = {"class_type": "LTXVScheduler",
                  "inputs": {"steps": steps, "max_shift": 2.05, "base_shift": 0.95,
                             "stretch": True, "terminal": 0.1, "latent": lat_in}}
    g["sample"] = {"class_type": "SamplerCustom",
                   "inputs": {"model": ["ckpt", 0], "add_noise": True, "noise_seed": seed,
                              "cfg": cfg, "positive": ["cond", 0], "negative": ["cond", 1],
                              "sampler": ["ksamp", 0], "sigmas": ["sched", 0],
                              "latent_image": lat_in}}
    g["ksamp"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}}
    g["dec"] = {"class_type": "VAEDecode",
                "inputs": {"samples": ["sample", 0], "vae": ["ckpt", 2]}}
    g["save"] = {"class_type": "SaveAnimatedWEBP",
                 "inputs": {"filename_prefix": "ltxv", "fps": fps, "lossless": False,
                            "quality": 90, "method": "default", "images": ["dec", 0]}}
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default="low quality, worst quality, deformed, distorted, blurry")
    ap.add_argument("--image", help="frame inicial (img2video)")
    ap.add_argument("--out", default="video_local.webp")
    ap.add_argument("--seconds", type=float, default=4.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--width", type=int, default=768)
    ap.add_argument("--height", type=int, default=512)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cfg", type=float, default=3.0)
    ap.add_argument("--seed", type=int, default=int(time.time()) & 0xFFFFFFFF)
    a = ap.parse_args()

    if not comfy_up():
        print("ERROR: ComfyUI no está corriendo. Arráncalo desde Cine Studio.",
              file=sys.stderr)
        sys.exit(2)

    print("Verificando modelos LTX-Video…", flush=True)
    ensure_models()

    # LTX-Video: length debe ser 8n+1, dims múltiplos de 32
    length = max(9, int(a.seconds * a.fps))
    length = ((length - 1) // 8) * 8 + 1
    w = (a.width // 32) * 32
    h = (a.height // 32) * 32

    image_name = None
    if a.image:
        src = Path(a.image)
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        dst = INPUT_DIR / src.name
        if src.resolve() != dst.resolve():
            import shutil
            shutil.copy2(src, dst)
        image_name = src.name

    wf = workflow(a.prompt, a.negative, w, h, length, a.fps, a.seed, a.steps, a.cfg, image_name)
    cid = uuid.uuid4().hex
    res = post("/prompt", {"prompt": wf, "client_id": cid})
    pid = res.get("prompt_id")
    if not pid:
        print(f"ERROR ComfyUI: {res}", file=sys.stderr); sys.exit(1)
    print(f"Cola enviada ({pid}). Generando {length} frames @ {w}x{h}… (1-5 min)", flush=True)

    deadline = time.time() + 1200
    out_file = None
    while time.time() < deadline:
        time.sleep(2)
        try:
            hist = json.load(urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=15))
        except Exception:
            continue
        if pid not in hist:
            continue
        for node in hist[pid].get("outputs", {}).values():
            for f in node.get("images", []) + node.get("gifs", []):
                out_file = f
        break
    if not out_file:
        print("ERROR: timeout esperando salida.", file=sys.stderr); sys.exit(1)

    q = urllib.parse.urlencode({"filename": out_file["filename"],
                                "subfolder": out_file.get("subfolder", ""),
                                "type": out_file.get("type", "output")})
    raw = Path(a.out).with_suffix(".webp")
    urllib.request.urlretrieve(f"{COMFY}/view?{q}", raw)
    print(f"WebP animado: {raw}", flush=True)

    # Re-encode a mp4 H.264 para que reproduzca en WebView2
    try:
        import imageio_ffmpeg, subprocess
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        mp4 = Path(a.out).with_suffix(".mp4")
        NO_WIN = 0x08000000 if sys.platform == "win32" else 0
        cmd = [ffmpeg, "-y", "-i", str(raw), "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart", str(mp4)]
        subprocess.run(cmd, capture_output=True, creationflags=NO_WIN)
        if mp4.exists() and mp4.stat().st_size > 1000:
            raw.unlink(missing_ok=True)
            print(f"MP4 H.264: {mp4}", flush=True)
    except Exception as e:
        print(f"(no se pudo re-encodear a mp4: {e}; quedó el .webp)", file=sys.stderr)


if __name__ == "__main__":
    main()
