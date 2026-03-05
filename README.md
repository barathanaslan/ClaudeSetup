# ClaudeSetup

Global Claude Code configuration — skills, agents, and preferences. Synced across machines via GitHub.

## Quick Start

```bash
git clone <your-repo-url> ~/Projects/ClaudeSetup
cd ~/Projects/ClaudeSetup
./setup.sh
```

## What's Included

### Skills (auto-triggered background knowledge)
- **workflow** — Architect-delegate pattern: plan in conversation, delegate implementation to background agents
- **project-docs** — Persistent docs/ folder for project memory across sessions
- **gemini-api** — Gemini API rules: respect model names, web-search before coding
- **ml-training** — Training standards: checkpoints, early stopping, metrics, logging
- **apple-ml** — Apple Silicon patterns: PyTorch MPS, MLX

### Agents (background workers)
- **plan-implementer** — Reads a plan file and implements it autonomously (opus)
- **plan-reviewer** — Reviews implementation against plan for correctness (opus)

### CLAUDE.md (always loaded)
Core preferences: working style, environment, documentation requirements.

## Updating

After making changes:
```bash
git add -A && git commit -m "update skills" && git push
```

On other machines:
```bash
cd ~/Projects/ClaudeSetup && git pull && ./setup.sh
```

## Adding New Skills

1. Create `skills/<name>/SKILL.md`
2. Run `./setup.sh`
3. Commit and push
