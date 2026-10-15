---
name: research-retrofit
description: |
  Retrofit and update an existing research proposal based on a user-maintained Research Report and newly implemented core code. Performs gap analysis (report vs code) and a rebuttal-style review for submission readiness.
  Accepts: Core Code Files/Paths, Research Report Document, Docs Root Directory (e.g., `docs/`)
  Trigger: "update proposal from code", "通过代码更新方案", "retrofit proposal", "基于代码翻新", "根据代码改大纲"
version: 2.0.0
author: Zhihao Li
license: MIT
metadata:
  related_skills: [research-run-experiment, research-experiment-plannning, research-paper-plan]
  hermes:
    tags: [Research, Retrofit, Code-to-Plan, Review]
---

# Research Retrofit: Code-Driven Proposal Overhaul & Rebuttal-Style Review

Retrofit proposal using: **$ARGUMENTS**

## Overview

Apply the [shared human anchor gates](../research-shared-references/anchor-gates.md). Use this skill when you have a **user-maintained research report document** (reliable, up-to-date project notes) and **already written or tuned core code** (the implementation ground truth). Your formal research proposal files (`<DOCS_ROOT>/research-ideas/FINAL_PROPOSAL.md` and `<DOCS_ROOT>/research-ideas/PROBLEM_ANCHOR.md`) need to be reconciled with the actual implementation and current plans.

**CRITICAL PRINCIPLE**: Code is ground truth for what was *implemented*, NOT authority over what *problem the researcher intends to solve*. When code drifts from the original problem definition, the agent must NOT unilaterally rewrite the problem anchor to match the code. Instead, it must diagnose the divergence, draft the reconciliation, and ask the researcher whether to re-anchor or adjust the implementation.

```text
User Input (Docs Root + Core Code Files + Research Report)
  -> Phase 0: Auto-locate inputs -> Find Research Report, FINAL_PROPOSAL.md, PROBLEM_ANCHOR.md
  -> Phase 1: Reverse-Engineer & Gap Analysis -> Extract implementation, write docs/research-retrofit/CODE_ANALYSIS.md
  -> Phase 2: Draft Reconciliation & Human Re-anchoring Decision -> Present delta, obtain explicit user anchor approval before updating canonical files
  -> Phase 3: One-Shot External Review -> Host-native isolated subagent review, write docs/research-retrofit/REBUTTAL_REVIEW.md
  -> Phase 4: Final Polish & State Persistence -> Save docs/research-retrofit/RETROFIT_REPORT.md and RETROFIT_STATE.json
```
## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| Core Code Files / Paths | Explicit Paths / Glob | **Yes** | The single source of truth for the method's actual capability, architecture, and optimizations. |
| Research Report Document | Path | **Yes** | The user-maintained, up-to-date research project document containing the latest plans and notes to guide the proposal update. |
| Docs Root Directory | Path | Optional | Defaults to `<PROJECT_ROOT>/docs`; an explicit docs-root override is resolved against the current project. Output defaults to `<DOCS_ROOT>/research-retrofit/`. |
| Proposal / Anchor | Explicit Paths | Optional | Prefer supplied existing method documents, then bound paths, then exact canonical defaults. |

## Confirmed upstream entry

Adjacent upstream: [research-run-experiment](../research-run-experiment/SKILL.md). Adjacent receivers: [research-experiment-plannning](../research-experiment-plannning/SKILL.md) and [research-paper-plan](../research-paper-plan/SKILL.md).

Accept named inputs `project` (alias of `project_root`), `docs_root`, `proposal_path`, `anchor_path`, `report_path`, `code_paths`, and, when supplied, actual `repo_path`, completed `result_paths`, `plan_path`, `tracker_path`, `evidence_paths`, `completed_run_ids`, `original_run_bindings`, `review_json_path`/`input_json`, `summary_dir` and their existing provenance/digest bindings. Expand directories/globs into the actual consumed files; preserve selected code-root and original attempt/result identities through either downstream route, not only narrative summaries. Do not discard current experiment/evidence bindings or original per-run plan/proposal fingerprints. Resolve project explicit > accepted handoff > working project, with explicit changed inputs superseding any pending offer. Echo the full `/research-retrofit` chat invocation with resolved absolute paths before execution.

A direct request authorizes this skill once without a second entry question. Otherwise accept only the unique latest unresolved `NEXT_SKILL_HANDOFF` from `research-run-experiment`, with `to_skill: research-retrofit` and `status: awaiting_confirmation`, after a direct unambiguous affirmative referring to that offer. Read the whole reply: quoted assent, refusal, "可以，但先别执行", unrelated/ambiguous assent, silence, timeout, autonomous mode and absent/stale/consumed offers do not authorize entry. Refusal sets `declined`; valid assent sets `accepted`.

Before writes or external actions, verify every named path against the packet's `artifacts` list of `{role,path,sha256}` using exact file-byte SHA-256, including all consumed code/report/result files and literature summary contexts/sidecars. Also perform Phase 0's semantic provenance checks: byte hashes do not replace canonical review `input_sha256`, summary `papers_sha256`, or the separate reviewed-source/final-export fingerprints. Preserve source permissions and absent optional inputs; missing bound files never permit latest-file substitution. Any changed binding sets the offer `stale`: report the change and require a refreshed specifically confirmed offer or new explicit invocation, not a silent rebind.

After successful revalidation set `running`; set `completed` only after Phases 0–4 genuinely finish, and `failed` on failure. Accepted/running/completed/declined/failed/stale offers cannot authorize repetition. Recovery may resume only this already-authorized stage with unchanged verified inputs, never another stage. Entry assent does not grant internal reviewer approval, new data-source access, or permission for the next skill.

## Workflow

### Phase 0: Auto-Locate Inputs
1. Resolve `PROJECT_ROOT` from the explicit project argument, otherwise the bound handoff's accepted project root, otherwise the current working project directory (never the installed skill location). Resolve relative arguments against this root; **Docs Root Directory** defaults to `<PROJECT_ROOT>/docs`.
2. Locate the **Research Report Document** specified by the user and the supplied core code paths; explicit inputs take precedence and explicit missing paths remain errors.
3. Locate the outdated proposal: prefer the explicit existing proposal, then a bound handoff's path, otherwise exactly `<DOCS_ROOT>/research-ideas/FINAL_PROPOSAL.md`. `ResearchIdeasOverview.md` may provide user intent if supplied, but is not a replacement for an existing generated proposal to retrofit. Do not scan dated folders or select by modification time.
4. Locate the original problem anchor: prefer the explicit existing anchor, then its recorded bound path, otherwise exactly `<DOCS_ROOT>/research-ideas/PROBLEM_ANCHOR.md`. Missing proposal/anchor paths must be reported rather than creating replacement method files.
5. Read the bound `REVIEW_STATE.json` or report for actual upstream paths and content fingerprints. Defaults are `<DOCS_ROOT>/research-literature-review/research_foundation_review.json` and `<DOCS_ROOT>/research-literature-summary/`; explicit and recorded bindings must agree. Verify the summary manifest's resolved input path and canonical JSON `input_sha256` match the actual review, and current per-paper contexts and overview `papers_sha256` bindings are valid before using overview, aggregate report, or paper analyses for positioning.
6. Bind actual proposal/anchor/report/code paths and byte SHA-256 fingerprints before updating. The old proposal may intentionally be outdated, but its old score only applies to its exact reviewed source snapshot; preserve the clean final export/source fingerprint distinction. Report missing files, changed/conflicting provenance, or unavailable literature precisely. Do not overwrite an unrelated proposal or treat a prior final proposal as the choice for an awaiting-selection ideas workflow.
7. When supplied, read the exact `plan_path`, `tracker_path` and `evidence_paths` alongside `completed_run_ids`/`original_run_bindings`. Compare each executed run's original proposal/plan hashes with the method being retrofitted; preserve historical mismatches and required-evidence gaps explicitly. Code existence, tracker status and a review score do not establish an empirical result. Carry these bindings into the analysis and next-stage route; never silently rebind old runs to changed claims.

### Phase 1: Code Reverse-Engineering & Gap Analysis

Analyze the provided **Core Code Files** and cross-reference with the **Research Report Document**:

1. **System Architecture**: What are the actual modules, backbones, and data flows in the code?
2. **Objective Functions**: What losses, rewards, or regularization terms are actually computed?
3. **Representations**: What exact features, embeddings, or intermediate tensors are used? 
4. **Gap Analysis (Report vs Code)**: Explicitly list the discrepancies. Crucially, **identify features, components, or ideas mentioned in the Research Report that are NOT YET implemented in the code**. This unimplemented list provides the basis for future experiments.

Write your findings to `<DOCS_ROOT>/research-retrofit/CODE_ANALYSIS.md`, including the actual report/code input paths and fingerprints.

### Phase 2: Proposal Overhaul & Human Re-Anchoring Gate

Analyze whether the code implementation remains faithful to the bound `PROBLEM_ANCHOR.md` or introduces a fundamental problem drift:

1. **Draft reconciliation in `<DOCS_ROOT>/research-retrofit/`**:
   - Draft `<DOCS_ROOT>/research-retrofit/FINAL_PROPOSAL_DRAFT.md` replacing abandoned ideas with concrete code realities, integrating report plans, and adding a Pending Experiments section.
   - If the code solves a different problem or alters bottom-line constraints, draft `<DOCS_ROOT>/research-retrofit/PROBLEM_ANCHOR_DRAFT.md` showing the exact delta.
2. **Human Re-anchoring Gate**:
   - If problem drift is detected, you **MUST STOP AND ASK** the user before touching the canonical `PROBLEM_ANCHOR.md`:
     *"代码实现与既定问题锚点存在偏差：[说明偏差内容]。请确认：是（A）调整实现以符合原问题，还是（B）确认重新锚定问题（Re-anchor）以匹配当前实现？"*
   - Only upon explicit unambiguous user confirmation to re-anchor may `PROBLEM_ANCHOR.md` be updated in-place. If the user chooses (A), halt retrofit and report code adjustments needed.
3. **Commit approved proposal and anchor**:
   - After user approval, write updated proposal in-place to `FINAL_PROPOSAL.md` and (if approved) `PROBLEM_ANCHOR.md`.
   - Save the exact retrofitted proposal snapshot as the next unused `proposal-<N>.md` in `<DOCS_ROOT>/research-ideas/`.
### Phase 3: One-Shot External Review (Rebuttal-Style)

Launch a single, strict isolated sub-agent review of that exact immutable snapshot, supplying its actual path and byte SHA-256 fingerprint. The review result must identify this fingerprint; only this unchanged source snapshot receives its assessment.

Dispatch a single, strict isolated sub-agent review through host-native capabilities (supplying the snapshot path and SHA-256):

Prompt rubric:
- Evaluate CONGRUENCE, FOCUS, and SUBMISSION READINESS.
- Score out of 10: Problem-Method Alignment, Contribution Sharpness, Mechanism Elegance, Empirical Feasibility.
- Identify the single biggest target for rejection and suggest at most 3 immediate text/framing adjustments.

Preserve the raw response as the next unused `round-<N>-review.md` file in `<DOCS_ROOT>/research-ideas/`. Update the current `<DOCS_ROOT>/research-retrofit/REBUTTAL_REVIEW.md` with the actual snapshot path/hash, raw review path, and assessment; never overwrite an old raw review.

### Phase 4: Final Polish & State Persistence

Based on the review, perform one final textual polish directly on the bound `FINAL_PROPOSAL.md` to patch framing vulnerabilities (without changing code mechanics). Record its new final-export byte hash separately from the exact reviewed source hash.

Write `<DOCS_ROOT>/research-retrofit/RETROFIT_REPORT.md` and persist `<DOCS_ROOT>/research-retrofit/RETROFIT_STATE.json` with:
- `schema_version: 1`, `status: "completed"` (or `"awaiting_confirmation"` if approval is pending)
- `project_root`, `docs_root`, `output_dir: "<DOCS_ROOT>/research-retrofit"`
- `proposal_path`, `proposal_sha256`, `anchor_path`, `anchor_sha256`, `report_path`, `code_paths`
- `anchor_approval: {approved, anchor_sha256, confirmation_reference}`
- `proposal_approval: {approved, proposal_sha256, confirmation_reference}`

Present a summary to the user:
- Components discovered in code and added to proposal.
- Ideas from the Research Report identified as missing in code (Pending Experiments).
- Area Chair assessment score and biggest risk.
## Optional next-stage offer — route on actual readiness

Only after the analysis, in-place final export, immutable review and final summary genuinely exist, report the actual paths/hashes and remaining limitations. Do not interpret a favorable rebuttal review as empirical evidence or attach historical scores to changed claims.

- **Changed claims/method bindings or pending experiments required to support the claims:** recommend [research-experiment-plannning](../research-experiment-plannning/SKILL.md). Pass the updated proposal/anchor, report/code, current plan/tracker/evidence where available, and actual retrofit analysis/review. Set `review_summary_path` to `<DOCS_ROOT>/research-retrofit/REBUTTAL_REVIEW.md` and `code_analysis_path` to `<DOCS_ROOT>/research-retrofit/CODE_ANALYSIS.md`; bind `method_state_path` to `<DOCS_ROOT>/research-retrofit/RETROFIT_STATE.json`.
- **No required empirical gap and proposal matches real completed code/results:** offer [research-paper-plan](../research-paper-plan/SKILL.md), passing actual `repo_path`, inspectable method/evaluation `code_paths`, completed `result_paths`, `report_paths` and exact experiment/literature bindings. Reports/review scores are not measurements. Paper planning performs result auditing, statistics, table/figure generation and narrative preparation in `<DOCS_ROOT>/research-paper-plan`; final publication assets need not already exist. An unimplemented optional future-work idea is not completed evidence. Missing required experiments, inspectable code or actual data blocks an executable offer.

Choose one recommended route with a reason; if genuinely undecidable, ask for route selection before creating an offer. Never leave two routes pending for bare assent to choose. Keep only one active `NEXT_SKILL_HANDOFF` in conversation, not a new state file. Ask "是否使用这些绑定材料进入 [target]？" and wait. No automatic next-stage execution.

Canonical examples below are illustrative; runtime must replace every path/hash with actual resolved files and exact byte digests, enumerate every consumed file (including code directories, evidence and literature sidecars), and retain existing semantic digest fields separately. Optional fields are omitted when absent, not fabricated.
Each JSON block below is the bare object value of the conversation variable `NEXT_SKILL_HANDOFF`, not a nested envelope or an additional state file.

```json
{
    "from_skill": "research-retrofit",
    "to_skill": "research-experiment-plannning",
    "project_root": "/work/project",
    "docs_root": "/work/project/docs",
    "invocation": "/research-experiment-plannning project=\"/work/project\" proposal_path=\"/work/project/docs/research-ideas/FINAL_PROPOSAL.md\" anchor_path=\"/work/project/docs/research-ideas/PROBLEM_ANCHOR.md\" report_path=\"/work/project/docs/NARRATIVE_REPORT.md\" code_paths=[\"/work/project/src/model.py\"] review_summary_path=\"/work/project/docs/research-retrofit/REBUTTAL_REVIEW.md\" code_analysis_path=\"/work/project/docs/research-retrofit/CODE_ANALYSIS.md\" method_state_path=\"/work/project/docs/research-retrofit/RETROFIT_STATE.json\"",
    "proposal_path": "/work/project/docs/research-ideas/FINAL_PROPOSAL.md",
    "anchor_path": "/work/project/docs/research-ideas/PROBLEM_ANCHOR.md",
    "report_path": "/work/project/docs/NARRATIVE_REPORT.md",
    "code_paths": ["/work/project/src/model.py"],
    "review_summary_path": "/work/project/docs/research-retrofit/REBUTTAL_REVIEW.md",
    "code_analysis_path": "/work/project/docs/research-retrofit/CODE_ANALYSIS.md",
    "method_state_path": "/work/project/docs/research-retrofit/RETROFIT_STATE.json",
    "method_state_sha256": "<actual-retrofit-state-byte-sha256>",
    "limitations": ["Changed claim requires a newly bound validation plan; old results remain historical."],
    "artifacts": [
      {"role": "proposal", "path": "/work/project/docs/research-ideas/FINAL_PROPOSAL.md", "sha256": "<actual-final-export-byte-sha256>"},
      {"role": "anchor", "path": "/work/project/docs/research-ideas/PROBLEM_ANCHOR.md", "sha256": "<actual-anchor-byte-sha256>"},
      {"role": "report", "path": "/work/project/docs/NARRATIVE_REPORT.md", "sha256": "<actual-report-byte-sha256>"},
      {"role": "code", "path": "/work/project/src/model.py", "sha256": "<actual-code-byte-sha256>"},
      {"role": "review_summary", "path": "/work/project/docs/research-retrofit/REBUTTAL_REVIEW.md", "sha256": "<actual-review-byte-sha256>"},
      {"role": "code_analysis", "path": "/work/project/docs/research-retrofit/CODE_ANALYSIS.md", "sha256": "<actual-analysis-byte-sha256>"},
      {"role": "method_state", "path": "/work/project/docs/research-retrofit/RETROFIT_STATE.json", "sha256": "<actual-retrofit-state-byte-sha256>"}
    ],
    "status": "awaiting_confirmation"
}
```

For evidence-ready work use the following alternative, never as a second simultaneous offer:

```json
{
    "from_skill": "research-retrofit",
    "to_skill": "research-paper-plan",
    "project_root": "/work/project",
    "docs_root": "/work/project/docs",
    "invocation": "/research-paper-plan project=\"/work/project\" docs_root=\"/work/project/docs\" proposal_path=\"/work/project/docs/research-ideas/FINAL_PROPOSAL.md\" report_paths=[\"/work/project/docs/NARRATIVE_REPORT.md\"] repo_path=\"/work/code-repo\" code_paths=[\"/work/code-repo/src/model.py\",\"/work/code-repo/src/evaluate.py\"] result_paths=[\"/work/code-repo/results/metrics.jsonl\"] plan_path=\"/work/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md\" tracker_path=\"/work/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md\" method_state_path=\"/work/project/docs/research-retrofit/RETROFIT_STATE.json\"",
    "proposal_path": "/work/project/docs/research-ideas/FINAL_PROPOSAL.md",
    "report_paths": ["/work/project/docs/NARRATIVE_REPORT.md"],
    "repo_path": "/work/code-repo",
    "code_paths": ["/work/code-repo/src/model.py", "/work/code-repo/src/evaluate.py"],
    "result_paths": ["/work/code-repo/results/metrics.jsonl"],
    "plan_path": "/work/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md",
    "tracker_path": "/work/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md",
    "method_state_path": "/work/project/docs/research-retrofit/RETROFIT_STATE.json",
    "method_state_sha256": "<actual-retrofit-state-byte-sha256>",
    "limitations": ["Carry the actual reviewer and evidence limitations here; no required experiments remain."],
    "artifacts": [
      {"role": "proposal", "path": "/work/project/docs/research-ideas/FINAL_PROPOSAL.md", "sha256": "<actual-final-export-byte-sha256>"},
      {"role": "report", "path": "/work/project/docs/NARRATIVE_REPORT.md", "sha256": "<actual-report-byte-sha256>"},
      {"role": "plan", "path": "/work/project/docs/research-experiment-plannning/EXPERIMENT_PLAN.md", "sha256": "<actual-plan-byte-sha256>"},
      {"role": "tracker", "path": "/work/project/docs/research-experiment-plannning/EXPERIMENT_TRACKER.md", "sha256": "<actual-tracker-byte-sha256>"},
      {"role": "method_code", "path": "/work/code-repo/src/model.py", "sha256": "<actual-method-byte-sha256>"},
      {"role": "evaluation_code", "path": "/work/code-repo/src/evaluate.py", "sha256": "<actual-evaluation-byte-sha256>"},
      {"role": "completed_result_data", "path": "/work/code-repo/results/metrics.jsonl", "sha256": "<actual-result-byte-sha256>"},
      {"role": "method_state", "path": "/work/project/docs/research-retrofit/RETROFIT_STATE.json", "sha256": "<actual-retrofit-state-byte-sha256>"}
    ],
    "status": "awaiting_confirmation"
}
```

The recommended chat command is exactly the selected packet's `invocation`, augmented with all actual supplied literature, reviewed-source and evidence bindings; print it for the user with real absolute paths. On the planning route, name the paired foundation input `input_json` (the bound `review_json_path` value), retaining canonical `input_sha256` and summary snapshot semantics, and pass actual `review_summary_path`/`code_analysis_path` overrides rather than obsolete ideas companions. Retain `completed_run_ids` and `original_run_bindings` on either route where supplied. A valid "可以/继续/yes" authorizes only that uniquely offered target once under its receiver checks; it does not approve further transitions.

## Changes in 2.0.0

Code is recognized as ground truth for implementation, not authority over user problem; added explicit human re-anchoring decision before modifying canonical anchor/proposal. Relocated outputs to `<DOCS_ROOT>/research-retrofit/` (`CODE_ANALYSIS.md`, `REBUTTAL_REVIEW.md`, `RETROFIT_REPORT.md`, `RETROFIT_STATE.json`). Added `RETROFIT_STATE.json` with `anchor_approval` and `proposal_approval` passed as `method_state` to downstreams. Removed Hermes-specific CLI syntax in favor of host-native isolated subagents.