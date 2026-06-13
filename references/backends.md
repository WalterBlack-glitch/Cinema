# Generation backends — one brief, many engines

The Look Recipe and per-shot prompts are **engine-agnostic**. Phase 5 routes them to whatever
generator fits the budget and the shot. Use `scripts/generate.py --engine <name>` as the single
entry point; it normalizes the prompt + aspect + image flags across engines.

## Engines

| Engine | Where | Cost | Does | When to use |
|---|---|---|---|---|
| `higgsfield` | cloud CLI | credits ($) | **video** (Seedance/Kling…) + stills | the final motion shots; anything that needs real camera movement |
| `comfyui` | local GPU | **free, unlimited** | **stills** (SDXL txt2img / img2img) | start-frames, look tests, palette/composition iteration — burn zero credits here |

Planned/easy to add (same adapter shape): a cloud API (Replicate / fal.ai) for cheaper per-shot
video, or a local video model (AnimateDiff / LTX) on bigger VRAM. Not wired yet — add an
`run_<engine>()` function in `generate.py` mirroring the two existing ones.

## The cost-smart workflow (default)
1. **Iterate stills locally for free** on ComfyUI until the frame matches the Look Recipe
   (composition, lens feel, light, grade). Zero credits.
2. **Promote the keeper frame to motion** on Higgsfield with `--start-image` (image-to-video).
   Credits are spent only on shots you already approved as stills.
3. Assemble with `scripts/assemble.py`.

This is why the skill isn't Higgsfield-only: the expensive step (video) runs cloud, the cheap,
high-iteration step (finding the look) runs on your own 4050.

## Engine quick reference

### Local stills — ComfyUI (free)
Prereqs: ComfyUI running (default `http://127.0.0.1:8188`) + one SDXL checkpoint in
`ComfyUI/models/checkpoints/` (e.g. `sd_xl_base_1.0.safetensors`; a 6 GB-VRAM card like the 4050
handles SDXL with ComfyUI's auto low-VRAM offload).
```bash
# text-to-image
python scripts/generate.py --engine comfyui --prompt "<frame prose from the brief>" \
  --aspect 16:9 --out shot1_frame.png
# image-to-image refine (place source in ComfyUI/input/ first)
python scripts/generate.py --engine comfyui --prompt "<tweaked prose>" \
  --image shot1_frame.png --denoise 0.5 --out shot1_v2.png
```
Tuning: `--steps` (quality vs speed), `--cfg` (prompt adherence), `--ckpt` (swap in a photoreal or
cinematic SDXL model), `--seed` (reproduce a result). No camera move here — stills only.

### Cloud video/stills — Higgsfield (credits)
```bash
# video (camera move lives in the prompt — see camera_motion.md)
python scripts/generate.py --engine higgsfield --hf-model seedance_2_0 \
  --prompt "<frame prose> — slow dolly push-in" --duration 4 --aspect 16:9
# animate a locally-made start frame
python scripts/generate.py --engine higgsfield --hf-model seedance_2_0 \
  --prompt "<motion prose>" --image shot1_frame.png --duration 4 --aspect 16:9
```
Check cost first with `higgsfield generate cost <model> --prompt t --duration N --aspect_ratio 16:9`.

## Aspect ratios across engines
Higgsfield allows `auto,16:9,9:16,4:3,3:4,1:1,21:9` — **there is no 2.39:1**; use **21:9** for scope.
`generate.py` maps the same labels to SDXL-friendly pixel buckets for ComfyUI, so one `--aspect`
value works for both engines.
