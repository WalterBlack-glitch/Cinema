---
topic: Escena de batalla épica en Blender (multitudes + VFX + cámara)
slug: blender-battle-scene-fxforge
source: https://www.youtube.com/watch?v=NEG9lafbzvI
author: FxForge (Albin Thorburn)
kind: video
learned: 2026-06-13
---

# Escena de batalla en Blender — workflow FxForge

Cómo se arma un plano de batalla creíble en Blender sin un pipeline de estudio:
multitud procedural barata, polvo/humo/impacto como VFX, y una cámara que vende la escala.

## Principios (accionables)

- **La multitud es geometry nodes, no rigs.** Instanciar agentes sobre una malla de terreno
  con `Distribute Points on Faces` + `Instance on Points`; variar rotación/escala con `Random Value`
  para romper la repetición. Para movimiento, offset por ruido temporal — no animar cada agente.
- **Profundidad por capas (layout en Z).** Foreground (pocos agentes detallados) → midground (grueso
  de la multitud instanciada) → background (cards/siluetas o niebla). El ojo lee escala por solape
  y por gradiente de densidad, no por polycount.
- **La atmósfera hace el 80% del drama.** Niebla volumétrica + haces de luz (god rays) + polvo en
  suspensión separan los planos de profundidad y unifican la paleta. Sin volumetría, una batalla
  se ve como muñecos sobre un suelo plano.
- **VFX = pocas sims, muchas instancias.** Una sim de humo/polvo buena se reusa como instancia en
  múltiples impactos; flipbooks/cards para chispas y debris lejano. Caro solo lo cercano a cámara.
- **La cámara vende la escala.** Lente larga (85–135mm) comprime las filas y las hace parecer
  infinitas; cámara baja mirando arriba agranda a los agentes. Movimiento lento (dolly/crane) +
  ligero shake handheld da peso. Nada de paneos rápidos: matan la sensación de masa.
- **Color y contraste cuentan la historia.** Cielo apagado/desaturado + un acento cálido (fuego,
  estandarte) que guía el ojo. Grade final: bajar negros, niebla atmosférica para integrar capas.

## Aplicación en 3D

- **Cámara/lente**: CineCamera, 85–135mm, f/2.8–4, cámara a ~1.6m mirando ligeramente arriba.
  Dolly-in lento o crane-up; añadir noise sutil al transform para handheld.
- **Luz**: Sun key rasante (god rays a través de volumen) + fill frío de cielo. WorldEnvironment
  con volumetric fog. Un práctico cálido por foco de interés.
- **Color**: paleta desaturada fría con 1 acento cálido; tonemap ACES/AgX, negros levantados por niebla.
- **Movimiento**: agentes por geometry nodes con offset de ruido temporal; VFX caros solo en foreground.

> Aplica directo a Granja Nova/NovaSurvival cuando se quiera un plano de masa (rebaño, horda, ejército):
> instanciar barato + volumetría + lente larga. Cita: `[[learned/blender-battle-scene-fxforge]]`
