---
name: research-shared-references
description: |
  Canonical reference and shared specifications for the Anchor Research pipeline: human anchor gate contracts, explicit handoff protocol, cryptographic bindings, authority hierarchy, and stage transition rules.
  Trigger: "anchor gates", "人机门控规范", "科研阶段门控", "research protocols", "科研门控", "阶段衔接协议"
version: 1.0.0
author: Zhihao Li
license: MIT
user-invocable: true
argument-hint: "topic: anchor-gates | stage: <stage-name>"
metadata:
  category: research
  tags: [research, protocols, anchor-gates, human-in-the-loop, specifications]
---

# Research Shared References: Protocols & Human Anchor Gates

Canonical specifications governing the anchor-first human-in-the-loop Auto Research system: **$ARGUMENTS**

## Overview

This skill defines the shared protocols, decision boundaries, state schemas, and handoff rules that coordinate all research skills in the `anchor-research` framework:

1. **[Human Anchor Gates Contract](./anchor-gates.md)** — Core decision boundaries, three-permission separation, owner state records, approved task projections, and anti-drift rules.
2. **Three-Permission Separation**:
   - **Stage Entry**: Authorization to inspect inputs and draft outputs for one specific stage (granted via direct invocation or accepting a unique `NEXT_SKILL_HANDOFF`).
   - **Anchor Approval**: Explicit user acceptance of a concrete, presented, content-bound artifact (`PROBLEM_ANCHOR.md`, `FINAL_PROPOSAL.md`, `EXPERIMENT_PLAN.md`, `PAPER_BUNDLE.json`, `MANUSCRIPT_MANIFEST.json`). Neither an LLM review score, code execution, nor silence/timeout can substitute for human approval.
   - **Consequential Action**: Explicit authorization to execute actions with irreversible side effects (process launching/killing, retries, budget extensions, permanent knowledge-base filing, paper submission, or printing).
3. **Single Active Handoff**: At any stage boundary, at most one bare-object `NEXT_SKILL_HANDOFF` exists in the conversation, cryptographically bound with exact file-byte SHA-256 and canonical JSON digests.
4. **Stale on Input Modification**: Any upstream file modification immediately stales downstream pending offers, requiring fresh presentation and re-confirmation.

## Core Documents

- [`anchor-gates.md`](./anchor-gates.md) — The complete specification of human anchor gates, owner states (`CORPUS_STATE.json`, `SUMMARY_STATE.json`, `REVIEW_STATE.json`, `EXPERIMENT_PLAN_STATE.json`, `RETROFIT_STATE.json`, `PAPER_PLAN_STATE.json`, `WRITING_STATE.json`, `POSTER_STATE.json`), approved task inventory projections, and stage handoff fields.

## Authority Hierarchy

When conflicts arise during automated research:
1. **Human Researcher Decisions** (highest authority).
2. **Confirmed Anchors** (`PROBLEM_ANCHOR.md`, `FINAL_PROPOSAL.md`, `EXPERIMENT_PLAN.md`, `PAPER_BUNDLE.json`).
3. **Execution Ground Truth** (actual code behavior and real evaluated metric values).
4. **Autonomous Agent Proposals & LLM Reviewer Scores** (advisory only; cannot override anchors or grant permissions).
