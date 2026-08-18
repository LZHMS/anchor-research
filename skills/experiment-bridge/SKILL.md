---
name: experiment-bridge
description: |
   Takes an experiment plan, parses the milestones, and plans them out into the EXPERIMENT_TRACKER.md.
   Trigger: "解析计划", "parse plan", "规划实验", "初始化追踪器", "initialize tracker"
version: 2.0.0
author: Zhihao Li
license: MIT
metadata:
   hermes:
      tags: [Experiment, Planning, Tracker]
---

# Experiment Bridge: Plan Parsing & Tracker Initialization

Parse experiment plan and initialize the tracker: **$ARGUMENTS**

## Overview

This skill takes an experiment plan (`EXPERIMENT_PLAN.md`) and structures it into a tracking report (`EXPERIMENT_TRACKER.md`). It acts as the bridge between planning and execution, ensuring that all milestones are properly documented before `run-experiment` takes over the actual implementation and deployment.

## Constants

- **DOCS_ROOT = ""** — Optional root directory prefix for logs (e.g., `docs` implies finding files at `docs/refine-logs/`).

> Override: `/experiment-bridge "EXPERIMENT_PLAN.md" — docs root: docs`

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `<DOCS_ROOT>/refine-logs/FINAL_PROPOSAL.md` | Markdown | Recommended | Detailed method description for contextual understanding |
| `<DOCS_ROOT>/refine-logs/EXPERIMENT_PLAN.md` | Markdown | Yes | Claim-driven experiment roadmap |
| `<DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md` | Markdown | Recommended | Run-by-run execution table to create or update |

## Workflow

### Phase 1: Parse the Experiment Plan

Read `FINAL_PROPOSAL.md` and `EXPERIMENT_PLAN.md` and extract:

1. **Method details** from `FINAL_PROPOSAL.md` — to understand the architecture, proposed method, and context of the experiments.
2. **Run order and milestones** — which experiments run first (sanity → baseline → main → ablation → polish)
3. **For each experiment block:**
   - Dataset / split / task
   - Compared systems and variants
   - Metrics to compute
   - Setup details (backbone, hyperparameters, seeds)
   - Success criterion
   - Priority (MUST-RUN vs NICE-TO-HAVE)

### Phase 2: Initialize EXPERIMENT_TRACKER.md

Create or update `<DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md` with the following structure:

1. **## Overview & Milestones**: Table containing each mapped out run and its status. Template:
   ```markdown
   # Experiment Results

   **Date**: [today]
   **Plan**: <DOCS_ROOT>/refine-logs/EXPERIMENT_PLAN.md

   ## Overview & Milestone
   
   | Milestone | Run ID | System / Variant | Key Metric | Expected Value | Status | Notes |
   |-----------|--------|------------------|-----------|----------------|--------|-------|
   | M0: Sanity | R001 | baseline | loss | < 2.0 | PENDING | - |
   | M1: Baseline | R002 | baseline_full | accuracy | > 0.80 | PENDING | - |
   | M2: Main | R003 | our_method | accuracy | > 0.85 | PENDING | - |
   | M3: Ablation | R004 | our_method_no_X | accuracy | > 0.83 | PENDING | - |
   ```

2. **## Files Created/Updated**: A structured section to record code implementation (to be filled continually by `run-experiment`). Be sure to append to previous history explicitly under subsections like `### Models`, `### Trainers`, `### Losses`, `### Configs`. Template:
   ```markdown
   ## Files Created/Updated
   *(Append new records below preserving previous history)*
   
   ### Models
   - `models/EPStyleTalk.py` - StyleEncoderDecoder, StyleVQVAESingleCB
   - `models/EPStyleTalk_incremental.py` - StyleReasonerIncremental with TemporalLowPassBottleneck
   
   ### Trainers
   - `trainers/sanity.py` - StyleEncoderDecoderTrainer, StyleVQVAESingleCBTrainer
   - `trainers/discriminator.py` - IdentityDiscriminatorTrainer, EmotionDiscriminatorTrainer
   
   ### Losses
   - `losses/talker_losses.py` - Added DiscriminatorCELoss, StyleEncoderDecoderLoss
   
   ### Configs
   - `config/EPStyleTalk/m0_sanity/` - StyleEncoderDecoderTrainer.yaml, StyleVQVAESingleCBTrainer.yaml
   - `config/EPStyleTalk/m1_discriminator/` - IdentityDiscriminatorTrainer.yaml, EmotionDiscriminatorTrainer.yaml
   ```

3. **## Experiment Reports**: A structured section for `run-experiment` to log strategy adjustments, completions, and evaluation metrics per run. Template:
   ```markdown
   ## Experiment Reports
   
   ### R001: M0 Sanity Check (StyleEncoderDecoderTrainer)
   - **Status**: COMPLETED / FAILED / IN_PROGRESS
   - **Completion**: 100% (1/1 epochs)
   - **Key Metrics**:
      - Training Loss: 1.85
      - Validation Accuracy: 0.78
   - **Notes**: Sanity passed. Training loop verified. Ready for full baseline.
   - **Strategy Changes**: None
   
   ### R002: M1 Baseline (Full Training)
   - **Status**: COMPLETED
   - **Completion**: 100% (100/100 epochs)
   - **Key Metrics**:
      - Training Loss: 1.23
      - Validation Accuracy: 0.82
   - **Notes**: Baseline established. Main method deployment next.
   - **Strategy Changes**: Reduced learning rate from 0.001 to 0.0005 after epoch 50 due to plateau.
   
   ### R003: M2 Main Method (Our Method)
   - **Status**: IN_PROGRESS
   - **Completion**: 45% (45/100 epochs)
   - **Key Metrics**:
      - Training Loss: 1.10
      - Validation Accuracy: 0.84
   - **Notes**: On track. GPU memory stable.
   - **Strategy Changes**: None yet. Awaiting completion.
   ```

### Phase 3: Handoff

\`\`\`
📋 Experiment plan parsed & tracker initialized:
- Milestones: [N]
- Tracker updated at: <DOCS_ROOT>/refine-logs/EXPERIMENT_TRACKER.md

Next Step: Please invoke `/run-experiment` (or wait if fully autonomous) to implement code and execute.
\`\`\`