# UPGRADE (A Brand New Day)

Track 12. The sibling to `virus.py`.

An upgrade process that is flawless, thorough, patient, beautifully
instrumented — and changes nothing. It downloads nothing, installs nothing,
migrates nothing into itself, restarts into the identical screen, and reports
success. The version number goes up. That is the entire delta.

`virus.py` is a threat that can't be carried out. `upgrade.py` is a promise
that is kept to the letter and means nothing. Same joke from the other end.

## Safety rails

Same as `virus.py`, and for the same reason.

- No writes. Nothing is downloaded, installed, migrated, or backed up.
- No network. The "download" is `time.sleep` and a progress bar.
- **No package manager. Ever.** No `subprocess`, no `pip`, no `winget`, no
  `apt`. It never touches a real upgrade path, because a joke that shells out
  to a package manager is not a joke.
- `finally:` restores the terminal on Ctrl-C.
- The closing summary literally reads `0 files changed`, and that is a true
  statement about the program, not a bit.

## Source material

The track is about the upgrade treadmill: a brand new day that is the same
day. Everything below is a real thing software does, played straight.

| The move | How it renders |
|---|---|
| A changelog of filler | "Improved performance." "Various bug fixes." |
| The rename | `Settings` becomes `Preferences`. Then: "New: Preferences" |
| The quiet removal | one feature retires. It's the one you used |
| The ETA that grows | 12 min remaining -> 18 min -> 2 min -> stall at 99% |
| The flattened icon | it was fine |
| Migration into itself | `config -> config (new format)` |
| The reset | your settings are not where you left them |

## Four acts

### 1. CHECK
"Checking for updates..." Beat. `v3030.2 available (v3030.1 installed)`.
Prints the changelog — six lines of filler, deadpan, no punchline delivery.
Ends on `Removed: [one feature]` sitting quietly among the improvements.

### 2. DOWNLOAD
Block-char progress bar. The gag is the ETA, and it must be a **data table,
not clever code** — a hand-authored `[(pct, eta_text), ...]` so the timing
lands the same way every run:

```
  Downloading v3030.2  [########################----------]  71%   18 min remaining
```

Crosses 99% and sits there. The size is in units nobody asked for.

### 3. MIGRATE
The meat. Steps that succeed at doing nothing:

```
  [OK] Migrating config -> config (new format)
  [OK] Rebuilding index (1,204 items)
  [OK] Optimizing
  [OK] Retiring: batch rename
  [--] This will only take a moment
```

`This will only take a moment` takes the longest of any step, by a lot. One
step must visibly hang before succeeding, because they always do.

### 4. RESTART
Screen clears. Fake reboot. Comes back up to a screen identical to act 1 —
same banner, same everything. Then the payoff, shaped like `git diff --stat`
because that is the shape that makes the joke land:

```
  UPGRADE COMPLETE

  version     v3030.1  ->  v3030.2
  features         47  ->  46
  settings    where you left them  ->  reset
  icon             fine  ->  flat

  0 files changed, 0 insertions(+), 0 deletions(-)

  A brand new day.
```

`--rollback` prints `Rollback is not available for this version.` and exits 1.
One line, and it is the truest line in the program.

## Audio

A four-note ascending fanfare that resolves to the note it started on, so the
"success" chime goes nowhere. `CHIME` lives in `upgrade.py`; same
`winsound.Beep` daemon thread as `virus.py`.

`music.py` grows a `--track {virus,upgrade}` arg to emit `upgrade.mid` from
the same struct-packing it already does. Small change; the MIDI machinery is
already written and generic.

## Sharing code with virus.py

**Copy the four helpers** (`w`, `nap`, `type_out`, `size`) into `upgrade.py`.
Do not extract a shared `theater.py` yet.

Two callers is not a pattern. The extraction is obvious and will still be
obvious at three, when it can be done knowing what the third one actually
needed. Same for a `deltron <track>` umbrella CLI — worth it at four
programs, premature at two.

## Layout

```
upgrade.py         everything
changelog.txt      the filler, so it's tunable without touching code
SPEC-upgrade.md    this
```

Stdlib only.

## Check

`demo()` under `--check`, sleeps zeroed. One assert per act, plus the two
that protect the joke:

- all four acts produced their output
- the version string went **up**
- the feature count went **down**
- `0 files changed` is in the output
- the terminal was restored

## Non-goals

- Touching a real package manager, or anything that could be mistaken for one.
- A self-updater. This program must never acquire the ability to change itself.
- `theater.py`. Not until the third track. See above.
- An umbrella CLI. Not until the fourth.
