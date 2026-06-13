"""Parser de briefs cinemáticos a estructura común consumida por los adapters DCC.

Un brief .md tiene front-matter YAML + secciones de shots. Estructura mínima:

---
title: Mi escena
fps: 24
resolution: [1920, 1080]
---

## shot 1
- lens: 35mm
- aperture: f/2.0
- camera_move: dolly-in 2m
- duration: 4s
- lighting: key 45° izq, rim azul cyan
- subject: personaje en silla
- color: teal & orange
- refs: [[learned/noir-lighting]]

Devuelve dict: {meta:{...}, shots:[{n, lens, aperture, move, dur, lights, subject, color, refs}]}.
"""
import re
from pathlib import Path


def parse(md_path):
    text = Path(md_path).read_text(encoding="utf-8")
    meta, body = {}, text
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip("[]").strip()
        body = m.group(2)
    shots = []
    for block in re.split(r"\n##\s+", body):
        if not block.strip():
            continue
        head, *rest = block.splitlines()
        s = {"name": head.strip()}
        for line in rest:
            m2 = re.match(r"^\s*-\s*([\w-]+)\s*:\s*(.+)$", line)
            if m2:
                s[m2.group(1).strip()] = m2.group(2).strip()
        if any(k in s for k in ("lens", "camera_move", "subject", "duration")):
            shots.append(s)
    return {"meta": meta, "shots": shots}


def seconds(v, fps=24):
    if not v:
        return 4.0
    m = re.match(r"([\d.]+)\s*(s|sec|f|frame)?", str(v))
    if not m:
        return 4.0
    n = float(m.group(1))
    return n / fps if (m.group(2) or "s").startswith("f") else n


def mm(v, default=35):
    if not v:
        return default
    m = re.search(r"(\d+)", str(v))
    return int(m.group(1)) if m else default
