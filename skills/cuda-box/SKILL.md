---
name: cuda-box
description: Access, wake, and use the user's CUDA GPU machine (gaming PC "barathans-5070", RTX 5070 Ti 16GB, Windows 11 + WSL2) on their tailnet. TRIGGER whenever the user mentions the cuda device/box, the tailnet GPU, the 5070, the gaming PC, waking or shutting down the PC, training on the GPU remotely, or where model weights/checkpoints live on that machine.
---

# The CUDA box

One GPU machine exists: `barathans-5070` — RTX 5070 Ti (16GB VRAM), Windows 11 + WSL2 (Ubuntu),
Tailscale IP **100.95.91.27**, user **barat**, passwordless key auth (`~/.ssh/id_ed25519`).
It is usually **powered off** (idle wattage); the Mac Studio is the always-on machine.

## Use the `cuda` helper — don't hand-roll ssh

```
cuda status            # up? GPU load? training procs? disks?
cuda on                # wake from power-off via WoL, polls until reachable (~40s typical)
cuda off               # shutdown — self-guards: refuses if GPU busy (--force overrides)
cuda run '<bash>'      # run bash INSIDE WSL (all ML lives there), quoting-safe
cuda win '<cmd>'       # Windows cmd command
cuda inventory         # regenerate references/INVENTORY.md (what lives where)
```

`ssh cuda` also works (alias in ~/.ssh/config) but lands in Windows cmd — ML work is in WSL,
so prefer `cuda run`. Full docs: `~/bin/CUDA-README.md`.

## Standard workflow for a training task

1. `cuda status` — if off, `cuda on` (takes under a minute; tell the user if it fails —
   they may need to press the power button once).
2. Work in WSL under `~/ml/<project>/` (create it; never scatter files in WSL `~`).
3. Transfer files: `scp <file> cuda:<project>_sync/...` (lands in `C:\Users\barat`), then
   `cuda run 'cp /mnt/c/Users/barat/<project>_sync/... ~/ml/<project>/...'`.
   scp cannot write into the WSL filesystem directly.
4. HuggingFace cache is shared at WSL `~/.cache/huggingface` (~34G) — models are probably
   already there; check before downloading.
5. Long runs: launch with `nohup ... &` inside `cuda run`, poll with `cuda run 'tail ...'`.
6. When done: **leave the box on** and tell the user it's running. See Power policy.

## Power policy (the owner was explicit about this — 2026-07-10)

- `cuda on` freely: waking is cheap and harmless (works from full-off AND sleep).
- `cuda off` and `cuda sleep` are **never agent-initiated**. Change power state only when
  the user explicitly asks in the current conversation, or pre-authorized it for this
  specific task. An idle-looking box may still be in use — a desktop session, a download,
  a job between epochs. When in doubt, leave it on.
- When the user does authorize powering down and expects to return soon, prefer
  `cuda sleep` (suspend to RAM: ~2s resume by any key at the desk) over `cuda off`.
- If you woke the box for your own task, the default after finishing is ON + inform the
  user — never "clean up" by powering it down.
- Don't power-cycle as a testing convenience. On/off churn wears the hardware and annoys
  the owner; batch your work while it's up.
- The `cuda off` guard refuses on GPU load, WSL training processes, or an active login
  session; `--force` exists but only use it after the user says so.

## Hard rules

- **Trendyol 2026 is FROZEN until the competition ends**: WSL `~/trendyol`, `~/ft`, `~/judge`,
  venvs `~/vllmenv`/`~/ftenv`, everything loose in `C:\Users\barat` (parquets, train_*.py,
  `trendyol_sync`), and the Mac-side `~/Projects/Trendyol2026/scripts/*` (gpu.sh, sync_to_gpu.sh,
  orchestrate*.sh). Read them for reference; never modify, move, or "clean up".
- **Never `cuda off` on your own initiative** — see Power policy above. The guard is a
  safety net, not permission.
- **Only Tailscale TCP works.** LAN IP 192.168.1.101 pings but TCP is firewalled. SMB hangs;
  use scp/SFTP. Don't burn time re-deriving this.
- Windows-side HF cache is empty by design — weights live in WSL.
- **SSH sessions are FULL ADMINISTRATOR** (key in `administrators_authorized_keys`; verified
  2026-07-10 with the owner's blessing). Registry, services, schtasks all work remotely.
  With that power: never make system-level changes (services, HKLM, scheduled tasks,
  firewall) without the user explicitly approving that specific change. Don't trust
  `net session` as an admin probe — it false-negatives; use the WindowsPrincipal check.
- PowerShell scripts sent to this box must be ASCII-only (PS 5.1 + BOM-less UTF-8 = mangled
  string literals).

## Related

- What's on the box right now: [references/INVENTORY.md](references/INVENTORY.md)
  (regen with `cuda inventory` when it looks stale).
- Cold storage / archive offload: `~/bin/ARCHIVE-README.md` (Studio `~/Outbox` →
  `E:\Archive` on this same PC; `archive-ls.sh` / `archive-get.sh` to browse/retrieve).
- Archived model weights: `E:\Archive\ModelArchive\` (e.g. phonetic-whisper-mlx).
