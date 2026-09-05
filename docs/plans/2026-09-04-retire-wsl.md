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
  `E:\Archive\wsl-ubuntu-2026-09-04.tar` and unregistered. No distro is registered; if a task
  ever truly needs Linux, `wsl --install -d Ubuntu` on demand.

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
    shrink `.wslconfig`. No fresh distro (install on demand). Keep the tar.

## Decisions taken with the owner

- Accounts: weekly switching via `/login`; Trace Lab first.
- vLLM dropped (no native Windows build); llama.cpp/Ollama if inference is needed later.
- biohub's 81 GB Kaggle data kept under `E:\ML\biohub`.
- blue-ledger gets a private GitHub remote; pyfk-opt pending the owner's answer.
- Stray staging files in `C:\Users\Barat` go to `E:\ML\archive\windows-home-leftovers-2026\`,
  nothing deleted.

## Status 2026-09-04, evening: done

- Export: `E:\Archive\wsl-ubuntu-2026-09-04.tar`, 250.9 GB, 923,193 entries, 20 min. Rollback:
  `wsl --import Ubuntu <dir> <tar>`.
- Extraction natively from the tar (bsdtar; entries carry a `./` prefix, so strip = depth + 1):
  code trees 20 s, 184 GB of ml in under 5 min. Verified file by file: 296,392 regular files
  present with identical sizes (the only difference was `pyfk-opt/.git/config`, changed on
  purpose when its remote was recreated). 160,718 files excluded by policy (.venv, node_modules,
  __pycache__, .pytest_cache, the Linux rclone binary) remain in the tar.
- Symlinks: 239 in the tar; 231 recreated as NTFS symlinks (230 under ProjectDocs, most in
  `kahramanmaras-study-dataset/`, plus `FocoNet/foconet-dataset`); the 8 skipped were
  ClaudeSetup's own links and codex internals. `~/ml` is a junction to `E:\ML`.
- Claude sessions: 828 transcripts (525 Google-Deprem, 293 presser, 6 BarathanAslan,
  4 trace-website) re-keyed to `C--Users-Barat-...`; WSL-era `cwd` fields rewritten; a
  973-turn, 19.5 MB session resumed headlessly on the native CLI and answered.
- Dotfiles: kaggle, rclone (incl. gdrive-rw), gh, ssh keys, seisbench, pyrocko, muse, uv config,
  bash history merged. `.codex` and `.copilot` from WSL preserved beside the Windows ones as
  `~/.codex-from-wsl`, `~/.copilot-from-wsl`. Staged copy kept at
  `E:\Archive\wsl-home-staging-2026-09-04`.
- Repos: git state identical to WSL (FocoNet untracked experiments dir, blue-ledger
  `docs/research.md`, presser's three modified files). pyfk-opt recreated as a private repo with
  main/cpu/cuda. blue-ledger private repo created.
- Environments: FocoNet venv with torch 2.11.0+cu128 sees the RTX 5090 as sm_120; 428 tests pass.
  Remaining failures are the 10 tests that import `pyfk`: the vendored fork ships Cython
  extensions built only for Linux and macOS, so on Windows it needs MSVC Build Tools once
  (`winget install Microsoft.VisualStudio.2022.BuildTools`, C++ workload; admin prompt).
  blue-ledger builds and its dev server is reachable at `localhost:5173`, the blocker that
  survived every WSL session. presser installs and type-checks (two pre-existing TS errors).
- Two Windows portability fixes left uncommitted in FocoNet for review: `webapp/store.py` uses
  `msvcrt` locking where `fcntl` does not exist, and writes the provenance path in POSIX form.
  `PYTHONUTF8=1` is set as a user env var (Python on Windows otherwise reads text as cp1252).
- Windows: WSL distro unregistered (C: 499 GB -> 201 GB used), `E:\wsl-swap.vhdx` deleted,
  `.wslconfig` shrunk to 8 GB/4 GB, Remote-WSL extension and its cache removed, Terminal
  defaults to Git Bash and the Ubuntu profile is gone, stray home files archived under
  `E:\ML\archive\windows-home-leftovers-2026`.
- Docs updated: Google-Deprem `docs/status.md` and three plans, blue-ledger overview/architecture/
  status, presser status and checklist, `E:\ML\README.md`.

Open at hand-over: the OpenSSH `DefaultShell` key (owner runs `set-ssh-shell.cmd` elevated);
`/login` on the native CLI to switch to the Trace Lab account (the copied credential file and the
desktop app's account metadata disagree, so log in fresh); Build Tools for pyfk if the arm-3 corpus
code is needed; on the Macs `cd ~/Projects/ClaudeSetup && git pull && ./setup.sh`.

Addendum, same evening: the OpenSSH `DefaultShell` is set and verified (ssh lands in Git Bash at
`~`; `cuda status/run/win` work from the Mac-side script). One Git Bash quirk found in the process:
over ssh, a shebang script executed through an NTFS symlink fails with "bad interpreter:
Permission denied", so `setup.sh` now copies the box-only helpers (`detach`) into `~/bin` instead
of linking them. Re-run `./setup.sh` after editing them.

## Addendum, late evening: the desktop app's sidebar

The Claude desktop app does not scan `~/.claude/projects`. Its sidebar comes from its own index,
`%APPDATA%\Claude\claude-code-sessions\<account>\<org>\local_<id>.json`, one tree per login, and
only sessions started from the app were in it. The migrated transcripts were therefore invisible.
Fixed by generating an entry for each of the 82 top-level transcripts in every account tree
(`1dc35416/b4f988cc` = the Boğaziçi/Trace Lab login, `abdee200/3d161006` = gmail, plus two minor
trees), repointing the ten dead WSL-remote entries at the local transcripts, and moving the eight
`OneDrive\claude` sessions to where they belong (the game demo to `Projects\blue-ledger`, the PC
and hardware chats to `C:\Claude`). Backup of the index before the change:
`E:\Archive\wsl-home-staging-2026-09-04\claude-code-sessions.bak-*`.

pyfk on Windows: MSVC has no C99 complex arithmetic, which the vendored Cython extension uses
(`pyfk.utils.complex` shims over `complex.h`). Building as C++ removes most errors but not the
`_Dcomplex` ones from that shim, so a real port is needed (std::complex via `libcpp.complex`, or
compile with clang). Build Tools are installed; `cl.exe` 14.44 is present.
