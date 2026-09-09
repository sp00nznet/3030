#!/usr/bin/env python3
"""UPGRADE (A Brand New Day) -- Deltron 3030, track 12. See SPEC-upgrade.md.

Upgrades nothing. Perfectly. The version number goes up; that is the delta.

    python upgrade.py             the full bit, ~40s
    python upgrade.py --fast      no sleeps
    python upgrade.py --mute      no chime
    python upgrade.py --rollback  the truest line in the program
    python upgrade.py --check     self-check

virus.py is a threat that cannot be carried out. This is a promise kept to
the letter that means nothing. Same joke from the other end.
"""
import io
import os
import sys
import threading
from contextlib import redirect_stdout

import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, size, type_out, w

HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
MUTE = "--mute" in sys.argv

BLUE = ESC + "38;5;39m"
WHITE = ESC + "38;5;255m"
DIM = ESC + "38;5;245m"
OK = ESC + "38;5;42m"
WARN = ESC + "38;5;214m"

FROM_V, TO_V = "v3030.1", "v3030.2"
FEATURES_BEFORE, FEATURES_AFTER = 47, 46
SIZE = "1,204 MiB"

def changelog():
    """'#' lines are notes to whoever edits the file, not changelog entries."""
    with open(os.path.join(HERE, "changelog.txt"), encoding="utf-8") as f:
        return [ln.rstrip() for ln in f if not ln.lstrip().startswith("#") and ln.strip()]


# --- audio -----------------------------------------------------------------
# Ascending fanfare that resolves to the note it started on: the success chime
# goes exactly as far as the upgrade does.
CHIME = [(523, 120), (659, 120), (784, 160), (523, 320)]


def chime():
    try:
        import winsound
    except ImportError:
        return  # not Windows: silent, everything else runs
    for freq, ms in CHIME:
        winsound.Beep(freq, ms)


def banner():
    w(BLUE + "  +--------------------------------------------------------+\n")
    w("  |  DELTRON 3030  //  UPGRADE                             |\n")
    w("  |  installed: " + FROM_V + "                                    |\n")
    w("  +--------------------------------------------------------+" + RESET + "\n")


# --- act 1: check ----------------------------------------------------------
def act_check():
    w(CLEAR + HIDE + WHITE)
    banner()
    w("\n")
    type_out("  Checking for updates", 30, end="")
    for _ in range(3):
        nap(0.5)
        w(".")
    nap(0.8)
    w("\n\n  " + OK + TO_V + " is available." + RESET + "  (" + SIZE + ")\n\n")
    nap(0.6)
    w("  " + DIM + "What is new in " + TO_V + ":" + RESET + "\n")
    for line in changelog():
        w("    " + DIM + "-" + RESET + " " + line + "\n")
        nap(0.55)
    nap(1.0)


# --- act 2: download -------------------------------------------------------
# ponytail: hand-authored table, not computed. The ETA getting worse is the
# joke, and it has to land identically every run.
ETA = [
    (0, "estimating..."),
    (8, "12 min remaining"),
    (19, "14 min remaining"),
    (31, "18 min remaining"),
    (46, "22 min remaining"),
    (58, "9 min remaining"),
    (67, "2 min remaining"),
    (79, "4 min remaining"),
    (88, "less than a minute"),
    (95, "less than a minute"),
    (99, "less than a minute"),
]


def eta_for(pct):
    text = ETA[0][1]
    for at, t in ETA:
        if pct >= at:
            text = t
    return text


def act_download():
    cols, _ = size()
    width = max(20, min(40, cols - 40))
    w("\n")
    for pct in range(0, 100):
        fill = int(width * pct / 100)
        bar = "#" * fill + "-" * (width - fill)
        w("\r  Downloading " + TO_V + "  [" + BLUE + bar + RESET + "] "
          + str(pct).rjust(3) + "%   " + DIM + eta_for(pct).ljust(20) + RESET)
        nap(0.04 if pct < 88 else 0.10)
    stalled = "#" * (width - 1) + "-"
    for _ in range(14):  # the stall. everyone knows this stall
        w("\r  Downloading " + TO_V + "  [" + BLUE + stalled + RESET + "]  99%   "
          + DIM + "less than a minute".ljust(20) + RESET)
        nap(0.35)
    w("\r  Downloading " + TO_V + "  [" + OK + "#" * width + RESET + "] 100%   "
      + DIM + "done".ljust(20) + RESET + "\n")
    w("  " + DIM + SIZE + " downloaded (3 MiB of it is new)" + RESET + "\n")
    nap(0.9)


# --- act 3: migrate --------------------------------------------------------
# (label, seconds, kind). "This will only take a moment" must be the longest.
STEPS = [
    ("Migrating config -> config (new format)", 0.9, None),
    ("Rebuilding index (1,204 items)", 1.3, None),
    ("Converting Settings to Preferences", 0.8, None),
    ("Optimizing", 1.5, None),
    ("Retiring: batch rename", 0.7, "gone"),
    ("This will only take a moment", 5.0, None),
    ("Finalizing", 0.5, None),
]


def act_migrate():
    frames = "|/-" + chr(92)
    w("\n")
    for label, secs, kind in STEPS:
        n = 1 if theater.FAST else max(4, int(secs / 0.12))
        for i in range(n):
            w("\r  [" + DIM + frames[i % 4] + RESET + "] " + label)
            nap(0.12)
        tag = (WARN if kind == "gone" else OK) + "OK" + RESET
        w("\r  [" + tag + "] " + label + ESC + "K\n")
    nap(0.8)


# --- act 4: restart --------------------------------------------------------
SUMMARY = [
    ("version", FROM_V, TO_V),
    ("features", str(FEATURES_BEFORE), str(FEATURES_AFTER)),
    ("settings", "where you left them", "reset"),
    ("icon", "fine", "flat"),
]


def act_restart():
    w("\n")
    type_out("  Restarting to complete the upgrade...", 40)
    nap(1.4)
    w(CLEAR)
    nap(1.0)
    banner()  # the identical screen. that is the whole act
    w("\n")
    nap(1.2)
    w("  " + OK + "UPGRADE COMPLETE" + RESET + "\n\n")
    for name, before, after in SUMMARY:
        w("  " + DIM + name.ljust(10) + RESET + " " + before.rjust(20)
          + "  " + DIM + "->" + RESET + "  " + after + "\n")
        nap(0.5)
    w("\n  " + DIM + "0 files changed, 0 insertions(+), 0 deletions(-)" + RESET + "\n\n")
    nap(1.2)
    type_out("  " + WHITE + "A brand new day." + RESET, 12)
    nap(1.0)


def main():
    if not MUTE and not theater.FAST:
        threading.Thread(target=chime, daemon=True).start()
    try:
        act_check()
        act_download()
        act_migrate()
        act_restart()
    finally:
        w(RESET + SHOW + "\n")  # always give the terminal back


def _ver(s):
    return tuple(int(x) for x in s.lstrip("v").split("."))


def demo():
    """One assert per act, plus the ones that protect the joke."""
    global MUTE
    MUTE = True
    theater.fast(True)
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    assert TO_V in out and "is available" in out, "act 1 (check) did not run"
    assert "100%" in out and "3 MiB of it is new" in out, "act 2 (download) did not finish"
    assert all(label in out for label, _, _ in STEPS), "act 3 (migrate) dropped a step"
    assert "UPGRADE COMPLETE" in out and "A brand new day." in out, "act 4 (restart) did not run"
    # The post-restart banner still reads "installed: v3030.1" while the summary
    # under it claims v3030.2. That contradiction is the joke, not a bug. Do not
    # "fix" the banner.
    assert out.count("installed: " + FROM_V) == 2, "the banner must come back unchanged"

    # the joke, asserted
    assert _ver(TO_V) > _ver(FROM_V), "the version must go up"
    assert FEATURES_AFTER < FEATURES_BEFORE, "the feature count must go down"
    assert "0 files changed" in out, "the punchline is missing"
    assert max(STEPS, key=lambda s: s[1])[0] == "This will only take a moment", \
        "'a moment' must be the longest step"
    mins = [int(t.split()[0]) for _, t in ETA if t.split()[0].isdigit()]
    assert any(b > a for a, b in zip(mins, mins[1:])), "the ETA must get worse"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print("ok: 4 acts, version up, features down, 0 files changed")


if __name__ == "__main__":
    if "--rollback" in sys.argv:
        print("Rollback is not available for " + TO_V + ".")
        sys.exit(1)
    demo() if "--check" in sys.argv else main()
