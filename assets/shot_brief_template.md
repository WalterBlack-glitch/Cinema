# Shot Brief — <project name>

> Fill this from the reference analysis, then map each shot to Higgsfield. One file per project.

## 1. Look Recipe (the learned style)

Derived from: <local file / YouTube URL / named style>

| Craft axis | Finding | Prompt vocabulary to reuse |
|---|---|---|
| Shot scale & framing | | |
| Composition | | |
| Lens & depth | | |
| Lighting & exposure | | |
| Color & grade | | |
| Camera movement | | |
| Edit rhythm (ASL) | | |

**One-line style summary:** <e.g. "neon blue-hour noir, 85mm shallow, slow tracking, crushed blacks">

## 2. Shot list

| # | Subject / action | Scale | Lens / DoF | Light | Color | Camera move | Duration |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |

## 3. Higgsfield mapping (the deliverable)

For each shot: model + mode + the ready `higgsfield generate create` command (camera move stated in
the prompt, no preset flag). See `references/higgsfield.md` and `references/camera_motion.md`.

### Shot 1
- **Model:** seedance_2_0 | kling3_0 | cinema_studio_video_3_0 | (still: gpt_image_2 / soul_cinematic)
- **Mode:** text-to-video | image-to-video (--start-image) | transition (--start-image + --end-image)
- **Start frame:** <path/desc, if image-to-video>
- **Prompt (frame prose + ONE camera move):**
  > <subject+detail, action, setting w/ FG+BG depth, lens+focal+DoF, light dir+quality+time, color palette+grade+contrast, film stock/grain, mood> — <camera move, e.g. "slow dolly push-in">
- **Command:**
  ```bash
  higgsfield generate create seedance_2_0 --prompt "..." [--start-image ./f.png] --duration <s> --aspect_ratio <16:9|9:16|21:9> --wait
  ```

### Shot 2
- **Model:**
- **Mode:**
- **Prompt:**
  > 
- **Command:**
  ```bash
  ```

## 4. Generation log

| # | Model/duration | Output URL/file | Verdict vs. recipe | Fix for next pass |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

## 5. Assembly notes
- Target sequence ASL: <s> → order + trim durations accordingly.
- Cut style: <hard / match / on-beat>. Audio/music: <ref>.
