#!/bin/bash
# Recreate every WSL symlink as an NTFS symlink, data-driven from symlinks.tsv (link<TAB>target),
# which was generated from the tar listing. Needs Developer Mode. Git Bash on the box.
# Skips ~/.claude/* and ~/.codex/* (ClaudeSetup's setup.sh and the Windows Codex own those).
set -uo pipefail
export MSYS=winsymlinks:nativestrict
H=/c/Users/Barat
TSV="${1:-$(dirname "$0")/symlinks.tsv}"
ok=0; skip=0; fail=0
while IFS=$'\t' read -r link target; do
  [ -n "$link" ] || continue
  case "$link" in .claude/*|.codex/*) skip=$((skip+1)); continue;; esac
  t="$target"
  t="${t/#\/mnt\/e\//\/e\/}"; t="${t/#\/mnt\/c\//\/c\/}"; t="${t/#\/home\/barathanaslan\//$H/}"
  l="$H/$link"
  if [ ! -e "$t" ]; then echo "SKIP target missing: $link -> $t"; skip=$((skip+1)); continue; fi
  if [ -L "$l" ]; then rm -f "$l"; fi
  if [ -e "$l" ]; then echo "SKIP real file/dir at link path: $link"; skip=$((skip+1)); continue; fi
  mkdir -p "$(dirname "$l")"
  if ln -s "$t" "$l" 2>/dev/null; then ok=$((ok+1)); else echo "FAILED: $link -> $t"; fail=$((fail+1)); fi
done < "$TSV"
echo "links created=$ok skipped=$skip failed=$fail"
