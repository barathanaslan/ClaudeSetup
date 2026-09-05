---
name: cuda-box
description: Access, wake, and use the user's CUDA GPU machine ("barathans-5090", RTX 5090 32GB, native Windows 11, Git Bash shell) on their tailnet. TRIGGER whenever the user mentions the cuda device/box, the tailnet GPU, the 5090, the gaming PC, waking or shutting down the PC, or training on the GPU remotely.
---

# The CUDA box

One GPU machine: `barathans-5090` — RTX 5090 (32GB VRAM), Windows 11, Tailscale IP **100.95.91.27**,
ssh user **barat**, key auth. Usually on; `cuda on` wakes it. Everything runs natively on Windows.
The shell is Git Bash: `~` is `C:\Users\Barat`, `ls`/`grep`/`bash` scripts all work, and an ssh
login lands in it. WSL exists on the machine but holds nothing — never put work there.

## Use the `cuda` helper — don't hand-roll ssh

```
cuda status               # up? GPU load? python procs? detached jobs? disks?
cuda on                   # wake via WoL, polls until reachable
cuda off / cuda sleep     # owner-initiated only — see Power policy
cuda run '<bash>'         # run bash on the box, quoting-safe (base64 transport)
cuda detach '<bash>' [n]  # start a long job that survives disconnect; log in ~/jobs/<n>.log
cuda jobs                 # list detached jobs
cuda win '<cmd>'          # Windows cmd.exe command
cuda ssh                  # interactive bash on the box
```

Full docs: `~/bin/CUDA-README.md`.

## Working on the box

- Home mirrors the Mac home: `~/Google-Deprem/`, `~/Projects/<name>/`. Same paths everywhere.
  Look around with `ls` rather than assuming what is there.
- `~/ml` is a junction to `E:\ML`, the one data root (`datasets/`, `models/`, `bench/`, `corpora/`,
  `outputs/`, `archive/`, `hf-cache/`). It is native NTFS on a 4 TB drive: read and write it
  directly, no staging copies. `HF_HOME` points at `E:\ML\hf-cache`; check it before downloading.
- Transfers from a Mac: `scp <file> cuda:Google-Deprem/...` or `cuda:ml/datasets/...` — paths are
  relative to the real home, nothing to stage or move afterwards.
- Python: `uv`, one venv per project, `source .venv/Scripts/activate`. Torch comes from the cu128
  index. `uv sync` in a project is the only setup step.
- Long runs: `detach '<command>' <name>` on the box, or `cuda detach` from the Mac. A plain
  background `&` dies with the ssh session. `detach list` / `detach tail <name>` / `detach kill <name>`.
- Claude Code on the box: native `claude` in Git Bash; global config comes from
  `~/Projects/ClaudeSetup` via `./setup.sh`. Accounts are switched with `/login`; sessions are
  keyed by folder, not account, so history survives a switch. VS Code opens folders directly.
- Tools: `uv`, `gh`, `node`, `npm`, `rclone`, `claude`, `pwsh`, `git`, `tailmon`. Installs go
  through `winget`; anything needing an admin prompt is the owner's call.
- Paths for Windows-native programs: Git Bash rewrites arguments that look like POSIX paths.
  Prefer `//flag` or `MSYS_NO_PATHCONV=1 <cmd>` when calling cmd-style tools such as `tasklist /FI`.
  PowerShell sent to the box must be ASCII-only (PS 5.1 mangles BOM-less UTF-8 literals).

## Seeing the screen (fallback, owner-driven)

TightVNC runs on the box as service `tvnserver`, port 5900, firewall rule `VNC over Tailscale
only` (100.64.0.0/10), VNC authentication on. From a Mac, `/Applications/CUDA Connection.app`
opens macOS Screen Sharing with the password from `~/.config/cuda-vnc/password`. It mirrors the
console. RDP is not used: the Windows account is Microsoft-account-linked and RDP from a Mac
cannot authenticate against it — don't propose it.

## Storage policy

- C: holds Windows, tools and code. Bulk data lives under `E:\ML`.
- When a project goes dormant, its data moves to `E:\ML\archive\` and derived artifacts (venvs,
  node_modules, quantized copies) are deleted, not archived — keep the script that rebuilds them.
- The old WSL distro is preserved in full at `E:\Archive\wsl-ubuntu-2026-09-04.tar`.

## Power policy

- `cuda on` freely: waking is cheap and harmless.
- `cuda off` / `cuda sleep` are **never agent-initiated**. Change power state only when the user
  explicitly asks in the current conversation. An idle-looking box may still be in use — a desktop
  session, a download, a job between epochs. When in doubt, leave it on.
- If you woke the box for your own task, leave it on afterwards and say so.
- Don't power-cycle as a testing convenience.
- The guard refuses on GPU load, python processes or an active login; `--force` only after the
  user says so.

## Hard rules

- **Never `cuda off` on your own initiative.**
- **Only Tailscale TCP works.** The LAN IP pings but TCP is firewalled. SMB hangs; use scp/SFTP.
- **SSH sessions are full Administrator.** Never make system-level changes (services, registry,
  scheduled tasks, firewall) without the user approving that specific change.
- **No WSL.** Don't start it, don't install into it, don't suggest it unless a task cannot run on
  Windows — and then ask first.
