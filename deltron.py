#!/usr/bin/env python3
"""3030 -- the album, as command-line programs.

    python deltron.py                 the tracklist
    python deltron.py virus           play a track
    python deltron.py slipping --drift 4    flags pass straight through
    python deltron.py --check         every self-check in the repo

ponytail: runpy, not a plugin system. Each track is already a standalone
program with its own __main__ and its own flags; this hands it argv and gets
out of the way. Nothing here needs to know what a track does.
"""
import os
import runpy
import subprocess
import sys

# (module, track no., title, one line)
TRACKS = [
    ("y3k", 2, "3030", "a Y3K compliance checker. The only one that does something real"),
    ("things", 4, "Things You Can Do", "a capability list. Everything on it is unavailable"),
    ("contact", 5, "Positive Contact", "finds life, files the mineral rights, never replies"),
    ("news", 15, "The News", "the disclosure outgrows the story, then closes on itself"),
    ("memory", 20, "Memory Loss", "memory climbs, the description of the work erodes"),
    ("virus", 7, "Virus", "a threat that cannot be carried out"),
    ("newcoke", 9, "New Coke", "a rebrand that ends with two products instead of one"),
    ("madness", 12, "Madness", "ten thousand hostile inputs. None of them can fail"),
    ("battlesong", 18, "Battlesong", "two sorts, six rounds, real timings, settled in one"),
    ("mastermind", 10, "Mastermind", "a lock, ten tries. The one that keeps score"),
    ("slipping", 14, "Time Keeps On Slipping", "a clock that is correct for about a minute"),
    ("turbulence", 16, "Turbulence", "a route to the tower, degrading. It reaches nothing"),
    ("upgrade", 8, "Upgrade (A Brymar College Course)", "a promise kept to the letter, meaning nothing"),
]
CHECKS = [m for m, _, _, _ in TRACKS] + ["audio", "music"]

ESC = "\033["
DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
RESET = ESC + "0m"


def tracklist():
    print()
    print(f"  {WHITE}DELTRON 3030{RESET}  {DIM}// the album, as command-line programs{RESET}")
    print()
    for mod, no, title, blurb in sorted(TRACKS, key=lambda t: t[1]):  # album order
        print(f"  {DIM}{no:>2}.{RESET}  {WHITE}{mod:<12}{RESET}{title}")
        print(f"       {DIM}{blurb}{RESET}")
    print()
    print(f"  {DIM}python deltron.py <name> [flags]   --fast on any of them skips the sleeps{RESET}")
    print()


def check_all():
    """Run every self-check as its own process, so one crash does not hide the rest."""
    if getattr(sys, "frozen", False):
        print("  --check needs the source checkout; the binary has no .py files to run.")
        print("  Try: deltron virus --check")
        return 1
    here = os.path.dirname(os.path.abspath(__file__))
    failed = []
    for mod in CHECKS:
        r = subprocess.run([sys.executable, os.path.join(here, mod + ".py"), "--check"],
                           capture_output=True, text=True, cwd=here)
        line = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
        print(f"  {mod:<10} {line[0]}")
        if r.returncode:
            failed.append(mod)
    print()
    print(f"  {len(CHECKS) - len(failed)}/{len(CHECKS)} passed" + (f", failed: {failed}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        tracklist()
    elif args[0] == "--check":
        sys.exit(check_all())
    elif args[0] in dict((m, 1) for m, _, _, _ in TRACKS):
        sys.argv = [args[0] + ".py"] + args[1:]   # the track parses its own flags
        runpy.run_module(args[0], run_name="__main__")
    else:
        print(f"No such track: {args[0]}")
        tracklist()
        sys.exit(1)
