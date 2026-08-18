---
name: research-retrofit
description: |
  Retrofit and update an existing research proposal based on a user-maintained Research Report and newly implemented core code. Performs gap analysis (report vs code) and a rebuttal-style review for submission readiness.
  Accepts: Core Code Files/Paths, Research Report Document, Docs Root Directory (e.g., `docs/`)
  Trigger: "update proposal from code", "通过代码更新方案", "retrofit proposal", "基于代码翻新", "根据代码改大纲"
version: 1.0.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [Research, Retrofit, Code-to-Plan, Review]
---

# Research Retrofit: Code-Driven Proposal Overhaul & Rebuttal-Style Review

Retrofit proposal using: **$ARGUMENTS**

## Overview

Use this skill when you have a **user-maintained research report document** (the reliable, up-to-date project notes) and **already written or tuned core code** (the "Ground Truth"). Your formal research proposal files (typically inside your `Docs Root`, e.g., `docs/refine-logs/FINAL_PROPOSAL.md`, `docs/refine-logs/PROBLEM_ANCHOR.md`) are outdated and need to be aligned with the actual implementation and latest plans. 

Unlike `research-refine`, which is a multi-round, from-scratch ideation loop, `research-retrofit` is a **single-pass alignment and validation pipeline**. It compares the latest report with the implemented code to identify gaps, overhauls the existing proposal files in-place, and performs a one-shot "Rebuttal-Style" external review.

```text
User Input (Docs Root Directory + Core Code Files + Research Report)
  -> Phase 0 (Hermes): Auto-locate inputs -> Find Research Report, FINAL_PROPOSAL.md, etc.
  -> Phase 1 (Hermes): Reverse-Engineer & Gap Analysis -> Extract implementation, compare with report to find unimplemented ideas
  -> Phase 2 (Hermes): In-place Overhaul of PROBLEM_ANCHOR.md & FINAL_PROPOSAL.md
  -> Phase 3 (Hermes -> delegate_task): One-Shot External Review (Rebuttal-style readiness assessment)
  -> Phase 4 (Hermes): Polish final proposal based on review feedback.
```

## Inputs

| Input | Type | Required | Purpose |
|-------|------|----------|---------|
| Core Code Files / Paths | Explicit Paths / Glob | **Yes** | The single source of truth for the method's actual capability, architecture, and optimizations. |
| Research Report Document | Path | **Yes** | The user-maintained, up-to-date research project document containing the latest plans and notes to guide the proposal update. |
| Docs Root Directory | Path | **Yes** | The root dir (e.g., `docs/`) containing your research material. The agent will automatically search this directory for `FINAL_PROPOSAL.md` (or `ResearchIdeasOverview.md`), `PROBLEM_ANCHOR.md`, and `research_foundation_review.json`. |

## Workflow

### Phase 0: Auto-Locate Inputs
1. Search the **Docs Root Directory** (default: `docs/`) using file reading/searching tools.
2. Locate the **Research Report Document** specified by the user.
3. Locate the outdated proposal: Prefer `docs/refine-logs/FINAL_PROPOSAL.md`. If missing, fall back to `docs/ResearchIdeasOverview.md`.
4. Locate the original problem anchor: Prefer `docs/refine-logs/PROBLEM_ANCHOR.md`.
5. Locate the foundation review: Look for `docs/research_foundation_review.json`.
6. Keep these file paths in mind for the next phases.

### Phase 1: Code Reverse-Engineering & Gap Analysis

Analyze the provided **Core Code Files** and cross-reference with the **Research Report Document**:

1. **System Architecture**: What are the actual modules, backbones, and data flows in the code?
2. **Objective Functions**: What losses, rewards, or regularization terms are actually computed?
3. **Representations**: What exact features, embeddings, or intermediate tensors are used? 
4. **Gap Analysis (Report vs Code)**: Explicitly list the discrepancies. Crucially, **identify features, components, or ideas mentioned in the Research Report that are NOT YET implemented in the code**. This unimplemented list provides the basis for future experiments.

Write your findings to `docs/retrofit-logs/CODE_ANALYSIS.md`.

### Phase 2: Proposal Overhaul

Rewrite the existing proposal documents **in-place** to strictly align with the code and the new report. Do not create a new file.

1. **Update `docs/refine-logs/PROBLEM_ANCHOR.md`**: If the code or report solves a slightly different problem than the original anchor, rewrite the anchor in its original file to better fit the current reality.
2. **Rewrite `docs/refine-logs/FINAL_PROPOSAL.md` (in-place)**:
   - Replace abstract or abandoned ideas with concrete, implemented realities from the code.
   - Integrate updated plans from the Research Report Document.
   - **Add a Future Work / Pending Experiments section** highlighting the unimplemented ideas identified in Phase 1.
   - Re-frame "engineering hacks" as principled "methodological components" if they work well.
   - Regenerate the ASCII pipeline diagram to match the actual code variables and classes.
   - Update the "Claim-Driven Validation Sketch" to match the actual ablation points available in the codebase.

### Phase 3: One-Shot External Review (Rebuttal-Style)

Launch a single, strict isolated sub-agent review to grade the newly updated `FINAL_PROPOSAL.md`.

```text
hermes cli:
  action: delegate_task
  agent: isolated-reviewer
  isolation: strict
  input: |
    You are an Area Chair for a top venue evaluating a retrofitted research proposal. 
    The authors have already written the core code, so the method is mechanically bound. 
    
    Review the attached proposal for CONGRUENCE, FOCUS, and SUBMISSION READINESS.
    
    1. Score the following out of 10:
       - Problem-Method Alignment
       - Contribution Sharpness (no sprawl)
       - Mechanism Elegance
       - Empirical Feasibility
       
    2. Identify the single biggest target for Reviewer #2 (the most likely rejection reason).
    3. Suggest at most 3 IMMEDIATE text/framing adjustments to patch this weakness.
```

Save the response to `docs/retrofit-logs/REBUTTAL_REVIEW.md`.

### Phase 4: Final Polish

Based on the review, perform one final textual polish directly on `docs/refine-logs/FINAL_PROPOSAL.md` to patch framing vulnerabilities (without changing the code-based mechanics).

Present a summary to the user:
- What components were discovered in the code and added to the proposal.
- What ideas from the Research Report were identified as missing in the code (Pending Experiments).
- The Area Chair's assessment (Score and biggest risk).