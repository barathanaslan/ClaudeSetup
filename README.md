# ClaudeSetup

Global Claude Code configuration — skills, commands, settings, and preferences. Synced across machines via GitHub.

## Quick Start

```bash
git clone <your-repo-url> ~/Projects/ClaudeSetup
cd ~/Projects/ClaudeSetup
./setup.sh
```

`setup.sh` symlinks everything into `~/.claude/`.

## What's Included

### CLAUDE.md (always loaded)
Core preferences: architect-delegate working style, Apple Silicon environment, docs/ requirement.

### settings.json (always loaded)
Permissions default mode, theme, effort level, thinking toggle.

### Skills (auto-triggered background knowledge)
- **workflow** — How the user works: architect-delegate pattern (delegate big work, do small work inline) plus the `docs/` folder for persistent project memory
- **skill-creator** — Create, modify, and benchmark skills
- **gemini-api** — Gemini API rules: model names, web-search before coding
- **ml-training** — Training standards: checkpoints, early stopping, metrics, logging
- **apple-ml** — Apple Silicon patterns: PyTorch MPS, MLX

### Commands
- **/init-docs** — Initialize a project with the `docs/` folder structure used by the architect-delegate workflow

## Updating

After making changes:
```bash
git add -A && git commit -m "update" && git push
```

On other machines:
```bash
cd ~/Projects/ClaudeSetup && git pull && ./setup.sh
```

## Adding New Skills

1. Create `skills/<name>/SKILL.md`
2. Run `./setup.sh`
3. Commit and push
