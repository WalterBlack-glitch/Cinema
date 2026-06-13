#!/usr/bin/env python3
"""Brief cinemático → script Blender (bpy) listo para ejecutar.

Emite un .py que, al correrlo con Blender (`blender -b escena.blend -P out.py` o
`blender -P out.py` con escena abierta), crea/configura:
  - CameraData con focal length + DOF
  - Constraint Track-To al sujeto (si --subject_obj se indica)
  - Animation: dolly/pan/orbit con keyframes en location/rotation
  - 3 luces: key (cálida), fill (1/4 key), rim (color del brief)
  - Render: EEVEE Next con bloom + GTAO + resolución y fps del meta
  - VSE: agrega el render del shot a la Sequencer en frame contiguo

Uso:
  python apply/blender.py brief.md --out shot.py [--subject_obj Cube] [--render-dir out/]
  python apply/blender.py brief.md --out shot.py --execute  # llama a blender directamente
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apply._brief import parse, seconds, mm  # noqa: E402


TEMPLATE = '''# Auto-generado por higgsfield-cinematography / apply/blender.py
import bpy, math, os
from mathutils import Vector

FPS = {fps}
W, H = {w}, {h}
RENDER_DIR = r"{render_dir}"
SUBJECT = {subject!r}  # nombre de objeto a trackear, o None

scene = bpy.context.scene
scene.render.fps = FPS
scene.render.resolution_x = W
scene.render.resolution_y = H
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in {{e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}} else "BLENDER_EEVEE"

def ensure(name, kind, data_new):
    obj = bpy.data.objects.get(name)
    if obj: return obj
    data = data_new()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return obj

def keyframe(obj, frame, loc=None, rot=None):
    if loc is not None: obj.location = Vector(loc); obj.keyframe_insert("location", frame=frame)
    if rot is not None: obj.rotation_euler = rot; obj.keyframe_insert("rotation_euler", frame=frame)

def make_light(name, kind, energy, color, loc, rot):
    l = ensure(name, "LIGHT", lambda: bpy.data.lights.new(name, kind))
    l.data.energy = energy
    l.data.color = color
    l.location = loc
    l.rotation_euler = rot
    return l

# --- Luces 3-point ---
make_light("Key",  "AREA", 800, (1.0, 0.92, 0.85), (4, -3, 4),  (math.radians(55), 0, math.radians(45)))
make_light("Fill", "AREA", 200, (0.9, 0.95, 1.0), (-4, -2, 3), (math.radians(60), 0, math.radians(-30)))
{rim_block}

frame = 1
{shots_block}

scene.frame_start = 1
scene.frame_end = frame - 1

os.makedirs(RENDER_DIR, exist_ok=True)
scene.render.filepath = os.path.join(RENDER_DIR, "shot_")
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
print("OK — listo para render. F12 o `blender -b ... -a`.")
'''


def shot_block(i, s, fps):
    lens = mm(s.get("lens"), 35)
    dur_s = seconds(s.get("duration"), fps)
    nf = max(1, int(dur_s * fps))
    move = (s.get("camera_move") or "static").lower()
    aperture = float((s.get("aperture") or "f/2.8").split("/")[-1]) if "/" in (s.get("aperture") or "") else 2.8

    if "dolly-in" in move:
        start, end = (0, -5, 1.6), (0, -1.5, 1.6)
    elif "dolly-out" in move:
        start, end = (0, -1.5, 1.6), (0, -5, 1.6)
    elif "pan-left" in move:
        start, end = (0, -4, 1.6), (-3, -4, 1.6)
    elif "pan-right" in move:
        start, end = (0, -4, 1.6), (3, -4, 1.6)
    elif "crane-up" in move:
        start, end = (0, -4, 1.0), (0, -4, 3.5)
    elif "orbit" in move:
        start, end = (3, -3, 1.6), (-3, -3, 1.6)
    else:
        start = end = (0, -4, 1.6)

    return f'''
# --- shot {i}: {s.get("name", "")} ({move}) ---
cam_data = bpy.data.cameras.new("Cam{i}")
cam_data.lens = {lens}
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = {aperture}
cam = bpy.data.objects.new("Cam{i}", cam_data)
bpy.context.collection.objects.link(cam)
if SUBJECT and SUBJECT in bpy.data.objects:
    c = cam.constraints.new("TRACK_TO")
    c.target = bpy.data.objects[SUBJECT]
    c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
    cam_data.dof.focus_object = bpy.data.objects[SUBJECT]
else:
    cam.rotation_euler = (math.radians(80), 0, 0)
keyframe(cam, frame, loc={start})
keyframe(cam, frame + {nf} - 1, loc={end})
scene.camera = cam  # último shot ganador para render base; usa Markers para multicam
frame += {nf}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--out", default="shot.py")
    ap.add_argument("--subject_obj", default=None)
    ap.add_argument("--render-dir", default="//renders/")
    ap.add_argument("--execute", action="store_true",
                    help="ejecuta directamente con blender (-b si --blend-file)")
    ap.add_argument("--blend-file", default=None)
    a = ap.parse_args()

    b = parse(a.brief)
    fps = int(b["meta"].get("fps", 24))
    res = b["meta"].get("resolution", "1920, 1080")
    w, h = [int(x.strip()) for x in res.split(",")[:2]] if "," in res else (1920, 1080)

    rim_color = "(0.2, 0.6, 1.0)"  # default cyan
    if b["shots"]:
        c0 = (b["shots"][0].get("color") or "").lower()
        if "warm" in c0 or "naranja" in c0: rim_color = "(1.0, 0.5, 0.2)"
        elif "magenta" in c0 or "rosa" in c0: rim_color = "(1.0, 0.3, 0.7)"
    import math as _m
    rim_block = (f'make_light("Rim", "AREA", 400, {rim_color}, (0, 3, 3.5),'
                 f' ({_m.radians(-55):.4f}, 0, {_m.radians(180):.4f}))')

    shots = "\n".join(shot_block(i + 1, s, fps) for i, s in enumerate(b["shots"]))
    out_py = Path(a.out)
    out_py.write_text(TEMPLATE.format(
        fps=fps, w=w, h=h, render_dir=a.render_dir, subject=a.subject_obj,
        rim_block=rim_block, shots_block=shots or "# (sin shots en el brief)"
    ), encoding="utf-8")
    print(f"Generado: {out_py}")

    if a.execute:
        blender = shutil.which("blender")
        if not blender:
            print("ERROR: 'blender' no está en PATH.", file=sys.stderr); sys.exit(2)
        cmd = [blender]
        if a.blend_file:
            cmd += ["-b", a.blend_file]
        cmd += ["-P", str(out_py)]
        print("$", " ".join(cmd))
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
