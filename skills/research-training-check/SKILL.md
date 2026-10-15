---
name: research-training-check
description: |
  Diagnose the quality of a specified training run from bounded real metrics and logs, save an evidence-backed report under project docs, and return recommendations to research-run-experiment. Never control training or update its tracker.
  Trigger: "diagnose training", "训练诊断", "is training healthy", "check wandb", "检查训练质量"
version: 2.0.0
author: Zhihao Li
license: MIT
user-invocable: true
argument-hint: "project: <workspace> | run id: <ID> | attempt: <number> | sources: <actual paths or WandB run>"
metadata:
  category: research
  tags: [research, training, diagnostics, monitoring, evidence]
  related_skills: [research-run-experiment, research-experiment-plannning]
---

# Research Training Check: Evidence & Advisory Diagnosis

Diagnose the requested training attempt: **$ARGUMENTS**

## Responsibility and boundaries

This is a diagnostic helper of [research-run-experiment](../research-run-experiment/SKILL.md), not another execution manager or pipeline stage. Read authorized evidence, write a diagnosis, and report upward. The execution skill alone decides and performs authorized continuation, termination, strategy changes or retries, and alone updates the shared tracker.

Use the host's available file, read-only observation and subagent capabilities. No particular agent framework, CLI, model or tool name is required. Do not install dependencies, log in to services, reveal credentials, change code/configuration, allocate devices, launch/restart/stop training, send process signals, modify checkpoints or write the experiment plan/tracker. A critical diagnosis or a reviewer's recommendation grants no control permission.

Default to one bounded check. A completed diagnosis is not completed training. Do not start a polling loop, schedule another invocation or promise unattended monitoring. The parent may arrange another check only within its actual authorized duration/budget or an explicitly configured external service.

## Project paths and report ownership

- `PROJECT_ROOT`: explicit project > calling execution skill's bound project > current working project; never the installed skill directory or an unrelated code repository.
- `DOCS_ROOT`: inherit the parent's accepted explicit docs-root override, otherwise `<PROJECT_ROOT>/docs`.
- `DIAGNOSIS_DIR`: `<DOCS_ROOT>/research-training-check`.
- Write one new immutable Markdown report per check: `diagnosis-0001.md`, `diagnosis-0002.md`, etc., directly in this directory. No date/RUN_ID subdirectories, separate progress database or duplicate latest-report copy.
- The parent reserves distinct unused report paths before dispatching concurrent checks. For a standalone check, choose an unused number. Each report has one writer; serialize allocation/writes when exclusive creation is unavailable. Recheck before creation, never overwrite an existing report, and report a collision rather than replacing another diagnosis. Corrections are new reports that reference the superseded report.
- Resolve the actual output location within `DIAGNOSIS_DIR`; refuse traversal, a symlink redirect or a supplied report path outside it. Never overwrite an input. The supplied output path is a constraint, not permission to choose another directory.

## Inputs and caller contract

| Input | Requirement |
|---|---|
| Project/docs roots | Resolve as above; preserve the parent's accepted roots. |
| Request identity | Parent supplies a unique request ID, exact Run ID, attempt number and reserved report path. These are distinct from a WandB run ID. |
| Attempt bindings | Parent supplies actual command, code root, configuration/source/plan fingerprints, process/job identity and source locations from the original attempt, where available. Do not replace them with the latest project documents. |
| Metric specification | Actual metric keys, meaning, optimization direction, stage/step/epoch, validation cadence and comparable baseline, where available. |
| Observation policy | Requested step/time window, freshness limit, minimum samples, warm-up, divergence/patience/early-stop criteria, where explicitly defined in the plan or request. Missing policy stays missing. |
| Evidence sources | One or more explicitly supplied or attempt-recorded WandB runs, local/remote logs, JSON/CSV metrics, TensorBoard data or evaluation artifacts. Every source is optional; use only accessible authorized sources. |

Do not require WandB, Structured Codebase or a particular logging layout. Never search other runs for a replacement. If all sources are unavailable, produce an `unknown` diagnosis with actual errors rather than assuming success or failure.

A standalone user may supply just a uniquely identified source without a formal plan/tracker. Diagnose what is observable, record absent experimental Run ID/attempt/bindings as null, and explain the limits. Do not invent a tracker, attempt identity, stop policy or baseline to fill missing fields. An unbound standalone report is not sufficient for parent control actions.

Before a parent-called check, echo the equivalent complete chat invocation, not a terminal command:

```text
/research-training-check project: "<PROJECT_ROOT>" — docs root: "<DOCS_ROOT>" — run id: <ID> — attempt: <number> — request id: <request ID> — report: "<reserved absolute report path>" — sources: <actual bound sources>
```

Use actual resolved values; omit unavailable optional standalone fields. This internal helper call consumes no new downstream-stage consent and grants no new execution scope.

## Workflow

### 1. Bind the check

Verify the request identity and source-to-attempt association before diagnosis. Reused output paths, mismatched WandB runs, a different seed/configuration or a restarted step counter require explicit disambiguation. Do not combine different attempts into one curve. Training may be checked immediately after an observed launch; decreasing initial loss is not an entry requirement.

### 2. Capture a bounded evidence window

Read the actual metric schema and a relevant bounded window. For WandB, use only existing authentication and the exact bound run; request the needed keys and step/time range. Do not treat a default sampled history as an exhaustive chronology or silently skip invalid records. For files, use actual line/byte/step ranges rather than a fixed assumed log path or arbitrary last-lines sample.

Record source identities, capture time in actual UTC, timestamp semantics/timezone where known, metric keys, step/epoch boundaries, sample counts, latest metric time and observed age. Preserve missing/non-finite/conflicting values explicitly. Keep duplicate/conflicting step records visible until explained. Distinguish observed facts from inference. Missing gradients, GPU telemetry or evaluation metrics are unavailable, not zero or healthy. Do not claim to diagnose idle GPUs without actual relevant telemetry.

Embed the consumed numeric rows or bounded log excerpts in the report with source locators and a watermark (last observed step/time and file range, where applicable). Encode NaN/Inf as strings in JSON, not invalid JSON numbers. Redact credentials and unrelated personal content; record redaction limits.

Static plan/configuration/source bindings retain their real byte hashes. Live logs/history are mutable: freeze the consumed window in the report, not an entire growing file as an immutable prerequisite. Normal later appends do not invalidate that snapshot; truncation, identity changes, out-of-window evidence and resets must be disclosed. The parent must obtain current process/evidence observations before any control action; this report is not a live lease.

### 3. Diagnose in context

Separate technical instability, scientific performance and observability. Use the actual metric direction and training stage; do not assume every objective decreases monotonically. A short noisy segment, warm-up or falling behind a paper's final baseline is not an automatic failure.

| Severity | Meaning |
|---|---|
| `healthy` | Adequate fresh evidence supports normal behavior within the observed window; not proof of final success. |
| `warning` | An evidence-backed concern needs inspection or more observations, but failure is not established. |
| `critical` | Concrete severe instability/failure evidence, such as confirmed non-finite training loss, interpreted in the actual training context. |
| `unknown` | Missing, stale, mismatched or insufficient evidence prevents a reliable quality judgment. |

Use explicit plan/request thresholds, warm-up exclusions, comparable baseline protocol and minimum windows. Without them, state the concern and uncertainty instead of inventing `N`, a universal divergence ratio or an early-stop rule. Missing freshness policy means report actual ages and the limit on a current-health claim; never invent a freshness threshold. A repeated scan of unchanged data is not additional evidence.

Recommendations are `continue`, `wait`, `inspect` or `request_stop`, with evidence and a reason. They are advisory only. Scientific underperformance without an approved early-stop criterion normally calls for inspection, not termination. A verified negative final result is not a technical failure and does not authorize a retry.

### 4. Review ambiguous evidence when useful

For genuinely ambiguous signals, use the host's isolated read-only subagent capability when available. Supply the frozen evidence window, original attempt bindings, metric definitions, actual policy, comparable baseline and precise question. Ask for evidence-backed diagnosis, uncertainties and a recommendation, not an instruction to kill a process.

The reviewer cannot write reports/tracker, control processes or authorize actions. The diagnostic helper is the sole report writer. Preserve reviewer disagreement. If isolation is unavailable, disclose that fact and retain uncertainty; never claim an independent review occurred. Obvious observations do not require delegation.

### 5. Persist the diagnosis before reporting success

Write the reserved unused report and read it back. Use this report structure, filled only with actual observations:

1. **Binding**: diagnosis ID (`D0001`, matching its allocated filename), request ID, Run ID/attempt, project/docs/code roots, process/job identity as observed, original static input paths/hashes and caller mode if supplied. Null fields are explained.
2. **Observation**: capture UTC, source identities, windows/watermarks, actual sample counts, latest metric timestamps/ages and freshness policy or its absence.
3. **Evidence snapshot**: consumed metric rows/excerpts, units/directions, source locators and any conflicts/redactions. Keep enough actual data to audit the conclusion without relying on a later mutable log.
4. **Diagnosis**: severity, supporting observations, technical versus scientific concerns, baseline comparability, uncertainty and missing evidence; distinguish facts from inference.
5. **Advice to controller**: recommendation, rationale and a next-check condition/interval only if justified by the supplied cadence/policy. Explicitly state that no control action or tracker update was performed.
6. **Review**: whether independent review actually occurred, its findings/disagreement or why not needed/available.

The report's fenced JSON summary contains `diagnosis_id`, `request_id`, `run_id`, `attempt`, `observed_at`, `severity` and `recommendation`, matching the report and returned message. Keep the report's own SHA-256 out of its content; compute it from finalized UTF-8 file bytes after writing and reading back.

If writing/read-back fails, report the exact failure and any actually written path. Do not claim a persisted diagnosis, emit `report_ready` or fall back to overwriting another report. Still alert the caller to observed critical evidence; it may assess that evidence independently, not treat the missing report as verified.

### 6. Return to the parent; do not make its decision

After successful persistence, return a `TRAINING_DIAGNOSIS_RESULT` bare JSON object through the current host's normal caller-result channel. The following is a field template, not a real diagnosis:

```json
{
  "from_skill": "research-training-check",
  "to_skill": "research-run-experiment",
  "status": "report_ready",
  "request_id": "<actual request ID>",
  "diagnosis_id": "D0001",
  "project_root": "<actual absolute project root>",
  "docs_root": "<actual absolute docs root>",
  "run_id": "<bound experimental Run ID or null>",
  "attempt": null,
  "report_path": "<actual absolute report path>",
  "report_sha256": "<actual finalized report byte SHA-256>",
  "observed_at": "<actual capture UTC>",
  "severity": "unknown",
  "recommendation": "inspect",
  "controller_decision": null
}
```

At runtime use real values/types, including a numeric attempt or actual JSON null, not placeholder strings. `report_ready` means the diagnosis file is available, even if its severity is `unknown`; it is never a run lifecycle status. No parent decision is invented inside this result.

For a parent-called check, return to the already-active execution invocation. Do not recursively start another execution invocation, fabricate a `NEXT_SKILL_HANDOFF`, ask to reapprove reading the requested diagnosis, or bypass the parent's internal control-authorization gates.

For a standalone check, show the actual report path, digest and conclusion to the user. Without an active parent, do not pretend to have delivered a callback. Recommend a fully resolved `/research-run-experiment ... — mode: review` invocation if the real plan/tracker and attempt are available; otherwise name the missing bindings. Do not autonomously enter monitor/deploy or invent filenames. Explicit invocation or fresh specific user consent is required for a new execution invocation.

## Parent acceptance and decision boundary

The parent must read the exact returned file, verify its byte digest, roots, request ID, diagnosis ID, Run ID/attempt, summary values and original input bindings, and reject stale/mismatched/tampered reports. Never discover a replacement by newest filename or mtime. A critical recommendation is an input to a decision, not a control command.

Only the parent reconciles the diagnosis with current process identity/state, newer evidence, budget, mode and explicit stop/retry authorization. Review mode records and recommends only. A monitoring or deployment invocation may stop only the exact verified authorized process/job when its actual stop permission/criterion is satisfied; absent permission, ask the user rather than terminating. Parameter edits and retries retain their separate authorization gates.

The parent records report path/hash, observation time, actual decision, reason, permission basis and observed action outcome under the same attempt in the existing `EXPERIMENT_TRACKER.md`. The helper report is evidence, never a competing tracker. A diagnostic warning or unavailable telemetry alone does not change a genuinely active run into `BLOCKED` or `DONE`.

## Changes in 2.0.0

Renamed to `research-training-check`; removed framework-specific metadata, mandatory WandB, direct process control and implicit polling. Added fixed project-docs report storage, immutable flat diagnosis history, attempt-bound evidence snapshots and an explicit advisory return/parent-decision contract.
