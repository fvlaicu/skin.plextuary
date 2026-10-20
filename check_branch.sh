#!/usr/bin/env bash
# usage: check_branch.sh SKIN BASE XBMC_REF
# Runs verify_skin.py and check_strings.py on one skin tree.
#   SKIN      a skin directory (a worktree, to check uncommitted work), or a
#             commit-ish in this repo, exported to a temporary directory
#   BASE      the stock Estuary SKIN was built on: a directory, or a commit-ish
#             in this repo such as the branch's "4.1.0 base" commit
#   XBMC_REF  ref in the xbmc checkout whose core strings Kodi will use
#             (xbmc/xbmc's Piers commit for piers, the CoreELEC commit for piers-ce)
# Exit status: 1 if either check fails.
set -uo pipefail
[ $# -eq 3 ] || { sed -n '2,10p' "$0"; exit 2; }
here=$(cd "$(dirname "$0")" && pwd)
repo=$(git -C "$here" rev-parse --show-toplevel)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
tree() {  # tree DIR_OR_COMMIT NAME -> prints a directory
  if [ -d "$1" ]; then echo "$1"; return; fi
  mkdir -p "$tmp/$2" && git -C "$repo" archive "$1" | tar -x -C "$tmp/$2" && echo "$tmp/$2"
}
skin=$(tree "$1" skin) || exit 2
base=$(tree "$2" base) || exit 2
"$here/core_strings.sh" "$3" "$tmp/core.po" || exit 2
rc=0
echo "### verify_skin: $1 against $2"
python3 -I "$here/verify_skin.py" "$skin" "$base" || rc=1
echo "### check_strings: $1 with core strings from $3 (Kodi 22 rules)"
python3 -I "$here/check_strings.py" "$skin" "$tmp/core.po" || rc=1
exit $rc
