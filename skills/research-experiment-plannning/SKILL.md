---
name: research-experiment-plannning
description: 'Turn a reviewed proposal into a claim-driven experiment roadmap with execution order, checkpoints, and paper-ready evidence mapping. Use when the user asks for experiment plan, ablation matrix, evaluation protocol, run order, compute budget, or claim-to-evidence validation after research-ideas.'
argument-hint: 'Paste proposal context or point to docs/research-ideas/ outputs; include project and constraints on compute, data, and timeline.'
user-invocable: true
version: 3.0.0
author: Zhihao Li
license: MIT
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent
metadata:
  category: research
  tags: [research, experiment-planning, claims, validation, ablation]
  related_skills: [research-literature-review, research-literature-summary, research-ideas, research-retrofit, research-run-experiment, research-paper-plan]
  hermes:
    tags: [Experiment, Planning, Claims, Validation, Ablation]
---

# Research Experiment Planning: Claim-Driven, Paper-Oriented Validation

Refine and concretize: **$ARGUMENTS**

Apply the [shared human anchor gates](../research-shared-references/anchor-gates.md). A reviewed proposal or candidate choice is not permission to plan; an authored plan is not user approval; plan approval is not execution permission.

## Overview

Use this skill when the method direction is stable and the next question is:
what exact runs should be launched, in what order, to defend the paper's claims?

This skill converts a proposal into a compact:

- claim -> evidence -> block -> run-order map
- must-run vs nice-to-have execution plan
- reviewer-facing risk and decision-gate checklist

The objective is not benchmark sprawl. The objective is a defendable paper story.

Own experiment design and initial task decomposition, not live execution progress.
Create the initial task inventory and empty execution-record sections in the single
`EXPERIMENT_TRACKER.md`; [research-run-experiment](../research-run-experiment/SKILL.md) owns subsequent
execution, observation, status, attempt and result updates. Planning state records
planning phases only; it is not a second experiment-progress database. Replanning
preserves the runner's historical evidence and reconciles task applicability.

## Constants

- **PROJECT_ROOT** — Explicit project argument, otherwise the bound handoff's accepted project root, otherwise the current working project directory; never the installed skill directory. Resolve relative paths against this root.
- **DOCS_ROOT = `<PROJECT_ROOT>/docs`**
- **IDEAS_DIR = `<DOCS_ROOT>/research-ideas`**
- **OUTPUT_DIR = `<DOCS_ROOT>/research-experiment-plannning`**
- **MAX_PRIMARY_CLAIMS = 2**
- **MAX_CORE_BLOCKS = 5**
- **MAX_BASELINE_FAMILIES = 3**
- **DEFAULT_SEEDS = 3**
- **MAX_MILESTONES = 5**
- **PLAN_SCORECARD_FIELDS = claim_coverage, novelty_isolation, simplicity_defense, frontier_justification, run_feasibility**

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `<IDEAS_DIR>/FINAL_PROPOSAL.md` | Markdown | Recommended | Canonical method thesis and mechanism details |
| `<IDEAS_DIR>/REVIEW_SUMMARY.md` | Markdown | Recommended | Reviewer concerns to convert into decisive experiments |
| `<IDEAS_DIR>/REFINEMENT_REPORT.md` | Markdown | Recommended | Constraints, unresolved risks, score evolution |
| User prompt / notes | Text | Optional | Missing context fallback |
| Supplied codebase/repository constraints | Text / paths | Optional | Existing code source or framework assumptions that affect experiment design; execution resolves the actual implementation base |

Input handling rules:

1. Explicit user proposal files, notes, and project take precedence, followed by a bound handoff's exact paths, then the exact default `<IDEAS_DIR>/FINAL_PROPOSAL.md`. Resolve companion paths from that binding or the fixed `IDEAS_DIR`; never scan for dated folders or select by modification time. An explicitly supplied missing file is an error.
2. Record actual paths and content fingerprints from `REVIEW_STATE.json` or the handoff. Verify the delivered proposal's byte SHA-256 against `final_proposal_sha256`; keep its reviewed source path/hash separate, and accept review scores only for the unchanged snapshot matching `last_reviewed_proposal_sha256`. Literature defaults to `<DOCS_ROOT>/research-literature-review/research_foundation_review.json` and `<DOCS_ROOT>/research-literature-summary/`. Verify the summary manifest's resolved input path and canonical JSON `input_sha256` match the actual review, and its completed per-paper contexts and overview `papers_sha256` bindings remain valid. Changed sources invalidate the old bundle; matching directories alone prove nothing. For other missing context, use available user notes and label lower confidence and the precise gaps.
3. Never invent claims, constraints, or prior results.
4. Reuse proposal assumptions (data, model size, timeline, compute) unless user explicitly changes them.
5. For standalone user context without an existing proposal, write to the same fixed `OUTPUT_DIR`, bind the supplied context and its digest, and record absent upstream artifacts as absent. Genuine user adoption of that input scope must be recorded before final planning approval. Keep method inputs in `IDEAS_DIR` and experiment outputs in `OUTPUT_DIR`; do not assume they are colocated.
6. If ideas state is awaiting candidate selection or its confirmed input/proposal fingerprints no longer match, stop the downstream handoff. A prior `FINAL_PROPOSAL.md` belongs to the prior selection and is not approval of the new candidates.
7. When entering from `research-ideas` or `research-retrofit`, read the bound `method_state_path` and verify `anchor_approval.approved: true` and `proposal_approval.approved: true` bound to the actual delivered proposal and anchor SHA-256. Unapproved or stale method proposals block experiment planning.

### Codebase responsibility boundary

Record an explicitly supplied `codebase_kind` (`existing` or `research-structured-codebase`),
`repo_path`, `repo_url` and `repo_revision` when they constrain architecture, baselines,
data, evaluation or budget. Resolve known local paths against `PROJECT_ROOT`; inspect
only accessible, authorized files needed for planning and bind their actual hashes in
the context inventory. Preserve user intent and any available pinned revision.

Do not clone repositories, bootstrap templates, install dependencies, select a framework
on the user's behalf or rewrite project code during planning. Unknown codebase fields
stay JSON `null`; a valid design does not require forcing a new project structure.
[research-run-experiment](../research-run-experiment/SKILL.md) owns deployment-time
selection, compatibility checks and initialization/reuse. Changing those constraints
later invalidates affected design/consent bindings rather than silently changing the
scientific experiment. Project docs stay in this project's fixed output directory even
when execution uses an external local repository.

## Research workflow and confirmed entry

This skill connects the preceding research stages without redoing their work:

- [research-literature-review](../research-literature-review/SKILL.md) supplies
  `docs/research-literature-review/research_foundation_review.json`.
- [research-literature-summary](../research-literature-summary/SKILL.md) supplies the
  matching completed overview and per-paper analyses in `docs/research-literature-summary/`.
- [research-ideas](../research-ideas/SKILL.md) supplies the selected, designed and reviewed
  proposal plus its reports in `docs/research-ideas/`. Its candidate-selection gate must
  be resolved before this downstream handoff can use the current proposal.
- [research-retrofit](../research-retrofit/SKILL.md) may return an implemented, updated
  proposal for replanning when claims changed or required experiments remain. Use its
  actual `report_path`, `code_paths`, `anchor_path`, and `docs/research-retrofit/` outputs
  (`REBUTTAL_REVIEW.md`, `RETROFIT_REPORT.md`, `RETROFIT_STATE.json`); absent companions remain absent rather than borrowing old
  ideas reports or their scores. Carry the new final-export/reviewed-source distinction.

An explicit `/research-experiment-plannning "<actual absolute proposal path>" project: "<actual absolute project root>"`
is a request to execute planning, not training. Otherwise accept only a unique latest
unresolved `NEXT_SKILL_HANDOFF` whose `from_skill` is `research-ideas` or `research-retrofit`,
`to_skill` is `research-experiment-plannning`, and `status` is `awaiting_confirmation`.

A direct reply such as `可以`, `继续`, or `yes` to that offer accepts this bound planning
step once. Approval of an earlier literature step or candidate choice is not planning
consent. Quoted assent, `可以，但先别执行`, refusal, or a bare affirmative without a
specific pending offer must not start planning. A refusal marks the offer `declined`;
an ambiguous reply requires clarification.

On acceptance, mark the offer `accepted`, verify its `invocation`, `project_root`,
`docs_root`, exact named input paths, every `artifacts` file byte SHA256 and all existing
source/summary/proposal/report semantic fingerprints before writes. Use the host's
normal skill loader, echo the resolved invocation, and execute without repeating entry
confirmation. Pass the actual named packet fields as overrides to the normal input
loader; optional absent fields stay absent. Do not substitute another input on changed
bindings: mark `stale`, disclose the mismatch, and require a refreshed specifically
confirmed offer or new direct invocation. An awaiting candidate selection cannot be
bypassed by an old FINAL. An explicit changed invocation supersedes the pending offer.
Silence, timeout or autonomous mode cannot approve entry to this or a later skill.

Set the offer to `running` during planning, `completed` only after the plan, tracker and
state are actually written, or `failed` on a real execution/prerequisite failure. A
consumed offer cannot authorize another planning pass. Completion may recommend
`research-run-experiment` with exact run IDs, mode and bound input paths, but does not authorize
training, code deployment, permanent PKBase filing, or repeat execution.


## State Persistence (Checkpoint Recovery)

Long planning sessions may be interrupted. Persist state to:

- `<OUTPUT_DIR>/EXPERIMENT_PLAN_STATE.json`

State schema:

```json
{
  "phase": "claims",
  "status": "in_progress",
  "round": 0,
  "timestamp": "2026-04-25T10:00:00",
  "project_root": "<actual absolute project root>",
  "output_dir": "<actual absolute research-experiment-plannning directory>",
  "ideas_dir": "<actual absolute ideas directory, or null when absent>",
  "proposal_path": "<actual absolute proposal path, or null when absent>",
  "proposal_sha256": "<SHA-256 of actual proposal UTF-8 bytes, or null>",
  "reviewed_proposal_path": "<actual immutable reviewed source path, or null>",
  "reviewed_proposal_sha256": "<SHA-256 of exact reviewed source bytes, or null>",
  "method_state_path": "<actual ideas or retrofit state path, or null>",
  "method_state_sha256": "<SHA-256 of actual method owner state bytes, or null>",
  "foundation_input_json": "<actual paired review JSON path, or null when absent>",
  "foundation_input_sha256": "<canonical JSON digest of actual review, or null>",
  "summary_dir": "<actual paired summary directory, or null when absent>",
  "summary_papers_sha256": "<validated completed-paper corpus digest, or null>",
  "codebase_kind": null,
  "repo_path": null,
  "repo_url": null,
  "repo_revision": null,
  "context_sources": ["<actual absolute proposal path>", "<actual absolute review summary path>"],
  "context_sha256": {"<actual source path or user-context key>": "<content digest>"},
  "mode": "<planning from reviewed proposal or standalone user context>",
  "intent_sha256": "<SHA-256 of actual supplied planning intent and constraints>",
  "must_run_count": 0,
  "nice_to_have_count": 0,
  "approved_task_inventory": [],
  "task_inventory_sha256": null,
  "plan_approval": {
    "approved": false,
    "plan_sha256": null,
    "task_inventory_sha256": null,
    "confirmation_reference": null
  }
}
```

Field definitions:

- `phase`: `load_context` / `claims` / `storyline` / `blocks` / `run_order` / `outputs` / `done`
- `status`: `in_progress` / `completed`
- `round`: plan drafting iteration, start from 0
- `project_root`, `output_dir`, `ideas_dir`, `proposal_path`, `reviewed_proposal_path`, `foundation_input_json`, `summary_dir`: actual input/output paths; use JSON `null` for absent upstream inputs.
- `proposal_sha256` and `reviewed_proposal_sha256`: separate delivered-export and reviewed-snapshot byte hashes; never transfer a score to a changed method.
- `foundation_input_sha256` and `summary_papers_sha256`: actual canonical review and validated completed-summary bindings, not directory identifiers.
- `context_sources` / `context_sha256`: exact source paths or supplied user context with their digests. JSON uses SHA-256 of UTF-8 serialization with sorted keys, `ensure_ascii=False`, and separators `(',', ':')`; text uses actual UTF-8 bytes.
- `must_run_count` and `nice_to_have_count`: current run inventory
- `codebase_kind`, `repo_path`, `repo_url`, `repo_revision`: supplied planning constraints only; null means unresolved, not permission to bootstrap. Bind these values in context/intent recovery and pass them unchanged to execution.

Write rules:

- Update the fixed state file after each completed phase.
- If state is in-progress within 24h and project, paths, actual content digests, proposal fingerprint, mode and user intent all match, resume from the next phase.
- If stale (>24h), completed, or any binding changed, start fresh; never treat old review scores or empirical evidence as current approval.
- Update current plan outputs in place. Preserve tracker file history and completed run reports with their original plan/proposal fingerprints; revalidate their applicability explicitly, and allocate new unused experimental IDs for new runnable items rather than recycling old `R001` results.

## Output Structure

```
<DOCS_ROOT>/research-experiment-plannning/
├── EXPERIMENT_PLAN_STATE.json
├── EXPERIMENT_PLAN.md
└── EXPERIMENT_TRACKER.md
```

An optional planning-readiness section may be appended to the selected `<IDEAS_DIR>/score-history.md` if it already exists; do not copy method artifacts into the experiment folder.

## Workflow

### Initialization (Checkpoint Recovery)

1. Resolve the input bundle and check `<OUTPUT_DIR>/EXPERIMENT_PLAN_STATE.json`.
2. If resumable, continue from saved phase.
3. If stale/completed/missing, start from Phase 0.

### Phase 0: Load Proposal Context

Read in order if present:

- `<IDEAS_DIR>/FINAL_PROPOSAL.md` (or the explicit proposal path)
- `<IDEAS_DIR>/REVIEW_SUMMARY.md`
- `<IDEAS_DIR>/REFINEMENT_REPORT.md`

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

#### Step 5.1: Write `<OUTPUT_DIR>/EXPERIMENT_PLAN.md`

Use this template:

```markdown
# Experiment Plan

**Problem**: [problem]
**Method Thesis**: [one-sentence thesis]
**Date**: [today]
**Project Root**: [actual absolute project root]
**Proposal**: [actual absolute proposal path, or absent]
**Proposal SHA-256**: [actual delivered proposal byte hash, or absent]
**Reviewed Proposal**: [actual immutable source path and byte hash, or absent/unreviewed]
**Ideas Directory**: [actual absolute ideas directory, or absent]
**Foundation Review**: [actual absolute paired JSON path and canonical digest, or absent]
**Literature Summary**: [actual absolute paired summary directory and validated papers_sha256, or absent]
**Codebase Constraints**: [supplied kind/local path/remote/revision, or unresolved; no initialization performed]

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

#### Step 5.2: Write `<OUTPUT_DIR>/EXPERIMENT_TRACKER.md`

Translate each retained block into concrete tasks before offering execution:

- Allocate one stable, unused Run ID for each planned dataset/split, system/variant,
  seed and configuration combination that needs an independent execution. Expand only
  combinations actually justified in the plan, not an invented Cartesian product.
- Carry the claim/block, milestone, metrics, success criterion, priority and resource
  constraints into each task. Distinguish `MUST` from `NICE` using the plan's
  MUST-RUN/NICE-TO-HAVE priorities.
- Record explicit `Depends On` Run IDs and the milestone decision gate. Dependencies
  must exist, be acyclic and be compatible with the task's method/evidence binding.
  Pending dependencies keep a planned task `TODO` but not eligible for launch.
  A known missing prerequisite or unmet gate is `BLOCKED`, with the actual reason.
- Preserve stable identities for unchanged tasks. New or substantively changed tasks
  get new unused IDs; never recycle an executed ID for a different configuration.

Use this structure, filling only actual planned values and observed history:

```markdown
# Experiment Tracker

**Project Root**: [actual absolute project root]
**Plan**: [actual absolute EXPERIMENT_PLAN.md path]
**Proposal**: [actual absolute proposal path, or absent]
**Plan SHA-256**: [actual plan byte hash]
**Proposal SHA-256**: [actual delivered proposal byte hash, or absent]

## Codebase
[Supplied codebase_kind/repo_path/repo_url/repo_revision constraints, or unresolved. Execution records the actual verified selection and commands here.]

## Progress Summary
[Derived task counts by TODO/RUNNING/DONE/BLOCKED, required evidence gaps, and last observation time or "not observed".]

## Overview & Milestones
| Run ID | Milestone | Block / Purpose | System / Variant | Dataset / Split | Seed | Depends On | Metrics / Success Criterion | Priority | Status | Latest Attempt | Notes |
|--------|-----------|-----------------|------------------|-----------------|------|------------|-----------------------------|----------|--------|----------------|-------|
| [unused ID] | [milestone] | [block/claim] | [variant] | [dataset/split] | [planned seed] | [IDs or none] | [actual criterion] | MUST or NICE | TODO or BLOCKED | none | [gate or blocker] |

## Files Created/Updated
### Models
### Trainers
### Losses
### Configs
### Scripts

## Experiment Reports
[Preserve existing real reports; new tasks have no fabricated attempts, metrics or completion records.]

## Next Action
[Recommend the next dependency-ready task and reason, or report blockers; this is not execution consent.]
```

Tracker rules:

- This file is the single task/progress/result source. Do not allocate another tracker,
  dated/suffixed output directory or per-execution documentation folder.
- New tasks start `TODO` or `BLOCKED`, never `RUNNING` or `DONE` from a plan alone.
  Use only `TODO`, `RUNNING`, `DONE`, `BLOCKED` for current task status. The runner's
  lifecycle contract defines evidence required for transitions; success against the
  scientific criterion is recorded separately from execution completion.
- Initialize the file-history/report sections empty for new work. Never copy example
  project filenames, metrics, completion percentages or claimed passes into real data.
- Replanning may add/decompose tasks and update current planning metadata, but must not
  reset or rewrite ongoing/completed attempts, file history, process identity or original
  plan/proposal bindings. Preserve previous task bindings before refreshing header hashes.
  Mark superseded task applicability explicitly; old results do not prove new claims.
- Summaries count only tasks applicable to the current plan, distinguish MUST from NICE,
  and show historical/superseded work separately. A DONE count is not a claim of novelty
  validation or of every success criterion being met.
- Read the existing tracker again before writing. Unexpected external changes require
  reconciliation; do not overwrite concurrent runner updates or create duplicate IDs.

#### Step 5.3: Optional score-history update

If `<IDEAS_DIR>/score-history.md` exists, append a concise section describing planning-readiness checks for:

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

Plan file: [actual absolute OUTPUT_DIR/EXPERIMENT_PLAN.md]
Tracker file: [actual absolute OUTPUT_DIR/EXPERIMENT_TRACKER.md]
Method proposal: [actual absolute proposal path, or absent]
Next invocation: /research-run-experiment run ids: [specific proposed IDs] mode: deploy plan: "[actual absolute plan path]" tracker: "[actual tracker path]" project: "[actual project root]"
```

Checkpoint:

Before offering execution, compile the planning-only task projection `approved_task_inventory` (Run ID, claim/block, milestone, dataset/task/split, system/variant, seed, config, metrics/direction, success criteria, priority, dependencies, milestone human decisions, budgets) and its canonical JSON SHA-256 `task_inventory_sha256`. Write `EXPERIMENT_PLAN_STATE.json` with `phase = outputs`, `status = awaiting_plan_approval`, `plan_approval.approved = false`.

Display the exact claims, first three runs, milestone decision gates, compute budget ceiling, and the plan/tracker locations. Ask the user explicitly: *"是否确认这份实验计划（包括核心 claims、决策门控、任务清单及预算上限）？确认后将写入 plan 锚点，之后才可授权具体运行。"*

Only an actual unambiguous user affirmative sets `plan_approval.approved = true`, `plan_approval.plan_sha256`, `plan_approval.task_inventory_sha256`, the real `confirmation_reference`, and `status = completed`. Silence, timeout, or autonomous mode does not approve the plan.

Once approved, write state with `phase = done`, `status = completed`.
## Confirmed next step: research-run-experiment

The next adjacent skill is [research-run-experiment](../research-run-experiment/SKILL.md). It reconciles
the plan with the tracker, implements and executes authorized tasks, and owns subsequent
progress/result updates. Offer it only after the actual plan, initialized tracker and
completed planning state exist and their bound inputs remain current.

Propose a concrete dependency-ready scope, normally the first ready MUST task in the
plan's run order. Resolve `authorized_run_ids` and `execution_mode` before offering;
never bind an unresolved "next pending run" or all future runs. Every proposed deployment
task must be `TODO` with satisfied dependencies, decision gates and prerequisites.
When nothing is ready, report blockers without an executable launch offer. A proposed
monitor/review of existing work instead binds those exact runs' original execution
evidence, uses that mode explicitly, and grants no launch permission.

If the codebase is unresolved but the design is otherwise ready, the offer must explain
that execution first reuses usable existing project code or asks for an explicit choice
between an existing repository and Structured Codebase. Entry assent does not select or
initialize a framework. Pass supplied constraints unchanged; null fields remain
unresolved. Bootstrap/clone/revision changes have their own execution-time authorization
and compatibility checks before any launch.

Keep this one active `NEXT_SKILL_HANDOFF` in conversation, replacing an obsolete offer:

```json
{
  "from_skill": "research-experiment-plannning",
  "to_skill": "research-run-experiment",
  "project_root": "<actual absolute project root>",
  "docs_root": "<actual absolute docs root>",
  "invocation": "/research-run-experiment run ids: R001 mode: deploy plan: \"<actual absolute plan path>\" tracker: \"<actual absolute tracker path>\" project: \"<actual absolute project root>\"",
  "plan_path": "<actual absolute EXPERIMENT_PLAN.md>",
  "tracker_path": "<actual absolute EXPERIMENT_TRACKER.md>",
  "plan_state_path": "<actual absolute EXPERIMENT_PLAN_STATE.json>",
  "plan_state_sha256": "<actual completed plan state byte SHA256>",
  "task_inventory_sha256": "<actual approved task inventory byte SHA256>",
  "proposal_path": null,
  "plan_sha256": "<actual plan byte SHA256>",
  "tracker_sha256": "<actual initialized tracker byte SHA256>",
  "proposal_sha256": null,
  "method_state_path": "<actual ideas or retrofit state path, or null>",
  "method_state_sha256": "<SHA-256 of actual method owner state bytes, or null>",
  "authorized_run_ids": ["R001"],
  "execution_mode": "deploy",
  "codebase_kind": null,
  "repo_path": null,
  "repo_url": null,
  "repo_revision": null,
  "artifacts": [
    {"role": "plan", "path": "<actual absolute plan path>", "sha256": "<exact file byte SHA256>"},
    {"role": "tracker", "path": "<actual absolute tracker path>", "sha256": "<exact file byte SHA256>"},
    {"role": "plan-state", "path": "<actual absolute state path>", "sha256": "<exact file byte SHA256>"}
  ],
  "status": "awaiting_confirmation"
}
```

R001 above is illustrative; use the actual proposed run IDs consistently in the command
and packet. Optional absent inputs remain JSON `null`/omitted. When supplied, bind the
actual proposal and its byte hash separately from the reviewed source. Expand `artifacts`
to every actual consumed source/config/script/report/literature/summary file. The full
command must reproduce the same bound inputs, modes and run scope.
Carry actual supplied codebase/repository/revision constraints in both the packet and
visible command (`codebase:`, `repo_path:`, `repo_url:`, `repo_revision:` as applicable).
Do not fabricate paths/revisions or assume an unselected framework when fields are null.
Display this command and ask `是否现在按这些 Run ID 和执行模式进入 research-run-experiment？回复“可以”或“继续”即可；代码基础未确定时，进入后先确认，不会自动初始化。`

Only direct unambiguous assent to this unique unresolved offer accepts it once; quoted,
unrelated or qualified assent (`可以，但先别执行`) is not consent. Refusal sets `declined`;
absent/ambiguous offers require clarification. Set `accepted`, revalidate all paths,
byte hashes, semantic provenance, selected rows, dependencies, gates and budget before
actions, then `running` while actually executing only that scope through the host loader.
Changed bindings set `stale` and require a refreshed specifically confirmed offer.
Mark the handoff `completed` only when that requested deploy/monitor/review scope truly
finishes under the runner's lifecycle contract, or `failed` on real failure. A completed
monitor visit can leave training `RUNNING`; it is not completed experimental evidence.
Consumed assent cannot repeat or expand execution, approve a new strategy or enter a
publication skill. Silence, timeout and autonomous mode supply no missing permission.

## Output Protocols

Follow the [shared human anchor gates](../research-shared-references/anchor-gates.md).

Fixed project output paths take precedence over generic output-versioning rules: update current files in place, do not allocate dated or suffixed directories, and never move/delete user-owned historical materials automatically.

## Changes in 3.0.0

Added explicit human `plan_approval` gate in `EXPERIMENT_PLAN_STATE.json` binding `approved_task_inventory` and canonical `task_inventory_sha256`. Planning stage approval is separated from execution authorization; execution offer requires prior plan approval. Validates upstream `method_state_path` approval before planning. Replaced legacy protocol references with `anchor-gates.md`.
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
/research-literature-review -> collect and normalize the literature foundation
/research-literature-summary -> per-paper analysis and research-landscape synthesis
/research-ideas -> literature-grounded proposal generation or user-idea optimization and independent review
/research-experiment-plannning -> detailed experiment roadmap after explicit confirmation
/research-run-experiment -> resolve/reuse codebase, execute authorized runs, and maintain the shared progress/results tracker
/auto-review-loop -> iterate after empirical results
```
