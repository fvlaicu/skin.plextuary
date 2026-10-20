#!/usr/bin/env python3
"""Find string IDs a skin references that Kodi 22 resolves to nothing.

usage: check_strings.py SKIN_DIR CORE_PO [OLD_CORE_PO]

SKIN_DIR is a skin root (xml/ and language/resource.language.en_gb/strings.po).
CORE_PO is Kodi's core en_gb strings.po for the Kodi you target (core_strings.sh
writes one). With OLD_CORE_PO, IDs whose core text changed are reported too.

Kodi 22 rule (xbmc/addons/Skin.h IsSkinStringId, xbmc/xbmc 05d6044b2c): an ID is
looked up in the skin's own strings.po only if it is in 31000-31999; every other
ID goes to Kodi's core strings.po, whatever the skin defines.

Exit status: 1 if anything is MISSING, else 0.
"""
import re
import sys
from pathlib import Path


def load_po(path):
    ids = {}
    ctx = None
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r'msgctxt "#(\d+)"', line)
        if m:
            ctx = int(m.group(1))
            continue
        m = re.match(r'msgid "(.*)"', line)
        if m and ctx is not None:
            ids[ctx] = m.group(1)
            ctx = None
    return ids


# Places Kodi treats a bare number as a localized string id.
PATTERNS = [
    re.compile(r"\$LOCALIZE\[(\d+)\]"),
    re.compile(r"<(?:label|label2|altlabel|heading|hinttext)>(\d+)</"),
    re.compile(r'<param name="(?:label|label2|header|heading)" value="(\d+)"'),
    re.compile(r'<fontset [^>]*idloc="(\d+)"'),
]
SELECTBOOL = re.compile(r"Skin\.Select(?:Bool|String)?\(([^)]*)\)")
SKIN_RANGE = range(31000, 32000)


def ids_in(text):
    found = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat in PATTERNS:
            for m in pat.finditer(line):
                found.setdefault(int(m.group(1)), lineno)
        for m in SELECTBOOL.finditer(line):
            for part in m.group(1).split(","):
                head = part.strip().split("|")[0]
                if head.isdigit():
                    found.setdefault(int(head), lineno)
    return found


def main():
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    skin = load_po(root / "language" / "resource.language.en_gb" / "strings.po")
    new = load_po(sys.argv[2])
    old = load_po(sys.argv[3]) if len(sys.argv) == 4 else None
    missing = changed = 0
    for path in sorted((root / "xml").glob("*.xml")):
        for sid, lineno in sorted(ids_in(path.read_text(encoding="utf-8")).items()):
            if sid in SKIN_RANGE:
                if sid not in skin:
                    missing += 1
                    print(f"MISSING  {path.name}:{lineno}  #{sid}  (skin range, not in skin strings.po)")
                continue
            if sid not in new:
                missing += 1
                where = f"old core: {old.get(sid, '<not in old core either>')!r}" if old is not None else "not in core"
                print(f"MISSING  {path.name}:{lineno}  #{sid}  ({where})")
            elif old is not None and sid in old and old[sid] != new[sid]:
                changed += 1
                print(f"CHANGED  {path.name}:{lineno}  #{sid}  {old[sid]!r} -> {new[sid]!r}")
    print(f"\n{missing} missing" + (f", {changed} changed" if old is not None else ""))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
