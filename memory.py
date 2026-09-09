#!/usr/bin/env python3
"""MEMORY LOSS -- Deltron 3030, track 20.

Memory climbs. The description of what it is doing gets shorter. By the end
it is using a gigabyte and cannot tell you what for.

    python memory.py            ~45s
    python memory.py --fast     no sleeps
    python memory.py --check    self-check

Nothing is actually allocated. The number is a number. See SPEC.md.
"""
import io
import sys
from contextlib import redirect_stdout

import audio
import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
AMBER = ESC + "38;5;214m"
RED = ESC + "38;5;203m"

START_MIB = 64.0
GROWTH = 1.32          # per step. Never shrinks, because nothing is freed.

# The same task, erased one clause at a time. This is the whole program.
TASK = [
    "Reticulating splines in sector 7 (batch 3 of 12, 1,204 items)",
    "Reticulating splines in sector 7 (batch 3 of 12)",
    "Reticulating splines in sector 7",
    "Reticulating splines",
    "Reticulating",
    "Working on sector 7",
    "Working on something",
    "Working",
    "Doing the thing",
    "The thing",
    "...",
]
# The banner forgets itself too, on the same slope.
TITLE = ["MEMORY LOSS v3030.1", "MEMORY LOSS v3030", "MEMORY LOSS",
         "MEMORY", "MEM", "M", ""]


def used(step):
    """MiB after `step` steps. Monotonic, because nothing is ever freed."""
    return START_MIB * (GROWTH ** step)


def title_at(step):
    """The banner erodes across the same span as the task, at its own pace.

    Scaled off both lengths rather than a fixed divisor, so the banner still
    reaches its last state (blank) if either list is edited.
    """
    return TITLE[min(step * len(TITLE) // len(TASK), len(TITLE) - 1)]


def frame(step):
    """Pure: (title, task, mib) at a step. Pure so the check can skip to the end."""
    return title_at(step), TASK[min(step, len(TASK) - 1)], used(step)


def run():
    w(CLEAR + HIDE)
    for step in range(len(TASK)):
        title, task, mib = frame(step)
        ink = RED if mib > 600 else AMBER if mib > 200 else DIM
        w(CLEAR)
        w(f"\n  {WHITE}{title}{RESET}\n")
        w(f"  {DIM}{'-' * 52}{RESET}\n\n")
        w(f"  {task}\n\n")
        w(f"  {ink}{mib:,.0f} MiB{RESET}{DIM}   resident, nothing freed{RESET}\n")
        nap(1.1 if step else 1.8)
    nap(0.8)
    w(f"\n  {DIM}{used(len(TASK) - 1):,.0f} MiB allocated. 0 freed.{RESET}\n")
    w(f"  {WHITE}I don't remember why.{RESET}\n\n")


def main():
    audio.cue("memory")
    try:
        run()
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    # The two slopes that are the joke: memory up, description down.
    mib = [used(s) for s in range(len(TASK))]
    assert all(b > a for a, b in zip(mib, mib[1:])), "memory must never go down"
    # What erodes is specificity, not length -- "Reticulating" becomes the
    # longer "Working on sector 7" on the way down. So measure the trend, not
    # each step, or the assert ends up describing the wrong thing.
    lens = [len(t) for t in TASK]
    assert sum(lens[:3]) / 3 > sum(lens[-3:]) / 3 * 3, "the task must erode"
    assert lens[0] > lens[-1] * 5, "and end at almost nothing"
    assert TASK[-1] == "...", "and end on nothing at all"
    assert title_at(0).startswith("MEMORY LOSS"), "it starts out knowing its name"
    assert title_at(len(TASK) - 1) == "", "and ends not knowing it"
    assert mib[-1] > 1000, f"it should end over a gigabyte, got {mib[-1]:.0f}"

    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    assert "0 freed" in out and "I don't remember why." in out, "the ending is missing"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {START_MIB:,.0f} MiB -> {mib[-1]:,.0f} MiB, {lens[0]} chars -> {lens[-1]}")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
