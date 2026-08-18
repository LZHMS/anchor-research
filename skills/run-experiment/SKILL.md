---
name: run-experiment
description: |
   Implement code, record file changes to EXPERIMENT_TRACKER.md, deploy ML experiments, monitor training health, review logs, evaluate, and adjust strategies.
   Trigger: "run experiment", "跑实验", "launch training", "implement and run", "review log", "复查日志", "监控训练", "check training"
version: 3.0.0
author: Zhihao Li
license: MIT
metadata:
   hermes:
      tags: [Experiment, Deployment, Implementation, Codebase, GPU, Monitoring, WandB]
---

# Run Experiment: Implementation, Tracking & Deployment

Implement, track, and run ML experiment: **$ARGUMENTS**

## Overview

This skill handles the actual implementation, tracking, deployment, and evaluation of machine learning experiments. Relies on the `EXPERIMENT_PLAN.md` for strategy and `EXPERIMENT_TRACKER.md` for historical and real-time tracking. It ensures code is written structurally, records all additions BEFORE execution, securely manages GPU allocation, deploys the bash script, evaluates the fixed-path log outputs, and loops back or adjusts strategies if expectations aren't met.

**Operating Modes:**
- **Deploy Mode**: Writes code, updates tracker, deploys the bash script.
- **Monitor/Review Mode**: Invoked during training or post-run. Checks WandB/local logs (`output/${DATASET}/${CFG}/output.log`) to evaluate training health (NaNs, loss divergence) and stops broken runs early. Updates tracker and triggers autonomous strategy pivots if needed.

Five principles dominate this skill:
1. **Traceable Code Implementation.** Every new model, trainer, or config file must be logged in `EXPERIMENT_TRACKER.md` before execution.
2. **Verify Before Launch.** Check `nvidia-smi` and memory before assigning GPUs. Auto-backup the codebase via git.
3. **Compare Against Ground Truth.** Evaluation *must* compare predictions against dataset labels/targets, never another model's output alone.
4. **Early Anomaly Detection.** Monitor early training steps for NaNs or diverging losses. Kill doomed runs early to prevent wasting GPU hours.
5. **Autonomous Strategy Loop.** If the evaluation fails, propose a strategy adjustment. If the user doesn't respond quickly (timeout), automate the strategy update into `EXPERIMENT_PLAN.md` and continue.

## Constants

- **BASE_REPO = false** — GitHub repo URL or local directory path. Initialize/clone if set.
- **AUTO_DEPLOY = true** — Automatically deploy after implementation.
- **SANITY_FIRST = true** — Always run a small sanity-check script first to catch pipeline bugs early.
- **DOCS_ROOT = ""** — Root for documentation logs (e.g., `docs`).

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `Run ID` | Argument | Optional | The specific run to deploy/evaluate (e.g., `R002`). If omitted, picks the next PENDING run. |
| `<DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md` | Markdown | Yes | Primary target for code logging and run reports |
| `<DOCS_ROOT>/refine-logs/EXPERIMENT_PLAN.md` | Markdown | Yes | Source of truth for criteria, budget, and base strategy |
| `<DOCS_ROOT>/refine-logs/FINAL_PROPOSAL.md` | Markdown | Recommended | Detailed method implementation definitions |

## Workflow

### Phase 1: Context & Run Identification

1. Read `<DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md`. Identify the target run (`Run ID` provided in arguments, otherwise select the next `PENDING` run from the `## Overview & Milestones` table).
2. Read `<DOCS_ROOT>/refine-logs/EXPERIMENT_PLAN.md` to retrieve hyperparameter specifics, required metrics, and success criteria for this run.
3. Read `<DOCS_ROOT>/refine-logs/FINAL_PROPOSAL.md` to understand exactly what needs to be coded if this is a novel method or ablation.

### Phase 2: Implement Experiment Code

1. Use `/structured-codebase` principles to build modular components:
   - **Trainers**: Inherit `TrainerBase`, register with `@TRAINER_REGISTRY.register()`.
   - **Models/Losses/Datasets**: Place in corresponding folders (`models/`, `losses/`, `dataset/`), leveraging the registry system.
   - **Configs**: Write YACS `.yaml` configs in `config/<category>/`.
   - **Bash Scripts**: Write the execution loop in `scripts/<category>/<script_name>.sh`.
2. **Mandatory Documentation Step**: Immediately open `<DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md` and append to the `## Files Created/Updated` section.
   - Do **NOT** overwrite previous lines.
   - Append formatted bullet points under the relevant `### Models`, `### Trainers`, `### Losses`, or `### Configs` headers.

### Phase 3: Pre-flight & GPU Allocation

Check GPU availability:
```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
# or for Mac MPS:
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

Allocate single free GPU for sanity checks, or multiple GPUs for full deployments. Configure the bash script (`DISTRIBUTED=True`, `GPU_IDS`) accordingly.

### Phase 4: Code Backup & Deploy

1. **Update `scripts/setup.sh` (Unified Entry Point)**:
   The `structured-codebase` framework uses `scripts/setup.sh` as the centralized execution manager. 
   - Add or uncomment the specific bash command (e.g., `bash scripts/<category>/<script>.sh <args>`) for the current Run ID.
   - Ensure all other runs are commented out.
   - Document the arguments, milestone, and target metrics as comments above the command in `setup.sh` for clarity.
2. Sync/backup codebase: 
   ```bash
   git add -A && git commit -m "backup: pre-experiment run" && git push
   ```
3. Deploy the experiment:
   ```bash
   CUDA_VISIBLE_DEVICES=<gpu_id> bash scripts/setup.sh
   ```
   *(Note: The structured codebase already redirects and saves terminal outputs to `output/${DATASET}/${CFG}/output.log` automatically.)*

*(If `SANITY_FIRST=true` and this is a new pipeline, deploy a minimal sanity run first and wait for completion before launching full runs.)*

### Phase 5: Monitor Training Health, Review Logs & Evaluate

During an ongoing run (Monitoring) or after completion (Evaluation):
1. **Locate Metrics & Logs**: 
   - Check the top of the local log (`output/${DATASET}/${CFG}/output.log`) to find the `ENV.WANDB` configuration block dumped by `structured-codebase`.
   - Extract `ENTITY`, `PROJECT`, and `NAME` from this dump to pinpoint the exact WandB run.
   - Read WandB metrics via API if enabled (`import wandb; api = wandb.Api(); run = api.run("<entity>/<project>/<name>"); run.history()`).
   - If WandB is unreachable or disabled, tail the local log: `tail -n 100 output/${DATASET}/${CFG}/output.log` to observe local iterations.
2. **Active Training Health Check**:
   Evaluate current metrics to decide the run's fate.
   | Signal | Judgment | Action |
   |--------|----------|--------|
   | NaN/Inf in loss | **Clearly bad** | **KILL** process, trigger Phase 6 |
   | Loss diverging (increasing for >N steps) | **Clearly bad** | **KILL** process, trigger Phase 6 |
   | Eval metrics significantly worse than baseline | **Clearly bad** | **KILL** process, trigger Phase 6 |
   | Loss decreasing, metrics improving | **Clearly fine** | Continue monitoring |
   | Loss flat but not diverging | **Unsure** | Spawn subagent (`runSubagent`) |
   | Metrics noisy, can't tell trend | **Unsure** | Spawn subagent (`runSubagent`) |
   | Slightly worse than baseline but still early | **Unsure** | Spawn subagent (`runSubagent`) |
3. **Update `## Experiment Reports`** in `EXPERIMENT_TRACKER.md`.
   - Document completion status, final/latest matching metrics, curve behavior, or tracebacks.
   - If killed early, distinctly record the anomaly (e.g., "Killed at Epoch 5 due to NaN loss").
4. **Strategy Evaluation**:
   - Check `EXPERIMENT_PLAN.md` criteria: Did the run perform as expected?
   - If results fail, underperform, or if the run was killed early due to instability, sequence to Phase 6.

### Phase 6: Strategy Adjustment (The Timeout Rule)

If the experiment underperforms or fails health checks:
1. Identify the root cause (e.g., loss plateau, memory leak, low accuracy, NaN error).
2. Formulate a strategy change (e.g., reduce LR, add gradient clipping, tweak loss weights).
3. Use `vscode_askQuestions` to request user approval for the new strategy.
4. **TIMEOUT / AUTONOMOUS RULE**: If the user does not respond within a reasonable timeout, or if in full autonomous mode, automatically apply the new strategy to keep the loop moving:
   - Update `EXPERIMENT_PLAN.md` with the new strategy details.
   - Note the specific strategy override in the `EXPERIMENT_TRACKER.md` report column.
   - Loop back to Phase 2 to adjust code/configs and retry.

### Phase 7: Notification

Notify the user of completion or automated strategy pivots using `hermes` CLI (WeChat/QQ integration) or terminal ping.

## Key Rules

- **ALWAYS WRITE FILES TO TRACKER BEFORE RUNNING.** If the agent or PC crashes during execution, the user must still have a historical log of what files were added for the experiment.
- **NEVER OVERWRITE FILE HISTORY.** When updating `## Files Created/Updated`, specifically append new items underneath the existing ones.
- **GROUND TRUTH ONLY.** Evaluation must compare predictions directly against the dataset's actual labels/targets.
- **AUTO-RESUME.** Do not hang indefinitely waiting for the user to approve a failed run's fix. Automate the strategy pivot, document it in both the Plan and Tracker, and resume.
