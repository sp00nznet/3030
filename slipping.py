#!/usr/bin/env python3
"""TIME KEEPS ON SLIPPING -- Deltron 3030, track 14. See SPEC.md.

A clock. It is correct when it starts. It is not correct for long.

The drift is exponential, so the first half minute looks fine, a minute in
you are a couple of minutes fast, three minutes in you are weeks ahead, and
around the five minute mark it arrives in 3030 and stops.

    python slipping.py                the clock, ~5 min to 3030
    python slipping.py --drift 4      slip sooner (time constant, seconds)
    python slipping.py --drift 40     slip later
    python slipping.py --check        self-check

Ctrl-C gives you your terminal back and tells you how far it got.
"""
import math
import sys
import time
from datetime import datetime, timedelta

from theater import CLEAR, EOL, ESC, HIDE, HOME, RESET, restore, w

TAU = 12.4          # seconds. The knob. Smaller slips sooner.
TARGET_YEAR = 3030
FPS = 10

ESC = "\033["
HOME = ESC + "H"
CLEAR = ESC + "2J" + ESC + "H"
EOL = ESC + "K"
DIM = ESC + "38;5;245m"
CYAN = ESC + "38;5;44m"
WHITE = ESC + "38;5;255m"

# ponytail: block char where the console can encode it, '#' where it cannot.
BLOCK = "█"
try:
    BLOCK.encode(sys.stdout.encoding or "utf-8")
except (UnicodeEncodeError, LookupError, TypeError):
    BLOCK = "#"

_SEG = {
    "0": ("###", "# #", "# #", "# #", "###"),
    "1": ("  #", "  #", "  #", "  #", "  #"),
    "2": ("###", "  #", "###", "#  ", "###"),
    "3": ("###", "  #", "###", "  #", "###"),
    "4": ("# #", "# #", "###", "  #", "  #"),
    "5": ("###", "#  ", "###", "  #", "###"),
    "6": ("###", "#  ", "###", "# #", "###"),
    "7": ("###", "  #", "  #", "  #", "  #"),
    "8": ("###", "# #", "###", "# #", "###"),
    "9": ("###", "# #", "###", "  #", "###"),
    ":": ("   ", " # ", "   ", " # ", "   "),
}
DIGITS = {c: tuple(r.replace("#", BLOCK) for r in rows) for c, rows in _SEG.items()}


def big(text):
    """'12:34' -> five strings of block digits."""
    return ["  ".join(DIGITS[c][row] for c in text) for row in range(5)]


def slip(t, tau=TAU):
    """Seconds of drift after t real seconds. Exponential: unnoticeable, then not."""
    return math.exp(t / tau) - 1.0


def human(sec):
    sec = int(sec)
    for div, name in ((31556952, "year"), (86400, "day"), (3600, "hour"),
                      (60, "minute"), (1, "second")):
        if sec >= div:
            n = sec // div
            return f"{n:,} {name}" + ("" if n == 1 else "s")
    return "no time at all"


def frame(start, t, tau=TAU):
    """Pure: the screen at t real seconds in, and whether we have arrived.

    Pure so the self-check can jump to minute five without waiting for it.
    """
    cap = (datetime(TARGET_YEAR, 1, 1) - start).total_seconds()
    done = slip(t, tau) >= cap
    off = min(slip(t, tau), cap)   # the clock stops at 3030, so the readout does too
    shown = start + timedelta(seconds=off)
    lines = [""]
    lines += [f"    {CYAN}{r}{RESET}" for r in big(shown.strftime("%H:%M:%S"))]
    lines += ["",
              f"    {WHITE}{shown.strftime('%A %d %B %Y')}{RESET}",
              "",
              f"    {DIM}ahead by {human(off)}{RESET}",
              ""]
    if done:
        lines += [f"    {WHITE}3030.{RESET}", f"    {DIM}It kept on slipping.{RESET}", ""]
    else:
        lines += [f"    {DIM}time keeps on slipping   (ctrl-c to stop it){RESET}", ""]
    return lines, done


def main(tau=TAU):
    start, t0 = datetime.now(), time.monotonic()
    off = 0.0
    try:
        w(CLEAR + HIDE)
        while True:
            elapsed = time.monotonic() - t0
            cap = (datetime(TARGET_YEAR, 1, 1) - start).total_seconds()
            off = min(slip(elapsed, tau), cap)
            lines, done = frame(start, elapsed, tau)
            w(HOME + "\n".join(ln + EOL for ln in lines))
            if done:
                break
            time.sleep(1.0 / FPS)
    except KeyboardInterrupt:
        pass
    finally:
        restore()
        print(f"  It slipped {human(off)} in {human(time.monotonic() - t0)}.")


def demo():
    assert set(DIGITS) >= set("0123456789:"), "missing a digit"
    assert all(len(r) == 5 for r in DIGITS.values()), "digits must be five rows"
    assert len(big("12:34")) == 5, "big() must render five rows"

    assert slip(0) == 0.0, "the clock must be correct when it starts"
    ts = [0, 10, 30, 60, 180, 300]
    drifts = [slip(t) for t in ts]
    assert all(b > a for a, b in zip(drifts, drifts[1:])), "drift must only grow"
    assert drifts[1] < 5, "still looks fine ten seconds in"
    assert drifts[-1] > 3e10, "five minutes in it should be a thousand years"

    start = datetime(2026, 1, 1, 12, 0, 0)
    early, done = frame(start, 0)
    assert not done and all(r in "".join(early) for r in big("12:00:00")), "starts on time"
    late, done = frame(start, 600)
    assert done and "3030." in "".join(late), "it must arrive and stop"
    assert human(1) == "1 second" and human(31556952 * 3).startswith("3 year")
    assert "1,00" in "".join(late), "the arrival readout must be ~1004 years, not 3e13"
    print(f"ok: correct at 0s, {human(slip(60))} fast at 60s, arrives by 300s")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        tau = TAU
        if "--drift" in sys.argv:
            tau = float(sys.argv[sys.argv.index("--drift") + 1])
        main(tau)
