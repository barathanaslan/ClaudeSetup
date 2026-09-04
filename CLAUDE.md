# Global Preferences

## Working style

- Think the approach through with me before large or multi-step changes; small changes, just do them.
- Agents are fine for bulk work, but review what they produce yourself before accepting it.
- Substantial projects keep a `docs/` folder (`overview.md`, `status.md`, `plans/`). Read it at the start of a session and keep `status.md` current. `/init-docs` creates one.

## Machines

- **cuda box** — Windows 11 PC with an RTX 5090, Tailscale `barathans-5090`. Everything runs natively on Windows; the shell is Git Bash, both locally and as the `ssh` landing shell. WSL is installed but holds nothing of mine — don't put work in it. From a Mac it is managed through `~/bin/cuda`; details are in the `cuda-box` skill.
- **Macs** (Mac mini, MacBook) — where I develop. No CUDA: PyTorch uses MPS. Anything that needs the GPU or the big data runs on the box over SSH.

## Layout on the box

- Home is `C:\Users\Barat`, which is `~` in Git Bash and over ssh, and it mirrors the Mac home: `~/Google-Deprem/` (seismology, my main job) and `~/Projects/<name>/` (everything else). Same paths on every machine; look around instead of assuming.
- `~/ml` is a junction to `E:\ML`, the single data root: `datasets/`, `models/`, `bench/`, `corpora/`, `outputs/`, `archive/`, `hf-cache/`. Native NTFS is fast; there is no hot/cold split any more.
- C: is for the OS and code. Anything above a few GB goes under `E:\ML`.

## Tools on the box

- Python via `uv`, one venv per project (`.venv/Scripts/python.exe`; `source .venv/Scripts/activate` in Git Bash). Torch from the cu128 index (the 5090 is sm_120).
- `uv`, `gh`, `node`, `rclone`, `claude`, `pwsh` are native Windows installs. New software goes through `winget`; ask before anything that needs an admin prompt.
- Stats for any tailnet machine: `tailmon json`.

## Rules on the box

- Never shut down or sleep the box unless I ask for it in the current conversation.
- Windows kills every child of an ssh session when the connection drops. Long jobs run through `detach` (cuda-box skill), never in the foreground of an ssh session.
- No changes to Windows services, registry, firewall or scheduled tasks without asking.
- Don't use WSL for my projects. If a task genuinely needs Linux, say so first.
