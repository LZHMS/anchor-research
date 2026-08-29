# Step 4 Reference — Deep Per-Paper Analysis

How the agent reads a downloaded paper source and writes its analysis entry.

## Reading order (per paper, in `ARTIFACTS/<DATE>/papers/{paper_id}/`)

1. `text_dump.txt` — the primary input. For LaTeX-sourced papers it is the document body with
   preamble, comments stripped and `\input{}` files inlined. For PDF-only papers it is the
   extracted text (noisy; cross-check against `paper.pdf` when unsure).
2. `figures.json` — the extracted figure list: `filename` (original path in source),
   `caption` (original English), `type` (heuristic: Task / Method / Result),
   `local_path` + `embeddable_path` (under `figures/`), `format`, `note`.
3. `paper.pdf` — only when the dump lacks something concrete (a table, an equation, an
   appendix detail you want to quote).
4. `source/` — only for ground-truth disputes (e.g. verifying a caption or a filename).

If `text_dump.txt` is empty AND the PDF text failed, analyze from the abstract only and set
`"analysis_depth": "abstract-only"`. Never invent method details that are not in the source.

## Figure selection

Pick **at most two** figures per paper:

- **task_figure** — the teaser / problem-setting / key-results figure. Look for `type`
  "Task (问题/概念图)" first; fallback: caption keywords (teaser, overview, illustrate,
  demonstrate, example, comparison, motivation, input and output); filename hints
  (teaser, intro, fig1, concept, task, motivation).
- **methodology** — the architecture / pipeline / framework figure. Look for `type`
  "Method (架构图)"; caption keywords (method overview, architecture, pipeline, framework,
  proposed method, consists of); filename hints (method, arch, pipeline, framework, system).

Rules:
- Always verify the choice by opening the actual image (the `embeddable_path` file) when the
  two candidates are close — heuristics mislabel frequently.
- Record both `filename` (traceability into the source) and `embeddable_path` (the PNG/SVG that
  will be embedded in PKBase). `embeddable_path` must point to a file that exists on disk.
- Captions stay in the **original English**, quoted verbatim (trim to the first sentence if
  very long).
- If no suitable figure exists for a slot, use `{"filename": "", "embeddable_path": "",
  "format": "", "caption": ""}`. Do not promote a Result figure into a Method slot.

## Depth bar (what "deep" means)

An entry is acceptable only if `method_detail` names the paper's concrete mechanism, not a
paraphrase of the abstract:

- **ML papers:** architecture components (with sizes/layer counts where given), the loss or
  objective, training data, the key experimental setup (datasets, metrics, baselines), and at
  least one ablation or failure finding.
- **Non-ML papers:** the core argument/algorithm, its inputs/outputs, evaluation method, and
  the strongest empirical or theoretical result.

`research_background` / `research_problem` / `motivation` must be distinguishable from each
other (context → gap → why now), not three restatements of the same sentence.

`limitations` — 1-2, from the paper's own discussion if present, otherwise a defensible
inference clearly framed as such ("据方法设计推断…").

`transferability_*` — three distinct angles, each one sentence, each naming a concrete
target area (not "其他领域"):

- `transferability_model_ideas` — which component/loss/trick moves to which other task
- `transferability_directions` — which broader research direction this advances
- `transferability_visualization` — which figure/plot/evaluation presentation is reusable

## Quality score (`quality_score`, 1-10)

Judge five dimensions, each 1-10; the score is the rounded mean:

- **新颖性** — is the core idea new, or an incremental combination of known parts?
- **技术严谨** — are the method details, derivations, and claims well supported?
- **实验完整** — datasets, baselines, ablations, statistics — how convincing is the evidence?
- **相关性** — how directly does it serve the user's direction (cf. `matched_corpus`)?
- **可复现** — code/data availability; clear enough to build on?

Bands: **8-10** must-read for the user's direction; **6-7.9** solid, selectively useful;
**4-5.9** marginal; **<4** would not have ranked in (revisit the ranking). An
`abstract-only` entry has not verified the claims — cap it at 6.

## Worked example (abridged)

Source: a DiT video-generation paper with `figures/intro.pdf` (teaser of generated clips) and
`figures/framework.pdf` (pipeline).

```json
{
  "paper_id": "2405.18991",
  "title": "EasyAnimate: ...",
  "domain": "生成模型 / 视频生成",
  "topic": "video-generation",
  "tags": ["video-generation", "dit", "reward-backprop", "attention"],
  "quality_score": 8.5,
  "one_line_summary": "提出混合窗口注意力与奖励反向传播的高性能视频生成框架。",
  "research_background": "视频扩散模型（DiT）在长序列下计算开销二次增长，且缺乏直接偏好对齐手段。",
  "research_problem": "如何在保持质量的前提下降低变长、高分辨率视频序列的注意力计算复杂度，并实现对齐优化。",
  "motivation": "全注意力是长视频生成的主要瓶颈；Reward Model 直接回传梯度可省去 RL 的不稳定性。",
  "method_detail": "主干为 1.3B 参数 DiT，采用 hybrid windows attention（局部窗口 + 全局 token）将复杂度降至近线性；训练分 VAE、DiT 预训练、reward backprop 三阶段；在 WebVid 10M 子集上训练，用 VBench 与人工偏好评估，对比 CogVideoX 等基线；消融显示窗口大小 4×4 与 reward 权重 0.5 最优。",
  "task_figure": {
    "filename": "Figures/examples.pdf",
    "embeddable_path": "research-daily-ideas/artifacts/2026-08-24/papers/2405.18991/figures/Figures_examples.png",
    "format": "png",
    "caption": "Qualitative results of generated video clips."
  },
  "methodology": {
    "filename": "Figures/pipeline.pdf",
    "embeddable_path": "research-daily-ideas/artifacts/2026-08-24/papers/2405.18991/figures/Figures_pipeline.png",
    "format": "png",
    "caption": "Overview of the EasyAnimate framework."
  },
  "main_contributions": ["开源完整训练/推理 pipeline", "混合窗口注意力降低长视频计算瓶颈", "验证 reward 直接回传的对齐有效性"],
  "limitations": ["依赖高质量视频-文本对齐数据", "极速运动场景仍有伪影"],
  "transferability_model_ideas": "混合窗口注意力可迁移到 3D 点云、超长音频等时空序列 Transformer。",
  "transferability_directions": "Reward 直接回传范式可推广到音频/3D 生成等需主观对齐的任务。",
  "transferability_visualization": "Reward Model 打分对比图可作偏好对齐类工作的评估模板。",
  "analysis_depth": "full"
}
```
