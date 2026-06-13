# Worked example — Epic nature documentary (reference: golden-hour landscape reel)

## 1. Look Recipe
Derived from: style "nature doc / epic" + YouTube ref (downloaded, analyzed).

| Axis | Finding | Vocabulary |
|---|---|---|
| Scale & framing | extreme wide, low horizon for grandeur | extreme wide shot, low horizon |
| Composition | leading lines (ridgelines, rivers), deep layers | leading lines, deep focus |
| Lens & depth | wide, deep focus, everything sharp | 24mm, deep depth of field, f/11 |
| Light | golden hour, volumetric god rays, long shadows | golden hour, god rays, backlit |
| Color & grade | rich saturated, warm, gentle contrast | saturated, warm amber, filmic |
| Camera move | slow crane reveals + slow orbit | crane up, slow orbit |
| Edit rhythm (ASL) | ~7 s, contemplative | long takes |

**Style summary:** golden-hour epic vistas, ultrawide deep focus, slow crane/orbit, rich warm grade.

## 2 & 3. Shots + commands

### Shot 1 — valley reveal (text-to-video, seedance_2_0)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Vast mountain valley at golden hour, a winding river leading the eye toward distant peaks, low horizon, layered ridgelines fading into atmospheric haze, 24mm deep depth of field everything sharp, warm backlight with volumetric god rays and long shadows, richly saturated warm amber palette, filmic gentle contrast, epic and serene — slow crane up rising above the valley" \
  --duration 8 --aspect_ratio 16:9 --wait
```

### Shot 2 — lone tree hero (text-to-video)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "A solitary windswept tree on a golden ridge, backlit by low sun, grass glowing, distant valley behind in soft haze, 35mm deep focus, god rays, warm saturated grade, filmic, majestic — camera slowly orbits around the tree" \
  --duration 7 --aspect_ratio 16:9 --wait
```

### Shot 3 — wildlife detail (image-to-video; start frame in same grade)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Close detail of an eagle scanning the horizon at golden hour, feathers rim-lit, soft warm bokeh background, 200mm shallow depth of field, saturated warm tones, fine grain, regal — static locked-off shot, only the head turns" \
  --start-image ./eagle_frame.png --duration 4 --aspect_ratio 16:9 --wait
```

## 5. Assembly
Target ASL ~7 s, slow crossfades over orchestral bed:
`python scripts/assemble.py --dir clips -o epic.mp4 --crossfade 0.6 --music score.mp3 --size 1920x1080 --fps 24`
