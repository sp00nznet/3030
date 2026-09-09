#!/usr/bin/env python3
"""VIRUS v3030.1 -- Deltron 3030's "Virus", implemented literally.

Does nothing to your computer. Loudly. See SPEC.md.

    python virus.py            the full bit
    python virus.py --fast     no sleeps, watch it in 2 seconds
    python virus.py --mute     no bassline
    python virus.py --check    self-check, asserts all four acts ran
"""
import io
import os
import sys
import threading
import time
from contextlib import redirect_stdout

import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, size, type_out, w

# _MEIPASS: PyInstaller onefile unpacks lyrics.txt there. See .github/workflows/build.yml
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
MUTE = "--mute" in sys.argv

GREEN = ESC + "38;5;46m"
DIM = ESC + "38;5;28m"
REED = ESC + "48;5;180m" + ESC + "38;5;94m"  # tan ground, brown ink


def lyrics():
    """The verse. '#' lines are notes to whoever edits the file, not lyrics --
    act 4 scrolls this onto the papyrus, so they must not end up on it."""
    with open(os.path.join(HERE, "lyrics.txt"), encoding="utf-8") as f:
        return [ln.rstrip() for ln in f if not ln.lstrip().startswith("#")]


# --- audio -----------------------------------------------------------------
# ponytail: winsound.Beep is the whole sound engine. Sounds like a 1997
# shareware installer, which is the joke. Upgrade path is a .mid via
# struct.pack, but then it needs a player -- see SPEC.md non-goals.
RIFF = [(98, 200), (98, 200), (117, 160), (98, 200),
        (73, 260), (0, 120), (87, 200), (98, 320)]


def beat(stop):
    try:
        import winsound
    except ImportError:
        return  # not Windows: silent, everything else still runs
    while not stop.is_set():
        for freq, ms in RIFF:
            if stop.is_set():
                return
            if freq:
                winsound.Beep(freq, ms)
            else:
                time.sleep(ms / 1000)


# --- act 1: boot -----------------------------------------------------------
BANNER = r"""
  +--------------------------------------------------------+
  |  DELTRON 3030  //  VIRUS v3030.1                       |
  |  AUTOMATOR ON THE BOARDS                               |
  |  it is 3030. this program does nothing. loudly.        |
  +--------------------------------------------------------+
"""


def act_boot():
    w(CLEAR + HIDE + GREEN)
    for line in BANNER.splitlines():
        w(line + "\n")
        nap(0.06)
    nap(0.4)
    type_out("  POST .................. OK", 60)
    type_out("  PAYLOAD ............... v3030.1", 60)
    # the only syscall in this program that touches your machine
    n = len(os.listdir(HERE))
    type_out(f"  TARGETS ACQUIRED ...... {n} file(s)", 60)
    nap(0.6)


# --- act 2: noise ----------------------------------------------------------
# Everything in the verse that isn't a mechanism, failing deadpan.
NOISE = [
    ("SKIP", "whitehouse.gov", "air-gapped"),
    ("NOOP", "politicians", "already corrupt"),
    ("FAIL", "space-station-01", "timeout (400ms RTT)"),
    ("DUPE", "whiteout.exe", "see: del (1981)"),
    ("HELD", "microsoft", "cannot uninstall a corporation"),
    ("WARN", "papyrus.sys", "closest match: paperweight"),
    ("TODO", "forward-compat", "1000 years (millennium LTS)"),
]


def act_noise():
    w("\n")
    for tag, target, why in NOISE:
        dots = "." * max(3, 26 - len(target))
        w(f"  {DIM}[{tag}]{GREEN} {target} {dots} {why}\n")
        nap(0.35)
    nap(0.8)


# --- act 3: bomb -----------------------------------------------------------
# The one line in the verse that describes a real mechanism: replication.
# Rendered, not executed. Nothing is created. See SPEC.md safety rails.
BOMB_N = 2047


def act_bomb():
    cols, _ = size()
    room = max(12, cols - 24)
    w("\n")
    type_out("  REPLICATING ...", 50)
    for i in range(1, BOMB_N + 1):
        path = "./" + "scrolls/" * i
        if len(path) > room:
            path = f"./scrolls/x{i}/"  # collapsed: it outgrew the terminal
        w(f"  SPAWNING  {path:<{room}} [{i:>5}]\n")
        nap(max(0.001, 0.20 * (0.90 ** i)))  # accelerates into a blur
    type_out("  DISK: 100% PAPYRUS", 50)
    nap(0.8)


# --- act 4: papyrus --------------------------------------------------------
def act_papyrus():
    cols, rows = size()
    reed = REED + "~" * cols + RESET
    for r in range(rows, 0, -1):  # fills bottom-up
        w(f"{ESC}{r};1H{reed}")
        nap(0.04)
    nap(0.8)
    w(ESC + "H")
    for line in lyrics():
        # full-width tan so scrolled-in rows stay papyrus
        w(REED + f"  {line}".ljust(cols)[:cols] + RESET + "\n")
        nap(0.9 if line.strip() else 0.4)
    nap(1.0)


def main():
    stop = threading.Event()
    if not MUTE and not theater.FAST:
        threading.Thread(target=beat, args=(stop,), daemon=True).start()
    try:
        act_boot()
        act_noise()
        act_bomb()
        act_papyrus()
    finally:
        stop.set()
        w(RESET + SHOW + "\n")  # always give the terminal back


def demo():
    """One assert per act. Fails if any act stops producing its payload."""
    global MUTE
    MUTE = True
    theater.fast(True)
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    assert "v3030.1" in out, "act 1 (boot) did not run"
    assert all(f"[{t}]" in out for t, _, _ in NOISE), "act 2 (noise) dropped a line"
    assert f"[{BOMB_N:>5}]" in out, "act 3 (bomb) never reached the counter"
    assert "~" * 8 in out, "act 4 (papyrus) did not fill the screen"
    assert lyrics()[0] in out, "act 4 (papyrus) did not scroll the lyrics"
    assert not any(l.startswith("#") for l in lyrics()), "build notes on the scroll"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print("ok: 4 acts, terminal restored, 0 files harmed")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
