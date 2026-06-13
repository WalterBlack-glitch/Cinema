# Shot types, angles & ratios — glossary (ES/EN)

Naming the frame precisely is half the craft. Use these exact terms when scoring a reference and
when writing prompts — the model responds far better to "medium close-up, chest up" than "a normal
shot". Spanish ↔ English mapping included because references and briefs here are bilingual.

## 1. Shot scale (escala de plano) — wide → tight

| Español | English | What's in frame | Reads as | Prompt phrase |
|---|---|---|---|---|
| Gran plano general (GPG) | Extreme wide / establishing | Subject tiny in a vast space | Scale, isolation, context | "extreme wide establishing shot, figure small in frame" |
| Plano general (PG) | Wide / long shot | Full body + lots of environment | Place & action | "wide shot, full body with surrounding environment" |
| Plano entero (PE) | Full shot | Full body, feet to head, tight to edges | The whole person | "full shot, head to feet" |
| Plano americano (PA) | American / cowboy shot | Mid-thigh up (knees to head) | Stance, presence, the classic Western | "american shot framed from mid-thigh up" |
| Plano medio (PM) | Medium shot | Waist up | Conversation, gesture | "medium shot, waist up" |
| Plano medio corto | Medium close-up (MCU) | Chest/shoulders up | Intimacy without losing body language | "medium close-up, chest up" |
| Primer plano (PP) | Close-up (CU) | Head & shoulders / the face | Emotion | "close-up on the face" |
| Primerísimo primer plano (PPP) | Big / extreme close-up (ECU) | Eyes, mouth, a single feature | Tension, detail | "extreme close-up on the eyes" |
| Plano detalle (PD) | Insert / detail | An object (hands, a watch, a trigger) | Significance of a thing | "insert detail of <object>, macro" |

Two-shot / three-shot (plano a dos / a tres) = N subjects sharing the frame; name it when a relationship matters.
Over-the-shoulder (escorzo / plano sobre el hombro) = "over-the-shoulder shot past <A> onto <B>".
Point-of-view (plano subjetivo / POV) = "POV shot, as if through the character's eyes".

## 2. Camera angle (angulación) — vertical & roll

| Español | English | Effect | Prompt phrase |
|---|---|---|---|
| Picado | High angle (looking down) | Subject weak, small, observed | "high angle looking down on the subject" |
| Contrapicado | Low angle (looking up) | Subject powerful, heroic, looming | "low angle looking up, subject towering" |
| Cenital / picado total | Top / overhead / bird's-eye / God's-eye | Pattern, fate, omniscience | "overhead top-down God's-eye shot" |
| Nadir / contrapicado total | Worm's-eye | Disorientation, monumentality | "extreme low worm's-eye shot" |
| Plano a la altura de los ojos | Eye-level | Neutral, naturalistic | "eye-level shot" |
| Plano holandés / cámara inclinada | Dutch / canted angle | Unease, instability, madness | "dutch tilt, horizon canted" |

## 3. Ratios — the three "ratios" that matter

These are distinct; name which you mean.

- **Aspect ratio (relación de aspecto)** — frame shape. Maps to `--aspect_ratio`.
  - 2.39:1 (anamorphic scope) → epic, cinematic, Tarantino/Villeneuve. **The CLI has no 2.39:1 —
    use `--aspect_ratio 21:9`** (closest scope) and say "anamorphic 2.39:1" in the prompt prose.
  - 1.85:1 / 16:9 → standard widescreen. `--aspect_ratio 16:9`
  - 4:3 (Academy 1.37) / 1:1 → vintage, intimate, boxed-in (Wes Anderson interiors, *The Lighthouse*).
  - 9:16 → vertical social. `--aspect_ratio 9:16`
- **Cutting ratio / ASL (ritmo de montaje)** — average shot length = total runtime ÷ number of cuts.
  Low ASL (<1.5 s) = montage/action energy; high ASL (8 s+) = contemplative long takes. `analyze_video.py`
  reports it. In this toolchain you set ASL at **assembly** (clip durations + cut frequency), not in one prompt.
- **Shooting ratio (ratio de rodaje)** — footage shot vs. used (e.g. 10:1). For AI gen the analog is
  **how many variants you generate per keeper** — budget 2–4 generations per final shot for motion-heavy looks.

## 4. Composition ratios (where the subject sits)
- **Rule of thirds (regla de los tercios)** — subject on a third line / intersection. Default for natural framing.
- **Golden ratio / phi grid** — tighter spiral placement; elegant, classical.
- **Centered / symmetry (composición simétrica)** — formality, control (Kubrick one-point perspective, Wes Anderson).
- **Headroom / look room / lead room (aire)** — space above the head, and ahead of a gaze or a moving subject.
  Too little = claustrophobic (sometimes intentional); too much = subject sinks.

## 5. How to use this in the workflow
1. **Analyzing a reference:** for each detected shot, name the scale + angle + which composition ratio + the aspect ratio. Write them into the Look Recipe "Shot scale & framing" and "Composition" rows.
2. **Designing shots:** vary scale deliberately across the sequence (wide to establish → medium for action → close for emotion); don't shoot everything at the same plano.
3. **Writing the prompt:** drop the exact phrase from the tables above near the front of the prompt, before lens/light/color (see the prompt formula in `cinematography.md`).
