---
name: apple-ml
description: Apple Silicon ML patterns. Use when writing PyTorch code, MLX code, or any ML code that will run on the user's machine. The user ONLY has Apple Silicon (M-series) machines — no CUDA. TRIGGER on torch, mlx, or device selection code.
user-invocable: false
---

# Apple Silicon ML (MPS & MLX)

The user runs ALL workloads on Apple Silicon. Never assume CUDA.
All APIs below verified on PyTorch 2.9.1 + MLX 0.29.3 (March 2026).

## Device Selection (PyTorch)

```python
import torch

def get_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")
```

## MPS Memory Management

### Setting Memory Limits (use the API, not env vars)
```python
import torch

# Cap MPS memory at 50% of recommended max (~42GB on 96GB machine)
# Range: 0 (unlimited) to 2.0. Fraction of device.recommendedMaxWorkingSetSize.
torch.mps.set_per_process_memory_fraction(0.5)

# Check what the system recommends as max:
max_gb = torch.mps.recommended_max_memory() / 1e9  # ~83.5 GB on 96GB machine
```

### Monitoring During Training (all verified working)
```python
if device.type == "mps":
    alloc_gb = torch.mps.current_allocated_memory() / 1e9   # Live tensor memory
    pool_gb  = torch.mps.driver_allocated_memory() / 1e9    # Metal pool = REAL cost
    max_gb   = torch.mps.recommended_max_memory() / 1e9     # System recommended max
    sys_gb   = psutil.virtual_memory().available / 1e9       # System available (safety)
    mem_str  = f"mem={alloc_gb:.1f}/{pool_gb:.1f}GB (sys avail {sys_gb:.0f}GB)"
```

**IMPORTANT**: Use `driver_allocated_memory()` for budget decisions, NOT `current_allocated_memory()`.
The driver pool stays large even after tensors are freed — it's the real system memory cost.
`Process().memory_info().rss` does NOT track MPS allocations — don't use it for GPU memory.

**Note on Activity Monitor discrepancy**: `driver_allocated_memory()` may report ~5-10% more than
what Activity Monitor shows for the Python process (e.g., 14 GB API vs 13.2 GB Activity Monitor).
This is because Activity Monitor shows RSS which doesn't perfectly map to MPS pool size.
`driver_allocated_memory()` is the more accurate measure for MPS budgeting.
Similarly, `psutil.virtual_memory().used` reports less than Activity Monitor's "Kullanılan Bellek"
because macOS counts wired + compressed memory separately (~5-8 GB overhead).
For safety, always leave a margin when setting memory budgets.

### Cleanup
```python
import gc
gc.collect()
if device.type == "mps":
    torch.mps.empty_cache()  # Releases unused memory from the MPS pool
```

### System-Level Memory (unified memory shared by CPU+GPU)
```python
import psutil
vm = psutil.virtual_memory()
print(f"System: {vm.used/1e9:.1f}/{vm.total/1e9:.1f} GB ({vm.percent}%)")
```

## MPS Synchronization

MPS operations are async. For accurate timing:
```python
torch.mps.synchronize()  # Wait for all MPS ops to complete
```

## MPS Operation Fallback

Some ops aren't supported. Enable global fallback BEFORE importing torch:
```python
import os
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
```

Known unsupported: `torchvision::roi_align` (use YOLO/DETR not RCNN), some scatter/gather ops.

For individual ops: `result = some_op(tensor.cpu()).to(device)`

## MPS Known Issues

| Issue | Solution |
|-------|----------|
| Float64 not supported | Always use `torch.float32` |
| DataLoader hangs | Use `num_workers=0` (always on macOS) |
| OOM despite free memory | `torch.mps.set_per_process_memory_fraction(0.5)` |
| Slow training | Verify `next(model.parameters()).device` shows `mps:0` |
| `torch.compile` issues | Don't rely on it with MPS |
| Non-deterministic results | Expected — set seeds, accept minor variations |

## MLX

### Decision Flowchart
```
Starting a new project?
├─ Whisper/audio? → MLX (mlx-whisper)
├─ LLM inference/fine-tuning? → mlx-lm
├─ Computer vision? → PyTorch + MPS
├─ Model in mlx-examples? → Try MLX first
└─ Custom architecture? → PyTorch (broader ecosystem)
```

### MLX Memory Monitoring (all verified, use mx.* NOT mx.metal.*)
```python
import mlx.core as mx

# mx.metal.* is DEPRECATED — use mx.* directly
active_bytes = mx.get_active_memory()   # Currently allocated
cache_bytes  = mx.get_cache_memory()    # Cached but not active
peak_bytes   = mx.get_peak_memory()     # Peak since last reset

print(f"MLX mem: {active_bytes/1e6:.1f}MB active, {peak_bytes/1e6:.1f}MB peak")

mx.reset_peak_memory()        # Reset peak counter
mx.set_memory_limit(limit)    # Set max memory (bytes)
mx.set_cache_limit(limit)     # Set max cache (bytes)
mx.clear_cache()              # Free cached memory
```

### Lazy Evaluation — The #1 Gotcha
```python
x = mx.array([1.0, 2.0, 3.0])
y = x + 1    # NOT computed yet — just builds the graph
mx.eval(y)   # NOW it runs on Metal
```

### Gradient Accumulation — Must eval per micro-step
```python
for micro_step in range(grad_accum_steps):
    loss, grads = nn.value_and_grad(model, loss_fn)(model)
    mx.eval(loss)  # CRITICAL: prevents computation graph bloat
    accumulated_loss += loss.item()

    if accumulated_grads is None:
        accumulated_grads = grads
    else:
        accumulated_grads = tree_map(lambda a, b: a + b, accumulated_grads, grads)

accumulated_grads = tree_map(lambda g: g / grad_accum_steps, accumulated_grads)
grads, _ = clip_grad_norm(accumulated_grads, max_grad_norm)
optimizer.update(model, grads)
mx.eval(model.parameters())
```

### LR Scheduling
```python
import mlx.optimizers as optim

warmup = optim.linear_schedule(0, lr, steps=warmup_steps)
decay = optim.cosine_decay(lr, decay_steps=decay_steps, end=min_lr)
schedule = optim.join_schedules([warmup, decay], [warmup_steps])
```

### Checkpointing (use safetensors for large models)
```python
from mlx.utils import save_safetensors, flatten_params
weights = flatten_params(model.parameters())
save_safetensors(str(path / "model.safetensors"), weights)
# mx.savez has a 1024 args limit — safetensors has no such limit
```

### MLX Notes
- API changes frequently — web search before writing MLX code
- No `.to(device)` needed — everything auto-runs on Apple Silicon
- Gradient clipping: `from mlx.optimizers import clip_grad_norm`

## Performance Profiling Template
## Auto Batch Size Tuning

On Apple Silicon, larger batch sizes are NOT always faster (unlike CUDA). Always measure.
A working batch tuner is available at: `~/Projects/ClaudeSetup/research/batch_tuner.py`

### Key Pattern
```python
import gc, time, torch, psutil

def find_optimal_batch_size(model, input_shape, device, budget_fraction=0.35, max_gb=30):
    """Binary-search for fastest batch size within memory budget."""
    avail = psutil.virtual_memory().available
    budget = min(int(avail * budget_fraction), int(max_gb * 1024**3))

    best_bs, best_throughput = 1, 0
    for bs in [4, 8, 16, 32, 64, 128, 256, 512]:
        gc.collect(); torch.mps.empty_cache(); torch.mps.synchronize()
        try:
            x = torch.randn(bs, *input_shape, device=device)
            t = torch.randint(0, 10, (bs,), device=device)
            opt = torch.optim.SGD(model.parameters(), lr=0.01)
            # Warmup
            opt.zero_grad(); loss = torch.nn.functional.cross_entropy(model(x), t)
            loss.backward(); opt.step(); torch.mps.synchronize()
            # Timed
            t0 = time.perf_counter()
            for _ in range(3):
                opt.zero_grad(); loss = torch.nn.functional.cross_entropy(model(x), t)
                loss.backward(); opt.step(); torch.mps.synchronize()
            elapsed = time.perf_counter() - t0

            mem = torch.mps.driver_allocated_memory()  # Real memory cost
            throughput = (bs * 3) / elapsed

            if mem <= budget and throughput > best_throughput:
                best_bs, best_throughput = bs, throughput
            if mem > budget:
                break
            del x, t, opt
        except RuntimeError:
            break

    return best_bs
```

### Why This Matters
- MPS throughput often peaks at surprisingly small batch sizes (16-32)
- Larger batches just waste memory without speed gain
- Use `driver_allocated_memory()` not `current_allocated_memory()` for budgeting
- Always `gc.collect() + torch.mps.empty_cache()` between trials

## Reference Links (web search these when issues arise)

- **PyTorch MPS**: https://pytorch.org/docs/stable/notes/mps.html
- **PyTorch MPS backend**: https://pytorch.org/docs/stable/mps.html
- **MLX documentation**: https://ml-explore.github.io/mlx/
- **MLX examples**: https://github.com/ml-explore/mlx-examples
- **mlx-lm** (LLM inference/fine-tuning): https://github.com/ml-explore/mlx-examples/tree/main/llms/mlx_lm
- **mlx-whisper**: https://github.com/ml-explore/mlx-examples/tree/main/whisper
- **Apple ML Research**: https://machinelearning.apple.com/

When hitting MPS errors, search: `site:github.com/pytorch/pytorch <error message>`
When hitting MLX errors, search: `site:github.com/ml-explore/mlx <error message>`

## Performance Profiling Template
```python
import time

# Data loading speed
t0 = time.time()
for i, batch in enumerate(train_loader):
    if i >= 10: break
print(f"Data: {(time.time()-t0)/10:.3f}s/batch")

# Training step speed (must synchronize for accurate timing)
x, y = next(iter(train_loader))
x, y = x.to(device), y.to(device)
t0 = time.time()
loss = criterion(model(x), y)
loss.backward()
optimizer.step()
if device.type == "mps":
    torch.mps.synchronize()
dt = time.time() - t0
est_epoch = dt * len(train_loader) / 60
print(f"Train step: {dt:.3f}s | Est. epoch: {est_epoch:.1f}min")
```
