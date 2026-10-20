#!/usr/bin/env bash
# usage: core_strings.sh XBMC_REF OUT.po
# Writes Kodi's core en_gb strings.po at XBMC_REF to OUT.po, for check_strings.py.
# XBMC_REF is a ref in the xbmc checkout: xbmc/xbmc's Piers branch for plain
# Kodi 22, the CoreELEC commit (e.g. 496c00ffd1) for CoreELEC 22.
#   XBMC  Kodi source checkout (required; can be set in tools/local.env)
set -euo pipefail
[ $# -eq 2 ] || { sed -n '2,6p' "$0"; exit 2; }
here=$(cd "$(dirname "$0")" && pwd)
[ -f "$here/local.env" ] && . "$here/local.env"
: "${XBMC:?set XBMC to a Kodi source checkout, in the environment or tools/local.env}"
git -C "$XBMC" show "$1:addons/resource.language.en_gb/resources/strings.po" > "$2"
