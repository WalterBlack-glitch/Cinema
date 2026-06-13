# Worked example — Hype / FPV social reel (vertical)

## 1. Look Recipe
Derived from: style "FPV / hype reel" for 9:16 social.

| Axis | Finding | Vocabulary |
|---|---|---|
| Scale & framing | ultrawide, dynamic diagonals, subject centered for vertical | ultrawide, centered, dynamic angle |
| Composition | strong FG whip-bys, motion blur | foreground motion blur |
| Lens & depth | ultrawide, mostly deep focus | 16mm, deep focus |
| Light | high-key sun, punchy | high-key, hard sun |
| Color & grade | punchy contrast, vivid | vivid, high contrast, teal-orange pop |
| Camera move | FPV flythrough + crash zoom + speed ramp | FPV drone, crash zoom, speed ramp |
| Edit rhythm (ASL) | <1.5 s, very fast | rapid cuts on the beat |

**Style summary:** kinetic high-key FPV reel, ultrawide, crash zooms + speed ramps, punchy vivid grade, vertical.

## 2 & 3. Shots + commands

### Shot 1 — flythrough intro (text-to-video, seedance_2_0)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Rushing between urban rooftops at midday, dynamic diagonal horizon, foreground edges blurred with speed, 16mm ultrawide deep focus, high-key hard sun, vivid punchy high-contrast teal-orange grade, energetic — FPV drone flythrough, kinetic and continuous" \
  --duration 4 --aspect_ratio 9:16 --wait
```

### Shot 2 — subject crash zoom (image-to-video; hero subject still)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Athlete mid-jump against bright sky, ultrawide low angle, motion-blur foreground, high-key sun, vivid high-contrast grade, explosive energy — fast crash zoom in" \
  --start-image ./athlete_frame.png --duration 3 --aspect_ratio 9:16 --wait
```

### Shot 3 — speed-ramp action (text-to-video)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Fast move past a runner on a sunlit street, strong parallax, foreground blur, 16mm, high-key, vivid punchy grade, kinetic — tracking shot with a speed ramp, accelerating then slowing" \
  --duration 4 --aspect_ratio 9:16 --wait
```

## 5. Assembly
Target ASL <1.5 s, HARD cuts on the beat (no crossfade). Generate longer clips, then trim tight:
`python scripts/assemble.py s1.mp4 s2.mp4 s3.mp4 -o reel.mp4 --music beat.mp3 --size 1080x1920 --fps 30`
