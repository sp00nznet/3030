"""Sound for the 3030 programs. Stdlib only, all three platforms.

winsound.Beep was Windows-only and could not do more than one note at a time,
so the album was silent everywhere else. This synthesises a WAV in memory with
`wave` and hands the bytes to whatever the platform has:

    Windows   winsound.PlaySound(..., SND_MEMORY)   -- no file at all
    Linux     aplay / paplay, WAV on stdin          -- no file at all
    macOS     afplay, which insists on a path       -- one temp file, deleted

If none of that works, everything falls silent and every program still runs.
A missing player is not an error; it is a quiet Tuesday.

Every riff is original, written to sound like cheap hardware from 1997. None
of it is transcribed from the record -- see the Notice in README.md.
"""
import array
import io
import math
import os
import sys
import threading
import wave

RATE = 22050
VOL = 0.26

# (hz, ms). 0 hz is a rest. One cue per track, each its own small idea.
RIFFS = {
    # low, four-note, the shareware-installer bassline the repo started with
    "virus": [(98, 200), (98, 200), (117, 160), (98, 200),
              (73, 260), (0, 120), (87, 200), (98, 320)],
    # ascending fanfare that resolves to the note it started on
    "upgrade": [(523, 120), (659, 120), (784, 160), (523, 320)],
    # two notes, down. The sound of a door not opening
    "things": [(330, 110), (247, 260), (0, 160)],
    # a beacon: sparse, high, patient, and nobody answers
    "contact": [(880, 90), (0, 300), (880, 90), (0, 300), (1175, 90), (0, 500)],
    # a jingle that plays itself twice because it tested well
    "newcoke": [(392, 140), (494, 140), (587, 200), (0, 100),
                (392, 140), (494, 140), (587, 200)],
    # tumblers falling, one at a time
    "mastermind": [(262, 110), (330, 110), (392, 110), (523, 260)],
    # never resolves, on purpose
    "madness": [(415, 90), (622, 90), (466, 90), (740, 90),
                (440, 90), (587, 90), (494, 200)],
    # slows and sags as it goes
    "slipping": [(440, 120), (438, 150), (432, 200), (415, 280), (370, 420)],
    # three-note news sting
    "news": [(587, 130), (784, 130), (988, 300)],
    # descending, losing altitude
    "turbulence": [(494, 140), (440, 140), (392, 160), (349, 200), (294, 420)],
    # two motifs trading, one clearly better
    "battlesong": [(196, 150), (392, 150), (196, 150), (494, 150),
                   (196, 150), (587, 300)],
    # the phrase loses a note each time it comes round
    "memory": [(523, 140), (494, 140), (440, 140), (392, 300), (0, 120),
               (523, 140), (494, 140), (440, 300), (0, 120),
               (523, 140), (494, 300), (0, 120), (523, 400)],
    # a clock tick that is not quite regular
    "y3k": [(1047, 60), (0, 440), (1047, 60), (0, 430), (1047, 60), (0, 450)],
}


def samples(freq, ms):
    """One note, with a short attack and release so it does not click."""
    n = int(RATE * ms / 1000)
    if not freq:
        return array.array("h", bytes(2 * n))
    atk, rel = max(1, int(RATE * 0.006)), max(1, int(RATE * 0.03))
    step = 2 * math.pi * freq / RATE
    out = array.array("h", bytes(2 * n))
    for i in range(n):
        env = min(1.0, i / atk, (n - i) / rel)
        out[i] = int(32767 * VOL * env * math.sin(step * i))
    return out


def wav_bytes(notes, loops=1):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(RATE)
        one = array.array("h")
        for freq, ms in notes:
            one.extend(samples(freq, ms))
        for _ in range(loops):
            f.writeframes(one.tobytes())
    return buf.getvalue()


def _play_bytes(data):
    """True if something actually made a sound."""
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(data, winsound.SND_MEMORY)
        return True
    import subprocess
    if sys.platform == "darwin":
        # afplay cannot read stdin, so this is the one temp file in the repo.
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            subprocess.run(["afplay", path], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    for cmd in (["aplay", "-q", "-"], ["paplay", "-"], ["play", "-q", "-"]):
        try:
            subprocess.run(cmd, input=data, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (OSError, subprocess.SubprocessError):
            continue
    return False


def play(name, loops=1, block=False):
    """Play a track's cue. Never raises, never blocks unless asked."""
    notes = RIFFS.get(name)
    if not notes:
        return False
    def go():
        try:
            _play_bytes(wav_bytes(notes, loops))
        except Exception:
            pass          # no player, no device, no sound card: stay quiet
    if block:
        go()
        return True
    threading.Thread(target=go, daemon=True).start()
    return True


def cue(name, loops=1):
    """What the tracks call. Decides on its own whether sound is wanted.

    Silent when muted, when sleeps are off, and whenever stdout is not a
    terminal -- so piping, redirecting, CI and the self-checks never make a
    noise, and no track has to remember any of that.
    """
    if "--mute" in sys.argv or "--fast" in sys.argv:
        return False
    try:
        if not sys.stdout.isatty():
            return False
    except (AttributeError, ValueError):
        return False
    return play(name, loops)


def demo():
    assert len(RIFFS) >= 13, f"a cue per track, got {len(RIFFS)}"
    for name, notes in RIFFS.items():
        assert notes, f"{name} has no notes"
        assert all(f == 0 or 40 <= f <= 12000 for f, _ in notes), f"{name}: bad pitch"
        assert all(10 <= ms <= 2000 for _, ms in notes), f"{name}: bad duration"
    # The riffs the tracks are named for must keep their shape.
    assert RIFFS["upgrade"][0][0] == RIFFS["upgrade"][-1][0], \
        "the upgrade fanfare must end where it started"
    assert [f for f, _ in RIFFS["turbulence"]] == \
        sorted((f for f, _ in RIFFS["turbulence"]), reverse=True), \
        "turbulence must only descend"

    data = wav_bytes(RIFFS["news"])
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE", "not a WAV"
    with wave.open(io.BytesIO(data)) as f:
        assert f.getframerate() == RATE and f.getsampwidth() == 2, "wrong format"
        secs = f.getnframes() / RATE
    want = sum(ms for _, ms in RIFFS["news"]) / 1000
    assert abs(secs - want) < 0.02, f"news cue is {secs:.2f}s, expected {want:.2f}s"
    assert len(wav_bytes(RIFFS["news"], loops=3)) > len(data) * 2.5, "loops must repeat"
    assert play("nope") is False, "an unknown cue must be silent, not an error"
    # cue() must stay silent wherever a noise would be unwelcome
    assert cue("news") is False, "no sound when stdout is not a terminal"
    print(f"ok: {len(RIFFS)} cues, WAV synthesis, {sys.platform} playback path")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        which = [a for a in sys.argv[1:] if not a.startswith("-")]
        for name in which or sorted(RIFFS):
            print(f"  {name}")
            play(name, block=True)
