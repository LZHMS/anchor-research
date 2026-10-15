---
name: research-paper-plan
description: "Prepare audited results, real tables and figures, code-to-claim evidence, and a reviewed, explicitly user-approved high-level paper narrative from project docs, implementation/evaluation code, and completed result data."
version: 3.1.0
author: Zhihao Li
license: MIT
metadata:
  related_skills: [research-run-experiment, research-retrofit, research-paper-writing]
  tags: [Research, Results, Writing, Plan]
---

# Research Paper Plan

Project, evidence, and target venue: $ARGUMENTS

## Scope and contract change (3.0.0)

This stage prepares the evidence and high-level story; `research-paper-writing` expands it into a manuscript. An imagined outline, project report, intended experiment, or unchecked plot is not a ready paper plan. Version 3 replaces the report-only/root-plan contract with flat docs-stage artifacts, audited normalized results, runnable project-specific analysis, actual visual outputs, independent review, and a digest-bound final user gate. Existing explicit user-bound input/output paths remain valid; do not move or delete user material or silently substitute legacy paths.

Use host capabilities for reading files, execution, questions, optional isolated review, and visual inspection. No fixed provider, reviewer profile, agent framework, model, or tool API is required. Dependencies must actually be available; do not install packages or change a global environment automatically. This skill does not train, run inference, launch new evaluations/experiments, modify source code/configs/experiment trackers, manage processes, stage/commit/push, submit, upload, notify, or print. It may inspect implementation and evaluation code read-only and execute inspected analysis on already completed results. It does not write the full paper.

Apply the [shared human anchor gates](../research-shared-references/anchor-gates.md). Stage entry, input-anchor adoption, final narrative approval and permission to write are distinct. Keep the inline gates below even when the shared reference is unavailable; neither a reviewer score nor current code can approve a changed user problem.

## Roots, inputs, and entry authorization

Resolve `PROJECT_ROOT` from explicit `project`/`project_root`, then an accepted invocation binding, then the current working project; never the installed skill directory. `DOCS_ROOT` defaults to `<PROJECT_ROOT>/docs`, inheriting an explicitly bound override. `PLAN_DIR` defaults to `<DOCS_ROOT>/research-paper-plan`; the next stage defaults to `<DOCS_ROOT>/research-paper-writing`. Resolve relative paths against their declared root and record absolute resolved paths. No dated/RUN_ID output folders, root `PAPER_PLAN.md`, `paper/` aliases, newest-by-mtime selection, or silent fallback to historical files.

Accept exact inputs from direct invocation or upstream `research-run-experiment` / `research-retrofit`:

- `repo_path`: actual selected code root, which may differ from `PROJECT_ROOT`; honest null if unavailable.
- `code_paths`: actual implementation, evaluation/metric, and relevant analysis source files; inspect their dependencies/callers needed to understand the reported method.
- `result_paths`: actual completed machine-readable metrics, predictions, or evaluation records. Reports/diagnostic advice cannot replace these data.
- `proposal_path`, `report_paths`, `evidence_paths`, `plan_path`, `tracker_path`, `completed_run_ids`, and `original_run_bindings` when present.
- `review_json_path` (or explicit `input_json`), `summary_dir`, canonical `input_sha256`, summary snapshot/context bindings, and source permissions when present.
- `method_state_path`/`method_state_sha256`, `plan_state_path`/`plan_state_sha256`, and corpus/summary owner state bindings when supplied: exact human acceptance evidence, not inferred from artifact names or technical review.

Prefer explicit exact paths, then accepted exact bindings, then these inspectable defaults:

1. `<DOCS_ROOT>/research-ideas/FINAL_PROPOSAL.md`.
2. `<DOCS_ROOT>/research-literature-review/research_foundation_review.json` with the paired `<DOCS_ROOT>/research-literature-summary/` manifest, contexts, analyses, sidecars, and overview actually consumed.
3. `<DOCS_ROOT>/research-experiment-plannning/EXPERIMENT_PLAN.md` and `EXPERIMENT_TRACKER.md` (the existing directory spelling is intentional).
4. Explicit retrofit/diagnostic/narrative reports, real code/configs, original attempt evidence, completed result data, and relevant existing assets. Inspect actual supplied/project structure; never guess a universal log/result format or ingest unrelated directories recursively.

Direct existing projects can supply exact equivalent materials; record missing context, unknown provenance, and limitations rather than fabricate proposals, code versions, or literature. Missing final publication tables/plots is not an upstream blocker: preparing them from real data is this stage's job. Missing actual code/results or experiments required for the proposed claims is a blocker. A brief contribution description can clarify intent, not replace evidence.

A direct explicit invocation authorizes only this stage. Otherwise require the latest unique unresolved bare-object conversation variable `NEXT_SKILL_HANDOFF`, addressed from an upstream above to `research-paper-plan`, with `project_root`, `docs_root`, full resolved `invocation`, exact stage input fields, `artifacts: [{role,path,sha256}]`, and `status: awaiting_confirmation`. Echo the actual fully resolved recommended CHAT invocation. Direct unambiguous assent (`yes` / `可以` / `继续`) to that unique offer consumes it once: `accepted`, revalidate paths/bytes/semantic bindings before writes or actions, then `running`. Refusal is `declined`; changed inputs are `stale` and require fresh scope/assent. Quoted/ambiguous assent, conditional refusal, silence, timeout, autonomous mode, or consumed assent never authorizes entry. Track `completed` only after ready artifacts exist; record real `failed` outcomes and pending gates honestly. A pending approval is not completion or an execution failure. Interruption can resume only the same authorized stage with unchanged validated inputs.

Entry assent is not final narrative approval and never authorizes writing. Never replace a missing bound file with another/latest result.

## Required references

- Read `refer/result-preparation.md` before auditing, normalizing, aggregating, or plotting results; it defines the result preparation and traceability procedure.
- Read `refer/writing-principles.md` when framing What/Why/So What, contribution, high-level Abstract/Introduction/Related Work, or hero visual. Detailed paragraph composition belongs to writing.
- Read `refer/venue-checklists.md` before setting a venue/year/type page budget. Official current requirements, not historical defaults, govern. Unknown venue/year permits a clearly declared generic plan, not a compliance claim.

## Workflow

### 1. Inspect docs context and validate semantic provenance

Read the actual proposal, paired literature, experiment plan/tracker, original run bindings, and reports. Separate intended design, implemented behavior, measured findings, and interpretive advice. If ideas state is awaiting candidate selection, an old final proposal is not the current choice. A score or report applies only to its exact reviewed source; keep the delivered final proposal byte hash separate from the immutable reviewed-source hash and explain differences.

For framework-produced methods, read the explicitly bound `method_state_path` (ideas `REVIEW_STATE.json` or retrofit `RETROFIT_STATE.json`) and verify its actual byte digest, `anchor_approval` and `proposal_approval`, real confirmation references and matching anchor/proposal bytes. Verify supplied experiment `plan_approval` against its approved plan/planning snapshot, and consumed corpus/summary approvals against their exact content bindings. A candidate choice, high technical score, completed run or source-code difference cannot approve a new problem or mechanism. Pending/stale upstream decisions remain pending/stale; do not select another owner state by mtime.

An existing project may lack canonical predecessor states. Present its actual problem, non-goals, method, evidence scope and differences, and obtain genuine explicit `input_anchor_approval` in this paper stage's state/report before finalizing it as accepted direction. Bind actual source paths/digests and the real reply; do not fabricate upstream phases or write their approval states. Authorized read-only auditing/result preparation may proceed as a draft, but missing direction adoption blocks ready state and downstream offers. It cannot waive missing measurements, review or build evidence.

Preserve existing literature semantics, not just file existence or byte hashes:

- Canonical JSON digest means SHA-256 of UTF-8 `json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`, matching the upstream digest helper. It is distinct from hashing the actual JSON file bytes.
- Validate the summary `analysis_manifest.json` input path and canonical `input_sha256` against the actual foundation review. For each consumed/current task, recompute canonical `context_sha256` from the entire actual context; require matching paper identity, evidence level, actual analysis and result sidecar, and sidecar context binding. Do not rebuild a digest from selected fields or accept stale four-field sidecars.
- Validate the overview's actual ordered paper snapshots: `paper_id`, task `context_sha256`, actual Markdown-byte `analysis_sha256`, and canonical sidecar-dictionary `result_sha256`. `papers_sha256` is the canonical digest of the OBJECT `{"papers": paper_snapshots}`, not the bare list or concatenated hashes. Validate actual overview context/result `input_sha256` and `papers_sha256` against that current snapshot.
- Carry canonical review/context/overview digests AND exact byte inventories of consumed review, manifest, contexts, sidecars, analyses, and overview. Preserve metadata/evidence level; an abstract-only summary is not full-text evidence. Verify cited metadata and separate literature-reported measurements from this project's measurements.

Record stale/missing bindings and absent optional context in `RESULTS_REPORT.md` and the plan. Never silently relabel old evidence. Do not repair upstream research files within this skill.

### 2. Inspect implementation and original evaluation applicability

Inspect actual method entry points, relevant modules/configs, data/split/preprocessing, training/inference/evaluation definitions, metric/direction/unit and checkpoint-selection rules. Trace each planned method description to code paths and symbols/line locators. Read inherited analysis before running it: imports and subprocesses must not launch training, inference, new evaluation, mutate upstream data, use uncontrolled network access, or overwrite source/tracker files.

For each attempt retain its original code/config/plan/proposal/checkpoint/data bindings. Current code SHA-256 is an observation of current bytes, never retroactive proof of historical run code. Compare observed changes with original snapshots/diffs and explain whether old results apply. Unknown historical code/config, divergent protocols, or an obsolete implementation cannot support unqualified current-method claims. `R001`, directory identity, completed status, and matching filenames alone prove nothing about applicability.

Build a code-to-method/claim map containing method component, source path/hash/symbol/locator, config/protocol, original attempt applicability, relevant result IDs, and limitations. Missing inspectable implementation/evaluation code blocks readiness for affected empirical claims.

### 3. Prepare and execute real result analysis

Follow `refer/result-preparation.md` against observed project schemas. Inventory source bytes/locators, freeze consumed bounded windows of growing logs into immutable snapshots with source identities/watermarks, and preserve originals. Record truncation/reset/mismatch. Bind snapshots, not a growing whole-log digest asserted to remain immutable.

Reuse trustworthy project analysis where possible. Otherwise implement complete project-specific adapters and analysis under `analysis/`; no universal assumed format, TODO adapter, synthetic fallback, promised future script, or no-op scaffold. Specify interpreter/dependency versions, source schemas, exact commands/cwd, parameters/selections, stdout/stderr/exit status, output paths, and actual execution records. Execute the inspected analysis on existing results only. If dependencies or execution capability are unavailable, report the concrete blocker; do not claim generated or checked output.

Produce `RESULTS.json`, `RESULTS_REPORT.md`, actual prepared `tables/` and suitable `figures/`. Inspect numeric outputs, source-to-cell/series mapping, table content, and rendered figures. Recompute metrics only when existing stored predictions AND actual matched ground truth permit it without model execution. A completed negative/null finding is evidence; absent/failed measurements are not zero or a negative finding.

### 4. Form a result-backed high-level narrative

Read the narrative reference; choose the strongest honest story the evidence supports, not the intended proposal's story by default. Answer:

- **What**: one clear contribution or diagnostic finding, with scope.
- **Why**: actual result/aggregate IDs and appropriate uncertainty, including conflicting findings.
- **So What**: significance grounded in verified literature and actual scope, not unsupported superiority.

Draft `PAPER_PLAN.md` with working title, venue/year/document type (or generic/unknown), evidence-backed one-sentence contribution, What/Why/So What, notation, limitations, high-level section purposes and page budget. Include the code-to-method map and claim-evidence matrix: claim ID/text, supported/partial/unsupported, result IDs, comparability/uncertainty, limitations, planned section. Unsupported claims remain explicitly excluded or proposed missing work, never factual contributions. Qualified partial claims must state the qualification. Required missing experiments keep the plan blocked; do not silently shrink requested scope to bypass the gate.

Plan high-level Abstract/Introduction/Related Work/Method/Results/Discussion/Conclusion as appropriate, not full sections or paragraph-level prose. Section count and page allocation follow the actual story and verified requirements, not a fixed template. Each section identifies its role, claims, prepared figures/tables and citations. Map verified paper IDs/metadata to citation purposes without invented references. Reference-paper LaTeX is optional style context, never an entry prerequisite.

List every consumed figure/table with actual prepared path/hash, result/aggregate IDs, transformations, uncertainty definition, caption intent, section, and limitations. A conceptual diagram must be clearly distinguished from a measured plot and must match inspected code. No figure quota or decorative fake curves. Proposed future experiments/plots remain separate from actual assets and cannot satisfy readiness.

### 5. Independent evidence, code, and narrative review

Request a genuinely independent review through available host-native isolated review capability. Supply bounded actual source files, the code-method map, normalized results, analysis/execution records, real tables/rendered figures, literature provenance, draft plan, and applicable venue rules. The reviewer must inspect evidence, not merely rate an outline. Ask for actionable findings on:

1. input/historical-code applicability, metric correctness, duplicate/missing/failed/nonfinite data, incompatible protocols, denominators, statistics/uncertainty;
2. source-to-result-to-table/figure-to-claim traceability and reproducible commands;
3. narrative/evidence alignment, negative findings, literature positioning, section/page budget, and mandatory venue constraints.

Write the actual report to an unused flat `plan-review-0001.md`, `plan-review-0002.md`, etc., without overwriting prior reports. Record reviewer independence/capability, actual reviewed file paths/digests, findings and disposition. A self-review, fictional reviewer response, or score alone is not independent evidence. Missing capability leaves `awaiting_review`, never ready. Reviewers cannot alter experiment inputs or approve user intent.

Apply actionable planning/analysis fixes only within scope; rerun affected analysis and inspect changed outputs. Resolve mandatory findings or record why a finding is nonblocking with evidence. Substantive changes to reviewed code applicability, data, statistics, claims, narrative or assets require renewed relevant review; never present old review as covering new bytes.

### 6. Freeze reviewed artifacts, then obtain explicit final user approval

Use the acyclic freeze order below; approval is not stored in the plan or bundle.

1. Finish results, analysis records, tables/figures, report and draft plan. Save actual review reports with hashes of the content they inspected. Apply fixes and obtain renewed review where required.
2. Finalize `PAPER_PLAN.md` (including source references and bundle path, but no bundle digest, readiness/approval flag, or self-hash). Freeze the reviewed source/derived bytes. Review reports bind their actual review inputs, NOT the eventual bundle digest. If final plan text changes after review, obtain coverage of those changes before freezing.
3. Build `PAPER_BUNDLE.json` from observed inventories, including the frozen plan, results, analysis, assets, and actual review reports. Do not put the bundle itself or mutable `PAPER_PLAN_STATE.json` into either inventory. Compute actual plan and bundle byte SHA-256.
4. Write `PAPER_PLAN_STATE.json` with current paths/digests, real review evidence, `status: awaiting_confirmation`, and `outline_approval.approved: false` (digest/reference null until actual approval). If evidence or review remains incomplete use the appropriate blocked/pending state instead.
5. Present the EXACT final story, claim statuses, key numeric results with n/uncertainty, negative findings, code-applicability limits, high-level sections, real table/figure previews, unresolved nonblocking limitations, plan/bundle paths and final bundle SHA-256. Ask the user explicitly to approve this narrative and high-level outline for that bundle. Earlier entry assent, a pre-review draft approval, silence, timeout, or autonomous mode cannot approve it.
6. On actual unambiguous user approval of this exact bundle, revalidate all bound bytes and review coverage; write only state with the approved digest and actual confirmation reference, then mark `ready` if every gate passes. Do NOT edit approved plan/bundle bytes to mark approval. Rejection/edits keep approval false; revise, review as needed, rebuild, and request fresh approval.

Any changed consumed source or derived content invalidates the old bundle and its approval; invalidate review when its inspected content changes. A plan-only/root legacy outline cannot satisfy writing entry. Missing actual data/code, mandatory experiments, justified statistics, appropriate real tables/figures, traceability, independent review, or explicit final approval cannot be waived by a readiness flag.

## Artifact schemas and inventory

All defaults below are directly in `PLAN_DIR`, with only `analysis/`, `tables/`, and `figures/` as content subdirectories. Update the current artifacts in place while preserving user files and unused-numbered review reports. Record actual paths for explicit overrides. A saved unapproved draft is allowed; readiness exists only in state.

### `RESULTS.json` — `schema_version: 1`

Root arrays: `records` and `aggregates`. Full field semantics and statistics are in `refer/result-preparation.md`.

- Each record retains unique `result_id`, `run_id`/`attempt` (honest null if unknown), `method`/`role`, `dataset`/`task`/`split`, `seed`, `metric`/`direction`/`unit`, actual finite `value` or null with `reason`, `status`, exact source `path`/`sha256`/`locator`, and original code/config/attempt/protocol bindings. Extra observed metadata is permitted, never invented. Missing/failed/excluded cases remain visible.
- Each aggregate retains `aggregate_id`, explicit `grouping`, `member_result_ids`, valid `n`, `mean`, sample `sd` (`ddof: 1`, null for n<2), statistic semantics, exclusions and attempted/observed/valid denominators. No incompatible pooling, duplicate attempt counting, best-seed cherry-picking, or zero-filled missing results. Other justified statistics require declared data/assumptions.

### `RESULTS_REPORT.md`

Actual source inventory and data audit; original/current code-method trace and applicability; observed schema/parser decisions; valid/excluded/missing/failure counts and denominators; comparability; statistical procedures/assumptions; actual commands/execution records; numeric/visual inspection findings; claim support and negative findings; missing experiments/data and limitations. Reports and plans are context, not measurements.

### `analysis/`, `tables/`, `figures/`

Complete runnable project-specific scripts/adapters, observed source schemas, exact interpreter/commands/deps, execution records and frozen source/derived data snapshots. Real consumed CSV/LaTeX tables as useful, real publication-appropriate plots in PDF/SVG plus viewable PNG as applicable. Keep machine-readable cell/series mappings under `analysis/` linking every output value to record/aggregate IDs, selection/transformation/rounding and uncertainty. Rendered images must actually be viewed; a zero-exit plotting command alone is not inspection. No placeholders or unsupported output claims.

### `PAPER_PLAN.md`

Include roots/actual source references and bundle path; title and verified venue rules or generic status; What/Why/So What and one-sentence contribution; notation; high-level sections and page allocations; code-to-method map; claims/evidence/limitations; figure/table/citation plans referencing actual assets and IDs; review dispositions and open nonblocking limitations. No full manuscript, self-hash, embedded approval/readiness flag, or unbound numeric claim.

### `PAPER_BUNDLE.json` — `schema_version: 1`

Required fields: `project_root`, `docs_root`, `repo_path` (honest null if unavailable), `paper_plan_path`, `results_path`, `sources`, `derived`, `claims`, `limitations`.

- `sources` and `derived` are lists of `{role,path,sha256}` for every actually consumed file: original code/config/raw result snapshots, proposal/literature/context/sidecars/reports, source schemas, prepared analysis scripts/data/execution records/tables/figures and review reports. Include `PAPER_PLAN.md` under `derived`. Enumerate consumed files, not directory-only hashes. Preserve `repo_path`, exact `code_paths`/`result_paths`, original bindings and semantic literature provenance in the plan/report and source entries; no current-code hash substituted for historical provenance.
- Each claim is `{claim_id,text,status,result_ids,limitations}`; `status` is `supported`, `partial`, or `unsupported`. `result_ids` refers to normalized records; map any aggregate/asset IDs through their members in the plan/report. Empty/unsupported evidence remains visible and cannot silently become a supported assertion.
- Hash actual file bytes (UTF-8 text exactly as stored), not reserialized JSON, except separately labeled upstream canonical semantic digests. No bundle self-entry, mutable state entry, guessed file, irrelevant recursive inventory, or digest cycle.

### `PAPER_PLAN_STATE.json` — `schema_version: 1`

Required: `status` (`blocked` / `awaiting_review` / `awaiting_confirmation` / `ready`), `paper_plan_path`, `paper_plan_sha256`, `bundle_path`, `bundle_sha256`, actual review evidence/bindings, and `outline_approval` with `approved` boolean, approved `bundle_sha256`, and actual user `confirmation_reference`. Also retain verified upstream method/plan/corpus/summary acceptance bindings, or a genuine current-stage `input_anchor_approval` for explicitly adopted existing-project inputs. Pending approval digest/reference are null; do not invent a conversation identifier. Store actual available message/turn reference or exact recorded confirmation with context. A direct stage invocation alone does not adopt newly inferred input anchors.

Record review report paths/digests, their actual reviewed file bindings and outcomes, unresolved findings and evidence blockers. `awaiting_review` requires preparation to be complete but independent review pending; `awaiting_confirmation` requires completed review and a frozen current bundle. `ready` requires all evidence/visual/statistical/traceability gates, actual independent review coverage, and approval of the current bundle digest. Missing required evidence is `blocked`, not a ready negative result. If blocked before plan/bundle files exist, use honest null unavailable path/hash bindings and record blockers; never synthesize hashes. A consumed upstream handoff is completed only on true ready completion.

## Plan → writing handoff (separate authorization)

Offer `research-paper-writing` only when the current bundle and state are ready, all inventory bytes and semantic provenance revalidate, no mandatory experiment/review blocker remains, and final narrative approval matches the current bundle. Writing may use a generic draft venue when declared; optional reference-paper LaTeX and venue unknowns are not invented prerequisites. Writing owns detailed prose/templates and real compilation, not evidence repair or new experiments.

Print the actual fully resolved recommended CHAT command:

`/research-paper-writing project="<PROJECT_ROOT>" docs_root="<DOCS_ROOT>" paper_plan_path="<actual-plan>" bundle_path="<actual-bundle>" paper_plan_state_path="<actual-state>"`

Then ask whether to enter that stage. Publish one active bare-object `NEXT_SKILL_HANDOFF` (not a nested envelope or extra state file) with:

- `from_skill: research-paper-plan`, `to_skill: research-paper-writing`;
- actual `project_root`, `docs_root`, `invocation`, `paper_plan_path`, `bundle_path`, `paper_plan_state_path`;
- `source_materials`: every consumed source/derived file `{role,path,sha256}` plus original attempt/code/config and semantic literature provenance carried through the bound plan/report; exact `repo_path`, `code_paths`, and `result_paths` where available;
- `artifacts`: all THREE control files (`PAPER_PLAN.md`, `PAPER_BUNDLE.json`, `PAPER_PLAN_STATE.json`) and the complete actual consumed inventory with byte hashes (including sources, results, analysis, tables/figures, reviews and literature sidecars/contexts);
- honest `limitations`, `status: awaiting_confirmation`.

Fill fields with actual resolved values only; do not emit a runnable-looking packet of placeholder hashes. Directory names and a ready flag are not inventories. Direct unambiguous assent to this unique latest unresolved offer authorizes writing once; revalidate before actions, mark accepted/running and actual completed/failed outcomes. Refusal declines; changes stale the offer and require fresh assent. Outline approval cannot be reused as writing assent. No automatic writing, poster, submission, publication, or printing follows this stage.

## Changes in 3.1.0

Connected paper preparation to the framework's human-approved method/plan/literature anchors. Existing-project adoption is an explicit local decision, not a fabricated predecessor history; draft analysis, independent review, final narrative acceptance and writing entry remain separate.
