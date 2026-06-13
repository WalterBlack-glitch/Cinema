---
topic: Creación de texturas para VFX (noise, gradientes, flipbooks, channel packing)
slug: vfx-texture-creation-lelu
source: https://www.youtube.com/watch?v=dMthnzpR-eU
author: Le Lu
kind: video
learned: 2026-06-13
---

# VFX Texture Creation — guía Le Lu

Las texturas son el material base de casi todo VFX de tiempo real (humo, fuego, magia, impactos).
Saber qué mapa hace qué y cómo empaquetarlos es lo que separa un efecto plano de uno con vida.

## Principios (accionables)

- **Tres familias de textura cubren casi todo:**
  1. **Noise** (perlin/worley/curl) — turbulencia, disolución, distorsión UV.
  2. **Gradientes** (lineal, radial, esférico) — máscaras de fade, forma base, control de erosión.
  3. **Shapes/flipbooks** — formas concretas (chispa, salpicadura, humo simulado en frames).
- **Tilea SIEMPRE el noise.** Un noise que no tilea se nota en bucles y scroll de UV. Generarlo
  tileable de origen (Substance Designer, o nodos con wrap) — corregirlo después es dolor.
- **Channel packing = rendimiento.** Mete 3-4 máscaras grises en RGBA de una sola textura
  (ej. R=noise erosión, G=gradiente, B=máscara alpha, A=motion). Una muestra en vez de cuatro;
  crítico en VFX donde hay overdraw alto.
- **Flipbooks: simula caro una vez, reproduce barato.** Sim de humo/fuego (EmberGen/Houdini) →
  hornear a sheet NxN (típico 8x8). En el material, lerp entre frames para suavizar (motion vectors
  si quieres fluidez real con menos frames).
- **Erosión = noise + gradiente + smoothstep.** El "disolverse" de casi todo VFX es:
  `mask = smoothstep(threshold-soft, threshold, noise*gradient)`, animando `threshold`. Un solo
  patrón que sirve para fuego, materializaciones, daño, bordes ardientes.
- **Distorsión UV con flow/noise** da el "calor/energía" — sumar un noise paneado a las UV antes
  de muestrear la textura principal. Barato y vende muchísimo movimiento orgánico.
- **Grises, no color, en las máscaras.** El color se aplica en el material con gradientes/ramps;
  las texturas guardan datos (máscaras) para máximo reuso entre efectos.

## Aplicación en 3D

- **Blender**: noise/gradient nodes → bake a imagen tileable; Shader con Mix por smoothstep para erosión.
- **UE5**: Material con `Texture Sample` channel-packed, `SubUV`/flipbook node para sheets, `Panner`
  + noise para distorsión UV; Niagara para emisión.
- **Godot 4**: `NoiseTexture2D` (FastNoiseLite) tileable, ShaderMaterial con `texture()` + smoothstep
  para disolución, `TIME`-driven UV scroll; partículas GPUParticles con flipbook en el material.
- **Color**: máscaras en grises; color final por gradient ramp en el shader, emisión para glow.

> Base reusable para todo efecto de NovaSurvival (magia, humo de hoguera, impactos de tala/combate).
> Cita: `[[learned/vfx-texture-creation-lelu]]`
