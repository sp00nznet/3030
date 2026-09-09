# VIRUS v3030.1

A joke. Implements the Deltron 3030 track "Virus" as literally as is legal,
possible, and funny — in that order.

The bit: the honest implementation of the entire verse is one `print()`.
We are going to write four hundred lines instead.

## Safety rails

Non-negotiable. They are the reason it's funny instead of a conversation
with someone's IT department.

- No writes outside this repo. None.
- No self-replication. The folder bomb is **rendered, not executed**.
- No network. No subprocess. No registry, no startup, no persistence.
- Only syscall that touches the machine: `os.listdir('.')` for flavor text.
- `finally:` restores the terminal on Ctrl-C, always.
- Exit 0. Nothing to clean up, because nothing was made.

## Feasibility triage (the source material)

Everything Del asks for, and what it actually is:

| Lyric | Verdict |
|---|---|
| "bring dire straits to your environment" | mood, not a spec |
| "revert you to papyrus" | closest real behavior is *paperweight*. off by one material |
| "no Microsoft or Windows when I'm through" | cannot uninstall a corporation |
| "a file gets deleted / Bingo! hard drive" | this is `del`. shipped 1981. Del invented Del |
| "delete your text like so much white out" | duplicate of above |
| "shut down the entire whitehouse" | air-gapped |
| "corrupt politicians" | no-op, idempotent |
| "even space stations" | 400ms RTT, custom RTOS, they'd notice |
| "3030" | one thousand years of forward compat. a millennium LTS |

Only **file replication** describes a real mechanism. Win95 folder bomb —
not clever, just `mkdir` in a loop until Explorer gave up. So that's the
one we perform, and we perform it as theater.

## Four acts

### 1. BOOT
ANSI green on black, `\033[2J`, hide cursor. Fake POST. Banner:
`DELTRON 3030 // VIRUS v3030.1 // AUTOMATOR ON THE BOARDS`.
Typewriter effect: `sys.stdout.write` + `time.sleep`, ~40 chars/sec.

### 2. NOISE
The triage table, delivered as scrolling log lines. The impossible
requirements fail one by one, deadpan:

```
[SKIP] whitehouse.gov ......... air-gapped
[NOOP] politicians ............ already corrupt
[FAIL] space-station-01 ....... timeout (400ms RTT)
[DUPE] whiteout.exe ........... see: del (1981)
[HELD] microsoft .............. cannot uninstall a corporation
```

Funniest act, and it's a list of strings.

### 3. BOMB
The one real mechanism, faked. Counter climbs, path gets absurd, nothing
is created:

```
SPAWNING  ./scrolls/scrolls/scrolls/          [    1 ]
SPAWNING  ./scrolls/scrolls/scrolls/scrolls/  [    2 ]
SPAWNING  ./scrolls/x2047/                    [ 2047 ]
DISK: 100% PAPYRUS
```

Path collapses to `xN` notation once it outgrows the terminal width
(`shutil.get_terminal_size`). Accelerating delay — starts slow, ends in a blur.

### 4. PAPYRUS
Screen fills with `~` from the bottom up, row by row, until every cell is
papyrus. Then the lyrics scroll down the reed. End state: your terminal is
a scroll.

## Audio

`winsound.Beep(freq, ms)` on a daemon thread, under the typewriter.
Four-note bassline, ~90bpm. Stdlib, Windows, zero deps. Sounds like a 1997
shareware installer, which is the joke.

`--mute` flag. Non-Windows: import fails, audio silently off, everything
else runs.

## Layout

```
virus.py      everything
lyrics.txt    the verse, so timing is tunable without touching code
SPEC.md       this
```

Three files. Stdlib only.

## Check

`demo()` under `__main__`, run with `--fast` (all sleeps zeroed): asserts
all four acts run end to end and the terminal is restored. One assert per
act. No framework.

## Non-goals

- MIDI. Add when it needs to leave the machine (~40 lines of `struct.pack`,
  still no deps, but then it needs a player and it's a two-file problem).
- Packaging, `.exe`, installer.
- curses. ANSI is enough.
- Any actual virus behavior. Obviously.
- Going public with full lyrics in the repo. Strip them first if it ever does.
