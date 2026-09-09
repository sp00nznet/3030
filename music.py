#!/usr/bin/env python3
"""Writes virus.mid -- the act-3 bassline, as a real MIDI file.

    python music.py            -> virus.mid
    python music.py --check    self-check

ponytail: a .mid is 60 lines of struct.pack. A MIDI library is a dependency
for a file format that was finished in 1983 and never moved again.
The riff is imported from virus.py so there is one copy of it.

The notes are ORIGINAL -- four of them, written to sound like a shareware
installer. Not a transcription of the Automator's instrumental, and not
meant to stand in for it. See the Notice in README.md.
"""
import math
import os
import struct
import sys

from virus import RIFF  # (hz, ms) -- single source of truth

BARS = 8
PPQ = 1000            # ticks per quarter
TEMPO = 1_000_000     # us per quarter -> 1 tick == 1 ms, so RIFF ms ARE ticks
BASS_PROG = 38        # GM 39 "Synth Bass 1", zero-based
NAME = b"DELTRON 3030 // VIRUS v3030.1"


def note(hz):
    """Hz -> MIDI note number. 98Hz -> 43 (G2)."""
    return max(0, min(127, round(69 + 12 * math.log2(hz / 440.0))))


def vlq(n):
    """MIDI variable-length quantity."""
    out = bytearray([n & 0x7F])
    n >>= 7
    while n:
        out.append((n & 0x7F) | 0x80)
        n >>= 7
    return bytes(reversed(out))


def chunk(events):
    """events: list of (delta_ticks, payload) -> one MTrk chunk."""
    body = b"".join(vlq(d) + p for d, p in events)
    body += vlq(0) + b"\xff\x2f\x00"  # end of track
    return b"MTrk" + struct.pack(">I", len(body)) + body


def tempo_track():
    return [(0, b"\xff\x51\x03" + struct.pack(">I", TEMPO)[1:]),
            (0, b"\xff\x03" + bytes([len(NAME)]) + NAME)]


def bass_track():
    ev, wait = [(0, bytes([0xC0, BASS_PROG]))], 0
    for _ in range(BARS):
        for hz, ms in RIFF:
            if not hz:
                wait += ms  # rest: carry the delta to the next real event
                continue
            n = note(hz)
            ev.append((wait, bytes([0x90, n, 100])))
            ev.append((ms, bytes([0x80, n, 0])))
            wait = 0
    return ev


def drum_track():
    """4-on-the-floor kick, snare on 2 and 4, over the riff's own cycle."""
    step = sum(ms for _, ms in RIFF) // 4
    ev = []
    for _ in range(BARS):
        for i in range(4):
            hits = [36] + ([38] if i % 2 else [])   # kick, +snare on 2 & 4
            for h in hits:
                ev.append((0, bytes([0x99, h, 90 if h == 36 else 70])))
            ev.append((step, bytes([0x89, hits[0], 0])))
            for h in hits[1:]:
                ev.append((0, bytes([0x89, h, 0])))
    return ev


def build():
    return (b"MThd" + struct.pack(">IHHH", 6, 1, 3, PPQ)
            + chunk(tempo_track()) + chunk(bass_track()) + chunk(drum_track()))


def write(path="virus.mid"):
    data = build()
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def demo():
    assert note(98) == 43, "G2 should be MIDI 43"
    assert note(440) == 69, "A4 should be MIDI 69"
    assert vlq(0) == b"\x00" and vlq(128) == b"\x81\x00", "bad varlen encoding"
    d = build()
    assert d[:4] == b"MThd" and d.count(b"MTrk") == 3, "not a 3-track format-1 file"
    beats = sum(ms for _, ms in RIFF) * BARS
    assert 5000 < beats < 60000, f"riff is {beats}ms, that is not a song"
    print(f"ok: {len(d)} bytes, 3 tracks, {beats / 1000:.1f}s")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        n = write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "virus.mid"))
        print(f"wrote virus.mid ({n} bytes)")
