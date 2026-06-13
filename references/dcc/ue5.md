# Unreal Engine 5 (Python) — guía mínima

## Prerrequisitos
- Habilita plugins: **Python Editor Script Plugin** y **Sequencer Scripting**.
- Ejecuta: File → Execute Python Script, o consola Output Log con `py> ...`.

## Cámara
- `unreal.CineCameraActor` spawneada con `EditorLevelLibrary.spawn_actor_from_class`.
- `get_cine_camera_component()` → `set_current_focal_length(mm)`, `set_current_aperture(f)`.
- Focus: `focus_settings.manual_focus_distance` (cm). Sensor: ALEXA Mini default.

## Sequencer
- `tools.create_asset("Name", "/Game/Cinematics", unreal.LevelSequence, unreal.LevelSequenceFactoryNew())`.
- `seq.add_possessable(actor)` → binding → `add_track(MovieScene3DTransformTrack)`.
- Cámara cuts: `seq.add_master_track(MovieSceneCameraCutTrack)`.

## Iluminación
- DirectionalLight (sol/key), SkyLight (ambient), PointLight/SpotLight/RectLight.
- Lumen activo por default en UE5 (Project Settings → Rendering → Global Illumination).

## Post FX
- `PostProcessVolume` con `unbound=True`. `settings.bloom_intensity`, `film_grain_intensity`,
  `auto_exposure_method=AutoExposureMethod.AEM_MANUAL`, `color_grading_*`.

## Render
- Movie Render Queue (preferido) → `unreal.MoviePipelineQueue` API.
- Quick: PIE + capture, o Sequencer → Render Movie.

## Remote Control HTTP
- Plugin "Remote Control API" → habilita servidor HTTP en puerto 6766.
- POST /remote/object/call con `{"objectPath":"...","functionName":"..."}`.
