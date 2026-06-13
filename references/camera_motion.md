# Camera motion in prompts (no presets)

Higgsfield video models (Seedance 2.0, Kling, etc.) have **no named motion presets** — the camera
move is part of the **prompt text**. This file maps each craft move (cinematography.md axis 6) to
phrasing the model understands. Rules:

- **One dominant move per clip.** Two competing moves degrade output.
- State the move explicitly and early, with a speed/intensity word ("slow", "fast", "subtle").
- Keep the move separate from the frame prose: describe the frame, then the motion.
- For precise begin→end motion, prefer `--start-image` + `--end-image` over wordy description.

## Craft move → prompt phrasing

| Craft move | Say in the prompt | Notes / intensity words |
|---|---|---|
| Static / locked-off | "static locked-off shot", "still camera" | keep duration short; let subject move |
| Slow push-in | "slow dolly push-in toward the subject" | "creeping", "gentle"; rising tension |
| Pull-out / reveal | "slow dolly pull-back revealing the scene" | "gradual"; ending beat |
| Lateral tracking | "tracking shot following the subject left to right" | add "with parallax" for depth |
| Crane / boom up | "crane up rising above the scene" | "sweeping"; scale/transition |
| Crane / boom down | "crane down descending toward the subject" | |
| Orbit / arc | "camera orbits around the subject" | "slow 180° arc"; showcases 3D |
| Handheld | "handheld camera, subtle natural shake" | "documentary", "urgent" for more |
| Crash zoom | "fast crash zoom in" | punctuation; use sparingly |
| Whip pan | "fast whip pan to the next subject" | transitions |
| FPV / flythrough | "FPV drone flythrough rushing through the space" | "kinetic", "continuous"; reels |
| Speed ramp | "speed-ramped action, accelerating then slowing" | stylized action |
| Rack focus | "rack focus from foreground to background" | pairs with shallow DoF prose |
| Dolly zoom (vertigo) | "dolly zoom, background warps while subject stays" | dramatic unease |

## Combine with the frame prose

Full prompt = frame prose (subject, action, setting+depth, lens, light, color/grade, film stock,
mood) **+** one motion phrase. Example:

> Lone traveler in a wet wool coat walking away, rain-slick neon alley with steam in the foreground
> and blurred signage behind, 85mm anamorphic shallow depth of field with oval bokeh, soft magenta
> rim light at blue hour, cyan-magenta palette crushed blacks, film grain, melancholic —
> **slow dolly push-in toward the figure**.

## Speed & duration interaction
- Longer `--duration` makes a slow move read as slower and more elegant; short durations suit
  punchy moves (crash zoom, whip pan).
- If a move feels too strong/weak in the output, reword the speed adjective and/or change
  `--duration` before changing anything else.
