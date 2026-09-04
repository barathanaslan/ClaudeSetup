# Retire WSL on the cuda box — 2026-09-04

## Why

Two layers (Windows host + WSL2 Ubuntu) made every routine thing a problem: two Claude Code
logins, ssh landing in cmd with a `wsl` hop, paths that meant different things per layer, and a
slow 9P bridge that forced a hot-ext4 / cold-E: data split with staging copies. The GPU, the tools
and the data all work natively on Windows, so the Linux layer bought nothing.

## End state

- Everything runs natively on Windows. Shell = Git Bash (Terminal default, ssh `DefaultShell`,
  VS Code terminal). `~` = `C:\Users\Barat`, mirroring the Mac layout.
- `~/ml` is a junction to `E:\ML`, the single data root. No staging, no hot/cold split.
- One native Claude Code with one `~/.claude`; accounts switched with `/login`; every old WSL
  session transcript re-keyed to the new folder paths so `--resume` still finds them.
- `detach` replaces tmux for long jobs (WMI-created processes survive ssh disconnect — verified
  2026-09-04: WMI child alive after disconnect, `Start-Process` child killed).
- WSL stays installed but empty: the old distro is exported in full to
  `E:\Archive\wsl-ubuntu-2026-09-04.tar`, unregistered, and a fresh small Ubuntu registered in
  its place for any future task that truly needs Linux.

## Inventory at start (2026-09-04)

| Item | Size |
|---|---|
| ext4.vhdx on C: | 318 GB allocated / 199 GB used |
| ~/ml (biohub 97, datasets 77, corpora 7, models+bench 3) | 176 GB |
| ~/.cache (uv 30, huggingface 11) | 33 GB |
| ~/Google-Deprem (not a repo; FocoNet + pyfk-opt inside are) | 17 GB |
| ~/Projects (ClaudeSetup, BarathanAslan, Bosphorify/presser, blue-ledger, MuseTest) | 2 GB |
| E:\wsl-swap.vhdx | 34 GB |

No cron, tmux, systemd or Windows scheduled tasks depended on WSL. Only VS Code Remote-WSL
servers and Claude desktop-app remote sessions were running in it.

Work that existed only in WSL: FocoNet (1 unpushed commit + untracked experiments dir),
blue-ledger (no remote at all), pyfk-opt (remote 404s; branches main/cpu/cuda only local),
Google-Deprem docs/ProjectDocs (not a repo), Bosphorify, MuseTest, all Claude session transcripts.

## Steps

1. Seatbelts: push FocoNet; create private `barathanaslan/blue-ledger` and push. (done)
2. Windows toolchain via winget: uv, gh, node LTS, rclone, PowerShell 7; Claude Code CLI;
   `uv python install 3.11 3.12`; git `autocrlf=false longpaths=true symlinks=true`. (done)
3. Credentials carried over: ssh keys, kaggle.json, rclone.conf (incl. gdrive-rw), gh hosts.yml,
   .cf_token. (done)
4. Windows settings (owner ran them elevated): Developer Mode, LongPathsEnabled,
   OpenSSH DefaultShell = Git Bash with `-c`.
5. Owner closes every VS Code / desktop-app session into WSL → `wsl --shutdown` →
   `wsl --export Ubuntu E:\Archive\wsl-ubuntu-2026-09-04.tar`.
6. Extract from the tar natively (no 9P): `home/barathanaslan/{Google-Deprem,Projects}` →
   `C:\Users\Barat\`, `home/barathanaslan/ml` → `E:\ML\` (union, WSL wins), HF cache →
   `E:\ML\hf-cache`, dotfiles (`.claude`, `.claude.json` projects, `.codex`, `.copilot`,
   `.config/*`, `.seisbench`, `.pyrocko`, `.bash_history`). Excluded from the live tree, still in
   the tar: `.venv`, `node_modules`, `__pycache__`, `.cache/uv`, `.vscode-server`, `.local`, `.npm`.
   Pre-flight found no NTFS-invalid names or case collisions; longest path 249 chars.
7. Recreate the 20 WSL symlinks as NTFS symlinks/junctions (`~/ml` → `E:\ML`,
   `FocoNet/foconet-dataset`, `ProjectDocs/*` → `E:\ML\studio\...`).
8. Re-key Claude sessions: `~/.claude/projects/-home-barathanaslan-X` → `C--Users-Barat-X`;
   merge `.claude.json` project entries; drop the desktop app's `wsl:ubuntu:` entries.
9. Verify: file counts and byte totals per top-level dir, WSL vs Windows; `git status` in each
   repo; `uv sync` + `torch.cuda.is_available()` on sm_120; FocoNet tests; blue-ledger build and
   dev server in a browser (the old "unreachable from Windows" blocker disappears).
10. Fix references: this repo (CLAUDE.md, cuda-box skill, bin/cuda, CUDA-README, setup.sh),
    Google-Deprem docs, blue-ledger docs, Terminal default profile, Remote-WSL extension.
    Macs: `git pull && ./setup.sh`.
11. Retire: `wsl --unregister Ubuntu` (frees ~318 GB on C:), delete `E:\wsl-swap.vhdx`,
    shrink `.wslconfig`, `wsl --install -d Ubuntu` fresh. Keep the tar.

## Decisions taken with the owner

- Accounts: weekly switching via `/login`; Trace Lab first.
- vLLM dropped (no native Windows build); llama.cpp/Ollama if inference is needed later.
- biohub's 81 GB Kaggle data kept under `E:\ML\biohub`.
- blue-ledger gets a private GitHub remote; pyfk-opt pending the owner's answer.
- Stray staging files in `C:\Users\Barat` go to `E:\ML\archive\windows-home-leftovers-2026\`,
  nothing deleted.
