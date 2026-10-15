# Anchor Research

> **Anchor first. Automate second.**

An **anchor-first automated research (Auto Research) skill system**.

**[中文版 README → README.zh.md](README.zh.md)**

Traditional auto research is "automate first, think later" — you hand a direction to an agent and let it explore on its own: auto-run experiments, auto-stack baselines, auto-rewrite the proposal……
**and nobody notices when the direction has gone wrong.** By the time the paper is written, it turns out the work solved a different problem than the one you set out to solve — and several GPU-months are gone.

**Anchor Research does the opposite: drop an anchor at every stage before automating.**
An "anchor" is not just the Problem Anchor at the start — it is **a chain of human checkpoints that runs through the entire pipeline**. The output of every stage (corpus scope, evidence landscape, problem definition, method proposal, experiment plan, per-run milestone decisions, paper storyline, compiled manuscript, poster presentation) must first be **presented to the researcher, discussed, and explicitly confirmed as an anchor** before downstream automation is allowed to proceed. Every stage re-reads and cryptographically binds the upstream anchors to answer the question: *"am I still solving the right problem?"*

```
Classic auto research:   idea ──► unguided auto-exploration ──► paper (direction drifted long ago, unnoticed)

Anchor Research:
                         literature review & summary
                            │  📌 Anchor 0: Corpus scope & Evidence landscape (confirmed with you)
                            ▼
                         research ideas
                            │  📌 Anchor 1: Problem Anchor (problem definition & constraints confirmed with you)
                            │  📌 Anchor 2: Core contribution / FINAL_PROPOSAL (approach confirmed with you)
                            ▼
                         experiment planning
                            │  📌 Anchor 3: Core claims + task inventory + decision gates (confirmed with you)
                            ▼
                         run & monitor
                            │  📌 Anchor 4: Run records & Milestone decisions (drift → pause, discuss with human)
                            ▼
                         paper planning
                            │  📌 Anchor 5: Audited results, plots & paper storyline (confirmed with you)
                            ▼
                         paper writing
                            │  📌 Anchor 6: Complete compiled manuscript & claim verification (confirmed with you)
                            ▼
                         poster & delivery
                            │  📌 Anchor 7: Poster visual layout & talk script (confirmed with you)
                            ▼
                         delivery complete
```

**Every stage = one anchoring (human + agent alignment) + one anchor-constrained automated execution.**

---

## What Is an "Anchor"

An anchor is **a concrete decision that has been discussed with the researcher and committed at the end of a stage**. It has three essential properties:

1. **Confirmed** — It is not a one-sided agent artifact or optimistic progress flag; it is a conclusion explicitly approved by the human researcher (confirm-then-commit). Neither a high LLM review score, an executed script, nor silence/timeout can substitute for human approval.
2. **Verifiable** — Every subsequent stage re-reads the upstream anchors via exact content SHA-256 byte hashes and canonical JSON digests (`anchor check`) to detect drift.
3. **Authoritative** — Anchors outrank the agent's autonomous decisions. On conflict, automation must either obey the anchor or pause and ask the human to re-anchor.

### The Complete Anchor Chain Across the Pipeline

| # | Stage | Anchor (artifact) | How it aligns with the human | Owned by |
|---|-------|-------------------|------------------------------|----------|
| 0a | Literature review | **Corpus scope** (`CORPUS_STATE.json`) | Displays source coverage, merged paper counts, and evidence limits; requires `corpus_approval` before summary can be offered | `research-literature-review` |
| 0b | Literature summary | **Evidence landscape** (`SUMMARY_STATE.json`) | Displays cross-paper synthesis, open gaps, and limitations; requires `summary_approval` before ideas generation | `research-literature-summary` |
| 1 | Problem framing | **Problem Anchor** (`PROBLEM_ANCHOR.md`) | In literature-driven mode, displays 4–6 candidates for explicit route selection; drafts anchor and requires `anchor_approval` before method synthesis | `research-ideas` |
| 2 | Method proposal | **Core contribution / method proposal** (`FINAL_PROPOSAL.md`) | One dominant mechanism delta; fresh independent host-subagent review; requires explicit `proposal_approval` before replacing canonical exports | `research-ideas` |
| 3 | Experiment planning | **Core claims + task inventory** (`EXPERIMENT_PLAN.md` + `EXPERIMENT_PLAN_STATE.json`) | Claims, success criteria, milestone stop/go gates, compute budget ceiling; requires `plan_approval` on canonical task projection | `research-experiment-plannning` |
| 4 | Experiment execution | **Run records & milestones** (`EXPERIMENT_TRACKER.md`) | Verifies approved plan projection; milestone human decision gates pause execution for user review; unexpected drift or failed runs pause for human strategy decisions (no automatic kill or timeout auto-resume) | `research-run-experiment` |
| 5 | Paper planning | **Audited results, figures & storyline** (`PAPER_PLAN.md` + `PAPER_BUNDLE.json`) | Audits raw metrics against saved predictions/ground truth; generates runnable analysis, tables, and plots; independent review; requires `outline_approval` on exact bundle before writing | `research-paper-plan` |
| 6 | Paper writing | **Compiled manuscript** (`main.tex` + `main.pdf` + `MANUSCRIPT_MANIFEST.json`) | Expands approved plan into full sections; traces every number/caption to prepared results; verifies citations; compiles with real LaTeX; independent review; requires `manuscript_approval` before poster handoff | `research-paper-writing` |
| 7 | Poster & delivery | **Visual conference presentation** (`main.pdf` + `poster.pptx` + `poster.svg` + `POSTER_SPEECH.md`) | Organizes final paper and bound data into a 60-second visual story; content plan and card layout checkpoints require user confirmation; visual inspection + independent review | `research-paper-poster` |

> **Note on Re-anchoring**: Anchors are not "read-only fossils." When the codebase and the proposal diverge substantially, `research-retrofit` uses the code as Ground Truth for what was *implemented*, but **NOT authority over what problem the researcher intends to solve**. It diagnoses discrepancies, drafts reconciliation in `docs/research-retrofit/`, and **asks the researcher whether to re-anchor the problem or adjust the implementation**, rather than letting the agent quietly change course.

---

## System Architecture

Every skill is an "automation executor"; what actually keeps the direction correct are the **📌 anchors** slotted between them. Automated outputs must pass anchor confirmation before they can become the input of the next stage.

```
 ┌─ Knowledge & Literature ────────────────────────────────────────────────────────┐
 │  wiki-pk-base (PKBase) / research-daily-ideas (daily feeder)                    │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-literature-review ──📌 Anchor 0a (Corpus Scope Approval)──►          │
 │  research-literature-summary ──📌 Anchor 0b (Evidence Landscape Approval)──►    │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ Proposal Layer ────────────────────────────────────────────────────────────────┐
 │  research-ideas:                                                                │
 │    Route selection ──► 📌 Anchor 1: PROBLEM_ANCHOR.md (Human Approval)          │
 │    Method synthesis ──► Independent Review ──► 📌 Anchor 2: FINAL_PROPOSAL.md   │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ Experiment Layer ──────────────────────────────────────────────────────────────┐
 │  research-experiment-plannning:                                                 │
 │    Claim mapping ──► Milestone gates ──► 📌 Anchor 3: EXPERIMENT_PLAN.md        │
 │    Approved Task Inventory Projection (Human Approval)                          │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-run-experiment:                                                       │
 │    Deploy authorized runs ──► Evaluate vs ground truth                          │
 │    Helper 1: research-structured-codebase (modular registry training framework) │
 │    Helper 2: research-training-check (advisory quality monitoring reports)      │
 │    📌 Anchor 4: Run Tracker + Milestone human decision gates                    │
 │    (Drift / failure / budget limit → pause new work, discuss with researcher)   │
 └──────────────────────────────────────────┬──────────────────────────────────────┘
                                            ▼
 ┌─ Paper & Delivery Layer ────────────────────────────────────────────────────────┐
 │  research-paper-plan:                                                           │
 │    Audited results normalization + runnable plots/tables generation             │
 │    Storyline planning ──► 📌 Anchor 5: PAPER_PLAN.md & Bundle (User Approval)   │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-paper-writing:                                                        │
 │    Detailed composition ──► LaTeX compilation ──► Independent Review            │
 │    📌 Anchor 6: MANUSCRIPT_MANIFEST.json & Complete Manuscript (Human Approval) │
 │        │                                                                        │
 │        ▼                                                                        │
 │  research-paper-poster:                                                         │
 │    📌 Anchor 7: Poster content plan & card layout checkpoints (Human Approval)  │
 │    A0/A1 PDF + Native/Component PPTX + SVG + Talk script                        │
 └─────────────────────────────────────────────────────────────────────────────────┘

 ↺ research-retrofit: Code ↔ proposal alignment. Analyzes code as implementation
   ground truth, drafts reconciliation, and asks human whether to re-anchor
   PROBLEM_ANCHOR.md before updating canonical files.
```

Re-reading anchors is the norm, not the exception:
- `research-ideas` verifies the frozen problem anchor before and after every review round.
- `research-experiment-plannning` verifies that planned runs test the approved claims without benchmark sprawl.
- `research-run-experiment` checks that every deploy task matches the approved task inventory projection.
- `research-paper-plan` audits actual result data and builds a claim-to-evidence matrix before planning the paper.
- `research-paper-writing` traces every numeric claim and caption directly back to the audited result IDs.
- `research-paper-poster` binds figures and statistics strictly to the compiled paper and underlying data.

If any stage detects drift, the pipeline **pauses and consults the researcher** — it never marches forward with a known misalignment.

---

## Skills Overview

All 12 skills reside under `skills/` and operate host-neutrally (compatible with Claude Code, VS Code Copilot, OpenCodeInterpreter, etc.) without hardcoded vendor CLI commands or proprietary API bindings:

### 📚 Literature & Knowledge Layer

| Skill | Role | Triggers |
|---|---|---|
| [`research-literature-review`](skills/research-literature-review/SKILL.md) | Multi-source literature retrieval (Zotero, PKBase, Obsidian, Web/arXiv), de-duplication, and canonical normalization into `research_foundation_review.json`. Requires `corpus_approval` in `CORPUS_STATE.json` | "find papers", "literature review", "文献调研" |
| [`research-literature-summary`](skills/research-literature-summary/SKILL.md) | Deep literature summarization: per-paper analysis agents + global landscape synthesis (`overview_summary.md`, `aggregate_report.md`). Requires `summary_approval` in `SUMMARY_STATE.json` | "summarize literature", "analyze papers", "文献综述" |
| [`wiki-pk-base`](skills/wiki-pk-base/SKILL.md) | Persistent Personal Knowledge Base (PKBase) following Karpathy's LLM Wiki pattern: interlinked Markdown vault + static browser showcase. Curated by human, maintained by agent | "wiki", "knowledge base", "PKBase", "知识库" |
| [`research-daily-ideas`](skills/research-daily-ideas/SKILL.md) | Optional daily discovery feeder: fetches latest arXiv preprints by topic or Zotero profile, downloads sources/figures, writes analyses, files to PKBase | "今日论文", "daily ideas", "arxiv daily" |

### 🧠 Proposal Layer

| Skill | Role | Triggers |
|---|---|---|
| [`research-ideas`](skills/research-ideas/SKILL.md) | Literature-grounded research proposal design. Literature-driven mode offers 4–6 candidates for explicit user selection; freezes `PROBLEM_ANCHOR.md` upon human approval; conducts multi-round independent review; commits `FINAL_PROPOSAL.md` upon explicit user proposal approval | "research ideas", "提出研究方案", "打磨idea", "refine my approach" |
| [`research-retrofit`](skills/research-retrofit/SKILL.md) | Code ↔ proposal reconciliation. Treats implemented code as ground truth for implementation. Performs gap analysis in `docs/research-retrofit/CODE_ANALYSIS.md`, drafts reconciliation, and requires human re-anchoring decision before updating canonical files | "update proposal from code", "通过代码更新方案", "retrofit proposal" |

### 🧪 Experiment Layer

| Skill | Role | Triggers |
|---|---|---|
| [`research-experiment-plannning`](skills/research-experiment-plannning/SKILL.md) | Converts proposal into a claim-driven roadmap (`EXPERIMENT_PLAN.md`) with execution order, milestone decision gates, and compute budget ceiling. Projects canonical `approved_task_inventory` and initializes single tracker `EXPERIMENT_TRACKER.md`. Requires human `plan_approval` | "experiment plan", "规划实验", "ablation matrix", "run order" |
| [`research-run-experiment`](skills/research-run-experiment/SKILL.md) | Manages single `EXPERIMENT_TRACKER.md` lifecycle. Reconciles tasks against approved planning projection, deploys authorized runs, monitors training, evaluates predictions directly against dataset ground truth, and pauses for human decision on milestone gates or drift | "run experiment", "跑实验", "launch training", "review log", "实验进度" |
| [`research-structured-codebase`](skills/research-structured-codebase/SKILL.md) | Modular, registry-driven PyTorch training framework skeleton (inspired by Dassl/Detectron2). Optional implementation helper for `research-run-experiment` | "structured codebase", "代码库架构", "训练框架骨架" |
| [`research-training-check`](skills/research-training-check/SKILL.md) | Quality diagnostic helper: reads metrics/logs during training, assesses learning quality (NaN, divergence, stagnation), writes immutable reports to `docs/research-training-check/diagnosis-NNNN.md`, and reports advisory recommendations up to the execution owner. Never kills processes or modifies tracker directly | "check training", "monitor metrics", "is training healthy", "训练诊断" |

### ✍️ Paper & Presentation Layer

| Skill | Role | Triggers |
|---|---|---|
| [`research-paper-plan`](skills/research-paper-plan/SKILL.md) | Result preparation and narrative planning: audits metrics against saved predictions/ground truth, executes runnable analysis under `docs/research-paper-plan/analysis/`, produces real tables and plots, maps code-to-claims, conducts independent review, and requires user confirmation on `PAPER_BUNDLE.json` | "paper plan", "论文规划", "规划论文", "整理实验结果" |
| [`research-paper-writing`](skills/research-paper-writing/SKILL.md) | Detailed manuscript drafting: expands approved plan into complete sections using venue templates, programmatically verifies citations, traces every number to audited result IDs, compiles with LaTeX, conducts independent review, and requires human manuscript approval | "write paper", "draft manuscript", "论文写作", "compile paper" |
| [`research-paper-poster`](skills/research-paper-poster/SKILL.md) | Conference poster generation: extracts 60-second visual story from final paper and underlying data, formats A0/A1 LaTeX poster, checks card layout, performs visual rendering review, and exports editable/component PPTX, SVG, and talk script (`POSTER_SPEECH.md`). Checkpoints require human confirmation | "make poster", "conference poster", "海报制作", "论文海报" |

---

## Typical Workflow (Happy Path)

```text
1.  /research-literature-review  ──► Collect papers from Zotero/Web into unified JSON
        📌 Human Anchor: Confirm corpus scope, sources, and evidence boundaries
2.  /research-literature-summary ──► Generate deep per-paper analyses and global landscape
        📌 Human Anchor: Confirm synthesized evidence landscape and open gaps
3.  /research-ideas              ──► Generate 4–6 candidates from literature gaps
        📌 Human Anchor: Select candidate route
        📌 Human Anchor: Approve drafted Problem Anchor (bottleneck + non-goals)
        ├── Multi-round independent host-subagent review & refinement
        📌 Human Anchor: Approve final method proposal (FINAL_PROPOSAL.md)
4.  /research-experiment-plannning ──► Translate claims into milestone blocks & task inventory
        📌 Human Anchor: Approve experiment plan, decision gates, and compute budget
5.  /research-run-experiment     ──► Deploy authorized runs, evaluate predictions vs labels
        ├── (Optional) /research-structured-codebase for registry-driven model code
        ├── (Optional) /research-training-check for bounded metric diagnostics
        📌 Human Anchor: Milestone decision gates & failure recovery require human decision
6.  [If code diverges] /research-retrofit ──► Code analysis & gap identification
        📌 Human Anchor: Re-anchoring decision (adjust code vs re-anchor problem)
7.  /research-paper-plan         ──► Audit raw results, execute plotting, plan storyline
        ├── Runnable analysis, CSV/LaTeX tables, real PDF/SVG/PNG plots
        ├── Independent review of claim-evidence matrix & code trace
        📌 Human Anchor: User Confirmation Loop on exact PAPER_BUNDLE.json
8.  /research-paper-writing      ──► Draft complete sections using conference template
        ├── Verified BibTeX citations & numeric assertion traceability ledger
        ├── Real LaTeX compilation & independent review
        📌 Human Anchor: Approve final compiled manuscript & manifest
9.  /research-paper-poster       ──► Generate A0/A1 poster, PPTX/SVG exports & talk script
        📌 Human Anchor: Confirm poster content plan and visual card layout
```

---

## The Concrete Artifact Hierarchy

All project state lives within standard project documentation directories under `docs/`. State files are concrete, verifiable anchors:

| File | Anchor Nature | Produced By | Consumed By |
|---|---|---|---|
| `docs/research-literature-review/CORPUS_STATE.json` | Corpus Scope Anchor | `research-literature-review` | `research-literature-summary` |
| `docs/research-literature-summary/SUMMARY_STATE.json` | Evidence Landscape Anchor | `research-literature-summary` | `research-ideas` |
| `docs/research-ideas/PROBLEM_ANCHOR.md` | Problem Definition Anchor: immutable problem, bottleneck, non-goals | `research-ideas` / `research-retrofit` | All downstream skills |
| `docs/research-ideas/FINAL_PROPOSAL.md` | Method Proposal Anchor: core mechanism delta & minimal validation | `research-ideas` / `research-retrofit` | Planning, runner, paper |
| `docs/research-experiment-plannning/EXPERIMENT_PLAN.md` | Experiment Strategy Anchor: claims, success criteria, milestone gates | `research-experiment-plannning` | Runner, retrofit, paper |
| `docs/research-experiment-plannning/EXPERIMENT_TRACKER.md` | Execution Record Anchor: single tracker, actual metrics, file changes | `research-experiment-plannning` / `research-run-experiment` | Researcher + downstream |
| `docs/research-paper-plan/PAPER_PLAN.md` + `PAPER_BUNDLE.json` | Narrative & Evidence Anchor: audited data, tables, figures, story | `research-paper-plan` | `research-paper-writing` |
| `docs/research-paper-writing/MANUSCRIPT_MANIFEST.json` | Manuscript Anchor: final PDF, TeX includes, build log, review | `research-paper-writing` | `research-paper-poster` |
| `docs/research-paper-poster/POSTER_STATE.json` | Delivery Anchor: poster PDF, PPTX, SVG, speech script, review log | `research-paper-poster` | Researcher (presentation) |

---

## Stage Handoff Protocol

Stage transitions between adjacent skills follow the **Explicit Handoff Protocol** defined in [`research-shared-references/anchor-gates.md`](skills/research-shared-references/anchor-gates.md) (or trigger [`research-shared-references`](skills/research-shared-references/SKILL.md)):

1. **One Offer at a Time**: When a stage genuinely finishes and its human anchor is confirmed, it exposes a single conversation-scoped `NEXT_SKILL_HANDOFF` JSON object with status `awaiting_confirmation`.
2. **Cryptographic Binding**: The handoff enumerates all consumed artifacts with absolute paths and exact SHA-256 byte hashes, plus canonical JSON digests for structured data.
3. **No Automatic Cascade**: A direct affirmative (`yes`, `可以`, `继续`) authorizes **only the offered stage once**. It never grants authorization for subsequent stages, training runs, code execution, or publication.
4. **Stale on Change**: If any bound input file changes before execution begins, the offer becomes `stale` and requires fresh presentation and confirmation.
5. **No Timeout Auto-Approval**: Silence, timeout, or autonomous agent flags never grant authorization to cross a stage gate or enter a new skill.

---

## Repository Layout

```text
anchor-research/
├── README.md                          # Master English documentation
├── README.zh.md                       # Master Chinese documentation
└── skills/
    ├── research-shared-references/    # Canonical human anchor gate & protocol specification
    │   ├── SKILL.md                   # Skill definition & protocol index
    │   └── anchor-gates.md            # Detailed anchor gate specification
    ├── research-literature-review/    # Corpus collection, deduplication & normalization
    ├── research-literature-summary/   # Per-paper analyses & landscape synthesis
    ├── wiki-pk-base/                  # Persistent LLM Wiki knowledge base (PKBase)
    ├── research-daily-ideas/          # Daily arXiv discovery & PKBase feeder
    ├── research-ideas/                # Problem anchor & iterative proposal refinement
    ├── research-retrofit/             # Code-driven proposal overhaul & human re-anchoring
    ├── research-experiment-plannning/ # Claim mapping, milestone gates & tracker initialization
    ├── research-run-experiment/       # Authorized deployment, monitoring & evaluation
    ├── research-structured-codebase/  # Modular registry-driven training framework
    ├── research-training-check/       # Diagnostic quality monitoring (read-only advice)
    ├── research-paper-plan/           # Results audit, plots/tables & narrative bundle
    ├── research-paper-writing/        # Template-based drafting, compilation & verification
    └── research-paper-poster/         # Conference poster, multi-format export & talk script
```

---

## License

MIT License. Author: Zhihao Li.
