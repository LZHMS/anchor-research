# Step 6 Reference — Research Ideas for the Day's Topic

How to turn (today's papers × PKBase knowledge × user interests) into defensible research ideas.

## Inputs (read all three before writing a single idea)

1. **Today's papers** — `analyzed_papers.json`. The richest idea seeds are `limitations`,
   `transferability_model_ideas`, and `method_detail` (specific mechanisms you can build on).
2. **PKBase existing knowledge** — from `index.md`, collect the pages under the run's
   domain/topic (and adjacent topics); read the relevant concept pages and a few source
   summaries. These are what "existing knowledge" means in the output — ideas that ignore them
   (duplicate known work) fail the quality bar.
3. **User interest signals** — the corpus items in `matched_corpus` per paper (the user's own
   Zotero neighbors), plus any annotations/notes captured in step 1. These say what the user
   actually works on — bias ideas toward that.

## Idea generation patterns (mix 3-8 of these, no duplicates)

1. **Gap-fix** — a limitation of a top-ranked paper (or a cluster of today's papers) that no
   paper in the PKBase has solved. "Paper X does A but fails at B; PKBase concept
   `[[c]]` shows B is the bottleneck for the user's direction → do C."
2. **Transfer** — a mechanism from today's paper transplanted into the user's own direction
   (from `matched_corpus`), justified by a PKBase concept that describes the target's current
   state of the art.
3. **Cross-paper synthesis** — two+ of today's papers (or one + an older PKBase source) make a
   combined contribution neither does alone.
4. **Contradiction / tension** — today's paper conflicts with or undercuts a claim in the
   PKBase; designing the experiment that decides between them is itself a contribution.
5. **Evaluation gap** — a benchmark/metric missing from both today's work and the PKBase that
   the user's direction would need.
6. **User-signal driven** — an annotation/note in the corpus that today's papers partially
   answer; frame the remaining question as the idea.

## Per-idea structure (Chinese body, English title)

```markdown
### Idea N: <中文一句话>
> English: <Concise English title>

- **动机与空白**：引用具体论文（arXiv ID）与 PKBase 页面（[[wikilink]]），说明空白在哪。
- **具体做法**：方法草图——输入/输出、关键模块、训练/评估方案；必须可证伪（明确成功标准）。
- **可行性**：难度 / 数据 / 算力估计；可复用的今日论文代码、权重或图表。
- **与已有知识的衔接**：延伸哪些已有概念（[[wikilink]]），会新建哪些概念页。
```

## Query page format (`wiki/queries/<domain>/<topic>/daily-<DATE>-<topic-slug>.md`)

```markdown
---
title: "每日研究想法 - <DATE> <Topic>"
domain: <domain>
topic: <topic>
created: <DATE>
sources: [wiki/sources/<domain>/<topic>/<slug-1>.md, wiki/concepts/<domain>/<topic>/<concept>.md, ...]
tags: [daily-ideas, <topic-tag>, ...]
---

# 每日研究想法 - <DATE>（<Topic>）

## 检索范围
- 日期窗口: <start> 到 <end>
- 来源: arXiv (<categories>) (+ web sources if any)
- 语料基础: Zotero（<N> 条兴趣语料）
- 排序依据: 加权语义相似度（top <TOP_K>）
- 现有知识: PKBase <domain>/<topic>（<n> 个概念页 / <m> 个来源页）

## Research Ideas
<3-8 ideas per the structure above>

## 今日论文速览
| # | 标题 | 一句话总结 | 评分 |
|---|------|-----------|------|
| 1 | [[wiki/sources/<domain>/<topic>/<slug-1>\|Title]] | <one_line_summary> | 8.8 |
...
```

Rules:
- Every idea cites ≥1 concrete anchor (arXiv ID, `[[wikilink]]`, or user note). "Apply X to Y"
  without a stated gap is rejected.
- `sources:` frontmatter lists plain PKBase-relative paths (not `[[...]]` — PKBase YAML rule).
- The 速览 table links each paper to its new source-summary page, making the query page the
  entry point into today's batch.
- Add the page to `index.md → Queries`, append the `log.md` entry (action `query`, `Filed: yes`),
  and make sure the site was rebuilt after this write (it is part of the same run's rebuild —
  include the query page in the `data.js` scan).
- **Site display:** the `daily-<DATE>-*` slug (and the `daily-ideas` tag) makes this the
  site's 每日论文看看 / Daily Papers entry for the day (standalone home section, last 3); the
  site excludes such pages from the 查询记录 / Queries column by design.

## Chat presentation

End the run by presenting in chat (concise, Chinese):
1. Top 3-5 ideas in full (structure above, trimmed).
2. Remaining ideas as one-line summaries.
3. Run report: date window, candidates → ranked → downloaded → analyzed → filed counts,
   PKBase pages created/updated, the query page path, and the site rebuild line.
