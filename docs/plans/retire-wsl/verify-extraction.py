"""Every regular file in the tar listing under the migrated trees must exist on disk, same size."""
import os, re, sys
L = sys.argv[1]; H = r"C:\Users\Barat"
EXCL = re.compile(r"(^|/)(\.venv|node_modules|__pycache__|\.pytest_cache)/")
MAP = [("Google-Deprem/", H + "\Google-Deprem\\"), ("Projects/", H + "\Projects\\"),
       ("ml/", r"E:\ML" + "\\"), (".cache/huggingface/", r"E:\ML\hf-cache" + "\\")]
STAGED = [".claude/", ".claude.json", ".codex/", ".copilot/", ".config/matplotlib/", ".config/btop/",
          ".config/muse/", ".config/uv/", ".seisbench/", ".pyrocko/", ".bash_history", ".gitconfig", ".bashrc"]
SKIP_STAGED = (".claude/remote/", ".claude/shell-snapshots/", ".claude/cache/", ".claude/downloads/")
tot = ok = 0; missing = []; sizediff = []; skipped_excl = 0
line_re = re.compile(r"^(\S+)\s+\d+\s+\S+\s+\S+\s+(\d+)\s+\S+\s+\d+\s+\S+\s+(.*)$")
with open(L, encoding="utf-8", errors="replace") as fh:
    for line in fh:
        m = line_re.match(line.rstrip("\n"))
        if not m or not m.group(1).startswith("-"): continue
        size = int(m.group(2)); path = m.group(3)
        if not path.startswith("./home/barathanaslan/"): continue
        rel = path[len("./home/barathanaslan/"):]
        if EXCL.search(rel) or rel.startswith("Projects/ClaudeSetup/") or rel.startswith("ml/bin/"): skipped_excl += 1; continue
        dst = None
        for pre, root in MAP:
            if rel.startswith(pre): dst = root + rel[len(pre):].replace("/", "\\"); break
        if dst is None and any(rel.startswith(s) for s in STAGED) and not rel.startswith(SKIP_STAGED):
            dst = H + "\.wsl-home\\" + rel.replace("/", "\\")
        if dst is None: continue
        tot += 1
        try: st = os.stat(dst)
        except FileNotFoundError: missing.append(rel); continue
        if st.st_size != size: sizediff.append((rel, size, st.st_size)); continue
        ok += 1
print(f"checked {tot} files: ok={ok} missing={len(missing)} size-mismatch={len(sizediff)} (excluded-by-policy {skipped_excl})")
for r in missing[:20]: print("  MISSING", r)
for r in sizediff[:20]: print("  SIZE", r)
sys.exit(0 if not missing and not sizediff else 1)
