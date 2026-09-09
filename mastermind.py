#!/usr/bin/env python3
"""MASTERMIND -- Deltron 3030, track 10. See SPEC.md.

A lock on the corporate tower, and you have ten tries. Six glyphs, four
slots, repeats allowed. After each attempt the panel tells you how many
glyphs are in the right slot and how many are right but somewhere else.

    python mastermind.py            play
    python mastermind.py --seed 7   the same lock every time
    python mastermind.py --check    self-check

The one program here that is an actual game, with actual logic you can lose
to. The rest of the album is theater; this one keeps score.
"""
import random
import sys
from collections import Counter

import audio
from theater import ESC, RESET, w

GLYPHS = 6
SLOTS = 4
ATTEMPTS = 10

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
GOOD = ESC + "38;5;42m"
BAD = ESC + "38;5;203m"
# One colour per glyph, so a repeat is obvious at a glance.
INK = {1: ESC + "38;5;203m", 2: ESC + "38;5;214m", 3: ESC + "38;5;220m",
       4: ESC + "38;5;42m", 5: ESC + "38;5;44m", 6: ESC + "38;5;177m"}


def score(secret, guess):
    """(exact, displaced) -- the classic scoring, with duplicates handled.

    The bug everyone writes here is counting a repeated glyph twice: once as
    exact and again as displaced. Intersecting the counts takes the minimum
    of each glyph, and subtracting the exacts leaves only the misplaced ones.
    """
    exact = sum(a == b for a, b in zip(secret, guess))
    common = sum((Counter(secret) & Counter(guess)).values())
    return exact, common - exact


def parse(text):
    """'1 4 4 2' or '1442' -> ((1, 4, 4, 2), None), else (None, why).

    The reason matters: "that guess is invalid" sends people looking for a
    rule they broke. Naming the glyph that is out of range does not.
    """
    parts = text.split() if " " in text else list(text.strip())
    if len(parts) != SLOTS:
        return None, f"that is {len(parts)} glyph{'' if len(parts) == 1 else 's'}, I need {SLOTS}"
    try:
        guess = tuple(int(p) for p in parts)
    except ValueError:
        return None, "glyphs are digits"
    bad = sorted({g for g in guess if not 1 <= g <= GLYPHS})
    if bad:
        listed = " and ".join(str(g) for g in bad)
        return None, f"no glyph {listed} on this lock -- they run 1 to {GLYPHS}"
    return guess, None


def render(guess):
    return " ".join(f"{INK[g]}{g}{RESET}" for g in guess)


def bar(exact, displaced):
    return ("#" * exact) + ("+" * displaced) + ("." * (SLOTS - exact - displaced))


def play(secret, ask):
    """Returns (won, attempts_used). `ask` supplies guesses, so this is testable."""
    legend = " ".join(f"{INK[g]}{g}{RESET}" for g in range(1, GLYPHS + 1))
    w(f"\n  {WHITE}BREACH{RESET} {DIM}// corporate tower, sublevel 4{RESET}\n")
    w(f"  {DIM}glyphs:{RESET} {legend}   {DIM}<- only these. {SLOTS} of them, repeats allowed{RESET}\n")
    w(f"  {DIM}{ATTEMPTS} attempts.  # = right slot   + = right glyph, wrong slot{RESET}\n\n")
    used = 0
    while used < ATTEMPTS:
        try:
            raw = ask(f"  {DIM}[{ATTEMPTS - used:>2} left]{RESET} > ")
        except (EOFError, KeyboardInterrupt):
            w(f"\n  {DIM}Withdrawn. The code was {render(secret)}{DIM}.{RESET}\n")
            return False, used
        guess, why = parse(raw)
        if guess is None:
            # A malformed guess is a typo, not an attempt. Do not charge for it.
            w(f"       {BAD}{why}{RESET}{DIM}  (try '1 4 4 2' or '1442'){RESET}\n")
            continue
        used += 1
        exact, displaced = score(secret, guess)
        w(f"       {render(guess)}   [{bar(exact, displaced)}]  "
          f"{DIM}{exact} exact, {displaced} displaced{RESET}\n")
        if exact == SLOTS:
            w(f"\n  {GOOD}The lock opens.{RESET} {DIM}{used} attempt"
              f"{'' if used == 1 else 's'}.{RESET}\n")
            w(f"  {WHITE}You are the mastermind.{RESET}\n\n")
            return True, used
    w(f"\n  {BAD}Lockout.{RESET} The code was {render(secret)}{DIM}.{RESET}\n\n")
    return False, used


def main(seed=None):
    audio.cue("mastermind")
    rng = random.Random(seed)
    secret = tuple(rng.randint(1, GLYPHS) for _ in range(SLOTS))
    play(secret, input)


def demo():
    # scoring, including the duplicate case that breaks naive implementations
    assert score((1, 2, 3, 4), (1, 2, 3, 4)) == (4, 0), "a perfect guess is 4 exact"
    assert score((1, 2, 3, 4), (5, 5, 5, 5)) == (0, 0), "no overlap is nothing"
    assert score((1, 2, 3, 4), (4, 3, 2, 1)) == (0, 4), "all present, all misplaced"
    assert score((1, 1, 2, 2), (1, 2, 1, 1)) == (1, 2), "duplicates must not double-count"
    assert score((1, 1, 1, 1), (1, 2, 2, 2)) == (1, 0), "one match, not four"
    assert score((1, 2, 2, 2), (1, 1, 1, 1)) == (1, 0), "and the same the other way round"

    assert parse("1 4 4 2")[0] == parse("1442")[0] == (1, 4, 4, 2), "both input forms"
    assert parse("1 4 4")[0] is None and parse("7777")[0] is None, "must reject bad guesses"
    assert parse("abcd")[0] is None and parse("0000")[0] is None, "and non-digits and zero"
    # the rejection has to say which glyph was wrong, or people hunt for a rule
    assert "8" in parse("1823")[1] and "9" in parse("1900")[1], "name the bad glyph"
    assert "0" in parse("1900")[1], "zero is a glyph people try, so name it too"
    assert "3" in parse("143")[1] and "4" in parse("143")[1], "say how many were given"

    secret = (3, 1, 4, 1)
    fed = iter(["1111", "nonsense", "9999", "3 1 4 1"])
    won, used = play(secret, lambda _: next(fed))
    assert won, "the scripted game should win"
    assert used == 2, f"typos must not cost an attempt (used {used})"

    lost, used = play((1, 1, 1, 1), lambda _: "2222")
    assert not lost and used == ATTEMPTS, "a losing game runs out of attempts"
    print(f"ok: scoring handles duplicates, {ATTEMPTS} attempts, typos are free")


if __name__ == "__main__":
    if "--check" in sys.argv:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo()
        print(buf.getvalue().strip().splitlines()[-1])
    else:
        s = None
        if "--seed" in sys.argv:
            s = int(sys.argv[sys.argv.index("--seed") + 1])
        main(s)
