#!/usr/bin/env python3
"""Writes one MIDI file per track, from the same cues the programs play.

    python music.py            -> midi/*.mid
    python music.py --check    self-check

ponytail: a .mid is sixty lines of struct.pack. A MIDI library is a
dependency for a file format that was finished in 1983 and never moved again.

The notes live in audio.py and are imported, not copied, so a cue and its
.mid can never drift apart. Every riff is original -- see the Notice in
README.md.
"""
import math
import os
import struct
import sys

from audio import RIFFS

PPQ = 1000            # ticks per quarter
TEMPO = 1_000_000     # us per quarter -> 1 tick == 1 ms, so cue ms ARE ticks
BARS = 4              # loops per file, so a .mid is long enough to be a loop

# General MIDI program per track, chosen to suit the cue. Zero-based.
VOICES = {
    "virus": 38,        # synth bass 1
    "upgrade": 80,      # lead 1 (square)
    "things": 11,       # vibraphone
    "contact": 94,      # pad 7 (halo)
    "newcoke": 12,      # marimba
    "mastermind": 9,    # glockenspiel
    "madness": 102,     # fx 7 (echoes)
    "slipping": 89,     # pad 2 (warm)
    "news": 56,         # trumpet
    "turbulence": 87,   # lead 8 (bass + lead)
    "battlesong": 33,   # electric bass (finger)
    "memory": 8,        # celesta
    "y3k": 115,         # woodblock
}


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


def tempo_track(name):
    label = name.encode()[:127]
    return [(0, b"\xff\x51\x03" + struct.pack(">I", TEMPO)[1:]),
            (0, b"\xff\x03" + bytes([len(label)]) + label)]


def voice_track(riff, program, bars=BARS):
    ev, wait = [(0, bytes([0xC0, program]))], 0
    for _ in range(bars):
        for hz, ms in riff:
            if not hz:
                wait += ms          # a rest carries its delta to the next note
                continue
            n = note(hz)
            ev.append((wait, bytes([0x90, n, 100])))
            ev.append((ms, bytes([0x80, n, 0])))
            wait = 0
    return ev


def drum_track(riff, bars=BARS):
    """Four on the floor over the cue's own cycle, snare on 2 and 4."""
    cycle = sum(ms for _, ms in riff)
    step = max(1, cycle // 4)
    ev = []
    for _ in range(bars):
        for i in range(4):
            hits = [36] + ([38] if i % 2 else [])
            for h in hits:
                ev.append((0, bytes([0x99, h, 90 if h == 36 else 70])))
            ev.append((step, bytes([0x89, hits[0], 0])))
            for h in hits[1:]:
                ev.append((0, bytes([0x89, h, 0])))
    return ev


def build(name, drums=True):
    riff = RIFFS[name]
    tracks = [chunk(tempo_track(f"DELTRON 3030 // {name}")),
              chunk(voice_track(riff, VOICES.get(name, 80)))]
    if drums:
        tracks.append(chunk(drum_track(riff)))
    head = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), PPQ)
    return head + b"".join(tracks)


def write_all(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for name in sorted(RIFFS):
        # The sparse cues get no drum track; a beat under them ruins them.
        drums = name not in ("contact", "y3k", "slipping", "memory")
        data = build(name, drums=drums)
        path = os.path.join(out_dir, name + ".mid")
        with open(path, "wb") as f:
            f.write(data)
        written.append((name, len(data)))
    return written


def demo():
    assert note(98) == 43, "G2 should be MIDI 43"
    assert note(440) == 69, "A4 should be MIDI 69"
    assert vlq(0) == b"\x00" and vlq(128) == b"\x81\x00", "bad varlen encoding"
    assert set(VOICES) == set(RIFFS), "every cue needs a voice, and vice versa"
    assert all(0 <= p <= 127 for p in VOICES.values()), "GM programs are 0-127"
    for name in RIFFS:
        d = build(name)
        assert d[:4] == b"MThd", f"{name}: not a MIDI file"
        assert d.count(b"MTrk") == 3, f"{name}: expected 3 chunks"
        assert len(d) > 60, f"{name}: suspiciously small"
    solo = build("contact", drums=False)
    assert solo.count(b"MTrk") == 2, "drums must be droppable"
    print(f"ok: {len(RIFFS)} tracks, format 1, notes shared with audio.py")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        out = os.path.join(here, "midi")
        for name, n in write_all(out):
            print(f"  midi/{name}.mid  {n:,} bytes")
