#!/usr/bin/env bash
# usage: build_texturepacker.sh
# Builds Kodi's TexturePacker into tools/build/texturepacker from the xbmc
# checkout as it is checked out now.
#   XBMC  Kodi source checkout (required)
#   BREW  optional prefix with giflib, lzo, libpng and libjpeg, for when the
#         system doesn't provide them; the binary gets an rpath to $BREW/lib
# Both can be set in tools/local.env (not tracked).
# SYSTEM_DEFINES is required on Linux; without it the build looks for windows.h.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
[ -f "$here/local.env" ] && . "$here/local.env"
: "${XBMC:?set XBMC to a Kodi source checkout, in the environment or tools/local.env}"
out=$here/build/texturepacker
prefix=()
if [ -n "${BREW:-}" ]; then
  prefix=(-DCMAKE_PREFIX_PATH="$BREW" -DCMAKE_INSTALL_RPATH="$BREW/lib" -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON)
fi
cmake -S "$XBMC/tools/depends/native/TexturePacker/src" -B "$out" \
  -DKODI_SOURCE_DIR="$XBMC" -DCMAKE_BUILD_TYPE=Release "${prefix[@]}" \
  "-DSYSTEM_DEFINES=TARGET_POSIX;TARGET_LINUX" >/dev/null
cmake --build "$out" -j"$(nproc)" >/dev/null
echo "$out/TexturePacker (from $XBMC at $(git -C "$XBMC" log -1 --format='%h %cs'))"
