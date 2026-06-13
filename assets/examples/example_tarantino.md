# Worked example — Tarantino diner standoff (style: "como Tarantino")

Few-shot for a director-style brief. Decoded via `references/directors.md` (Tarantino) +
`references/shot_types.md` (planos/ángulos). Picks 4 signatures only — trunk shot, God's-eye insert,
long dialogue push-in, snap zoom — not the whole bag. Camera move lives in the prompt; no preset flag.

## 1. Look Recipe
Derived from: named style "Tarantino" (no footage) + `directors.md` signatures.

| Axis | Finding | Vocabulary |
|---|---|---|
| Scale & framing | mix of low trunk-shot PA, overhead insert, dialogue MCU | american shot, overhead insert, medium close-up |
| Composition | flat profile two-shots, criss-crossed eyelines, centered inserts | profile two-shot, symmetrical overhead |
| Lens & depth | 35mm anamorphic, moderate DoF, lived-in deep backgrounds | 35mm anamorphic, 2.39:1 |
| Light | harsh practical diner light, hard noon through windows | hard practical light, warm tungsten |
| Color & grade | saturated retro 70s Americana, deep blacks, filmic grain | saturated 70s palette, deep blacks, 35mm grain |
| Camera move | slow dialogue push-in detonating into snap zoom | slow dolly push-in / fast snap zoom |
| Edit rhythm (ASL) | long patient dialogue (~8 s) → fast cut on violence (<1 s) | long takes then rapid cuts |

**Style summary:** retro Americana diner tension, 35mm anamorphic 2.39:1, trunk shot + God's-eye, slow push-in that snaps to a zoom, deep blacks.

## 2 & 3. Shots + commands

### Shot 1 — trunk-shot reveal (text-to-video, seedance_2_0)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Low-angle trunk-shot POV looking up at two men in 70s suits and skinny ties standing over an open car trunk, harsh noon desert light, saturated warm Americana palette, 35mm anamorphic 2.39:1, deep blacks, film grain, menacing and cool — slow dolly push-in from inside the trunk" \
  --duration 6 --aspect_ratio 21:9 --wait
```

### Shot 2 — diner dialogue (image-to-video; start frame in same grade)
```bash
# start frame
higgsfield generate create soul_cinematic --prompt "Profile two-shot of two men talking across a booth in a retro 70s diner, warm tungsten practicals, saturated Americana palette, 35mm anamorphic, deep blacks, film grain" --quality 2k --aspect_ratio 21:9 --wait
# animate — the long patient take
higgsfield generate create seedance_2_0 \
  --prompt "Two men in a diner booth mid-conversation, profile two-shot, subtle gestures, warm tungsten practical light, saturated retro palette, 35mm anamorphic 2.39:1, deep blacks, grain, tense calm before violence — very slow dolly push-in toward the speaker" \
  --start-image ./shot2_diner.png --duration 10 --aspect_ratio 21:9 --wait
```

### Shot 3 — God's-eye insert (image-to-video, the object beat)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "Overhead God's-eye top-down insert of a revolver and a stack of cash on a chrome diner table, hard overhead light, saturated 70s tones, deep blacks, fine 35mm grain, ominous — static locked-off shot" \
  --start-image ./shot3_table.png --duration 3 --aspect_ratio 21:9 --wait
```

### Shot 4 — the snap (text-to-video, the detonation)
```bash
higgsfield generate create seedance_2_0 \
  --prompt "A man's face hardening as he draws, retro diner background, harsh practical light, saturated Americana palette, 35mm anamorphic 2.39:1, deep blacks, grain, sudden danger — fast snap zoom in on his eyes" \
  --duration 2 --aspect_ratio 21:9 --wait
```

## 5. Assembly
The Tarantino rhythm IS the contrast: hold shots 1–3 long, then hard-cut fast into shot 4. No crossfade.
`python scripts/assemble.py shot1.mp4 shot2.mp4 shot3.mp4 shot4.mp4 -o tarantino.mp4 --music surf_rock.mp3 --size 2048x858 --fps 24`
