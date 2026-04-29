---
description: Initialize project with docs/ folder and architect-delegate workflow
---

Initialize this project for the architect-delegate workflow.

## Step 1: Check existing state

Check if `docs/` folder already exists.

- **If docs/ exists with the current structure** (overview.md, status.md): read all files and skip to Step 4.
- **If docs/ exists with the old structure** (progress.md, roadmap.md): read all files, then go to Step 2b.
- **If docs/ doesn't exist**: go to Step 2a.

## Step 2a: New project — Explore and create

Read the project structure (files, directories, README, config files, package.json/pyproject.toml/etc.) to understand what this project is about. Then create the docs:

- `docs/overview.md` — What the project does, architecture, key components, how to run/build/test, key dependencies. Populate from what you learned. Be concise.
- `docs/status.md` — Current snapshot: what's done, in progress, what's next, blockers. If the project has history (git log, existing code), summarize the current state. Otherwise start with "Project initialized."
- `docs/plans/` — Empty directory for plan files.

Do NOT create `docs/notes/` — it's only created when there's something to put in it.

## Step 2b: Existing project — Migrate old structure

Consolidate the old docs into the new structure:

1. Read progress.md and roadmap.md fully
2. Create `docs/status.md`: extract current state from progress.md (recent entries, known issues) and roadmap.md (priorities, next steps) into a single snapshot
3. Update `docs/overview.md` if it needs refreshing
4. Delete progress.md and roadmap.md (git history preserves them)
5. Ensure `docs/plans/` exists

## Step 3: Report

Tell the user:
- What was created/found/migrated
- A brief summary of the project as you understand it
- Ask if the overview is accurate and if they want to describe/update the project goals

Keep all docs concise. Every word must earn its place. No boilerplate.
