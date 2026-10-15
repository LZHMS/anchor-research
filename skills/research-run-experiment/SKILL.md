---
name: research-run-experiment
description: |
   Execute planned ML experiments and manage their shared task/progress/results tracker: reconcile dependencies, implement code, deploy authorized runs, monitor training, record evidence and recommend the next bounded action.
   Trigger: "run experiment", "跑实验", "launch training", "implement and run", "review log", "复查日志", "监控训练", "check training", "实验进度", "查看实验进度", "实验结果汇总"
version: 4.4.0
author: Zhihao Li
license: MIT
user-invocable: true
argument-hint: "project: <workspace> | mode: deploy/monitor/review | run ids: <IDs> | codebase: existing/research-structured-codebase | repo_path: <local-root> | repo_url: <optional-remote> | repo_revision: <optional-pin>"
metadata:
   category: research
   tags: [research, experiments, execution, progress, codebase, monitoring]
   related_skills: [research-experiment-plannning, research-structured-codebase, research-training-check, research-retrofit, research-paper-plan]
---

# Research Run Experiment: Execution, Progress & Results

Implement, track, and run ML experiment: **$ARGUMENTS**

## Overview

Own ongoing experiment execution, progress and results in the single `EXPERIMENT_TRACKER.md` initialized by [research-experiment-plannning](../research-experiment-plannning/SKILL.md). Reconcile the plan's concrete tasks before actions, execute only the authorized scope, update real observations and preserve original evidence. Do not maintain a second progress file or redesign the research plan merely to make a run pass.

Use the current host's available file, process, question and subagent capabilities.
Do not require a particular agent framework, CLI, model, tool name or reviewer profile.
Skill invocations below are chat requests, not terminal commands. If the host lacks
subagents, disclose that limit and keep uncertain judgments inconclusive rather than
pretending an independent review occurred. The main agent alone updates the tracker.

Follow the [shared human anchor gates](../research-shared-references/anchor-gates.md); the inline
rules below remain required when that reference is not installed. Stage entry, approval
of a concrete plan/method, and permission to launch/stop/retry are distinct. Neither a
direct invocation, reviewer recommendation nor an autonomous setting supplies a missing
approval or action permission.

**Operating Modes:**
- **Deploy Mode**: Reconciles ready tasks, implements code, records changes, launches only authorized runs and updates their progress/results.
- **Monitor Mode**: Checks already-launched runs through their recorded process identity and WandB/local logs, updates observations, and handles authorized health/recovery actions. Never launches or redeploys a run merely because monitoring was requested.
- **Review Mode**: Reports project/task progress or evaluates existing finished evidence and updates the tracker. Does not implement code, deploy, kill processes or retry. Without requested IDs, summarize the current applicable task inventory; unstarted tasks remain unstarted.

Monitoring exists only during an active invocation or a separately configured external
service. A skill is not a persistent scheduler: report observation time, stale/unknown
state and when monitoring stopped; never promise unattended continuous supervision.

Five principles dominate this skill:
1. **Traceable Code Implementation.** Every new model, trainer, or config file must be logged in `EXPERIMENT_TRACKER.md` before execution.
2. **Verify Before Launch.** Check the selected project's environment and device backend. Record actual source/configuration fingerprints; repository commits or remote pushes are never automatic.
3. **Compare Against Ground Truth.** Evaluation *must* compare predictions against dataset labels/targets, never another model's output alone.
4. **Evidence Before Intervention.** Use `research-training-check` for attempt-bound quality diagnoses. The main execution agent alone decides and performs control actions within the actual mode, explicit stop/retry permissions and resource budget; a diagnosis never grants permission.
5. **Bounded Strategy Loop.** If evaluation fails, propose a strategy adjustment. Autonomous recovery is limited to explicitly preauthorized changes within the accepted run scope and budget; silence/timeout cannot supply missing consent or authorize another skill.

## Constants

- **CODEBASE_KIND = null** — Unresolved, `existing`, or `research-structured-codebase`; resolved by this execution skill, not forced during experiment design.
- **REPO_PATH = null** — Actual local code root, or explicitly selected initialization/clone destination; resolve relative values against `PROJECT_ROOT`.
- **REPO_URL = null** — Optional explicitly supplied remote repository; never clone merely because a URL appeared in a paper or README.
- **REPO_REVISION = null** — Optional user/plan-pinned revision. Do not silently switch an existing checkout.
- **LAUNCH_AUTHORIZATION = explicit bounded scope** — Implementation never triggers deployment by default; verify approved planning content and the actual run/action/budget authorization immediately before every launch.
- **SANITY_FIRST = true** — Always run a small sanity-check script first to catch pipeline bugs early.
- **PROJECT_ROOT** — Explicit project argument, otherwise the bound handoff's accepted project root, otherwise the current working project directory; never the installed skill directory. Resolve relative arguments against this root.
- **DOCS_ROOT = `<PROJECT_ROOT>/docs`** — Existing explicit docs-root overrides remain supported and are resolved against `PROJECT_ROOT`.
- **PLAN_DIR = `<DOCS_ROOT>/research-experiment-plannning`**
- **IDEAS_DIR = `<DOCS_ROOT>/research-ideas`** — Default method directory; honor the plan's recorded actual proposal/ideas paths when they differ.

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| `Run ID` / `run ids` | Argument | Optional | Exact task scope. Deploy defaults to the next dependency-ready `TODO` task; monitor uses bound launched runs; review without IDs summarizes current applicable tasks. |
| `<PLAN_DIR>/EXPERIMENT_TRACKER.md` or explicit tracker path | Markdown | Yes | Primary target for code logging and run reports |
| `<PLAN_DIR>/EXPERIMENT_PLAN.md` or explicit plan path | Markdown | Yes | Source of truth for criteria, budget, and base strategy |
| `<PLAN_DIR>/EXPERIMENT_PLAN_STATE.json` or explicit `plan_state_path` | JSON | Deploy: Yes | Planner-owned `plan_approval` and immutable approved planning inventory; absence blocks new launches, not reporting original run evidence. |
| `method_state_path`, `method_state_sha256`, `anchor_path` | Paths / digest | Deploy: Yes | Actual ideas/retrofit owner and its current approved anchor/proposal, resolved from the approved plan's bindings. |
| `<IDEAS_DIR>/FINAL_PROPOSAL.md` or explicit proposal path | Markdown | Recommended | Detailed method implementation definitions |
| `mode` / `execution_mode` | Argument | Optional | `deploy`, `monitor`, or `review`, inferred from the actual request when omitted. A progress query is review, never implicit deployment. |
| `codebase` / `codebase_kind` | Argument | Optional | `existing` to reuse a project, or `research-structured-codebase` to use that framework. Unknown is a separate unresolved choice, not permission to initialize. |
| `repo_path` | Path | Optional | Local code root or explicitly chosen new destination; may differ from the project/docs root. |
| `repo_url`, `repo_revision` | Text | Optional | Explicit remote source and optional pinned revision; clone/check-out actions require the corresponding authorization. |

Input binding: Prefer explicit user paths, then a bound handoff's exact paths, then the exact canonical `<PLAN_DIR>/EXPERIMENT_PLAN.md` and tracker. Resolve proposal and literature paths from that plan's source fields or `EXPERIMENT_PLAN_STATE.json`; defaults are `<IDEAS_DIR>/FINAL_PROPOSAL.md`, `<DOCS_ROOT>/research-literature-review/research_foundation_review.json`, and `<DOCS_ROOT>/research-literature-summary/`. Verify actual paths and proposal byte SHA-256 against the recorded fingerprints, keeping clean-export and reviewed-source hashes separate. For literature context, verify summary manifest input path/canonical review digest and validated context/overview `papers_sha256` bindings. Missing explicit files or inconsistent/stale content bindings are errors; do not search dated folders or select by modification time. All plan/tracker reads and updates use these bound paths, including monitoring and strategy pivots.

When an explicit tracker is supplied without a plan, resolve its recorded `Plan` path first (relative paths against `PROJECT_ROOT`); only if no binding exists use `EXPERIMENT_PLAN.md` in the tracker's actual parent directory. When an explicit plan is supplied without a tracker, prefer its recorded tracker path, otherwise use `EXPERIMENT_TRACKER.md` in that plan's actual parent directory. Explicit overrides must agree with the bundle; a missing companion is an error. Experimental `Run ID` (`R001`, `R002`, etc.) selects a tracker row, never a documentation directory.

Update fixed current documents in place without moving/deleting historical material or allocating dated/suffixed output folders. Before deployment, compare current plan/proposal fingerprints with the target row's binding; changed method inputs require reconciliation, not automatic reuse of old approvals/results. If ideas state awaits candidate selection, do not deploy the prior final proposal as the new choice. Monitoring an already-launched run uses its recorded original evidence binding even if current docs changed; preserve that distinction in reports.

## Approved plan receiver gate

Before deploy implementation, any launch/retry, or a strategy/configuration change:

1. Resolve the exact planner-owned `plan_state_path` from the explicit binding, accepted
   packet or bound plan directory's `EXPERIMENT_PLAN_STATE.json`; verify its actual byte
   hash against `plan_state_sha256` at entry. Read the owner state, not a copied packet
   assertion. Require `plan_approval.approved: true`, a real `confirmation_reference`,
   actual current plan byte `plan_sha256`, and matching `task_inventory_sha256`.
   Missing, pending, declined or stale approval blocks deployment. Direct invocation
   cannot adopt an unapproved plan on the planner's behalf or waive this gate.
2. Verify the explicit `method_state_path`/`method_state_sha256` and delivered anchor/
   proposal bytes against that owner's `anchor_approval` and `proposal_approval`.
   Both approvals must be true with real confirmation references; proposal approval
   must bind the current proposal and anchor. A retrofit owner must have actually
   committed its approved export. Candidate selection or old review scores do not
   establish this. Method-state changes require affected plan revalidation, not
   choosing whichever ideas/retrofit state is newest.
3. Read the state's ordered `approved_task_inventory`. Reconstruct the current
   planning-only projection from the bound plan/tracker using that owner's schema,
   retaining these row keys: `run_id`, `claim_ids`, `block_id`, `milestone_id`, `task`,
   `dataset`, `split`, `system`, `variant`, `seed`, `configuration`,
   `blocking_prerequisites`, `metrics`, `success_criterion`, `failure_criterion`,
   `stop_criterion`, `priority`, `depends_on`, `milestone_human_decisions`,
   `resource_constraints`, `time_constraints`, `retry_constraints`,
   `total_budget_constraints`. Preserve row/array order and all action-scope fields
   and approved alternatives. Metrics define names/direction, not observed values.
   Null unresolved planning values remain unknown and block affected execution.
   Require the current projection to equal the approved snapshot and its digest:
   SHA-256 of UTF-8 JSON with `sort_keys=True`, `ensure_ascii=False`,
   `separators=(",", ":")`. Do not hash the whole live tracker as plan approval.
4. Exclude runtime status, attempts/reports, timestamps, process identities, actual
   metrics, file history and derived progress counts from this projection. The packet
   still binds actual tracker bytes at entry. Later authorized self-updates are
   reconciled through this invocation's history/checkpoint; normal progress does not
   stale the plan approval. External tracker changes require inspection/reconciliation,
   not blanket acceptance or automatic rejection of unchanged planning content.
5. Changed plan bytes, budget/configuration/criteria/dependencies or other planning
   fields stale the approval for affected NEW work. Preserve the accepted revision,
   identify the exact delta and pause new dependent actions pending approved replanning
   and applicable launch permission. Never recompute a digest to relabel old approval,
   edit the planner's approval record, or automatically kill a launched process.

Monitor/review can inspect and report already-launched attempts under their original
plan/proposal/configuration bindings even when the current plan is unapproved, stale
or unavailable. Record that limitation explicitly and retain accessible original
evidence; do not falsely label the current plan approved, relabel results, initialize
a codebase, or authorize a new launch. Missing explicit bound evidence remains an
error for that evidence, not a reason to invent it or suppress all observable progress.

## Codebase selection belongs to execution

Planning records supplied repository/framework constraints that affect architecture,
data, metrics or budget. This skill resolves the actual code root, implementation
framework and launch entry before deployment. `PROJECT_ROOT` continues to own the docs;
`REPO_PATH` owns code and process working directories. Reusing an external repository
does not move the shared plan/tracker into it or create another tracker.

For deployment, resolve explicit arguments > accepted planning/follow-up bindings >
recorded codebase selection in this project's tracker > the current project's actual
usable code. Inspect available project instructions, dependency/config files and real
entry points before deciding; a `.git` directory is not required. An explicitly missing
local source repository, conflicting revision or inaccessible source is an error, never
permission to fall back to another repository or initialize a different framework.
An explicitly authorized new clone/template destination may not exist yet; check its
parent and target for permissions/conflicting files instead of treating it as a missing
source. New destinations never justify overwriting an existing project.

| Choice | Required behavior |
|--------|-------------------|
| `existing` | Reuse the actual repository's framework, environment, configs, training/evaluation entry points and output conventions. Make the smallest experiment-specific changes. Do not force registry classes, YACS, Bash scripts or directory migration onto it. |
| `research-structured-codebase` | Load [research-structured-codebase](../research-structured-codebase/SKILL.md) through the host's skill mechanism. Reuse an already-bound instance; for an explicitly authorized fresh/docs-only destination, inspect its initializer's dry-run and apply the real bundled assets without overwriting user files. Follow that skill's actual registry/import/entrypoint conventions and protected `base/` rule. |

An existing project may itself use Structured Codebase; then use that helper for the
matching framework without reinitializing or replacing the repository. Never copy its
template over an unrelated codebase or bootstrap again on every run.

When loading the framework helper, pass the selected `REPO_PATH` as its code-project
root while retaining this skill's original `PROJECT_ROOT`/docs bindings. Template
initialization must not relocate or overwrite the research documents.

If no usable code or explicit choice exists, present two concrete choices: provide/reuse
an existing repository, or initialize Structured Codebase. Recommend the latter for a
new project but wait for an explicit selection before cloning, copying or implementing.
Assent to an unresolved planner-to-runner offer does not choose a codebase. Ask through
the host's available question mechanism or ordinary chat, without requiring a named API.

For an explicitly supplied remote, establish the exact source, authorized revision,
destination and network permission before cloning into a new/empty destination; never
overwrite, pull, reset or switch an existing checkout silently. Preserve user changes
and credentials; redact secrets in recorded URLs/commands. If the selected codebase
cannot meet the plan's scientific/resource constraints, report the mismatch and block
deployment pending separately authorized replanning, not an easier substitute experiment.

Record the resolved selection in a `## Codebase` section of the existing tracker:
`codebase_kind`, actual `repo_path`, optional sanitized `repo_url`/`repo_revision`,
working directory, discovered entry/config paths, launch/evaluation commands, device
backend and actual log/result locations. Record available commit identity and relevant
file-byte hashes; a commit alone does not describe uncommitted code. Preserve the same
facts with each attempt so historical runs retain their original codebase.

The packet's null codebase fields mean unresolved selection, not a missing scientific
input or bootstrap permission. An initially unbound selection may resolve under this
policy; echo and bind it before actions, recheck plan compatibility and record approval
for any initialization/clone. Once bound, changing repository/framework/revision is a
changed scope requiring fresh explicit authorization, never a silent rebind.

Monitor/review reuse recorded per-attempt roots, commands and evidence; never choose a
new framework, clone, initialize, migrate code or switch revisions. Legacy records with
unknown codebase metadata stay explicitly unknown while accessible evidence is reviewed;
do not block a progress query by insisting that the user first initialize a project.

### Invocation examples

```text
/research-run-experiment mode: deploy run ids: R001 project: "<actual project root>" codebase: existing repo_path: "<actual existing local code root>"
/research-run-experiment mode: deploy run ids: R001 project: "<actual project root>" codebase: research-structured-codebase repo_path: "<explicitly selected new code destination>"
/research-run-experiment mode: review project: "<actual project root>"
```

These are chat requests. Runtime commands use actual resolved paths, not placeholders.
An explicit framework choice permits its scoped preparation, not overwriting application
files, modifying protected base classes or launching experiments outside the accepted
run/mode/budget. A review query never initializes either codebase option.

## Confirmed Adjacent Entry

The adjacent upstream is [research-experiment-plannning](../research-experiment-plannning/SKILL.md). Conditional downstream routes remain [research-retrofit](../research-retrofit/SKILL.md) and [research-paper-plan](../research-paper-plan/SKILL.md), never automatic publication. Direct invocation grants stage entry only for its requested execution/monitor/review scope without another entry confirmation; deploy still requires actual approved plan/method state and explicit bounded action permission. Otherwise require the unique latest unresolved `NEXT_SKILL_HANDOFF` to `research-run-experiment`, with `status: awaiting_confirmation`, and direct unambiguous assent to that offer. `from_skill` is the planner, or this skill itself for a fresh bounded follow-up offered after the preceding authorized invocation genuinely finished; consumed assent cannot be reused.

Accept `project_root`, `docs_root`, `invocation`, `artifacts`, exact `plan_path`, `tracker_path`, `proposal_path`, `anchor_path`, `plan_state_path`, `method_state_path`, matching file `*_sha256` fields, `task_inventory_sha256`, `authorized_run_ids` and `execution_mode`. Deploy requires actual approved owner states; monitor/review preserve absent historical bindings as unknown. A planning/follow-up offer binds actual current tracker bytes and specific IDs/mode, not an unresolved "next pending run". Enumerate all consumed existing source/config/script, approval-state and provenance files in `artifacts`.
Also accept `codebase_kind`, `repo_path`, `repo_url`, and `repo_revision` as supplied
planning constraints or previously confirmed execution bindings. Preserve null values
as unresolved codebase selection; never infer Structured Codebase from an absent field.

Canonical incoming example (illustrative placeholders only; runtime replaces every path/digest and includes all actually consumed files, including relevant existing code/configs/scripts):

```json
{
    "from_skill": "research-experiment-plannning",
    "to_skill": "research-run-experiment",
    "project_root": "/absolute/project",
    "docs_root": "/absolute/project/docs",
    "invocation": "/research-run-experiment run ids: R001 — mode: deploy — plan: \"/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md\" — tracker: \"/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md\" — proposal: \"/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md\" — project: \"/absolute/project\" — docs root: \"/absolute/project/docs\"",
    "plan_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md",
    "plan_sha256": "<actual plan byte SHA-256>",
    "tracker_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md",
    "tracker_sha256": "<actual finalized tracker byte SHA-256>",
    "proposal_path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md",
    "proposal_sha256": "<actual delivered proposal byte SHA-256>",
    "anchor_path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md",
    "anchor_sha256": "<actual approved anchor byte SHA-256>",
    "method_state_path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json",
    "method_state_sha256": "<actual approved method state byte SHA-256>",
    "plan_state_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json",
    "plan_state_sha256": "<actual approved plan state byte SHA-256>",
    "task_inventory_sha256": "<actual approved canonical planning inventory SHA-256>",
    "authorized_run_ids": ["R001"],
    "execution_mode": "deploy",
    "codebase_kind": null,
    "repo_path": null,
    "repo_url": null,
    "repo_revision": null,
    "artifacts": [
      {"role": "experiment_plan", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "sha256": "<actual plan byte SHA-256>"},
      {"role": "experiment_tracker", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "sha256": "<actual finalized tracker byte SHA-256>"},
      {"role": "proposal", "path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md", "sha256": "<actual delivered proposal byte SHA-256>"},
      {"role": "anchor", "path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md", "sha256": "<actual approved anchor byte SHA-256>"},
      {"role": "method_approval_state", "path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json", "sha256": "<actual approved method state byte SHA-256>"},
      {"role": "plan_approval_state", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json", "sha256": "<actual approved plan state byte SHA-256>"}
    ],
    "status": "awaiting_confirmation"
}
```

Entry gates, before implementation, tracker writes or external actions:

1. Interpret the whole reply: quotations, refusal, “可以，但先别执行”, unrelated assent, ambiguity, silence or timeout do not approve an offer. Refusal sets `declined`; valid assent sets `accepted` once. No absent/stale/consumed offer can be revived by a bare “继续”.
2. Resolve project as explicit argument > accepted packet > working project, and use the exact-path/codebase rules. Echo `执行命令：` followed by the actual complete `/research-run-experiment ...` chat invocation with project/docs/plan/tracker/proposal paths, mode, run IDs and supplied codebase/repository constraints. It must match the accepted packet's scope; omit absent optional inputs. Unresolved codebase selection pauses at its own choice gate rather than silently initializing. For a direct invocation without run IDs, resolve scope under Phase 1 before actions.
3. Recompute exact byte SHA-256 for every entry artifact, check named file hashes agree, and verify existing semantic plan/proposal/method/literature provenance. For deploy apply the approved plan receiver gate, then validate IDs, readiness, criteria/budget, milestone decisions and action permission against the approved projection. Monitoring/review uses each launched run's original bindings; current documents do not relabel its evidence or prevent reporting accessible original evidence merely because current approval is missing/stale. Missing explicit/bound files are errors for those inputs, never permission to select latest files.
4. Changed entry binding, input inventory or scope sets `stale`: name changed paths/hashes/IDs/mode and require a refreshed specifically confirmed offer or explicit new invocation for the changed scope. Once running, reconcile authorized runtime self-updates through the checkpoint and planning-only comparison instead of freezing tracker bytes. Explicit changed user inputs supersede the offer, not inherit its consent. Revalidate immediately before writes/external actions, then set `running`.
5. Execute only the authorized scope. Existing implementation, deployment, health checks and in-scope strategy-recovery rules remain; timeout/autonomous mode cannot expand run scope, waive a required internal approval, or enter another skill. Preserve original evidence for each attempt; authorized edits refresh current fingerprints transparently without rewriting historical run/proposal bindings. Inputs changed by someone else require the stale-input gate again.
6. Mark the invocation `completed` only when its requested scope genuinely finishes, not on code creation or process launch. A monitoring/review visit can complete while a task remains `RUNNING`; report that distinction and never label it completed experimental evidence. Failures set `failed`; required internal approval pauses rather than falsely completing. Consumed packets cannot authorize another invocation. Resume only the same authorized scope: verify unchanged external inputs and any tracker/log/config changes produced by this invocation against its recorded checkpoint/history; never mistake its own recorded progress for new permission or silently accept someone else's edits.

## Shared tracker lifecycle and ownership

Use the planner's `## Progress Summary`, `## Overview & Milestones`,
`## Files Created/Updated`, `## Experiment Reports` and `## Next Action` sections in
the same tracker. This skill owns runtime updates; the planner owns initial task
decomposition and explicitly requested replanning. No separate execution database.

Before execution, reconcile rows against the actual plan: unique stable IDs, concrete
dataset/split/system/seed/configuration, claim/block, priority, metrics, success criterion,
budget, valid acyclic dependencies and milestone gates. Missing/conflicting details
block that task with an exact reason; do not invent a configuration or success target.
Preserve task applicability and all historical execution bindings on plan changes.

Current task statuses have one meaning throughout the table, summary and latest report:

| Status | Meaning and evidence |
|--------|----------------------|
| `TODO` | Planned, not launched. Pending dependencies do not authorize a launch. |
| `RUNNING` | An actual launch/process or remote-job identity was observed; record its command, host, start time and latest observation. |
| `DONE` | Execution ended and required evaluation/report artifacts were verified and bound to that attempt. Record separately whether the scientific success criterion was met. |
| `BLOCKED` | Cannot proceed or finish: missing prerequisite/approval, failed or cancelled attempt, unavailable required evaluation, or failed decision gate. Record reason and unblocking action. |

Transitions:

- `TODO -> RUNNING` only after the selected task is authorized, dependencies/gates and
  budget permit it, changes are recorded, and actual launch is observed.
- `TODO -> BLOCKED` for a verified missing prerequisite or gate.
- `RUNNING -> DONE` only with matching terminal execution and required evaluation/report
  evidence. A zero exit code alone is insufficient. A fully evaluated negative result
  may be `DONE` with "criterion not met"; do not relabel it as a successful claim.
- `RUNNING -> BLOCKED` for observed failure/cancellation or missing required final
  evaluation; preserve logs, error and last known process state.
- `BLOCKED -> TODO` only after the blocker is actually resolved and the exact retry or
  new scope is approved. `DONE` is not silently reset; changed scientific tasks get new
  unused IDs. An intentionally approved rerun keeps immutable previous attempts.
- `DONE -> TODO` is allowed only for an explicitly approved intentional rerun of the
  same task, preserving the completed attempt; a negative result alone is not approval.
- Completing an agent visit does not change task state by itself. An unverified process
  disappearance is not completion: record uncertainty and do not launch a duplicate.

For each real attempt, append an increasing attempt number under its stable Run ID,
with actual command/config/source paths and hashes, seed/data split, budget, process or
job identity, timestamps, log/result/artifact paths, original plan/proposal byte hashes
and separate reviewed-source reference where present. Preserve each original binding
and observations; never overwrite an earlier attempt's logs/results on retry. Record
latest observed metrics and criterion met/not-met/unknown separately from task status.
Before launch, record intent/configuration without pretending a process or metric exists.

Update the row's status/latest-attempt reference, derived progress summary and next
action from the same observations. Summarize TODO/RUNNING/DONE/BLOCKED counts, MUST/NICE,
known blockers and claim-evidence gaps for current applicable tasks; historical or
superseded tasks remain separately visible. Counts are not a second authoritative state.
Use "not observed"/"unknown" for unavailable facts, never fabricated percentages.

On first editing an older tracker, reconcile its current table once into these four
statuses using actual reports/process/evaluation evidence, preserve its raw historical
wording and log the migration. Do not keep a second active status dialect or infer
completion from an old optimistic label. Unresolved evidence is a recorded blocker.

Re-read the tracker before every update. Unexpected external changes require
reconciliation rather than overwriting. Preserve authorized self-produced changes in
the invocation's history/checkpoint so interruption can resume that same scope without
duplicating a live process. No background polling/automatic resumption is promised.

### Milestone, budget and drift decisions

At every approved milestone and before dependent work, present the actual claim
evidence, negative/unknown results, limitations, consumed/remaining per-run and total
budget, alternatives and exact proposed next action. A numeric pass or a `DONE` row
does not supply a required human stop/go decision. In the same tracker's matching
Run ID/attempt report, record `milestone_decisions` with `milestone_id`, supporting
`evidence_paths`/digests, `plan_sha256`, `task_inventory_sha256`, exact `proposed_action`,
`authorized_run_ids`, `budget_scope`, `status` (`pending`, `approved`, `declined`, `stale`)
and the real `confirmation_reference` (null while pending). A new result/scope that
changes the decision makes the old decision historical, not inherited approval.

Pause NEW dependent work while a required decision is pending/declined, the budget is
exhausted or unknown, or observed code/results conflict with the approved problem,
claim, protocol or strategy. Preserve the accepted anchor and original run evidence,
show the conflict and bounded options, and ask the user. Keep an actually live attempt
`RUNNING` with its real state: this pause never authorizes a kill, restart or budget
extension. Existing stop permission must independently cover the exact target/action.
A narrowly preauthorized deterministic step may proceed only when its exact criterion,
target, configuration, attempt limit, budget and action were explicitly approved for
this invocation and no human checkpoint was reserved; record that actual permission.
Generic autonomy, a helper return or milestone score never supplies it or enters a
new research stage.

## Workflow

### Phase 1: Context & Run Identification

1. Read the bound plan, tracker and supplied proposal, preserving absent historical optional inputs. For deploy verify actual approved plan/method states and the current planning-only inventory before implementation or external actions; for monitor/review preserve original evidence and report current approval limitations. Apply the shared reconciliation/lifecycle contract before tracker writes.
2. Resolve and echo the mode and exact scope. Deploy without IDs selects the next `TODO` task in the plan's MUST-first run order whose dependencies, milestone decision gates and prerequisites are satisfied. An unmet dependency or unknown gate is not satisfied merely because its row says `DONE`; inspect the required criterion/evidence. If none is eligible, report blockers without launching.
3. Respect explicitly bound IDs: invalid/not-ready/out-of-scope IDs fail with reasons, never silently substitute another task. Monitor identifies actual launched runs; when none exists, report that fact without deploying. Review without IDs summarizes applicable rows, keeping unknown/unstarted work honest.
4. For deploy, resolve and record the codebase under the selection contract before implementation or launch; reuse valid recorded selections without asking again. Bind the actual code/configuration/working directory and budget to the planned attempt. Monitor/review reuse original execution evidence and skip codebase initialization entirely. Do not declare `RUNNING` until an actual launch is observed.
5. **Dispatch by mode:** deploy continues through Phases 2–4; monitor/review skip code implementation, GPU allocation and deployment entirely and proceed to Phase 5. Review makes observations/report updates only; monitoring health interventions remain bounded to identified authorized processes and existing criteria.

### Phase 2: Implement Experiment Code

1. **Existing repository:** follow its actual architecture, dependency/environment setup, configuration and training/evaluation entry points. Extend its existing components with the smallest required change; do not convert it into another framework.
2. **Selected Structured Codebase:** load the framework skill and use its actual bundled assets and conventions: registry-driven components, trainer imports, YACS configs and matching project scripts. Its protected `base/` still requires explicit approval to modify. Do not initialize when the bound project already exists.
3. Inspect the real code before implementing either path. Missing dependencies or unsupported plan requirements are explicit blockers; dependency installation/global-environment changes require appropriate authorization.
4. **Mandatory Documentation Step**: Append actual changes to the bound tracker's `## Files Created/Updated`; preserve existing lines. Use the project's real component names/categories, not invented template files. Record actual code root, working directory, command/config paths and byte hashes plus the run's plan/proposal bindings before launch.

### Phase 3: Environment & Device Preflight

Use the selected codebase's documented interpreter/environment and requested backend.
Verify data/checkpoint/config paths, required packages and the accepted resource budget.
For CUDA, inspect available devices/memory with the host's appropriate tools; for MPS,
verify actual availability; CPU work must not require an NVIDIA GPU. Respect an existing
cluster scheduler or remote execution contract rather than inventing a local launch.

Select only authorized resources and record the actual device/distributed settings.
An availability observation is not an exclusive reservation. Report missing/conflicting
resources as blockers; never silently change backend, data, model or budget to make a
different experiment run. Monitor/review skip this deployment preflight.

### Phase 4: Record Provenance & Deploy

1. Resolve the exact authorized command from the selected project's actual entry point,
   configuration and working directory. An existing repository uses its own Python,
   shell, scheduler or other documented command; do not create/edit `scripts/setup.sh`
   unless that project actually uses it and the change is in scope. A selected Structured
   Codebase follows its helper's real script convention without mutating unrelated runs.
2. Record current source/configuration fingerprints and available revision identity.
   Do not stage unrelated work, commit or push by default; those operations require
   separate explicit authorization. A repository without Git can still run.
   Immediately before launch, repeat the approved plan/method and planning-projection
   checks; verify milestone decisions, remaining budget and exact launch permission.
   Code completion or resource availability alone never authorizes deployment.
3. Launch only the authorized command using the correct platform/interpreter/backend.
   Capture actual stdout/stderr, log/result paths and process/job identity. Record an
   actual launch before `RUNNING`; failure is a real `BLOCKED` error, not fake training.
   Preserve distinct previous attempt artifacts rather than overwriting them.

If `SANITY_FIRST=true`, any prerequisite sanity execution must already be a planned
authorized task or an explicitly included substep within the accepted task/budget.
Wait for its real completion; do not invent or launch an extra unapproved run.

### Phase 5: Diagnose, Decide, Record & Evaluate

During an ongoing run or a review of existing evidence, separate diagnosis from control:

1. **Bind actual evidence and request a diagnostic report.**
   - Start from the bound attempt's actual log/result paths, command, working directory, original plan/configuration/source fingerprints and process/job identity. Discover missing locations from the project's real configuration, not an assumed directory template. WandB is optional; never substitute an unrelated run.
   - For each requested training-quality check, load [research-training-check](../research-training-check/SKILL.md). Supply a unique request ID, exact Run ID/attempt, project/docs roots, original bindings, available sources, metric meaning/direction, actual observation window/freshness/baseline/early-stop policy and current caller mode. Missing policy remains absent, not invented.
   - Reserve an unused `<DOCS_ROOT>/research-training-check/diagnosis-NNNN.md` path for that request. Distinct concurrent checks get distinct reserved paths; one diagnostic writer per file. This is a flat immutable report history, not another tracker or RUN_ID directory.
   - Invoke the helper through the host's normal capability, or follow its instructions inline when a separate helper invocation is unavailable. Disclose inline versus isolated execution; do not fabricate independent review. The helper may read authorized evidence and write its diagnosis only. It cannot control training, alter the plan/tracker or grant new scope.
   - A simple progress inventory without a quality question need not generate a diagnosis for every row. Never launch an unstarted task merely to obtain diagnostic evidence.
2. **Accept the persisted diagnosis, not just a recommendation message.**
   - Receive `TRAINING_DIAGNOSIS_RESULT` from the already-requested helper. Read the exact returned report, recompute its actual byte SHA-256, and verify roots, reserved path, request/diagnosis IDs, Run ID/attempt, summary values and original input bindings. No newest-file substitution.
   - Reject mismatched, tampered or stale bindings before using the report for a control decision. Obtain a fresh diagnosis for a changed attempt/scope; never relabel an old report. A failed/missing report is reported as such, not as healthy. Independently observed failures may still be reported with their actual evidence.
   - The report freezes bounded metric rows/excerpts with source watermarks. Normal later appends to live logs/history do not stale that snapshot; a reset, identity/configuration change or unsupported source association does. Before acting, re-observe the current target and relevant newer evidence. Static files retain their original hashes; do not demand a growing log's full-file hash remain unchanged.
3. **The main execution agent makes the decision.**
   - Consider the report's evidence, uncertainty and advisory `continue`/`wait`/`inspect`/`request_stop` recommendation alongside current process/job identity/state, metric stage/direction, comparable baseline, actual plan criteria, remaining budget and permissions. Do not recreate a second universal threshold table here.
   - Review mode records observations and recommendations only: no stop, retry, deployment or configuration changes. A monitoring/deployment request is not blanket stop permission, and a `critical` diagnosis is not authorization.
   - Continue or wait only within the already-authorized run/budget. No automatic extension, follow-up scheduler or replacement launch. Unavailable/stale telemetry means unknown quality, not proof of success or a reason to kill.
   - Stop only when the exact live target, actual stop criterion and explicit in-scope stop permission are verified. Without that permission, report the concern and request a decision; do not terminate. Use the project's actual process-group/scheduler mechanism and only the authorized target, not a broad name-based kill. Record a stop request separately until termination is observed.
   - A low metric relative to a baseline alone is not technical failure. Apply scientific early stopping only under a defined approved criterion; new parameters/strategies/retries remain subject to Phase 6.
4. **Update the single shared tracker from actual observations.**
   - The main agent alone appends the report path/hash, request/diagnosis IDs, observation time/window, actual evidence, decision, rationale, permission basis and observed action outcome under the correct Run ID/attempt. Preserve original proposal/plan/configuration bindings and prior reports.
   - A still-active run remains `RUNNING`, including when awaiting permission to stop. A diagnostic warning/unknown result or completed diagnostic visit alone does not change its lifecycle. Record actual failed/killed/cancelled work or missing required final evaluation as `BLOCKED`; only verified terminal execution plus required evaluation/report evidence permits `DONE`.
   - Update the row's latest-attempt reference, derived `## Progress Summary` and `## Next Action` consistently. No fabricated percentages, duplicate progress database or unobserved control outcome.
5. **Evaluate scientific results separately.**
   - Compare actual final evidence against `EXPERIMENT_PLAN.md` criteria. A fully evaluated negative result may be `DONE` with "criterion not met"; a healthy diagnosis is not proof of scientific success.
   - If investigation or a strategy change is warranted, proceed to Phase 6's proposal/authorization gates. A returned report does not authorize another attempt or downstream skill.

### Phase 6: Strategy Adjustment Within Authorized Scope

If evidence indicates underperformance, failure or drift:
1. Identify the supported cause and uncertainties from real evidence, not a metric
   alone. Preserve the attempt outcome: technical failure is `BLOCKED`; a fully
   evaluated negative result stays `DONE` with "criterion not met".
2. Present the exact proposed configuration/strategy delta, affected claim/protocol,
   evidence, alternatives, additional resource/retry cost and affected dependencies.
   Pause new dependent work while its decision or budget is unresolved; do not kill
   an existing job merely because strategy discussion is pending.
3. If the exact alternative and deterministic trigger, attempt limit and budget were
   already explicitly approved in the unchanged plan/inventory and this invocation's
   action scope, select only that alternative and record the actual permission and
   chosen configuration in the tracker. Do not rewrite the plan to describe a runtime
   choice already contained in it. Generic autonomous mode and silence grant nothing.
4. Otherwise do not mutate `EXPERIMENT_PLAN.md` or the planner-owned approval state.
   Prepare the delta for explicitly authorized replanning, obtain content-bound
   approval of the changed plan/inventory, and revalidate affected method/evidence
   bindings before any new launch. Changing only hashes cannot refresh consent.
   A materially different scientific task needs a new unused Run ID.
5. Retry only with actual retry/launch authorization in deploy mode and remaining
   approved budget: resolved `BLOCKED -> TODO`, or explicitly approved intentional
   rerun `DONE -> TODO`. Append a new immutable attempt and original bindings.
   Monitor/review never becomes deploy, helper success cannot expand scope, and a
   new planning/retrofit stage needs its own specifically confirmed entry.

### Phase 7: Notification

Report completion, blockers or authorized strategy changes through the current host's normal user-facing response. Use an external notification channel only when explicitly configured and authorized; no particular CLI, messaging provider or agent framework is required.

Report the actual observation time and whether monitoring continues in this invocation
or has stopped. Do not describe notification or a completed review visit as persistent
supervision or completion of still-running training.

### Phase 8: Conditional Next-Stage Offer

First report the actual outcome, remaining runs/required evidence, and exact tracker/report/result locations. **Do not offer publication while any part of the authorized experiment scope is running, failed, killed, interrupted, awaiting an internal approval, or lacks final evaluation/report artifacts.** A completed monitoring request is not completed training. A single completed run also does not imply the entire paper's evidence requirements are satisfied.

First refresh `## Progress Summary` and `## Next Action`. If a completed invocation
leaves required work outstanding, recommend a specific dependency-ready next task or
an explicit monitor/review visit, not publication. For another invocation use the same
incoming packet schema with `from_skill: research-run-experiment`, `to_skill: research-run-experiment`,
fresh exact tracker/artifact hashes, IDs and mode; show its full actual command and wait
for new specific assent. Never reuse the consumed packet or choose another task after
confirmation. If nothing is ready, report concrete blockers. This recommendation is
not an automatic scheduler or permission to run all remaining tasks.

Every follow-up carries the established `codebase_kind`, actual `repo_path` and supplied
remote/revision constraints plus the relevant source/configuration bindings. Never reset
them to null to evade a changed-codebase gate. Downstream `code_paths` and original run
bindings refer to the actual selected code root, not an assumed `PROJECT_ROOT/models`.

Only after the explicitly authorized experiment scope has genuinely finished, choose at most one justified adjacent route:

- Recommend [research-retrofit](../research-retrofit/SKILL.md) when actual implemented core code and an actual up-to-date research report exist, existing proposal/anchor files exist, and those method documents need alignment with actual implementation/results. Bind `report_path` (singular), `code_paths`, actual `repo_path`, `result_paths` where available, `proposal_path`, `anchor_path`, and optional `plan_path`, `tracker_path`, `evidence_paths`. The tracker is a report only if its actual contents satisfy that research-report role; do not fabricate a report or redirect to an empty future path. Preserve actual completed data through retrofit for subsequent paper preparation.
- Otherwise recommend [research-paper-plan](../research-paper-plan/SKILL.md) when the current proposal matches actual implementation and completed result data covers the intended claims. Bind `proposal_path`, `report_paths`, actual selected `repo_path`, inspectable implementation/evaluation `code_paths`, actual completed `result_paths`, optional `plan_path`, `tracker_path`, `evidence_paths`, and the real literature/provenance bindings. Reports or training diagnoses alone are not measurements. Paper planning owns result auditing, statistics, publication tables/figures and narrative preparation under `<DOCS_ROOT>/research-paper-plan`; final plots need not already exist. Missing required experiments, inaccessible result data or unresolved code/method alignment block the offer.
- If neither route meets its prerequisites, report the concrete gaps and stop without a publication packet. If route choice is ambiguous, recommend one with the reason as the only active offer, or ask the user to select a route before creating an offer. Never leave two live offers for a bare assent to choose between.

Preserve actual output paths; no new run directories or synthesized metrics. Retain `completed_run_ids` and `original_run_bindings` with each run's original plan/proposal paths and byte hashes, its actual report path, and the assessed applicability to the current method. Do not substitute current proposal hashes for historical ones or transfer reviewed-source scores to changed exports. Enumerate all consumed source/config files, reports/results/logs/figures, method documents, plan/tracker/state and literature sidecars in `artifacts`; directory inputs require individual file entries and exact byte hashes. Keep source permissions and absent optional inputs unchanged. A publication receiver must revalidate these bytes and existing semantic provenance before acting.

Both routes carry the actual current `method_state_path`/`method_state_sha256`,
`anchor_path`/`anchor_sha256`, `proposal_sha256`, plus `plan_state_path`/
`plan_state_sha256`, current `plan_sha256` and `task_inventory_sha256` where applicable.
Verify the owner approvals against the actual delivered method and plan; enumerate
those owner states as artifacts, without hashing a state into its own approved content.
If current plan approval is stale, name that limitation and retain the approved
revision/attempt evidence; never claim changed planning content was approved.
Retrofit may inspect such a conflict, but paper preparation cannot silently inherit
stale problem/method approval. Stage-entry consent never grants new execution scope.

Canonical alignment-needed offer (illustrative placeholders; runtime uses actual paths, actual hashes, and the complete consumed inventory):

```json
{
    "from_skill": "research-run-experiment",
    "to_skill": "research-retrofit",
    "project_root": "/absolute/project",
    "docs_root": "/absolute/project/docs",
    "invocation": "/research-retrofit report: \"/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md\" — code: \"/absolute/project/models/method.py\" — repo_path: \"/absolute/project\" — result_paths: [\"/absolute/project/output/dataset/config/metrics.jsonl\"] — proposal: \"/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md\" — anchor: \"/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md\" — project: \"/absolute/project\" — docs root: \"/absolute/project/docs\"",
    "proposal_path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md",
    "anchor_path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md",
    "anchor_sha256": "<actual current anchor byte SHA-256>",
    "proposal_sha256": "<actual current proposal byte SHA-256>",
    "method_state_path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json",
    "method_state_sha256": "<actual current method owner state byte SHA-256>",
    "report_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md",
    "code_paths": ["/absolute/project/models/method.py"],
    "repo_path": "/absolute/project",
    "result_paths": ["/absolute/project/output/dataset/config/metrics.jsonl"],
    "plan_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md",
    "tracker_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md",
    "plan_sha256": "<actual current plan byte SHA-256>",
    "plan_state_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json",
    "plan_state_sha256": "<actual plan approval state byte SHA-256>",
    "task_inventory_sha256": "<actual approved planning inventory SHA-256>",
    "evidence_paths": ["/absolute/project/output/dataset/config/output.log"],
    "completed_run_ids": ["R001"],
    "original_run_bindings": [
      {"run_id": "R001", "plan_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "plan_sha256": "<original executed plan byte SHA-256>", "proposal_path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md", "proposal_sha256": "<original executed proposal byte SHA-256>", "report_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "applicability": "Implementation differs from the current proposal; alignment required before publication claims"}
    ],
    "artifacts": [
      {"role": "proposal", "path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md", "sha256": "<actual current proposal byte SHA-256>"},
      {"role": "anchor", "path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md", "sha256": "<actual anchor byte SHA-256>"},
      {"role": "method_approval_state", "path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json", "sha256": "<actual current method owner state byte SHA-256>"},
      {"role": "plan_approval_state", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json", "sha256": "<actual plan approval state byte SHA-256>"},
      {"role": "research_report_and_tracker", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "sha256": "<actual completed report byte SHA-256>"},
      {"role": "core_code", "path": "/absolute/project/models/method.py", "sha256": "<actual code byte SHA-256>"},
      {"role": "experiment_plan", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "sha256": "<actual current plan byte SHA-256>"},
      {"role": "run_evidence", "path": "/absolute/project/output/dataset/config/output.log", "sha256": "<actual final log byte SHA-256>"},
      {"role": "completed_result_data", "path": "/absolute/project/output/dataset/config/metrics.jsonl", "sha256": "<actual completed result byte SHA-256>"}
    ],
    "status": "awaiting_confirmation"
}
```

Canonical aligned, sufficient-evidence offer (an alternative, never a simultaneous second active offer):

```json
{
    "from_skill": "research-run-experiment",
    "to_skill": "research-paper-plan",
    "project_root": "/absolute/project",
    "docs_root": "/absolute/project/docs",
    "invocation": "/research-paper-plan project=\"/absolute/project\" docs_root=\"/absolute/project/docs\" proposal_path=\"/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md\" report_paths=[\"/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md\"] repo_path=\"/absolute/code-repo\" code_paths=[\"/absolute/code-repo/src/method.py\",\"/absolute/code-repo/src/evaluate.py\"] result_paths=[\"/absolute/code-repo/output/dataset/config/metrics.jsonl\"]",
    "proposal_path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md",
    "proposal_sha256": "<actual aligned proposal byte SHA-256>",
    "anchor_path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md",
    "anchor_sha256": "<actual approved anchor byte SHA-256>",
    "method_state_path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json",
    "method_state_sha256": "<actual approved method owner state byte SHA-256>",
    "report_paths": ["/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md"],
    "repo_path": "/absolute/code-repo",
    "code_paths": ["/absolute/code-repo/src/method.py", "/absolute/code-repo/src/evaluate.py"],
    "result_paths": ["/absolute/code-repo/output/dataset/config/metrics.jsonl"],
    "plan_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md",
    "tracker_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md",
    "plan_sha256": "<actual current plan byte SHA-256>",
    "plan_state_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json",
    "plan_state_sha256": "<actual approved plan state byte SHA-256>",
    "task_inventory_sha256": "<actual approved planning inventory SHA-256>",
    "evidence_paths": ["/absolute/code-repo/output/dataset/config/output.log"],
    "completed_run_ids": ["R001"],
    "original_run_bindings": [
      {"run_id": "R001", "plan_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "plan_sha256": "<original executed plan byte SHA-256>", "proposal_path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md", "proposal_sha256": "<original executed proposal byte SHA-256>", "report_path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "applicability": "Verified aligned method; required claim evidence actually complete"}
    ],
    "artifacts": [
      {"role": "proposal", "path": "/absolute/project/docs/research-ideas/FINAL_PROPOSAL.md", "sha256": "<actual aligned proposal byte SHA-256>"},
      {"role": "anchor", "path": "/absolute/project/docs/research-ideas/PROBLEM_ANCHOR.md", "sha256": "<actual approved anchor byte SHA-256>"},
      {"role": "method_approval_state", "path": "/absolute/project/docs/research-ideas/REVIEW_STATE.json", "sha256": "<actual approved method owner state byte SHA-256>"},
      {"role": "plan_approval_state", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json", "sha256": "<actual approved plan state byte SHA-256>"},
      {"role": "experiment_report_and_tracker", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "sha256": "<actual completed report byte SHA-256>"},
      {"role": "experiment_plan", "path": "/absolute/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "sha256": "<actual current plan byte SHA-256>"},
      {"role": "method_code", "path": "/absolute/code-repo/src/method.py", "sha256": "<actual aligned implementation byte SHA-256>"},
      {"role": "evaluation_code", "path": "/absolute/code-repo/src/evaluate.py", "sha256": "<actual executed metric implementation byte SHA-256>"},
      {"role": "completed_result_data", "path": "/absolute/code-repo/output/dataset/config/metrics.jsonl", "sha256": "<actual completed result file byte SHA-256>"},
      {"role": "run_evidence", "path": "/absolute/code-repo/output/dataset/config/output.log", "sha256": "<actual final log byte SHA-256>"}
    ],
    "status": "awaiting_confirmation"
}
```

At runtime print the recommended next action/route and reason, then `推荐命令：` with its actual full resolved chat invocation. Ask whether to execute that specific scope with those bound inputs and **stop**. Only direct unambiguous assent to the unique latest awaiting offer authorizes that receiver once; refusal sets `declined`, changes set `stale` and require a refreshed confirmation. Silence, timeout, a previously accepted planner/runner packet, automatic notification and autonomous strategy recovery never authorize another invocation or downstream entry. The receiver's outline/reviewer/internal approvals remain separate; no filing/submission or extra data-source permissions are granted.

## Key Rules

- **ALWAYS WRITE FILES TO TRACKER BEFORE RUNNING.** If the agent or PC crashes during execution, the user must still have a historical log of what files were added for the experiment.
- **NEVER OVERWRITE FILE HISTORY.** When updating `## Files Created/Updated`, specifically append new items underneath the existing ones.
- **GROUND TRUTH ONLY.** Evaluation must compare predictions directly against the dataset's actual labels/targets.
- **NO AUTONOMOUS DEFAULT.** Implementation, diagnosis and numeric milestone success do not launch, stop, retry, extend budget, change the approved plan or cross a stage gate. Record exact permissions and pause new dependent actions when decisions or content-bound approvals are missing.


## Changes in 4.4.0

Deployment now requires the actual planner/method approval states and unchanged
canonical planning-only inventory, without invalidating approval on normal runtime
tracker updates. Milestone/budget/strategy drift pauses new dependent work for a real
decision, never automatically kills training. Removed automatic deployment/resume
defaults; downstream packets preserve approval-owner and approved-plan evidence.
## Changes in 4.3.0

Paper preparation receives the actual selected code root, inspectable implementation/evaluation sources and completed machine-readable result files, directly or through retrofit. The paper-planning stage audits results and produces statistics/tables/figures before narrative approval; a report or training diagnosis alone is not empirical evidence, and final publication plots are not an entry prerequisite.

## Changes in 4.2.0

Training-quality checks now use `research-training-check` and its immutable reports under project `docs/research-training-check/`. The execution agent verifies the returned report and alone decides, performs authorized actions and updates the shared tracker. Removed duplicate universal kill thresholds; critical recommendations never supply stop permission, normal live-log appends preserve captured snapshots, and review remains non-controlling.
