#!/usr/bin/env bash
# usage: cont.sh WORKTREE "note"
# Finishes a resolved cherry-pick (stages everything in WORKTREE) and adds
# "Ported to $PORTED_TO: note" to its message, before the "(cherry picked from"
# trailer. PORTED_TO is the Estuary version being ported to (default 4.1.0).
set -e
cd "$1"
git add -A
msg=$(cat "$(git rev-parse --git-path MERGE_MSG)")
note="Ported to ${PORTED_TO:-4.1.0}: $2"
printf '%s\n' "$msg" | awk -v note="$note" '/^\(cherry picked from commit/ && !done {print note; print ""; done=1} {print}' > "$(git rev-parse --git-path MERGE_MSG)"
GIT_EDITOR=true git cherry-pick --continue >/dev/null
git log -1 --format='%h %an | %s%n%b' | sed 's/^/    /'
