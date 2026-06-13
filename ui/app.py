#!/usr/bin/env python3
"""Cine Studio — native desktop app.

Opens the Studio as a real desktop window (pywebview / WebView2), not a browser
tab. The modern HTML UI is served by the embedded local API server and rendered
inside the native window.

Run:  pythonw app.py   (or double-click the desktop shortcut)

If pywebview isn't available it falls back to opening the browser so the app still
works.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import server  # noqa: E402


def main():
    if sys.platform == "win32":
        try:  # taskbar agrupa la ventana bajo su propia identidad/ícono
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CineStudio.App")
        except Exception:
            pass
    srv, port = server.start_background()
    url = f"http://127.0.0.1:{port}"
    try:
        import webview
    except ImportError:
        import webbrowser
        print(f"pywebview no instalado; abriendo {url} en el navegador.")
        webbrowser.open(url)
        import threading
        threading.Event().wait()
        return
    webview.create_window("Cine Studio", url, width=1320, height=860,
                          min_size=(960, 640), background_color="#0b0d12")
    webview.start()
    srv.shutdown()


if __name__ == "__main__":
    main()
