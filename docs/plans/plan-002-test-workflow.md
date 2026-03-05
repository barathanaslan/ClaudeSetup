# Plan 002: Test Workflow — Create a Memory Monitor Utility

## Objective
Create a simple, reusable Python utility that prints a one-line memory status for Apple Silicon training loops. This tests the plan-implement-review workflow.

## Context
- Read: research/verify_memory.py and research/batch_tuner.py for patterns
- This is a small utility — one file

## Steps
1. Create `research/memory_utils.py` with:
   - A function `get_memory_status(device) -> str` that returns a formatted one-line string
   - For MPS: show MPS allocated, MPS pool, system available
   - For MLX: show active memory, peak memory
   - For CPU: show process RSS and system available
   - Include a function `log_memory_csv(path, epoch, **metrics)` that appends a row to a CSV
2. Add a `if __name__ == "__main__"` block that demonstrates the utility by:
   - Allocating a 1GB MPS tensor
   - Printing memory status
   - Freeing it
   - Printing memory status again

## Acceptance Criteria
- [ ] `memory_utils.py` exists and is importable
- [ ] `get_memory_status("mps")` returns a clean one-line string
- [ ] `log_memory_csv` appends to CSV correctly
- [ ] Demo block runs without errors
- [ ] Uses verified APIs only (driver_allocated_memory, psutil.virtual_memory, etc.)

## Constraints
- Do NOT use deprecated `mx.metal.*` APIs — use `mx.*` directly
- Do NOT use `Process().memory_info().rss` for GPU memory tracking
- Keep it simple — one file, no dependencies beyond torch/mlx/psutil
