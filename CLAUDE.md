# Global Preferences

## Working style

- Think the approach through with me before large or multi-step changes; small changes, just do them.
- Agents are fine for bulk work, but review what they produce yourself before accepting it.
- Substantial projects keep a `docs/` folder (`overview.md`, `status.md`, `plans/`). Read it at the start of a session and keep `status.md` current. `/init-docs` creates one.

## Machines

- **cuda box** — Windows 11 PC with an RTX 5090, Tailscale `barathans-5090`. All work on it happens in WSL2 Ubuntu; Windows is only the host. From a Mac it is managed through `~/bin/cuda`; details are in the `cuda-box` skill.
- **Macs** (Mac mini, MacBook) — where I develop. No CUDA: PyTorch uses MPS. Anything that needs the GPU or the big data runs on the box over SSH.

## Layout on the box

- The WSL home mirrors the Mac home: `~/Google-Deprem/` (seismology, my main job) and `~/Projects/<name>/` (everything else). Same paths on every machine; look around instead of assuming.
- `~/ml/<project>/` — active training working sets only (fast ext4). Bulk data lives on `E:` (`/mnt/e`, slow drvfs) and the large project subtrees are symlinks into it. Keep the WSL disk lean.

## Tools on the box

- Python via `uv`, one venv per project. Torch from the cu128 index (the 5090 is sm_120).
- `gh`, `rclone`, `node`, `claude` are installed in WSL. `sudo` needs my password; ask before `apt`.
- Stats for any tailnet machine: `tailmon json`.

## Rules on the box

- Never shut down or sleep the box unless I ask for it in the current conversation.
- WSL stops when the last `wsl.exe` session exits, taking background jobs with it. Long jobs run inside `tmux`.
- No changes to Windows services, registry, firewall or scheduled tasks without asking.
