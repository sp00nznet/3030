#!/usr/bin/env python3
"""TURBULENCE -- Deltron 3030, track 16. See SPEC.md.

A route to the tower, degrading in front of you. Latency climbs, hops start
starring out, the path flaps between two routes that are both wrong, and then
there is no route at all.

    python turbulence.py             ~35s to total loss
    python turbulence.py --speed 4   four times faster
    python turbulence.py --seed 7    the same bad weather every time
    python turbulence.py --check     self-check

It reaches nothing. There are no sockets in this file and the hosts are on a
TLD that does not exist, because a convincing fake network tool is a much
worse idea than a convincing fake virus. The self-check asserts both.
"""
import random
import sys
import time
import types

import audio
from theater import CLEAR, EOL, ESC, HIDE, HOME, RESET, nap, restore, w

DIM = ESC + "38;5;245m"
WHITE = ESC + "38;5;255m"
OK = ESC + "38;5;42m"
WARN = ESC + "38;5;214m"
BAD = ESC + "38;5;203m"

# .3030 is not a TLD and never will be. Nothing here can resolve.
HOPS = [
    ("local.3030", 1.1),
    ("gw-oakland.3030", 8.4),
    ("ubiq-relay-04.3030", 21.0),
    ("tower-07.corp.3030", 44.5),
    ("sublevel-4.corp.3030", 61.2),
    ("mothership.3030", 88.9),
]
# The flap: from ~24s the path alternates with a longer, worse one.
DETOUR = ("relay-null-9.3030", 132.0)

PHASES = [(0, "clear", OK), (8, "turbulence", WARN), (16, "severe", WARN),
          (24, "route flapping", BAD), (32, "no route", BAD)]
LOST_AT = 35.0


def phase(t):
    name, ink = PHASES[0][1], PHASES[0][2]
    for at, n, i in PHASES:
        if t >= at:
            name, ink = n, i
    return name, ink


def weather(t):
    """0.0 calm -> 1.0 gone. Everything else is derived from this."""
    return min(1.0, max(0.0, t / LOST_AT))


def snapshot(t, seed=0):
    """Pure: the table at t seconds, and whether the path is gone.

    Pure so the self-check can jump to total loss without waiting 35 seconds
    for it -- the same trick slipping.py uses for frame().
    """
    bad = weather(t)
    rows, hops = [], list(HOPS)
    if 24 <= t and int(t / 2) % 2:           # the flap, on alternate 2s windows
        hops.insert(4, DETOUR)
    visible = len(hops) if t > 5 else max(1, int(t / 0.9))   # discovery
    for i, (host, base) in enumerate(hops[:visible], 1):
        rng = random.Random(seed * 100003 + int(t * 4) * 97 + i)
        depth = i / len(hops)                # later hops suffer more
        loss = min(100.0, 100.0 * bad ** 1.6 * depth * rng.uniform(0.7, 1.3))
        dead = rng.random() < bad * depth    # a hop that answers nothing
        last = None if dead else base * (1 + 6 * bad * depth) * rng.uniform(0.9, 1.4)
        rows.append((i, host, loss, last))
    return rows, t >= LOST_AT


def render(t, seed):
    rows, done = snapshot(t, seed)
    name, ink = phase(t)
    out = ["",
           f"  {WHITE}TURBULENCE{RESET}  {DIM}// route to mothership.3030{RESET}",
           f"  {DIM}simulated. nothing is sent, nothing is resolved{RESET}",
           "",
           f"  {DIM}HOP  HOST                     LOSS      LAST{RESET}"]
    for i, host, loss, last in rows:
        lat = f"{last:7.1f}ms" if last is not None else f"{BAD}      * * *{RESET}"
        lk = BAD if loss > 40 else WARN if loss > 5 else OK
        out.append(f"  {DIM}{i:>3}{RESET}  {host:<22} {lk}{loss:5.1f}%{RESET}  {lat}")
    out += ["", f"  {ink}{name}{RESET}   {DIM}t+{t:>4.0f}s{RESET}", ""]
    return out, done


def main(speed=1.0, seed=0):
    audio.cue("turbulence")
    t0 = time.monotonic()
    try:
        w(CLEAR + HIDE)
        while True:
            t = (time.monotonic() - t0) * speed
            lines, done = render(t, seed)
            w(HOME + "\n".join(ln + EOL for ln in lines))
            if done:
                break
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        restore()
    w(f"  {BAD}PATH LOST.{RESET}\n")
    w(f"  {DIM}0 packets sent. 0 packets received. None of this happened.{RESET}\n\n")


def demo():
    # The important one: this program cannot reach anything.
    NET = {"socket", "ssl", "http", "urllib", "asyncio", "subprocess", "requests"}
    mine = {v.__name__.split(".")[0] for v in globals().values()
            if isinstance(v, types.ModuleType)}
    assert not (NET & mine), f"turbulence must not import {sorted(NET & mine)}"
    # Deliberately scoped to this module, not to sys.modules. Process-wide was
    # wrong twice: PyInstaller's bootloader imports urllib and subprocess, and
    # so does deltron.py, so the check failed in the binary and under the
    # umbrella while passing standalone. What matters is that *this file*
    # cannot reach the network, and that is what is asserted.
    assert all(h.endswith(".3030") for h, _ in HOPS + [DETOUR]), "hosts must be unresolvable"

    assert weather(0) == 0.0 and weather(LOST_AT) == 1.0, "weather runs 0 to 1"
    early, done = snapshot(1.0, seed=7)
    assert not done and len(early) < len(HOPS), "the path is still being discovered"
    assert all(loss < 1 for _, _, loss, _ in early), "no loss while it is clear"

    mid, _ = snapshot(12.0, seed=7)
    late, _ = snapshot(30.0, seed=7)
    assert len(mid) == len(HOPS), "all hops visible by then"
    assert (sum(l for _, _, l, _ in late) > sum(l for _, _, l, _ in mid)), "loss must worsen"
    assert any(lat is None for _, _, _, lat in late), "hops should start starring out"

    flapped = {tuple(h for _, h, _, _ in snapshot(t, seed=7)[0]) for t in (25.0, 27.0)}
    assert len(flapped) == 2, "the route must actually flap between two paths"
    assert snapshot(LOST_AT, seed=7)[1], "the path must be lost at the end"
    assert phase(0)[0] == "clear" and phase(33)[0] == "no route", "phases in order"
    print(f"ok: no network modules, {len(HOPS)} unresolvable hops, path lost at {LOST_AT:.0f}s")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        sp = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
        sd = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
        main(sp, sd)
