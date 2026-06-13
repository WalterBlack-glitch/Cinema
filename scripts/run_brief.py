#!/usr/bin/env python3
"""Execute the `higgsfield generate create` commands found in a shot brief.

Parses fenced ```bash blocks in a brief .md (the Phase-4 deliverable), joins
backslash line-continuations, and runs each command sequentially. A per-shot
failure is logged and the batch continues. Appends every result to
generation_log.md next to the brief (shot, command, status, output tail) so
Phase 6 iteration has a record.

Usage:
  python run_brief.py brief.md                 # run everything
  python run_brief.py brief.md --dry-run       # list the commands, run nothing
  python run_brief.py brief.md --only 1,3      # run shots 1 and 3 (1-based)
"""
import argparse
import datetime
import re
import shlex
import subprocess
import sys
from pathlib import Path


def extract_commands(text):
    cmds = []
    for block in re.findall(r"```(?:bash|sh)?\n(.*?)```", text, re.DOTALL):
        joined = re.sub(r"\\\s*\n\s*", " ", block).strip()
        for line in joined.splitlines():
            line = line.strip()
            if line.startswith("higgsfield generate create"):
                cmds.append(line)
    return cmds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="comma-separated 1-based shot numbers")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per shot")
    args = ap.parse_args()

    brief = Path(args.brief)
    cmds = extract_commands(brief.read_text(encoding="utf-8"))
    if not cmds:
        print("ERROR: no `higgsfield generate create` commands found in the brief.",
              file=sys.stderr)
        sys.exit(1)

    picked = set(range(1, len(cmds) + 1))
    if args.only:
        picked = {int(n) for n in args.only.split(",")}

    if args.dry_run:
        for i, c in enumerate(cmds, 1):
            mark = "*" if i in picked else " "
            print(f"[{mark}] shot {i}: {c[:160]}{'...' if len(c) > 160 else ''}")
        return

    log = brief.parent / "generation_log.md"
    ok = fail = 0
    with log.open("a", encoding="utf-8") as lf:
        lf.write(f"\n## Run {datetime.datetime.now():%Y-%m-%d %H:%M} — {brief.name}\n")
        for i, c in enumerate(cmds, 1):
            if i not in picked:
                continue
            print(f"--- shot {i}/{len(cmds)} ---")
            try:
                r = subprocess.run(shlex.split(c), capture_output=True, text=True,
                                   timeout=args.timeout)
                out = (r.stdout + r.stderr).strip()
                status = "OK" if r.returncode == 0 else f"FAIL (exit {r.returncode})"
            except FileNotFoundError:
                print("ERROR: `higgsfield` CLI not on PATH. Install/auth it first "
                      "(see references/higgsfield.md).", file=sys.stderr)
                sys.exit(2)
            except subprocess.TimeoutExpired:
                out, status = f"timed out after {args.timeout}s", "FAIL (timeout)"
            tail = out[-1500:]
            print(f"shot {i}: {status}\n{tail}\n")
            lf.write(f"\n### Shot {i} — {status}\n```\n{c}\n```\n```\n{tail}\n```\n")
            ok += status == "OK"
            fail += status != "OK"
    print(f"Done: {ok} ok, {fail} failed. Log: {log}")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
