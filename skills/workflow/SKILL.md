---
name: workflow
description: How the user likes to work — architect-delegate pattern and the docs/ folder for project memory. Background knowledge. Relevant when planning multi-step work, deciding whether to delegate to a background agent, or managing persistent project context. TRIGGER on "implement this", "go ahead", "delegate this", "spawn a worker", "let's plan this out", "what's the status", "where were we", "bring me up to speed", "create docs", or starting a new session on an existing project.
user-invocable: false
---

# Working Style: Architect-Delegate & Project Docs

The user prefers to keep the main conversation strategic — discussing goals, exploring approaches, planning, and reviewing — while heavier implementation runs in background agents. This is a preference, not a hard rule: use judgment.

## When to delegate vs. do it inline

- **Just do it inline**: small edits, quick fixes, single-file changes, exploration, anything faster to finish than to delegate. Don't spin up an agent for a one-line change.
- **Delegate to a background agent**: large or multi-step implementation, work that would flood this conversation with detail, or anything that benefits from a fresh context window. Keep the strategic thread clean and report back a short summary.

Newer models are good at judging this. Lean toward acting directly when the task is small; reach for delegation when scale or context pressure justifies it.

## The delegate pattern (when it applies)

### 1. Plan
- When direction is clear and the work is substantial, write a self-contained plan to `docs/plans/plan-NNN-<short-name>.md` — a fresh agent should be able to implement it from the plan plus `docs/` alone.
- Include: objective, files to touch, step-by-step instructions, acceptance criteria, and what NOT to do.

### 2. Delegate
```
Agent tool call:
  description: "Implement plan NNN"
  run_in_background: true
  model: opus
  prompt: "Read ~/.claude/agents/plan-implementer.md and follow those instructions. Execute the plan at docs/plans/plan-NNN-<name>.md"
```

### 3. Review (for substantial work)
```
Agent tool call:
  description: "Review plan NNN"
  run_in_background: true
  model: opus
  prompt: "Read ~/.claude/agents/plan-reviewer.md and follow those instructions. Review the implementation of docs/plans/plan-NNN-<name>.md"
```
Fix issues inline if trivial, or send the implementer back with fix instructions.

### 4. Continue
- Confirm completion with a brief summary and update `docs/status.md`.

## Plan File Format

```markdown
# Plan NNN: <Title>

## Objective
<What we're trying to achieve and why>

## Context
- Read: docs/ for project background
- Key files: <list relevant files>

## Steps
1. <Concrete step with file paths and specifics>

## Acceptance Criteria
- [ ] <What must be true when done>

## Constraints
- <What NOT to do, gotchas, edge cases>
```

# Project Docs (docs/)

A `docs/` folder is persistent memory for both the user and Claude across sessions — it survives context resets, bridges time gaps, and gives a fresh Claude instance full context without re-explanation. Use it for projects substantial enough to benefit; skip it for throwaway work.

## Structure

```
docs/
  overview.md    # What this project is, architecture, constraints. Updated rarely.
  status.md      # Current snapshot: done / in progress / next / blocked. Overwritten in place.
  plans/         # Plan files for the architect-delegate workflow
  notes/         # Optional. Research, references, scratch. Only when needed.
```

The principle matters more than the structure — a small project may need only `overview.md`.

## Content Guidelines

- **overview.md** — what it does (1–2 paragraphs), architecture and how components connect, how to run/build/test, key dependencies. Describes how it works, not a copy of the code. Updated rarely.
- **status.md** — always reflects *right now*; update in place, don't append history (git holds history). Under ~40 lines. Sections: Done, In Progress, Next, Blocked/Known Issues.
- **notes/** — only when there's something worth saving. No placeholder files.

## When to read / update

- **Read**: at the start of a session, before planning, and as part of a worker agent's context.
- **Update**: the main conversation (architect) maintains `status.md`, not worker agents — after a cycle completes, not after every tiny change. `overview.md` only on significant architectural changes.

## Conciseness

These docs are read by Claude instances with limited context. Every word earns its place — bullets over paragraphs, no boilerplate, summarize and archive sections that grow too long.
