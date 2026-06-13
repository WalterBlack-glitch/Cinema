# cinema

Skill de Claude para **aprender** cinematografía y craft 3D desde cualquier fuente (video, URL, PDF, texto) y **aplicarla** en múltiples entornos: Higgsfield (cloud), LTX-Video (local), Blender, Unreal Engine 5 y Godot 4.

## Capacidades

- **Aprendizaje** (`scripts/learn.py`): ingiere video local, YouTube/Vimeo, URL de artículo o PDF → destila en `references/learned/<slug>.md` citable.
- **Aplicación 3D** (`scripts/apply/`): toma un brief .md de shots y emite scripts ejecutables:
  - `blender.py` → `.py` con `bpy` (CineCamera + DOF + 3-point lights + EEVEE Next + H.264).
  - `ue5.py` → Python para Sequencer + CineCameraActor + PostProcessVolume.
  - `godot.py` → `.tscn` + `.gd` (Camera3D + AnimationPlayer + WorldEnvironment ACES + SDFGI).
- **Autodetección** (`scripts/env.py`): detecta qué DCC está abierto (Blender 9876 / UE5 6766 / Godot 6007) y enruta al adapter correcto.
- **Generación cloud** (`scripts/generate.py --engine higgsfield`): driver del CLI `higgsfield`.
- **Generación local** (`scripts/generate_video_local.py`): video diffusion con LTX-Video 0.9.5 vía ComfyUI (RTX 4050 6GB ok).
- **Análisis** (`scripts/analyze_video.py`, `contact_sheet.py`, `extract_palette.py`): ASL, paleta, contact sheets.
- **Cine Studio** (`ui/`): app de escritorio (pywebview/WebView2) que orquesta todo.

## Instalación

```sh
# Como skill de Claude Code
cp -r cinema ~/.claude/skills/

# Como skill de npx skills
cp -r cinema ~/.agents/skills/
```

Dependencias (Python global): `yt-dlp opencv-python numpy imageio-ffmpeg pywebview`.

## Uso

```sh
# Aprender de un video YouTube
python scripts/learn.py "https://youtu.be/..." --topic "iluminación noir"

# Detectar DCC abierto
python scripts/env.py detect

# Aplicar un brief al DCC abierto
python scripts/env.py apply assets/examples/example_noir_neon.md

# Generar video local (LTX-Video, gratis, requiere ComfyUI corriendo)
python scripts/generate_video_local.py --prompt "..." --seconds 4
```

## Estructura de un brief

```yaml
---
title: Mi escena
fps: 24
resolution: [1920, 1080]
---

## shot 1
- lens: 35mm
- aperture: f/2.0
- camera_move: dolly-in
- duration: 4s
- lighting: hora dorada, god rays
- color: teal & orange
- refs: [[learned/ue5-environments-master]]
```

## Referencias incluidas

- `references/cinematography.md` — 7 ejes del lenguaje cinematográfico.
- `references/shot_types.md` — planos ES/EN, ratios, ASL.
- `references/directors.md` — firmas de Tarantino, Kubrick, Wes Anderson, Fincher, Villeneuve, WKW, Deakins, Bay.
- `references/camera_motion.md` — vocabulario de movimientos.
- `references/dcc/{blender,ue5,godot}.md` — APIs mínimas por DCC.
- `references/learned/` — conocimiento destilado de fuentes externas.

## Licencia

MIT. Las referencias destiladas de fuentes terceras (`references/learned/`) son resúmenes/principios derivados, no contenido reproducido.
