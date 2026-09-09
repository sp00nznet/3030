#!/usr/bin/env python3
"""Renders docs/demo.gif with termshot -- https://github.com/sp00nznet/termshot

    pip install pillow
    TERMSHOT=/path/to/termshot python docs/demo.py

ponytail: the real program takes 45 seconds and ends by repainting the whole
terminal. A recorder would produce a 4MB GIF of that. termshot fakes it at
~30KB, and the fake is the honest option for a program whose entire premise
is that it is faking things.
"""
import os
import sys

sys.path.insert(0, os.environ.get("TERMSHOT", "."))
from termshot import CYAN, DIM, FG, GREEN, RED, YELLOW, Term  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
REED = (196, 164, 110)   # papyrus
INK = (120, 92, 52)

# Windows has no DejaVu; Consolas is the same shape of font.
FONTS = {"win32": ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/consolab.ttf")}
reg, bold = FONTS.get(sys.platform, (None, None))
kw = {"reg": reg, "bold": bold} if reg and os.path.exists(reg) else {}

t = Term(title="virus — 3030", user="del@3030", cwd="~/virus", rows=23, **kw)

t.type("python virus.py")
t.reveal([
    [("  +----------------------------------------------+", GREEN, False)],
    [("  |  DELTRON 3030  //  VIRUS v3030.1             |", GREEN, True)],
    [("  |  it is 3030. this program does nothing.      |", GREEN, False)],
    [("  +----------------------------------------------+", GREEN, False)],
], 260)

t.reveal([
    None,
    [("  [SKIP] ", DIM, False), ("whitehouse.gov", FG, False), ("  ......  air-gapped", DIM, False)],
    [("  [NOOP] ", DIM, False), ("politicians", FG, False), ("     ......  already corrupt", DIM, False)],
    [("  [FAIL] ", RED, True), ("space-station-01", FG, False), ("  ...  timeout (400ms RTT)", DIM, False)],
    [("  [DUPE] ", DIM, False), ("whiteout.exe", FG, False), ("    ......  see: del (1981)", DIM, False)],
    [("  [HELD] ", YELLOW, True), ("microsoft", FG, False), ("       ......  cannot uninstall a corporation", DIM, False)],
], 300)

t.blank(200)
t.reveal([
    [("  SPAWNING  ./scrolls/scrolls/scrolls/       [    3 ]", CYAN, False)],
    [("  SPAWNING  ./scrolls/scrolls/scrolls/scr…   [    4 ]", CYAN, False)],
    [("  SPAWNING  ./scrolls/x412/                  [  412 ]", CYAN, False)],
    [("  SPAWNING  ./scrolls/x2047/                 [ 2047 ]", CYAN, False)],
    [("  DISK: 100% PAPYRUS", GREEN, True)],
], 160)

t.blank(200)
t.reveal([
    [("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", REED, False)],
    [("  ~  crash your whole computer system            ~", INK, True)],
    [("  ~      and revert you to papyrus               ~", INK, True)],
    [("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", REED, False)],
], 420)
t.hold(1800)
t.blink()

t.save_gif(os.path.join(OUT, "demo.gif"))
t.save_png(os.path.join(OUT, "shot.png"))
print("wrote docs/demo.gif + docs/shot.png")
