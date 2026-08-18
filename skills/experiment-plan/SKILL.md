---
name: experiment-plan
description: 'Turn a refined proposal into a claim-driven experiment roadmap with execution order, checkpoints, and paper-ready evidence mapping. Use when the user asks for experiment plan, ablation matrix, evaluation protocol, run order, compute budget, or claim-to-evidence validation after research-refine.'
argument-hint: 'Paste proposal context or point to refine-logs outputs; include constraints on compute, data, and timeline.'
user-invocable: true
version: 2.0.0
author: Zhihao Li
license: MIT
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent
metadata:
  hermes:
    tags: [Experiment, Planning, Claims, Validation, Ablation]
---

# Experiment Plan: Claim-Driven, Paper-Oriented Validation

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill when the method direction is stable and the next question is:
what exact runs should be launched, in what order, to defend the paper's claims?

This skill converts a proposal into a compact:

- claim -> evidence -> block -> run-order map
- must-run vs nice-to-have execution plan
- reviewer-facing risk and decision-gate checklist

The objective is not benchmark sprawl. The objective is a defendable paper story.

## Constants

- **OUTPUT_DIR = `refine-logs/`**
- **MAX_PRIMARY_CLAIMS = 2**
- **MAX_CORE_BLOCKS = 5**
- **MAX_BASELINE_FAMILIES = 3**
- **DEFAULT_SEEDS = 3**
- **MAX_MILESTONES = 5**
- **PLAN_SCORECARD_FIELDS = claim_coverage, novelty_isolation, simplicity_defense, frontier_justification, run_feasibility**

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| refine-logs/FINAL_PROPOSAL.md | Markdown | Recommended | Canonical method thesis and mechanism details |
| refine-logs/REVIEW_SUMMARY.md | Markdown | Recommended | Reviewer concerns to convert into decisive experiments |
| refine-logs/REFINEMENT_REPORT.md | Markdown | Recommended | Constraints, unresolved risks, score evolution |
| User prompt / notes | Text | Optional | Missing context fallback |

Input handling rules:

1. If all refine-logs files exist, treat them as primary ground truth.
2. If one or more files are missing, derive context from user prompt and mark confidence as lower.
3. Never invent claims, constraints, or prior results.
4. Reuse proposal assumptions (data, model size, timeline, compute) unless user explicitly changes them.

## State Persistence (Checkpoint Recovery)

Long planning sessions may be interrupted. Persist state to:

- `refine-logs/EXPERIMENT_PLAN_STATE.json`

State schema:

```json
{
  "phase": "claims",
  "status": "in_progress",
  "round": 0,
  "timestamp": "2026-04-25T10:00:00",
  "context_sources": ["FINAL_PROPOSAL", "REVIEW_SUMMARY"],
  "must_run_count": 0,
  "nice_to_have_count": 0
}
```

Field definitions:

- `phase`: `load_context` / `claims` / `storyline` / `blocks` / `run_order` / `outputs` / `done`
- `status`: `in_progress` / `completed`
- `round`: plan drafting iteration, start from 0
- `context_sources`: which upstream files were used
- `must_run_count` and `nice_to_have_count`: current run inventory

Write rules:

- Overwrite the state file after each completed phase.
- If state exists and is in-progress within 24h, resume from next phase.
- If state is stale (>24h) or completed, start fresh.

## Output Structure

```
refine-logs/
├── EXPERIMENT_PLAN_STATE.json
├── EXPERIMENT_PLAN.md
├── EXPERIMENT_TRACKER.md
└── score-history.md (optional update if present)
```

## Workflow

### Initialization (Checkpoint Recovery)

1. Check `refine-logs/EXPERIMENT_PLAN_STATE.json`.
2. If resumable, continue from saved phase.
3. If stale/completed/missing, start from Phase 0.

### Phase 0: Load Proposal Context

Read in order if present:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`

Extract:

- Problem Anchor
- Dominant contribution
- Optional supporting contribution
- Critical reviewer concerns
- Data / compute / timeline constraints
- Central frontier primitive (if any)

Checkpoint:

- Write state with `phase = load_context`.

### Phase 1: Freeze the Paper Claims

Before planning runs, define exactly what must be defended.

Use this structure:

- Primary claim: mechanism-level core claim
- Supporting claim: optional and tightly linked to primary claim
- Anti-claim to rule out: strongest skeptical explanation
- Minimum convincing evidence: what changes reviewer belief

Rules:

- Do not exceed `MAX_PRIMARY_CLAIMS` unless inseparable.
- Every later block must map to at least one claim.

Checkpoint:

- Write state with `phase = claims`.

### Phase 2: Build the Experimental Storyline

Construct a compact block set. Default candidates:

1. Main anchor result
2. Novelty isolation
3. Simplicity/elegance check
4. Frontier necessity check (only if frontier primitive is central)
5. Failure analysis or qualitative diagnosis

For each candidate, classify as:

- Main paper
- Appendix
- Cut

Rules:

- Prefer strong baseline families over long lists.
- Keep main story compact, reviewer-decisive, and compute-realistic.

Checkpoint:

- Write state with `phase = storyline`.

### Phase 3: Specify Each Kept Block

For each kept block, specify all fields:

- Claim tested
- Why this block exists
- Dataset / split / task
- Compared systems
- Metrics (decisive first)
- Setup details (backbone, trainable parts, key hyperparams, budget, seeds)
- Success criterion
- Failure interpretation
- Table / figure target
- Priority: MUST-RUN or NICE-TO-HAVE

Special rules:

- Simplicity check compares final method against overbuilt or tempting-extra variant.
- Frontier necessity check compares chosen modern primitive against strongest plausible simpler alternative.
- If proposal is intentionally non-frontier, explicitly skip frontier block with rationale.

Checkpoint:

- Write state with `phase = blocks` and update run counters.

### Phase 4: Turn Plan Into Execution Order

Use milestone sequence:

1. Sanity stage
2. Baseline stage
3. Main method stage
4. Decision stage
5. Polish stage

For each milestone, define:

- Goal
- Runs
- Decision gate (stop/go)
- Cost (GPU-hours or equivalent)
- Turnaround time
- Risk and mitigation

Rules:

- Separate must-run from nice-to-have.
- Do not let appendix runs block core evidence.

Checkpoint:

- Write state with `phase = run_order`.

### Phase 5: Write Outputs

#### Step 5.1: Write refine-logs/EXPERIMENT_PLAN.md

Use this template:

```markdown
# Experiment Plan

**Problem**: [problem]
**Method Thesis**: [one-sentence thesis]
**Date**: [today]

## Claim Map
| Claim | Why It Matters | Minimum Convincing Evidence | Linked Blocks |
|-------|-----------------|-----------------------------|---------------|
| C1    | ...             | ...                         | B1, B2        |

## Paper Storyline
- Main paper must prove:
- Appendix can support:
- Experiments intentionally cut:

## Experiment Blocks

### Block 1: [Name]
- Claim tested:
- Why this block exists:
- Dataset / split / task:
- Compared systems:
- Metrics:
- Setup details:
- Success criterion:
- Failure interpretation:
- Table / figure target:
- Priority: MUST-RUN / NICE-TO-HAVE

### Block 2: [Name]
...

## Run Order and Milestones
| Milestone | Goal | Runs | Decision Gate | Cost | Risk |
|-----------|------|------|---------------|------|------|
| M0        | ...  | ...  | ...           | ...  | ...  |

## Compute and Data Budget
- Total estimated GPU-hours:
- Data preparation needs:
- Human evaluation needs:
- Biggest bottleneck:

## Risks and Mitigations
- [Risk]:
- [Mitigation]:

## Final Checklist
- [ ] Main paper tables are covered
- [ ] Novelty is isolated
- [ ] Simplicity is defended
- [ ] Frontier contribution is justified or explicitly not claimed
- [ ] Nice-to-have runs are separated from must-run runs
```

#### Step 5.2: Write refine-logs/EXPERIMENT_TRACKER.md

Use this template:

```markdown
# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|--------|-----------|---------|------------------|-------|---------|----------|--------|-------|
| R001   | M0        | sanity  | ...              | ...   | ...     | MUST     | TODO   | ...   |
```

Tracker rules:

- Compact and execution-oriented.
- Only include runnable items.
- Keep status values minimal: `TODO`, `RUNNING`, `DONE`, `BLOCKED`.

#### Step 5.3: Optional score-history update

If `refine-logs/score-history.md` exists, append a concise section describing planning-readiness checks for:

- claim_coverage
- novelty_isolation
- simplicity_defense
- frontier_justification
- run_feasibility

#### Step 5.4: Completion summary to user

Use this output format:

```text
Experiment plan ready.

Must-run blocks:
- [Block 1]
- [Block 2]

Highest-risk assumption:
- [risk]

First three runs to launch:
1. [run]
2. [run]
3. [run]

Plan file: refine-logs/EXPERIMENT_PLAN.md
Tracker file: refine-logs/EXPERIMENT_TRACKER.md
```

Checkpoint:

- Write state with `phase = done`, `status = completed`.

## Output Protocols

Follow shared protocols when available:

- [Output Versioning Protocol](../shared-references/output-versioning.md)
- [Output Manifest Protocol](../shared-references/output-manifest.md)
- [Output Language Protocol](../shared-references/output-language.md)

## Key Rules

- Every experiment must defend a claim; otherwise cut it.
- Prefer compact paper story over benchmark wishlist.
- Defend simplicity explicitly using deletion or overbuilt comparisons.
- Defend frontier choices explicitly when claimed as central.
- Prefer strong baselines over long baseline lists.
- Separate must-run from nice-to-have and protect main-paper critical path.
- Reuse proposal constraints; do not inflate assumptions.
- Do not fabricate results.
- If write fails due to size, retry via Bash chunk write silently.

## Composing with Other Skills

```text
/research-refine-pipeline -> one-shot method + experiment planning
/research-refine -> method and claim refinement
/experiment-plan -> detailed experiment roadmap
/run-experiment -> execute runs
/auto-review-loop -> iterate after empirical results
```
