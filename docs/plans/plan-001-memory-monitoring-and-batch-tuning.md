# Plan 001: Memory Monitoring & Auto Batch Size Tuning for Apple Silicon

## Objective
Research and verify the correct way to monitor real-time memory usage on Apple Silicon during ML training (both MPS and MLX), then build and test an auto batch size tuning routine.

## Context
- Machine: Apple Silicon M-series, 96GB unified memory, macOS
- PyTorch 2.9.1 with MPS, MLX 0.29.3, psutil 7.1.3 installed
- Unified memory means CPU and GPU share the same RAM pool
- Need to understand: what does "memory usage" mean on Apple Silicon? Is it MPS pool? System RSS? Metal allocations?

## Research Tasks

### Task 1: Understand Apple Silicon Memory Model
- Unified memory: CPU, GPU, Neural Engine all share one pool
- MPS allocates from this pool — `torch.mps.driver_allocated_memory()` shows pool size
- But system also uses memory — need to track TOTAL pressure, not just MPS
- Research: Is `psutil.virtual_memory().available` the right measure of "how much room do I have"?
- Research: Does `torch.mps.recommended_max_memory()` account for system usage?

### Task 2: Test Memory Monitoring Approaches
Write a Python script that:
1. Allocates increasingly large tensors on MPS
2. After each allocation, records:
   - `torch.mps.current_allocated_memory()` — MPS tensor memory
   - `torch.mps.driver_allocated_memory()` — MPS pool size
   - `psutil.virtual_memory().available` — system available memory
   - `psutil.virtual_memory().percent` — system memory pressure %
   - `psutil.Process().memory_info().rss` — process physical memory
3. Prints a table showing how these correlate
4. Tests if system-available drops as MPS allocates (proving they share the pool)
5. Tests what happens approaching the limit — does MPS OOM before system does?

### Task 3: Build Auto Batch Size Tuner
Write a function `find_optimal_batch_size()` that:
1. Takes a model, sample input shape, device, and memory budget (fraction of available)
2. Reads current available memory to determine safe allocation budget
3. Runs binary search over batch sizes:
   - For each candidate batch size: run one forward + backward pass
   - Monitor memory after pass
   - If within budget, try larger; if OOM or over budget, try smaller
4. Measures throughput (samples/sec) at each safe batch size
5. Returns the batch size with highest throughput that fits in memory budget
6. Cleans up between attempts (gc.collect, empty_cache)
7. Must work for both MPS (PyTorch) and MLX

### Task 4: Test the Tuner
- Create a small CNN or ResNet and run the tuner on it
- Verify it picks a reasonable batch size
- Verify memory stays within budget
- Print a summary table: batch_size | memory_used | throughput | status

## Output
- Save the working research script to: `/Users/barathanaslan/Projects/ClaudeSetup/research/memory_test.py`
- Save the batch tuner utility to: `/Users/barathanaslan/Projects/ClaudeSetup/research/batch_tuner.py`
- Print all findings to console so results are captured

## Constraints
- Use MPS device (Apple Silicon), NOT CUDA
- Don't allocate more than 30GB — leave room for the system
- Clean up between tests to avoid contaminating results
- This is research — code doesn't need to be production-polished, but results must be accurate
