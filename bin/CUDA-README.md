# CUDA box (barathans-5090) — access and wake

Windows 11 + WSL2 PC with an **RTX 5090 32GB**, on the tailnet at `100.95.91.27` (ssh user `barat`,
key auth with `~/.ssh/id_ed25519`). All ML work runs inside WSL (Linux user `barathanaslan`), not
native Windows.

## One command for everything: `~/bin/cuda`

```
cuda status            # up? GPU load? training running? disk space?
cuda on                # wake from power-off or sleep (WoL magic packet), waits for boot
cuda off [--force]     # shut down — refuses if GPU busy / logged in unless --force
cuda sleep [--force]   # suspend to RAM — wakes by any key or `cuda on`
cuda run '<bash>'      # run bash inside WSL, quoting-safe (base64 transport)
cuda win '<cmd>'       # run a Windows cmd command
cuda ssh               # interactive shell (Windows cmd; type `wsl` for Linux)
```

Also: `ssh cuda` works (alias in `~/.ssh/config`).

## Access level

SSH sessions as `barat` carry a **full Administrator token** — the key sits in
`C:\ProgramData\ssh\administrators_authorized_keys` and barat is in the Administrators group.
Service installs, schtasks, HKLM edits all work over ssh. (`net session` is a broken admin probe
on this box; use `[WindowsPrincipal]::IsInRole(Administrator)`.) System-level changes still
require the owner's explicit OK per change.

## Network facts (hard-won, don't re-derive)

- **Tailscale IP `100.95.91.27` is the only TCP path.** The LAN IP (`192.168.1.102`) answers
  ping but Windows Firewall blocks TCP there. SMB hangs over Tailscale — use SFTP/scp only.
- **Wake-on-LAN works** over the LAN broadcast (`192.168.1.255`, MAC `A0:AD:9F:D0:CC:2E`): full
  power-off → `cuda on` → reachable in about 40s, pre-login. Only from inside the home LAN.
- After boot, wait for Tailscale to come up; `cuda on` polls for up to 3 min.

## The wake stack — every layer below must stay set or WoL silently dies

| Layer | Setting | Where |
|---|---|---|
| BIOS | **Power On By PCI-E = Enabled** (was the original blocker) | Advanced → APM Configuration |
| BIOS | ErP Ready = Disabled | same page |
| BIOS | Restore AC Power Loss = Power Off (deliberate; plan-B lever is "Power On" + smart plug) | same page |
| Windows | Fast Startup OFF (`HiberbootEnabled=0`) — hybrid shutdown un-arms the NIC | admin: `REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f` |
| NIC driver | Wake on Magic Packet + Shutdown Wake-On-Lan = Enabled | Realtek 2.5GbE advanced properties |
| Tailscale | Unattended mode ON (connects pre-login) | `tailscale set --unattended=true` (as barat over ssh) |
| Services | sshd + Tailscale StartType = Automatic | already set |

If `cuda on` ever stops working after a BIOS update/CMOS reset or a big Windows update,
re-check this table top to bottom — something reverted.

## Using `cuda` from a new machine

The script is distributed via the ClaudeSetup repo (`./setup.sh` links it into `~/bin`).
The PC only trusts keys in its `authorized_keys`: either reuse the existing `~/.ssh/id_ed25519`
pair or append the new machine's pubkey to `C:\Users\barat\.ssh\authorized_keys` from a machine
that already has access.

## Conventions

- Work in WSL under `~/ml/<project>/` for active training sets; bulk data on `E:`.
- Stage transfers through `scp <file> "cuda:E:/ML/sync/<project>/..."`, then
  `cuda run 'cp /mnt/e/ML/sync/... ~/ml/<project>/...'` (scp can't write into WSL directly).
  Delete the staging copy after ingest.
- When a job finishes, **leave the box on**. Power and storage policy: the cuda-box skill.
