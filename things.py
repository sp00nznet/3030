#!/usr/bin/env python3
"""THINGS YOU CAN DO -- Deltron 3030, track 4.

A capability list. Everything on it is unavailable.

    python things.py            the list
    python things.py 7          attempt one of them
    python things.py --all      attempt all of them
    python things.py --check    self-check

The help text is the entire product. Exits 1 from --all, because zero of
twenty available is a failure by any honest measure.
"""
import sys

from theater import ESC, RESET

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
RED = ESC + "38;5;203m"
AMBER = ESC + "38;5;214m"

# (thing, why not). Every reason is one a real product has given someone.
THINGS = [
    ("export your data", "available on the Enterprise plan"),
    ("import your data", "temporarily unavailable"),
    ("rename a file", "removed in v3030.2"),
    ("batch rename", "removed in v3030.2"),
    ("undo", "not available in your region"),
    ("sort by date", "requires an account"),
    ("sort by name", "requires a different account"),
    ("print", "requires the mobile app"),
    ("print to file", "requires the desktop app"),
    ("work offline", "requires a connection"),
    ("search your own messages", "coming soon"),
    ("see who changed this", "on the roadmap"),
    ("turn off notifications", "in Preferences (formerly Settings)"),
    ("find Preferences", "moved"),
    ("cancel your subscription", "call us"),
    ("call us", "outside business hours"),
    ("speak to a person", "you are speaking to a person"),
    ("stop the assistant", "the assistant is a core feature"),
    ("read the terms", "1,204 pages"),
    ("disagree with the terms", "by continuing you agree to the terms"),
]


def attempt(i):
    """Returns (ok, message). Nothing ever returns ok."""
    thing, why = THINGS[i]
    return False, f"cannot {thing}: {why}"


def listing():
    out = [f"\n  {WHITE}THINGS YOU CAN DO{RESET}  {DIM}({len(THINGS)} things){RESET}\n"]
    for i, (thing, why) in enumerate(THINGS, 1):
        out.append(f"  {DIM}{i:>3}.{RESET}  {thing:<28} {DIM}{why}{RESET}")
    out.append(f"\n  {DIM}python things.py <n>   to do one of them{RESET}\n")
    return out


def main(argv):
    picks = [a for a in argv if a.isdigit()]
    if "--all" in argv:
        picks = [str(i) for i in range(1, len(THINGS) + 1)]
    if not picks:
        print("\n".join(listing()))
        return 0
    done = 0
    print()
    for p in picks:
        i = int(p) - 1
        if not 0 <= i < len(THINGS):
            print(f"  {RED}no such thing: {p}{RESET}")
            continue
        ok, msg = attempt(i)
        done += ok
        print(f"  {RED}x{RESET} {msg}")
    print(f"\n  {AMBER}{done} of {len(picks)} done.{RESET}\n")
    return 0 if done else 1


def demo():
    assert len(THINGS) >= 12, "the list has to be long enough to be funny"
    assert all(t and w for t, w in THINGS), "every thing needs a reason"
    # The joke, asserted: nothing on the list of things you can do can be done.
    assert not any(attempt(i)[0] for i in range(len(THINGS))), "nothing may succeed"
    assert main(["--all"]) == 1, "--all must exit nonzero, since nothing worked"
    assert main([]) == 0, "the listing itself is allowed to work"
    # the pairs that only land next to each other
    pairs = [("speak to a person", "you are speaking to a person"),
             ("disagree with the terms", "by continuing you agree to the terms")]
    for thing, why in pairs:
        assert (thing, why) in THINGS, f"lost the pair: {thing}"
    print(f"ok: {len(THINGS)} things, 0 doable, --all exits 1")


if __name__ == "__main__":
    if "--check" in sys.argv:
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            demo()
        print(buf.getvalue().strip().splitlines()[-1])
    else:
        sys.exit(main(sys.argv[1:]))
