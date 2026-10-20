#!/usr/bin/env bash
# usage: build_xbt.sh SKIN_DIR OUT_DIR
# Packs SKIN_DIR/media into OUT_DIR/Textures.xbt and each SKIN_DIR/themes/<name>
# into OUT_DIR/<name>.xbt with the arguments Kodi's own skin build uses
# (cmake/scripts/common/ProjectMacros.cmake), then checks each bundle against its
# source with xbt_check.py. TexturePacker only reads image files, so old bundles
# in media/ do not end up inside the new ones. Copying the bundles into media/
# is left to you.
#   TEXTUREPACKER  default tools/build/texturepacker/TexturePacker (build_texturepacker.sh)
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
TP=${TEXTUREPACKER:-$here/build/texturepacker/TexturePacker}
[ $# -eq 2 ] || { sed -n '2,10p' "$0"; exit 2; }
skin=$1 out=$2
[ -x "$TP" ] || { echo "no TexturePacker at $TP; run build_texturepacker.sh" >&2; exit 2; }
mkdir -p "$out"
rc=0
pack() {  # pack SOURCE_DIR BUNDLE
  "$TP" -input "$1" -output "$2" -dupecheck >/dev/null
  python3 -I "$here/xbt_check.py" "$2" "$1" || rc=1
}
pack "$skin/media" "$out/Textures.xbt"
for t in "$skin"/themes/*/; do
  [ -d "$t" ] && pack "${t%/}" "$out/$(basename "$t").xbt"
done
exit $rc
