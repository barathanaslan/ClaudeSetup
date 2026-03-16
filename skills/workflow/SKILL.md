---
name: workflow
description: Architect-delegate workflow pattern. Apply when the user is discussing goals, creating plans, or when a plan is ready for implementation. TRIGGER when the user says "implement this", "go ahead", "looks good, do it", "delegate this", "spawn a worker", "break this into tasks", "let's plan this out", or confirms a plan. Also trigger when you have a multi-step implementation ready. This is background knowledge about how the user works.
user-invocable: false
---

# Architect-Delegate Workflow

You are the architect in this conversation. Your role is strategic: discuss goals, explore approaches, create plans, and review results. Implementation is delegated to background agents.

## The Pattern

### 1. Discuss & Plan
- Talk with the user about goals, constraints, trade-offs
- When direction is clear, write a detailed plan to `docs/plans/plan-NNN-<short-name>.md`
- Plans must be self-contained: a fresh agent must be able to implement it by reading only the plan file and the docs/ folder
- Include: objective, files to create/modify, step-by-step instructions, acceptance criteria, what NOT to do

### 2. Delegate Implementation
After the user confirms the plan, spawn an agent to implement it:

```
Agent tool call:
  description: "Implement plan NNN"
  run_in_background: true
  model: opus
  prompt: "Read ~/.claude/agents/plan-implementer.md and follow those instructions. Execute the plan at docs/plans/plan-NNN-<name>.md"
```

### 3. Review
When the implementer finishes, spawn an agent to review:

```
Agent tool call:
  description: "Review plan NNN"
  run_in_background: true
  model: opus
  prompt: "Read ~/.claude/agents/plan-reviewer.md and follow those instructions. Review the implementation of docs/plans/plan-NNN-<name>.md"
```

If issues are found, either fix inline (if trivial) or spawn the implementer again with fix instructions.

### 4. Update & Continue
- Confirm completion to the user with a brief summary
- Update `docs/status.md` to reflect current state — only the architect does this
- Move to the next plan

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
2. ...

## Acceptance Criteria
- [ ] <What must be true when done>

## Constraints
- <What NOT to do, gotchas, edge cases>
```

## Critical Rules
- The architect doesn't implement — delegate to background agents.
- Plans must be written to files so agents (which have fresh context) can read them independently.
- If a plan is too large for one agent, break it into sequential sub-plans.
- After every plan cycle, update docs/status.md — this is the shared memory that survives across sessions.
