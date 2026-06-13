---
topic: Fundamentos de Unreal Engine (documentación oficial Epic)
slug: ue5-basics-epic-docs
source: https://dev.epicgames.com/documentation/unreal-engine/understanding-the-basics-of-unreal-engine
kind: article
learned: 2026-06-13
---

# Fundamentos de UE5 — docs oficiales Epic

Página índice oficial de los conceptos base de Unreal Engine. Vocabulario canónico de Epic
(útil para no inventar términos y alinear NovaSurvival con la nomenclatura real).

## Conceptos clave (canónicos)

- **Editor / Foundational Knowledge**: interfaz, terminología, herramientas, preferencias,
  estructura de directorios, plugins y atajos de teclado. El editor es el centro de todo.
- **Content Browser**: herramienta para ver/gestionar/usar todos los **Assets** del proyecto.
  Toda creación de contenido pasa por aquí (importar, organizar, migrar).
- **Projects & Templates**: un proyecto se crea desde templates (o custom); estructura estándar
  `Content/`, `Config/`, `Plugins/`. Migrar assets entre proyectos vía Content Browser.
- **Levels (Maps)**: contienen TODO lo que el jugador ve e interactúa. Un nivel = un mundo cargable.
- **Assets & Content Packs**: importar, organizar, migrar y gestionar el contenido. Los packs de Fab
  son content packs que se añaden al `Content/`.
- **Actors & Components**: el **Actor** es la unidad colocable en un nivel; los **Components** se
  enganchan al Actor para darle capacidades (malla, colisión, lógica). Composición sobre herencia.
- **Playing & Simulating (PIE)**: probar dentro del editor sin empaquetar (Play In Editor / Simulate).
- **Building/Packaging**: empaquetar para distribución por plataforma (Shipping/Development).

## Por qué importa para Cinema / NovaSurvival

- **Vocabulario correcto**: Actor, Component, Level/Map, Asset, Content Browser, PIE, Package.
  Usar estos términos exactos en docs/scripts evita ambigüedad con conceptos de Godot.
- **Modelo Actor+Component** = el equivalente UE a la composición de nodos de Godot; encaja con la
  arquitectura modular de NovaSurvival (componentes por feature, no monolitos).
- **Todo content-driven pasa por Content Browser + Asset Manager**: refuerza la regla §2 de
  NovaSurvival (DataAssets escaneables).

## Aplicación en 3D (UE5)

- **Cámara/lente**: los actores cinemáticos (CineCameraActor) son Actors con Components; viven en un Level.
- **Luz**: las luces son Actors (Directional/Sky/Point) colocados en el Level.
- **Color/Post**: Post Process Volume es un Actor con component de volumen.
- **Flujo**: importar asset (Content Browser) → colocar Actor en Level → ajustar Components → PIE → Package.

> Base canónica que respalda `references/dcc/ue5.md`. Complementa `[[learned/ue5-full-course-freecodecamp]]`
> (curso práctico) con la terminología oficial. Cita: `[[learned/ue5-basics-epic-docs]]`
