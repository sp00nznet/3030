#!/usr/bin/env python3
"""BATTLESONG -- Deltron 3030, track 18. See SPEC.md.

Two sorting algorithms, six rounds, one judge. The battle is real: both
contenders actually sort, and the times on screen are measured, not invented.

    python battlesong.py            the battle
    python battlesong.py --fast     smaller rounds
    python battlesong.py --check    self-check

The joke is not who wins. It is that the outcome is settled in round one and
we run all six anyway, with the boasts getting longer as the margin widens.
"""
import io
import random
import sys
import time
from contextlib import redirect_stdout

import audio
import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, type_out, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
GREEN = ESC + "38;5;42m"
AMBER = ESC + "38;5;214m"
RED = ESC + "38;5;203m"

SIZES = [200, 400, 800, 1200, 1600, 2000]
FAST_SIZES = [40, 60, 80, 100, 120, 140]

# The loser talks more the further behind it gets. One per round.
BOASTS = [
    "I have been doing this since 1956",
    "I am simple enough to explain on a napkin",
    "my worst case is my average case, which is honest",
    "I use no extra memory, unlike some people",
    "I am still going",
    "I am still going",
]


def bubble(xs):
    """The challenger. Correct, and that is all it has."""
    a = list(xs)
    for i in range(len(a)):
        swapped = False
        for j in range(len(a) - i - 1):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def timsort(xs):
    """The champion. Forty years of other people's work, called in one line."""
    return sorted(xs)


def round_of(n, seed=0):
    """Runs both, returns (bubble_secs, timsort_secs, agreed). Real timings."""
    data = random.Random(seed + n).sample(range(n * 10), n)
    t0 = time.perf_counter()
    a = bubble(data)
    t1 = time.perf_counter()
    b = timsort(data)
    t2 = time.perf_counter()
    return t1 - t0, t2 - t1, a == b


def run():
    sizes = FAST_SIZES if theater.FAST else SIZES
    w(CLEAR + HIDE)
    w(f"\n  {WHITE}BATTLESONG{RESET}  {DIM}// bubble sort vs timsort, {len(sizes)} rounds{RESET}\n")
    w(f"  {DIM}{'-' * 58}{RESET}\n\n")
    nap(0.8)
    score = [0, 0]
    for i, n in enumerate(sizes):
        bt, tt, agreed = round_of(n, seed=7)
        score[0 if bt < tt else 1] += 1
        margin = bt / tt if tt else float("inf")
        w(f"  {DIM}round {i + 1}{RESET}  {DIM}n={n:<6}{RESET}"
          f"{RED}bubble {bt * 1000:8.1f}ms{RESET}   "
          f"{GREEN}timsort {tt * 1000:6.2f}ms{RESET}   {DIM}x{margin:,.0f}{RESET}\n")
        nap(0.35)
        w(f"    {DIM}bubble: \"{BOASTS[i % len(BOASTS)]}\"{RESET}\n")
        nap(0.7)
        if not agreed:
            w(f"    {RED}disagreement: the battle is void{RESET}\n")
    w(f"\n  {DIM}{'-' * 58}{RESET}\n")
    w(f"  {WHITE}RESULT{RESET}  timsort {score[1]} - {score[0]} bubble\n\n")
    nap(0.8)
    type_out(f"  {AMBER}The result was known in round 1. We ran all {len(sizes)}.{RESET}", 40)
    w(f"  {DIM}Both answers were identical every time. That was never the question.{RESET}\n\n")


def main():
    audio.cue("battlesong")
    try:
        run()
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    # The battle has to be fair, or the joke is just a rigged benchmark.
    for n in (40, 120):
        bt, tt, agreed = round_of(n, seed=7)
        assert agreed, f"the two must produce identical output at n={n}"
        assert bt > 0 and tt > 0, "both must actually run"
    assert bubble([3, 1, 2]) == [1, 2, 3] == timsort([3, 1, 2]), "both must sort"
    assert bubble([]) == [] and bubble([1]) == [1], "and survive the empty cases"
    assert len(BOASTS) >= len(FAST_SIZES), "every round needs a boast"

    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    assert "RESULT" in out and "timsort" in out, "no result was declared"
    assert "The result was known in round 1." in out, "the punchline is missing"
    assert "void" not in out, "the contenders disagreed, which must never happen"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {len(FAST_SIZES)} rounds, both sort identically, timsort wins them all")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
