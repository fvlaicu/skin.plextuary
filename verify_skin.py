#!/usr/bin/env python3
"""Static checks for a Kodi skin tree, failing only on what is new relative to a base tree.

usage: verify_skin.py SKIN_DIR BASE_DIR

BASE_DIR is the stock Estuary the skin was built on (estuary_tree.sh writes one,
or export the branch's "<version> base" commit). Findings the base has too are
printed as inherited and do not affect the exit status.

  1. every xml/*.xml parses
  2. every fontset in Font.xml defines every font name the XML uses
     (inherited: the base uses that name and leaves it undefined too)
  3. duplicate control ids within a window, in files whose root element is
     <window>; include files legitimately repeat ids across includes
  4. literal texture paths that resolve to no file in media/ (case-insensitive,
     as Kodi lower-cases bundle lookups)

Exit status: 1 if there is anything new, else 0.
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


def parse_all(root):
    bad = []
    for p in sorted((root / "xml").glob("*.xml")):
        try:
            ET.parse(p)
        except ET.ParseError as e:
            bad.append(f"{p.name}: {e}")
    return bad


def font_gaps(root):
    """{fontset id: set of font names the XML uses that the fontset lacks}"""
    fx = ET.parse(root / "xml" / "Font.xml").getroot()
    sets = {fs.get("id"): {f.findtext("name") for f in fs.iter("font")} for fs in fx.iter("fontset")}
    used = set()
    for p in (root / "xml").glob("*.xml"):
        t = p.read_text(encoding="utf-8")
        used |= set(re.findall(r"<font>([^<$]+)</font>", t))
        used |= set(re.findall(r'<param name="font[^"]*" value="([^"$]+)"', t))
    return {k: used - v for k, v in sets.items() if used - v}


def window_files(root):
    for p in sorted((root / "xml").glob("*.xml")):
        try:
            if ET.parse(p).getroot().tag == "window":
                yield p
        except ET.ParseError:
            pass  # reported by check 1


def dup_ids(root):
    out = set()
    for p in window_files(root):
        ids = Counter(re.findall(r'<control type="[^"]+" id="(\d+)"', p.read_text(encoding="utf-8")))
        out |= {(p.name, i) for i, n in ids.items() if n > 1}
    return out


def missing_textures(root):
    media = {str(q.relative_to(root / "media")).lower() for q in (root / "media").rglob("*") if q.is_file()}
    out = set()
    for p in (root / "xml").glob("*.xml"):
        t = p.read_text(encoding="utf-8")
        for m in re.findall(r'(?:<texture[^>]*>|<icon>|<thumb>|value=")([^<"$]+\.(?:png|jpg|gif))', t, re.I):
            if "://" in m or m.startswith("special:"):
                continue
            if m.lower() not in media:
                out.add((p.name, m))
    return out


def report(label, new, inherited):
    tail = f"  ({len(inherited)} inherited from base: {sorted(inherited)})" if inherited else ""
    print(f"{label}: {sorted(new) or 'none'}{tail}")
    return not new


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    root, base = Path(sys.argv[1]), Path(sys.argv[2])
    ok = True
    bad = parse_all(root)
    print("1. XML parse:", "all ok" if not bad else bad)
    ok &= not bad

    gaps = font_gaps(root)
    base_gap_names = set().union(*font_gaps(base).values())
    new = {(fs, n) for fs, names in gaps.items() for n in names if n not in base_gap_names}
    inherited = {n for names in gaps.values() for n in names if n in base_gap_names}
    ok &= report("2. fontsets missing font names", new, inherited)

    dups, base_dups = dup_ids(root), dup_ids(base)
    ok &= report("3. duplicate control ids", dups - base_dups, dups & base_dups)

    tex, base_tex = missing_textures(root), missing_textures(base)
    ok &= report("4. unresolved textures", tex - base_tex, tex & base_tex)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
