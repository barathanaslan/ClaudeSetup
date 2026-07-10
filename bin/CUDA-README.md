# CUDA box (barathans-5070) — access, wake, and organization

The gaming PC doubles as the household GPU node: **RTX 5070 Ti 16GB**, Windows 11 + WSL2,
on the tailnet at `100.95.91.27` (user `barat`, key auth with `~/.ssh/id_ed25519`).
Set up 2026-07-10. All ML work runs **inside WSL** (`/home/barathanaslan`), not native Windows.

## One command for everything: `~/bin/cuda`

```
cuda status            # up? GPU load? training running? disk space?
cuda on                # wake from full power-off (WoL magic packet), waits for boot
cuda off               # shut down — refuses if GPU busy (override: --force)
cuda run '<bash>'      # run bash inside WSL, quoting-safe (base64 transport)
cuda win '<cmd>'       # run a Windows cmd command
cuda inventory         # regenerate the what-lives-where map
cuda ssh               # interactive shell (Windows cmd; type `wsl` for Linux)
```

Also: `ssh cuda` works (alias in `~/.ssh/config`).

## Access level

SSH sessions as `barat` carry a **full Administrator token** — the key sits in
`C:\ProgramData\ssh\administrators_authorized_keys` and barat is in the Administrators
group. Service installs, schtasks, HKLM edits all work over ssh. (`net session` is a
broken admin probe on this box; use `[WindowsPrincipal]::IsInRole(Administrator)`.)
System-level changes still require the owner's explicit OK per change.

## Network facts (hard-won, don't re-derive)

- **Tailscale IP `100.95.91.27` is the only TCP path.** The LAN IP (`192.168.1.101`)
  answers ping but Windows Firewall blocks TCP there. SMB hangs over Tailscale — use
  SFTP/scp only.
- **Wake-on-LAN works from the Studio** over the LAN broadcast (`192.168.1.255`,
  MAC `A0:AD:9F:D0:CC:2E`). Verified 2026-07-10: full power-off → `cuda on` → reachable
  in ~40s, pre-login. The old "AP isolation blocks WoL" note predates this test.
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

## Using `cuda` from the MacBook (or any non-Studio machine)

The script is distributed via the ClaudeSetup repo (`./setup.sh` links it into `~/bin`).
Two caveats away from the Studio:
- **SSH key**: the PC only trusts keys in its `authorized_keys`. If the MacBook's key
  isn't there yet, either copy the Studio's `~/.ssh/id_ed25519` pair over, or append the
  MacBook's pubkey to `C:\Users\barat\.ssh\authorized_keys` from a machine with access.
- **Waking remotely**: the WoL broadcast only works from inside the home LAN. Away from
  home, relay through the always-on Studio: `ssh barathanaslan@100.80.21.79 'bin/cuda on'`.

## Where things live on the box

| Place | What |
|---|---|
| WSL `~/trendyol`, `~/ft`, `~/judge` | **Trendyol 2026 competition — FROZEN, do not touch** |
| WSL `~/.cache/huggingface` | shared HF model cache (~34G) — all projects reuse this |
| WSL `~/vllmenv`, `~/ftenv` | venvs (vllm / fine-tuning) — Trendyol-era, leave alone |
| WSL `~/ml/<project>/` | **convention for every NEW project** (create as needed) |
| `C:\Users\barat\trendyol_sync` | Mac→PC staging for Trendyol (frozen) |
| `C:\Users\barat\<project>_sync` | staging pattern for new projects (scp lands here, WSL copies in) |
| `E:\Archive` | Studio offload target (see ARCHIVE-README.md) — incl. `ModelArchive/` |

Current snapshot: `~/.claude/skills/cuda-box/references/INVENTORY.md` (regen: `cuda inventory`).

## Conventions for new projects

1. Work in WSL under `~/ml/<project>/{src,data,ckpt,runs}` — never loose in `~`.
2. Point HF at the shared cache (default already) — don't duplicate model downloads.
3. Stage transfers through `C:\Users\barat\<project>_sync`, then `cuda run 'cp ...'`
   into WSL (scp can't write into the WSL filesystem directly).
4. When a job finishes: **leave the box on** and let the owner decide about power.
   `cuda off` is owner-initiated only (or pre-authorized per task); the guard refuses
   on GPU load, training procs, or an active login session. Minimize on/off churn.
5. Cold artifacts → drop into Studio `~/Outbox` → they land in `E:\Archive`.

## ⚠️ Trendyol 2026 (until the competition ends)

`~/Projects/Trendyol2026` on the Mac has its own scripts (`gpu.sh`, `sync_to_gpu.sh`,
`orchestrate*.sh`) that talk to this box directly. **Do not modify them, and do not
move/rename anything they depend on** (everything in the table above marked frozen,
plus the loose parquets/scripts in `C:\Users\barat`). The `cuda` command is additive
and independent — both can coexist.
