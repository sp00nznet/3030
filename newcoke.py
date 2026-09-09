#!/usr/bin/env python3
"""NEW COKE -- Deltron 3030, track 9. See SPEC.md.

A rebrand. It renames the product, migrates nothing, and ends with two
products instead of one, forever.

    python newcoke.py            ~35s
    python newcoke.py --fast     no sleeps
    python newcoke.py --check    self-check

Sibling to upgrade.py: that one is a change that changes nothing, this one
is a change that doubles what it touched.
"""
import io
import sys
from contextlib import redirect_stdout

import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, type_out, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
GREEN = ESC + "38;5;42m"
AMBER = ESC + "38;5;214m"
RED = ESC + "38;5;203m"

OLD, NEW = "Ubiquitous", "Ubiq"

# (where, how many, did the rename reach it). It mostly did not.
SURFACES = [
    ("marketing site", 47, True),
    ("app title bar", 3, True),
    ("error messages", 214, False),
    ("database schema", 1, False),
    ("the URL", 1, False),
    ("support articles (2027-)", 618, False),
    ("the favicon", 1, False),
    ("legal entity name", 1, False),
    ("what customers call it", 1, False),
]

FEEDBACK = [
    "bring back the old one",
    "what was wrong with the old one",
    "is this the old one",
]


def updated():
    return sum(n for _, n, ok in SURFACES if ok)


def remaining():
    return sum(n for _, n, ok in SURFACES if not ok)


def run():
    w(CLEAR + HIDE)
    w(f"\n  {WHITE}REBRAND{RESET}  {DIM}// {OLD} -> {NEW}{RESET}\n")
    w(f"  {DIM}{'-' * 54}{RESET}\n\n")
    nap(0.8)
    type_out(f"  Renaming {OLD} to {NEW} across all surfaces...", 50)
    nap(1.0)
    w("\n")
    for where, n, ok in SURFACES:
        tag = f"{GREEN}done{RESET}" if ok else f"{AMBER}still {OLD}{RESET}"
        w(f"    {DIM}{where:<28}{RESET}{n:>5}  {tag}\n")
        nap(0.4)
    nap(0.8)
    w(f"\n  {updated()} references updated. {remaining()} remain.\n\n")
    nap(0.9)
    w(f"  {DIM}Listening to customers...{RESET}\n")
    nap(0.7)
    for line in FEEDBACK:
        w(f"    {DIM}> {RESET}{WHITE}\"{line}\"{RESET}\n")
        nap(0.6)
    nap(1.0)
    w(f"\n  {DIM}{'-' * 54}{RESET}\n")
    w(f"  {GREEN}REBRAND COMPLETE{RESET}\n\n")
    for label, before, after in [("brands", "1", "2"), ("products", "1", "2"),
                                 ("support queues", "1", "2"),
                                 ("things anyone asked for", "0", "0")]:
        w(f"  {DIM}{label:<24}{RESET}{before:>3}  {DIM}->{RESET}  {after}\n")
        nap(0.5)
    nap(1.0)
    type_out(f"\n  {WHITE}{OLD} Classic is available from today.{RESET}", 35)
    w(f"  {DIM}You now maintain both. Forever.{RESET}\n\n")


def main():
    try:
        run()
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    # The joke, asserted: the rename mostly does not land, and the count goes up.
    assert remaining() > updated() * 5, "the old name must vastly outlive the rename"
    assert any(w == "what customers call it" and not ok for w, _, ok in SURFACES), \
        "customers must keep the old name; that is the whole track"
    assert OLD in NEW or NEW in OLD, "a rebrand nobody asked for barely changes the word"

    buf = io.StringIO()
    with redirect_stdout(buf):
        main()
    out = buf.getvalue()
    assert "REBRAND COMPLETE" in out, "it must claim success"
    assert f"{OLD} Classic is available from today." in out, "the old one has to come back"
    assert "You now maintain both. Forever." in out, "and both must survive"
    assert "brands" in out and "things anyone asked for" in out, "the summary is missing"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {updated()} renamed, {remaining()} not, 1 brand -> 2")


if __name__ == "__main__":
    demo() if "--check" in sys.argv else main()
