---
name: research-literature-summary
description: "Provides a deep summary of a collected literature review JSON through bundled Python evidence preparation, one host subagent per paper, research-landscape synthesis, and content-bound validated aggregation. Updates evidence-grounded Chinese drafts directly in the current project's docs/research-literature-summary and can optionally file results into a PKBase (comparison page + source pages). Use when the user asks to 'summarize literature', 'analyze papers', 'literature summary', or needs a systematic overview of `research_foundation_review.json`."
version: 1.8.0
author: Zhihao Li
license: MIT
argument-hint: "input: docs/research-literature-review/research_foundation_review.json | project: <current-project-root> | out: <docs/research-literature-summary> | pkbase: <accessible-base-dir>"
metadata:
  tags: [research, literature-review, summary, analysis, zotero, pkbase]
  category: research
  related_skills: [research-literature-review, research-ideas, research-experiment-plannning, research-daily-ideas, wiki-pk-base]
  hermes:
    tags: [Research, Literature, Summary, Analysis]
---

# Research Literature Summary

Input literature review file and optional output/PKBase paths: `$ARGUMENTS`.
Resolve the input in this order: explicit invocation arguments; an accepted
`research-literature-review` handoff's exact `input_json`; otherwise the fixed
`docs/research-literature-review/research_foundation_review.json` under the resolved
project root. Missing explicit or bound paths are errors; do not substitute a historical
corpus, search wildcard paths, or invent data. If the fixed default is missing, report
that prerequisite and ask for an actual review input.

## Previous skill and confirmed handoff

The upstream skill is [research-literature-review](../research-literature-review/SKILL.md).
It collects the corpus and can offer this skill through its
`Next Step: Optional Handoff Confirmation Gate`.

- A direct invocation such as `/research-literature-summary input: "<actual JSON path>"`
  requests stage entry, not approval of its supplied corpus or future summary. This is a
  chat skill invocation, not a shell command. Replace an older unresolved recommendation
  if explicit arguments change the input; the input-anchor gate below still applies.
- When the parent has a `NEXT_SKILL_HANDOFF` from `research-literature-review` to this
  skill with status `awaiting_confirmation`, a direct affirmative reply to that specific
  offer (e.g. `可以` or `继续`) authorizes execution. The parent changes it to `accepted`
  and passes the bound `input_json`, `input_sha256`, `corpus_state_path`,
  `corpus_state_sha256`, `project_root`, `docs_root`, `summary_dir`, `invocation`, and
  `artifacts`; do not require the user to repeat them.
- Follow the review skill's complete-reply consent rules. A bare affirmative without a
  unique unresolved offer, a quoted example, or approval of an unrelated action does
  not activate this skill. `可以，但先别执行` does not authorize starting.
- Before writes, verify the bound input is still an accessible, valid review JSON,
  its canonical `input_sha256` and every `artifacts` byte SHA256 are unchanged, and
  the bound project/docs/output paths and invocation agree. Changed bindings set the
  offer to `stale` and require a refreshed specific confirmation. Stop on missing or
  mismatched bindings; never silently substitute another file or project root.
  Also require the actual producer `corpus_approval` to match the input-anchor rules
  below. Acceptance of this stage offer cannot supply missing corpus approval.
- At execution start, briefly echo the resolved invocation:
  `/research-literature-summary input: "<actual absolute INPUT_JSON path>" project: "<actual absolute PROJECT_ROOT>"`.
  Include `out:` or `pkbase:` only when explicitly supplied. This makes the recommended
  invocation reproducible but is not a substitute for actually executing the workflow.
- Set an accepted handoff to `running` and execute preparation, one subagent per paper,
  validated synthesis-input preparation, synthesis with its freshness sidecar, and
  finalization without asking for the same authorization again. Preserve the review
  JSON's source restrictions. Completion means all those stages succeeded; update the
  anchor to `completed`, or `failed` on a real failure.
- Consent is scoped to this summary execution and its current draft outputs. It does not authorize
  permanent PKBase filing, downstream research/refinement skills, or repeat runs.
  Such actions still require their own explicit user request or confirmation.
- Silence, timeout, or autonomous mode cannot approve a downstream skill. Interrupted
  work may resume only this same already authorized stage with unchanged bindings.

### Input-anchor gate: verified producer approval or genuine imported-input adoption

Apply the [shared human-anchor contract](../research-shared-references/anchor-gates.md); these
inline gates remain operative when that reference is absent. Before preparation or
source access, read the handoff's exact `corpus_state_path` (or, for a directly supplied
review produced by this workflow, its known sibling `CORPUS_STATE.json`). Verify the
actual state bytes against `corpus_state_sha256` when packet-bound, and require:

- actual `project_root`, `docs_root`, `input_json`, `enabled_sources`, `source_status`,
  `scope_constraints` and `evidence_limits` match the selected corpus and presented scope;
- `corpus_approval.approved: true`, nonempty real `confirmation_reference`,
  `corpus_approval.corpus_sha256` equal both state `corpus_sha256` and the actual review
  file-byte SHA256, and `corpus_approval.input_sha256` equal both state `input_sha256`
  and the canonical digest of the parsed current review;
- the corpus decision is current, not pending, refused or stale. Record the actual
  producer path/hash in this receiver's `SUMMARY_STATE.json`; never modify its approval.

For a genuinely standalone imported review with no producer history, first inspect the
actual file without extending source access, present its topic/facets, paper count,
source restrictions, coverage/evidence limits, actual files/hashes and constraints.
Ask whether the user explicitly adopts this exact input scope for summary. An existing
explicit acceptance of that same displayed scope may be recorded without asking twice;
a filename, generic invocation or bare assent with no unique pending decision is not
adoption. Record the actual acceptance in **this receiver's** `input_anchor_approval`:
`{approved, artifacts: [{role,path,sha256}], input_sha256, constraints,
confirmation_reference}`. All hashes and the confirmation must be real; keep approval
false and unknown values null while pending. Do not fabricate a review execution,
write a fictitious `CORPUS_STATE.json`, or use import adoption to bypass a known pending,
declined or stale producer decision. Resolve that decision with the user instead.

`SUMMARY_STATE.json` is host-owned at the actual `SUMMARY_DIR`; it records actual
`project_root`, `docs_root`, `input_json`, canonical `input_sha256`, `summary_dir`,
`corpus_state_path`/`corpus_state_sha256` (null for a genuine import),
`input_anchor_approval` (null when producer approval is used), and `status`.
Use `awaiting_input_anchor_approval` for pending import adoption; after verified producer
approval or real equivalent adoption, use `in_progress`. Refusal sets `declined` and
stops preparation; changed bindings set `stale` and require a freshly presented decision.
Silence, timeout, autonomous mode and stage-entry assent cannot supply either approval.
Preserve source limits and all technical prerequisites regardless of the entry route.

## Goal and ownership

Execute **prepare → delegate → synthesize-input → synthesize + overview sidecar →
finalize**. Python prepares source evidence and task files, validates the paper outputs
before preparing synthesis input, then validates and aggregates the host agents' actual
analyses. It does not generate paper analyses or call model APIs. The parent assistant
orchestrates one host subagent per paper and owns integration, failure handling, and
final reporting.
No separate model credentials, endpoint configuration, or local-model service is required.

Produce evidence-grounded Chinese per-paper analyses and a research landscape retaining:

- **Derived facets:** retrieval branches, key sub-directions, and themes.
- **Field definition and subfields:** define the primary field and introduce related
  sub-domains.
- **Core scientific questions:** central unresolved problems.
- **Datasets:** names, introductions, distinguishing characteristics, availability,
  accessibility, and licenses where supported by the evidence.
- **Methodology lineages:** method families/schools and how their mechanisms work.
- **Evaluation metrics:** meanings and underlying mathematical formulas where evidenced.
- **Open research gaps:** unresolved issues and potential future directions.
- **Evidence and coverage limits:** incomplete sources and unsupported landscape claims.

Never turn missing datasets, licenses, formulas, figures, experiments, or source text
into invented facts.

## Paths and CLI contract

- **SKILL_DIR:** the installed directory containing this `SKILL.md`.
- **SCRIPT_PATH:** `{SKILL_DIR}/summarize_review.py`, the bundled script. Always invoke
  this file; never generate or copy a script into the output directory.
- **SUMMARY_STATE:** `{SUMMARY_DIR}/SUMMARY_STATE.json`, maintained by the host assistant.
  The unchanged Python CLI neither writes nor approves this state or `CORPUS_STATE.json`.
- **PROJECT_ROOT:** explicit `project`/`--project-root`, otherwise an accepted handoff's
  `project_root`, otherwise the current working project directory (`Path.cwd()`).
  Pass a bound root explicitly as `--project-root`; Python cannot read chat anchors.
  Never use the installed script or skill location as the project root.
- **DOCS_ROOT:** `{PROJECT_ROOT}/docs`. Resolve relative CLI input/output paths against
  `PROJECT_ROOT`; installed assets remain separate, read-only locations.
- **INPUT_JSON:** explicit input, otherwise an accepted handoff's exact `input_json`;
  only when neither is present, use the fixed
  `{DOCS_ROOT}/research-literature-review/research_foundation_review.json`.
- **OUT_DIR / SUMMARY_DIR:** explicit `--out`, accepted handoff's `summary_dir`, or the
  fixed `{DOCS_ROOT}/research-literature-summary`. Any explicit output must remain
  inside that subtree; reject paths outside it. Never nest summaries in the review
  folder or allocate dated/suffixed output directories.
  Bind the actual input/project/output once and reuse them across all stages.
- **PKBASE_ROOT:** explicit user-supplied `--pkbase`, otherwise `PKBASE_PATH`, then
  `~/PKBase`. Verify candidates are actual, accessible directories; never create a
  base automatically. An explicit invalid path is an error, not permission to silently
  fall back. Do not infer PKBase from an Obsidian vault path. Resolve an explicit relative
  `--pkbase` against `PROJECT_ROOT`, not the review folder.
- **VAULT_ROOT:** a user-specified or known classic Obsidian vault, used only for an
  explicitly requested copy of completed drafts, not for PKBase resolution.

| Option | Contract |
|--------|----------|
| `--input <path>` | Optional review JSON; fixed default path as above, no historical discovery |
| `--out <directory>` | Optional output under `PROJECT_ROOT/docs/research-literature-summary`; default that fixed directory |
| `--phase prepare\|synthesize-input\|finalize` | Optional phase, default `prepare` |
| `--project-root <directory>` | Optional project root; defaults to current working directory, also resolves relative input/output paths |
| `--pkbase <directory>` | Optional explicit accessible PKBase directory |
| `--max-chars <integer>` | Optional source-text limit, default `100000`; truncation must remain visible |

Use `--out`, not a vault-specific output flag. Quote paths, especially on Windows.
Use identical input/output/root/base options for all three CLI phases.

### Current-material updates and content bindings

The fixed output folder intentionally holds this project's current materials. Preparation
updates contexts and the manifest; newly generated paper/overview drafts and finalized
aggregates update their assigned current files. Preparation does not erase old drafts;
their mere existence is not evidence of freshness. Do not automatically move or delete
user-owned historical files/folders, or treat unlisted leftover paper files as this corpus.
After a review/context/paper update, disclose stale downstream summaries, pending choices,
proposals, and review approvals; only matching current bindings may resume. Never reuse a
previous candidate confirmation or score as approval of changed inputs.
Before replacing approved current material, preserve its exact bytes, approval and
explicit immutable revision references. A newly prepared/finalized draft does not
replace the prior accepted anchor's authority; it awaits its own result decision.

Canonical JSON SHA256 in this workflow means SHA256 of UTF-8
`json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`, matching
the bundled `review_digest` helper. The manifest's `input_sha256` binds the actual review,
and each task's `context_sha256` binds the entire actual prepared context. Paper children
copy the task-provided hash verbatim, not a digest reconstructed from selected fields.

## Evidence contract

Respect source selection in the input's `enabled_sources` and `source_status`.
Disabled sources MUST NOT be probed or downloaded; absent legacy source-selection fields
permit those sources. Explicit `--pkbase` authorizes reading PKBase context.
`source_metadata.pkbase.base_path` can resolve the provenance of a retained `pkbase_page`
or PDF, but is not an invitation to discover unrelated vaults.

Preparation grounds each paper in this order:

1. Read an existing `pkbase_page` first, when authorized and accessible. Preserve its
   path/text for grounding and cross-links; do not create a duplicate permanent page.
2. Extract a local `pdf_path` with `pypdf` or PyMuPDF. Resolve relative `raw/` paths
   against a known PKBase directory, and other relative PDFs against the input directory
   or project root. Never invent an existing path.
3. If no useful local PDF text is available and Web is allowed, use an arXiv ID/URL with
   the existing `research-daily-ideas/scripts/download_paper_sources.py` downloader.
   Its `process_paper(paper, date_dir, timeout, max_chars)`, `_find_main_tex`, and
   `_extract_latex_text` provide source retrieval/extraction; it also supports figure
   extraction/rasterization. Normalize an explicit `arxiv_id` into a downloader URL
   because its ID parser uses URLs. Prefer actual LaTeX/PDF text. A downloader
   `text_dump` can be an abstract fallback and is not automatically full-text evidence.
4. Retain available notes or abstracts when full text is unavailable; otherwise retain
   metadata alone. Preserve the whole original record, including relevance,
   `source_metadata.zotero` annotations, and other user notes.

Keep figure metadata, original captions, and verified embeddable paths. Missing extractors,
download failures, inaccessible sources, and truncation belong in the evidence warnings
and the resulting analyses, not only terminal logs. No networking when Web is disabled.

The four evidence levels are **`full-text`**, **`pkbase-note`**, **`abstract-only`**, and
**`metadata-only`**. Use the best actual evidence available, not the intended source.
Downgrade honestly when extraction/download fails or only notes/an abstract remain.
Metadata-only analyses are valid but must state that evidence is insufficient; they must
not claim methods, results, or contributions unavailable in the record.

## Workflow

### Step 1: Prepare evidence and task inputs

Run the bundled script:

```bash
python "<SCRIPT_PATH>" --project-root "<PROJECT_ROOT>" --input "<INPUT_JSON>" --out "<OUT_DIR>" --phase prepare
```

Add `--pkbase` or `--max-chars` when applicable. Always pass the resolved project/input/output
for a bound handoff; unbound direct invocations may use defaults. Read the exit status and warnings.
Preparation writes evidence and task inputs only, not placeholder analyses or overview
drafts:

- `analysis_manifest.json`: `schema_version: 2`, `input_path`, canonical
  `input_sha256`, `out_dir`, `tasks`, `overview_context_path`, `overview_path`, and
  `overview_result_path`.
- Each manifest task: `paper_id`, `context_path`, `analysis_path`, `result_path`,
  `evidence_level`, and canonical `context_sha256`.
- `contexts/<safe-paper-stem>.json`: `paper` (the whole original record),
  `review_topic`, `derived_facets`, `review_summary`, `pkbase_page_path`,
  `pkbase_page_text`, `source_text`, `source_path`, `source_kind`, `evidence_level`,
  `source_truncated`, `figures` (list), and `evidence_warnings` (list).
- `overview_context.json`: `review` (the whole input), `tasks`, and `overview_path`.
  This initial context is not synthesis-ready: preparation does **not** record a
  completed-paper digest. `synthesize-input` replaces it only after validating actual
  paper outputs.

The deterministic safe stem combines a sanitized paper ID and a short digest to prevent
collisions, path traversal, and Windows reserved names. Preparation and finalization use
the same naming. Duplicate paper IDs are errors; every unique input paper must remain
represented. Use manifest paths verbatim instead of reconstructing filenames.
Manifest/context path references are absolute; links in Markdown outputs are portable
and relative.

If preparation fails, diagnose the concrete input/path/dependency issue and report it.
Do not delegate against missing or fabricated context. Re-preparing updates current
contexts/manifest but must not replace user-written paper or overview drafts. Validate
retained drafts against the new bindings and regenerate stale outputs at their assigned
paths before continuing.

### Step 2: Delegate one host subagent per paper

Read the manifest and launch exactly one paper-analysis subagent for each task. Use the
host's subagent tool, with bounded parallel batches of **at most 32** active children
(or a lower host limit). Do not call an external model from Python. If host delegation
is unavailable, report that prerequisite as a blocker; do not substitute API calls.

Give each child the context file reference, exact task `context_sha256`, and its unique
`analysis_path` and `result_path`, together with the paper output contract below. Do not paste a giant
corpus into prompts. Each child reads its assigned context and writes **only** its
assigned Markdown and JSON sidecar, without editing shared aggregates, the overview,
scripts, or permanent PKBase pages. An existing `pkbase_page` must be read/linked when
authorized; deepen the draft from that evidence instead of duplicating the source page.

Wait for each batch, inspect actual success/failure results, and account for every task.
Do not launch synthesis until all paper agents have succeeded and their required outputs
are present and usable. A failed child or missing sidecar is not a completed paper.
Resolve failures against the same assigned paths and then recheck their outputs; never
silently drop a paper. Existing files alone are not evidence of successful resume:
inspect content, IDs, evidence levels, and the complete output contract including the
actual context/task/sidecar hash match. Same paper IDs do not make old drafts current.

#### Required per-paper Markdown

Start with `# <original title>` (use `# 未提供标题` only if the record has no title).
Narrative is fluent Chinese; original titles, author names, venues, and figure captions
remain unchanged. English topic tags are permitted. Before the first section, use the
canonical Chinese metadata labels `作者`, `年份`, `发表场所`, `领域`, `标签`,
`质量评分`, and `证据等级`. Unknown metadata stays explicitly unknown.

Include all these second-level sections in the exact order below, with nonempty bodies:

```markdown
## 一句话总结
## 研究背景
## 研究问题
## 研究动机
## 方法机制
## 主要贡献
## 实验与结果
## 局限性
## 可迁移思路
## task_figure
## methodology
## 证据与关联
```

Explain the problem, motivation, mechanisms, contributions, experiments/results,
limitations, and transferable ideas only to the extent supported. `task_figure` describes
the task, inputs, outputs, and verified figures. `methodology` describes the actual
steps/mechanisms and verified figure references. Embed/link figures only when paths and
captions are verified; say explicitly when figures, data, or formulas are unknown.
In `证据与关联`, cite available source pages/sections, link any existing PKBase page,
state evidence level/truncation/warnings, and distinguish user annotations from the
authors' claims. Do not present an inference as a reported experimental result.

#### Required JSON sidecar and quality rubric

Write UTF-8 JSON at the manifest's `result_path`, not `{}` or a Markdown code block:

```json
{
  "paper_id": "<exact manifest paper_id>",
  "domain": "<non-empty domain string>",
  "quality_score": null,
  "evidence_level": "<exact manifest evidence_level>",
  "context_sha256": "<exact task-provided context_sha256>"
}
```

All five fields are required. Copy `context_sha256` exactly from the assigned manifest
task; it must match the entire actual context's canonical digest. An older four-field
sidecar or a same-ID result from a different context is stale, not an accepted fallback.

`domain` must be non-empty; use an explicit unknown domain when evidence cannot classify
it. `quality_score` is a number from `0` through `10`, or `null` when evidence is
insufficient. Explain the assessment in the Markdown. Assess novelty, mechanism clarity,
experimental support, reproducibility, and treatment of limitations using concrete
evidence. The assessment is subjective, not a citation count, impact fact, venue ranking,
or proof of correctness. Do not invent a numeric score merely to fill the field.
For interpretable reporting, `[0,4)` means weak support/substantial weaknesses,
`[4,7)` means mixed or moderate support, and `[7,10]` means strong support on those
dimensions; `null` is unscored, not zero.

### Step 3: Validate synthesis inputs, then synthesize

After all paper tasks succeed, run the bundled script with the same bound options:

```bash
python "<SCRIPT_PATH>" --project-root "<PROJECT_ROOT>" --input "<INPUT_JSON>" --out "<OUT_DIR>" --phase synthesize-input
```

This phase validates every actual paper Markdown/sidecar and its context binding; it
does not call a model or write a fake overview. It then writes `overview_context.json`
with `review`, `tasks`, `input_sha256`, `paper_snapshots`, `papers_sha256`,
`overview_path`, and `overview_result_path`. In manifest order, each snapshot contains
`paper_id`, task `context_sha256`, `analysis_sha256` (SHA256 of the actual Markdown file
bytes), and `result_sha256` (canonical JSON SHA256 of the actual sidecar dictionary).
`papers_sha256` is the canonical digest of the **object** `{"papers": paper_snapshots}`,
not a hash of the bare list or a concatenation of file hashes.

Only after this phase succeeds, the parent or a dedicated synthesis subagent reads
the refreshed `overview_context_path` **and actual per-paper Markdown/sidecars**, then
writes `overview_path` (normally `overview_summary.md`) and `overview_result_path`
(normally `overview_summary.analysis.json`). A synthesis child writes only those two
assigned outputs, not paper files or aggregates. The parent integrates and reviews
coverage across every current input paper.

The required UTF-8 overview sidecar is:

```json
{
  "input_sha256": "<copy exact refreshed overview_context.input_sha256>",
  "papers_sha256": "<copy exact refreshed overview_context.papers_sha256>"
}
```

Copy both bindings verbatim; do not guess or recompute them from a subset of papers.
If any paper/context/input changes after `synthesize-input`, refresh that phase and
regenerate the overview and sidecar against the new complete snapshot before finalizing.

Use Chinese narrative and exactly these second-level sections in order, each with a
nonempty body (state insufficient evidence instead of leaving a section blank):

```markdown
## 检索分支
## 领域定义与子方向
## 核心科学问题
## 数据集
## 方法谱系
## 评价指标
## 开放研究缺口
## 证据与覆盖局限
```

Cover all landscape dimensions in the goal. Cite paper IDs and portable relative
analysis links for assertions; distinguish review-derived retrieval branches from
findings grounded in the analyses. Describe dataset availability/licenses/accessibility
and metric formulas only when evidenced; explicitly label unknowns. Method families
must explain mechanisms, not just enumerate names. Report source restrictions,
downgrades, truncation, and coverage limits. For an empty corpus, write an honest no-data
overview with the required sections; do not invent a landscape.

### Step 4: Finalize and integrate

Run the same bundled script and options against the prepared manifest:

```bash
python "<SCRIPT_PATH>" --project-root "<PROJECT_ROOT>" --input "<INPUT_JSON>" --out "<OUT_DIR>" --phase finalize
```

Finalization consumes `analysis_manifest.json` and requires **every** assigned paper
Markdown, five-field JSON sidecar, refreshed synthesis context, overview, and overview
sidecar. It validates the current review digest, actual context/task/sidecar digests,
the ordered actual paper-output snapshot, and the overview's `input_sha256` and
`papers_sha256`. It also validates IDs, evidence levels, quality types/range, titles,
metadata, and required Markdown sections in order with nonempty bodies. Empty files,
`{}`, missing hashes, and stale same-ID results do not qualify. Missing/failed/invalid
results are errors with a nonzero CLI exit, never automatically skipped as complete.

Only after validation does it write `all_papers_analysis.md` and `aggregate_report.md`.
Statistics use real input roles, years, venues, sidecar domains and quality scores,
quality buckets `[0,4)`, `[4,7)`, `[7,10]` plus unscored, and evidence levels. Show unknown
bins and link every paper. Use portable relative links throughout the output.
Finalization can be repeated without replacing the user-written analyses or overview.
The parent owns all integration/checks after children finish; children do not run shared
builds, tests, linters, formatters, or aggregate-generation commands mid-flight.

### Step 5: Report real completion or failure

Claim completion only after preparation, every paper task, validated synthesis-input
preparation, synthesis with its sidecar, and finalization have actually succeeded.
Report the real input/analyzed paper count (including zero),
the output directory, links to the overview, paper index, and statistical report, and a
short evidence-grounded overview highlight. Disclose evidence downgrades, unscored
papers, truncation, and material source limitations.
Technical completion may be reported before user acceptance. Report the owner-state
status separately; no downstream offer or ready approved landscape exists yet.

If a stage fails, report the stage, affected paper IDs/paths, actual error or missing
prerequisite, and which outputs really exist. Do not call partial or stale aggregates
complete, fabricate successful execution, or claim any filing/site rebuild not performed.
Finish reachable work and resolve actionable failures before handing off a blocker.

If explicitly requested for a classic (non-PKBase) Obsidian vault, copy the completed
output folder to `{VAULT_ROOT}/ResearchPapers/{review_topic}/`, preserving relative links
and the originals. Otherwise leave drafts in `OUT_DIR`. Optional permanent PKBase
filing requires its own explicit scope. Do not suggest advancement to ideas or a paper
stage before the completed-summary result gate; the adjacent main-stage offer is
`research-ideas`, only after approval and the binding checks below.

### Completed-summary result gate

After successful finalization, present the actual overview, full paper index and
aggregate report with evidence levels, missing sources, truncation, unsupported claims,
coverage limits and unresolved gaps. Ask whether the user accepts **this completed
evidence landscape and its stated limits** as the anchor for subsequent research ideas.
This approval is separate from the earlier corpus/input adoption, authorization to
prepare summaries and authorization to enter ideas.

Build the established ordered `summary_artifacts` byte inventory, with resolved absolute
paths and SHA256 of each actual file's bytes, in exactly this order:

1. `analysis_manifest.json`.
2. For each task **in manifest order**: `context_path`, `analysis_path`, `result_path`.
3. `overview_context_path`, `overview_path`, `overview_result_path`.
4. `all_papers_analysis.md`, then `aggregate_report.md`.

`summary_snapshot_sha256` is SHA256 of UTF-8 canonical JSON of that ordered
`[{path,sha256}]` list (`sort_keys=True`, `ensure_ascii=False`, `separators=(",", ":")`).
Exclude mutable `SUMMARY_STATE.json` and producer approval states from this inventory:
no state hashes itself or the snapshot it approves. Keep the separate canonical review,
context/task, `paper_snapshots`, `papers_sha256` and overview-sidecar semantic checks;
a matching byte inventory does not replace them.

Persist actual `papers_sha256`, `summary_artifacts`, `summary_snapshot_sha256` in
`SUMMARY_STATE.json` alongside its input/project/source approval bindings, and:

```json
{
  "status": "awaiting_summary_approval",
  "summary_approval": {
    "approved": false,
    "summary_snapshot_sha256": "<actual ordered snapshot digest, or null until known>",
    "confirmation_reference": null
  }
}
```

Only actual unambiguous user acceptance of this exact presented completed result sets
`summary_approval.approved: true`, `status: summary_approved` and the real message/turn
reference or exact confirmation text/context. Re-read every snapshot file and upstream
approval/adoption binding before committing. Refusal sets `declined`, keeps approval
false and stops advancement; change requests require revision and renewed presentation.
Any bound artifact, source scope or input approval change sets `stale`, preserves the
old accepted revision/confirmation and invalidates dependent offers. No silence,
timeout, autonomous mode, successful finalize, review score or prior consent is approval.
Do not publish a ready anchor or offer any next research stage while pending, declined
or stale. The host records real acceptance; the CLI's success cannot record it.


### Next Step: Optional [research-ideas](../research-ideas/SKILL.md) handoff

Offer this only after complete finalization **and** the matching completed-summary
user approval. Bind the same review JSON used for preparation and the actual completed
fixed summary directory; do not independently
discover historical review/summary pairs. Check the manifest's `input_path` and canonical
`input_sha256` against `INPUT_JSON`, all context/task/paper sidecar bindings, the refreshed
ordered paper snapshot and overview sidecar's `input_sha256`/`papers_sha256`, and the
overview/index/report. Missing, stale, mismatched, or unusable artifacts stop the handoff:
report exact paths and prerequisites rather than inventing grounding or substituting data.
Read the exact `SUMMARY_STATE.json`: actual project/input/output paths and upstream
approval/adoption bindings must match; `summary_approval.approved` must be true with a
real `confirmation_reference`, and its `summary_snapshot_sha256` must equal both the
state's and the freshly computed complete ordered snapshot. A known refused, pending,
missing or stale approval stops the offer regardless of usable technical outputs.

For this handoff, also bind `summary_artifacts` as an ordered list of `{path,sha256}`
for the resolved manifest, every task's context/Markdown/sidecar in manifest order,
overview context, overview Markdown, overview sidecar, index, and aggregate report.
Each entry hashes exact file bytes. `summary_snapshot_sha256` is the canonical JSON
digest of that ordered list. Revalidate this complete snapshot on acceptance and
candidate selection: an edited overview body or aggregate is a changed summary even
when its input/paper sidecar hashes remain the same.

Replace any older unresolved recommendation with this conversation `NEXT_SKILL_HANDOFF`:

```json
{
  "from_skill": "research-literature-summary",
  "to_skill": "research-ideas",
  "input_json": "<actual absolute INPUT_JSON>",
  "input_sha256": "<actual current manifest input_sha256>",
  "summary_dir": "<actual absolute completed SUMMARY_DIR>",
  "papers_sha256": "<actual current overview sidecar papers_sha256>",
  "summary_snapshot_sha256": "<canonical digest of the ordered summary_artifacts list>",
  "summary_artifacts": [{"path": "<actual absolute artifact path>", "sha256": "<exact file byte SHA256>"}],
  "summary_state_path": "<actual absolute SUMMARY_STATE.json>",
  "summary_state_sha256": "<exact approved owner-state file-byte SHA256>",
  "project_root": "<actual absolute PROJECT_ROOT>",
  "docs_root": "<actual absolute PROJECT_ROOT/docs>",
  "invocation": "/research-ideas input: \"<actual absolute review JSON>\" summary: \"<actual absolute summary directory>\" project: \"<actual absolute project root>\"",
  "artifacts": [
    {"role": "literature-review", "path": "<actual absolute review JSON>", "sha256": "<exact file byte SHA256>"},
    {"role": "summary-artifact", "path": "<actual absolute consumed summary file>", "sha256": "<exact file byte SHA256>"},
    {"role": "summary-approval-state", "path": "<actual absolute SUMMARY_STATE.json>", "sha256": "<exact state file byte SHA256>"}
  ],
  "status": "awaiting_confirmation"
}
```

Add `ideas_overview` only when the user supplied an overview path. Preserve direct
user-supplied idea text as intent when present; never manufacture or require an overview.
Expand `artifacts` to include the review, every file in `summary_artifacts`, the approved
summary owner state, the consumed corpus state when present, and any supplied overview.
Keep their byte hashes separate from canonical JSON digests. The `research-ideas`
receiver must verify this exact owner's actual `summary_approval` and upstream bindings,
not merely the presence of a state file. Never include these states in the snapshot.
Carry direct user idea text verbatim as `user_idea` when present and include it in the
visible invocation context; do not let a later context or omitted file silently replace
that intent. The `invocation` must include all actual explicit optional arguments shown
to the user. Placeholders above are examples, never values in a real pending offer.
Render the actual paths in this **chat skill invocation**, not a shell command:

```text
下一步建议：research-ideas（有用户想法则优化；没有想法则生成 4–6 个候选，逐项分析并排序，等你另行选择后才细化与评审）
推荐调用：/research-ideas input: "<actual absolute review JSON>" summary: "<actual absolute completed docs/research-literature-summary>" project: "<actual absolute project root>"
是否现在执行？回复“可以”或“继续”即可授权上述下一步；没有用户想法时，这只授权生成候选，不代表选中推荐第一名，也不授权自动细化或评审。回复“暂时不要”则停在本次总结结果。
```

Append `ideas-overview: "<actual supplied absolute overview path>"` only when supplied.
An explicit invocation requests that stage without a repeated entry confirmation; it
does not bypass summary approval or genuine equivalent adoption of imported inputs
in the receiving ideas state. Do not fabricate an upstream approval history.
A direct affirmative to the unique latest unresolved offer authorizes only the bound
ideas action described above: interpret the complete reply; `可以，但先别执行`, quoted
examples, unrelated approval, or bare assent without an unambiguous offer are not
consent. Earlier assent to review or summary never authorizes ideas. On consent set
`accepted`, load `research-ideas` through the host's normal skill loader, and execute
with these exact bound inputs without asking for the same handoff permission again.
Do not create backend-specific commands. Before writes, verify every `artifacts` byte
hash, all canonical source/summary bindings, and the actual producer summary approval;
changed or refused approvals stop advancement, and changed inputs set `stale` and require
fresh grounding and confirmation. Set `running`, then `completed` only for the actually
authorized stage or `failed` on failure. Silence, timeout or autonomous mode grants no
next step.
A refusal sets `declined` and stops the chain. Non-pending anchors do not authorize
repeat executions, experiment execution, or PKBase filing.

When no user idea is supplied, completion of this authorized stage means 4–6 distinct,
evidence-grounded candidates with visible IDs, full analyses and ranked comparison,
saved directly as `docs/research-ideas/CANDIDATE_PROPOSALS.md` and presented in chat.
`CANDIDATE_SELECTION.json` / `REVIEW_STATE.json` remain `awaiting_selection` with no
selected ID or confirmation. Do not freeze an anchor, design a full method, invoke
reviews, overwrite an existing `FINAL_PROPOSAL.md`, or call downstream skills. An
existing final belongs to its previous selection and is not current approval.
Prompt separately: `请回复候选ID（例如“选 C3”），或明确说“采用推荐第一名”；确认后才细化方法并开始独立评审。`
A bare `可以`/`继续`/`yes` at this multi-choice gate does not select a winner; ask which
candidate or whether the user explicitly adopts the displayed recommendation. Only a
unique explicit choice mapped to the unchanged current candidate/source/summary
bindings authorizes the selected-route design and fresh review. Changed bindings require
a fresh gate; declines stop, ambiguous/multiple choices require clarification. With a
supplied user idea, preserve that intent and use the skill's optimization workflow;
do not impose this no-idea candidate-selection gate.
If a direct invocation changes the input, summary directory, project, or supplied ideas,
replace the old pending recommendation before execution. Echo the actual resolved
invocation at execution start; never retain an obsolete offer that could run another corpus.

### Step 6: File results into PKBase (optional — explicit user request)

Resolve an accessible `PKBASE_ROOT` using the path rules above; an Obsidian path is not a
PKBase fallback. Read the `wiki-pk-base` skill and the chosen base's `SCHEMA.md` before
filing. Evidence preparation is read-only toward the base; permanent filing is separate.

1. **Classify:** pick the closest existing domain/topic per `SCHEMA.md`; register a
   genuinely new one in SCHEMA first.
2. **Landscape → comparison page:** find the topic comparison page already created by
   `research-literature-review` under `wiki/comparisons/<domain>/<topic>/`. If present,
   extend it with the deeper landscape (method families, evidenced metric formulas,
   open gaps) and bump `updated`. Otherwise create
   `wiki/comparisons/<domain>/<topic>/<topic-slug>-landscape-<DATE>.md` following
   `wiki-pk-base` comparison-page conventions: frontmatter `sources:`/`created`/`tags`,
   taxonomy tags only, and at least two `[[wikilinks]]`. Preserve evidence limitations.
3. **Per-paper → selected source pages:** when selection is not supplied, ask which
   papers to file; suggest the highest-relevance papers and/or those with local PDFs.
   Reuse and deepen any existing `pkbase_page`, never duplicate it. Follow the
   `wiki-pk-base` `add` flow: stage PDFs under `raw/papers/<domain>/<topic>/` (copy,
   never move; `YYYYMMDD-arxiv-<id>.pdf` naming where applicable); write source summaries
   at `wiki/sources/<domain>/<topic>/<paper-slug>.md` at the SCHEMA depth, with the
   required ASCII diagram and verified `![[figure]]` embeds for rasterized figures;
   extract 2–5 concept pages per SCHEMA thresholds. If this touches 10+ existing pages,
   confirm scope first. Missing PDFs/figures remain explicitly missing.
4. **Navigation + site:** update `index.md`, append to `log.md` using
   `## [<DATE>] ingest | Literature summary: <review_topic>` and the page list, and
   rebuild the site. Prefer `site/rebuild_site.py` when present; otherwise regenerate
   `site/data.js` per `wiki-pk-base`. Report `site rebuilt (N pages, M raw files)` only
   with actual counts and successful rebuild evidence; otherwise report the failure.

## Output files

Use manifest-provided paths; `<safe-paper-stem>` is not the raw paper ID.

| File under `OUT_DIR` | Writer and content |
|----------------------|--------------------|
| `analysis_manifest.json` | Python prepare: schema version 2, actual review digest, paths, every paper task/context digest, evidence levels |
| `contexts/<safe-paper-stem>.json` | Python prepare: whole paper record and grounded evidence context |
| `overview_context.json` | Python prepare initializes review/task paths; synthesize-input validates papers and refreshes actual input/paper snapshot digests and overview paths |
| `sources/` | Python prepare: retained/downloaded source evidence and verified figures when available |
| `papers/<safe-paper-stem>.md` | Assigned paper subagent: Chinese analysis with required sections |
| `papers/<safe-paper-stem>.analysis.json` | Assigned paper subagent: paper ID, domain, quality score, evidence level, exact task context_sha256 |
| `overview_summary.md` | Parent/synthesis subagent: landscape grounded in all current completed analyses |
| `overview_summary.analysis.json` | Parent/synthesis subagent: exact input_sha256 and papers_sha256 from refreshed overview_context |
| `all_papers_analysis.md` | Python finalize: validated aggregate/index linking all papers |
| `aggregate_report.md` | Python finalize: real role/year/venue/domain/quality/evidence statistics |
| `SUMMARY_STATE.json` | Host: input approval/adoption, ordered output snapshot and completed-summary user acceptance; excluded from its approved snapshot |
| (explicit filing) `wiki/comparisons/...`, `wiki/sources/...` in PKBase | Durable pages following Step 6, not preparation outputs |

## Changes in 1.8.0

- Added verified corpus-owner approval or real standalone input adoption before prepare,
  and a separate completed-landscape result gate before the adjacent ideas offer.
- Added host-owned `SUMMARY_STATE.json` and exact producer/consumer state bindings while
  preserving the ordered full summary snapshot and all semantic provenance validation.
- `summarize_review.py`, its `prepare` / `synthesize-input` / `finalize` CLI options,
  manifest, context and result-sidecar schemas, source permissions and PKBase resolution
  are unchanged. These user-decision gates are host instructions, not CLI enforcement.
