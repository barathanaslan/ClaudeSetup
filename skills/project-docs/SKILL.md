---
name: project-docs
description: Project documentation pattern using docs/ folder. Apply when starting work on any project, when docs/ doesn't exist, when the user returns after a break, or when project state needs to be captured. TRIGGER when the user says "what's the status", "bring me up to speed", "I'm picking this back up", "create docs", "update the progress", "where were we", or starts a new session on an existing project. This is background knowledge.
user-invocable: false
---

# Project Documentation (docs/)

Every project must have a `docs/` folder that serves as persistent memory for both the user and Claude across sessions.

## Purpose
- Survive context resets and conversation compaction
- Bridge time gaps when the user returns to a project after days/weeks
- Give any fresh Claude instance full project context without prior conversation history
- Replace the need to re-explain the project every session

## Structure

```
docs/
  overview.md    # What this project is, architecture, constraints. Updated rarely.
  status.md      # Current snapshot: what's done, in progress, next, blocked. Overwritten each update.
  plans/         # Individual plan files for the architect-delegate workflow
    plan-001-*.md
    plan-002-*.md
  notes/         # Optional. Research, references, scratch. Only created when needed.
```

Two files and one working directory. A small script may only need `overview.md`. The principle matters more than the structure.

## Content Guidelines

### overview.md
- What the project does (1-2 paragraphs)
- Architecture: key components, how they connect
- How to run/build/test
- Key dependencies and why they were chosen
- NOT a copy of the code — describe how it works at a level that helps you navigate
- Updated rarely — only when architecture or goals fundamentally change

### status.md
- **Always reflects current state** — update in place, don't append history
- Must fit on one screen (under ~40 lines)
- Sections: Done (completed milestones), In Progress, Next (priorities), Blocked/Known Issues
- When something changes, update the relevant section — no need to rewrite the whole file
- History lives in git and plan files — status.md only reflects *right now*

### notes/ (optional)
- Only create when there's something worth saving: research findings, external references, debugging notes
- No placeholder files — if the directory is empty, don't create it

## When to Update
- **status.md**: Only the architect (main conversation) updates this. Not worker agents. Update the relevant sections after a plan cycle completes — not after every small change.
- **overview.md**: After significant architectural decisions. Rare.
- Don't update on every tiny change — use judgment

## When to Read
- At the start of every new session
- Before creating a plan (to understand current state)
- Before any worker agent starts (part of its context)

## Migrating Old Structure
If a project has the old structure (progress.md, roadmap.md), consolidate them into status.md:
1. Extract current state from progress.md (recent entries, known issues) and roadmap.md (priorities, next steps)
2. Write a single status.md snapshot
3. Delete progress.md and roadmap.md
4. Git history preserves the old content

## Conciseness
- These docs are read by Claude instances with limited context. Every word must earn its place.
- No boilerplate, no filler, no verbose explanations of obvious things.
- Prefer bullet points over paragraphs.
- If a section grows too long, summarize and archive the details.
