# Director & auteur signatures — read and reproduce a style

When a user says "make it like Tarantino" or a reference clearly imitates a filmmaker, decode the
style into the seven craft axes (`cinematography.md`) + the shot/angle vocabulary
(`shot_types.md`), then build prompts from those. Each entry below lists the **signature moves**,
the **look settings**, and a **ready prompt seed** you can adapt. Pick 2–4 signatures per project —
piling on all of them reads as parody.

## Quentin Tarantino
- **Signatures:** the *trunk shot* (low POV from inside a car trunk looking up at characters); the
  *foot/low-angle insert*; *God's-eye overhead* inserts (an object on a table from directly above);
  long uninterrupted **dialogue takes** with slow push-ins; the **profile two-shot** of people
  talking in a car's front seats; the **Mexican standoff** (multiple subjects, criss-crossed
  eyelines, rising cut rhythm); sudden **snap/crash zoom** for emphasis; **chapter-title** structure.
- **Look:** shot on 35mm / anamorphic, saturated retro 70s palette, 2.39:1 scope, deep blacks,
  lived-in diner/desert/Americana production design, tactile film grain.
- **Pacing:** patient dialogue (long ASL) that detonates into fast-cut violence (low ASL) — the
  contrast IS the style. Build it at assembly.
- **Prompt seed:** "Low angle trunk-shot POV looking up at two figures in retro 70s wardrobe, harsh
  noon desert light, saturated warm Americana palette, anamorphic 2.39:1, 35mm film grain, deep
  blacks, tense — slow dolly push-in." Pair with a separate overhead-insert shot and a snap-zoom shot.

## Wes Anderson
- **Signatures:** dead-center **symmetrical** one-point-perspective framing; flat, planar staging
  (subjects face camera square-on); **whip pans** between symmetrical setups; **snap zooms**;
  precise **overhead inserts** of objects; chaptered, dollhouse blocking.
- **Look:** pastel + primary palette, 1.85:1 or boxed 4:3, flat even soft light, meticulous
  production design, vintage textures.
- **Prompt seed:** "Perfectly symmetrical centered composition, subject facing camera dead-on, pastel
  storybook palette, flat even soft lighting, 1.85:1, fine grain, whimsical and precise — static
  locked-off shot" (or "fast whip pan to the next symmetrical setup").

## Stanley Kubrick
- **Signatures:** **one-point perspective** corridors receding to a center vanishing point; slow
  relentless **dolly/Steadicam tracking**; the **Kubrick stare** (low-angle close-up, head tilted
  down, eyes up); rigorous symmetry; wide lenses for cold geometric space.
- **Look:** cold controlled palette, natural/practical light (famous candlelit interiors), deep
  focus, clinical.
- **Prompt seed:** "One-point perspective corridor receding to a central vanishing point,
  symmetrical, wide lens deep focus, cold controlled palette, clinical and ominous — slow relentless
  dolly push-in down the corridor."

## David Fincher
- **Signatures:** locked, exact, often **invisible motivated camera moves**; muted desaturated
  digital cleanliness; underexposed shadows with a single hard key; precise reframing, no handheld.
- **Look:** desaturated green/amber, crushed shadows, very low-key, sharp clean digital, 2.39:1.
- **Prompt seed:** "Subject lit by a single hard key in deep shadow, desaturated green-amber palette,
  crushed blacks, clean sharp digital, 2.39:1, cold and methodical — slow precise dolly push-in."

## Denis Villeneuve
- **Signatures:** monumental **scale** (tiny humans against vast structures), brutalist negative
  space, slow **god's-eye** and slow lateral drifts, atmospheric haze/fog, monochrome tonal blocks.
- **Look:** desaturated monochrome washes (amber, slate, ash), volumetric haze, anamorphic 2.39:1,
  rich blacks, immense.
- **Prompt seed:** "A lone figure dwarfed by a colossal monolithic structure, brutalist negative
  space, thick atmospheric haze, desaturated amber monochrome wash, anamorphic 2.39:1, awe and
  dread — slow majestic crane up revealing the scale."

## Wong Kar-wai (neon intimacy)
- **Signatures:** smeared **step-printed** slow motion, saturated neon practicals, tight claustral
  framing through foreground occlusion, longing handheld drift.
- **Look:** magenta-cyan-amber neon, very shallow 85mm, rain/steam, lush grain.
- **Prompt seed:** "Lovers half-hidden behind foreground clutter in a cramped neon-lit room, saturated
  magenta and cyan practicals, 85mm very shallow depth of field, steam and rain, lush film grain,
  longing — slow drifting handheld."

## Roger Deakins look (naturalist master cinematographer)
- **Signatures:** motivated naturalistic light that still sculpts; silhouettes against a single
  strong source; restraint; clean wides with one clear light idea.
- **Look:** warm/cool single-source motivation, controlled contrast, deep but readable shadows.
- **Prompt seed:** "Subject silhouetted against a single warm window source, motivated naturalistic
  light, controlled filmic contrast, deep readable shadows, restrained and beautiful — static
  locked-off shot."

## Michael Bay / hype-action
- **Signatures:** low-angle **hero shots**, constant motion, lens flares, golden-hour backlight,
  fast cuts, orbiting Steadicam around the subject ("Bay-hem" 360 orbit).
- **Look:** teal-orange, high contrast, haze, anamorphic flares.
- **Prompt seed:** "Low-angle hero shot of the subject at golden hour, anamorphic lens flares, teal-
  orange high-contrast grade, haze, epic and kinetic — camera orbits 360° around the subject."

## How to apply
1. Identify the auteur (user-named, or inferred from the reference's signatures).
2. Pull **2–4** signatures + the look row into the Look Recipe — note which ones, don't use all.
3. Translate each chosen signature into shot-scale/angle terms (`shot_types.md`) and a camera move
   (`camera_motion.md`), then assemble the prompt with the standard formula.
4. Respect the **pacing**: many auteur styles live as much in the ASL/cut rhythm as in any single
   frame — set that at assembly (`assemble.py`), not inside one prompt.
