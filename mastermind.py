#!/usr/bin/env python3
"""MASTERMIND -- Deltron 3030, track 6. See SPEC.md.

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
    """'1 4 4 2' or '1442' -> (1, 4, 4, 2). None if it is not a legal guess."""
    parts = text.split() if " " in text else list(text.strip())
    if len(parts) != SLOTS:
        return None
    try:
        guess = tuple(int(p) for p in parts)
    except ValueError:
        return None
    return guess if all(1 <= g <= GLYPHS for g in guess) else None


def render(guess):
    return " ".join(f"{INK[g]}{g}{RESET}" for g in guess)


def bar(exact, displaced):
    return ("#" * exact) + ("+" * displaced) + ("." * (SLOTS - exact - displaced))


def play(secret, ask):
    """Returns (won, attempts_used). `ask` supplies guesses, so this is testable."""
    w(f"\n  {WHITE}BREACH{RESET} {DIM}// corporate tower, sublevel 4{RESET}\n")
    w(f"  {DIM}{GLYPHS} glyphs, {SLOTS} slots, {ATTEMPTS} attempts. Repeats allowed.{RESET}\n")
    w(f"  {DIM}# = right slot   + = right glyph, wrong slot{RESET}\n\n")
    used = 0
    while used < ATTEMPTS:
        try:
            raw = ask(f"  {DIM}[{ATTEMPTS - used:>2} left]{RESET} > ")
        except (EOFError, KeyboardInterrupt):
            w(f"\n  {DIM}Withdrawn. The code was {render(secret)}{DIM}.{RESET}\n")
            return False, used
        guess = parse(raw)
        if guess is None:
            # A malformed guess is a typo, not an attempt. Do not charge for it.
            w(f"  {BAD}{SLOTS} digits, 1-{GLYPHS}. Try '1 4 4 2' or '1442'.{RESET}\n")
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

    assert parse("1 4 4 2") == parse("1442") == (1, 4, 4, 2), "both input forms"
    assert parse("1 4 4") is None and parse("7777") is None, "must reject bad guesses"
    assert parse("abcd") is None and parse("0000") is None, "and non-digits and zero"

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
