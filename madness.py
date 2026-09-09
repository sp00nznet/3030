#!/usr/bin/env python3
"""MADNESS -- Deltron 3030, track 12. See SPEC.md.

A fuzzer. It generates genuinely hostile input, runs ten thousand cases, and
every single one passes. At the end it shows you the assertion.

    python madness.py             ~30s
    python madness.py --fast      no sleeps
    python madness.py --cases N   how many to claim
    python madness.py --check     self-check

The inputs are real and really are nasty. The oracle is the problem, which is
the point: a suite that cannot fail is not a suite, it is a decoration.
"""
import io
import random
import sys
from contextlib import redirect_stdout

import audio
import theater
from theater import CLEAR, ESC, HIDE, RESET, SHOW, nap, type_out, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
GREEN = ESC + "38;5;42m"
AMBER = ESC + "38;5;214m"

CASES = 10000

# Real fuzzer fodder. Any of these would break something somewhere.
CORPUS = [
    ("empty string", ""),
    ("nul byte", "\\x00"),
    ("-1", -1),
    ("2**63", 2 ** 63),
    ("NaN", float("nan")),
    ("negative zero", -0.0),
    ("1970-01-01T00:00:00Z", "1970-01-01T00:00:00Z"),
    ("2038-01-19T03:14:08Z", "2038-01-19T03:14:08Z"),
    ("../../etc/passwd", "../../etc/passwd"),
    ("<script>", "<script>"),
    ("'; DROP TABLE --", "'; DROP TABLE --"),
    ("%s%s%s%n", "%s%s%s%n"),
    ("4096 'A's", "A" * 4096),
    ("emoji zwj sequence", "family-of-four"),
    ("right-to-left override", "U+202E"),
    ("a list containing itself", "[[...]]"),
]


def check(value):
    """The oracle.

    ponytail: this is the joke and it must stay exactly this weak. Do not
    'fix' it into a real assertion -- madness.py exists to be a suite that
    cannot fail, and the self-check asserts that it cannot.
    """
    return True


def run(cases=CASES):
    w(CLEAR + HIDE)
    w(f"\n  {WHITE}MADNESS{RESET}  {DIM}// fuzzing, {cases:,} cases{RESET}\n")
    w(f"  {DIM}{'-' * 56}{RESET}\n\n")
    nap(0.7)
    rng = random.Random(7)
    for i, (label, value) in enumerate(rng.sample(CORPUS, len(CORPUS))):
        ok = check(value)
        w(f"    {GREEN}PASS{RESET}  {DIM}case {i * 617 + 1:>5}{RESET}  {label}\n")
        nap(0.28)
    nap(0.6)
    w(f"\n  {DIM}...{cases - len(CORPUS):,} more{RESET}\n\n")
    nap(0.9)
    w(f"  {GREEN}{cases:,} cases. 0 failures. 100% pass rate.{RESET}\n")
    nap(1.2)
    w(f"\n  {DIM}{'-' * 56}{RESET}\n")
    type_out(f"  {AMBER}The assertion, in full:{RESET}", 45)
    nap(0.5)
    w(f"\n      {WHITE}def check(value):{RESET}\n")
    w(f"      {WHITE}    return True{RESET}\n\n")
    nap(1.0)
    w(f"  {DIM}No test has ever failed. No test can.{RESET}\n\n")


def main(cases=CASES):
    audio.cue("madness")
    try:
        run(cases)
    finally:
        w(RESET + SHOW + "\n")


def demo():
    theater.fast(True)
    # The joke, asserted: nothing in the corpus can fail, including the
    # things that obviously should. If check() ever grows teeth, this fails
    # and someone has to decide which program they are writing.
    assert all(check(v) for _, v in CORPUS), "check() must pass everything"
    assert check(None) and check(object()) and check(check), "including nonsense"
    assert len(CORPUS) >= 12, "the corpus has to be long enough to look serious"
    labels = [l for l, _ in CORPUS]
    assert len(set(labels)) == len(labels), "no duplicate cases"
    assert any("2038" in l for l in labels), "keep the y3k crossover case"

    buf = io.StringIO()
    with redirect_stdout(buf):
        main(cases=500)
    out = buf.getvalue()
    assert "0 failures" in out and "100% pass rate" in out, "it must claim success"
    assert "return True" in out, "the reveal is the ending; do not remove it"
    assert "FAIL" not in out, "nothing may ever fail"
    assert out.endswith(SHOW + "\n"), "terminal was not restored"
    print(f"ok: {len(CORPUS)} hostile inputs, 0 can fail, oracle is `return True`")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        n = int(sys.argv[sys.argv.index("--cases") + 1]) if "--cases" in sys.argv else CASES
        main(n)
