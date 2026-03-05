# Apple ML Recipes

## Auto Batch Size Tuner

Binary-search for the fastest batch size that fits within a memory budget.

```python
import gc, time, torch, psutil

def find_optimal_batch_size(model, input_shape, device, budget_fraction=0.35, max_gb=30):
    """Binary-search for fastest batch size within memory budget.

    Args:
        model: nn.Module already on device
        input_shape: per-sample shape, e.g. (3, 224, 224)
        device: torch.device("mps")
        budget_fraction: fraction of system available memory to use
        max_gb: hard cap in GB
    Returns:
        optimal batch size (int)
    """
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

A full working implementation with reporting is at `~/Projects/ClaudeSetup/research/batch_tuner.py`.

## Performance Profiling Template

Quick check to estimate training speed before committing to a full run.

```python
import time

# Data loading speed
t0 = time.time()
for i, batch in enumerate(train_loader):
    if i >= 10: break
print(f"Data: {(time.time()-t0)/10:.3f}s/batch")

# Training step speed (must synchronize for accurate timing on MPS)
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

## Memory Monitoring Utility

A reusable memory monitoring utility is at `~/Projects/ClaudeSetup/research/memory_utils.py` with:
- `get_memory_status(device)` — one-line memory status for MPS, MLX, or CPU
- `log_memory_csv(path, epoch, **metrics)` — append metrics to CSV
