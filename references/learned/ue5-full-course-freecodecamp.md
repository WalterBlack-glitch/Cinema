---
topic: Unreal Engine 5 — curso completo para principiantes (fundamentos)
slug: ue5-full-course-freecodecamp
source: https://www.youtube.com/watch?v=6UlU_FsicK8
author: freeCodeCamp.org
kind: video
learned: 2026-06-13
---

# UE5 Full Course for Beginners — fundamentos

Curso base de UE5: navegación, Blueprints, materiales, iluminación, landscape, packaging.
Referencia de fundamentos para la capa "aplicar en UE5" de Cinema y para NovaSurvival.

## Principios (accionables)

- **Editor**: viewport WASD + clic derecho para navegar; Outliner = jerarquía de actores,
  Details = propiedades, Content Browser = assets. Todo es un Actor con Components.
- **Blueprints = scripting visual.** Event Graph (lógica por eventos: BeginPlay, Tick, Input),
  variables tipadas, funciones. Regla de oro: Tick es caro — usa eventos/timers cuando puedas.
- **Materiales**: nodos sobre `Material` → conectar a Base Color/Metallic/Roughness/Normal/Emissive.
  Material Instances para variar parámetros sin recompilar el shader (clave para iterar y para data-driven).
- **Iluminación (Lumen por defecto en UE5)**: Directional Light (sol) + Sky Atmosphere + SkyLight +
  Exponential Height Fog dan un cielo creíble en 4 actores. Post Process Volume para exposición,
  tonemap y color grade. **Cuidado**: un Directional Light apuntando mal = escena negra (pitch del sol).
- **Lumen GI + reflections** es tiempo real, sin bake — pero cuesta; Nanite para geometría densa
  sin preocuparse por polycount/LODs.
- **Landscape**: esculpir terreno con brushes; material de landscape con layers por pintura (hierba,
  roca, tierra). Es la vía real para relieve (vs. plano).
- **Cámara cinemática**: CineCameraActor + Sequencer (LevelSequence) para animar transform, focal
  length y DOF por keyframes; Camera Cut track para montar planos.
- **Packaging**: Platforms → Windows → Shipping; revisar que los mapas/assets estén referenciados
  o incluidos para que no falten en el build.

## Aplicación en 3D (UE5 — refuerza el adapter de Cinema)

- **Cámara/lente**: CineCameraActor, focal por mm real, f-stop para DOF; animar en Sequencer.
- **Luz**: Directional + SkyAtmosphere + SkyLight + HeightFog; Post Process para exposición/grade.
- **Color**: Post Process Volume con tonemap (AgX/ACES), color grading wheels, bloom controlado.
- **Movimiento**: Sequencer transform track; ease in/out en keyframes para dolly/crane suaves.

> Fundamentos que respaldan `references/dcc/ue5.md` y el trabajo en NovaSurvival (UE5.7).
> Cita: `[[learned/ue5-full-course-freecodecamp]]`
