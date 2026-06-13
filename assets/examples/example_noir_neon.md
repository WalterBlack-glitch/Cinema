# Worked example — Neon noir (reference: night city clip)

Few-shot example of a finished brief. Mirror this density when filling
`assets/shot_brief_template.md`. Camera move goes in the prompt; no preset flag.

## 1. Look Recipe
Derived from: local file `ref_neon.mp4` (analyzed) + style "Wong Kar-wai neon".

| Axis | Finding | Vocabulary |
|---|---|---|
| Scale & framing | medium/medium-close, subject off-center left, lead room into neon | medium close-up, rule of thirds |
| Composition | strong FG occlusion (rain, signage bokeh), 3 depth layers | foreground bokeh, framing in frame |
| Lens & depth | long lens feel, very shallow DoF, oval bokeh | 85mm anamorphic, shallow depth of field, oval bokeh |
| Light | neon practicals, soft magenta rim, backlit haze | neon practical lighting, soft rim, blue hour |
| Color & grade | magenta + cyan, crushed blacks, medium-high contrast | cyan-magenta palette, crushed blacks |
| Camera move | slow lateral tracking, occasional handheld | tracking, subtle handheld |
| Edit rhythm (ASL) | ~4 s, contemplative | long-ish takes |

**Style summary:** rain-slick magenta-cyan noir, 85mm anamorphic shallow, slow tracking, crushed blacks.

## 2 & 3. Shots + commands

### Shot 1 — establishing alley (text-to-video, seedance_2_0)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Rain-slick neon alley at night, steam rising in the foreground, blurred magenta and cyan signage receding into the background, 85mm anamorphic shallow depth of field with oval bokeh, soft backlit haze at blue hour, cyan-and-magenta palette with crushed blacks, film grain, melancholic — slow dolly push-in" \
  --duration 5 --aspect_ratio 21:9 --wait
```

### Shot 2 — the figure (image-to-video; start frame from a Soul/GPT still in the same grade)
```bash
# start frame
higgsfield generate create soul_cinematic --prompt "Lone figure in a wet wool coat seen from behind, neon-lit rain, reflective puddles, 85mm anamorphic shallow DoF, soft magenta rim light, cyan-magenta palette, crushed blacks" --quality 2k --aspect_ratio 21:9 --wait
# animate
higgsfield generate create seedance_2_0 \
  --prompt "The figure walks slowly away from camera through neon rain, soft magenta rim light, cyan-magenta crushed blacks, film grain, lonely — tracking shot following the subject with parallax" \
  --start-image ./shot2_frame.png --duration 6 --aspect_ratio 21:9 --wait
```

### Shot 3 — close on eyes (image-to-video, subtle)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Extreme close-up of weary eyes catching neon reflections, faint magenta and cyan glints, 100mm razor-thin depth of field, soft rim, crushed blacks, fine grain, intimate — static locked-off shot" \
  --start-image ./shot3_eyes.png --duration 3 --aspect_ratio 21:9 --wait
```

## 5. Assembly
Target ASL ~4 s, hard cuts on a slow synth pulse:
`python scripts/assemble.py shot1.mp4 shot2.mp4 shot3.mp4 -o noir.mp4 --crossfade 0.3 --music synth.mp3 --size 2048x858 --fps 24`
