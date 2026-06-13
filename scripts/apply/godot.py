#!/usr/bin/env python3
"""Brief cinemático → escena Godot 4 (.tscn) + GDScript de animación.

Emite dos archivos:
  - <out>.tscn: nodo raíz Node3D con Camera3D por shot, DirectionalLight3D key,
    OmniLight3D fill+rim, WorldEnvironment con SSR + GI + Tonemap ACES.
  - <out>.gd: script en AnimationPlayer con keyframes de cámara por shot.

Cárgalo en Godot 4 (project → import → escena), reproduce con AnimationPlayer.

Uso:
  python apply/godot.py brief.md --out cinematic_scene
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apply._brief import parse, seconds, mm  # noqa: E402

MOVES = {
    "dolly-in":  ((0, 1.6, -5),  (0, 1.6, -1.5)),
    "dolly-out": ((0, 1.6, -1.5),(0, 1.6, -5)),
    "pan-left":  ((0, 1.6, -4),  (-3, 1.6, -4)),
    "pan-right": ((0, 1.6, -4),  (3, 1.6, -4)),
    "crane-up":  ((0, 1.0, -4),  (0, 3.5, -4)),
    "orbit":     ((3, 1.6, -3),  (-3, 1.6, -3)),
}


def move_for(s):
    m = (s.get("camera_move") or "").lower()
    for k, v in MOVES.items():
        if k in m:
            return v
    return ((0, 1.6, -4), (0, 1.6, -4))


TSCN_HEAD = '''[gd_scene load_steps=4 format=3]

[sub_resource type="Environment" id="Env_1"]
background_mode = 1
background_color = Color(0.02, 0.02, 0.03, 1)
ambient_light_source = 2
ambient_light_color = Color(0.1, 0.12, 0.18, 1)
tonemap_mode = 3
glow_enabled = true
ssr_enabled = true
sdfgi_enabled = true

[node name="Cinematic" type="Node3D"]

[node name="WorldEnvironment" type="WorldEnvironment" parent="."]
environment = SubResource("Env_1")

[node name="Key" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.7, 0, 0.7, -0.5, 0.7, 0.5, -0.5, -0.7, 0.5, 4, 5, -2)
light_color = Color(1.0, 0.92, 0.85, 1)
light_energy = 2.0
shadow_enabled = true

[node name="Fill" type="OmniLight3D" parent="."]
transform = Transform3D(1,0,0,0,1,0,0,0,1, -4, 3, -3)
light_color = Color(0.85, 0.92, 1, 1)
light_energy = 0.6
omni_range = 12

[node name="Rim" type="OmniLight3D" parent="."]
transform = Transform3D(1,0,0,0,1,0,0,0,1, 0, 3.5, 3)
light_color = Color(0.2, 0.6, 1.0, 1)
light_energy = 1.4
omni_range = 10

[node name="AnimationPlayer" type="AnimationPlayer" parent="."]
'''


def cam_node(i, lens, start):
    return f'''
[node name="Cam{i}" type="Camera3D" parent="."]
transform = Transform3D(1,0,0,0,1,0,0,0,1, {start[0]}, {start[1]}, {start[2]})
fov = {2*57.2958*0.5*0.0245/(lens/1000):.2f}
current = false
'''


GD_HEAD = '''extends AnimationPlayer
# Auto-generado: anima cámaras por shot. Llama play("cinematic") en _ready.

func _ready():
    var lib = AnimationLibrary.new()
    var anim = Animation.new()
    anim.length = {total}
'''

GD_TAIL = '''    lib.add_animation("cinematic", anim)
    add_animation_library("auto", lib)
    play("auto/cinematic")
'''


def gd_track(i, t0, t1, start, end):
    return f'''
    var t_{i} = anim.add_track(Animation.TYPE_VALUE)
    anim.track_set_path(t_{i}, NodePath("../Cam{i}:position"))
    anim.track_insert_key(t_{i}, {t0}, Vector3{start})
    anim.track_insert_key(t_{i}, {t1}, Vector3{end})
    # activar cámara
    var tc_{i} = anim.add_track(Animation.TYPE_VALUE)
    anim.track_set_path(tc_{i}, NodePath("../Cam{i}:current"))
    anim.track_insert_key(tc_{i}, {t0}, true)
    anim.track_insert_key(tc_{i}, {t1}, false)
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--out", default="cinematic_scene")
    a = ap.parse_args()
    b = parse(a.brief)
    fps = int(b["meta"].get("fps", 24))

    tscn = TSCN_HEAD
    gd_tracks = ""
    t = 0.0
    for i, s in enumerate(b["shots"], 1):
        lens = mm(s.get("lens"), 35)
        dur = seconds(s.get("duration"), fps)
        start, end = move_for(s)
        tscn += cam_node(i, lens, start)
        gd_tracks += gd_track(i, t, t + dur, start, end)
        t += dur

    base = Path(a.out)
    (base.with_suffix(".tscn")).write_text(tscn, encoding="utf-8")
    gd = GD_HEAD.format(total=max(1.0, t)) + gd_tracks + GD_TAIL
    (base.with_suffix(".gd")).write_text(gd, encoding="utf-8")
    print(f"Generado: {base}.tscn  +  {base}.gd")
    print("Carga el .tscn en Godot 4 y adjunta el .gd al AnimationPlayer.")


if __name__ == "__main__":
    main()
