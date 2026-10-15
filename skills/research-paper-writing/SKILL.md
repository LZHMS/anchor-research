---
name: research-paper-writing
description: Compose, review, and actually compile a detailed manuscript from an approved, immutable result-backed paper planning bundle. No experiments or publication actions.
version: 3.1.0
author: Zhihao Li
license: MIT
platforms: [linux, macos, windows]
metadata:
  related_skills: [research-paper-plan, research-paper-poster]
---

# Research Paper Writing

Writing is the middle stage: **research-paper-plan → research-paper-writing → research-paper-poster**. Planning organizes actual code/results and approves the high-level story; writing expands that story into detailed sections and paragraphs, verifies citations and numeric correspondence, and produces a genuinely reviewed build. It does not run experiments, re-analyze data, select new evidence, or publish anything.

Use host-provided file access, command execution, questions, optional isolated reviewers and visual inspection. No particular agent framework, editor, provider, reviewer profile or API is required. Dependencies are capabilities to check, not packages to automatically install. Never change global environments, launch training/inference/evaluation, control unrelated processes, perform Git operations, schedule work, send notifications, upload, submit or print.

Follow the [shared human anchor gates](../research-shared-references/anchor-gates.md) and the self-contained rules here. User-confirmed direction outranks autonomous framing; actual code/results describe implementation, not permission to change the problem. Stage entry, final manuscript acceptance and poster entry are separate decisions.

## 1. Resolve scope and authorization

Resolve `PROJECT_ROOT`: explicit argument > accepted bound invocation > current working project. `DOCS_ROOT` defaults to `PROJECT_ROOT/docs`; inherit an explicitly bound override. `repo_path` is the actual code root and may differ. Never use the installed skill directory as project root.

Defaults:
- `PLAN_DIR = DOCS_ROOT/research-paper-plan`
- `WRITING_DIR = DOCS_ROOT/research-paper-writing`
- Inputs: `PLAN_DIR/PAPER_PLAN.md`, `PAPER_BUNDLE.json`, `PAPER_PLAN_STATE.json`.
- Outputs: `WRITING_DIR/main.tex`, `sections/`, `references.bib`, `figures/`, `tables/`, successful `main.pdf`, `WRITING_REPORT.md`, actual review reports, `MANUSCRIPT_MANIFEST.json`, `WRITING_STATE.json`.

Honor explicitly bound existing source/output paths without moving or deleting user files. Do not silently fall back to root `PAPER_PLAN.md`, `paper/`, dated folders, latest-by-mtime sources or aliases. Accept exact `paper_plan_path`, `bundle_path`, `paper_plan_state_path`, `source_materials`, `repo_path`, `code_paths`, `result_paths`, `report_paths` and `evidence_paths`; preserve the approved bundle's exact bindings onward. Reports and diagnostic advice are context, not measurements; writing consumes planning's prepared results, not newly extracted report numbers.

A direct explicit invocation authorizes only this requested stage. Otherwise require one latest unresolved bare-object `NEXT_SKILL_HANDOFF` from `research-paper-plan` to `research-paper-writing`, with `project_root`, `docs_root`, fully resolved recommended chat `invocation`, `artifacts: [{role,path,sha256}]`, `status: awaiting_confirmation`, and exact `paper_plan_path`, `bundle_path`, `paper_plan_state_path`, `source_materials`. Artifacts must enumerate all three control files and consumed inventories, with hashes and semantic provenance.

Direct unambiguous yes/可以/继续 to that unique offer consumes it once. Quoted/ambiguous assent, refusal, silence, timeout, autonomous mode and previously consumed assent never authorize. Refusal sets `declined`; changed bindings set `stale` and require fresh scope/assent. Revalidate before writes/actions, then record `accepted` and `running`; `completed` only for the real completed stage, `failed` on failure. Recovery is only within the same authorized stage and unchanged verified scope. Outline approval is not writing authorization; neither grants poster or publication permission.

## 2. Mandatory immutable entry gate

Before drafting or resuming:

1. Read the exact plan, bundle and state. Require schema_version 1, plan state `ready`, actual independent plan review evidence, and `outline_approval.approved: true` with the current `bundle_sha256` and actual user confirmation reference. Verify state's `paper_plan_path`, `paper_plan_sha256`, `bundle_path`, `bundle_sha256` against real bytes.
2. Verify every `sources` and `derived` `{role,path,sha256}` inventory entry in `PAPER_BUNDLE.json`, including plan, actual implementation/evaluation code, original configurations/attempt bindings, completed raw result snapshots, `RESULTS.json`, `RESULTS_REPORT.md`, analysis scripts, prepared tables/figures and reviews. Inventory files, not directory labels. Hash actual file bytes; UTF-8 text is not normalized before hashing. Missing files, stale hashes, malformed records, unapproved/incomplete bundles and unresolved required evidence/review are blockers, not opportunities to pick substitutes.
3. Validate the bound proposal/literature and paired summary's existing canonical `input_sha256`, context and `papers_sha256` semantics when consumed. Preserve original plan/proposal/code/config/run/attempt bindings; never reassign historical metrics to current code. Direct projects may bind exact equivalent materials; record absent context honestly, never fabricate it.
4. For dynamic logs use the bundle's immutable bounded snapshots and recorded source identities/watermarks; do not replace them with the now-growing log or silently ignore truncation/reset/mismatch.
5. Read approved claims (`supported`, `partial`, `unsupported`), limitations, exclusions and denominators. Only approved, appropriately qualified claims may enter prose. A completed negative result is legitimate; missing evidence is not. Reject unsupported assertions presented as established findings.

Keep these bindings fixed. Changed claim, result, method, data, source selection or figure semantics returns to planning for regenerated evidence/review and fresh user outline approval; writing must not repair evidence by recomputing statistics, running jobs, selecting better seeds, adding baselines or silently changing the story. A new invocation alone cannot waive readiness.

## 3. Template and composition preparation

Read [writing-guide.md](references/writing-guide.md), relevant parts of [paper-types.md](references/paper-types.md), [reviewer-guidelines.md](references/reviewer-guidelines.md), and [checklists.md](references/checklists.md). Venue/year details in these references are historical aids, not current requirements. Experiment/human-evaluation/autoreason references are background only; they do not authorize analysis or execution in this stage. The boundaries here override any older lifecycle advice in references.

Inspect actual available [templates](templates/README.md), their source instructions and the bound target venue, year, track and document type. Use a supplied current template where appropriate; do not call an old bundled year current. Copy only needed template resources into the output workspace, preserving licenses. Do not modify vendor templates in the installed skill or delete user compiled assets. Unknown requirements permit a clearly declared generic draft, not venue-compliance claims. No arbitrary automatic downloads, package installs or shell escape. If required resources are unavailable, record the exact blocker.

Optional reference-paper LaTeX can inform rhetorical structure, notation, caption density and transitions. It is not mandatory, evidence for this project's results, or permission to copy prose/claims. Enumerate/hash any actually consumed reference includes/assets. Do not require a fixed reference-paper directory.

Build a paragraph-level composition map in `WRITING_REPORT.md`: section/subsection, paragraph purpose, planned claim IDs, evidence IDs, citation keys, figure/table labels and page budget. This detailed expansion belongs here, not in the planning outline. Preserve the approved high-level story and scope while choosing effective paragraph order and transitions.

## 4. Citations and prepared assets

Construct `references.bib` from the approved citation plan and bound literature. Verify identity (title, authors, year, venue, stable identifier), actual cited passage and metadata against supplied source documents or authoritative records using available capabilities. No invented entries or references from memory. Metadata verification is allowed; searching for a new literature/evidence selection is not. Missing or conflicting metadata/support is recorded as a blocking citation issue, not a fake citation key in a ready manuscript. API clients in [citation-workflow.md](references/citation-workflow.md) are optional examples, never mandatory dependencies or installation instructions.

Copy the bundle's actual prepared figures and tables into the manuscript workspace, preserving originals and source IDs. No new analysis, replotting, smoothing, recomputation, reselection or changed aggregates here. Typographic adjustments (font size, line wrapping, dimensions, label readability) may preserve semantics and must be recorded. A semantic asset change returns to planning.

Maintain a traceability ledger in `WRITING_REPORT.md`. For **every numeric assertion and every caption**, record TeX path/label/locator, claim ID, result_id/aggregate_id or prepared table-cell/figure-series ID, exact source path/hash/locator, displayed value/unit/precision, uncertainty semantics and any already approved transform. Protocol numbers, dataset sizes and hyperparameters map to bound code/config/protocol sources rather than being mislabeled as measured outcomes. Qualitative diagrams/captions map to bound method evidence; never invent result IDs. All empirical values must match `RESULTS.json` and approved prepared assets. Use only already justified rounding; percentage versus percentage-point differences, direction, valid n, split and budget remain explicit. A missing approved numeric transform is a planning issue, not permission to calculate a new headline.

## 5. Detailed manuscript composition

Use the approved What/Why/So What as the narrative spine. Do not confuse persuasive structure with inflated certainty.

- **Title:** precise problem/contribution keywords; avoid unsupported superiority and unnecessary acronyms.
- **Abstract:** specific contribution, challenge/importance, approach, evidence and qualified takeaway. The five-sentence formula is a useful scaffold, not a quota. Every result/number must already be approved and traceable.
- **Introduction:** move from concrete problem to gap, central insight, approved contribution bullets and bounded evidence preview. Explain why the gap matters, not why the whole field is popular. Fit the approved page budget rather than applying a universal page rule.
- **Background/related work:** group by approaches, assumptions and contrasts, not a sequence of paper summaries. Separate prior authors' findings from this study's claims; cite the actual support for each distinction.
- **Method:** define task and notation before use; present intuition before formalism, then algorithm, inputs/outputs, assumptions, objective and implementation details from the approved code-to-method map. Distinguish implemented behavior from aspirational proposal text. Use reproducible specifics without adding unexecuted variants.
- **Experimental setup:** specify bound datasets/tasks/splits, metrics and direction/unit, baselines, budgets, seeds, valid/excluded run counts and already prepared statistical procedures. State which approved question each comparison answers.
- **Results:** lead paragraphs with the question, point to the actual table/figure, state the bounded observation, then interpret cautiously. Include failures/null findings and comparability limits. Tables use legible aligned numbers and consistent precision; emphasize best entries only where the approved comparisons justify it. Never imply significance merely from ranking or overlapping error bars.
- **Captions:** explain what is shown, data scope, axes/units, method labels, independent unit/valid n and the actual error-bar statistic; distinguish observation from interpretation. Make the panel understandable without inventing missing methodological detail.
- **Discussion/limitations/impact:** distinguish evidence from hypotheses, describe external-validity and missing-experiment limits, and report genuine ethics/disclosure facts without invented approval, consent or universal safety claims.
- **Conclusion:** restate only the supported takeaway and scope; no new claims or numbers.
- **Appendices:** preserve required reproducibility details/proofs and planned supporting results. Do not hide evidence needed to understand a main claim or add unapproved results.

For theory, survey or position structures use the approved evidence and [paper-types.md](references/paper-types.md); this skill cannot bypass an incomplete planning bundle by relabeling an empirical paper.

### Two passes

**Pass 1: draft and locally refine.** Give each paragraph one purpose: topic sentence → evidence/reasoning → bounded implication → transition. Keep subjects near verbs, put familiar context first and important new information in stress positions, replace vague pronouns and nominalizations, define symbols/acronyms once, and remove generic openings. Preserve technical precision over decorative variation.

**Pass 2: global consistency.** Read the whole paper against the ledger and plan. Align title/abstract/contributions/results/conclusion, terminology, notation, units, denominators, limitations, captions and cross-references. Remove duplicated background and unsupported causal/superlative language. Check bibliography completeness, labels/includes, escaped characters and venue-compatible packages. Use typography helpers only if compatible with the actual template.

## 6. Actual build and independent review

Inspect the build recipe for side effects; use an available compiler appropriate to the actual template. For example, `latexmk -pdf main.tex` is suitable only when that executable and the template's engine/dependencies are present. Alternatives must perform the real necessary bibliography and cross-reference passes, not merely execute one command. No automatic installs or uploads. Record exact command, cwd, engine/version, dependency information, exit code and full log. Inspect unresolved citations/references, missing assets/fonts, overflow/page constraints and the produced PDF when inspection is available. Zero exit alone is insufficient. Never use an old PDF as evidence of a current successful build; preserve it as historical if needed and mark it nonfinal.

Obtain real independent review through available isolated host reviewers or an independent human review, not a self-authored pretend ensemble or named framework profile. Give reviewers the actual manuscript, approved plan/bundle/results, ledger and build evidence. Request actionable checks of evidence/numerical/caption fidelity, method/code correspondence, citation support, clarity, limitations and actual venue/layout constraints. Save actual reports at unused flat `writing-review-0001.md`, etc., including reviewer independence, reviewed input hashes, findings and disposition. Do not overwrite earlier reports or invent scores. Self-checks complement but never replace independence. Missing independent review capability leaves `awaiting_review`, never `ready`.

Integrate actual feedback; record each fix or unresolved issue. Evidence changes return upstream. After material edits repeat affected checks, rebuild when any build input changes, and obtain review covering the final content; explicitly bind final review coverage. Numerical/citation/review/compilation blockers prevent readiness and a poster offer. Missing required visual inspection is explicitly unverified/blocked, not claimed as passed.

## 7. Freeze actual artifacts and state

Write `WRITING_REPORT.md` with resolved scope/paths, template provenance and compliance limits, paragraph map, citation and numeric/caption ledger, copied asset bindings, typography changes, actual build/inspection records, review dispositions and outstanding blockers. No placeholder completion claims.

Write `MANUSCRIPT_MANIFEST.json` with `schema_version: 1` and these required fields:
- `project_root`, `docs_root`, `paper_plan_path`, `bundle_path`, `bundle_sha256`, `paper_plan_state_path`, `paper_plan_state_sha256`.
- `paper_tex_path`; `paper_pdf_path` and `paper_pdf_sha256` only for a real corresponding PDF (use honest null when no final PDF exists).
- `sources`: exact consumed source inventories `{role,path,sha256}`, retaining original planning provenance and control-file bindings, including optional consumed style sources and verified citation records.
- `files`: actual `{role,path,sha256}` for entry TeX, every transitive include, bibliography/style resources, tables/figures/assets, build logs, report, actual reviews and relevant produced analysis artifacts if any. No invented analysis output; existing prepared analysis stays attributed to planning.
- `build`: actual command/cwd/engine/version/exit_code, log path/hash, actual build-input hashes and final PDF correspondence. Capture engine, bibliography/style and local template inputs actually used, not just `main.tex`. Record unavailable command/engine/log facts honestly as null with reason; failed/unavailable compilation cannot imply a final build.

Freeze sources before recording build-input hashes; perform the actual build against those bytes, then bind its real PDF digest and successful checks. Build evidence must show that final PDF corresponds to exactly the inventoried inputs. If any input changes, invalidate/rebuild. Record review/report hashes after finalizing them. Do not hash `MANUSCRIPT_MANIFEST.json` itself or mutable `WRITING_STATE.json` inside its inventories; do not introduce report/review/manifest digest cycles. Reports can bind reviewed source digests without embedding the future manifest digest.

Freeze manifest, then write `WRITING_STATE.json` with `schema_version: 1`, `status: blocked|awaiting_review|awaiting_confirmation|ready`, actual `compilation_status: succeeded|failed|unavailable`, `manifest_path`, `manifest_sha256`, `bundle_sha256`, actual review result evidence/bindings, and `manuscript_approval: {approved, manifest_sha256, confirmation_reference}`. Pending approval is false with null approved digest/reference. Ready requires current real successful compilation, resolved mandatory numeric/citation/format checks, actual independent final-content review AND user acceptance of this exact final manifest. Hash the exact state only when offering downstream; never insert its own hash or mutate frozen manifest to contain it. Any subsequent content change invalidates state/review/build/approval as applicable. Deliver partial drafts honestly as blocked or waiting, not ready.

### Final manuscript anchor — wait for the researcher

After genuine build/review checks pass, set `awaiting_confirmation`, present the actual final PDF/source, main claims and numeric takeaways, exclusions/limitations, review disposition, exact manifest path/hash and proposed delivery scope. Ask whether the user accepts this exact manuscript as the current final content. Entry consent, paper-outline approval, reviewer praise, silence, timeout and an autonomous flag do not answer this gate. Record the actual reply/reference only after unambiguous acceptance, revalidate all manifest/input bytes, then update only state to `manuscript_approval.approved: true` bound to that manifest and `status: ready`. Do not edit the frozen manifest to mark approval. Edits/refusal retain false approval; changed content returns through affected checks and a fresh final gate. Accepting this manuscript alone does not enter poster or authorize submission.

## 8. Explicitly scoped revision operations

Rebuttal, camera-ready preparation and venue conversion require explicit requested scope and the same valid evidence/build/review gates. Rebuttal addresses actual supplied review points politely with supported evidence; missing new experiments are routed to approved planning/execution, not promised or run. A change-marked PDF may be made only with an available inspected tool and real compilation. Camera-ready changes identities/acknowledgments only from supplied authorized facts and actual venue requirements; it does not infer acceptance. Format conversion starts from the actual target template, migrates content rather than incompatible preambles, and checks changed page/disclosure rules; claim/data changes still return to planning. None authorizes submission, public posting, upload, code release or publication strategy execution.

## 9. Optional writing → poster handoff

Offer [research-paper-poster](../research-paper-poster/SKILL.md) only when writing state is `ready`, `manuscript_approval.approved` is true for the actual current `manifest_sha256` with a genuine confirmation reference, real final PDF/source/assets match the successful build, final independent review is resolved and the approved planning bundle remains current. Never offer from an unapproved manuscript, failed/unavailable build, stale PDF, draft or unresolved blocker.

Print actual final paths and a fully resolved recommended chat invocation, for example `/research-paper-poster project="<actual-project-root>" docs_root="<actual-docs-root>" manuscript_manifest_path="<actual-manifest>" writing_state_path="<actual-state>" bundle_path="<actual-bundle>" paper_pdf_path="<actual-pdf>" paper_tex_path="<actual-tex>" asset_paths=[<actual-enumerated-assets>]`. Replace every illustrative value; do not emit placeholders as an offer.

Expose one bare-object conversation variable `NEXT_SKILL_HANDOFF` with:
- `from_skill: research-paper-writing`, `to_skill: research-paper-poster`, actual `project_root`, `docs_root`, fully resolved `invocation`, `status: awaiting_confirmation`;
- `manuscript_manifest_path`, `writing_state_path`, `bundle_path`, `paper_pdf_path`, `paper_tex_path`, `asset_paths` (actual transitive included paths, bibliography and assets, not a presumed glob), `target_venue` (honest null if unknown), and genuine `limitations`;
- `artifacts: [{role,path,sha256}]` enumerating manifest, state, frozen planning control/results inventories, final PDF, TeX/includes/bibliography/assets and real build/review evidence.

Ask whether to enter poster with this exact reviewed build, then stop. Only direct unambiguous assent to the latest unique offer authorizes that stage once. No approval cascading, automatic poster creation, printing or acceptance claim. Poster is terminal in this workflow.

## Version history

- **3.1.0:** Added a final user-confirmed manuscript anchor after genuine review/build, separate from poster entry; state binds exact manifest bytes and invalidates acceptance on content changes.

- **3.0.0:** Host-neutral manuscript-only stage; approved immutable planning bundle gate; default docs stage directories; detailed paragraph composition and numeric/caption ledger; actual independent review/build manifest/state; explicit scoped revisions and consent-bound poster handoff. Removed framework/editor/API requirements, automatic Git/install/publication actions and legacy output aliases.
- **2.3.0:** Earlier plan-driven writing and adjacent-stage confirmation workflow.
