---
topic: UE5 environment & cinematic mastery (Gorka Games playlist)
slug: ue5-environments-master
source: https://www.youtube.com/playlist?list=PLGEDpELN0zHDiStehu4bleZ7KVhOaGAUK
kind: video-playlist
videos: 40+
ingested_via: yt-dlp auto-subs (acelerado)
---

# UE5 environments — master reference

Playlist completa (40+ tutoriales) destilada a principios accionables para crear entornos de calidad en Unreal Engine 5. Citable como `[[learned/ue5-environments-master]]` en briefs.

## Videos núcleo destilados

### 1. Creating an Island (1cfPiofNy-U) — base de Landscape + Water
- **Setup**: New Level → Basic (no Open World) para entornos contenidos. Plugins requeridos: **Landmass** y **Water** (Edit → Plugins → reiniciar editor).
- **Landscape**: modo Landscape → activa **Edit Layers** (capas tipo Photoshop, no destructivo). Tamaño 8×8 componentes con 2×2 sections por componente = isla pequeña controlada.
- **Sculpt workflow**: crea capa nueva por experimento → brush size + strength → si no funciona, borra capa entera (no destructivo).
- **Water**: el plugin Water spawnea actores Ocean/River/Lake que tallan automáticamente el landscape (la "playa" se genera sola por la interacción Water+Landmass).
- **Foliage**: pinta vegetación con densidad escalada por máscara (slope + altitud).

### 2-40. Patrones recurrentes en toda la playlist
- **Landscape materials**: layer blend con 3-5 capas (rock, grass, sand, snow, dirt) mezcladas por slope/altitud/world-aligned. Megascans Quixel como fuente PBR.
- **Sequencer cinematics** (videos "God Rays", "How to Make Cinematics"): CineCameraActor + LevelSequence + CameraCutTrack. God rays = Exponential Height Fog + Volumetric Fog + Directional Light "Light Shaft Bloom/Occlusion" on.
- **Niagara VFX** (snow, fluids, weapon glow): emitters CPU/GPU, módulos Spawn Rate + Initialize Particle + Add Velocity + Sprite/Mesh Renderer. Fluids 5.2+ con Niagara Fluid templates.
- **Blueprints**: comunicación entre BPs vía Interfaces (preferido) → Event Dispatchers (broadcast) → Direct Cast (último recurso, costoso).
- **Procedural Content Generation (PCG)** 5.2+: PCGGraph con Surface Sampler + Static Mesh Spawner + Density Filter por slope/material. Substituye foliage tradicional para bosques densos.
- **Modeling Tools** (in-editor): Cube/Sphere primitivos → Poly Edit → Boolean → Triplanar UV. Útil para castle ruins, crystal mine sin Blender.
- **Nanite**: virtualized geometry, ON para todo asset estático >50k triángulos. OFF para foliage con WPO (wind), transparencias o Megascans con holes.
- **Lumen**: GI dinámica default UE5. Hardware Ray Tracing ON si GPU≥3060. Para escenas oscuras: aumenta Lumen Scene → Final Gather Quality.
- **Foot IK / Retargeting**: IK Rig + IK Retargeter para usar Mixamo en cualquier rig. Foot placement con Control Rig + line traces.
- **Vertex Paint**: pinta máscara en cualquier mesh para revelar segundo material (musgo, polvo, nieve).
- **Chaos Destruction**: Geometry Collection desde meshes → Fracture (Voronoi 20-50 cells) → Cluster → simula Apply Force.

## Principios cinemáticos transversales (aplicables en cualquier env)

- **Composición**: regla de tercios + leading lines naturales (ríos, caminos, troncos caídos). Foreground/midground/background con 3 layers de detalle.
- **Luz**: 1 Directional (sol) + 1 Sky Light (rebote) + Exponential Height Fog + Volumetric Fog. Hora dorada = ángulo solar 15-25° + temperatura 3000-4000K + Fog Density 0.05.
- **Color**: PostProcessVolume con Color Grading → split toning (highlights cálidos, shadows fríos). LUT custom si se quiere look específico.
- **Atmósfera**: Sky Atmosphere (Rayleigh + Mie scattering físico) + Volumetric Cloud (procedural, NO planos).
- **Escala**: usar referencia humana (mannequin BP_ThirdPersonCharacter) en escena DURANTE construcción para no perder proporción.
- **Polish pass**: micro-detail con decals (cracks, leaks, dirt), pequeñas variaciones de rotación/escala en assets repetidos (foliage no debe ser uniforme).

## Aplicación en 3D

- **Cámara/lente**: CineCameraActor con focal 24-35mm para paisajes amplios, 50-85mm para retratos del entorno. F-stop f/4-8 para mantener foco profundo.
- **Luz**: Directional sun + Sky Light + Volumetric Fog. Para god rays: Light Shaft Bloom/Occlusion en Directional Light.
- **Color**: PostProcessVolume con tonemap ACES (default UE5), bloom 0.5-0.8, film grain 0.1-0.2, vignette 0.3.
- **Movimiento**: en Sequencer, anima transform de CineCamera con curvas EaseIn/EaseOut (no Linear) — el adapter `apply/ue5.py` ya las pone linear, ajustar manualmente para shots cinemáticos.

## Cómo usar esta referencia

En un brief .md, cita así en cualquier shot:

```
## shot 1
- lens: 28mm
- camera_move: crane-up
- duration: 6s
- lighting: hora dorada, god rays, volumetric fog
- color: teal & orange, ACES
- refs: [[learned/ue5-environments-master]]
```

El adapter `apply/ue5.py` lee la cita y aplica los principios al PostProcessVolume y al Sequencer generado.

## Lista completa de videos de la playlist

```
Creating an Island                              1cfPiofNy-U
Landscape Beginner                              V54kqpy1Q-Q
Modeling Inside Unreal                          9InU0xbX7l0
Blueprints ZERO to HERO                         W0brCeJNMqk
Create a Forest                                 90rv-0g7O_4
Beginner Environment Step by Step               d4MWM5HOAek
Car Racing Game                                 3P1A73Ghisw
5.2 Starter Course 2023                         LeY6tAP-qss
5.3 Castle Ruins                                2uf4fuSLQJ8
Crystal Mine environment                        YgWUSQBuPLA
RTS Game beginner                               CCO0-64cfe4
Materials from Scratch                          AEfMLaSB7is
First Game with Blueprints                      uyp1I4HJJBg
Castle Ruins environment                        oGOYSd0Ve-g
FPS Game                                        69HNJVS6818
Snow Level                                      HK3IYKYfRRg
Materials Complete Guide                        TSPbHLHmDJg
Animation Blueprint                             _oSQq7pKJtk
5.3 Complete Beginner Course                    td0rVkL1LVE
Foot IK Tutorial                                lfU3p80EjQE
Vertex Paint                                    rn21tf4mcWo
Niagara VFX 5.3                                 LOgH5DONzqQ
Jump Mechanics                                  bE9n1sBWtM4
Chaos Destruction                               JbuuEmMCKdQ
Procedural Content Generation (PCG)             ewhnpkIsHLM
Create Levels FASTER                            GQFjS8L7tfg
God Rays with Sequencer                         7HbXwRWKdMY
Niagara Fluids                                  kGG4xTTbF_I
Blueprint Communication                         QC8sTf7bklg
Snow Storm VFX Niagara                          ZOJ_AHlldfw
Cinematics Sequencer Tutorial                   2hTjyAppDNM
Nanite for Games                                DmnAI01boww
First Game in UE5                               gzPrN3tI250
PCG Forest                                      8c1t4Pok_E8
Weapon Glow VFX Niagara                         wkYkPIfg7Nw
Retarget Animations                             ljO5_yeF5kA
Japanese Shrine environment                     Qck4REJNySw
```

Cada uno se puede ingerir individualmente con `python scripts/learn.py "https://youtu.be/<ID>" --topic "..."` para sacar un .md más profundo si se necesita.
