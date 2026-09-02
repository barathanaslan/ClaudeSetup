---
name: cuda-box
description: Access, wake, and use the user's CUDA GPU machine ("barathans-5090", RTX 5090 32GB, Windows 11 + WSL2) on their tailnet. TRIGGER whenever the user mentions the cuda device/box, the tailnet GPU, the 5090, the gaming PC, waking or shutting down the PC, or training on the GPU remotely.
---

# The CUDA box

One GPU machine: `barathans-5090` — RTX 5090 (32GB VRAM), Windows 11 + WSL2 Ubuntu, Tailscale IP
**100.95.91.27**, ssh user **barat**, key auth. Usually on; `cuda on` wakes it. Everything happens
inside WSL (Linux user `barathanaslan`); Windows is only the host.

## Use the `cuda` helper — don't hand-roll ssh

```
cuda status            # up? GPU load? training procs? disks?
cuda on                # wake via WoL, polls until reachable
cuda off / cuda sleep  # owner-initiated only — see Power policy
cuda run '<bash>'      # run bash inside WSL, quoting-safe
cuda win '<cmd>'       # Windows cmd command
cuda ssh               # interactive shell (Windows cmd; type `wsl` for Linux)
```

Full docs: `~/bin/CUDA-README.md`.

## Working on the box

- The WSL home mirrors the Mac home: `~/Google-Deprem/`, `~/Projects/<name>/`. Same paths
  everywhere. Look around with `ls` rather than assuming what is there.
- `~/ml/<project>/` — active training working sets only, on fast ext4. Bulk data is on `E:`
  (`/mnt/e`), slow drvfs: fine for reading archives and writing results, never for a hot training
  loop's data — copy into `~/ml` first. Large project subtrees are symlinks into `/mnt/e`; don't
  run recursive tools (pytest, grep -r, du) over them without need.
- HuggingFace cache: WSL `~/.cache/huggingface`, shared — check before downloading.
- Transfers from a Mac: `scp <file> "cuda:E:/ML/sync/<project>/..."`, then
  `cuda run 'cp /mnt/e/ML/sync/... ~/ml/<project>/...'`. scp cannot write into WSL directly.
  Delete staging copies after ingest.
- Long runs: inside `tmux` in WSL, or keep the ssh session open — WSL2 stops the distro seconds
  after the last `wsl.exe` session exits and takes background jobs with it.
- Claude Code on the box: `claude` inside WSL; global config comes from `~/Projects/ClaudeSetup`
  via `setup.sh`. VS Code: Remote - WSL.
- Tools in WSL: `uv`, `python3`, Node + `npm`, `gh`, `rclone`, `zstd`, `claude`. `sudo` needs the
  owner's password — ask before `apt`.

## Storage policy

C: holds Windows and the WSL `ext4.vhdx`, which grows but never shrinks. Keep WSL lean:

- Bulky things not in active use live on `E:` (`E:\ML\datasets`, `E:\ML\outputs`, `E:\Archive`).
- When a project goes dormant, move the originals to E: and delete them from WSL. Derived
  artifacts (quantized copies, venvs) get deleted, not archived — keep the script that rebuilds them.
- After big deletions inside WSL, C: only recovers space via vhdx compaction (`wsl --shutdown`,
  then `Optimize-VHD`). Needs an idle box and the owner's go-ahead.

## Power policy

- `cuda on` freely: waking is cheap and harmless.
- `cuda off` / `cuda sleep` are **never agent-initiated**. Change power state only when the user
  explicitly asks in the current conversation. An idle-looking box may still be in use — a desktop
  session, a download, a job between epochs. When in doubt, leave it on.
- If you woke the box for your own task, leave it on afterwards and say so.
- Don't power-cycle as a testing convenience.
- The guard refuses on GPU load, training processes or an active login; `--force` only after the
  user says so.

## Hard rules

- **Never `cuda off` on your own initiative.**
- **Only Tailscale TCP works.** The LAN IP pings but TCP is firewalled. SMB hangs; use scp/SFTP.
- **SSH sessions are full Administrator.** Never make system-level changes (services, registry,
  scheduled tasks, firewall) without the user approving that specific change.
- PowerShell sent to the box must be ASCII-only (PS 5.1 mangles BOM-less UTF-8 literals).
