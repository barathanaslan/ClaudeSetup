# ClaudeSetup

Global Claude Code configuration — CLAUDE.md, settings, skills, commands and the `cuda` helper.
Synced across machines via GitHub.

## Quick Start

```bash
git clone git@github.com:barathanaslan/ClaudeSetup.git ~/Projects/ClaudeSetup
cd ~/Projects/ClaudeSetup
./setup.sh
```

`setup.sh` symlinks everything into `~/.claude/` and `bin/*` into `~/bin/`.

## What's Included

- **CLAUDE.md** — working style, the machines, layout and tools on the cuda box.
- **settings.json** — permissions mode, theme, effort level.
- **skills/cuda-box** — the tailnet GPU box: `~/bin/cuda`, storage and power policy.
- **skills/ml-training** — training standards: checkpoints, early stopping, metrics, logging.
- **skills/skill-creator** — create, modify and benchmark skills.
- **commands/init-docs** — `/init-docs` creates the `docs/` folder structure.
- **bin/cuda**, **bin/CUDA-README.md** — the box helper and its docs.

## Updating

```bash
git add -A && git commit -m "update" && git push
```

On other machines:
```bash
cd ~/Projects/ClaudeSetup && git pull && ./setup.sh
```
