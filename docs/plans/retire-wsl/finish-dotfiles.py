"""Finish the dotfile merge (steps 4-5) after the earlier crash. Idempotent, never overwrites.
Linux tool trees (.codex, .copilot) are preserved beside the Windows ones, not merged into them."""
import os, shutil
H = r"C:\Users\Barat"; S = os.path.join(H, ".wsl-home")
def copy_missing(src, dst):
    n = skipped = 0; errs = []
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src); d = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(d, exist_ok=True)
        for f in files:
            s = os.path.join(root, f); t = os.path.join(d, f)
            if os.path.islink(s): skipped += 1; continue          # Linux symlinks: nothing to point at here
            if os.path.exists(t): continue
            try: shutil.copy2(s, t); n += 1
            except OSError as e: errs.append(f"{s}: {e.__class__.__name__}")
    return n, skipped, errs
PAIRS = [(".codex", ".codex-from-wsl"), (".copilot", ".copilot-from-wsl"), (".seisbench", ".seisbench"),
         (".pyrocko", ".pyrocko"), (os.path.join(".config","matplotlib"), os.path.join(".config","matplotlib")),
         (os.path.join(".config","btop"), os.path.join(".config","btop")),
         (os.path.join(".config","muse"), os.path.join(".config","muse")),
         (os.path.join(".config","uv"), os.path.join("AppData","Roaming","uv"))]
for sub, dst in PAIRS:
    src = os.path.join(S, sub)
    if not os.path.isdir(src): print(f"  (absent) {sub}"); continue
    n, sk, errs = copy_missing(src, os.path.join(H, dst))
    print(f"  {sub} -> {dst}: {n} copied, {sk} symlinks skipped, {len(errs)} errors")
    for e in errs[:5]: print("     ", e)
hs = os.path.join(S, ".bash_history"); hd = os.path.join(H, ".bash_history")
marker = "# --- WSL history imported 2026-09-04 ---"
cur = open(hd, encoding="utf-8", errors="replace").read() if os.path.exists(hd) else ""
if os.path.exists(hs) and marker not in cur:
    with open(hd, "a", encoding="utf-8") as b:
        b.write(("\n" if cur and not cur.endswith("\n") else "") + marker + "\n")
        b.write(open(hs, encoding="utf-8", errors="replace").read())
    print("  .bash_history: WSL history appended")
else:
    print("  .bash_history: already imported or absent")
