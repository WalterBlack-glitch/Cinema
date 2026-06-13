#!/usr/bin/env python3
"""Brief cinemático → script Python para Unreal Engine 5 (Sequencer + CineCamera).

Emite un .py que se ejecuta dentro del editor de UE5 (consola Python, o
File → Execute Python Script). Requiere plugins: 'Python Editor Script Plugin'
y 'Sequencer Scripting' habilitados.

Crea:
  - LevelSequence con sección por shot
  - CineCameraActor por shot con focal length, aperture, focus distance
  - PostProcessVolume con auto-exposure manual + bloom + film grain
  - Lumen activado (UE5 default)
  - Tracks de transform animados por shot (dolly/pan/orbit)

Uso:
  python apply/ue5.py brief.md --out shot_ue5.py
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from apply._brief import parse, seconds, mm  # noqa: E402


TEMPLATE = '''# Auto-generado por higgsfield-cinematography / apply/ue5.py
# Ejecutar dentro del editor UE5 (Python plugin activo).
import unreal

FPS = {fps}
W, H = {w}, {h}
SEQ_PATH = "/Game/Cinematics/AutoSequence"

eu = unreal.EditorAssetLibrary
els = unreal.EditorLevelLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()

# Crea LevelSequence
if eu.does_asset_exist(SEQ_PATH):
    eu.delete_asset(SEQ_PATH)
seq = tools.create_asset("AutoSequence", "/Game/Cinematics",
                         unreal.LevelSequence, unreal.LevelSequenceFactoryNew())
seq.set_display_rate(unreal.FrameRate(numerator=FPS, denominator=1))

frame = 0
shots = []
{shots_block}

# PostProcessVolume global
ppv = els.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(0,0,0))
ppv.set_actor_label("AutoPPV")
ppv.set_editor_property("unbound", True)
ppv.settings.set_editor_property("bloom_intensity", 0.8)
ppv.settings.set_editor_property("film_grain_intensity", 0.15)
ppv.settings.set_editor_property("auto_exposure_method",
    unreal.AutoExposureMethod.AEM_MANUAL)
ppv.settings.set_editor_property("auto_exposure_bias", 1.0)

print(f"Listo: secuencia {{SEQ_PATH}} con {{len(shots)}} shots @ {{FPS}}fps")
'''


def shot_block(i, s, fps):
    lens = mm(s.get("lens"), 35)
    dur_s = seconds(s.get("duration"), fps)
    nf = max(1, int(dur_s * fps))
    move = (s.get("camera_move") or "static").lower()
    aperture = float((s.get("aperture") or "f/2.8").split("/")[-1]) if "/" in (s.get("aperture") or "") else 2.8

    if "dolly-in" in move:
        start, end = "(0,-500,160)", "(0,-150,160)"
    elif "dolly-out" in move:
        start, end = "(0,-150,160)", "(0,-500,160)"
    elif "pan-left" in move:
        start, end = "(0,-400,160)", "(-300,-400,160)"
    elif "pan-right" in move:
        start, end = "(0,-400,160)", "(300,-400,160)"
    elif "crane-up" in move:
        start, end = "(0,-400,100)", "(0,-400,350)"
    elif "orbit" in move:
        start, end = "(300,-300,160)", "(-300,-300,160)"
    else:
        start = end = "(0,-400,160)"

    return f'''
# --- shot {i}: {s.get("name","")} ---
cam = els.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector{start})
cam.set_actor_label("Cam{i}")
cs = cam.get_cine_camera_component()
cs.set_current_focal_length({lens}.0)
cs.set_current_aperture({aperture})
cs.focus_settings.manual_focus_distance = 400.0

binding = seq.add_possessable(cam)
tr_track = binding.add_track(unreal.MovieScene3DTransformTrack)
section = tr_track.add_section()
section.set_range(frame, frame + {nf})
# keyframes inicio/fin
for ch_i, val_s, val_e in [(0, {start}[0], {end}[0]), (1, {start}[1], {end}[1]), (2, {start}[2], {end}[2])]:
    ch = section.get_channels()[ch_i]
    ch.add_key(unreal.FrameNumber(frame), val_s, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)
    ch.add_key(unreal.FrameNumber(frame + {nf}), val_e, interpolation=unreal.MovieSceneKeyInterpolation.LINEAR)

# Cámara cut
cam_track = seq.add_master_track(unreal.MovieSceneCameraCutTrack)
cut = cam_track.add_section()
cut.set_camera_binding_id(seq.make_binding_id(binding))
cut.set_range(frame, frame + {nf})

frame += {nf}
shots.append("Cam{i}")
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--out", default="shot_ue5.py")
    a = ap.parse_args()
    b = parse(a.brief)
    fps = int(b["meta"].get("fps", 24))
    res = b["meta"].get("resolution", "1920, 1080")
    w, h = [int(x.strip()) for x in res.split(",")[:2]] if "," in res else (1920, 1080)
    shots = "\n".join(shot_block(i + 1, s, fps) for i, s in enumerate(b["shots"]))
    Path(a.out).write_text(TEMPLATE.format(fps=fps, w=w, h=h,
                                           shots_block=shots or "# (sin shots)"),
                          encoding="utf-8")
    print(f"Generado: {a.out}")
    print("Ejecuta en UE5: File → Execute Python Script… → selecciona este .py")


if __name__ == "__main__":
    main()
