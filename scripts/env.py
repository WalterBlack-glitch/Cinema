#!/usr/bin/env python3
"""Detecta qué DCC está abierto y enruta el brief al adapter correcto.

Detección:
  - Blender: proceso blender.exe / puerto 9876 (addon bpy-socket si lo tienes)
  - UE5: UnrealEditor.exe / puerto 6766 (Remote Control HTTP por defecto)
  - Godot: godot.exe / puerto 6007 (--remote-debug)

Uso:
  python env.py detect
  python env.py apply brief.md          # autodetecta y genera + sugiere ejecutar
  python env.py apply brief.md --to blender|ue5|godot
"""
import argparse
import socket
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def port_open(p):
    try:
        s = socket.create_connection(("127.0.0.1", p), timeout=0.3)
        s.close(); return True
    except Exception:
        return False


def processes():
    if sys.platform == "win32":
        r = subprocess.run(["tasklist"], capture_output=True, text=True,
                           creationflags=0x08000000)
        return r.stdout.lower()
    r = subprocess.run(["ps", "-A"], capture_output=True, text=True)
    return r.stdout.lower()


def detect():
    procs = processes()
    out = []
    if "blender" in procs or port_open(9876):
        out.append("blender")
    if "unrealeditor" in procs or port_open(6766):
        out.append("ue5")
    if "godot" in procs or port_open(6007):
        out.append("godot")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["detect", "apply"])
    ap.add_argument("brief", nargs="?")
    ap.add_argument("--to", choices=["blender", "ue5", "godot"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if a.cmd == "detect":
        d = detect()
        print("DCC activos:", ", ".join(d) if d else "(ninguno)")
        return

    target = a.to or (detect() or ["blender"])[0]
    out = a.out or {"blender": "shot_blender.py", "ue5": "shot_ue5.py",
                    "godot": "cinematic_scene"}[target]
    script = HERE / "apply" / f"{target}.py"
    cmd = [sys.executable, str(script), a.brief, "--out", out]
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=False)
    hints = {
        "blender": f"  Ejecuta: blender -P {out}   (o `blender -b escena.blend -P {out}` headless)",
        "ue5":     f"  Ejecuta dentro del editor UE5: File → Execute Python Script → {out}",
        "godot":   f"  Importa {out}.tscn en Godot 4 y adjunta {out}.gd al AnimationPlayer."
    }
    print(hints[target])


if __name__ == "__main__":
    main()
