---
name: research-paper-plan
description: "Generate a structured paper outline from research project reports, proposals, and foundation reviews. Focuses on paper writing preparation, extracting core contributions, and planning sections, figures, and citations. Orchestrates user confirmation before finalizing."
version: 2.1.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [Research, Writing, Plan]
---

# Research Paper Plan

Topic or Workspace Directory: $ARGUMENTS

## Constants

- **REVIEWER_AGENT = `isolated-reviewer`** — Isolated sub-agent profile invoked via delegate task or Hermes CLI.
- **TARGET_VENUE = `ICLR`** — Default venue. User can override (e.g., /paper-plan "topic" — venue: NeurIPS). Supported: `ICLR`, `NeurIPS`, `ICML`, `CVPR`, `ACL`, `AAAI`, `ACM`, `IEEE_JOURNAL` (IEEE Transactions / Letters), `IEEE_CONF` (IEEE conferences).
- **MAX_PAGES** — Page limit. For ML conferences: main body to Conclusion end (excluding references, appendix). ICLR=9, NeurIPS=9, ICML=8. **For IEEE venues: references ARE included in page count.** IEEE journal Transactions ≈ 12-14 pages total, Letters ≈ 4-5 pages total; IEEE conference ≈ 5-8 pages total (including references).

## Goal

Produce a structured, section-by-section paper outline and preparation plan from research materials, confirm with the user, and save as PAPER_PLAN.md.

## Input interpretation

The skill expects these primary materials in the project directory:

1. **`FINAL_PROPOSAL.md`** — The finalized research proposal and method design.
2. **`TopicOverview.md`** & **`research_foundation_review.json`** — Literature, background, and related work foundations.
3. **Research project reports** (e.g., `NARRATIVE_REPORT.md`, `STORY.md`, `EXPERIMENT_LOG.md`, `AUTO_REVIEW.md`) — containing the experiment results, metrics, and review conclusions.
4. **Figures and Visuals** — Located in `docs/materials/figures/` (architecture diagrams, method plots).

If key materials are missing, ask the user to provide a brief 3-5 sentence description of the paper's contribution.

## Pre-Planning Principles (From Paper Writing Strategy)
- **Paper is a story, not a collection of experiments.**
- Every paper needs **one clear contribution** stated in a single sentence.
- You must answer: **The What** (what is contributed), **The Why** (what evidence supports it), and **The So What** (why should readers care).
- Establish notation conventions early.

## Orchestra-Guided Writing Overlay

Keep the existing insleep workflow and outputs, but use the shared references below to improve the quality of the story and outline.

- Read `./refer/writing-principles.md` when framing the one-sentence contribution, Abstract, Introduction, Related Work, or hero figure.
- Read `./refer/venue-checklists.md` before freezing the outline for a specific venue.
- Only load these references when needed; do not paste their full contents into the working draft.

## Workflow

### Step 1: Identify the Contribution & Establish the Narrative

Analyze FINAL_PROPOSAL.md, TopicOverview.md, and the project reports. Extract and articulate:
1. **The What**: The core method/discovery.
2. **The Why**: The key evidence from results.
3. **The So What**: The broader impact or gap filled based on `research_foundation_review.json`.
4. **Notation Conventions**: Standardize mathematical or architectural notations before detailed section planning.

### Step 2: Extract Claims and Evidence Matrix

Map validated claims to experimental evidence. Merge insights from project reports and auto-reviews.

```markdown
| Claim | Evidence | Status | Section |
|-------|----------|--------|---------|
| [claim 1] | [exp A, metric B] | Supported | §3.2 |
| [claim 2] | [exp C] | Partially supported | §4.1 |
```

### Step 3: Determine Paper Structure and Section Planning

Based on TARGET_VENUE and paper content, classify and select structure. Apply the narrative principle from `./refer/writing-principles.md`.

**IMPORTANT**: The section count is FLEXIBLE (5-8 sections). Choose what fits the content best. Front-load the most important material: title, abstract, introduction, and hero figure must convey the main narrative.

**Empirical/Diagnostic paper:**
```markdown
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method / Setup (1.5 pages)
4. Experiments (3 pages)
5. Analysis / Discussion (1 page)
6. Conclusion (0.5 pages)
```

**Theory + Experiments paper:**
```markdown
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Preliminaries & Modeling (1.5 pages)
4. Experiments (1.5 pages)
5. Theory Part A (1.5 pages)
6. Theory Part B (1.5 pages)
7. Conclusion (0.5 pages)
```

**Method paper:**
```markdown
1. Introduction (1.5 pages)
2. Related Work (1 page)
3. Method (2 pages)
4. Experiments (2.5 pages)
5. Ablation / Analysis (1 page)
6. Conclusion (0.5 pages)
```

For each section, specify details in markdown format:
- **§0 Abstract**: What, Why, How, Evidence, Remarkable result (150-250 words).
- **§1 Introduction**: Hook, Gap, One-sentence contribution, Approach, Contributions, Results preview, Hero figure description.
- **§2 Related Work**: Subtopics from `research_foundation_review.json`, positioning.
- **§3 Method/Setup**: Notation, Problem formulation, Method description.
- **§4 Experiments**: Planned figures, tables, and data sources.
- **§5 Conclusion**: Restatement, Limitations, Future work.

### Step 4: Figure & Citation Planning

- **Figure Plan**: Scan docs/materials/figures/ for existing method/architecture diagrams. Assign them to sections (e.g., Hero Figure to Intro or Method). Plan missing plots based on results. List every figure and table.
- **Citation Scaffolding**: Use `research_foundation_review.json` to map key baselines and background to Introduction and Related Work. *Never hallucinate citations.*

```markdown
## Citation Plan
- §1 Intro: [paper1], [paper2], [paper3] (problem motivation)
- §2 Related: [paper4]-[paper10] (categorized by subtopic)
- §3 Method: [paper11] (baseline), [paper12] (technique we build on)
```

### Step 5: User Confirmation Loop (CRITICAL)

Before finalizing and saving to disk, you **MUST** present the draft outline and core framing to the user for confirmation. 

1. **Present Draft**: Display the synthesized contribution (What/Why/So What), the claims-evidence matrix, and the high-level outline.
2. **Ask for Feedback**: Use the vscode_askQuestions tool to ask the user: *"Based on my understanding, the main contribution is: [one sentence]. The key results show [Y]. Is this the framing and structure you want?"*
3. **Process Feedback**: If the user provides modifications, update the plan. 
4. **Auto-Approve/Timeout**: If the user explicitly approves, or if you run in a fully autonomous mode and the user hasn't responded within a reasonable workflow context, proceed to save.

### Step 6: Cross-Review with REVIEWER_AGENT

Send the confirmed outline to an isolated sub-agent for a final sanity check feedback before generating the file.

```yaml
hermes cli:
  action: delegate_task
  agent: REVIEWER_AGENT
  isolation: strict
  input: |
    Review this paper outline for a [VENUE] submission.
    [full outline including Claims-Evidence Matrix]
    Score 1-10 on logical flow, claim-evidenc alignment, missing experiments, positioning, page budget, front-matter strength.
    Suggest the MINIMUM actionable fix.
```

## Output expectations

Once approved or auto-approved, save the complete plan to PAPER_PLAN.md in the project root:

`markdown
# Paper Plan

**Title**: [working title]
**Venue**: [target venue]
**One-sentence contribution**: [single-sentence statement]
**The What/Why/So What**: [Summary]
**Notation Conventions**: [List of math/variable notations]
**Type**: [empirical/theory/method]
**Date**: [today]
**Page budget**: [MAX_PAGES] pages
**Section count**: [N]

## Claims-Evidence Matrix
[from Step 2]

## Structure
[from Step 3]

## Figure Plan
[from Step 4 - integrating docs/materials/figures/]

## Citation Plan
[from Step 4 - integrating research_foundation_review.json]

## Reviewer Feedback
[from Step 6]

## Next Steps
- [ ] /paper-figure to generate missing figures
- [ ] /paper-write to draft LaTeX
- [ ] /paper-compile to build PDF
`

### Key Rules
- **Large file handling**: If the Write tool fails due to file size, run cat << 'EOF' > file using Bash silently.
- **User-Centric Framing**: Ensure the user agrees with the single-sentence contribution before locking the outline.
- **No Hallucinated Citations**: Only use verified papers from the JSON foundation or explicitly searched sources.
- **Evidence Gaps**: Mark claims as "needs experiment" rather than overclaiming.
- **Page budget**: If content exceeds MAX_PAGES, suggest what to move to appendix.
- **Venue-specific norms**: ML conferences use natbib; IEEE venues use cite package.
