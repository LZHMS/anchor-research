---
name: research-ideas
description: |
  Use matching approved literature-review and literature-summary outputs to generate 4–6 ranked research candidates and await explicit route selection when no idea is supplied, or optimize supplied intent. Separately obtain approval of the exact drafted problem anchor before full synthesis and approval of the exact independently reviewed proposal before replacing current exports or offering planning; preserve prior approved anchors and immutable proposal/review evidence.
  Trigger: "research ideas", "提出研究方案", "基于文献生成新idea", "打磨idea", "refine my approach", "细化研究方案", "decompose this problem"
version: 6.0.0
author: Zhihao Li
license: MIT
argument-hint: "input: docs/research-literature-review/research_foundation_review.json | summary: docs/research-literature-summary | ideas-overview: <optional-user-file> | project: <current-project-root> | select: <existing-candidate-ID>"
metadata:
  tags: [research, ideas, proposal, candidates, selection-gate, literature, review, planning]
  category: research
  related_skills: [research-literature-review, research-literature-summary, research-experiment-plannning]
---

# Research Ideas: Literature-Grounded Proposal and Independent Review

Resolve and execute **$ARGUMENTS** using the host's normal skill loader and subagent tools. This is one generic agent workflow; it needs no special CLI, reviewer profile, model selection, or model API call.

## Purpose and boundaries

Produce a focused **problem → mechanism → minimal claim validation** proposal that an engineer can implement. BOTH the structured literature review and its completed matching summary are required grounding. A user-written idea is optional:

- **`literature-driven`**: when no user idea is supplied, derive 4–6 genuinely distinct NEW candidate proposals from reviewed gaps and actual paper evidence, display a ranked recommendation with concrete analysis, and **STOP awaiting explicit selection**. Recommendation is not authorization to choose, freeze an anchor, design a full method, or review.
- **`optimize-user-idea`**: when an idea is supplied, preserve the user's problem, intent, non-goals, and constraints while improving mechanism, specificity, evidence-backed positioning, and feasibility.

Absence of `ResearchIdeasOverview.md` is never a blocker and never a request that the user write one. Missing literature is a different, concrete prerequisite failure. Do not replace research with speculative claims, fabricate results, or silently switch to another topic because it is easier to propose a method there.

Write narrative outputs in Chinese. Preserve original paper titles, author names, venues, identifiers, and faithful technical notation. Keep one dominant contribution and at most one supporting contribution. Prefer the smallest adequate intervention, reuse strong components, and avoid fashionable primitives unless their exact role addresses the bottleneck.

This skill plans methods and 1–3 core validation blocks. It does not implement code, launch training, build, test, lint, format, permanently file to PKBase, or automatically run another skill.

### Human anchor authority

Follow the [shared anchor-gate contract](../research-shared-references/anchor-gates.md); the inline rules here remain mandatory if that reference is unavailable. Stage entry, candidate choice, problem-anchor approval, final-proposal approval and downstream entry are different decisions. No reviewer, score, filename, silence, timeout or autonomous mode can supply a user's missing approval. Present actual content, limitations, affected paths and SHA-256 bindings, persist the pending gate with `approved=false`, and record only an actual unambiguous reply to that exact decision (`confirmation_reference`: real message/turn reference, or exact confirmation text with context). Re-read bound bytes before committing. Changes stale the affected approval; preserve the prior approved revision and ask again. A generic invocation cannot approve future artifacts.

## Arguments and project-local paths

These are **chat skill arguments**, not shell flags:

| Argument | Default / contract |
|---|---|
| `input` | Exact review JSON; otherwise the accepted summary handoff's `input_json`; otherwise `DOCS_ROOT/research-literature-review/research_foundation_review.json` |
| `summary` | Exact completed summary directory; otherwise the accepted handoff's `summary_dir`; otherwise `DOCS_ROOT/research-literature-summary` |
| `ideas-overview` | Optional explicit user overview file; otherwise an accepted handoff's supplied `ideas_overview`; otherwise use `DOCS_ROOT/ResearchIdeasOverview.md` only if it actually exists and is nonempty |
| `project` | Explicit path, otherwise an accepted handoff's `project_root`, otherwise the current working project directory |
| `max-rounds` | `5`; positive integer, maximum independent review attempts |
| `threshold` | `9`; finite number in `[1, 10]`, subject to all non-score readiness gates |
| `constraints` | Optional user resource, data, time, deployment, scope, or venue constraints; preserve exact intent |
| `select` | Optional explicit ID from an existing matching pending candidate set; resumes selection only, never creates candidates and chooses one in the same invocation |

Direct user-supplied idea text also counts as intent, even without a file. Merely naming the literature topic, giving a project path, or setting resource constraints does not supply a method idea. A generated proposal from a previous run is not automatically user intent; use it as intent only if the user explicitly designates it for optimization.

When resuming a pending selection, resolve omitted input/summary, original mode/intent, constraints and loop settings from that exact saved binding, not fresh defaults. Explicitly changed arguments must still match or invalidate the set. Process selection replies against the pending table before interpreting a unique candidate title as newly supplied idea text; selecting a generated candidate does not switch to optimization mode.

Resolve relative arguments against `PROJECT_ROOT`, not the skill installation or review folder. Installed skill assets are read-only locations, separate from project outputs.

- `PROJECT_ROOT`: explicit `project`, otherwise an accepted handoff's exact `project_root`, otherwise the current working project directory. Pass it explicitly to downstream tools; a changed working directory cannot move a confirmed workflow to another project.
- `DOCS_ROOT = PROJECT_ROOT/docs`.
- `FOUNDATION_OUTPUT_JSON`: the resolved review file, by default `DOCS_ROOT/research-literature-review/research_foundation_review.json`.
- `SUMMARY_DIR`: the resolved completed summary directory, by default `DOCS_ROOT/research-literature-summary`. A supplied path must be inside this project's summary subtree and prove the exact input/content binding; folder names are not evidence.
- `IDEAS_DIR = DOCS_ROOT/research-ideas`. All skill outputs are files directly in this fixed directory.

There is no per-execution directory allocation or newest-file discovery. Default outputs intentionally update this project's current material. Explicit missing files, invalid paths, or unavailable accepted-handoff artifacts are errors, not permission to substitute other inputs. Bind actual paths plus content digests, not folder names or timestamps. Do not search wildcard or dated historical directories, move/delete user-owned history, write alongside installed skills, or write into upstream outputs.

At execution start echo the actual resolved invocation, project root, review file, summary directory, mode, and intended output directory. Resolve scope from these real inputs rather than asking the user to repeat tool-accessible information.

## Confirmed upstream entry

An explicit `/research-ideas ...` request authorizes this skill only; no second confirmation is needed. The upstream [research-literature-summary](../research-literature-summary/SKILL.md) skill may instead offer a specific optional `NEXT_SKILL_HANDOFF`:

```json
{
  "from_skill": "research-literature-summary",
  "to_skill": "research-ideas",
  "input_json": "<actual absolute review JSON>",
  "input_sha256": "<actual canonical review JSON digest>",
  "summary_dir": "<actual absolute completed summary directory>",
  "papers_sha256": "<actual overview sidecar papers_sha256>",
  "summary_snapshot_sha256": "<canonical digest of the ordered summary_artifacts list>",
  "summary_state_path": "<actual absolute SUMMARY_STATE.json>",
  "summary_state_sha256": "<actual owner state file byte SHA256>",
  "summary_artifacts": [{"path": "<actual absolute summary file>", "sha256": "<exact file byte SHA256>"}],
  "project_root": "<actual absolute project root>",
  "docs_root": "<actual absolute PROJECT_ROOT/docs>",
  "invocation": "/research-ideas input: \"<actual absolute review JSON>\" summary: \"<actual absolute summary directory>\" project: \"<actual absolute project root>\"",
  "artifacts": [
    {"role": "literature-review", "path": "<actual absolute review JSON>", "sha256": "<exact file byte SHA256>"},
    {"role": "summary-artifact", "path": "<actual absolute consumed summary file>", "sha256": "<exact file byte SHA256>"},
    {"role": "summary-state", "path": "<actual absolute SUMMARY_STATE.json>", "sha256": "<exact file byte SHA256>"}
  ],
  "status": "awaiting_confirmation"
}
```

Add `ideas_overview` only when the user supplied that path, and pass it as
`ideas-overview` on acceptance; do not drop it merely because the default file is absent.
Preserve any direct user idea text explicitly through the handoff and record it in the
anchor/context; generated paper analyses are not user idea intent. Do not invent an
overview file.

For this handoff, `artifacts` enumerates the review, every actual `summary_artifacts`
file, its approval owner state and any supplied overview. Before writes, validate each exact file byte SHA256,
the packet's project/docs/input/output paths and invocation, then all Phase 0 canonical
review/summary bindings. An edited or missing bound file marks the offer `stale`;
report the changed binding and wait for a refreshed specific offer to be confirmed,
or a new direct invocation. Never substitute another summary or user idea.
Keep supplied `user_idea` verbatim as intent. Silence, timeout and autonomous mode do
not authorize this stage or a downstream stage; unchanged interrupted work resumes
only its already authorized scope.

A direct affirmative such as `可以`, `继续`, or `yes` accepts only the unique latest unresolved specific upstream offer. Interpret the whole reply: quoted assent, unrelated approval, `可以，但先别执行`, ambiguity, or assent without a pending bound offer is not authorization. Refusal sets `declined` and stops. On acceptance set `accepted`, revalidate the exact bound artifacts, then `running`. In literature-driven mode this authorizes **candidate generation only**: reaching `awaiting_selection` fulfills that upstream offer, not full proposal completion. It does not select the recommended candidate. In optimization mode mark `completed` only after genuine proposal output completion; prerequisite/execution failure is `failed`. A consumed offer cannot authorize repetition. An explicit changed invocation replaces the older pending offer; never retain stale consent to another corpus.

Neither summary consent nor ideas consent authorizes downstream planning, training, expanded source access, or permanent filing. Missing prerequisites must be reported by exact path and reason. Offer the appropriate upstream skill with a separate specific confirmation rather than executing it automatically.

## Phase 0 — Validate grounding and choose the mode

Complete these checks before method synthesis or a review:

1. Read the actual selected review JSON, including its topic, paper records, `derived_facets`, `review_summary`, open gaps wherever represented, and source policy. A malformed or empty corpus cannot support a literature-driven proposal; state the missing evidence rather than generating a generic idea.
2. Read `SUMMARY_DIR/analysis_manifest.json`. Its resolved `input_path` must equal the selected review file and `out_dir` must equal the selected summary directory. Its `input_sha256` must equal the existing summary helper's canonical digest of the parsed review: SHA-256 of UTF-8 JSON serialized with sorted keys, `ensure_ascii=False`, and separators `(',', ':')`. Reformatting the review alone is not a content change; changing review content invalidates prior summary/selection/proposal approval.
3. Confirm manifest tasks cover every unique review paper ID exactly once. Read each task's actual context, `analysis_path` Markdown and `result_path` JSON sidecar using listed paths, not guessed filenames. Each task must contain `context_sha256`, the existing helper's canonical JSON digest of its actual prepared context. Require all five sidecar fields: `paper_id`, nonempty `domain`, `quality_score` (finite `[0,10]` or `null`), `evidence_level`, and `context_sha256`. Task hash, actual context hash, and sidecar hash must match, as must paper ID/evidence provenance. Four-field legacy sidecars cannot count as complete. Empty, missing, placeholder, mismatched, stale or failed outputs stop grounding; never drop a paper to pass.
4. Read the actual `overview_path`, `overview_context_path`, the overview sidecar at overview context's `overview_result_path` (normally `SUMMARY_DIR/overview_summary.analysis.json`), `all_papers_analysis.md`, and `aggregate_report.md`. All must be nonempty, usable, and consistent with the bound task set. The upstream sequence is `prepare` → real paper agents → `synthesize-input` → real overview synthesis plus sidecar → `finalize`: `synthesize-input` validates papers and adds `paper_snapshots` and `papers_sha256` to overview context, but never fabricates an overview. The overview context and sidecar must both carry current `input_sha256` and matching `papers_sha256`. Recompute manifest-ordered `paper_snapshots` entries `{paper_id,context_sha256,analysis_sha256,result_sha256}`, where `analysis_sha256` hashes actual UTF-8 Markdown bytes and `result_sha256` hashes canonical sidecar JSON; `papers_sha256` is the existing helper's canonical digest of the **object `{"papers": paper_snapshots}`**, not the bare list. Require context's snapshots to equal these actual entries. Preparation alone lacks this completed-paper binding and is not completion. Check successful finalization/handoff when available and the full content contract. Do not rerun upstream preparation/finalization here to conceal missing work.
   Bind `summary_snapshot_sha256` as the canonical digest of an ordered list of `{path,sha256}` for the resolved manifest, every task context/Markdown/sidecar in manifest order, overview context, overview Markdown, overview sidecar, index and aggregate report; each `sha256` hashes exact file bytes. Persist the list as `summary_artifacts`. Revalidate every file and the resulting snapshot at candidate selection, checkpoint recovery and downstream acceptance. An edited summary body invalidates approval even if its review digest is unchanged.
   Read the explicitly bound `summary_state_path` (default `SUMMARY_DIR/SUMMARY_STATE.json` for direct entry) and hash its actual bytes as `summary_state_sha256`. Require matching project/docs/input paths, canonical `input_sha256`, summary directory, `papers_sha256`, ordered `summary_artifacts` and `summary_snapshot_sha256`; require `summary_approval.approved=true`, the same `summary_approval.summary_snapshot_sha256` and an actual `confirmation_reference`. Recompute the snapshot from actual files, not the state's claim. The mutable approval state is an artifact in handoffs, never part of the snapshot it approves. A completed helper, old FINAL, file existence or inherited stage-entry assent is not summary approval.
   For genuinely imported/equivalent inputs only, an actual explicit user acceptance of the presented evidence landscape, limitations and exact supplied input/constraints may instead be recorded in this skill's own `REVIEW_STATE.json` as `input_anchor_approval={approved,artifacts:[{role,path,sha256}],input_sha256,summary_snapshot_sha256,constraints,confirmation_reference}`. Require `approved=true` and matching actual bindings; do not fabricate SUMMARY_STATE, upstream execution/review, or adoption from a filename/invocation. Missing technical grounding is not waived. Preserve either producer-state binding or this actual local adoption throughout recovery and handoff.
5. Inherit each paper's evidence level, truncation, source warnings, and uncertainty. A completed abstract-only summary is usable but supports only abstract-level facts. Never upgrade abstract inference into verified architectural detail, empirical failure, or comprehensive novelty clearance.
6. Honor the review's `enabled_sources` and `source_status`. Disabled sources must not be accessed, downloaded, or probed. Use permitted retained sources for method details. Additional verification may use only authorized accessible sources, linking exact evidence. Lack of full text is an evidence limitation, not permission to fabricate details or silently change source policy.
7. Resolve optional idea intent. An explicit `ideas-overview` that is missing, unreadable, or empty is a concrete input error, not a silent switch to new-proposal mode. An absent default overview means no file intent; an empty default overview is ignored with an honest note, not a blocker. Read an existing nonempty default overview. Combine file intent with direct user idea text and explicit constraints; a clear current user amendment takes precedence, but a material unresolved conflict must be surfaced rather than selecting whichever produces a higher score.

Choose `optimize-user-idea` if usable file or direct idea intent exists; otherwise choose `literature-driven` immediately, with no request for user supplementation. If supplied intent falls outside the reviewed corpus, explain the mismatch and offer a matching upstream review or a user-approved scope decision; do not replace either the user's problem or the corpus silently.

Report all reachable missing/stale inputs together with exact paths and remediation. Without matched completed literature, stop proposal generation honestly. Never fabricate a fallback review, candidate evidence, reviewer output, or readiness result.

## Output bundle and preservation

```text
PROJECT_ROOT/docs/research-ideas/
  CONTEXT_BRIEF.md              # current grounding and intent
  CANDIDATE_PROPOSALS.md         # current alternatives and ranking
  CANDIDATE_SELECTION.json       # pending/confirmed selection binding
  PROBLEM_ANCHOR_DRAFT.md        # pending problem interpretation, never authoritative
  PROBLEM_ANCHOR.md              # current explicitly approved problem only
  anchor-N.md                   # immutable approved anchor revision before replacement
  proposal-1.md                 # immutable full proposal with verbatim anchor
  proposal-2.md                 # next unused proposal file number
  round-1-review.md             # immutable raw independent review
  round-1-refinement.md         # immutable full revision/change record, if needed
  round-2-review.md             # next unused review sequence number
  round-N-discussion-input.md   # immutable clarification packet, if needed
  round-N-discussion-review.md  # immutable fresh clarification response
  REVIEW_STATE.json             # current workflow checkpoint
  REVIEW_SUMMARY.md             # current final report
  FINAL_PROPOSAL_DRAFT.md        # exact clean export awaiting proposal approval
  REVIEW_SUMMARY_DRAFT.md        # pending report, not an approved current export
  REFINEMENT_REPORT_DRAFT.md     # pending report, not an approved current export
  FINAL_PROPOSAL.md              # current explicitly approved clean export
  REFINEMENT_REPORT.md           # current final report
  score-history.md              # append-only attempt ledger across workflows
```

The parent owns current context, candidates, selection, anchor, immutable proposal snapshots, state, history and final aggregates. Each independent reviewer writes only its assigned unused review file. Current files update when genuinely new validated material/intent is requested; immutable numbered files never overwrite. Allocate a `proposal-N.md` number greater than every existing proposal number, and a `round-N-*` sequence greater than every existing or reserved round number, including incomplete files. Do not fill old gaps or reuse a reserved number for another review attempt. Related refinement/discussion files may share their attempt's sequence only when those exact filenames are unused. This is file numbering within one directory, not a storage namespace. Do not automatically archive into extra directories or delete user-owned history.

`review_attempts` counts full review attempts in the current workflow, including failed/invalid attempts; `max-rounds` bounds that budget. `review_sequence` is the ever-increasing file index and may start above 1. A new workflow resets the attempt budget, not the file sequence. A matching recovery keeps the consumed budget; selecting again or reconnecting cannot reset it.

After route selection, set `status=selected` only while drafting the problem; supplied intent likewise permits a draft, not automatic approval of its interpretation. Save `status=awaiting_anchor_approval` before full synthesis. Only matching actual anchor approval permits `status=in_progress` and the full design/review cycle. The selection file remains `status=confirmed`; its reply authorizes that route only. Revalidate source, summary owner/adoption and content bindings at every completed phase.

While generating candidates, drafting an anchor or awaiting final-proposal approval, leave the prior confirmed `PROBLEM_ANCHOR.md`, `FINAL_PROPOSAL.md` and current final reports untouched and identify their prior workflow explicitly. Before replacing an approved revision, preserve its exact anchor/export/report bytes in unused immutable revision files and retain their approvals, paths, hashes and workflow binding in `approved_revision_history` within the existing state. Do not recycle their READY or consent for the pending workflow. Drafts remain non-authoritative; an approved anchor is frozen throughout its design/review cycle.

### Selection and checkpoint bindings

After each completed phase persist `REVIEW_STATE.json` with real recoverable references. At the literature-driven gate also persist `CANDIDATE_SELECTION.json`. A candidate-stage state has these fields (placeholders describe types only):

```json
{
  "schema_version": 3,
  "project_root": "<resolved absolute project root>",
  "input_json": "<resolved absolute review JSON>",
  "input_sha256": "<current canonical review digest>",
  "summary_dir": "<resolved absolute completed summary directory>",
  "summary_snapshot_sha256": "<canonical digest of summary_artifacts>",
  "summary_artifacts": [{"path": "<absolute artifact path>", "sha256": "<exact byte digest>"}],
  "summary_state_path": "<actual approval owner state path, or null for recorded equivalent adoption>",
  "summary_state_sha256": "<actual owner state byte hash, or null>",
  "input_anchor_approval": null,
  "mode": "literature-driven",
  "intent_sources": [],
  "intent_sha256": null,
  "constraints": {},
  "candidate_path": "<absolute IDEAS_DIR/CANDIDATE_PROPOSALS.md>",
  "candidate_sha256": "<SHA-256 of candidate file UTF-8 bytes>",
  "candidate_ids": ["C1", "C2", "C3", "C4", "C5"],
  "ranking": [{"rank": 1, "candidate_id": "<actual top-ranked ID>"}],
  "recommended_candidate_id": "<actual top-ranked ID>",
  "selected_candidate_id": null,
  "user_confirmation": null,
  "confirmed_snapshot": null,
  "anchor_path": null,
  "anchor_sha256": null,
  "anchor_candidate_path": null,
  "anchor_approval": {"approved": false, "anchor_sha256": null, "confirmation_reference": null},
  "proposal_candidate_path": null,
  "proposal_sha256": null,
  "proposal_approval": {"approved": false, "proposal_sha256": null, "anchor_sha256": null, "confirmation_reference": null},
  "approved_revision_history": [],
  "max_rounds": 5,
  "threshold": 9,
  "phase": "candidates",
  "review_attempts": 0,
  "review_sequence": null,
  "current_proposal_path": null,
  "current_proposal_sha256": null,
  "final_proposal_path": null,
  "final_proposal_sha256": null,
  "final_proposal_source_path": null,
  "final_proposal_source_sha256": null,
  "last_review_path": null,
  "last_reviewed_proposal_sha256": null,
  "review_agent_id": null,
  "review_model": null,
  "review_valid": null,
  "last_score": null,
  "last_verdict": null,
  "blocking_issues": [],
  "status": "awaiting_selection",
  "timestamp": "<actual ISO 8601 timestamp>"
}
```

Persist the complete actual ranking, not just its first row. The selection file carries the same project/input/summary, mode, intent/constraints/settings and candidate binding, IDs/ranking/recommendation, selected ID, confirmation, phase and status. For optimization, no selection file or candidate consent is required: record supplied intent and explicitly mark selection fields not applicable, without reusing an earlier literature-driven confirmation.

For supplied intent retain exact file/direct text in `CONTEXT_BRIEF.md` and fingerprint it canonically. After selection save the exact confirming reply, selected ID/title/rank and full candidate analysis in `confirmed_snapshot`, together with its candidate/source/summary digests, constraints and settings; never reconstruct authorization from memory. Add a `workflow_sha256` derived canonically from these bindings (or supplied intent), selected route, frozen anchor and settings to all subsequent checkpoints/review ledger entries. This binds historical evidence without an invented directory identifier.

`phase` is the last completed phase: `candidates`, `anchor_draft`, `anchor`, `proposal`, `review`, `refine`, `proposal_draft`, or `done`. Gate statuses are `awaiting_selection`, `selected`, `awaiting_anchor_approval`, `awaiting_proposal_approval`, `in_progress`, `completed`, `declined`, `stale` or `failed` as actually applicable. Approval records begin false with null unknowns; only actual bound user decisions can set true. Record literal `null` with an explanatory note when reviewer identity/model is not exposed. Persist exact proposal/review fingerprints and frozen constraints to prevent scoring an unreviewed revision.

Inspect only the fixed current state and its explicit references. Resume only if project, review path/canonical digest, full summary snapshot and producer approval/adoption, mode, intent, constraints, candidate/confirmation when applicable, anchor candidate/approval, proposal bytes and settings match. Re-present a matching pending selection/anchor/proposal gate and wait for that decision, preserving consumed attempts and settings regardless of age. Changed inputs or candidate bytes invalidate pending confirmation: report the change, refresh grounded candidates on an authorized generation request, and require a fresh choice. An explicit `select` against missing/stale state stops with the exact reason; it cannot silently generate replacements or carry its choice into a refreshed set.

A mismatched/corrupt active state cannot reuse its anchor, budget or scores. Preserve numbered history and identify the exact recovery failure; an authorized new/restarted workflow updates current files from validated inputs and requires a new literature-driven gate. An existing completed state may be delivered as historical output, not consumed as authorization for another workflow. A materially changed current invocation supersedes any old pending offer.

On valid active recovery read the anchor, context, confirmed candidate, full current proposal, explicit reviews/rebuttals and ledger from files:

| Last completed phase | Next action |
|---|---|
| `candidates`, `awaiting_selection` | Show bound ranking and wait for an explicit unique selection |
| `candidates`, `selected` | Verify route confirmation, draft and present the problem; wait at `awaiting_anchor_approval` |
| `anchor_draft`, `awaiting_anchor_approval` | Revalidate draft/source bindings, re-present exact anchor and wait; no full synthesis |
| `anchor` | Verify matching actual `anchor_approval`, then author the full initial immutable proposal |
| `proposal` | Launch a fresh reviewer if attempt budget remains |
| `review` | Validate saved review; prepare final candidate only if eligible or budget exhausted, otherwise revise |
| `refine` | Fresh reviewer on saved full revision, if budget remains |
| `proposal_draft`, `awaiting_proposal_approval` | Revalidate exact export, anchor and independent-review binding; present final decision and wait; no commit or handoff |
| `done` | Deliver the bound completed artifacts; new generation requires fresh authorization/gate |

A partially written file or child not represented by a completed checkpoint is not a completed phase. Reconcile any still-running task before additional writes. Preserve partial/raw files and choose unused file sequence numbers; persist attempt consumption when dispatching, so interruption cannot replenish the budget. Missing recovery artifacts are an exact inability to resume, not permission to infer a score or proposal from chat.

## Phase 1 — Synthesize context, rank candidates, await selection

### Context and claim-level evidence

Write `CONTEXT_BRIEF.md` using BOTH the review and all actual paper analyses. Include:

- Resolved project/source binding, selected mode, review digest, complete summary snapshot and exact literature paths.
- Original user intent verbatim when supplied, its provenance, constraints, and non-goals; explicitly say none supplied in literature-driven mode.
- Field/method-family snapshot, strongest relevant baselines, interfaces and objectives available for reuse, and operational bottlenecks.
- Relevant review facets and gaps with paper IDs, links, and summary/source section locators. Do not turn a review's speculative open gap into an established failure fact.
- Evidence coverage: what is verified, abstract-only, inferred, contradicted, truncated, or unknown; any missing method detail or novelty coverage.
- Closest-work comparison ledger: paper, documented mechanism, proposal's prospective delta, exact supporting source, uncertainty, and necessary verification.
- Resources confirmed by the user versus explicit planning assumptions; unknown GPU count, dataset access, costs, and timeline remain unknown.

When review and summary disagree, follow the actual accessible paper evidence and retain the unresolved conflict. For every central factual claim distinguish **文献事实**, **推断**, **待验证假设**, and **计划实验**. Cite paper identifiers and accessible evidence; do not invent equations, numerical results, dataset availability, or negative findings. Proposed architecture/loss details may be concrete design choices, clearly separated from facts claimed about prior work.

### Candidate comparison

Write `CANDIDATE_PROPOSALS.md`:

- **Literature-driven:** generate **4–6** genuinely distinct proposals (default 5), not paper summaries, renamed known mechanisms, trivial variants or arbitrary combinations. Each has a stable visible ID (`C1`, `C2`, …), Chinese title, operational gap and nearest source paper IDs/locators, concrete mechanism delta with reused backbone/new component, prospective contribution, feasibility/resource assumptions, major novelty and implementation risks, falsifiable central claim, and minimal decisive test. Use nearest 2–3 papers when the corpus supports that count, otherwise all available closest evidence with an explicit coverage limitation. Every candidate remains within reviewed facets and user constraints. Evidence-thin routes are explicitly provisional; do not invent novelty or results. If the evidence genuinely cannot support at least four distinct candidates, disclose the precise gap and request broader grounding, rather than padding or silently reducing the range.
- **Optimize-user-idea:** compare credible bounded mechanism alternatives for the same supplied problem where alternatives exist. Record what is fixed/negotiable; no extra no-idea selection gate. If one route is viable, explain rather than padding with different problems. Choose a focused intent-preserving mechanism using the criteria below and proceed to its anchor.

For literature-driven mode include a ranked comparison table with **rank, candidate ID/Chinese title, concrete recommendation reasons, prospective contribution/novelty uncertainty, feasibility, major risks, validation cost** (unknown when unknown). Rank by bottleneck fit, evidence-backed delta, feasibility under stated constraints, simplicity and decisiveness of the smallest test—not fashion or fabricated numeric precision. Explain why the recommendation outranks the alternatives and each candidate's tradeoffs, including why combining routes adds unjustified complexity. Provisional positioning against examined work is not global novelty clearance.

### Mandatory no-idea selection gate

Show **all 4–6 candidates, the ranked table and concrete per-candidate analysis in chat**, not only a file link. Persist `CANDIDATE_SELECTION.json` and `REVIEW_STATE.json` with validated bindings, candidate file digest, IDs/ranking, recorded recommended ID, `selected_candidate_id=null`, `user_confirmation=null`, `phase=candidates`, `status=awaiting_selection`. Then **STOP**. Before selection do not choose a route, write/freeze an anchor, author a full initial method, invoke any reviewer, overwrite FINAL, or call any downstream skill. If FINAL exists, identify it as belonging to an earlier selection and not updated/approved for these candidates.

Ask exactly: **请回复候选ID（例如“选 C3”），或明确说“采用推荐第一名”；这只选择路线，之后将展示问题锚点供你单独确认，确认锚点后才完整设计并独立评审。** This is a textual multi-choice gate, not a yes/no confirmation or a host widget limited to five choices.

On a subsequent reply or `select` invocation:

1. Load the existing pending set and revalidate project/input/summary snapshot, mode/intent/constraints/settings, candidate bytes, complete IDs and displayed ranking. Every digest must be unchanged. Stale/missing artifacts invalidate the gate; never apply a remembered ID, rank or consent to regenerated candidates.
2. Accept only an **explicit unique candidate ID**, **unique displayed title**, or **unambiguous displayed recommendation rank**. `采用推荐第一名` selects the persisted `recommended_candidate_id`, not hardcoded `C1`. `选推荐第3名` means displayed rank; `选 C3` means ID. A bare number/ordinal that could mean either must be clarified.
3. Bare `可以`/`继续`/`yes`, including assent to the earlier summary offer, does not select among alternatives. Re-present the ranking and ask for the ID or explicit adoption of the recommendation; keep selection null. Decline/“都不选” records `declined` and stops. Multiple IDs or a combine request requires clarification, or an explicitly requested newly analyzed combined candidate set with another selection gate; never merge/pick silently.
4. For one matching explicit choice persist the exact reply and full `confirmed_snapshot`, set selection status `confirmed` and state status `selected`, and only **then** draft the selected route's problem anchor. Selection does not approve the draft, full design or final proposal. A consumed confirmation cannot authorize a repeat workflow or different candidate. Reopening a declined/changed set needs a fresh explicit choice, not old assent.

If every proposed route duplicates known work or cannot address the bottleneck, explain `RETHINK` and the evidence gap rather than recommending fabricated novelty.

### Draft, approve, then freeze `PROBLEM_ANCHOR.md`

After confirmed literature-driven selection, or intent-preserving route choice in optimization mode, write `PROBLEM_ANCHOR_DRAFT.md` without replacing the current approved anchor. Include:

- Mode, review topic/digest, full summary snapshot, exact upstream paths and intent provenance; selected candidate ID, confirmation binding and analysis reference when applicable.
- **Bottom-line problem** and intended application/setting.
- **Must-solve bottleneck**, with verified evidence or an explicit hypothesis label.
- **Non-goals** and user intent that must not change.
- **Constraints**, separating confirmed limits, planning assumptions, and unknown resources.
- **Success condition**: observable evidence that would address the actual bottleneck, not a claimed result.
- Selected route and one-sentence thesis; note the selection rationale's candidate file.

Present the exact draft in chat with its bottom-line problem, bottleneck, non-goals, constraints/unknowns, success condition, route and actual path/hash. Persist `phase=anchor_draft`, `status=awaiting_anchor_approval`, `anchor_candidate_path`, actual candidate `anchor_sha256` and `anchor_approval={approved:false,anchor_sha256:<actual candidate bytes>,confirmation_reference:null}`; preserve the previous approved revision separately. Ask whether this exact interpretation is accepted as the problem anchor and permits full method synthesis. Candidate selection or supplied intent alone cannot set this approval. A real reply already explicitly accepting this exact presented draft may be recorded without redundant questioning; otherwise stop here.

On actual approval re-read draft and source/summary bindings, record `anchor_approval.approved=true` and its real confirmation reference, archive any previous approved canonical revision and copy the approved draft bytes unchanged to `PROBLEM_ANCHOR.md`. Record its actual path/hash and `phase=anchor`, `status=in_progress`. A requested change means revise the draft and ask again, not approve. Refusal is `declined`; changed bindings are `stale`.

Copy the approved anchor verbatim into every initial/revised/final proposal and supply it plus its approval binding to every reviewer. Reviewer suggestions changing the problem are drift, not ordinary improvement. A material direction change pauses dependent work and needs a newly presented/approved anchor with retained immutable history; never mutate the anchor to chase a score. No full synthesis or independent review starts before this gate.

## Phase 2 — Author an implementation-ready initial proposal

Write the full next unused `proposal-N.md`, not an outline or list of modules. Treat it as immutable after saving; every full revision uses a new unused numbered proposal file. It and every revised/final proposal must contain:

1. **Title, provenance and status**: project/source digest and summary binding, selected candidate/intent, mode, proposal-only status, and scope of novelty evidence. Distinguish method-review readiness from empirical success.
2. **Problem Anchor**: verbatim standalone content.
3. **Technical gap**: exact baseline pipeline failure point or hypothesis, why naive fixes may be insufficient, closest-work evidence, and the smallest adequate intervention.
4. **Method thesis and contribution focus**: one dominant mechanism-level contribution, at most one supporting contribution, and explicit non-contributions. State why this is not simply renaming a known module.
5. **Complexity budget**: frozen/reused backbone, trainable and non-trainable additions, parameter/computation effects where derivable, and tempting additions deliberately excluded. Prefer at most two new trainable pieces; justify any essential exception rather than treating a soft limit as a reason to omit necessary mechanics.
6. **Representations and interfaces**: concrete input/output types, tensor/state dimensions or symbolic shapes, normalization, masks, conditioning, sampling, and boundary contracts. Name the attach point in the base pipeline and the exact mechanism delta.
7. **Core mechanism**: implementable equations, algorithm or ordered pseudocode, update/information flow, gradient paths, and what is learned versus fixed. If an LLM/VLM/diffusion/RL primitive is used, specify its precise role and why it is necessary; otherwise explain the intentional simpler choice.
8. **Structure diagram**: an ASCII graph showing module boundaries, key signals, conditioning, reused/frozen/new components, and the novelty entry point; keep width under 80 characters and ensure the diagram agrees with the equations and inference path.
9. **Training recipe**: proposed data source and access assumptions, preprocessing/splits, supervision or pseudo-label construction, negatives, losses with term definitions/weights and proposed selection rationale, schedule/stages, optimizer defaults as design choices, and which parameters update when. No trainable component may have an undefined learning signal. For training-free methods say so and replace irrelevant losses/stages with concrete inference-control/calibration rules.
10. **Inference recipe**: exact ordered steps, required resources/state, decoding/decision rules, integration point, and latency/memory tradeoffs. Separate proposed estimates from measured facts.
11. **Failure modes and diagnostics**: detectable failure signals, falsification conditions, mitigation or scope limits, and what should be removed if it adds no value. Do not fabricate a working fallback.
12. **Novelty and evidence table**: closest methods, shared components, precise prospective delta, cited evidence and unresolved verification. Never claim full novelty clearance from an abstract-only corpus or a review score.
13. **Minimal claim-driven validation**, following the next section.
14. **Experiment handoff inputs**: must-prove claims, required baselines/ablations, candidate datasets/metrics with access status, highest-risk assumptions, and implementation dependencies.
15. **Resource/timeline planning**: only confirmed resources as facts; derive estimates transparently when possible and label every estimate/assumption. Unknown values are explicit unknowns, not invented GPU-hours or dates.

A named module with no interface/loss/inference rule is not implementation-ready. A key empirical question may remain open, but its test procedure must be executable. If a material implementation dependency is unavailable, state it precisely and do not claim readiness. Save `phase=proposal`, `review_attempts=0` for the initial proposal only, and its actual immutable path/fingerprint; recovery never resets already consumed attempts.

### Minimal claim-driven validation

Use 1–3 core validation blocks by default, with one primary claim and at most one supporting claim. For each block specify:

- Falsifiable claim and connection to the frozen problem.
- Smallest useful controlled test, candidate data/split and access assumptions.
- Closest strong baseline and the targeted ablation, controlling compute/data differences.
- Decisive metric, comparison criterion, expected direction as a hypothesis, and a result that would refute the claim.
- Why this block is necessary; delete redundant benchmark shopping.

At least one block must directly test the anchor bottleneck. Include a deletion/simplification check when complexity is a risk and a necessity check if a frontier primitive is central; combine compatible checks within the core blocks. Do not give invented numerical gains or label planned tests as completed. Leave detailed run matrices, tracker creation, budgets, and execution schedules to `research-experiment-plannning`.

## Phase 3 — Fresh independent host-subagent review

The parent authors/revises; it cannot impersonate the independent reviewer. For **every** review attempt, use the host's native subagent/delegation capability to create a genuinely fresh reviewer with default host configuration. Do not reuse the proposal author's agent, a prior reviewer instance, or hidden thread memory. If the host cannot launch an independent subagent, record the exact blocker and deliver any reachable proposal work as unreviewed; never substitute self-scoring or fabricated `READY`.

Give the reviewer a self-contained packet containing:

- Assigned current-workflow attempt number and distinct unused review sequence `N`, threshold, exact output file `IDEAS_DIR/round-N-review.md`, and ownership restriction.
- Standalone anchor verbatim and full current proposal (inline or exact accessible full-file reference), including its fingerprint.
- Original user intent/constraints when present; explicitly identify literature-driven mode otherwise.
- Exact bound review JSON/digest, summary manifest/snapshot, context, candidate comparison and confirmed selection when applicable, relevant paper analyses/sidecars and accessible source references. The reviewer must read sufficient evidence to check central novelty/mechanism claims, not simply trust the author's synthesis.
- Prior raw critique and explicit change/rebuttal records when relevant. Prior scores are history, not a target the reviewer must match.

The reviewer writes only the assigned review file; no proposal, anchor, state, aggregates, tests, builds, lint, or formatting. Before dispatch reserve an unused `review_sequence` and persist incremented `review_attempts` within `max-rounds`. Record actual host-exposed agent identity and model, or honest unavailability. Keep full raw review text intact. The file must include structured assessment and unabridged reasoning; the parent may attach clearly separated metadata/validation notes, never replace raw responses with favorable summaries.

### Reviewer task and rubric

Instruct the reviewer to evaluate this early-stage method, not reward extra modules or a giant experiment menu. Stress-test bottleneck fidelity, exact interfaces/learning signals/integration, closest-work overlaps, evidence limitations, complexity, realistic resources, and focused falsification. Foundation-model-era leverage is appropriate fit, not mandatory fashion. Do not penalize a justified simple method just for not using a fashionable model.

| Dimension (structured key) | Weight | What to judge |
|---|---:|---|
| Problem Fidelity (`problem_fidelity`) | 0.15 | Solves the frozen bottleneck without changing intent or scope |
| Method Specificity (`method_specificity`) | 0.25 | Interfaces, representations, objectives, stages and inference are implementable |
| Contribution Quality (`contribution_quality`) | 0.25 | Evidence-backed prospective mechanism delta, parsimony, one dominant contribution |
| Frontier Leverage (`frontier_leverage`) | 0.15 | Appropriate contemporary primitives or justified simple reuse; no forced buzzwords |
| Feasibility (`feasibility`) | 0.10 | Compatible with stated resources, data access and explicit assumptions |
| Validation Focus (`validation_focus`) | 0.05 | Minimal decisive tests can falsify the core claims |
| Venue Readiness (`venue_readiness`) | 0.05 | If executed well, focused paper potential—not acceptance probability or achieved results |

Require finite numeric scores in `[1,10]` for all seven dimensions and a proposed weighted overall. For every score below 7 give the specific weakness, concrete method-level fix, priority (`CRITICAL`, `IMPORTANT`, `MINOR`), and evidence/proposal locator. Also report high-scoring dimensions' blocking issues; a score is not a waiver for missing evidence. Each issue must identify whether it blocks readiness, the rationale, and the resolution evidence needed.

Require this structured block alongside full raw reasoning, with actual values rather than these illustrative markers:

```json
{
  "scores": {
    "problem_fidelity": 1,
    "method_specificity": 1,
    "contribution_quality": 1,
    "frontier_leverage": 1,
    "feasibility": 1,
    "validation_focus": 1,
    "venue_readiness": 1
  },
  "overall": 1,
  "verdict": "REVISE",
  "drift_warning": "NONE or specific drift and evidence",
  "issues": [],
  "simplification_opportunities": [],
  "modernization_opportunities": [],
  "evidence_limitations": [],
  "reviewed_proposal_sha256": "<actual supplied fingerprint>"
}
```

`issues` entries must carry `id`, `dimension`, `priority`, `blocking`, `weakness`, `concrete_fix`, and `evidence`. Lists may be empty only when honestly justified in the prose. Include 1–3 useful simplification/modernization opportunities, or explicitly `NONE` if already tight/appropriate. State whether the anchor is preserved, novelty is only provisional, unknown assumptions are manageable versus blocking, and what still needs source verification.

Verdicts:

- **READY**: weighted score meets the configured threshold, anchor preserved, one focused contribution, actionable method and minimal validation, and no unresolved blocking drift, novelty/evidence, implementation, feasibility, or complexity issues. This means technical planning readiness, not user anchor/proposal approval, proven effectiveness or guaranteed novelty.
- **REVISE**: promising route with fixable deficiencies or unmet readiness gates.
- **RETHINK**: central mechanism/framing is unsupported, duplicates closest work without a defensible delta, or cannot address the anchor.

### Parent validation and scoring

After the reviewer returns, preserve its raw response and record metadata. Verify that the assigned artifact exists, is complete, refers to the actual full current proposal and anchor, contains all scores/required fields, and has usable grounded reasoning. Compute the authoritative weighted score from the seven dimensions; preserve the reviewer-reported overall separately and record discrepancies. Compare the unrounded computed value to `threshold`; display rounding must not turn a subthreshold score into readiness.

A failed child, missing file, malformed/nonfinite/out-of-range scores, proposal fingerprint mismatch, absent verdict, or incomplete assessment is an **invalid review**, never success. Record failure, null authoritative score/verdict where unavailable, and the exact reason. It consumes an attempt and requires a fresh reviewer within the remaining limit; never fill absent scores with guesses, silently coerce them, or overwrite its raw history.

Append to `score-history.md` the workflow binding, attempt, file sequence, actual agent/model availability, reviewed immutable proposal/hash, seven scores, reviewer-reported overall, parent-computed overall, raw verdict, validity, blockers and effective status. Keep earlier workflows clearly historical. Save `phase=review` with the actual review binding, consumed attempts, sequence, validity, score/verdict and remaining blockers.

## Phase 4 — Revise and re-review until ready or stopped

For a valid review, parent readiness requires **all** of: computed score `>= threshold`, reviewer verdict `READY`, correct current-proposal binding, no unresolved drift, and no blocking issues. A high score alone never terminates successfully. The parent may reject a review's unsupported favorable assessment, not silently upgrade an unfavorable verdict.

If not ready and attempts remain:

1. Copy the anchor verbatim and write an **Anchor Check**: original bottleneck, why the method still addresses it, and suggestions rejected as drift.
2. Write a **Simplicity Check**: dominant contribution, pieces to delete/merge/freeze, suggestions rejected as unnecessary complexity, and precise primitive roles.
3. Resolve every issue by explicit disposition: accepted fix, partial fix with remaining risk, or evidence-backed rejection. Map changes to issue IDs, paper/proposal evidence, and core-method consequences. Improve mechanisms before adding experiments or modules.
4. If clarification is genuinely necessary, save unused `round-N-discussion-input.md` with the anchor, full immutable proposal reference, critique, explicit rebuttal evidence and focused questions. Launch a **fresh** clarification subagent restricted to unused `round-N-discussion-review.md`; preserve raw answers and actual metadata. Reserve a fresh file sequence if these filenames already exist. Clarification cannot edit proposals or establish readiness; any score is advisory, not a full review attempt. Permit at most one clarification exchange per full-review attempt, not an unbounded loop.
5. Write the entire revised implementation-ready proposal to the next unused immutable `proposal-M.md` with the verbatim anchor. Save unused `round-N-refinement.md` with anchor/simplicity checks, issue/change log and an exact path/hash reference to that full snapshot, not an incomplete method patch. Save `phase=refine` and its current proposal path/fingerprint.
6. Launch a fresh reviewer on the full revision with a newly reserved unused review sequence and incremented current-workflow attempt count. Re-evaluate all seven dimensions independently; never tell a new reviewer that it authored prior critique.

Invalid reviews trigger a fresh attempt on the unchanged full proposal instead of pretending to revise missing critique. `max-rounds` caps current-workflow full-review attempts, including failed/invalid ones, not clarification or historical file numbers. Never quietly reset/raise it, lower the threshold, average past rounds to pass, or claim improvement without observed reviews.

At the limit, prepare the best fully specified current proposal as a final **candidate** with honest **REVISE** or **RETHINK** and unresolved blockers; do not commit it as current FINAL without the proposal gate. Do not author an unreviewed extra revision then attach the last review's score to it. If interruption leaves an unreviewed proposal, label it unreviewed and show which earlier snapshot the last valid score applies to. If there are no valid reviews, final score is unavailable and status is not READY; report the independent-review blocker and do not claim reviewed completion or offer downstream. A required pivot beyond the approved problem stops as `RETHINK` pending a new human anchor decision.

## Phase 5 — Final artifacts and user report

Prepare the candidate final document and report drafts even when the attempt limit is reached without readiness, provided proposal work exists. Never describe a blocked or incomplete method as implementation-ready. Preserve old current exports while approval is pending. Technical verdict and human approval are separate fields and must stay consistent across state, reports and chat.

### `FINAL_PROPOSAL.md`

The clean, full final method document, using all Phase 2 sections and the verbatim anchor. No raw critique or round chatter. Include provenance, exact upstream paths, mode, readiness/evidence status and honest assumptions. Its core mechanism, diagram, training/inference recipe, novelty delta and minimal validation must agree. If not READY, retain the usable best current method and clearly mark unresolved implementation/evidence prerequisites. `FINAL` names the delivered snapshot, not proven success.

Export only the method content from the selected full proposal; removing revision
chatter or adding delivery-status metadata is not a new method revision. Record
`final_proposal_path`/`final_proposal_sha256` separately from
`final_proposal_source_path`/`final_proposal_source_sha256`. Keep the authoritative score
bound to the exact source snapshot reviewed by the last valid reviewer; do not replace
`last_reviewed_proposal_sha256` with the differently formatted export's hash. Preserve
`current_proposal_path`/`current_proposal_sha256` as that reviewed source snapshot when
finalization makes only this clean export. Any substantive method change needs another
fresh review within the remaining attempt limit, or an explicit unreviewed status; it
cannot inherit the previous score.
Prepare the exact clean export as `FINAL_PROPOSAL_DRAFT.md`, with reports in `REVIEW_SUMMARY_DRAFT.md` and `REFINEMENT_REPORT_DRAFT.md`. Persist `phase=proposal_draft`, `status=awaiting_proposal_approval`, `proposal_candidate_path`, actual `proposal_sha256`, and `proposal_approval={approved:false,proposal_sha256:<candidate export byte hash>,anchor_sha256:<approved anchor byte hash>,confirmation_reference:null}`. Reports retain the independent review's exact source/hash and honest verdict; do not imply the user has accepted them.

After technical independent review/parent validation, display the actual final candidate (full mechanism or a complete readable presentation plus exact accessible full document), approved problem/non-goals, changed mechanisms, minimal claims/tests, evidence limits, unresolved blockers, resource assumptions, actual affected paths and export/anchor digests. Ask whether the user approves this exact proposal as the current method anchor; acceptance permits canonical export/report replacement, not experiment planning or launch. `READY`, the earlier anchor approval and candidate choice cannot approve it. Without a valid independent review, retain an unreviewed draft and the precise blocker rather than passing this reviewed-final gate.

On an actual unambiguous approval, re-read export/anchor/source/summary/review bindings and record true with the real `confirmation_reference`. Preserve prior approved immutable exports/reports and their approval evidence, then copy the approved clean export bytes unchanged to `FINAL_PROPOSAL.md` and commit the matching reports. `proposal_approval.proposal_sha256` must equal the delivered export's actual `final_proposal_sha256`; it is not `last_reviewed_proposal_sha256`. Any content change stales this proposal approval (and substantive method changes require fresh independent review); re-present the changed candidate. Rejection pauses as `declined`; no canonical replacement, completed status or downstream offer while pending/stale/declined.


### `REVIEW_SUMMARY.md`

Include project, review digest, complete summary snapshot and workflow binding; mode and original intent or exact confirmed candidate/rationale; upstream paths, anchor, current-workflow attempts/valid reviews, threshold, final computed score or unavailability, verdict and exact reviewed-snapshot binding. Provide a table with distinct attempt/file sequence, reviewer identity/model availability, concerns, fixes/pushback, simplification, resolution evidence and remaining risks. State anchor preservation, contribution focus, appropriate modern leverage, novelty coverage and final blockers; prior workflows' scores are historical only.

### `REFINEMENT_REPORT.md`

Include the same binding/status facts, actual output paths, full score evolution, method evolution and candidate rejection rationale, anchor/simplicity checks, issue dispositions, drift/pushback log, confirmed resources versus assumptions, remaining weaknesses, and downstream implementation/validation inputs. Preserve all raw reviewer responses verbatim under separate `<details>` sections with their round metadata, or link their unchanged complete files and explicitly explain that raw records live there. Do not summarize away failed or dissenting reviews.

### `score-history.md` and state

Complete the score table with every attempt, including invalid/failed reviews and null scores where applicable. Only after matching actual anchor/proposal approvals and required canonical artifacts are committed save `phase=done`, `status=completed` in `REVIEW_STATE.json` with actual final binding/verdict. A technically non-ready but independently reviewed proposal may be user-approved and completed as `REVISE`/`RETHINK`, never mislabeled READY. Pending final approval stays `phase=proposal_draft`, `status=awaiting_proposal_approval`; recovery re-presents that exact candidate without repeating reviews or replenishing attempts. On a real failure retain the checkpoint and record the reason, not a nonexistent completed bundle.

### User-facing report

Respond concisely in Chinese with:

- Mode, explicitly selected candidate/thesis or preserved supplied idea, current literature binding and evidence limits.
- Why this new route was chosen or which original user intent was preserved.
- Attempts/valid reviews, computed score and verdict, explicitly subjective method-review assessment.
- Anchor status, strongest concrete method improvements, and unresolved novelty/implementation/resource risks.
- Actual links/paths to `FINAL_PROPOSAL.md`, `REVIEW_SUMMARY.md`, `REFINEMENT_REPORT.md`, and score history.
- A separately confirmed next-step offer only when appropriate. No invented experiments, observed gains, or automatic downstream launch.

## Confirmed downstream handoff

Only after genuine user-approved final commit, recommend [research-experiment-plannning](../research-experiment-plannning/SKILL.md) when the proposal is stable enough to plan tests. Require current `anchor_approval` and `proposal_approval` matching actual delivered bytes; never offer an old FINAL during a new pending gate. If not READY, report blockers first. Any planning offer for a reviewed but non-ready approved proposal must explicitly preserve those limitations; entering planning still requires separate authorization.

Keep the following specific optional offer in the conversation as `NEXT_SKILL_HANDOFF` rather than relying on independently discovered latest files:

```json
{
  "from_skill": "research-ideas",
  "to_skill": "research-experiment-plannning",
  "project_root": "<actual absolute project root>",
  "docs_root": "<actual absolute project/docs>",
  "invocation": "/research-experiment-plannning \"<actual absolute FINAL_PROPOSAL.md>\" project: \"<actual absolute project root>\"",
  "artifacts": [
    {"role": "proposal", "path": "<actual absolute FINAL_PROPOSAL.md>", "sha256": "<exact file byte SHA256>"},
    {"role": "review-summary", "path": "<actual absolute REVIEW_SUMMARY.md>", "sha256": "<exact file byte SHA256>"},
    {"role": "refinement-report", "path": "<actual absolute REFINEMENT_REPORT.md>", "sha256": "<exact file byte SHA256>"},
    {"role": "upstream-artifact", "path": "<actual absolute consumed source or state file>", "sha256": "<exact file byte SHA256>"}
  ],
  "proposal_path": "<actual IDEAS_DIR/FINAL_PROPOSAL.md>",
  "anchor_path": "<actual approved PROBLEM_ANCHOR.md>",
  "anchor_sha256": "<actual approved anchor byte SHA256>",
  "method_state_path": "<actual IDEAS_DIR/REVIEW_STATE.json>",
  "method_state_sha256": "<actual committed owner state byte SHA256>",
  "review_summary_path": "<actual IDEAS_DIR/REVIEW_SUMMARY.md>",
  "refinement_report_path": "<actual IDEAS_DIR/REFINEMENT_REPORT.md>",
  "input_json": "<actual paired review JSON>",
  "summary_dir": "<actual paired completed summary directory>",
  "input_sha256": "<actual canonical review digest>",
  "summary_snapshot_sha256": "<bound completed summary snapshot digest>",
  "proposal_sha256": "<actual FINAL UTF-8 byte digest>",
  "review_summary_sha256": "<actual report UTF-8 byte digest>",
  "refinement_report_sha256": "<actual report UTF-8 byte digest>",
  "workflow_sha256": "<actual completed workflow binding>",
  "status": "awaiting_confirmation"
}
```

Expand `artifacts` to all actual consumed proposal/anchor/state/review/report and paired
literature/summary files, including the immutable reviewed-source snapshot. Verify each
byte hash and the named semantic fingerprints before planning writes. Changed bindings
set `stale`, invalidate this offer, and need a refreshed specific confirmation. Only
one unresolved next-skill offer may exist; replace obsolete offers instead of silently
retaining them. Silence, timeout or autonomous mode does not authorize the next skill.

Show `/research-experiment-plannning "<actual absolute FINAL_PROPOSAL.md>" project: "<actual absolute project root>"` with actual resolved paths and explain that companions are fixed files in the same `IDEAS_DIR`; outputs belong in `DOCS_ROOT/research-experiment-plannning`. A direct affirmative to this specific unresolved offer accepts once; refusal stops. Revalidate all exact bound source/summary/proposal/report fingerprints on acceptance and pass their actual paths/project/digests through the normal loader. Updated current files invalidate the offer, never substitute another proposal or retain an old score. Consent authorizes planning only, not bridge/training, paper writing, PKBase filing or repetition. An explicit invocation replaces an obsolete offer.

## Invocation examples

These are runnable chat syntax examples with illustrative project paths, not claims that the files already exist. When recommending a real invocation, replace them with actual resolved accessible paths.

**New proposal from completed literature, no overview needed:**

```text
/research-ideas input: "docs/research-literature-review/research_foundation_review.json" summary: "docs/research-literature-summary" project: "F:/projects/adaptation-study"
```

If the default overview is absent and no direct idea is supplied, this generates and displays 4–6 ranked candidates, saves `awaiting_selection` in `docs/research-ideas`, and stops before anchor/design/review. It never asks the user to write an idea. A nonempty default overview is supplied project intent and selects optimization; report the mode.

**Optimize a supplied overview with the same paired literature:**

```text
/research-ideas input: "docs/research-literature-review/research_foundation_review.json" summary: "docs/research-literature-summary" ideas-overview: "docs/ResearchIdeasOverview.md" project: "F:/projects/adaptation-study" max-rounds: 3 threshold: 9 constraints: "保持用户定义的任务与部署预算，不引入额外教师模型"
```

**Direct user idea text, no overview file:**

```text
/research-ideas input: "docs/research-literature-review/research_foundation_review.json" summary: "docs/research-literature-summary" project: "F:/projects/adaptation-study" 想法：保留当前参数高效适配任务与主干，优化适配更新的稳定性；不改变部署接口。请在这些意图内改进机制。
```

This selects optimization, records the direct intent, and verifies that this actual corpus can ground it. It does not invent empirical instability as an established fact.

**Confirmed summary offer:** after a unique bound `/research-ideas input: "<actual review>" summary: "<actual summary>" project: "<actual project>"` offer, `继续` executes that offer once without requiring an overview. With no user idea this starts candidate generation only, then stops at the separate candidate gate. A later `继续` at that gate asks which candidate, not automatic adoption of rank 1.

**Explicit candidate selection:** after an unchanged pending table, `选 C3` selects ID C3; `采用推荐第一名` selects the recorded top recommendation, which need not be C1. `3` alone, `可以`, `C2 和 C3`, and `都不选` do not select a route. Changed review/summary/candidate bytes require fresh selection.

```text
/research-ideas project: "F:/projects/adaptation-study" select: C3
```

This resumes only an existing matching pending C3 selection with unchanged input/summary/constraints/settings bindings. Missing or stale pending candidates are an error; no candidate creation-and-pick shortcut.

**Optional next stage:**

```text
/research-experiment-plannning "F:/projects/adaptation-study/docs/research-ideas/FINAL_PROPOSAL.md" project: "F:/projects/adaptation-study"
```

This is a separate explicit request. Method companions stay in `docs/research-ideas`; plan/tracker outputs update `docs/research-experiment-plannning`, not the proposal directory. Experimental IDs such as R001 remain experiment identifiers, not output-folder names.

## Version notes

- **6.0.0** — Separate route selection, content-bound problem approval and independently reviewed final-proposal approval; preserve prior confirmed revisions during pending gates. Validate matching summary owner approval or real equivalent input adoption, retain gate checkpoints/review budgets, and carry explicit method owner state to planning. No review verdict or output filename supplies human consent.
