#!/usr/bin/env python3
"""Renders the README images with termshot -- github.com/sp00nznet/termshot

    pip install pillow
    TERMSHOT=/path/to/termshot python docs/demos.py [name ...]

One function per image, named for what it makes. No arguments makes all of
them. ponytail: a real recorder would produce megabytes of GIF for programs
that run for 45 seconds; termshot fakes it at ~40KB each, and faking a demo
of programs that are themselves fakes is the honest option.

Not every track gets one. slipping's joke is five minutes long and a GIF
cannot hold it; y3k prints a static report that reads better as text in the
README than as a picture of text.
"""
import os
import sys

sys.path.insert(0, os.environ.get("TERMSHOT", "."))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mastermind as mm  # noqa: E402  -- the demo scores with the real scorer
from termshot import CYAN, DIM, FG, GREEN, RED, YELLOW, Term  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
WHITE = (240, 244, 250)   # termshot ships no WHITE; FG is a touch grey
REED = (196, 164, 110)   # papyrus
INK = (120, 92, 52)
BLUE = (96, 160, 232)
TAN = (200, 170, 120)
# One colour per mastermind glyph, matching mastermind.py's INK table.
GLYPH = {1: (232, 116, 110), 2: (224, 160, 72), 3: (224, 196, 96),
         4: (126, 211, 126), 5: (108, 196, 214), 6: (188, 140, 230)}

# Windows has no DejaVu; Consolas is the same shape of font.
FONTS = {"win32": ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/consolab.ttf")}
_reg, _bold = FONTS.get(sys.platform, (None, None))
_KW = {"reg": _reg, "bold": _bold} if _reg and os.path.exists(_reg) else {}


def term(title, rows):
    return Term(title=title, user="del@3030", cwd="~/3030", rows=rows, **_KW)


def save(t, name):
    # ponytail: GIF only. save_png exists, but a still nothing links to is cruft.
    t.save_gif(os.path.join(OUT, name + ".gif"))
    print("wrote", name)


def glyphs(digits, pad="  "):
    """'3416' -> coloured segments, the way mastermind.py renders a guess."""
    segs = []
    for d in digits:
        segs.append((d + " ", GLYPH[int(d)], True))
    return [(pad, FG, False)] + segs


# --------------------------------------------------------------------------
def tracklist():
    """The hero image: the album, as a menu."""
    t = term("3030", 20)
    t.type("deltron")
    t.reveal([
        None,
        [("  DELTRON 3030", WHITE, True), ("  // the album, as command-line programs", DIM, False)],
        None,
        [("   2.  ", DIM, False), ("y3k         ", WHITE, True), ("3030", FG, False)],
        [("       a Y3K compliance checker. The only one that does something real", DIM, False)],
        [("   7.  ", DIM, False), ("virus       ", WHITE, True), ("Virus", FG, False)],
        [("       a threat that cannot be carried out", DIM, False)],
        [("  10.  ", DIM, False), ("mastermind  ", WHITE, True), ("Mastermind", FG, False)],
        [("       a lock, ten tries. The one that keeps score", DIM, False)],
        [("  14.  ", DIM, False), ("slipping    ", WHITE, True), ("Time Keeps On Slipping", FG, False)],
        [("       a clock that is correct for about a minute", DIM, False)],
        [("  16.  ", DIM, False), ("turbulence  ", WHITE, True), ("Turbulence", FG, False)],
        [("       a route to the tower, degrading. It reaches nothing", DIM, False)],
        [("   8.  ", DIM, False), ("upgrade     ", WHITE, True), ("Upgrade (A Brymar College Course)", FG, False)],
        [("       a promise kept to the letter, meaning nothing", DIM, False)],
    ], 220)
    t.blink()
    save(t, "tracklist")


def virus():
    t = term("virus — 3030", 23)
    t.type("deltron virus")
    t.reveal([
        [("  +----------------------------------------------+", GREEN, False)],
        [("  |  DELTRON 3030  //  VIRUS v3030.1             |", GREEN, True)],
        [("  |  it is 3030. this program does nothing.      |", GREEN, False)],
        [("  +----------------------------------------------+", GREEN, False)],
    ], 260)
    t.reveal([
        None,
        [("  [SKIP] ", DIM, False), ("whitehouse.gov", FG, False), ("  ......  air-gapped", DIM, False)],
        [("  [NOOP] ", DIM, False), ("politicians", FG, False), ("     ......  already corrupt", DIM, False)],
        [("  [FAIL] ", RED, True), ("space-station-01", FG, False), ("  ...  timeout (400ms RTT)", DIM, False)],
        [("  [DUPE] ", DIM, False), ("whiteout.exe", FG, False), ("    ......  see: del (1981)", DIM, False)],
        [("  [HELD] ", YELLOW, True), ("microsoft", FG, False), ("       ......  cannot uninstall a corporation", DIM, False)],
    ], 300)
    t.blank(200)
    t.reveal([
        [("  SPAWNING  ./scrolls/scrolls/scrolls/       [    3 ]", CYAN, False)],
        [("  SPAWNING  ./scrolls/scrolls/scrolls/scr…   [    4 ]", CYAN, False)],
        [("  SPAWNING  ./scrolls/x412/                  [  412 ]", CYAN, False)],
        [("  SPAWNING  ./scrolls/x2047/                 [ 2047 ]", CYAN, False)],
        [("  DISK: 100% PAPYRUS", GREEN, True)],
    ], 160)
    t.blank(200)
    t.reveal([
        [("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", REED, False)],
        [("  ~  crash your whole computer system            ~", INK, True)],
        [("  ~      and revert you to papyrus               ~", INK, True)],
        [("  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", REED, False)],
    ], 420)
    t.hold(1800)
    t.blink()
    save(t, "virus")


def mastermind():
    """The only one where you watch a loop rather than a payoff."""
    t = term("mastermind — 3030", 22)
    t.type("deltron mastermind")
    t.reveal([
        None,
        [("  BREACH", WHITE, True), ("  // corporate tower, sublevel 4", DIM, False)],
        [("  glyphs: ", DIM, False)] + glyphs("123456", "")[1:]
        + [("  <- only these. 4 of them, repeats allowed", DIM, False)],
        [("  10 attempts.  # = right slot   + = right glyph, wrong slot", DIM, False)],
        None,
    ], 280)
    # Feedback comes from the real scorer, not from me typing plausible numbers.
    # A demo of a deduction game that shows impossible feedback is worse than
    # no demo: the first person to check it finds the game "broken".
    secret = (4, 4, 2, 6)
    for i, guess in enumerate(["1234", "4123", "4216", "4426"]):
        exact, displaced = mm.score(secret, tuple(int(c) for c in guess))
        won = exact == mm.SLOTS
        left = 10 - i
        t.out([(f"  [{left:>2} left]", DIM, False), (" > ", FG, False), (guess, FG, False)], 500)
        row = glyphs(guess, "       ") + [("  [", FG, False),
                                          (mm.bar(exact, displaced), GREEN if won else FG, True),
                                          ("]  ", FG, False)]
        if not won:
            row.append((f"{exact} exact, {displaced} displaced", DIM, False))
        t.out(row, 700)
    t.reveal([
        None,
        [("  The lock opens.", GREEN, True), ("  4 attempts.", DIM, False)],
        [("  You are the mastermind.", WHITE, True)],
    ], 600)
    t.hold(1600)
    t.blink()
    save(t, "mastermind")


def turbulence():
    """Redraws the table in place, so add() drives whole frames."""
    t = term("turbulence — 3030", 16)
    t.type("deltron turbulence")

    def table(rows, phase, ink, secs):
        out = [None,
               [("  TURBULENCE", WHITE, True), ("  // route to mothership.3030", DIM, False)],
               [("  simulated. nothing is sent, nothing is resolved", DIM, False)],
               None,
               [("  HOP  HOST                     LOSS      LAST", DIM, False)]]
        for i, (host, loss, last) in enumerate(rows, 1):
            lk = RED if loss > 40 else YELLOW if loss > 5 else GREEN
            out.append([(f"  {i:>3}  ", DIM, False), (f"{host:<22} ", FG, False),
                        (f"{loss:5.1f}%", lk, False), ("  ", FG, False),
                        (last, RED if "*" in last else FG, False)])
        out += [None, [("  " + phase, ink, True), (f"   t+{secs:>4.0f}s", DIM, False)]]
        return out

    frames = [
        ([("local.3030", 0.2, "    1.1ms"), ("gw-oakland.3030", 0.3, "   12.2ms")],
         "clear", GREEN, 2),
        ([("local.3030", 3.0, "    1.4ms"), ("gw-oakland.3030", 6.6, "   17.5ms"),
          ("ubiq-relay-04.3030", 9.4, "   46.9ms"), ("tower-07.corp.3030", 9.8, "  127.5ms"),
          ("sublevel-4.corp.3030", 11.2, "  215.2ms"), ("mothership.3030", 17.2, "    * * *")],
         "turbulence", YELLOW, 12),
        ([("local.3030", 10.8, "    2.1ms"), ("gw-oakland.3030", 12.8, "   20.4ms"),
          ("ubiq-relay-04.3030", 30.2, "   63.9ms"), ("tower-07.corp.3030", 39.5, "  150.6ms"),
          ("relay-null-9.3030", 47.6, "  568.6ms"), ("sublevel-4.corp.3030", 65.9, "  384.7ms"),
          ("mothership.3030", 61.0, "  525.8ms")],
         "route flapping", RED, 26),
        ([("local.3030", 14.1, "    1.9ms"), ("gw-oakland.3030", 32.2, "    * * *"),
          ("ubiq-relay-04.3030", 45.4, "    * * *"), ("tower-07.corp.3030", 44.6, "  179.6ms"),
          ("relay-null-9.3030", 71.0, "  673.9ms"), ("sublevel-4.corp.3030", 88.6, "    * * *"),
          ("mothership.3030", 76.5, "    * * *")],
         "no route", RED, 34),
    ]
    for rows, phase, ink, secs in frames:
        t.add(table(rows, phase, ink, secs), 1500)
    t.add([None,
           [("  PATH LOST.", RED, True)],
           [("  0 packets sent. 0 packets received. None of this happened.", DIM, False)],
           None], 2600)
    save(t, "turbulence")


def upgrade():
    """The ETA getting worse is the joke, so the bar has to move."""
    t = term("upgrade — 3030", 18)
    t.type("deltron upgrade")

    def screen(pct, eta, tail=None):
        fill = int(34 * pct / 100)
        bar = "#" * fill + "-" * (34 - fill)
        out = [None,
               [("  +--------------------------------------------+", BLUE, False)],
               [("  |  DELTRON 3030  //  UPGRADE                 |", BLUE, True)],
               [("  |  installed: v3030.1                        |", BLUE, False)],
               [("  +--------------------------------------------+", BLUE, False)],
               None,
               [("  Downloading v3030.2  [", FG, False), (bar, BLUE, False),
                ("] ", FG, False), (f"{pct:>3}%", FG, True),
                (f"   {eta}", DIM, False)]]
        if tail:
            out += [None] + tail
        return out

    for pct, eta in [(8, "12 min remaining"), (31, "18 min remaining"),
                     (46, "22 min remaining"), (67, "2 min remaining"),
                     (99, "less than a minute"), (99, "less than a minute")]:
        t.add(screen(pct, eta), 1100)
    t.add(screen(100, "done", [
        [("  [OK] Migrating config -> config (new format)", GREEN, False)],
        [("  [OK] Retiring: batch rename", YELLOW, False)],
        [("  [OK] This will only take a moment", GREEN, False)],
    ]), 1600)
    t.add([None,
           [("  UPGRADE COMPLETE", GREEN, True)],
           None,
           [("  version    ", DIM, False), ("             v3030.1  ->  v3030.2", FG, False)],
           [("  features   ", DIM, False), ("                  47  ->  46", FG, False)],
           [("  settings   ", DIM, False), (" where you left them  ->  reset", FG, False)],
           [("  icon       ", DIM, False), ("                fine  ->  flat", FG, False)],
           None,
           [("  0 files changed, 0 insertions(+), 0 deletions(-)", DIM, False)],
           None,
           [("  You are current.", WHITE, True)]], 3000)
    save(t, "upgrade")


ALL = {f.__name__: f for f in (tracklist, virus, mastermind, turbulence, upgrade)}

if __name__ == "__main__":
    names = sys.argv[1:] or list(ALL)
    for n in names:
        ALL[n]()
