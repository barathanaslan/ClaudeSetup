#!/bin/bash
# Recreate the WSL symlinks as NTFS symlinks (needs Developer Mode). Git Bash on the box.
set -uo pipefail
export MSYS=winsymlinks:nativestrict
H=/c/Users/Barat; GD="$H/Google-Deprem"; ST=/e/ML/studio/Google-Deprem/ProjectDocs
mk() { # mk <link> <target>
  local l="$1" t="$2"
  [ -e "$t" ] || { echo "SKIP (target missing): $l -> $t"; return; }
  [ -L "$l" ] && rm -f "$l"
  [ -e "$l" ] && { echo "SKIP (real file/dir exists at link path): $l"; return; }
  ln -s "$t" "$l" && echo "ok: $l -> $t" || echo "FAILED: $l -> $t (Developer Mode on?)"
}
mk "$GD/FocoNet/foconet-dataset" "$H/ml/datasets/foconet-dataset"
mkdir -p "$GD/ProjectDocs"
for name in "Meetings" "[EXT] Kandilli Observatory __ Turkey AI Earthquake Detection - Funding Proposal_Locked Version (5).pdf" \
  "Foconet.pdf" "kahramanmaras-study" "ross2018.pdf" "ProvidedFM" "9pwy7rgzkt-2" \
  "2025jh000879-sup-0001-supporting information si-s01.pdf" "notes.md" "phasenet.pdf" "meier-polarity.pdf" \
  "Kandilli istasyonlar.rtf" "An Introduction to Seismology, Earthquakes, and Earth Structure.pdf"; do
  mk "$GD/ProjectDocs/$name" "$ST/$name"
done
