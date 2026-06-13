#!/usr/bin/env python3
"""Cine Studio — interactive terminal UI for the cinematography skill.

A menu-driven front end so you can drive generation from cmd/PowerShell/any terminal
without remembering flags. Wraps generate.py + the higgsfield CLI.

Run:  python studio.py        (or double-click studio.bat on Windows)

No external deps — pure stdlib. Shows live credit balance and per-shot cost,
confirms before spending, and saves prompts you build to studio_prompts.txt.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAVE_DIR = Path.home() / "Videos" / "Higgsfield"
ASPECTS = ["16:9", "9:16", "21:9", "1:1", "4:3", "3:4"]
VIDEO_MODELS = ["kling3_0", "seedance_2_0", "cinema_studio_video_3_0"]
STILL_MODELS = ["gpt_image_2", "soul_cinematic", "text2image_soul_v2"]


def c(txt, code):
    return f"\033[{code}m{txt}\033[0m" if sys.stdout.isatty() else txt


def have_higgsfield():
    return shutil.which("higgsfield") is not None


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def generate_and_save(cmd):
    """Run a higgsfield generate command, echo it, and download results to SAVE_DIR."""
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout + r.stderr
    print(out)
    if r.returncode == 0:
        _save_inline(out)
    return r.returncode


def _save_inline(text):
    import datetime
    import urllib.request
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    urls = re.findall(r"https?://[^\s\"'<>]+\.(?:mp4|mov|webm|mkv|png|jpg|jpeg|webp)(?:\?[^\s\"'<>]*)?", text)
    for u in dict.fromkeys(urls):
        ext = re.search(r"\.(\w+)(?:\?|$)", u).group(1).lower()
        out = SAVE_DIR / f"{datetime.datetime.now():%Y%m%d_%H%M%S}.{ext}"
        try:
            urllib.request.urlretrieve(u, out)
            print(c(f"saved {out}", "32"))
        except Exception as e:
            print(c(f"failed to save {u}: {e}", "31"))
    if not urls:
        print(c(f"(no media URL to save in {SAVE_DIR})", "33"))


def balance():
    if not have_higgsfield():
        return "(higgsfield CLI not installed)"
    r = run(["higgsfield", "account", "status"])
    m = re.search(r"(\d+)\s*credits", r.stdout + r.stderr)
    return f"{m.group(1)} credits" if m else (r.stdout.strip() or "unknown")


def ask(prompt, default=None, choices=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        val = input(c(f"{prompt}{suffix}: ", "36")).strip()
        if not val and default is not None:
            return default
        if choices and val not in choices:
            print(c(f"  pick one of: {', '.join(choices)}", "33"))
            continue
        if val:
            return val


def menu(title, items):
    print(c(f"\n{title}", "1;35"))
    for i, it in enumerate(items, 1):
        print(f"  {c(i, '32')}) {it}")
    while True:
        s = input(c("> ", "36")).strip()
        if s.isdigit() and 1 <= int(s) <= len(items):
            return int(s) - 1


def pick_list(label, options):
    idx = menu(label, options)
    return options[idx]


def cost_for(model, prompt, duration, aspect):
    if not have_higgsfield():
        return None
    cmd = ["higgsfield", "generate", "cost", model, "--prompt", prompt, "--aspect_ratio", aspect]
    if duration:
        cmd += ["--duration", str(duration)]
    r = run(cmd)
    m = re.search(r"([\d.]+)\s*credits", r.stdout + r.stderr)
    return m.group(1) if m else (r.stdout.strip() + r.stderr.strip())[:120]


def build_prompt():
    print(c("\nBuild the shot prompt (Enter to skip a part):", "1;35"))
    parts = []
    for label in ["subject + key detail", "action", "setting + FG/BG depth",
                  "lens + focal + depth of field", "light direction + quality + time",
                  "color palette + grade + contrast", "film stock / grain", "mood word"]:
        v = input(c(f"  {label}: ", "36")).strip()
        if v:
            parts.append(v)
    move = input(c("  ONE camera move (e.g. slow dolly push-in): ", "36")).strip()
    prompt = ", ".join(parts)
    if move:
        prompt += f" — {move}"
    return prompt


def cloud_video():
    model = pick_list("Video model", VIDEO_MODELS)
    raw = input(c("\nPaste a full prompt, or leave empty to build one: ", "36")).strip()
    prompt = raw or build_prompt()
    aspect = pick_list("Aspect ratio", ASPECTS)
    duration = ask("Duration (s, min 4)", "4")
    print(c(f"\nPrompt:\n  {prompt}", "37"))
    cost = cost_for(model, prompt, duration, aspect)
    print(c(f"\nCost: {cost} credits   |   Balance: {balance()}", "1;33"))
    if ask("Generate? (y/n)", "n").lower() != "y":
        print("Cancelled."); return
    cmd = ["higgsfield", "generate", "create", model, "--prompt", prompt,
           "--duration", str(duration), "--aspect_ratio", aspect, "--wait"]
    img = input(c("Optional --start-image path (Enter for none): ", "36")).strip()
    if img:
        cmd += ["--start-image", img]
    print(c("\nRunning...\n", "32"))
    subprocess.run(cmd)


def local_still():
    raw = input(c("\nPaste a full prompt, or leave empty to build one: ", "36")).strip()
    prompt = raw or build_prompt()
    aspect = pick_list("Aspect ratio", ASPECTS)
    out = ask("Output file", "still.png")
    img = input(c("Optional source image for img2img (Enter for txt2img): ", "36")).strip()
    cmd = [sys.executable, str(HERE / "generate.py"), "--engine", "comfyui",
           "--prompt", prompt, "--aspect", aspect, "--out", out]
    if img:
        cmd += ["--image", img]
    print(c("\nRunning on local ComfyUI (free)...\n", "32"))
    subprocess.run(cmd)


def cloud_still():
    model = pick_list("Still model", STILL_MODELS)
    raw = input(c("\nPaste a full prompt, or leave empty to build one: ", "36")).strip()
    prompt = raw or build_prompt()
    aspect = pick_list("Aspect ratio", ASPECTS)
    cost = cost_for(model, prompt, None, aspect)
    print(c(f"\nCost: {cost} credits   |   Balance: {balance()}", "1;33"))
    if ask("Generate? (y/n)", "n").lower() != "y":
        print("Cancelled."); return
    subprocess.run(["higgsfield", "generate", "create", model, "--prompt", prompt,
                    "--aspect_ratio", aspect, "--wait"])


def main():
    if os.name == "nt":
        os.system("")  # enable ANSI on Windows terminals
    print(c("\n  CINE STUDIO — higgsfield-cinematography", "1;35"))
    print(c("  cloud video/stills + free local stills (ComfyUI)\n", "90"))
    while True:
        print(c(f"  Balance: {balance()}", "1;33"))
        choice = menu("What do you want to do?", [
            "Cloud VIDEO shot (Higgsfield, costs credits)",
            "Local STILL — free (ComfyUI / SDXL)",
            "Cloud STILL (Higgsfield, costs credits)",
            "Show credit balance",
            "Quit",
        ])
        try:
            if choice == 0:
                cloud_video()
            elif choice == 1:
                local_still()
            elif choice == 2:
                cloud_still()
            elif choice == 3:
                print(c(f"\n  {balance()}\n", "1;33"))
            else:
                print("Bye."); return
        except KeyboardInterrupt:
            print("\n(cancelled)\n")
        except Exception as e:
            print(c(f"  error: {e}", "31"))


if __name__ == "__main__":
    main()
