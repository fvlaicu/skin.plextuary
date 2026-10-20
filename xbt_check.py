#!/usr/bin/env python3
"""Compare an XBT bundle's index with the images it should have been packed from.

usage: xbt_check.py BUNDLE.xbt SOURCE_DIR

Layout per xbmc/guilib/XBTFReader.cpp, which reads versions 2 and 3 the same
way: "XBTF", a version char, u32 file count; per file a 256-byte path, u32 loop,
u32 frame count; per frame u32 width, height, format, u64 packed size, u64
unpacked size, u32 duration, u64 offset (40 bytes).

Source images are the files TexturePacker packs: names ending in .png, .jpg,
.jpeg or .gif, case-sensitive (DecoderManager::IsSupportedGraphicsFile). The
writer lower-cases bundle paths (XBTFWriter.cpp), so paths are compared
lower-cased. Only names are compared, not image contents.

Exit status: 1 if the bundle and the source differ, else 0.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

PATH_LEN = 256  # CXBTFFile::MaximumPathLength
FRAME_LEN = 4 * 3 + 8 * 2 + 4 + 8
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif")


def entries(path):
    d = Path(path).read_bytes()
    if d[:4] != b"XBTF":
        sys.exit(f"{path}: not an XBT bundle")
    ver = chr(d[4])
    (n,) = struct.unpack_from("<I", d, 5)
    pos, names = 9, []
    for _ in range(n):
        names.append(d[pos:pos + PATH_LEN].split(b"\0", 1)[0].decode())
        pos += PATH_LEN
        _loop, nframes = struct.unpack_from("<II", d, pos)
        pos += 8 + nframes * FRAME_LEN
    return ver, names


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    bundle, srcdir = sys.argv[1], Path(sys.argv[2])
    ver, names = entries(bundle)
    src = [str(p.relative_to(srcdir)).lower() for p in srcdir.rglob("*") if p.is_file() and p.name.endswith(IMAGE_SUFFIXES)]
    clashes = sorted(k for k, v in Counter(src).items() if v > 1)
    missing, extra = sorted(set(src) - set(names)), sorted(set(names) - set(src))
    print(f"{Path(bundle).name}: XBT v{ver}, {len(names)} entries; {len(set(src))} source images in {srcdir}")
    for label, items in (("missing from bundle", missing), ("in bundle, not in source", extra), ("source names equal when lower-cased", clashes)):
        if items:
            print(f"  {label} ({len(items)}): {items}")
    sys.exit(1 if missing or extra or clashes else 0)


if __name__ == "__main__":
    main()
