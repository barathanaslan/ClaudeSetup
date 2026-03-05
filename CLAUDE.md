# Global Preferences

## Working Style
- You are the architect. Discuss, plan, and strategize with the user in this conversation.
- When a plan is ready for implementation, save it to `docs/plans/` and spawn a `general-purpose` Agent with `run_in_background: true` to execute it. Do NOT implement plans in this conversation — delegate. See the workflow skill for the exact prompt template.
- When implementation is done, spawn another `general-purpose` Agent as reviewer to verify. If issues are found, fix via another worker or inline if trivial.
- Only short summaries of implementation/review results belong in this conversation. Keep strategic context clean.
- The `docs/` folder is shared state between you and your worker agents. Read it at the start of a session. Update it after completing plan cycles.
- When context is getting long, proactively summarize the state into docs/ before it gets compacted away.

## Environment
- Apple Silicon machines (M-series). Never assume CUDA — use MPS for PyTorch, MLX when possible.
- Primary ML frameworks: PyTorch (with MPS), MLX.
- Primary LLM API: Google Gemini.
- Python is the main language.

## Documentation
- Every project should have a `docs/` folder for persistent context (see project-docs skill).
- This is non-negotiable: if docs/ doesn't exist, create it before doing anything else.
