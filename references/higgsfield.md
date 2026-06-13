# Higgsfield CLI & models (for cinematography)

Higgsfield generation runs through the **`higgsfield` CLI** (wrapped by the `higgsfield-generate`
skill). There is no MCP and no named camera "motion presets" — the camera move is described in the
prompt. This file is the subset needed to turn a shot brief into generation commands. For the full
generation surface (Marketing Studio, Virality Predictor, all flags) defer to `higgsfield-generate`.

## Bootstrap & auth (once)
- Install if missing: `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh`
- Check session: `higgsfield account status`. If not authenticated, the user runs
  `higgsfield auth login` (interactive) — ask and wait.

## The one command

```bash
higgsfield generate create <model> --prompt "..." [media flags] [param flags] --wait
```
`--wait` blocks until the job finishes and prints the result URL. Add `--json` for machine output.
Discover a model's exact params with `higgsfield model get <model> --json`; list models with
`higgsfield model list --json`.

## Models for cinematic work

### Video
| Model | Use for |
|---|---|
| `seedance_2_0` | **Default.** Serious motion, multi-shot, image-to-video, 4–15 s (12 valid). SOTA — validate this before downgrading. |
| `kling3_0` | Single-plane scene without strong dynamics; cheaper than Seedance 2.0. |
| `cinema_studio_video_3_0` | Cinema-grade highest fidelity. |
| `seedance_1_5_pro` | Cheap clean shot without cuts (only when user wants budget). |
| `minimax_hailuo` | Cheap with strong physics, no audio needed. |
| `veo3_1` / Veo 3.1 Lite | Fast batch / volume. |

### Stills (for start frames / image-to-video)
| Model | Use for |
|---|---|
| `gpt_image_2` | Default high-fidelity image, design, typography, on-image text. |
| `soul_cinematic` | Cinematic still frame (use `--quality 1.5k`/`2k`). |
| `text2image_soul_v2` | Aesthetic UGC / editorial / lifestyle character; supports `--soul-id`. |
| `soul_location` | Locations / environments / no-people scenes (best in class). |
| `nano_banana_2` / Pro | Character / cartoon / stylized / reference-driven (Pro for hard cases). |

## Media flags (path or UUID; paths auto-upload)
| Flag | Purpose | Notable models |
|---|---|---|
| `--image <path-or-id>` | reference image | most image models, `seedance_2_0` |
| `--start-image <path-or-id>` | first frame for image-to-video | `seedance_2_0`, `kling3_0`, `veo3_1` |
| `--end-image <path-or-id>` | last frame (transition) | `seedance_2_0`, `kling3_0` |
| `--audio <path-or-id>` | reference/soundtrack audio | `seedance_2_0` (use this, not `--generate-audio`) |

## Common params
- `--aspect_ratio` — allowed enum: `auto, 16:9, 9:16, 4:3, 3:4, 1:1, 21:9`. **No `2.39:1`** — it
  errors; use `21:9` for anamorphic scope (and keep "anamorphic 2.39:1" in the prompt prose).
- `--duration` — seconds; Seedance min 4 (4–15). Cost scales with duration: check before running
  with `higgsfield generate cost <model> --prompt t --duration N --aspect_ratio 16:9`.
- `--resolution` — model-dependent (`720p`, `2k`, …); Soul stills use `--quality 1.5k|2k`.
- `--soul-id <id>` — character identity for Soul models (create with `higgsfield-soul-id`).
- `--wait` / `--wait-timeout 20m` / `--wait-interval 5s`.

## Patterns

Text-to-video establishing shot:
```bash
higgsfield generate create seedance_2_0 \
  --prompt "<frame prose> , <camera move in words>" \
  --duration 8 --aspect_ratio 16:9 --wait
```

Image-to-video from a designed start frame:
```bash
# 1) make the frame
higgsfield generate create gpt_image_2 --prompt "<frame prose>" --aspect_ratio 16:9 --resolution 2k --wait
# 2) animate it
higgsfield generate create seedance_2_0 --prompt "<camera move + action>" --start-image ./frame.png --duration 8 --aspect_ratio 16:9 --wait
```

Start→end transition:
```bash
higgsfield generate create seedance_2_0 --prompt "<transformation described>" \
  --start-image ./a.png --end-image ./b.png --duration 6 --aspect_ratio 16:9 --wait
```

Consistent character across shots: create a Soul id once with `higgsfield-soul-id`, then pass
`--soul-id <id>` to `text2image_soul_v2` / `soul_cinematic` for the start frames before animating.

## Reliability
- One dominant camera move per clip; describe it explicitly (see `camera_motion.md`).
- Faces/hands and on-screen text are the usual failure points — for portraits prefer image-to-video
  with a clean Soul start frame and keep the subject mid-frame.
- Reproducibility: keep the working start frame; iterate the motion prose and `--duration` around it.
- Validate the preferred model (`higgsfield model get <model> --json`) before falling back to older
  ones. The server returns `adjustments` for non-fatal coercions and structured errors otherwise.
