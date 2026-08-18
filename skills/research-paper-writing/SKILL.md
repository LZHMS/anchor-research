---
name: research-paper-writing
description: Executes paper writing into LaTeX strictly after the research-paper-plan skill has completed. Focuses on drafting, revision, and submission based on PAPER_PLAN.md and already-completed experiments.
version: 2.0.0
author: Zhihao Li
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Paper Writing, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations]
    category: research
    related_skills: [arxiv, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]
---

# Research Paper Writing

Pipeline for producing publication-ready ML/AI research papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**. This skill strictly covers the writing lifecycle: literature review, narrative structuring, paper drafting, review, revision, and submission. 

*(Note: This skill assumes all experiments have been fully executed, and results are available in logs or data files.)*

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 4: Submission    ◄── Phase 3: Self-Review            │
│       Prep                       & Revision ◄─────────┐     │
│       │                          ▲                    │     │
│       ▼                          │                    │     │
│  Phase 5: Post-Acceptance   Phase 2: Paper Drafting ──┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## When To Use This Skill

Use this skill when:
- **Writing or revising** any section of a research paper from existing experimental results.
- **Synthesizing findings** from result JSONs or `experiment_log.md` into narrative.
- **Preparing for submission** to a specific conference or workshop (formatting, checks).
- **Responding to reviews** with revisions or rebuttals.
- **Converting** a paper between conference formats.

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence.
4. **Commit early, commit often.** Every paper draft update — commit with descriptive messages.

---

## Input Interpretation

This skill MUST consume the following materials before writing:
1. **`PAPER_PLAN.md`**: The exact structure, contribution, and claims-evidence matrix to follow (output of `research-paper-plan`).
2. **`docs/materials/paper/`**: Directory containing highly relevant, reference papers (source LaTeX code) to study for stylistic and structural reference.
3. **`docs/materials/figures/`**: Directory containing required figures (e.g., task PDFs, method diagrams) to insert into the manuscript.
4. **Research Reports**: (e.g., `experiment_log.md`, `NARRATIVE_REPORT.md`) Detailed logs containing the actual empirical data.
5. **`research_foundation_review.json`**: The canonical source for literature review. Use this to construct citations.
6. **Skill Resources**: Use the skill's `./templates/` directory to initialize the target LaTeX workspace and `./references/` for venue-specific writing norms.

---

## Phase 0: Project & Template Setup

**Goal**: Initialize the workspace using templates and ingest the planning materials.

### Step 0.1: Load Templates and References
- Check the venue targeted in `PAPER_PLAN.md`.
- Locate the matching LaTeX template inside the skill's `./templates/` folder. Copy it to the workspace's `paper/` directory.
- Consult the skill's `./references/` folder for LaTeX best practices or venue checklists before writing.

### Step 0.2: Ingest the Plan
Read `PAPER_PLAN.md` thoroughly. Internalize the **One-sentence contribution**, the **Claims-Evidence Matrix**, and the **Section Structure**. The drafted paper MUST strictly adhere to this outline.

### Step 0.3: Inspect Reference Materials
Read through the LaTeX source files in `docs/materials/paper/` to understand your target tone, terminology, math formatting, and structural habits of high-quality papers in this specific domain.

---

## Phase 1: Citation Building & Asset Mapping

**Goal**: Prepare the BibTeX file and figure assets before drafting prose.

### Step 1.1: Construct the Bibliography
Extract required references from `research_foundation_review.json` and `PAPER_PLAN.md`'s Citation Plan.
- Construct `paper/references.bib`.
- **Never hallucinate citations.** If a requested citation lacks metadata, use Python APIs (Semantic Scholar / arXiv) to fetch the accurate BibTeX.

### Step 1.2: Map the Figures
Verify the image files listed in the `PAPER_PLAN.md` Figure Plan against `docs/materials/figures/`.
- Copy or link these PDFs/images into the `paper/figures/` directory.
- Prepare the `\includegraphics{}` paths for the drafting phase.

---

## Phase 2: Paper Drafting

**Goal**: Write a complete, publication-ready paper.

### Step 2.1: Ingest Results & Execute the Narrative

Review the research reports (e.g., `experiment_log.md`) to extract the exact empirical numbers. Bridge these findings to prose supporting the claims validated in the `PAPER_PLAN.md` Claims-Evidence matrix. 
**Do not invent claims** — only write what was planned and evidenced.

### Step 2.2: Two-Pass Refinement Pattern

**Pass 1 — Write + immediate refine per section:**
Draft complete sections (Abstract, Intro, Methods, etc.) and immediately refine local logic and clarity.

**Pass 2 — Global refinement with full-paper context:**
Revisit sections looking for cross-section consistency, redundancy, and terminology alignment.

### Step 2.3: Section-by-Section Guidelines

*   **Title**: 1-2 keywords, method name. Not too long.
*   **Abstract (5-Sentence Formula)**: What you achieved, why it's hard, how you do it, evidence, most remarkable number.
*   **Introduction (1-1.5 pages)**: Clear problem statement, 2-4 bullet contributions.
*   **Methods**: Enable reimplementation. Pseudocode, architectural details.
*   **Experiments & Results**: State what claim each experiment supports. Use booktabs for tables, bold best values. Explicit direction symbols ($\uparrow$ or $\downarrow$).
*   **Related Work**: Organize methodologically, not paper-by-paper.
*   **Limitations & Broader Impact (REQUIRED)**: Be honest. "No negative impacts" is an instant red flag.
*   **Conclusion**: Restate contribution, summarize findings, don't introduce new claims.

### Step 2.4: LaTeX Professionalism

```
LaTeX Quality Checklist:
- [ ] No unenclosed math symbols ($ signs balanced)
- [ ] Only reference figures/tables that exist (\ref matches \label)
- [ ] Every \begin{env} has matching \end{env}
- [ ] No unescaped underscores outside math mode (use \_ in text)
- [ ] Numbers in text match actual experimental results
- [ ] All figures have captions and labels
```

Use `microtype` (typography), `booktabs` (tables), `siunitx` (number alignment), `cleveref` (cross-references).

---

## Phase 3: Self-Review & Revision

**Goal**: Simulate the review process before submission. Catch weaknesses early.

### Step 3.1: Simulate Reviews (Ensemble Pattern)

Generate reviews from multiple perspectives.
**Step 1:** Form 3-5 independent reviewing agents (with a critical bias). Have them score Soundness, Clarity, Significance, Originality.
**Step 2:** Meta-review (Area Chair aggregation) to find consensus on weaknesses.

### Step 3.2: Claim Verification Pass

1. Extract every factual claim from the paper (numbers, comparisons).
2. Trace it to the specific result file.
3. Flag any claim without a traceable source as `[VERIFY]`.

### Step 3.3: Rebuttal Writing

When responding to actual reviews (post-submission):
- Address every concern point-by-point.
- Never be defensive or dismissive.
- Use `latexdiff` to generate a marked-up PDF showing changes.

---

## Phase 4: Submission Preparation

**Goal**: Final checks, format verification, and compilation.

### Step 4.1: Anonymization Checklist

```
- [ ] No author names or affiliations
- [ ] No acknowledgments section
- [ ] Self-citations in third person ("Smith et al. [1] showed..." not "We showed...")
- [ ] Use Anonymous GitHub for code links
```

### Step 4.2: Pre-Compilation Validation

```bash
# 1. Lint with chktex
chktex main.tex -q -n2 -n24 -n13 -n1

# 2. Check duplicate labels or missing figures using simple regex/scripts.
```

### Step 4.3: Final Compilation

```bash
latexmk -pdf main.tex
# Or: pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

### Step 4.4: Venue Format Conversion

When converting between venues (e.g., ICML to ICLR), **never copy LaTeX preambles**. Start fresh with the target template, copy only content sections, adjust for page limits, and add venue-specific required sections (like ICLR LLM disclosure).

---

## Phase 5: Post-Acceptance Deliverables

### Step 5.1: Camera-Ready Preparation
- De-anonymize (names, emails, real GitHub).
- Add acknowledgments.
- Final page limit check (sometimes differs from submission).

### Step 5.2: arXiv Strategy
Post to arXiv *after* submission deadlines for double-blind venues, using the correct category (e.g., `cs.LG`, `cs.CL`). Update with v2 after acceptance.

---

## Tool Usage Patterns (Writing & Revision)

| Tool | Usage in This Pipeline |
|------|----------------------|
| **`terminal`** | LaTeX compilation (`latexmk -pdf`), git operations. |
| **`execute_code`** | Run Python for citation verification, querying arXiv/SemanticScholar. |
| **`read_file`** / **`write_file`** / **`patch`** | Paper editing. Use `patch` for targeted edits to large .tex files. |
| **`delegate_task`** | **Parallel section drafting** — spawn isolated subagents for abstract, methods, and results parsing. |
| **`todo`** | Track granular progress (e.g., drafting queue, revision checks). |
