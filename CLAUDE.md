# Global Preferences

## Working Style

- You tend to act as the architect: think through goals, trade-offs, and approach with the user here, rather than rushing to code. Use your judgment on how much of that a given task needs.
- For large or multi-step implementation, lean on background `general-purpose` agents and keep this conversation strategic — a short summary of the result is enough here. For small or quick changes, just do them inline; don't stand up an agent for a one-line edit.
- When you do delegate, a self-contained plan file in `docs/plans/` lets a fresh agent work from the plan alone. The `workflow` skill has the details.
- `docs/` is shared state between you and any worker agents. Read it at the start of a session if it exists, and keep it current when you finish meaningful work.
- When context is getting long, summarize the state into `docs/` before it gets compacted away.

## Environment

- Machine: Mac Studio, M3 Ultra chip, 96GB unified memory, macOS.
- Never assume CUDA locally — use MPS for PyTorch, MLX when possible.
- A remote CUDA box exists on the tailnet (RTX 5070 Ti, usually powered off): manage it only through `~/bin/cuda` (status/on/off/run) — see the `cuda-box` skill before touching it.
- To read CPU/RAM/GPU usage of this or any tailnet machine, run `tailmon json` (or `curl http://<tailscale-ip>:7020/stats`) — never parse vm_stat/top/Activity Monitor by hand; macOS memory readings there are misleading.
- Primary ML frameworks: PyTorch (with MPS), MLX.
- Primary LLM API: Google Gemini.

## Documentation

- Prefer a `docs/` folder for persistent project context (see the `workflow` skill). Create one when a project is substantial enough to benefit; skip it for throwaway or trivial work.
