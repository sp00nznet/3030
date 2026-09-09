#!/usr/bin/env python3
"""THE NEWS (A Wholly Owned Subsidiary of Microsoft, Inc.) -- track 15.

A news broadcast where the ownership disclosure is longer than the story,
and gets longer with every story, until the chain closes on itself.

    python news.py             the broadcast, ~40s
    python news.py --fast      no sleeps
    python news.py --check     self-check

The title is already the whole program. All that was left was to run the
disclosure to its logical end.
"""
import io
import sys
from contextlib import redirect_stdout

import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, type_out, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
AMBER = ESC + "38;5;214m"
RED = ESC + "38;5;203m"

# Every name here is invented. The joke is the structure, not any real company.
OWNERS = [
    "Ubiquitous Media",
    "Ubiquitous Media Holdings",
    "Vandal Broadcast Group",
    "Meridian Content Partners",
    "the Brymar College Endowment",
    "Continental Trust (Orbital)",
    "the Orbital Workers' Pension Fund",
    "an algorithm nobody has read",
    "itself",
]

# (headline, how deep the disclosure runs). It only ever goes one way.
STORIES = [
    ("Mars colony votes to secede. Vote not recognised.", 1),
    ("Third sun over Oakland declared a lighting feature.", 2),
    ("Water restored to sublevel 4 after nine years.", 3),
    ("Memory prices fall. Nobody can remember why.", 5),
    ("Corporate personhood extended to shell companies.", 7),
    ("Broadcast licence renewed. No other bids were possible.", 9),
]


def disclosure(depth):
    return [f"a wholly owned subsidiary of {o}" for o in OWNERS[:depth]]


def broadcast():
    w(CLEAR + HIDE + WHITE)
    w(f"\n  {WHITE}THE NEWS{RESET}{DIM}   3030-09-08   this broadcast is sponsored{RESET}\n")
    w(f"  {DIM}{'-' * 62}{RESET}\n\n")
    nap(0.8)
    for headline, depth in STORIES:
        type_out(f"  {WHITE}{headline}{RESET}", 55)
        nap(0.35)
        for i, line in enumerate(disclosure(depth)):
            ink = RED if line.endswith("itself") else DIM
            w(f"  {' ' * (2 + i * 2)}{ink}{line}{RESET}\n")
            nap(0.13)
        w("\n")
        nap(0.5)
    w(f"  {DIM}{'-' * 62}{RESET}\n")
    nap(0.6)
    type_out(f"  {AMBER}The preceding was a wholly owned subsidiary of itself.{RESET}", 40)
    nap(0.5)
    w(f"  {DIM}Thank you for your attention. Your attention has been sold.{RESET}\n\n")


def main():
    try:
        broadcast()
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()

    assert all(h in out for h, _ in STORIES), "a story went missing"
    # The joke, asserted: the disclosure must outgrow the story, and only grow.
    depths = [d for _, d in STORIES]
    assert depths == sorted(depths), "the chain must only ever get longer"
    assert depths[-1] > depths[0], "and it must actually grow"
    longest = STORIES[-1]
    assert len(disclosure(longest[1])) > len(longest[0].split()), \
        "the last disclosure must be longer than the story it discloses"
    assert disclosure(len(OWNERS))[-1].endswith("itself"), "the chain must close on itself"
    assert OWNERS.count("itself") == 1, "and only close once"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {len(STORIES)} stories, chain runs {depths[0]} deep to {depths[-1]}, ends on itself")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
