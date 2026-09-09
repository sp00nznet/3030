# VIRUS v3030.1

> _"I want to devise a virus / to bring dire straits to your environment /
> crash your whole computer system / and revert you to papyrus"_
> — Deltron 3030, _Virus_ (2000)

Somebody had to try. This is that verse, implemented as literally as is
legal, possible, and funny — in that order.

![demo](docs/demo.gif)

It does **nothing** to your computer. That's the joke: the honest
implementation of the entire verse is one `print()`, and this is four
hundred lines instead.

## Run

```bash
python virus.py            # the full bit, ~45s, bassline on
python virus.py --fast     # no sleeps, watch it in two seconds
python virus.py --mute     # no bassline
python virus.py --check    # self-check: all four acts, terminal restored
```

Stdlib only. Python 3.8+. No pip install, no venv, nothing to uninstall.

## The spec review

Before writing it we triaged the requirements. The client is Del. The spec
is a rap verse.

| Requirement | Verdict |
|---|---|
| "bring dire straits to your environment" | a mood, not a spec |
| "revert you to papyrus" | closest real behavior is *paperweight*. off by one material |
| "no Microsoft or Windows when I'm through" | you cannot uninstall a corporation |
| "a file gets deleted / Bingo! hard drive" | this is `del`. shipped 1981. **Del invented Del** |
| "delete your text like so much white out" | duplicate of the above |
| "shut down the entire whitehouse" | air-gapped |
| "corrupt politicians" | no-op, idempotent |
| "even space stations" | 400ms RTT, custom RTOS, they'd notice |
| "3030" | a thousand years of forward compat. a millennium LTS |

Exactly one line in the verse describes a real mechanism: **replication**.
The Win95 folder bomb — not clever, just `mkdir` in a loop until Explorer
gave up. So that's the one we perform, and we perform it as theater.

## What it actually does

Four acts, in `virus.py`:

1. **BOOT** — ANSI green, fake POST, banner.
2. **NOISE** — the table above, as scrolling log lines, failing deadpan.
3. **BOMB** — the folder bomb, **rendered, not executed**. The counter climbs
   to 2047, the path collapses to `./scrolls/x2047/` once it outgrows your
   terminal, and your disk is exactly where it was.
4. **PAPYRUS** — the screen fills with `~` from the bottom up until every
   cell is reed, then the lyrics scroll down it. Your terminal is a scroll.

### The safety rails, since the repo is called `virus`

- No writes outside this repo. **None.** Nothing is created, so there is
  nothing to clean up.
- No self-replication. Ever. Act 3 is `print()` in a loop.
- No network, no subprocess, no registry, no startup entry, no persistence.
- The only syscall that touches your machine is one `os.listdir('.')`, for
  a flavor line that counts files it will not open.
- `finally:` restores your cursor and colors on Ctrl-C. Always.
- `python virus.py --check` asserts all of it and prints
  `ok: 4 acts, terminal restored, 0 files harmed`.

## The bassline

`winsound.Beep` on a daemon thread — a four-note riff at 90bpm that sounds
like a 1997 shareware installer, which is the correct sound for this. Windows
only; elsewhere the import fails, audio goes quiet, everything else runs.

`music.py` writes the same riff out as **`virus.mid`** (bass + drums, 13
seconds, 1 KB), so you can loop it in anything:

```bash
python music.py            # -> virus.mid
```

Hand-rolled `struct.pack`, no MIDI library. The riff lives in `virus.py` and
`music.py` imports it, so there is one copy of the notes.

## Binaries

PyInstaller can't cross-compile, so `.github/workflows/build.yml` builds on
one runner per platform and uploads `virus` / `virus.exe` on any `v*` tag.
The mac build is unsigned — right-click → Open the first time, or
`xattr -d com.apple.quarantine virus`.

You don't need any of that: `virus.py` is stdlib-only with a shebang, so
`chmod +x virus.py && ./virus.py` already works everywhere.

## Files

```
virus.py      the whole program
music.py      writes virus.mid
lyrics.txt    the verse. act 4 scrolls whatever is in here
SPEC.md       what we decided before writing it
docs/demo.py  makes the GIF above, with termshot
```

The GIF is not a screen recording — it's [termshot](https://github.com/sp00nznet/termshot),
which fakes terminal captures with Pillow. Faking a demo of a fake virus felt
correct.

`lyrics.txt` ships a four-line excerpt on purpose. Paste the rest in
yourself; act 4 reads the file, not the code.

## Other tracks

The album, not the track. Same repo, one file per song.

**`upgrade.py`** — _Upgrade (A Brand New Day)_. An upgrade process that is
flawless, thorough, patient, beautifully instrumented, and changes nothing. It
downloads nothing, migrates config into itself, restarts into the identical
screen, and reports success. The version goes up, the feature count goes down,
and the last line is `0 files changed` — which is a true statement about the
program, not a bit.

```bash
python upgrade.py             # the full bit, ~40s
python upgrade.py --rollback  # the truest line in the program
```

`virus.py` is a threat that cannot be carried out. `upgrade.py` is a promise
kept to the letter that means nothing. Same joke from the other end.

Planned, in [SPEC.md](SPEC.md): a Y3K compliance checker (_3030_), a clock that
drifts (_Time Keeps On Slipping_), the code-breaking game (_Mastermind_).

## Credit

Deltron 3030 — Del the Funky Homosapien, Dan the Automator, Kid Koala.
Go buy the album. It's better than this.

## Notice

An unofficial, non-commercial fan project. Not affiliated with, endorsed by,
or connected to Deltron 3030, Del the Funky Homosapien, Dan the Automator,
Kid Koala, or their labels. Made as homage, by someone who thinks a 2000
concept album about a mech soldier rap battling through a corporate dystopia
is one of the best records ever built.

- **The lyrics** are a four-line excerpt, quoted with attribution, in a
  project that exists to comment on those four lines. Rights remain with
  their owners. Don't paste the full verse into the repo.
- **The music is original.** `RIFF` is four notes written to sound like a
  1997 shareware installer. It is not a transcription of, sample of, or
  derivative of the album's instrumental.
- **The code** is free to take. The song isn't ours to give.

## License

MIT for everything in this repo — code, `virus.mid`, docs. See [LICENSE](LICENSE),
which carves out the quoted lyrics: those aren't ours to license to you.
