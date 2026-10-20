# Plextuary port tools

The scripts used to port Plextuary to Estuary 4.1.0 (Kodi 22 "Piers"): the `piers` and `piers-ce` branches.

This folder is the `tools` branch: an orphan branch with no history shared with the skin branches, checked out as a worktree at `tools/` in the main checkout (`git worktree add tools tools` recreates it). It is never part of a skin tree, so no release can include it, however the zip is built. The main checkout ignores the folder through `/tools/` in `.git/info/exclude`; `build/` (the compiled TexturePacker) is ignored on this branch.

Settings, from the environment or from `tools/local.env` (not tracked; shell `NAME=value` lines):

- `XBMC`: a Kodi source checkout (xbmc/xbmc, or CoreELEC/xbmc for the CoreELEC variant). Required by the scripts that read Kodi's sources or strings.
- `BREW`: optional prefix holding giflib, lzo, libpng and libjpeg for `build_texturepacker.sh`, when the system doesn't provide them.

## Tools

| Tool | What it does |
|---|---|
| `build_texturepacker.sh` | Builds Kodi's TexturePacker into `tools/build/texturepacker/` from the xbmc checkout as it is checked out now. Run once, and again when Kodi changes the XBT format. |
| `build_xbt.sh SKIN_DIR OUT_DIR` | Packs `media/` into `Textures.xbt` and each `themes/<name>/` into `<name>.xbt` with Kodi's own arguments (`-input … -output … -dupecheck`), then runs `xbt_check.py` on each. Copy the bundles into `media/` yourself. |
| `xbt_check.py BUNDLE SOURCE_DIR` | Compares a bundle's index with the images TexturePacker would pack from `SOURCE_DIR`. Names only, not contents. |
| `check_branch.sh SKIN BASE XBMC_REF` | Runs `verify_skin.py` and `check_strings.py` on one tree. `SKIN` and `BASE` are directories or commits in this repo. |
| `verify_skin.py SKIN_DIR BASE_DIR` | XML parses; every fontset defines every font name used; no duplicate control ids per window; no unresolved literal texture paths. Fails only on findings the base doesn't have; inherited ones are printed. |
| `check_strings.py SKIN_DIR CORE_PO [OLD_CORE_PO]` | Lists string IDs that come out blank under Kodi 22's rule: skin strings resolve only in 31000–31999, every other ID from Kodi's core strings. |
| `core_strings.sh XBMC_REF OUT.po` | Writes Kodi's core en_gb `strings.po` at a ref, for `check_strings.py`. |
| `estuary_tree.sh XBMC_REF OUT_DIR` | Exports stock Estuary at a ref: the tree for a `<version> base` commit, or a base for `verify_skin.py`. |
| `pick.sh WORKTREE COMMIT…` | Cherry-picks pannal-style (`-x`), resolving `addon.xml` to the branch side and dropping `media/*.xbt`; stops at any other conflict. |
| `cont.sh WORKTREE "note"` | Finishes a resolved cherry-pick and adds `Ported to $PORTED_TO: note` (default 4.1.0) before the `(cherry picked from` trailer. |
| `renumber_strings.py SKIN_DIR` | Moves Plextuary's strings 32100–32111 to 31900–31911 in `strings.po`, `$LOCALIZE[]` and `idloc`. pannal has since made his own Kodi 22 fix; check which IDs it uses before running this on his commits. |

## Checking the branches

```
tools/check_branch.sh piers    6625848 33bf4cc022
tools/check_branch.sh piers-ce a4ca2f9 496c00ffd1
```

`6625848` and `a4ca2f9` are the `4.1.0 base` commits (`git log --grep='^4.1.0 base$' <branch>`); xbmc/xbmc `33bf4cc022` (its Piers branch) and CoreELEC/xbmc `496c00ffd1` (`aml-5.15.196-22.0`) are the Kodi sources each branch was built from, and give the core strings it runs against. Pass a worktree path instead of the branch name to check uncommitted work.

Results on 2026-10-21, both exit 0:

- 0 missing strings on both.
- Inherited from stock Estuary 4.1.0, on both: duplicate control ids `DialogMusicInfo.xml` 130 and `VideoFullScreen.xml` 1.
- Inherited on `piers-ce` only: `font8`, used by two empty 6-pixel spacer labels in CoreELEC 22's `DialogPlayerProcessInfo.xml` and defined by no fontset. Kodi falls back to `font13`, so nothing shows.
- `build_xbt.sh` on either branch reproduces the committed `Textures.xbt`, `curial.xbt` and `flat.xbt` byte for byte.
- For comparison, `omega` as released, against the `33bf4cc022` core strings: 13 missing, the 12 Plextuary strings plus Estuary 4.0.0's `#35255`.

## Re-syncing to a newer Estuary

How 4.1.0 was done:

1. `tools/estuary_tree.sh <ref> <dir>`, then on a new branch replace the tree with it, without `media/*.xbt`, as a `<version> base` commit (record the source ref in the message).
2. `tools/pick.sh <worktree> <commits…>`; on a conflict, resolve, `PORTED_TO=<version> tools/cont.sh <worktree> "<note>"`, and re-run with the rest. Check each pick's file list: a clean pick can still re-add media or strings from an older Estuary sync.
3. `tools/check_branch.sh <worktree> <base commit> <ref>` until only inherited findings are left.
4. `tools/build_xbt.sh <worktree> <out>`, copy the bundles into `media/`, commit them on their own.
5. Version commit: `addon.xml` with Plextuary's identity and the new `xbmc.gui` version.

## Limits

- `verify_skin.py` check 3 looks at one window file at a time; controls pulled in through `<include>` are not expanded.
- `verify_skin.py` check 4 only sees literal `.png`/`.jpg`/`.gif` paths in `<texture>`, `<icon>`, `<thumb>` and `value="…"`; paths built from `$VAR`/`$INFO` are skipped.
- `check_strings.py` finds IDs in `$LOCALIZE[]`, numeric `<label>`, `<label2>`, `<altlabel>`, `<heading>`, `<hinttext>`, label/header `<param>`s, `Skin.SelectBool()` options and fontset `idloc`. `$ADDON[]` strings are not checked.
- `pick.sh` and `cont.sh` were not re-run after the rebuild, since they need a branch to cherry-pick onto; they are the versions used for the 4.1.0 port, with `PORTED_TO` added to `cont.sh`.
