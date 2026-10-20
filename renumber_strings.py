#!/usr/bin/env python3
"""Move Plextuary's skin strings 32100-32111 to 31900-31911 (Kodi 22 skin string range).

usage: renumber_strings.py SKIN_ROOT

Rewrites files in place. Only these three forms are rewritten, and only for the
twelve IDs below:
  language/*/strings.po   msgctxt "#N"
  xml/*.xml               $LOCALIZE[N]
  xml/*.xml               idloc="N"
Control ids that share a number (e.g. Includes.xml id="32111") are not touched.
"""
import re
import sys
from pathlib import Path

MAPPING = {old: old - 200 for old in range(32100, 32112)}
ALT = "|".join(str(i) for i in MAPPING)

RULES = [
    ("language/*/strings.po", re.compile(r'(msgctxt "#)(' + ALT + r')(")')),
    ("xml/*.xml", re.compile(r"(\$LOCALIZE\[)(" + ALT + r")(\])")),
    ("xml/*.xml", re.compile(r'(idloc=")(' + ALT + r')(")')),
]


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    total = 0
    for glob, pat in RULES:
        for path in sorted(root.glob(glob)):
            text = path.read_text(encoding="utf-8")
            new, n = pat.subn(lambda m: f"{m.group(1)}{MAPPING[int(m.group(2))]}{m.group(3)}", text)
            if n:
                path.write_text(new, encoding="utf-8")
                print(f"{n:3d}  {path.relative_to(root)}")
                total += n
    print(f"{total} replacements")


if __name__ == "__main__":
    main()
