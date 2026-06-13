#!/usr/bin/env python3
"""Aprende de cualquier fuente y persiste el conocimiento como referencia citable.

Fuentes soportadas:
  - video local (.mp4/.mov/.mkv/.webm): pasa por analyze_video.py (ASL, palette, planos)
  - URL de YouTube/Vimeo: fetch_reference.py + analyze_video.py
  - URL http(s) de artículo: descarga texto y lo resume en bullets cinemáticos
  - archivo de texto local (.md/.txt/.pdf): lo lee y lo resume

Salida: references/learned/<slug>.md con sección 'Principios' (bullets accionables)
y 'Citas' (con timestamps o párrafos fuente). Estos .md son leídos por los adapters
DCC (apply/*.py) cuando se construye un brief.

Uso:
  python learn.py <fuente> --topic "iluminacion noir" [--slug noir-lighting]
"""
import argparse
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEARNED = HERE.parent / "references" / "learned"


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower()).strip()
    return re.sub(r"[\s_-]+", "-", s)[:60] or "topic"


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    # quita scripts/styles/tags
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", txt).strip()


def read_local_text(p):
    if p.suffix.lower() == ".pdf":
        try:
            import pypdf
            return "\n".join(page.extract_text() or "" for page in pypdf.PdfReader(str(p)).pages)
        except ImportError:
            print("Falta pypdf: pip install pypdf", file=sys.stderr); sys.exit(2)
    return p.read_text(encoding="utf-8", errors="ignore")


def analyze_video(path):
    r = subprocess.run([sys.executable, str(HERE / "analyze_video.py"), str(path)],
                       capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="ruta local, URL http(s), o YouTube")
    ap.add_argument("--topic", required=True, help="tema en lenguaje natural")
    ap.add_argument("--slug", help="nombre de archivo (auto si no se da)")
    a = ap.parse_args()

    slug = a.slug or slugify(a.topic)
    LEARNED.mkdir(parents=True, exist_ok=True)
    out = LEARNED / f"{slug}.md"

    s = a.source
    kind, body = "?", ""
    if re.match(r"^https?://", s):
        if "youtube.com" in s or "youtu.be" in s or "vimeo.com" in s:
            r = subprocess.run([sys.executable, str(HERE / "fetch_reference.py"),
                                s, "--out", str(HERE.parent / "refs")],
                               capture_output=True, text=True)
            path = next((ln for ln in r.stdout.splitlines() if Path(ln.strip()).exists()), None)
            if path:
                kind, body = "video", analyze_video(Path(path.strip()))
            else:
                print(r.stderr, file=sys.stderr); sys.exit(1)
        else:
            kind, body = "article", fetch_text(s)[:30000]
    else:
        p = Path(s)
        if not p.exists():
            print(f"No existe: {p}", file=sys.stderr); sys.exit(1)
        if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm", ".avi"}:
            kind, body = "video", analyze_video(p)
        else:
            kind, body = "text", read_local_text(p)[:30000]

    # Plantilla: Claude (al consumir esta skill) destila body→Principios. Acá guardamos crudo
    # + scaffold para que el modelo lo complete cuando se cite en un brief.
    md = f"""---
topic: {a.topic}
slug: {slug}
source: {s}
kind: {kind}
---

# {a.topic}

## Fuente
- {s}

## Crudo (para destilación)
```
{body[:8000]}
```

## Principios (rellenar al usar)
- [ ] {a.topic}: principio 1
- [ ] principio 2

## Aplicación en 3D
- **Cámara/lente**: ...
- **Luz**: ...
- **Color**: ...
- **Movimiento**: ...
"""
    out.write_text(md, encoding="utf-8")
    print(f"Aprendido → {out}")
    print(f"Cita en briefs como: [[learned/{slug}]]")


if __name__ == "__main__":
    main()
