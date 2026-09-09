"""Shared stage machinery for the 3030 programs.

Extracted at the fourth track, not the first. virus.py, upgrade.py and
slipping.py had all grown their own copy of these by then, which is when you
know what the shared thing actually is -- see SPEC.md.

Structural escapes only. Each program keeps its own palette, because the
colour is part of what the program is.
"""
import shutil
import sys
import time

ESC = "\033["
HOME = ESC + "H"
CLEAR = ESC + "2J" + ESC + "H"
EOL = ESC + "K"
RESET = ESC + "0m"
HIDE, SHOW = ESC + "?25l", ESC + "?25h"

FAST = "--fast" in sys.argv


def fast(on=True):
    """Zero every sleep. The self-checks use this to run in no time at all."""
    global FAST
    FAST = on


def w(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def nap(t):
    if not FAST:
        time.sleep(t)


def size():
    c = shutil.get_terminal_size((80, 24))
    return c.columns, c.lines


def type_out(s, cps=45, end="\n"):
    for ch in s:
        w(ch)
        nap(1.0 / cps)
    w(end)


def restore():
    """Always give the terminal back: colours reset, cursor visible."""
    w(RESET + SHOW + "\n")
