#!/usr/bin/env python3
"""3030 -- Deltron 3030, track 2. A Y3K compliance checker.

Scans code for date handling that will not survive the year 3030, which is
most date handling. Unlike the rest of this repo it does something real:
two-digit years and 32-bit clocks are real bugs with real dates attached.

    python y3k.py                 scan the current directory
    python y3k.py path/to/src     scan somewhere else
    python y3k.py --check         self-check

Exits 1 if anything is found, so it works in CI, which is an absurd thing for
this repo to be able to say. Put `y3k: ignore` on a line to skip it.
"""
import io
import os
import re
import sys
from contextlib import redirect_stdout
from datetime import date

TARGET_YEAR = 3030
SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "build", "venv",
             ".venv", ".mypy_cache", ".pytest_cache", "docs"}
MAX_BYTES = 1_000_000
IGNORE = "y3k: ignore"
START, END = IGNORE + "-start", IGNORE + "-end"

# (label, pattern, breaks_in, why). Ordered most-urgent first.
RULES = [
    ("32-bit timestamp",
     r"\btime_t\b|\bint32\b|\bInt32\b|int\(\s*time\.time\(\)\s*\)",  # y3k: ignore
     2038,
     "signed 32-bit seconds overflow on 2038-01-19"),
    ("two-digit year",
     r"%y\b|\byy\b|'YY'|\"YY\"",  # y3k: ignore
     2100,
     "a two-digit year is ambiguous the moment a century turns"),
    ("hardcoded century",
     r"(?:19|20)\d\d\s*[<>]=?|[<>]=?\s*(?:19|20)\d\d",  # y3k: ignore
     2100,
     "a bound that assumes which century you are in"),
    ("century arithmetic",
     r"year\s*[-+]\s*(?:19|20)00",  # y3k: ignore
     2100,
     "arithmetic against a hardcoded century"),
    ("this-millennium regex",
     r"\(1\[89\]\|20\)|\(19\|20\)|\[12\]\[0-9\]\{3\}",  # y3k: ignore
     3000,
     "a date pattern that only matches years starting 1 or 2"),
    ("four-digit year",
     r"%04d.{0,12}year|year.{0,12}%04d|\\d\{4\}.{0,12}year",  # y3k: ignore
     10000,
     "assumes the year fits in four digits. It does, for now"),
]
RULES = [(label, re.compile(pat), yr, why) for label, pat, yr, why in RULES]


def severity(breaks_in):
    left = breaks_in - date.today().year
    if left <= 25:
        return "CRITICAL"
    if left <= 200:
        return "HIGH"
    return "MEDIUM" if breaks_in <= TARGET_YEAR else "LOW"


def scan_text(text, path="<text>"):
    """The whole engine. Takes a string so the self-check needs no files."""
    out, skipping = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if START in line:
            skipping = True
            continue
        if END in line:
            skipping = False
            continue
        if skipping or IGNORE in line:
            continue
        for label, pat, breaks_in, why in RULES:
            if pat.search(line):
                out.append((path, n, label, breaks_in, why, line.strip()[:90]))
    return out


def _rel(path):
    """Relative where it can be. On Windows, relpath dies across drives."""
    try:
        return os.path.relpath(path)
    except ValueError:
        return path


def scan_path(root):
    findings, files = [], 0
    if os.path.isfile(root):
        paths = [root]
    else:
        paths = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            paths += [os.path.join(dirpath, f) for f in filenames]
    for p in paths:
        try:
            if os.path.getsize(p) > MAX_BYTES:
                continue
            with open(p, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError):
            continue  # binary, unreadable, or gone. Not our problem
        files += 1
        findings += scan_text(text, _rel(p))
    return findings, files


def report(findings, files, root):
    left = TARGET_YEAR - date.today().year
    print()
    print(f"  3030 // Y3K COMPLIANCE  --  {files} file(s) under {root}")
    print()
    for path, n, label, breaks_in, why, src in sorted(findings, key=lambda f: f[3]):
        yrs = breaks_in - date.today().year
        print(f"  {path}:{n}  [{severity(breaks_in)}]  {label}")
        print(f"      breaks in {breaks_in} ({yrs} years) -- {why}")
        print(f"      > {src}")
        print()
    if not findings:
        print("  VERDICT: 3030-READY.")
        print("  Nothing here handles a date at all, which is one way to do it.")
        return 0
    worst = min(f[3] for f in findings)
    print(f"  {len(findings)} finding(s). Earliest failure: {worst}.")
    print("  VERDICT: NOT 3030-READY.")
    print(f"  {left} years to fix it. That is not as long as it sounds.")
    return 1


# y3k: ignore-start  (deliberately broken sample code)
FIXTURE = """
ts = int(time.time())
label = d.strftime('%y-%m-%d')
if year > 1999 and year < 2100:
    pass
age = year - 1900
DATE = re.compile(r'(19|20)\\d\\d-\\d\\d')
print('%04d' % year)
clean = 'no dates here at all'
skipped = int(time.time())  # y3k: ignore
"""
# y3k: ignore-end


def demo():
    found = scan_text(FIXTURE, "fixture")
    labels = {f[2] for f in found}
    for label, _, _, _ in RULES:
        assert label in labels, f"rule never fired: {label}"
    assert not any(f[5].startswith("skipped") for f in found), "'y3k: ignore' was not honored"
    assert not scan_text("clean = 1\nx = 'nothing'\n"), "false positive on clean code"
    assert severity(2038) == "CRITICAL" and severity(10000) == "LOW", "severity is off"
    assert _rel("Z:\\elsewhere\\x.py"), "relpath must survive a path on another drive"
    with redirect_stdout(io.StringIO()):
        assert report([], 0, ".") == 0 and report(found, 1, ".") == 1, "wrong exit codes"
    print(f"ok: {len(RULES)} rules, {len(found)} findings on the fixture, ignore honored")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    else:
        target = next((a for a in sys.argv[1:] if not a.startswith("-")), ".")
        sys.exit(report(*scan_path(target), root=target))
