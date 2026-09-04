"""Merge the staged WSL dotfiles into the Windows home. Never overwrites an existing Windows file.
Re-keys Claude session folders from /home/barathanaslan/X to C:\\Users\\Barat\\X and rewrites
the cwd fields inside copied transcripts so --resume finds them from the new folders."""
import json, os, re, shutil, time
H = r"C:\Users\Barat"; S = os.path.join(H, ".wsl-home")
OLD = "/home/barathanaslan"; NEW = r"C:\Users\Barat"

def key(path):  # Claude Code project-dir key: every non-alnum char -> '-'
    return re.sub(r"[^A-Za-z0-9]", "-", path)

def to_win(p):  # /home/barathanaslan/a/b -> C:\Users\Barat\a\b
    return NEW + p[len(OLD):].replace("/", "\\")

def copy_missing(src, dst):
    n = 0
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src); d = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(d, exist_ok=True)
        for f in files:
            t = os.path.join(d, f)
            if not os.path.exists(t):
                shutil.copy2(os.path.join(root, f), t); n += 1
    return n

report = []
# 1. Claude session folders, re-keyed, with cwd rewritten in the copies
pj = os.path.join(S, ".claude", "projects")
for name in sorted(os.listdir(pj)):
    old_key = key(OLD); assert name.startswith(old_key), name
    rest = name[len(old_key):]                       # e.g. "-Google-Deprem"
    new_name = key(NEW) + rest                       # C--Users-Barat-Google-Deprem
    dst = os.path.join(H, ".claude", "projects", new_name); os.makedirs(dst, exist_ok=True)
    n = 0
    for root, dirs, files in os.walk(os.path.join(pj, name)):
        rel = os.path.relpath(root, os.path.join(pj, name)); d = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(d, exist_ok=True)
        for f in files:
            src = os.path.join(root, f); t = os.path.join(d, f)
            if os.path.exists(t): continue
            if f.endswith(".jsonl"):
                with open(src, encoding="utf-8", errors="surrogateescape") as fh: txt = fh.read()
                txt = re.sub(r'"cwd":"(/home/barathanaslan[^"]*)"',
                             lambda m: '"cwd":' + json.dumps(to_win(m.group(1))), txt)
                with open(t, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh: fh.write(txt)
            else:
                shutil.copy2(src, t)
            n += 1
    report.append(f"sessions {name} -> {new_name}: {n} files")

# 2. other ~/.claude pieces (sessions, backups, session-env, plugins, .credentials.json)
for sub in ("sessions", "backups", "session-env", "plugins"):
    src = os.path.join(S, ".claude", sub)
    if os.path.isdir(src):
        report.append(f".claude/{sub}: {copy_missing(src, os.path.join(H, '.claude', sub))} files added")
cred_src = os.path.join(S, ".claude", ".credentials.json"); cred_dst = os.path.join(H, ".claude", ".credentials.json")
if os.path.exists(cred_src) and not os.path.exists(cred_dst):
    shutil.copy2(cred_src, cred_dst); report.append(".credentials.json (Trace Lab login) placed for the native CLI")

# 3. .claude.json: merge project entries (re-keyed), drop dead wsl:ubuntu entries, keep everything else
wj = os.path.join(H, ".claude.json"); shutil.copy2(wj, wj + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
win = json.load(open(wj, encoding="utf-8")); wsl = json.load(open(os.path.join(S, ".claude.json"), encoding="utf-8"))
projects = win.setdefault("projects", {})
for p, v in wsl.get("projects", {}).items():
    if p.startswith(OLD):
        np_ = to_win(p)
        if np_ not in projects: projects[np_] = v; report.append(f".claude.json project added: {np_}")
for p in [k for k in projects if k.startswith("wsl:")]:
    projects.pop(p); report.append(f".claude.json dead entry removed: {p}")
json.dump(win, open(wj, "w", encoding="utf-8"), indent=2)

# 4. plain dotfiles/dirs: add what is missing, never overwrite
for sub in (".codex", ".copilot", ".seisbench", ".pyrocko",
            os.path.join(".config", "matplotlib"), os.path.join(".config", "btop"), os.path.join(".config", "muse")):
    src = os.path.join(S, sub)
    if os.path.isdir(src): report.append(f"{sub}: {copy_missing(src, os.path.join(H, sub))} files added")
uvcfg = os.path.join(S, ".config", "uv")
if os.path.isdir(uvcfg):
    report.append(f".config/uv -> AppData/Roaming/uv: {copy_missing(uvcfg, os.path.join(H, 'AppData', 'Roaming', 'uv'))} files added")

# 5. bash history: append the WSL history
hs = os.path.join(S, ".bash_history"); hd = os.path.join(H, ".bash_history")
if os.path.exists(hs):
    with open(hs, encoding="utf-8", errors="replace") as a, open(hd, "a", encoding="utf-8") as b: b.write(a.read())
    report.append(".bash_history appended")
print("\n".join(report))
