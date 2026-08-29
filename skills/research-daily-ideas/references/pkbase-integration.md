# Step 5 Reference — Filing Analyses into PKBase

Per-paper recipe for ingesting step-4 analyses into the PKBase. **No new page types and no
new directories** — papers are sources, figures are assets, durable knowledge is concepts.
Everything below must respect the PKBase's own `SCHEMA.md` (read in step 0).

## Paths used by this run

Given a paper with `domain`/`topic` from its analysis entry and paper id `P`:

| What | PKBase path |
|---|---|
| PDF (immutable) | `raw/papers/<domain>/<topic>/YYYYMMDD-arxiv-P.pdf` |
| Task figure (embeddable) | `raw/assets/<domain>/<topic>/<P>_task.png` |
| Method figure (embeddable) | `raw/assets/<domain>/<topic>/<P>_method.png` |
| Source summary | `wiki/sources/<domain>/<topic>/<paper-slug>.md` |
| Concept pages | `wiki/concepts/<domain>/<topic>/<concept-name>.md` |
| Day's ideas (step 6) | `wiki/queries/<domain>/<topic>/daily-<DATE>-<topic-slug>.md` |

- `YYYYMMDD` = the run date; `paper-slug` = `YYYYMMDD-arxiv-P` lowercased (matches the raw
  PDF name minus extension) — this keeps `frontmatter.source` resolvable.
- Figures are **copied** from the run's `embeddable_path` (under `research-daily-ideas/artifacts/`),
  never moved. Skip a figure slot when `embeddable_path` is empty or the file is missing.
- Never overwrite an existing `raw/` file: on name collision append `-2`, `-3`, …
- Only PNG/JPG/SVG go to `raw/assets/`. If a figure's `format` is still `pdf`/`eps`
  (conversion failed), do NOT put it in the vault as an embeddable — reference it in the
  summary as text ("源图：figures/xxx.pdf，栅格化失败") and note it in the run report.

## Source summary format

Depth = the SCHEMA's `depth_level` (default 500). Narrative in Chinese (or the SCHEMA's
`default_lang`). Template:

```markdown
---
title: "Source Summary: <Paper Title>"
domain: <domain>
topic: <topic>
created: <DATE>
source: raw/papers/<domain>/<topic>/YYYYMMDD-arxiv-<P>.pdf
depth: <100|300|500>
tags: [<taxonomy tags from the analysis entry>]
arxiv_id: <P>
quality_score: <n.n>
url: <arxiv abs url>
articles_created: [<concept-name-1>.md, <concept-name-2>.md]
---

# <Paper Title> - Summary

<one_line_summary 作为开头，然后展开>

## What This Source Covers
- <bullet：背景/问题/方法/实验/局限，各一条>

## 任务图
![[<P>_task.png]]
> <original English caption, verbatim>

## 方法图
![[<P>_method.png]]
> <original English caption, verbatim>

## 方法细节
<method_detail；必须含至少一个 ASCII 架构图，宽度 <70 字符>

## 主要贡献
- ...

## 局限性
- ...

## 可迁移性
- 模型思路：<transferability_model_ideas>
- 研究方向：<transferability_directions>
- 可视化：<transferability_visualization>

## Wiki Articles From This Source
- [[<concept-name-1>]] - one line
- [[<concept-name-2>]] - one line
```

Notes:
- Images use Obsidian `![[filename]]` syntax (resolves by file name across the vault), so the
  `raw/assets/<domain>/<topic>/` nesting is safe.
- The ASCII diagram is **required** by the PKBase SCHEMA — draw the method pipeline even when
  the paper has a figure (the figure complements, doesn't replace, the diagram).
- Math is LaTeX (`$...$` / `$$...$$`), never backticks.
- Frontmatter values stay plain strings / flat string arrays (PKBase rule — no nested
  arrays, no `[[...]]` in YAML).

## Concept pages

Extract **2-5 granular concepts** per paper (algorithm name, architecture component,
loss/objective, dataset/benchmark, or a distinctive limitation). For each concept:

1. Search the whole `wiki/` tree for the concept name / close variants (file search across
   `*.md`, case-insensitive).
2. **Exists** → append: new insight bullets, the new source in `sources:` frontmatter (plain
   path `raw/papers/<domain>/<topic>/YYYYMMDD-arxiv-<P>.pdf`), bump `updated`, add a
   `## Sources` wikilink line. Do not rewrite existing content.
3. **Missing** → create `wiki/concepts/<domain>/<topic>/<concept-name>.md` per the SCHEMA
   Article Format, with `related:` (plain paths) and ≥2 body `[[wikilinks]]`.
4. Cross-link: the new source summary links to its concepts; each touched concept links back
   to the source summary in its `## Sources` section.

## Navigation + log + site (once per run, not per paper)

1. `index.md` — add every new source summary and concept page under its domain/topic section
   (one line: wikilink + summary + tags); update "Last updated" and "Total pages".
2. `log.md` — one batch entry:

   ```markdown
   ## [<DATE>] ingest | Daily papers <DATE> (<N> papers, topic: <TOPIC|broad>)
   - Domain: <domain> | Topic: <topic>
   - Per paper: <P> → sources/<domain>/<topic>/<slug>.md; concepts created/updated: <list>
   - ...
   - Site: rebuilt (<n> pages, <m> raw files)
   ```

3. **Site rebuild** (PKBase web rule — do this, the site must never lag the vault):
   - **Prefer the bundled rebuild script when present:** if `<PKBase>/site/rebuild_site.py`
     exists, run `python <PKBase>\site\rebuild_site.py <PKBASE_PATH>` — it performs the whole
     procedure below (data.js + `?v=` bump) and prints the report line. Only when it is
     absent, do the manual procedure:
   - Scan `wiki/{sources,concepts,comparisons,queries}/<domain>/<topic>/*.md` + existing pages
     → parse frontmatter + body (no frontmatter) into `data.js` entries; if `bilingual: true`,
     merge sibling translation files (`<slug>.en.md` when `default_lang: zh`, `<slug>.zh.md`
     when `default_lang: en`) into the same entry's `_en`/`_zh` fields (do not list them as
     separate pages).
   - Re-scan `raw/` → `raw[]` (the new PDFs + PNGs appear here).
   - Merge `log.md` (+ `log-*.md`) → `log[]` (newest ~50).
   - Write `<PKBase>/site/data.js`, bump `meta.updated`, and update the `data.js?v=<DATEcompact>`
     query string in `site/index.html` (e.g. `?v=20260824`). Never hand-edit the other four
     site files.
   - Report the line: `site rebuilt (N pages, M raw files)`.

## Domain/topic & tag hygiene

- Reuse the closest existing SCHEMA domain/topic; if the run's topic genuinely falls outside
  the SCHEMA's domains, propose the new domain/topic to the user and register it in
  `SCHEMA.md → ## Domains & Topics` before filing (one-time cost, keeps the vault consistent).
- Every tag used must exist in `SCHEMA.md → ## Tag Taxonomy`. The analysis entries' English
  tags map onto taxonomy tags; when one is missing, add it to the taxonomy first with a short
  definition, then use it.
- If a run would update 10+ existing concept pages, confirm the scope with the user before
  writing.
