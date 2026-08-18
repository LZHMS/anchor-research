---
name: training-check
description: |
  Periodically check WandB metrics during training to catch problems early (NaN, loss divergence, idle GPUs).
  Trigger: "check training", "monitor metrics", "is training healthy", "check wandb"
version: 1.0.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [Training, Monitoring, WandB, Evaluation]
---

# Training Check: Automated Quality Monitoring

Periodically read WandB metrics during training to catch problems early: **$ARGUMENTS**

## Overview

This skill periodically checks training metrics (like WandB) to catch issues early, saving GPU hours on broken runs. It operates differently from basic system monitors by analyzing the actual machine learning quality of the run.

Four principles dominate this skill:

1. **Quality Over Health.** Process timeouts are for system watchdogs. This skill evaluates if the model is actually learning (loss trends, NaNs, degradation).
2. **Trends Over Spikes.** Do not kill a run over a single noise spike. Evaluate the trajectory over multiple checkpoints.
3. **Direct Judgment.** Make clear decisions on obvious failures or successes directly from the metrics. If unsure, wait for more data.
4. **Progressive Scaling.** Gradually increase the checking interval (10m → 60m) as the training stabilizes.

## Constants

- **WANDB_ENTITY / PROJECT** — Read from workspace context or passed as an argument (`<entity>/<project>/<run_id>`).
- **CHECK_INTERVAL** — Starts at 10 minutes, gradually increasing if healthy (10 → 20 → 30 → 60).

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `WandB Run Path` | Argument | Yes | The target run identifier (`<entity>/<project>/<run_id>`) to check |
| `Context` | Workspace| Optional | Project-specific metric expectations and baseline targets |
| `output.log` | Text | Fallback | Local log file (in `output/.../`) if WandB is unreachable or disabled |

Input handling rules:

1. Trigger this skill *after* training is confirmed running (session alive, loss decreasing for first few steps).
2. Use this for monitoring **training QUALITY, not process HEALTH** (which should be handled by basic OS process checks like `ps` / `nvidia-smi`).
3. Can be fired periodically via a simple bash loop or manual checks during training.

## Workflow

### Phase 1: Read WandB Metrics

Ensure the local environment is authenticated with WandB (e.g., `WANDB_API_KEY` is set in the environment or `wandb login` was previously executed). 

```python
import wandb
# Relies on local ~/.netrc or WANDB_API_KEY env matching the target run
api = wandb.Api()
run = api.run("<entity>/<project>/<run_id>")
history = run.history()
```

If WandB is unreachable (API error, network issue) or disabled, fall back to reading the local log file created by `structured-codebase` (typically `output.log` inside the `output/<dataset>/<cfg_name>/` run directory):
```bash
tail -n 100 output/<dataset>/<trainer_name>/output.log
```

Check these signals:
- **Loss trend**: Is training loss decreasing over the last N steps?
- **Eval metrics**: Are evaluation metrics improving (or at least not degrading)?
- **NaN / Inf**: Any NaN or Inf values in loss or gradients?
- **Spikes**: Sudden large jumps in loss (>10x normal variance)?
- **Learning rate**: Is the schedule behaving as expected?
- **Gradient norm**: Exploding or vanishing?

### Phase 2: Judgment

| Signal | Judgment | Action |
|--------|----------|--------|
| NaN/Inf in loss | **Clearly bad** | Stop training, investigate |
| Loss diverging (increasing for >N steps) | **Clearly bad** | Stop training, investigate |
| Eval metrics significantly worse than baseline | **Clearly bad** | Stop training, investigate |
| Loss decreasing, metrics improving | **Clearly fine** | Continue, increase check interval |
| Loss flat but not diverging | **Unsure** | → Phase 3 (Subagent Review) |
| Metrics noisy, can't tell trend | **Unsure** | → Phase 3 (Subagent Review) |
| Slightly worse than baseline but still early | **Unsure** | → Phase 3 (Subagent Review) |

### Phase 3: Subagent Review (only when unsure)

Only escalate to an isolated subagent when the signal is ambiguous. For clearly good or clearly bad signals, act directly.

Use the `runSubagent` tool (or equivalent delegation tool) to spawn an isolated subagent to deeply review the metrics and logs:
- **Description**: Review ambiguous training metrics for run `<run_id>`
- **Prompt**: 
  ```text
  TRAINING HEALTH CHECK — need your judgment on ambiguous metrics.
  
  Run: <entity>/<project>/<run_id>
  Current epoch/step: X / Y total
  Training loss (last 10 checkpoints): [values]
  Eval metrics (last 3 evals): [values]
  Baseline reference: [numbers from paper/reproduction]
  
  What I'm unsure about: [specific concern]
  
  Analyze the current progress. Respond with exactly one of:
  - STOP: clearly problematic, should kill training
  - CONTINUE: looks fine, check again next interval
  - WAIT: not enough data to judge, check again sooner
  ```

### Phase 4: Act

| Decision | Action |
|----------|--------|
| **Stop** | Kill the training session. Save the WandB run URL, key metrics, and reason for stopping. Log to project notes for debugging. |
| **Continue** | Do nothing. Will be invoked again at next interval (increase interval if consistently healthy). |
| **Wait** | Do nothing but keep the current short interval (don't increase). |

## Key Rules

- Do not stop training on first sign of noise — some loss spikes are normal. Look at **trends over multiple checkpoints**.
- When stopping training, always save the WandB run URL and key metrics as evidence.
- If both WandB and log files are unreachable, report the connectivity issue and try again next interval. Do not assume training is broken.
- Gradually increase check interval when healthy (10 → 20 → 30 → 60 min). Reset to 10 min after any anomaly.
- For automation, use background polling scripts (e.g., a simple `while` loop with `sleep` checking logs) rather than asking the user to manually trigger checks repeatedly.
