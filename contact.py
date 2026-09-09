#!/usr/bin/env python3
"""POSITIVE CONTACT -- Deltron 3030, track 5. See SPEC.md.

A distributed-computing screensaver that listens for intelligent life, finds
it, and resolves it into a mineral rights filing before the greeting has
finished decoding.

    python contact.py            ~50s
    python contact.py --fast     no sleeps
    python contact.py --check    self-check

The track is about assimilating matter and energy on the way through space.
This is that, rendered as a workflow with a ledger at the end. Nobody is ever
replied to; replying is not one of the steps.
"""
import io
import sys
from contextlib import redirect_stdout

import audio
import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, type_out, w
from news import OWNERS  # the same corporations, because of course it is

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
GREEN = ESC + "38;5;42m"
AMBER = ESC + "38;5;214m"
RED = ESC + "38;5;203m"

BANDS = ["1420.406 MHz", "1612.231 MHz", "1665.402 MHz", "4829.660 MHz"]

# (designation, what they said, what they were sitting on, tonnes)
CIVS = [
    ("Kepler-442 b", "we have been waiting", "heavy water", 1.2e9),
    ("Gliese 667 Cc", "we have so much to teach you", "rare earths", 4.4e11),
    ("TRAPPIST-1 e", "is anyone there", "helium-3", 8.7e8),
]

# Every contact runs the same pipeline. None of the steps is "reply".
PIPELINE = [
    ("DECODE", "language decoded", 0.4),
    ("CLASSIFY", "lifeform classified", 0.3),
    ("SURVEY", "resource survey complete", 0.9),
    ("VALUE", "reserves valued", 0.5),
    ("CLAIM", "mineral rights filed", 0.6),
    ("RESOLVE", "contact resolved", 0.4),
]


def ledger_row(i):
    """One filing. Assigned to whichever shell company is next in the chain."""
    world, _, resource, tonnes = CIVS[i]
    return world, resource, tonnes, OWNERS[i % len(OWNERS)]


def scan(i):
    w(f"\n  {DIM}workunit {i + 1:03d}  band {BANDS[i % len(BANDS)]}{RESET}\n")
    for step in range(4):
        w(f"\r  {DIM}listening{'.' * (step + 1):<6}{RESET}")
        nap(0.45)
    w(f"\r  {GREEN}POSITIVE CONTACT{RESET}{DIM}   signal-to-noise 31.4{RESET}      \n")
    nap(0.6)


def resolve(i):
    world, said, resource, tonnes = CIVS[i]
    w(f"  {WHITE}{world}{RESET}\n")
    nap(0.4)
    for tag, what, secs in PIPELINE:
        ink = RED if tag == "RESOLVE" else AMBER if tag == "CLAIM" else DIM
        w(f"    {ink}{tag:<9}{RESET}{DIM}{what}{RESET}\n")
        nap(secs)
        if tag == "DECODE":
            # The only thing they ever say, arriving after it stops mattering
            w(f"    {DIM}          they said: {RESET}{WHITE}\"{said}\"{RESET}\n")
            nap(0.8)
    world, resource, tonnes, owner = ledger_row(i)
    w(f"    {DIM}          {tonnes:,.0f} t {resource} -> {owner}{RESET}\n")
    nap(0.9)


def run():
    w(CLEAR + HIDE)
    w(f"\n  {WHITE}POSITIVE CONTACT{RESET}  {DIM}// deep field survey, node 1 of 1{RESET}\n")
    w(f"  {DIM}{'-' * 58}{RESET}\n")
    nap(0.8)
    for i in range(len(CIVS)):
        scan(i)
        resolve(i)
    w(f"\n  {DIM}{'-' * 58}{RESET}\n")
    w(f"  {WHITE}LEDGER{RESET}\n")
    total = 0.0
    for i in range(len(CIVS)):
        world, resource, tonnes, owner = ledger_row(i)
        total += tonnes
        w(f"    {world:<15}{DIM}{resource:<14}{tonnes:>14,.0f} t   {owner}{RESET}\n")
    w(f"\n  {len(CIVS)} civilisations contacted. {len(CIVS)} resolved.\n")
    w(f"  {total:,.0f} tonnes booked. {AMBER}0 replies sent.{RESET}\n")
    nap(0.8)
    type_out(f"  {DIM}Listening resumes in 4 seconds.{RESET}", 40)
    w("\n")


def main():
    audio.cue("contact")
    try:
        run()
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    assert "reply" not in [t.lower() for t, _, _ in PIPELINE], "replying is not a step"
    assert PIPELINE[0][0] == "DECODE" and PIPELINE[-1][0] == "RESOLVE", \
        "it must end on resolve, not on the greeting"
    # The joke, asserted: understanding them comes first, and changes nothing.
    tags = [t for t, _, _ in PIPELINE]
    assert tags.index("DECODE") < tags.index("CLAIM") < tags.index("RESOLVE"), \
        "decode before claim before resolve, or the point is lost"
    assert all(said for _, said, _, _ in CIVS), "every civilisation says something"

    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    for world, said, _, _ in CIVS:
        assert world in out and said in out, f"{world} went missing"
    assert "0 replies sent." in out, "the ledger must admit nobody was answered"
    assert out.count("POSITIVE CONTACT") == len(CIVS) + 1, "one per contact, plus the header"
    total = sum(t for _, _, _, t in CIVS)
    assert f"{total:,.0f} tonnes" in out, "the ledger total must add up"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {len(CIVS)} contacted, {len(PIPELINE)} steps, none of them a reply")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
