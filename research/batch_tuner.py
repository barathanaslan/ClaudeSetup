#!/usr/bin/env python3
"""
Plan 001 — Tasks 3 & 4: Auto Batch Size Tuner for Apple Silicon
Finds the optimal batch size by binary-searching over sizes while monitoring memory.
"""

import gc
import time
import torch
import torch.nn as nn
import psutil

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_gb(b):
    return f"{b / (1024**3):.2f} GB"

def fmt_mb(b):
    return f"{b / (1024**2):.1f} MB"

def cleanup_mps():
    gc.collect()
    torch.mps.empty_cache()
    torch.mps.synchronize()
    time.sleep(0.3)

def get_mps_memory():
    torch.mps.synchronize()
    return {
        "mps_allocated": torch.mps.current_allocated_memory(),
        "mps_driver": torch.mps.driver_allocated_memory(),
        "sys_available": psutil.virtual_memory().available,
    }

# ---------------------------------------------------------------------------
# Core: test a single batch size
# ---------------------------------------------------------------------------

def test_batch_size(model, input_shape, batch_size, device, num_warmup=1, num_timed=3):
    """
    Run forward+backward at the given batch_size.
    Returns dict with memory and throughput info, or None on OOM.
    """
    cleanup_mps()
    before = get_mps_memory()

    try:
        # Build batch
        x = torch.randn(batch_size, *input_shape, device=device)
        target = torch.randint(0, 10, (batch_size,), device=device)
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

        # Warmup
        for _ in range(num_warmup):
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, target)
            loss.backward()
            optimizer.step()
            torch.mps.synchronize()

        # Timed runs
        torch.mps.synchronize()
        t0 = time.perf_counter()
        for _ in range(num_timed):
            optimizer.zero_grad()
            out = model(x)
            loss = criterion(out, target)
            loss.backward()
            optimizer.step()
            torch.mps.synchronize()
        elapsed = time.perf_counter() - t0

        after = get_mps_memory()

        throughput = (batch_size * num_timed) / elapsed
        # Use driver_allocated (Metal pool) as the real memory cost —
        # current_allocated only tracks live tensors and is much smaller
        mem_used = after["mps_driver"]

        del x, target, out, loss, optimizer, criterion
        cleanup_mps()

        return {
            "batch_size": batch_size,
            "mem_used": mem_used,
            "mem_driver": after["mps_driver"],
            "sys_available": after["sys_available"],
            "throughput": throughput,
            "elapsed": elapsed,
            "status": "OK",
        }

    except RuntimeError as e:
        if "out of memory" in str(e).lower() or "MPS" in str(e):
            cleanup_mps()
            return {
                "batch_size": batch_size,
                "mem_used": 0,
                "mem_driver": 0,
                "sys_available": 0,
                "throughput": 0,
                "elapsed": 0,
                "status": f"OOM",
            }
        raise

# ---------------------------------------------------------------------------
# Binary search tuner
# ---------------------------------------------------------------------------

def find_optimal_batch_size(
    model,
    input_shape,
    device="mps",
    memory_budget_fraction=0.4,
    max_memory_gb=30,
    min_batch=1,
    max_batch=1024,
    num_warmup=1,
    num_timed=3,
):
    """
    Binary-search for the batch size that maximises throughput while staying
    within the memory budget.

    Parameters
    ----------
    model : nn.Module           — already on `device`
    input_shape : tuple         — per-sample shape, e.g. (3, 224, 224)
    device : str                — "mps"
    memory_budget_fraction : float — fraction of system available memory to use
    max_memory_gb : float       — hard cap in GB (default 30)
    min_batch, max_batch : int  — search range
    """
    device = torch.device(device)

    cleanup_mps()
    sys_avail = psutil.virtual_memory().available
    budget_bytes = min(
        int(sys_avail * memory_budget_fraction),
        int(max_memory_gb * 1024**3),
    )
    print(f"System available memory:  {fmt_gb(sys_avail)}")
    print(f"Memory budget ({memory_budget_fraction*100:.0f}% of avail, capped {max_memory_gb}GB): {fmt_gb(budget_bytes)}")
    print()

    results = []

    # Phase 1: exponential scan to find rough upper bound
    print("Phase 1: Exponential scan")
    print("-" * 90)
    header = f"{'Batch':>6} | {'MPS Alloc':>12} | {'MPS Driver':>12} | {'Sys Avail':>12} | {'Throughput':>14} | {'Status':>8}"
    print(header)
    print("-" * 90)

    scan_sizes = []
    b = min_batch
    while b <= max_batch:
        scan_sizes.append(b)
        b *= 2

    upper_bound = max_batch
    lower_bound = min_batch
    best_ok = min_batch

    for bs in scan_sizes:
        result = test_batch_size(model, input_shape, bs, device, num_warmup, num_timed)
        if result is None:
            result = {"batch_size": bs, "status": "ERROR", "mem_used": 0, "mem_driver": 0,
                      "sys_available": 0, "throughput": 0}

        results.append(result)
        _print_result_row(result)

        if result["status"] != "OK":
            upper_bound = bs
            break
        elif result["mem_used"] > budget_bytes:
            upper_bound = bs
            print(f"  ^ Over budget ({fmt_gb(result['mem_used'])} > {fmt_gb(budget_bytes)})")
            break
        else:
            best_ok = bs
            lower_bound = bs

    # Phase 2: binary search between lower_bound and upper_bound
    print()
    print(f"Phase 2: Binary search in [{lower_bound}, {upper_bound}]")
    print("-" * 90)
    print(header)
    print("-" * 90)

    lo, hi = lower_bound, upper_bound
    while lo < hi - 1:
        mid = (lo + hi) // 2
        # round to nearest power-of-2-friendly number (multiple of 8)
        mid = max(lo + 1, (mid // 8) * 8)
        if mid <= lo or mid >= hi:
            break

        result = test_batch_size(model, input_shape, mid, device, num_warmup, num_timed)
        if result is None:
            result = {"batch_size": mid, "status": "ERROR", "mem_used": 0, "mem_driver": 0,
                      "sys_available": 0, "throughput": 0}
        results.append(result)
        _print_result_row(result)

        if result["status"] == "OK" and result["mem_used"] <= budget_bytes:
            lo = mid
        else:
            hi = mid

    # Pick best
    ok_results = [r for r in results if r["status"] == "OK" and r["mem_used"] <= budget_bytes]
    if not ok_results:
        print("\nNo batch size fit within budget!")
        return results

    best = max(ok_results, key=lambda r: r["throughput"])

    print()
    print("=" * 90)
    print("RESULTS SUMMARY")
    print("=" * 90)
    print(f"{'Batch':>6} | {'MPS Alloc':>12} | {'MPS Driver':>12} | {'Throughput':>14} | {'Status':>8}")
    print("-" * 70)
    for r in sorted(ok_results, key=lambda r: r["batch_size"]):
        _print_result_row(r, short=True)
    print()
    print(f">>> OPTIMAL BATCH SIZE: {best['batch_size']}")
    print(f"    Throughput:  {best['throughput']:.1f} samples/sec")
    print(f"    MPS memory:  {fmt_gb(best['mem_used'])}")
    print(f"    Budget:      {fmt_gb(budget_bytes)}")
    print()

    return results


def _print_result_row(r, short=False):
    if r["status"] != "OK":
        print(f"{r['batch_size']:>6} | {'—':>12} | {'—':>12} | {'—':>14} | {r['status']:>8}")
    elif short:
        print(
            f"{r['batch_size']:>6} | "
            f"{fmt_gb(r['mem_used']):>12} | "
            f"{fmt_gb(r['mem_driver']):>12} | "
            f"{r['throughput']:>11.1f} s/s | "
            f"{r['status']:>8}"
        )
    else:
        print(
            f"{r['batch_size']:>6} | "
            f"{fmt_gb(r['mem_used']):>12} | "
            f"{fmt_gb(r['mem_driver']):>12} | "
            f"{fmt_gb(r['sys_available']):>12} | "
            f"{r['throughput']:>11.1f} s/s | "
            f"{r['status']:>8}"
        )


# ---------------------------------------------------------------------------
# Task 4: Test with a small CNN
# ---------------------------------------------------------------------------

def build_test_model(device):
    """A small ResNet-like CNN for testing."""
    model = nn.Sequential(
        # Block 1
        nn.Conv2d(3, 64, 3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.Conv2d(64, 64, 3, padding=1),
        nn.BatchNorm2d(64),
        nn.ReLU(),
        nn.MaxPool2d(2),
        # Block 2
        nn.Conv2d(64, 128, 3, padding=1),
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.Conv2d(128, 128, 3, padding=1),
        nn.BatchNorm2d(128),
        nn.ReLU(),
        nn.MaxPool2d(2),
        # Block 3
        nn.Conv2d(128, 256, 3, padding=1),
        nn.BatchNorm2d(256),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(4),
        # Head
        nn.Flatten(),
        nn.Linear(256 * 4 * 4, 256),
        nn.ReLU(),
        nn.Linear(256, 10),
    )
    return model.to(device)


def main():
    print("=" * 90)
    print("AUTO BATCH SIZE TUNER — Apple Silicon MPS")
    print("=" * 90)
    print()

    device = torch.device("mps")
    model = build_test_model(device)

    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters: {param_count:,}")
    print(f"Input shape: (3, 224, 224)")
    print()

    results = find_optimal_batch_size(
        model=model,
        input_shape=(3, 224, 224),
        device="mps",
        memory_budget_fraction=0.35,   # conservative: 35% of available
        max_memory_gb=30,
        min_batch=4,
        max_batch=512,
        num_warmup=1,
        num_timed=3,
    )

    # Final cleanup
    del model
    cleanup_mps()
    print("Done.")


if __name__ == "__main__":
    main()
