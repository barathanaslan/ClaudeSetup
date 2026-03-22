---
name: kaggle-submit
description: Automate Kaggle competition submissions — create datasets from local files, push notebooks with environment config, and submit to competitions. Use this skill whenever the user mentions "submit to kaggle", "push notebook", "kaggle submission", "upload to competition", "submit my model", "kaggle dataset upload", or wants to automate any part of the Kaggle notebook/dataset/submission workflow, even if they don't explicitly say "submit". Also trigger when the user has a notebook and weights/model files and wants to get them running on Kaggle.
user_invocable: true
---

# Kaggle Competition Submission

Automates the full workflow: local files → Kaggle dataset → notebook push → competition submission. Everything runs via the `kaggle` CLI — no web scraping needed.

## Prerequisites

- **kaggle package**: `pip install kaggle`
- **Auth**: Look for `KAGGLE_API_TOKEN` in the project's `.env` file first. Fall back to `~/.kaggle/kaggle.json`. The token format is `KGAT_<hex>` and is passed as an env var prefix on all commands: `KAGGLE_API_TOKEN=<token> kaggle ...`
- **Competition rules**: The user must have accepted the competition rules on kaggle.com. Verify with `kaggle competitions submissions <slug>` — if it returns results, they're in.

## Workflow

Follow these steps in order. Each step depends on the previous one succeeding.

### 1. Gather Context

Figure out these values (ask the user or infer from the project):

| Value | How to find it |
|-------|---------------|
| Competition slug | `kaggle competitions list --search <name>` |
| Kaggle username | Parse from `~/.kaggle/kaggle.json` or `kaggle config view` |
| Notebook file | Look for `.ipynb` files in the project |
| Files to upload | Model weights (`.pt`, `.pth`, `.ckpt`, `.safetensors`, `.bin`), configs, etc. |
| Dataset slug | Derive from competition name (e.g., `birdclef2026-weights`) |
| Accelerator | none (CPU), NvidiaTeslaP100, NvidiaTeslaT4, NvidiaA100, NvidiaH100, TpuV6E8, TpuV38 |
| Internet access | Code competitions typically require disabled |

### 2. Create or Update Dataset

Upload local files (weights, configs, etc.) as a Kaggle dataset so the notebook can access them.

```bash
# Prepare files in a temp directory
mkdir -p /tmp/<dataset-slug>
cp <files> /tmp/<dataset-slug>/

# Initialize and configure metadata
kaggle datasets init -p /tmp/<dataset-slug>
# Edit dataset-metadata.json:
#   "title": "<dataset-slug>"
#   "id": "<username>/<dataset-slug>"

# Upload — use 'create' for new, 'version' for existing
kaggle datasets create -p /tmp/<dataset-slug>
# or: kaggle datasets version -p /tmp/<dataset-slug> -m "update weights"

# Confirm it's ready before proceeding (this matters — pushing a kernel
# before the dataset finishes processing causes mount failures)
kaggle datasets status <username>/<dataset-slug>
# Must return "ready"
```

### 3. Update Notebook Paths

Kaggle mounts data under a nested directory structure. This is different from what many online examples show, and getting it wrong is the #1 cause of kernel failures:

```
/kaggle/input/
├── competitions/
│   └── <competition-slug>/     ← competition data lives here
│       ├── sample_submission.csv
│       ├── train.csv
│       └── ...
└── datasets/
    └── <username>/
        └── <dataset-slug>/     ← your uploaded dataset lives here
            └── model.pt
```

The old flat paths like `/kaggle/input/<slug>/` no longer work. Update the notebook's path configuration to use the nested structure. Most notebooks have a path config section near the top — look for it and adjust accordingly.

**Debugging tip**: If paths are unclear, temporarily add a cell with `import os; print(os.listdir('/kaggle/input/'))` and push to see what's actually mounted. Remove it once paths are confirmed.

### 4. Create kernel-metadata.json

Write this to the notebook's directory. It tells Kaggle how to run the notebook:

```json
{
  "id": "<username>/<kernel-slug>",
  "title": "<Kernel Title>",
  "code_file": "<notebook>.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": false,
  "enable_tpu": false,
  "enable_internet": false,
  "dataset_sources": ["<username>/<dataset-slug>"],
  "competition_sources": ["<competition-slug>"],
  "kernel_sources": [],
  "model_sources": []
}
```

Set `enable_gpu` or `enable_tpu` to `true` if the user requested an accelerator. The `competition_sources` field is what makes the competition data available to the kernel.

### 5. Push Notebook

```bash
kaggle kernels push -p <notebook-directory>
```

### 6. Monitor Execution

Poll the status every 30–60 seconds. Kernels go through QUEUED → RUNNING → COMPLETE or ERROR.

```bash
kaggle kernels status <username>/<kernel-slug>
```

If the kernel errors, download and inspect the logs:
```bash
kaggle kernels output <username>/<kernel-slug> -p /tmp/kaggle-logs
```
The log is JSON — extract stdout/stderr with:
```python
import json
lines = json.load(open('/tmp/kaggle-logs/<kernel-slug>.log'))
for l in lines:
    print(l.get('data', ''), end='')
```

### 7. Submit to Competition

This is a separate step from pushing — `kernels push` runs the notebook but does not submit to the competition. For code competitions, you must explicitly submit the kernel version:

```bash
kaggle competitions submit <competition-slug> \
  -k <username>/<kernel-slug> \
  -v <version-number> \
  -f submission.csv \
  -m "<submission message>"
```

The reason for the split: Kaggle lets you iterate on notebooks without burning submission quota. Only submit when you're confident the kernel ran correctly.

### 8. Verify

```bash
kaggle competitions submissions <competition-slug>
```

The new submission should appear. It may show PENDING while Kaggle re-runs the notebook on the hidden test set and scores it — this can take several minutes for code competitions.

## Error Reference

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| 401 Unauthorized | Token expired or missing | Check `.env` or `~/.kaggle/kaggle.json` |
| FileNotFoundError in kernel | Wrong mount paths | Add `os.listdir('/kaggle/input/')` debug cell |
| Dataset not mounting | Dataset still processing | Wait for `datasets status` to show "ready" |
| Kernel ERROR (no obvious cause) | Check the full log | Download with `kernels output`, read stderr |
| "already exists" on dataset create | Dataset was created before | Use `datasets version` instead of `datasets create` |
