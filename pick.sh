#!/usr/bin/env bash
# usage: pick.sh WORKTREE COMMIT...
# Cherry-picks each commit with -x. addon.xml always resolves to the branch side
# (identity is restored by the final version commit) and media/*.xbt to deleted
# (rebuilt in a dedicated commit). Stops at the first conflict in any other path
# and prints it; resolve, finish with cont.sh, then re-run with the remaining
# commits. Review each pick's file list afterwards: a clean pick can still bring
# along files that belong to an older Estuary sync.
set -u
W=$1; shift
cd "$W" || exit 2
for c in "$@"; do
  subj=$(git log -1 --format=%s "$c" | cut -c1-90)
  if git cherry-pick -x "$c" >/dev/null 2>&1; then
    echo "ok        $c $subj"
    continue
  fi
  for f in $(git diff --name-only --diff-filter=U); do
    case "$f" in
      addon.xml) git checkout --ours -- addon.xml && git add addon.xml ;;
      media/*.xbt) git rm -q --cached "$f" 2>/dev/null; rm -f "$f" ;;
    esac
  done
  # Non-conflicting xbt/addon.xml changes that cherry-pick staged anyway
  git diff --cached --name-only | grep -E '^media/.*\.xbt$' | while read -r f; do git rm -q --cached "$f"; rm -f "$f"; done
  if git diff --cached --quiet -- addon.xml; then :; else git checkout HEAD -- addon.xml; fi
  left=$(git diff --name-only --diff-filter=U)
  if [ -z "$left" ]; then
    if git diff --cached --quiet; then
      echo "EMPTY     $c $subj  (nothing left after auto-resolve; skipped)"
      git cherry-pick --skip >/dev/null 2>&1
    else
      GIT_EDITOR=true git cherry-pick --continue >/dev/null 2>&1 && echo "auto      $c $subj  (addon.xml/xbt resolved)"
    fi
    continue
  fi
  echo "CONFLICT  $c $subj"
  echo "$left" | sed 's/^/          /'
  exit 1
done
