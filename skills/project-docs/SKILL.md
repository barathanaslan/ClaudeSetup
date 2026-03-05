---
name: project-docs
description: Project documentation pattern using docs/ folder. Apply when starting work on any project, when docs/ doesn't exist, or when project state needs to be captured. This is background knowledge.
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
  overview.md        # What this project is, architecture, how the code works
  progress.md        # What's been done, decisions made, mistakes and fixes, known issues
  roadmap.md         # Where we're going: goals, todo list, priorities
  plans/             # Individual plan files for the architect-delegate workflow
    plan-001-*.md
    plan-002-*.md
```

The file names above are suggestions. Adapt to the project — a small script doesn't need all of these. The principle matters more than the structure.

## Content Guidelines

### overview.md
- What the project does (1-2 paragraphs)
- Architecture: key components, how they connect
- How to run/build/test
- Key dependencies and why they were chosen
- NOT a copy of the code — describe how it works at a level that helps you navigate

### progress.md
- Reverse chronological (newest first)
- Each entry: date, what changed, why
- Include mistakes made and how they were fixed — this prevents repeating them
- Known issues and workarounds
- Keep entries concise — one line per change is fine for small things

### roadmap.md
- The end goal described in detail
- Current priorities (ordered)
- Todo items with rough scope indicators
- Ideas/possibilities that aren't committed yet (separate section)
- Update this as goals evolve — it's a living document

## When to Update
- After implementing a plan: update progress.md and roadmap.md
- After discovering a bug or issue: add to progress.md known issues
- After goals change: update roadmap.md
- After significant architectural decisions: update overview.md
- Don't update on every tiny change — use judgment

## When to Read
- At the start of every new session
- Before creating a plan (to understand current state)
- Before any worker agent starts (part of its context)

## Conciseness
- These docs are read by Claude instances with limited context. Every word must earn its place.
- No boilerplate, no filler, no verbose explanations of obvious things.
- Prefer bullet points over paragraphs.
- If a section grows too long, summarize and archive the details.
