#!/usr/bin/env bash
# usage: estuary_tree.sh XBMC_REF OUT_DIR
# Exports stock Estuary (addons/skin.estuary) at XBMC_REF into OUT_DIR, which
# must be new or empty: the tree for a "<version> base" commit, or a base for
# verify_skin.py.
#   XBMC  Kodi source checkout (required; can be set in tools/local.env)
set -euo pipefail
[ $# -eq 2 ] || { sed -n '2,6p' "$0"; exit 2; }
here=$(cd "$(dirname "$0")" && pwd)
[ -f "$here/local.env" ] && . "$here/local.env"
: "${XBMC:?set XBMC to a Kodi source checkout, in the environment or tools/local.env}"
mkdir -p "$2"
[ -z "$(ls -A "$2")" ] || { echo "$2 is not empty" >&2; exit 2; }
git -C "$XBMC" archive "$1:addons/skin.estuary" | tar -x -C "$2"
