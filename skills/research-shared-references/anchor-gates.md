# Anchor Research: Human Anchor Gates

This is the shared decision contract for the research skills. Each skill remains responsible for its own technical prerequisites, local state and action scope. An installed skill must retain its inline gates even if this reference is unavailable. These instructions are not a permission sandbox, scheduler or proof that scientific judgment is correct.

## 1. Authority and three distinct permissions

User-confirmed problem, non-goals and constraints govern the research direction. Implementation and measurements establish what was actually done; they do not authorize changing that direction. A reviewer advises and checks evidence; its score cannot approve user intent or grant resources.

Distinguish:

1. **Stage entry:** an explicit invocation or assent to one exact pending stage offer permits preparing that stage, not approving artifacts that do not yet exist.
2. **Anchor approval:** the user accepts a presented, concrete, content-bound problem, proposal, plan, narrative or visual decision. Saving a draft, candidate selection, a high review score or a ready-looking filename is not approval.
3. **Consequential action:** deployment, process termination, retries, strategy/budget changes, new sources, permanent knowledge-base filing, publication and printing need the corresponding exact scope/permission. Approval of a plan alone does not launch it.

A candidate choice selects one route. It does not approve the agent's later interpretation of the problem or its final mechanism. Poster auto-proceed, if explicitly requested, applies only to that poster invocation's internal presentation checkpoints; it cannot waive stage-entry, upstream anchors, evidence checks, or publication permissions.

## 2. The gate procedure

Before asking, present the actual decision: problem/non-goals, alternatives or result-backed changes, evidence and limitations, resource implications, exact affected files and actual content digests. State precisely what a yes permits. Do useful authorized inspection/drafting before asking; do not request information available in the project.

Persist pending state with approval false and actual artifact bindings. Preserve the previously accepted anchor/export while preparing a replacement draft. Drafts are not authoritative current anchors. At a final gate, show the current candidate—not an earlier version—and wait. A request to change it means revise and present again, not approval.

Record approval only after an actual unambiguous reply to that exact decision. Store its real message/turn reference or exact confirmation text with context; never invent an identifier, timestamp or user response. Re-read bound content before committing. Explicit user wording that already approves the exact presented artifact/scope can be recorded without asking the same question again; a generic request to run a skill cannot approve its future output.

Silence, timeout, autonomous mode, a checkpoint's age, a reviewer score, a previous stage's approval, and bare assent without one identifiable pending decision supply no permission. A bare yes cannot choose among multiple candidates. Refusal pauses/declines; ambiguity is clarified.

After content/scope changes, approvals become stale. Preserve the old approved revision and its evidence, name what changed, then obtain approval for the new revision. Revalidate affected downstream artifacts rather than relabeling old results. Do not automatically restart or choose latest-by-mtime. A completed negative result is evidence; a failed/missing measurement is not zero or success.

## 3. Owner states and approval records

Use existing owner state/report files; no global approval database or duplicate tracker. Approval records below require `approved`, the named actual digests and `confirmation_reference` (with the real confirmation text/context when a stable message ID is unavailable). Pending approval is false; unknown references/digests stay null. Owner state also binds actual project, sources, constraints and workflow. Do not put an owner's own file hash in itself.

| Owner | Local state | Required content-bound decision |
|---|---|---|
| literature review | `docs/research-literature-review/CORPUS_STATE.json` | `corpus_approval`: actual `corpus_sha256` file bytes and canonical review `input_sha256`; approve corpus scope, enabled sources and evidence limits, not scientific truth |
| literature summary | `docs/research-literature-summary/SUMMARY_STATE.json` | `summary_approval`: actual `summary_snapshot_sha256`; accept the completed evidence landscape and its limits |
| research ideas | `docs/research-ideas/REVIEW_STATE.json` | `anchor_approval`: `anchor_sha256`; then `proposal_approval`: `proposal_sha256` and `anchor_sha256`, separate from candidate selection and technical review |
| experiment planning | `docs/research-experiment-plannning/EXPERIMENT_PLAN_STATE.json` | `plan_approval`: `plan_sha256` and `task_inventory_sha256`; accept claims, tasks, budgets, criteria and milestone decisions |
| code/proposal reconciliation | `docs/research-retrofit/RETROFIT_STATE.json` | `anchor_approval` and `proposal_approval` for the unchanged/adopted or explicitly re-anchored problem and exact proposed export; accept a displayed delta before replacing current method files |
| paper planning | `docs/research-paper-plan/PAPER_PLAN_STATE.json` | existing `outline_approval`: actual `bundle_sha256`, independent evidence review and final user-confirmed narrative |
| paper writing | `docs/research-paper-writing/WRITING_STATE.json` | `manuscript_approval`: finalized `manifest_sha256`; accept the actual reviewed manuscript and its limitations |
| poster | `docs/research-paper-poster/POSTER_STATE.json` | actual content/layout approvals or an explicitly scoped poster-internal waiver, with exact reviewed content/layout bindings |

For summary snapshots reuse the established ordered `summary_artifacts` byte inventory and canonical `summary_snapshot_sha256` consumed by research-ideas: manifest; each task's context, analysis Markdown and result sidecar in task order; overview context, Markdown and sidecar; index and aggregate report. Exclude mutable SUMMARY_STATE.json. Preserve separate review/context/overview semantic digest validation. Hashing the approval state into its approved snapshot would create a cycle.

Idea/retrofit downstream packets carry `method_state_path` and `method_state_sha256`; readers verify the actual owner's anchor/proposal approvals against the delivered proposal and anchor. The owner is explicit, not whichever state is newest. Literature packets likewise carry `corpus_state_path`/`corpus_state_sha256` or `summary_state_path`/`summary_state_sha256` as applicable. Enumerate these states in handoff artifacts, but never include a state in the snapshot it approves.

For direct entry into an existing project, genuine equivalent explicit user acceptance may be recorded as `input_anchor_approval` in the receiving stage's own state/report, binding the actual supplied files/constraints and real confirmation reference. Do not fabricate an upstream execution/review history, write approval into someone else's owner state, or treat a mere filename/invocation as adoption. Equivalent acceptance cannot waive missing measurements, code applicability, required independent review, or current build correspondence.

## 4. An approved task inventory is not a frozen live tracker

The planner records `approved_task_inventory` in its existing state as a canonical planning snapshot, not another mutable tracker. Each row includes Run ID, claim/block, milestone, dataset/task/split, system/variant, seed, exact configuration or unresolved blocking prerequisite, metrics/direction, success/failure/stop criteria, priority, dependencies, milestone human decision requirements, and per-run/total resource/time/retry constraints. Include all actual planning fields that can change action scope. Unknown values remain unknown and block affected execution.

`task_inventory_sha256` is SHA-256 of UTF-8 canonical JSON (`sort_keys=True`, `ensure_ascii=False`, `separators=(",", ":")`) of that ordered planning snapshot. The runner compares current planning fields to the approved snapshot before deploy or a strategy change. Runtime status, attempt reports, timestamps, process identities, actual metrics, file-history entries and derived progress counts are excluded: normal authorized progress must not invalidate the plan merely because EXPERIMENT_TRACKER.md changed bytes.

The handoff still binds actual tracker bytes at entry; subsequent authorized self-updates use its execution checkpoint/history. External changes need reconciliation. A changed planning field or plan bytes requires refreshed approval, not recomputing hashes to pretend old consent covers it. Runtime codebase selection has its own explicit choice and compatibility gate; it does not let unresolved planned data/budget turn into invented defaults.

Milestone human decisions are recorded by the execution owner under the matching task/attempt and evidence. A passed numeric check is not human stop/go. A narrowly preauthorized deterministic action may occur only if the user actually approved that exact criterion, target, budget and action within the same invocation; generic autonomous mode never supplies it. Crossing a research-stage gate always needs its own specific authorization.

## 5. Stage adjacency and handoff

Main path:

`research-literature-review → research-literature-summary → research-ideas → research-experiment-plannning → research-run-experiment → research-paper-plan → research-paper-writing → research-paper-poster`.

Conditional reconciliation: execution → research-retrofit → experiment planning (changed claims/missing experiments), or → paper planning (aligned code and sufficient completed evidence). Reconciliation never makes code the authority over the user's problem.

`research-structured-codebase` and `research-training-check` are bounded helpers of execution, not extra mandatory research stages. Diagnostics return immutable reports and advice; only the execution owner controls authorized jobs and updates the one tracker. Existing repositories are valid code bases. Optional daily discovery and PKBase operations do not approve a proposal, enter the main path automatically, or gain write permission merely because a base exists.

At a real stage boundary offer at most one bare-object conversation `NEXT_SKILL_HANDOFF`: `from_skill`, `to_skill`, actual `project_root`, `docs_root`, fully resolved chat `invocation`, exact stage-specific inputs, `artifacts: [{role,path,sha256}]`, `status: awaiting_confirmation`. Include all actually consumed control/source/data/approval files and preserve existing semantic provenance. Print the command and the decision, then wait. Examples/placeholders are not live offers.

Unique unambiguous assent accepts once; refusal declines; changed paths/bytes/scope stale the offer. Revalidate before actions. `accepted → running → completed` describes actual authorized stage completion, not a fabricated success; failures are `failed`, internal approvals remain pending. Never reuse consumed assent, cascade a stage's output approval into another stage's entry, or turn a helper return into new execution permission. Paper/poster completion does not authorize submission, upload or printing.

## 6. Drift and re-anchoring

On a problem/claim/protocol/budget conflict: identify original anchor versus observed code/results, preserve evidence and the old anchor, pause new dependent actions, present options and ask the researcher. Pausing new actions is not permission to kill an already-running job. Preserve its real state; stop it only under actual stop authorization. Data failures and loss of observability are different facts.

Retrofit drafts and reviews a proposed reconciliation before user approval; it never silently edits the problem to rationalize drift. Approved exports retain old immutable snapshots and original attempt hashes. Invalidate affected method, plan, narrative, build or visual approvals, then resume from the appropriate explicitly authorized stage. Reusing paths or a favorable score cannot restore stale authority.
