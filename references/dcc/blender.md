# Blender (bpy) — guía mínima para aplicar cinematografía

## Cámara
- `bpy.data.cameras.new(name)` → `data.lens` (focal mm), `data.sensor_width` (36mm default).
- DOF: `cam_data.dof.use_dof = True`, `aperture_fstop`, `focus_object` o `focus_distance`.
- Track-To: constraint TRACK_TO con `track_axis=TRACK_NEGATIVE_Z`, `up_axis=UP_Y`.

## Luz
- Tipos: POINT, SUN, SPOT, AREA. Para cine usa AREA (key/fill/rim).
- Energía: AREA 200-1000W para interior; SUN 3-5 para HDR.
- Color en escala 0-1 lineal (no sRGB).

## Render
- Engine: `BLENDER_EEVEE_NEXT` (4.2+) > `BLENDER_EEVEE` > `CYCLES`.
- GTAO, bloom, screen-space reflections en `scene.eevee.*`.
- FFmpeg H.264: `render.image_settings.file_format="FFMPEG"`, `ffmpeg.codec="H264"`.

## Animación
- `obj.keyframe_insert("location", frame=N)`, idem `rotation_euler`, `scale`.
- `scene.frame_start/end` definen el rango.

## Ejecución headless
- `blender -b scene.blend -P script.py -a` (renderiza animación).
- Sin .blend: `blender -P script.py` (escena vacía).

## Socket bridge (opcional)
- Addon "Blender MCP" o "blender-bpy-socket" abre puerto 9876 para comandos en vivo.
- Sin addon: regenera el .py y relanza `blender -P`.
