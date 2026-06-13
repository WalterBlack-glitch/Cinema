# Godot 4 — guía mínima cinemática

## Cámara
- `Camera3D` con `fov` (grados), `near/far`, `current=true` para activar.
- Conversión focal mm → FOV: `fov = 2 * atan(sensor/2 / focal) * 180/PI`.
  Sensor 24.89mm (S35): `fov ≈ degrees(2*atan(12.45/lens_mm))`.

## Movimiento
- Cámara en `Path3D` + `PathFollow3D` para dollys curvos.
- O AnimationPlayer con tracks de `position`/`rotation` (Vector3 keyframes).

## Luces
- `DirectionalLight3D` (sol/key), `OmniLight3D` (point fill/rim), `SpotLight3D`.
- `light_color`, `light_energy`, `shadow_enabled=true`.

## Entorno
- `WorldEnvironment` con `Environment` resource: tonemap ACES (mode=3),
  `glow_enabled`, `ssr_enabled`, `sdfgi_enabled` (GI dinámica).

## Animación
- `AnimationPlayer` + `Animation` + `add_track(TYPE_VALUE)` + `track_set_path("Cam:position")`.
- `track_insert_key(idx, time, value)`. Activa con `play("nombre")`.

## Headless
- `godot --headless --script script.gd` para batch sin ventana.
- Render de video: usa `MovieMaker` (Godot 4.3+) con `--write-movie out.avi`.
