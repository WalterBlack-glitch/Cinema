# Cinematography & visual-quality reference

The vocabulary and rules to (a) read what makes a reference clip look good and (b) write prompts
that reproduce it. Organized as seven craft axes, then a style cheat sheet, then the prompt formula.

## The seven craft axes

When analyzing footage or designing a shot, score each axis explicitly. Vague prompts come from
skipping axes; "cinematic" is the sum of these, not a keyword.

### 1. Shot scale & framing
- Scales: extreme wide / wide / full / medium-wide / medium / medium-close / close-up / extreme
  close-up / insert. Each carries intent — wide = context & scale, close = emotion & detail. Full
  bilingual glossary + camera angles (picado, contrapicado, dutch) + ratios in
  `references/shot_types.md`.
- Subject placement: rule of thirds, centered (symmetry/formality), headroom, lead/look room.
- Vertical position of horizon sets dominance (low horizon = grandeur, high = oppression).

### 2. Composition
- Leading lines, framing-within-frame, foreground occlusion (depth layers: FG / MG / BG).
- Balance vs. tension; negative space; symmetry (Wes Anderson) vs. dynamic diagonals.
- Always describe at least foreground + background in prompts to force depth.

### 3. Lens & depth
- Focal length feel: wide (18–28mm — exaggerated space, environmental), normal (35–50mm — natural),
  tele (85–135mm — compression, isolated subject, creamy bokeh).
- Aperture: shallow DoF (f/1.4–2.8 — subject isolation, bokeh) vs. deep (f/8+ — everything sharp).
- Anamorphic traits: oval bokeh, horizontal blue lens flares, 2.39:1, subtle edge distortion.
- Prompt words that pull lens feel: "85mm portrait lens, shallow depth of field, creamy bokeh",
  "anamorphic widescreen, horizontal flares".

### 4. Lighting & exposure
- Direction: front / side (modeling) / back (rim, separation) / top / under.
- Quality: hard (sharp shadows, drama) vs. soft (diffused, flattering).
- Schemes: high-key (bright, low contrast, upbeat), low-key (dark, high contrast, moody/noir),
  chiaroscuro, motivated practicals (neon, lamps, windows).
- Times that read instantly: golden hour, blue hour, overcast, harsh noon, night-interior-practicals.
- Key terms: "soft rim light", "single hard key, deep shadows", "neon practical lighting",
  "volumetric god rays", "backlit haze".

### 5. Color & grade
- Palette: complementary (teal-orange), analogous (warm amber), monochrome, pastel, desaturated.
- Contrast & black level: crushed blacks vs. lifted/faded; filmic toe.
- Temperature & tint shift the mood more than any single word — name both ("cool teal shadows,
  warm skin tones").
- Reference grades: "Kodak Vision3 film stock", "bleach-bypass desaturated", "Fuji pastel",
  "teal-and-orange blockbuster grade".

### 6. Camera movement
One dominant move per shot. Map intent to move:
- Static / locked-off — observation, formality.
- Slow push-in (dolly/zoom) — rising tension, intimacy.
- Pull-out — reveal, isolation, ending beat.
- Tracking / dolly lateral — follows subject, parallax.
- Crane / boom — scale, transition between heights.
- Handheld — urgency, realism, unease.
- Whip pan / crash zoom — energy, comedic or action punctuation.
- Orbit / arc — showcases subject in 3D space.
- FPV drone — kinetic continuous flythrough.
- Speed ramp — stylized action emphasis.

### 7. Edit rhythm & pacing
- Average shot length (ASL): long takes (8s+) = contemplative; rapid cuts (<1s) = energetic/montage.
- Match cuts, J/L cuts (audio), cut on action, cut on the beat.
- For AI generation: pacing is decided at assembly — design each clip's duration to serve the
  intended ASL of the sequence.

## Style cheat sheet (look → settings)

For a *named director* instead of a generic look, use `references/directors.md` (Tarantino, Kubrick,
Wes Anderson, Fincher, Villeneuve, WKW, Deakins, Bay) — it gives signatures + settings + prompt seeds.

| Look | Lens/DoF | Light | Color | Move | Pacing |
|---|---|---|---|---|---|
| A24 intimate drama | 35–50mm, shallow | soft window/practical | muted, lifted blacks | slow push / static | long takes |
| Blockbuster action | anamorphic wide | hard key, haze | teal-orange | crash zoom, tracking | fast cuts |
| Noir / thriller | 50mm, shallow | low-key chiaroscuro | desaturated, deep blacks | slow dolly, handheld | medium |
| Neon nightlife (WKW/CP2077) | 85mm, very shallow | neon practicals, rim | magenta-cyan | slow tracking, handheld | varied |
| Nature doc / epic | wide deep focus | golden hour, god rays | rich saturated | crane, slow orbit | long |
| FPV / hype reel | ultrawide | high-key sun | punchy contrast | FPV drone, speed ramp | very fast |
| Dreamy / ethereal | tele, dreamy bokeh | backlit haze, bloom | pastel, warm | slow float/orbit | slow |
| Documentary realism | 35mm normal | available light | natural/neutral | handheld | naturalistic |

## Prompt formula

Write every shot prompt in this order; omit nothing the look needs:

```
[subject + key detail] , [action] , [setting/environment + FG/BG depth] ,
[lens + focal length + depth of field] , [light direction + quality + time] ,
[color palette + grade + contrast] , [film stock / grain / texture] , [mood word]
```

Example:
> Lone traveler in a wool coat, walking away slowly, rain-slick neon alley with steam in the
> foreground and blurred signage behind, 85mm anamorphic, shallow depth of field with oval bokeh,
> soft magenta rim light at blue hour, cyan-and-magenta palette with crushed blacks, Kodak Vision3
> grain, melancholic.

Then append ONE camera **move** as an explicit phrase at the end (Phase 4), e.g. "— slow dolly
push-in". Keep the prose about the frame and the move as a distinct clause (see
`references/camera_motion.md`). There are no preset flags; the move lives in the prompt text.

## Quick analysis checklist (per reference shot)
1. Scale & where the subject sits in frame.
2. Depth layers present? Lens feel (wide/normal/tele), DoF.
3. Light direction, hardness, scheme, time of day.
4. Dominant 2–3 colors, contrast, black level.
5. The one camera move.
6. How long the shot holds (ASL contribution).
