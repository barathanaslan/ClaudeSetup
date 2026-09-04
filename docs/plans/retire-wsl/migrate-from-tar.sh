#!/bin/bash
# Extract the WSL export tar into the Windows layout, natively (no 9P). Git Bash on the box.
# Usage: migrate-from-tar.sh [tar]     idempotent; re-running re-extracts (overwrites same files).
set -uo pipefail
export MSYS_NO_PATHCONV=1              # tar.exe gets its patterns and Windows paths untouched
TAR="${1:-E:/Archive/wsl-ubuntu-2026-09-04.tar}"
T=/c/Windows/System32/tar.exe          # bsdtar
H=/c/Users/Barat
P=home/barathanaslan                   # prefix inside the tar (entries carry a ./ in front, hence strip = depth+1)
LOG="$H/migrate-from-tar.log"
: > "$LOG"; log() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }
X=(--exclude='*/.venv' --exclude='*/node_modules' --exclude='*/__pycache__' --exclude='*/.pytest_cache')
[ -f "$TAR" ] || { log "tar not found: $TAR"; exit 1; }

log "1/6 code trees -> $H  (Google-Deprem, Projects minus ClaudeSetup which is a fresh clone)"
"$T" -xf "$TAR" -C "C:/Users/Barat" --strip-components=3 "${X[@]}" \
  --exclude="$P/Projects/ClaudeSetup" \
  "$P/Google-Deprem" "$P/Projects" 2>&1 | grep -v "Can't create\|symlink\|Removing leading" | tee -a "$LOG"
log "   exit=${PIPESTATUS[0]}"

log "2/6 ml -> E:/ML  (union; WSL versions overwrite same-named files; Linux rclone binary skipped)"
mkdir -p /e/ML
"$T" -xf "$TAR" -C "E:/ML" --strip-components=4 "${X[@]}" --exclude="$P/ml/bin" \
  "$P/ml" 2>&1 | grep -v "symlink\|Removing leading" | tee -a "$LOG"
log "   exit=${PIPESTATUS[0]}"

log "3/6 huggingface cache -> E:/ML/hf-cache"
mkdir -p /e/ML/hf-cache
"$T" -xf "$TAR" -C "E:/ML/hf-cache" --strip-components=5 "$P/.cache/huggingface" 2>&1 | grep -v "symlink\|Removing leading" | tee -a "$LOG"
log "   exit=${PIPESTATUS[0]}"

log "4/6 dotfiles -> staging $H/.wsl-home  (merged by migrate-dotfiles.py, nothing overwritten blindly)"
mkdir -p "$H/.wsl-home"
"$T" -xf "$TAR" -C "C:/Users/Barat/.wsl-home" --strip-components=3 \
  --exclude="$P/.claude/remote" --exclude="$P/.claude/shell-snapshots" \
  --exclude="$P/.claude/cache" --exclude="$P/.claude/downloads" \
  "$P/.claude" "$P/.claude.json" "$P/.codex" "$P/.copilot" "$P/.config/matplotlib" "$P/.config/btop" \
  "$P/.config/muse" "$P/.config/uv" "$P/.seisbench" "$P/.pyrocko" "$P/.bash_history" "$P/.gitconfig" \
  "$P/.bashrc" 2>&1 | grep -v "symlink\|Removing leading" | tee -a "$LOG"
log "   exit=${PIPESTATUS[0]}"

log "5/6 junction ~/ml -> E:\\ML"
if [ ! -e "$H/ml" ]; then cmd.exe /c 'mklink /J "C:\Users\Barat\ml" "E:\ML"' | tee -a "$LOG"; else log "   ~/ml exists: $(ls -ld "$H/ml" | cut -c1-60)"; fi

log "6/6 remove any dangling Linux-target symlinks bsdtar may have created (recreated by migrate-links.sh)"
find "$H/Google-Deprem" "$H/Projects" -maxdepth 3 -type l 2>/dev/null | while read -r l; do log "   rm dangling link: $l -> $(readlink "$l")"; rm -f "$l"; done
log "DONE. Next: migrate-links.sh, then migrate-dotfiles.py"
