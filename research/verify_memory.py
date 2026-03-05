#!/usr/bin/env python3
"""
Run this while watching Activity Monitor → Memory tab.
It allocates MPS tensors in steps and prints what our APIs report.
Compare the numbers with what Activity Monitor shows.

Press Enter between each step to give yourself time to check Activity Monitor.
"""
import gc
import torch
import psutil

device = torch.device("mps")
tensors = []

print("=== Memory Verification Script ===")
print("Watch Activity Monitor → Memory tab while running this.")
print(f"System total: {psutil.virtual_memory().total / 1e9:.1f} GB")
print()

def report(label):
    torch.mps.synchronize()
    alloc = torch.mps.current_allocated_memory() / 1e9
    driver = torch.mps.driver_allocated_memory() / 1e9
    sys_avail = psutil.virtual_memory().available / 1e9
    sys_used = psutil.virtual_memory().used / 1e9
    print(f"[{label}]")
    print(f"  MPS tensors (current_allocated): {alloc:.2f} GB")
    print(f"  MPS pool    (driver_allocated):  {driver:.2f} GB  ← should match Activity Monitor GPU memory")
    print(f"  System available:                {sys_avail:.1f} GB")
    print(f"  System used:                     {sys_used:.1f} GB")
    print()

report("Baseline - nothing allocated")
input("Press Enter to allocate 2 GB on MPS...")

# Step 1: 2 GB
tensors.append(torch.randn(500_000_000, device=device, dtype=torch.float32))  # 2 GB
report("After allocating 2 GB")
input("Press Enter to allocate 4 more GB (total 6 GB)...")

# Step 2: +4 GB
tensors.append(torch.randn(1_000_000_000, device=device, dtype=torch.float32))  # 4 GB
report("After allocating 6 GB total")
input("Press Enter to allocate 8 more GB (total 14 GB)...")

# Step 3: +8 GB
tensors.append(torch.randn(2_000_000_000, device=device, dtype=torch.float32))  # 8 GB
report("After allocating 14 GB total")
input("Press Enter to FREE all tensors...")

# Free everything
del tensors
gc.collect()
torch.mps.empty_cache()
report("After freeing all + empty_cache")

print("Done. Did the numbers match Activity Monitor?")
