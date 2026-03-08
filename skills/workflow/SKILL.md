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
- Plans must be self-contained: a fresh Claude instance with no prior context must be able to implement it by reading only the plan file and the docs/ folder
- Include: objective, files to create/modify, step-by-step instructions, acceptance criteria, what NOT to do

### 2. Delegate Implementation
- After the user confirms the plan, use the `plan-implementer` agent to execute it
- The `plan-implementer` agent is defined in `~/.claude/agents/plan-implementer.md` and will be auto-triggered when you recognize the pattern of a confirmed plan ready for implementation
- Spawn it in the background using the Agent tool with `run_in_background: true`
- Use `subagent_type: "general-purpose"` (custom agent names cannot be used as subagent_type — they are auto-discovered via description matching)
- The prompt MUST include:
  - The plan file path
  - Instruction to read `docs/` for project context first
  - Instruction to update `docs/` after completing the work
  - Full role instructions (the agent gets a fresh context with no memory)

**Spawn the worker:**
```
Agent tool call:
  subagent_type: "general-purpose"
  run_in_background: true
  prompt: |
    You are an expert implementation engineer. Your job is to execute a plan precisely.

    PLAN: Read the plan at docs/plans/plan-NNN-<name>.md
    CONTEXT: Read docs/ folder (overview.md, status.md) first.

    Process:
    1. Read context and plan fully before writing any code
    2. Implement each step in order — no placeholders, no TODOs
    3. Run/test the code if possible
    4. Do NOT update docs/status.md — the architect handles that
    5. Report: what was done, any issues, any deviations from plan

    Rules:
    - Do NOT ask questions — make reasonable decisions
    - Do NOT leave code in a broken state
    - Use MPS for PyTorch, not CUDA (Apple Silicon machine)
    - Save model checkpoints if writing training code
```

### 3. Review
- When the worker finishes, read its summary
- If changes are non-trivial, use the `plan-reviewer` agent (defined in `~/.claude/agents/plan-reviewer.md`)
- Same spawning pattern — `general-purpose` with review instructions:

```
Agent tool call:
  subagent_type: "general-purpose"
  run_in_background: true
  prompt: |
    You are an expert code reviewer. Verify the implementation against its plan.

    PLAN: Read docs/plans/plan-NNN-<name>.md
    CONTEXT: Read docs/ folder (overview.md, status.md).

    Check:
    1. Every plan step — was it done?
    2. Every acceptance criterion — is it met?
    3. Code correctness — bugs, logic errors, edge cases
    4. For ML code: checkpoints saved? Metrics logged? Early stopping?
    5. Does it work on Apple Silicon (MPS, not CUDA)?
    6. Did the worker avoid modifying docs/status.md? (architect handles that)

    Return: PASS / PASS WITH NOTES / FAIL, with specific issues and file:line references.
    Do NOT modify any code — read-only review.
```

- If issues are found, either fix inline (if trivial) or spawn another worker with fix instructions

### 4. Update & Continue
- Confirm completion to the user with a brief summary
- Update `docs/status.md` to reflect current state — only the architect does this, after reviewing worker results
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

## How Agent Triggering Works

- Custom agents in `~/.claude/agents/` are auto-discovered by Claude Code
- They are triggered by **description matching**: when the conversation context matches the examples in the agent's `description` field, Claude recognizes the pattern and spawns the agent
- They are NOT selectable via `subagent_type` — only built-in types (`general-purpose`, `Explore`, `Plan`) work there
- For reliable delegation, use `subagent_type: "general-purpose"` with the full role prompt embedded
- Use `run_in_background: true` to keep the main conversation responsive
- Each agent gets its own fresh context window — put everything it needs in the prompt + referenced files

## Critical Rules
- Multi-step plans are delegated to background agents because the main conversation should stay responsive and strategic — the architect doesn't lay bricks. Don't implement plans in this conversation.
- Plans must be written to files so worker agents (which have fresh context and no memory of this conversation) can read them independently.
- Worker agents are disposable — put everything they need in the plan + docs/.
- If a plan is too large for one agent, break it into sequential sub-plans.
- After every plan cycle, update docs/status.md to reflect what changed — this is the shared memory that survives across sessions.
