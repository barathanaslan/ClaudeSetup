---
name: ml-training
description: ML training best practices. Use when writing training loops, model training scripts, fine-tuning code, or any code that trains a model. TRIGGER when the user mentions training, fine-tuning, epochs, learning rate, loss curves, model convergence, overfitting, batch size, or wants to train anything with PyTorch, MLX, sklearn, or similar. Also trigger on code that contains training loops, optimizer steps, or loss computation.
user-invocable: false
---

# ML Training Standards

These rules apply to ALL training code — deep learning, classical ML, fine-tuning, anything that trains a model.

## 1. Checkpointing

Training runs crash, machines lose power, and hours of compute vanish without checkpoints. Save model weights so the user never loses progress.

- **Best model**: Save whenever the tracked metric improves
- **Periodic**: For long training runs (>1 hour estimated), also save every N epochs as fallback
- **What to save**: Model state dict, optimizer state, epoch number, best metric value, and training config
- **Where**: `checkpoints/` directory, with clear naming (e.g., `best_model.pt`, `checkpoint_epoch_010.pt`)
- **Gut check**: "If this crashes at epoch 47 of 50, will the user lose everything?" If yes, add checkpointing.

```python
# Minimum viable checkpoint
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'best_metric': best_metric,
}, f'checkpoints/best_model.pt')
```

## 2. Early Stopping

Without early stopping, training wastes compute on overfit epochs and the user has to manually watch for convergence. Implement it by default — the user can disable it if they want.

- Track the validation metric (not train loss)
- Default patience: 10 epochs (adjust based on training length)
- Restore best weights when stopping
- Log when early stopping triggers

## 3. Metrics & Logging

### What to Log (every epoch)
- Train loss
- Validation loss
- All relevant metrics on validation set — loss alone tells you the model is learning but not whether it's solving the actual task:
  - If a custom/official metric exists for the project → use it (check docs/, competition page, paper)
  - If classification → accuracy, F1, precision, recall
  - If regression → MSE, MAE, R2
  - If segmentation → IoU/Dice
  - If ranking → MAP, NDCG
  - Loss alone is NEVER sufficient

### Console Format
One clean line per epoch. No clutter, no redundant info:
```
Epoch 03/50 | train_loss: 0.342 | val_loss: 0.389 | val_f1: 0.847 | best: 0.851 (ep 2) | 45s
```

### File Logging
Save metrics to `logs/metrics.csv` — one row per epoch, all columns. Easy to plot later.

```python
import csv
# At training start
with open('logs/metrics.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['epoch', 'train_loss', 'val_loss', 'val_f1', ...])
```

### What NOT to Do
- Don't print every batch (unless the user asks for it)
- Don't use verbose progress bars that flood the terminal for small datasets
- Don't omit validation metrics
- Don't only show train metrics — always include validation

## 4. Training Configuration

- Print a summary of training config at the start (model, dataset size, learning rate, epochs, device, etc.)
- Set random seeds for reproducibility
- Use the correct device (MPS on Apple Silicon — see apple-ml skill)

## 5. Data Split Hygiene
- If the user doesn't specify splits, default to train/val/test (80/10/10 or similar)
- NEVER evaluate on training data and present it as results
- If a custom metric exists, compute it on the validation set during training and test set only at the very end

## 6. Performance — No Wasted Compute

Training speed matters. Days of compute are lost to avoidable bottlenecks. Profile BEFORE training, not after 30 hours of regret.

### NEVER use Python loops over batch/sequence dimensions

This is the #1 training speed killer. A nested loop over `batch_size × seq_len` that calls `.item()` on every iteration forces GPU sync 2,048 times per batch and turns a 1ms operation into 768ms. **Every operation inside a training step must be vectorized.**

```python
# WRONG — 768ms per batch (Python loops + .item() GPU syncs)
total_loss = 0
for b in range(batch_size):
    for w in range(max_wp):
        idx = indices[b, w].item()  # forces GPU sync!
        if idx < 0: continue
        total_loss += (pred[b, idx] - target[b, w]) ** 2

# RIGHT — 47ms per batch (fully vectorized, 16x faster)
valid_mask = indices >= 0
safe_idx = indices.clamp(min=0)
pred_at_wp = torch.gather(pred, 1, safe_idx.unsqueeze(-1).expand(-1, -1, 3))
diff_sq = (pred_at_wp - target) ** 2
loss = (diff_sq * valid_mask.unsqueeze(-1)).sum() / valid_mask.sum().clamp(min=1)
```

**Gut check**: Search for `for b in range(batch` or `.item()` inside loss functions and training loops. If found, vectorize immediately.

### Profile the training step BEFORE long runs

Before starting any training run >1 hour, profile one training step:
- Time each phase: data loading, forward, loss, backward, optimizer
- Identify which phase dominates
- A 1.2M parameter model should NOT take 800ms per batch — if it does, something is wrong

```python
torch.mps.synchronize()  # or torch.cuda.synchronize()
t0 = time.time()
# ... operation ...
torch.mps.synchronize()
print(f"Operation: {(time.time()-t0)*1000:.1f}ms")
```

### Data loading bottlenecks

If data loading is the bottleneck (>50% of step time):
- **Pre-compute expensive transforms**: If `__getitem__` does heavy CPU work (interpolation, feature extraction), pre-compute and cache to disk. This can give 100-400x speedup on data loading.
- **Increase batch size**: If GPU memory allows, larger batches mean fewer data loading calls per epoch.
- **`num_workers>0`**: Use multiprocessing workers for data loading — BUT test first, as it can be slower with large cached datasets due to fork/serialization overhead.
- **Pre-cache with multiprocessing**: Generate all samples once using a process pool, save to disk, load as a flat dataset during training.

### Tensor operations checklist

Before running training, verify:
- No `.item()` calls inside the training loop (except for logging at end of epoch)
- No Python `for` loops over batch, sequence, or feature dimensions
- No repeated `.to(device)` calls on the same tensor
- Loss functions operate on full tensors, not element-by-element
- Custom metrics computed with vectorized ops, not loops

## 7. For Large/Long Training
- Estimate training time before starting (print it)
- Save checkpoints more frequently
- Consider gradient accumulation if batch size is limited by memory
- Log to both console and file so nothing is lost if the terminal disconnects
