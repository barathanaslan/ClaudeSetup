#!/usr/bin/env python3
"""
Memory monitoring utility for Apple Silicon training loops.
Provides a one-line memory status and CSV logging for MPS, MLX, and CPU.
"""

import csv
import gc
import os
import time
from pathlib import Path

import psutil
import torch


def get_memory_status(device: str = "mps") -> str:
    """
    Return a formatted one-line memory status string.

    Parameters
    ----------
    device : str
        One of "mps", "mlx", or "cpu".

    Returns
    -------
    str
        A single-line summary of current memory usage.
    """
    device = device.lower().strip()

    if device == "mps":
        torch.mps.synchronize()
        allocated = torch.mps.current_allocated_memory()
        driver = torch.mps.driver_allocated_memory()
        sys_avail = psutil.virtual_memory().available
        return (
            f"[MPS] allocated: {allocated / 1e9:.2f} GB | "
            f"pool: {driver / 1e9:.2f} GB | "
            f"sys available: {sys_avail / 1e9:.1f} GB"
        )

    elif device == "mlx":
        import mlx.core as mx

        active = mx.get_active_memory()
        peak = mx.get_peak_memory()
        return (
            f"[MLX] active: {active / 1e9:.2f} GB | "
            f"peak: {peak / 1e9:.2f} GB"
        )

    elif device == "cpu":
        proc = psutil.Process()
        rss = proc.memory_info().rss
        sys_avail = psutil.virtual_memory().available
        return (
            f"[CPU] process RSS: {rss / 1e9:.2f} GB | "
            f"sys available: {sys_avail / 1e9:.1f} GB"
        )

    else:
        raise ValueError(f"Unknown device: {device!r}. Expected 'mps', 'mlx', or 'cpu'.")


def log_memory_csv(path: str, epoch: int, **metrics) -> None:
    """
    Append a row to a CSV file with epoch number and arbitrary metrics.

    Creates the file with headers on the first call. Subsequent calls append
    rows. If the file already exists, it appends without rewriting headers
    (assumes the columns match).

    Parameters
    ----------
    path : str
        Path to the CSV file.
    epoch : int
        Current epoch or step number.
    **metrics
        Arbitrary key-value pairs to log (e.g., loss=0.5, mps_allocated=1.2e9).
    """
    file_path = Path(path)
    file_exists = file_path.exists() and file_path.stat().st_size > 0

    fieldnames = ["epoch"] + sorted(metrics.keys())
    row = {"epoch": epoch, **metrics}

    with open(file_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile

    print("=" * 60)
    print("Memory Utils — Demo")
    print("=" * 60)
    print()

    device = torch.device("mps")

    # Baseline
    print("1) Baseline (nothing allocated):")
    print("   ", get_memory_status("mps"))
    print()

    # Allocate ~1 GB (250M float32 = 1 GB)
    print("2) Allocating a 1 GB MPS tensor...")
    t = torch.randn(250_000_000, device=device, dtype=torch.float32)
    torch.mps.synchronize()
    print("   ", get_memory_status("mps"))
    print()

    # Log to CSV
    csv_path = os.path.join(tempfile.gettempdir(), "memory_utils_demo.csv")
    torch.mps.synchronize()
    log_memory_csv(
        csv_path,
        epoch=0,
        mps_allocated=torch.mps.current_allocated_memory(),
        mps_driver=torch.mps.driver_allocated_memory(),
    )
    print(f"   Logged to CSV: {csv_path}")
    print()

    # Free
    print("3) Freeing tensor...")
    del t
    gc.collect()
    torch.mps.empty_cache()
    torch.mps.synchronize()
    time.sleep(0.3)
    print("   ", get_memory_status("mps"))
    print()

    # Log post-free
    log_memory_csv(
        csv_path,
        epoch=1,
        mps_allocated=torch.mps.current_allocated_memory(),
        mps_driver=torch.mps.driver_allocated_memory(),
    )

    # Show CSV contents
    print("4) CSV contents:")
    with open(csv_path) as f:
        print("   ", f.read().replace("\n", "\n    "))

    # CPU status
    print("5) CPU memory status:")
    print("   ", get_memory_status("cpu"))
    print()

    print("Done.")
