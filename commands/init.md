---
description: Initialize project with docs/ folder and architect-delegate workflow
---

Initialize this project for the architect-delegate workflow.

## Step 1: Check existing state

Check if `docs/` folder already exists. If it does, read all files in it and skip to Step 4.

## Step 2: Explore the project

Read the project structure (files, directories, any README, any existing documentation, config files, package.json/pyproject.toml/etc.) to understand what this project is about.

## Step 3: Create docs/ folder

Create the following structure:

- `docs/overview.md` — What the project does, architecture, key components, how to run/build/test, key dependencies. Populate this from what you learned in Step 2. Be concise.
- `docs/progress.md` — Start with current date and "Project initialized with docs/ folder." If the project already has history (git log, existing code), summarize the current state.
- `docs/roadmap.md` — If the user has described goals, capture them here. Otherwise, create with a placeholder asking the user to describe the end goal.
- `docs/plans/` — Empty directory for plan files.

## Step 4: Report

Tell the user:
- What was created/found
- A brief summary of the project as you understand it
- Ask if the overview is accurate and if they want to describe/update the project goals for the roadmap

Keep all docs concise. Every word must earn its place. No boilerplate.
