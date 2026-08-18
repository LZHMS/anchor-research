# Anchor Research

> **Anchor first. Automate second.**

An **anchor-first automated research (Auto Research) skill system**.

**[中文版 README → README.zh.md](README.zh.md)**

Traditional auto research is "automate first, think later" — you hand a direction to an agent and let it
explore on its own: auto-run experiments, auto-stack baselines, auto-rewrite the proposal……
**and nobody notices when the direction has gone wrong.** By the time the paper is written, it turns out
the work solved a different problem than the one you set out to solve — and several GPU-months are gone.

**Anchor Research does the opposite: drop an anchor at every stage before automating.**
An "anchor" is not just the Problem Anchor at the start — it is **a chain of checkpoints that runs through
the entire pipeline**. The output of every stage (problem definition, method proposal, experiment claims,
per-run success criteria, the paper's storyline) must first be **discussed with the researcher and
committed as an anchor** before any further automation is allowed to proceed — and the anchors are
continuously re-read to answer the question: *"am I still solving the right problem?"*

```
Classic auto research:   idea ──► unguided auto-exploration ──► paper (direction may have drifted long ago, unnoticed)

Anchor Research:         idea
                            │  📌 Anchor 1: Problem Anchor (problem definition confirmed with you)
                            ▼
                          refine
                            │  📌 Anchor 2: core contribution / FINAL_PROPOSAL (approach confirmed with you)
                            ▼
                          experiment plan
                            │  📌 Anchor 3: core claims + success criteria + decision gates (confirmed with you)
                            ▼
                          run & monitor
                            │  📌 Anchor 4: expected vs. actual per run (drift → stop, re-anchor, discuss)
                            ▼
                          paper plan
                            │  📌 Anchor 5: paper storyline / PAPER_PLAN (confirmed with you)
                            ▼
                          writing / poster
                            │  📌 Anchor 6: poster layout & figures (confirmed at each checkpoint)
                            ▼
                          delivery
```

**Every stage = one anchoring (human + agent alignment) + one anchor-constrained automated execution.**

---

## What Is an "Anchor"

An anchor is **a judgment that has been discussed with the researcher and committed at the end of a
stage**. It has three properties:

1. **Confirmed** — it is not a one-sided agent artifact; it is a conclusion aligned with the user
   (confirm-then-commit).
2. **Verifiable** — every subsequent round and run re-reads the anchors via **anchor checks** to detect
   drift (drift warnings).
3. **Authoritative** — anchors outrank the agent's autonomous decisions. On conflict, automation must
   either obey the anchor or stop and ask the human to re-anchor.

### The Anchor Chain Across the Pipeline

| # | Stage | Anchor (artifact) | How it aligns with the human | Owned by |
|---|-------|-------------------|------------------------------|----------|
| 1 | Proposal refinement | **Problem Anchor** (`PROBLEM_ANCHOR.md`) — immutable problem definition, bottleneck, bottom-line constraints | Extracted from user intent in Phase 0; copied verbatim into every round with an anchor check | research-refine |
| 2 | Proposal refinement | **Core contribution / method proposal** (`FINAL_PROPOSAL.md`) — one dominant contribution + the smallest adequate mechanism | Iterative review until the score threshold is met; the finalized proposal *is* the anchor | research-refine |
| 3 | Experiment planning | **Core claims + success criteria** (`EXPERIMENT_PLAN.md`) — at most 2 primary claims, a success criterion per run, decision gates (stop/go) | Decision gates are explicit human decision points; a failed run is reported to the human and waits for confirmation (only times out into auto re-anchoring) | experiment-plan / experiment-bridge |
| 4 | Experiment execution | **Run records** (`EXPERIMENT_TRACKER.md`) — expected vs. actual per run, change log | Strategy changes after a failed run require human confirmation (auto-resume is only a timeout fallback, and must be written back to plan/tracker) | run-experiment |
| 5 | Paper planning | **Paper storyline** (`PAPER_PLAN.md`) — the What / Why / So What of one clear contribution | An explicit **User Confirmation Loop**: the outline must be confirmed by the user before finalizing | research-paper-plan |
| 6 | Poster / delivery | **Poster visual anchors** (layout, figure selection, the 60-second story) | Every checkpoint **waits for explicit user confirmation by default** (`AUTO_PROCEED = false`) | research-paper-poster |

> Note the direction: anchors are not "read-only fossils." When the code and the proposal diverge
> substantially, `research-retrofit` uses the code as Ground Truth to **re-anchor** (updating
> `PROBLEM_ANCHOR.md` and `FINAL_PROPOSAL.md`) — re-anchoring still goes through the "discuss and
> confirm" step, instead of letting the agent quietly change course.

---

## System Architecture

Every skill is an "automation executor"; what actually keeps the direction correct are the **📌 anchors**
slotted between them (alignment points confirmed with the researcher and committed). Automated outputs
must pass anchor confirmation before they can become the input of the next stage.

```
 ┌─ Knowledge ────────────────────────────────────────────────────────────────────┐
 │  wiki-pk-base (PKBase) ──► literature-review ──► literature-summary           │
 └──────────────────────────────────────────┬─────────────────────────────────────┘
                                            ▼
 ┌─ Proposal ─────────────────────────────────────────────────────────────────────┐
 │  research-refine: freeze Problem Anchor → iterative review loop               │
 │  📌 Anchor 1+2: PROBLEM_ANCHOR.md + FINAL_PROPOSAL.md  (confirmed with you)   │
 └──────────────────────────────────────────┬─────────────────────────────────────┘
                                            ▼
 ┌─ Experiment ───────────────────────────────────────────────────────────────────┐
 │  experiment-plan ──📌 Anchor 3 (claims + success criteria, confirmed)──►      │
 │  experiment-bridge ──► EXPERIMENT_TRACKER.md                                  │
 │        │                                                                      │
 │        ▼                                                                      │
 │  run-experiment (impl → deploy → eval)  +  training-check (monitor)           │
 │  in:  structured-codebase (registry-driven training framework)                │
 │  📌 Anchor 4: expected vs actual per run; drift → stop, re-anchor, discuss    │
 └──────────────────────────────────────────┬─────────────────────────────────────┘
                                            ▼
 ┌─ Writing ──────────────────────────────────────────────────────────────────────┐
 │  research-paper-plan ──📌 Anchor 5 (User Confirmation Loop)──► PAPER_PLAN.md  │
 │  research-paper-hermes: write → self-review → revise → submit                 │
 └──────────────────────────────────────────┬─────────────────────────────────────┘
                                            ▼
 ┌─ Delivery ─────────────────────────────────────────────────────────────────────┐
 │  research-paper-poster ──📌 Anchor 6 (poster layout & figures, per-checkpoint  │
 │  human confirmation)  →  A0/A1 PDF / PPTX / SVG + talk script                 │
 └────────────────────────────────────────────────────────────────────────────────┘

 ↺ research-retrofit: at any point, re-anchor PROBLEM_ANCHOR / FINAL_PROPOSAL
   from the implemented code (Ground Truth) — re-anchoring still goes through
   human confirmation
```

Re-reading anchors is the norm, not the exception: `research-refine` runs an anchor check (drift
warning) in every round; `run-experiment` compares actual results against the success criteria in the
plan; `research-paper-plan` validates the storyline against the proposal. If any stage detects drift,
the pipeline **stops at that anchor and waits for a human to re-anchor** — it never limps on with a
known misalignment.

---

## Skills Overview

### 🧠 Proposal Layer

| Skill | Role | Trigger examples |
|-------|------|------------------|
| [`research-refine`](skills/research-refine/SKILL.md) | **The core of the system.** Turns a vague direction into a problem-anchored, elegant, frontier-aware, implementation-oriented method plan. Phase 0 freezes `PROBLEM_ANCHOR.md`; every round runs an anchor check (drift warning); isolated reviewers score the proposal until it reaches ≥ 9 | "refine my approach" |
| [`research-retrofit`](skills/research-retrofit/SKILL.md) | Code ↔ proposal alignment: uses the implemented code as Ground Truth to reverse-update the proposal, plus a rebuttal-style submission-readiness review | "update proposal from code" |

### 📚 Literature Layer

| Skill | Role |
|-------|------|
| [`research-literature-review`](skills/research-literature-review/SKILL.md) | Collects, de-duplicates, and normalizes papers from Zotero / Obsidian / web sources into a unified `research_foundation_review.json` |
| [`research-literature-summary`](skills/research-literature-summary/SKILL.md) | Two-stage deep analysis: a global research-landscape report (method lineages, datasets, metrics, open gaps) + per-paper LLM close reading (via `summarize_review.py`, supports OpenAI-compatible APIs / Ollama) |
| [`wiki-pk-base`](skills/wiki-pk-base/SKILL.md) | A persistent personal knowledge base (PKBase) following Karpathy's LLM Wiki pattern: compiled once, continuously maintained, queryable, lintable |

### 🧪 Experiment Layer

| Skill | Role |
|-------|------|
| [`experiment-plan`](skills/experiment-plan/SKILL.md) | Converts a proposal into a **claim → evidence → block → run-order** roadmap (must-run vs nice-to-have, decision gates, compute budget) |
| [`experiment-bridge`](skills/experiment-bridge/SKILL.md) | Parses plan milestones and initializes the per-run tracking table `EXPERIMENT_TRACKER.md` |
| [`structured-codebase`](skills/structured-codebase/SKILL.md) | A modular, registry-driven training framework (inspired by Dassl) — the standard home for experiment code |
| [`run-experiment`](skills/run-experiment/SKILL.md) | Implement code → log file changes → verify GPUs → deploy → evaluate → strategy loop on failure |
| [`training-check`](skills/training-check/SKILL.md) | Periodically reads WandB metrics and cuts broken runs early based on "learning quality" (NaN, loss divergence, trends) rather than system health |

### ✍️ Writing Layer

| Skill | Role |
|-------|------|
| [`research-paper-plan`](skills/research-paper-plan/SKILL.md) | Generates a section-by-section paper outline (`PAPER_PLAN.md`) with venue constraints for ICLR / NeurIPS / ICML / ACL / AAAI / IEEE |
| [`research-paper-hermes`](skills/research-paper-hermes/SKILL.md) | End-to-end paper writing pipeline: experiment analysis, drafting, self-review, revision, submission. Templates for NeurIPS / ICML / ICLR / ACL / AAAI / COLM; citations verified programmatically (no hallucinated references) |
| [`research-paper-poster`](skills/research-paper-poster/SKILL.md) | Generates an A0/A1 conference poster from a compiled paper (article + tcbposter → PDF / PPTX / SVG) + a talk script |

---

## Typical Workflow (Happy Path)

```
1. /wiki-pk-base              Build/maintain the domain knowledge base (PKBase)
2. /research-literature-review Collect literature → artifacts/research_foundation_review.json
3. /research-literature-summary Deep literature summary → Obsidian ResearchPapers/{topic}/
4. /research-refine           Freeze PROBLEM_ANCHOR.md, iterative refinement → FINAL_PROPOSAL.md
       📌 Anchor: problem definition + core contribution, confirmed with you
5. /experiment-plan           Claim-driven experiment roadmap → EXPERIMENT_PLAN.md
       📌 Anchor: core claims + success criteria + decision gates, confirmed with you
6. /experiment-bridge         Initialize the tracker → EXPERIMENT_TRACKER.md
7. /structured-codebase       Scaffold/reuse the registry-driven training codebase
8. /run-experiment            Per-run implement-deploy-evaluate (with /training-check monitoring)
       📌 Anchor: on a failed run, stop and confirm the strategy change with you before continuing
9. /research-retrofit         Late-stage: let code feed back into the proposal; re-anchor PROBLEM_ANCHOR / FINAL_PROPOSAL
10. /research-paper-plan      Generate the paper outline PAPER_PLAN.md
       📌 Anchor: paper storyline (What/Why/So What), User Confirmation Loop
11. /research-paper-hermes    Write → self-review → revise → submit
12. /research-paper-poster    Post-acceptance: poster + talk script (confirmed at each checkpoint)
```

The key state files (under `docs/refine-logs/`) — **they are the anchors made concrete** — ordered by
authority from highest to lowest:

| File | Anchor nature | Produced by | Consumed by |
|------|---------------|-------------|-------------|
| `PROBLEM_ANCHOR.md` | Highest authority: immutable problem definition, reused verbatim in every round | research-refine / research-retrofit (re-anchoring) | All (anchor check baseline) |
| `FINAL_PROPOSAL.md` | Proposal anchor: finalized core contribution and mechanism | research-refine / research-retrofit | experiment-plan, run-experiment, paper-plan |
| `EXPERIMENT_PLAN.md` | Experiment anchor: claims, success criteria, decision gates | experiment-plan / run-experiment (human-confirmed strategy updates) | experiment-bridge, run-experiment |
| `EXPERIMENT_TRACKER.md` | Execution record: expected vs. actual per run, auditable | experiment-bridge / run-experiment | Human + all downstream |
| `PAPER_PLAN.md` | Narrative anchor: the paper storyline (via User Confirmation Loop) | research-paper-plan | research-paper-hermes |

---

## Usage

This repository is a set of **agent skills** (each `skills/*/SKILL.md` defines a triggerable skill with
its workflow, constants, and trigger phrases). It works with agent runtimes such as Hermes / Claude
Code / VS Code Copilot:

- Wire the `skills/` directory into your agent's skills directory (e.g., `~/.agents/skills/` or a
  workspace `.claude/skills/`)
- Invoke by trigger phrase, e.g.:
  - `refine my approach: <problem description>`
  - `run experiment` (automatically picks the next PENDING run)
  - `check training <entity>/<project>/<run_id>`
- Some skills depend on environment variables:
  - `PKBASE_PATH` — knowledge base path (wiki-pk-base)
  - `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL` — OpenAI-compatible endpoint for the literature
    summary script (falls back to local Ollama when unset)
  - `WANDB_ENTITY` / `WANDB_PROJECT` — training monitoring

## Repository Layout

```
anchor-research/
└── skills/
    ├── research-refine/           # Proposal layer: refinement core (freezes the Problem Anchor)
    ├── research-retrofit/         # Proposal layer: code↔proposal alignment (re-anchoring)
    ├── research-literature-review/
    ├── research-literature-summary/  # + summarize_review.py
    ├── wiki-pk-base/
    ├── experiment-plan/
    ├── experiment-bridge/
    ├── structured-codebase/          # + StructCodebase/ training framework skeleton
    ├── run-experiment/
    ├── training-check/
    ├── research-paper-plan/          # + refer/ venue checklists & writing principles
    ├── research-paper-hermes/        # + references/ + templates/ (ICLR/NeurIPS/ICML/ACL/AAAI/COLM)
    └── research-paper-poster/        # + templates/ + logos/
```

## License

MIT (each skill is individually licensed; author: Zhihao Li; `research-paper-hermes` is adapted from
Orchestra Research's work)
