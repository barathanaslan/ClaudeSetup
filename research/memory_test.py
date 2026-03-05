#!/usr/bin/env python3
"""
Plan 001 — Task 2: Memory Monitoring on Apple Silicon
Tests how MPS memory and system memory correlate on unified memory architecture.
"""

import gc
import time
import torch
import psutil

def fmt_gb(bytes_val):
    return f"{bytes_val / (1024**3):.2f} GB"

def fmt_mb(bytes_val):
    return f"{bytes_val / (1024**2):.1f} MB"

def get_memory_snapshot():
    """Capture all relevant memory metrics."""
    torch.mps.synchronize()
    vm = psutil.virtual_memory()
    proc = psutil.Process()
    return {
        "mps_allocated": torch.mps.current_allocated_memory(),
        "mps_driver": torch.mps.driver_allocated_memory(),
        "sys_available": vm.available,
        "sys_percent": vm.percent,
        "proc_rss": proc.memory_info().rss,
    }

def cleanup():
    """Free MPS memory between tests."""
    gc.collect()
    torch.mps.empty_cache()
    torch.mps.synchronize()
    time.sleep(0.5)

def print_separator():
    print("=" * 110)

def main():
    print("=" * 110)
    print("APPLE SILICON MEMORY MONITORING TEST")
    print("=" * 110)

    device = torch.device("mps")
    total_mem = psutil.virtual_memory().total
    print(f"Total system memory: {fmt_gb(total_mem)}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"MPS available: {torch.backends.mps.is_available()}")
    print()

    # Check recommended max memory
    try:
        rec_max = torch.mps.recommended_max_memory()
        print(f"torch.mps.recommended_max_memory(): {fmt_gb(rec_max)}")
    except Exception as e:
        print(f"torch.mps.recommended_max_memory() not available: {e}")
        rec_max = None
    print()

    # --- Baseline ---
    cleanup()
    baseline = get_memory_snapshot()
    print("BASELINE (no MPS tensors allocated):")
    print(f"  MPS allocated:    {fmt_mb(baseline['mps_allocated'])}")
    print(f"  MPS driver pool:  {fmt_mb(baseline['mps_driver'])}")
    print(f"  System available: {fmt_gb(baseline['sys_available'])}")
    print(f"  System used %:    {baseline['sys_percent']:.1f}%")
    print(f"  Process RSS:      {fmt_mb(baseline['proc_rss'])}")
    print()

    # --- Test 1: Incremental allocation ---
    print_separator()
    print("TEST 1: Incremental tensor allocation on MPS")
    print_separator()
    header = f"{'Alloc Size':>12} | {'MPS Alloc':>12} | {'MPS Driver':>12} | {'Sys Avail':>12} | {'Sys %':>7} | {'Proc RSS':>12} | {'Sys Avail Drop':>14}"
    print(header)
    print("-" * len(header))

    sizes_gb = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0, 16.0]
    tensors = []
    prev_available = baseline["sys_available"]

    for size_gb in sizes_gb:
        num_floats = int(size_gb * (1024**3) / 4)  # float32 = 4 bytes
        try:
            t = torch.randn(num_floats, device=device, dtype=torch.float32)
            tensors.append(t)
            snap = get_memory_snapshot()
            avail_drop = baseline["sys_available"] - snap["sys_available"]
            print(
                f"{size_gb:>10.2f} GB | "
                f"{fmt_gb(snap['mps_allocated']):>12} | "
                f"{fmt_gb(snap['mps_driver']):>12} | "
                f"{fmt_gb(snap['sys_available']):>12} | "
                f"{snap['sys_percent']:>6.1f}% | "
                f"{fmt_gb(snap['proc_rss']):>12} | "
                f"{fmt_gb(avail_drop):>14}"
            )
            prev_available = snap["sys_available"]
        except Exception as e:
            print(f"{size_gb:>10.2f} GB | *** OOM or ERROR: {e}")
            break

    total_allocated_gb = sum(s for s in sizes_gb[:len(tensors)])
    print(f"\nTotal tensor size requested: {total_allocated_gb:.2f} GB")

    # Check correlation
    final_snap = get_memory_snapshot()
    total_avail_drop = baseline["sys_available"] - final_snap["sys_available"]
    print(f"Total system available drop:  {fmt_gb(total_avail_drop)}")
    print(f"MPS allocated reports:        {fmt_gb(final_snap['mps_allocated'])}")
    print(f"MPS driver pool reports:      {fmt_gb(final_snap['mps_driver'])}")
    print()

    if total_avail_drop > 0:
        ratio = final_snap["mps_allocated"] / total_avail_drop if total_avail_drop else 0
        print(f"FINDING: MPS allocated / system available drop ratio: {ratio:.2f}")
        if 0.7 < ratio < 1.3:
            print("  => System available memory DOES track MPS allocations (unified memory confirmed)")
        else:
            print("  => Ratio is off — system available may not perfectly track MPS allocations")
    print()

    # Free everything
    del tensors
    cleanup()

    # --- Test 2: Does memory return after freeing? ---
    print_separator()
    print("TEST 2: Memory recovery after freeing tensors")
    print_separator()
    after_free = get_memory_snapshot()
    print(f"After freeing + empty_cache:")
    print(f"  MPS allocated:    {fmt_mb(after_free['mps_allocated'])}")
    print(f"  MPS driver pool:  {fmt_mb(after_free['mps_driver'])}")
    print(f"  System available: {fmt_gb(after_free['sys_available'])}")
    recovered = after_free["sys_available"] - final_snap["sys_available"]
    print(f"  System available recovered: {fmt_gb(recovered)}")
    print()

    # --- Test 3: Forward+backward memory pattern ---
    print_separator()
    print("TEST 3: Memory during forward + backward pass")
    print_separator()
    cleanup()

    import torch.nn as nn

    model = nn.Sequential(
        nn.Conv2d(3, 64, 3, padding=1),
        nn.ReLU(),
        nn.Conv2d(64, 128, 3, padding=1),
        nn.ReLU(),
        nn.AdaptiveAvgPool2d(1),
        nn.Flatten(),
        nn.Linear(128, 10),
    ).to(device)

    batch_sizes = [16, 32, 64, 128, 256, 512]
    print(f"{'Batch':>6} | {'After Fwd':>12} | {'After Bwd':>12} | {'Peak MPS':>12} | {'Sys Avail':>12}")
    print("-" * 75)

    for bs in batch_sizes:
        cleanup()
        before = get_memory_snapshot()
        try:
            x = torch.randn(bs, 3, 224, 224, device=device)
            out = model(x)
            fwd_snap = get_memory_snapshot()

            loss = out.sum()
            loss.backward()
            torch.mps.synchronize()
            bwd_snap = get_memory_snapshot()

            print(
                f"{bs:>6} | "
                f"{fmt_gb(fwd_snap['mps_allocated']):>12} | "
                f"{fmt_gb(bwd_snap['mps_allocated']):>12} | "
                f"{fmt_gb(bwd_snap['mps_driver']):>12} | "
                f"{fmt_gb(bwd_snap['sys_available']):>12}"
            )
            del x, out, loss
            model.zero_grad()
        except Exception as e:
            print(f"{bs:>6} | *** ERROR: {e}")
            break

    del model
    cleanup()

    # --- Summary ---
    print()
    print_separator()
    print("SUMMARY OF FINDINGS")
    print_separator()
    print("1. torch.mps.current_allocated_memory() — tracks tensor-level MPS allocations")
    print("2. torch.mps.driver_allocated_memory()  — tracks Metal driver pool (>= allocated)")
    print("3. psutil.virtual_memory().available     — system-wide available (drops as MPS allocates)")
    print("4. psutil.Process().memory_info().rss    — process resident memory")
    print()
    print("For batch tuning, the BEST approach is to use a COMBINATION:")
    print("  - torch.mps.current_allocated_memory() for MPS-specific tracking")
    print("  - psutil.virtual_memory().available as a safety check against total system pressure")
    print("  - OOM exception handling as a fallback")
    if rec_max is not None:
        print(f"  - torch.mps.recommended_max_memory() = {fmt_gb(rec_max)} as an upper bound hint")
    print()

if __name__ == "__main__":
    main()
