# Global Preferences

## Working style

- Think the approach through with me before large or multi-step changes; small changes, just do them.
- Agents are fine for bulk work, but review what they produce yourself before accepting it.
- Substantial projects keep a `docs/` folder (`overview.md`, `status.md`, `plans/`). Read it at the start of a session and keep `status.md` current. `/init-docs` creates one.

## Machines (as of 2026-09)

- **cuda box** — Windows 11 PC, Tailscale `barathans-5090` (100.95.91.27), LAN 192.168.1.102. RTX 5090 32 GB, Ryzen 9 7900, 64 GB RAM. All development and ML work happens in **WSL2 Ubuntu** (user `barathanaslan`); the Windows side (user `barat`) is only the host. Wake-on-LAN works (`cuda on` from a Mac). Usually on.
- **MacBook** (`barathans-macbook-1`, 100.80.159.96) — the laptop. Works on the box over SSH: `ssh cuda` lands in Windows cmd, type `wsl`; `cuda run '<bash>'` runs a command inside WSL. Obsidian vault lives here.
- **Mac mini** — arriving around 2026-09-22; becomes the main development machine, same SSH pattern as the MacBook. The box stays the GPU machine.
- **Mac Studio** — sold 2026-09-02. Its archive is `E:\Archive\studio-2026-09\` on the box and the `studio-2026-09` folder on Google Drive; `contract/BOOTSTRAP.md` there explains how to restore onto a Mac.

## Layout on the box (WSL)

- `~/Google-Deprem/` — the seismology project, code tree on ext4. Git repos live inside it (`FocoNet/` → github `seismicbundle/FocoNet`). Large data subtrees (`FocoNet/out/*`, `FocoNet/foconet-dataset`, `FocoNet/benchmarks`, `ProjectDocs/*`, `analytic-corpus/out/*`, `analytic-corpus-v3`, `wf-experiments/evals|experiments/*`, `docs/research`) are symlinks into `/mnt/e/ML/studio/Google-Deprem/…`.
- `~/Projects/<name>/` — every other project (`Bosphorify/presser` → github `bosphorify/presser`, `ClaudeSetup`, …). Same paths as on the Macs.
- `~/ml/<project>/` — active training working sets on ext4. Copy data in before a hot training loop; `/mnt/e` is slow drvfs and fine only for reading archives or writing results.
- `E:\ML\` (`/mnt/e/ML`): `studio/` unpacked Mac Studio data, `sync/` scp staging from the Macs, `datasets/`, `outputs/`. `E:\Archive\`: cold storage. C: holds the WSL disk image, which grows and never shrinks, so bulk data goes to E:.

## Tools on the box

- Python: `uv` for venvs, one per project. Torch must come from `https://download.pytorch.org/whl/cu128` (the 5090 is sm_120). System `python3` is 3.12.
- Node via nvm (LTS). `gh`, `rclone`, `zstd`, `tailscale`, `claude` are installed in WSL; `gh` and `rclone` live in `~/.local/bin`.
- rclone remotes: `pc-archive` (this box over SFTP, for the Macs), `gdrive-rw` (Google Drive, read-write), `colabdrive` (Drive, read-only).
- HuggingFace cache: `~/.cache/huggingface` in WSL.
- `sudo` needs a password. Ask me before `apt` installs.
- Machine stats for any tailnet machine: `tailmon json` or `http://<tailscale-ip>:7020/stats`.
- Primary LLM API: Google Gemini. Primary ML framework: PyTorch (CUDA here, MPS on the Macs; MLX on the Macs when it fits).

## Rules on the box

- Never shut down or sleep the box unless I ask for it in the current conversation.
- WSL stops when the last `wsl.exe` session exits, taking background jobs with it. Run long jobs inside `tmux`, or keep an SSH session open.
- No changes to Windows services, registry, firewall or scheduled tasks without asking.

## On a Mac

- No local CUDA: PyTorch uses MPS, MLX when it fits. Anything that needs the GPU or the corpora runs on the box over SSH.
- Manage the box only through `~/bin/cuda` (`status` / `on` / `run`); see the `cuda-box` skill.
