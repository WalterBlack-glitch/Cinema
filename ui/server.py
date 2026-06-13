#!/usr/bin/env python3
"""Cine Studio — local web UI backend (stdlib only, no pip installs).

Serves a modern single-page panel and exposes a small JSON API that drives the
cinematography skill: cloud stills (Higgsfield), free local stills (ComfyUI),
animate a still into a short (Ken Burns), live credit balance, and a gallery of
everything in ~/Videos/Higgsfield.

Run:  python server.py   (opens http://127.0.0.1:8777)
"""
import json
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
SAVE_DIR = Path.home() / "Videos" / "Higgsfield"
LOCAL_BASE = Path.home() / "CineStudioLocal"
COMFY_URL = "http://127.0.0.1:8188"
PORT = 8777
URL_RE = re.compile(r"https?://[^\s\"'<>]+\.(?:mp4|mov|webm|mkv|png|jpg|jpeg|webp)(?:\?[^\s\"'<>]*)?")
MEDIA_EXT = {".mp4", ".mov", ".webm", ".mkv", ".png", ".jpg", ".jpeg", ".webp"}


HF = shutil.which("higgsfield")


# En pythonw (sin consola) cada subproceso de consola abriría una ventana cmd:
# CREATE_NO_WINDOW la suprime.
NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def run(cmd, **kw):
    kw.setdefault("creationflags", NO_WINDOW)
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def hf(args, **kw):
    """Run the higgsfield CLI; on Windows it's a .cmd, so route through cmd.exe."""
    exe = HF or "higgsfield"
    pre = ["cmd", "/c"] if exe.lower().endswith((".cmd", ".bat")) else []
    return run(pre + [exe, *args], **kw)


def balance():
    if not HF:
        return "CLI no instalado"
    r = hf(["account", "status"])
    m = re.search(r"(\d+)\s*credits", r.stdout + r.stderr)
    return f"{m.group(1)} créditos" if m else "?"


def gallery():
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    items = [f for f in SAVE_DIR.iterdir() if f.suffix.lower() in MEDIA_EXT]
    items.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    out = []
    for f in items:
        st = f.stat()
        out.append({
            "name": f.name,
            "kind": "video" if f.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"} else "image",
            "size": st.st_size,
            "mtime": int(st.st_mtime),
        })
    return out


def save_urls(text):
    import datetime
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for u in dict.fromkeys(URL_RE.findall(text)):
        ext = re.search(r"\.(\w+)(?:\?|$)", u).group(1).lower()
        out = SAVE_DIR / f"{datetime.datetime.now():%Y%m%d_%H%M%S}.{ext}"
        try:
            urllib.request.urlretrieve(u, out); saved.append(out.name)
        except Exception:
            pass
    return saved


def cost(p):
    model = p.get("model", "gpt_image_2")
    args = ["generate", "cost", model, "--prompt", p["prompt"],
            "--aspect_ratio", p.get("aspect", "16:9")]
    if p.get("duration"):
        args += ["--duration", str(p["duration"])]
    r = hf(args)
    m = re.search(r"([\d.]+)\s*credits", r.stdout + r.stderr)
    return {"cost": m.group(1) if m else None,
            "raw": (r.stdout + r.stderr).strip()[:200]}


def generate(p):
    engine = p.get("engine", "higgsfield")
    if engine == "comfyui":
        out = f"local_{__import__('time').strftime('%H%M%S')}.png"
        cmd = [sys.executable, str(SCRIPTS / "generate.py"), "--engine", "comfyui",
               "--prompt", p["prompt"], "--aspect", p.get("aspect", "16:9"),
               "--out", str(SAVE_DIR / out)]
        r = run(cmd, timeout=600)
        ok = r.returncode == 0
        return {"ok": ok, "saved": [out] if ok else [], "log": (r.stdout + r.stderr)[-1500:]}
    model = p.get("model", "gpt_image_2")
    args = ["generate", "create", model, "--prompt", p["prompt"],
            "--aspect_ratio", p.get("aspect", "16:9"), "--wait"]
    if p.get("duration"):
        args += ["--duration", str(p["duration"])]
    if p.get("image"):
        args += ["--start-image", p["image"]]
    r = hf(args, timeout=1200)
    text = r.stdout + r.stderr
    saved = save_urls(text) if r.returncode == 0 else []
    return {"ok": r.returncode == 0 and bool(saved), "saved": saved, "log": text[-1500:]}


def comfy_up():
    try:
        urllib.request.urlopen(COMFY_URL + "/system_stats", timeout=1.5)
        return True
    except Exception:
        return False


def local_status(p=None):
    logline = ""
    lg = LOCAL_BASE / "install.log"
    if lg.exists():
        try:
            lines = [l for l in lg.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
            logline = lines[-1] if lines else ""
        except Exception:
            pass
    return {"installed": (LOCAL_BASE / "ready.json").exists(),
            "running": comfy_up(), "log": logline}


def local_start(p=None):
    ready = LOCAL_BASE / "ready.json"
    if comfy_up():
        return {"ok": True, "log": "ComfyUI ya está activo."}
    if not ready.exists():
        return {"ok": False, "log": "El motor local aún no está instalado."}
    info = json.loads(ready.read_text(encoding="utf-8-sig"))
    portable = Path(info.get("portable", ""))
    py = portable / "python_embeded" / "python.exe"
    main = portable / "ComfyUI" / "main.py"
    if not py.exists() or not main.exists():
        return {"ok": False, "log": "ComfyUI portable incompleto (python_embeded/main.py)."}
    # Arranca el python embebido SIN ventana de consola (nada de .bat con pause).
    flags = 0
    if sys.platform == "win32":
        flags = 0x08000000 | 0x00000008  # CREATE_NO_WINDOW | DETACHED_PROCESS
    logf = open(LOCAL_BASE / "comfy.log", "ab")
    subprocess.Popen([str(py), "-s", str(main), "--windows-standalone-build"],
                     cwd=str(portable), stdout=logf, stderr=logf,
                     stdin=subprocess.DEVNULL, creationflags=flags, close_fds=True)
    return {"ok": True, "log": "Arrancando ComfyUI en segundo plano… dale ~20-40 s."}


def local_install(p=None):
    ps1 = HERE / "install_local.ps1"
    subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                      "-WindowStyle", "Hidden", "-File", str(ps1)],
                     creationflags=NO_WINDOW)
    return {"ok": True, "log": "Instalación lanzada en segundo plano (~8GB)."}


def video_local(p):
    """Genera video local con LTX-Video (ComfyUI). Auto-descarga modelo 1ª vez."""
    if not comfy_up():
        return {"ok": False, "log": "ComfyUI no está activo. Arráncalo en modo local primero."}
    import time as _t
    stem = f"local_video_{_t.strftime('%H%M%S')}"
    out = SAVE_DIR / f"{stem}.mp4"
    cmd = [sys.executable, str(SCRIPTS / "generate_video_local.py"),
           "--prompt", p["prompt"],
           "--seconds", str(p.get("seconds", 4)),
           "--fps", str(p.get("fps", 24)),
           "--width", str(p.get("width", 768)),
           "--height", str(p.get("height", 512)),
           "--out", str(out)]
    if p.get("image"):
        cmd += ["--image", str(SAVE_DIR / p["image"])]
    r = run(cmd, timeout=1800)
    final = out if out.exists() else out.with_suffix(".webp")
    ok = r.returncode == 0 and final.exists()
    return {"ok": ok, "saved": [final.name] if ok else [],
            "log": (r.stdout + r.stderr)[-2000:]}


def animate(p):
    src = SAVE_DIR / p["file"]
    out = SAVE_DIR / (src.stem + "_short.mp4")
    cmd = [sys.executable, str(SCRIPTS / "still_to_short.py"), str(src),
           "-o", str(out), "--move", p.get("move", "push-in"),
           "--seconds", str(p.get("seconds", 6))]
    r = run(cmd, timeout=300)
    ok = r.returncode == 0 and out.exists()
    return {"ok": ok, "saved": [out.name] if ok else [], "log": (r.stdout + r.stderr)[-1500:]}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _serve_media(self, f):
        """Sirve imagen/video con soporte Range (necesario para <video> y seek)."""
        ct = {"mp4": "video/mp4", "webm": "video/webm", "mov": "video/quicktime",
              "mkv": "video/x-matroska", "png": "image/png", "jpg": "image/jpeg",
              "jpeg": "image/jpeg", "webp": "image/webp"}.get(
            f.suffix.lower().lstrip("."), "application/octet-stream")
        size = f.stat().st_size
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        status = 200
        if rng and rng.startswith("bytes="):
            try:
                a, b = rng[6:].split("-", 1)
                if a:
                    start = int(a)
                if b:
                    end = int(b)
                end = min(end, size - 1)
                if start > end:
                    raise ValueError
                status = 206
            except ValueError:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return
        length = end - start + 1
        self.send_response(status)
        self.send_header("Content-Type", ct)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            with f.open("rb") as fh:
                fh.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = fh.read(min(64 * 1024, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionAbortedError):
            pass  # cliente cerró la conexión (típico cuando saltas en el seek)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/state":
            return self._send(200, {"balance": balance(), "gallery": gallery()})
        if self.path == "/api/local_status":
            return self._send(200, local_status())
        if self.path.startswith("/media/"):
            f = SAVE_DIR / urllib.request.url2pathname(self.path[len("/media/"):])
            if f.exists() and f.parent == SAVE_DIR:
                return self._serve_media(f)
            return self._send(404, {"error": "not found"})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        p = json.loads(self.rfile.read(n) or b"{}")
        try:
            if self.path == "/api/cost":
                return self._send(200, cost(p))
            if self.path == "/api/generate":
                return self._send(200, generate(p))
            if self.path == "/api/animate":
                return self._send(200, animate(p))
            if self.path == "/api/video_local":
                return self._send(200, video_local(p))
            if self.path == "/api/local_start":
                return self._send(200, local_start(p))
            if self.path == "/api/local_install":
                return self._send(200, local_install(p))
        except Exception as e:
            return self._send(200, {"ok": False, "log": f"error: {e}"})
        return self._send(404, {"error": "not found"})


def start_background(port=PORT):
    """Start the API server on a daemon thread and return (srv, port).

    Tries the preferred port, then a few fallbacks if it's taken. Used by the
    native desktop app (app.py) so the UI doesn't need a browser tab.
    """
    last = None
    for p in [port, port + 1, port + 2, 0]:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", p), H)
            real = srv.server_address[1]
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            return srv, real
        except OSError as e:
            last = e
    raise last


def main():
    url = f"http://127.0.0.1:{PORT}"
    print(f"Cine Studio en {url}  (Ctrl+C para salir)")
    srv, _ = start_background()
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        while True:
            threading.Event().wait(3600)
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
