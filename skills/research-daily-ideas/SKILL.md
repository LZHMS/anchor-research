---
name: research-daily-ideas
description: "Daily paper discovery pipeline: find today's newest arXiv papers matching a given topic OR the user's Zotero research interests (with configurable count), download each paper's LaTeX source + figures, write a deep per-paper Chinese analysis with embedded figures, ingest every analysis into the PKBase knowledge base, and finally synthesize research ideas for the day's topic grounded in both the new papers and existing PKBase knowledge. Use when the user asks for 今日论文, daily ideas, today's papers, 今天有什么新论文, arxiv daily, 从 Zotero 兴趣出发推荐新论文, or wants recent papers ranked by semantic similarity with analysis and knowledge-base ingestion."
argument-hint: "topic: '3D Facial Animation' | top_k: 20 | date: 2026-08-24 | pkbase: D:\\notes\\MyPKBase"
---

# Daily Idea

One-shot daily research pipeline that compounds over time:

```
topic / Zotero interests ──▶ ranked papers ──▶ downloaded sources ──▶ per-paper analysis
   (Step 1-2, scripts)        (Step 3, script)      (Step 4, agent)
                                                                        │
   research ideas ◀── PKBase (wiki/sources + raw) ◀────────────────────┘
   (Step 6, agent)                   (Step 5, agent, per PKBase conventions)
```

**Division of labor:** deterministic work (fetch, rank, download, convert) is done by bundled
scripts; judgment work (writing the analysis, filing into PKBase, generating ideas) is done by
the agent. The PKBase is the long-term memory — every run makes it richer, and later runs
produce better ideas because they read what earlier runs filed.

## Constants

- **TOPIC** — the research topic to search for. If the user passes no topic (or `all`), build
  the interest profile directly from the user's Zotero library.
- **TOP_K** — number of ranked papers to keep in `ranked_papers.json`, to download, to analyze,
  and to present. Default `20`; the user can override (`top_k: 15`).
- **DATE** — the run date, `YYYY-MM-DD`. Default: today. Always state the exact date window
  actually searched in every report (e.g. `2026-08-22 to 2026-08-24`).
- **PKBASE_PATH** — the PKBase directory, resolved in this order: explicit `pkbase:`
  argument (highest priority) → `$PKBASE_PATH` env var → ask the user → `~/PKBase`.
  Every step 5/6 action follows the `wiki-pk-base` skill conventions exactly
  (three-level `raw/` and `wiki/` trees, index.md, log.md, site rebuild).
- **ARTIFACTS** — scratch root, default `research-daily-ideas/artifacts/`, **relative to the project
  root** (the directory containing `skills/`). All intermediate JSON and downloaded sources
  live here; PKBase is the durable output.

> 💡 Overrides (slash or chat):
> - `/research-daily-ideas — topic: "3D Facial Animation", top_k: 15`
> - `/research-daily-ideas` → broad discovery from the whole Zotero library, top 20
> - `/research-daily-ideas — date: 2026-08-20` → re-run a specific past date
> - `/research-daily-ideas — pkbase: D:\notes\MyPKBase` → file into a specific PKBase (overrides env var/default)

## Step 0 — Orient (every run, before anything else)

1. **Resolve `PKBASE_PATH`**: explicit `pkbase:` argument → `$PKBASE_PATH` env var → ask the
   user (and suggest also setting the env var for future runs) → `~/PKBase`.
   Confirm the PKBase exists at the resolved path. Read `SCHEMA.md` (domains, topics, depth
   level, tag taxonomy, bilingual setting), `index.md`, and the last ~20 entries of `log.md`.
   This is what step 5 uses for domain/topic classification, tags, and cross-linking, and what
   step 6 reads as the "existing knowledge" base.
2. If the PKBase does not exist, stop and tell the user to run the `wiki-pk-base` skill's
   `init` first — this skill does not create PKBase.
3. Check Python deps for the scripts (see `requirements.txt`):
   `pip install pyyaml sentence-transformers numpy requests PyMuPDF pypdf`
   Missing `sentence-transformers` blocks step 2; missing `PyMuPDF` only degrades figure
   conversion (the script warns and continues).
4. Create `ARTIFACTS/<DATE>/` — all per-run state goes there.

## Step 1 — Build the interest corpus

Produce `ARTIFACTS/<DATE>/zotero_corpus.json` — the semantic anchor for ranking.

**Mode A — topic given (`TOPIC` ≠ all):**
1. Query Zotero via `mcp__zotero__*` tools (search by topic terms + related collections/tags).
2. Keep items with meaningful titles AND abstracts. Prefer items whose collections/tags/
   annotations match the topic; include the most relevant subset's `annotations` and `notes`
   as interest signals.
3. Compute per-item `weight` (auditable formula, also stored as `weight_signals`):

   ```text
   annotation_signal = min(annotation_count, 5) / 5
   tag_signal        = target_tag_match_score         # 1.0 exact, 0.5 close, 0.0 none
   collection_signal = target_collection_match_score  # 1.0 exact, 0.5 parent/child/sibling
   recency_signal    = max(0, 1 - min(days_since_added, 365) / 365)

   weight = 1.0 + 0.45*annotation_signal + 0.20*tag_signal
                + 0.20*collection_signal + 0.15*recency_signal
   ```

**Mode B — no topic (`all`):**
1. Pull the user's Zotero items (conferencePaper / journalArticle / preprint) with non-empty
   abstracts via `mcp__zotero__*`.
2. No target tag/collection — set both signals to `0` so annotations + recency dominate.
3. Optionally derive 3-5 thematic clusters from the library (by collection/tag) and note them;
   they become candidate topics for step 6.

**Corpus item schema** (one JSON array):

```json
{
  "item_key": "ABCD1234",
  "title": "Paper title",
  "abstract": "Abstract text",
  "authors": ["Author A", "Author B"],
  "venue": "Conference or journal",
  "year": "2025",
  "added_date": "2026-03-27T10:20:30Z",
  "paths": ["Collection/Path"],
  "tags": ["llm", "reasoning"],
  "weight": 1.42,
  "weight_signals": {
    "annotation_count": 4, "target_tag_match_score": 1.0,
    "target_collection_match_score": 0.5, "days_since_added": 12, "recency_score": 0.97
  },
  "annotations": [{ "page": 3, "text": "highlight", "comment": "why it matters", "color": "#ffd400" }],
  "notes": ["User note"],
  "citation": { "doi": "10.1000/example", "url": "https://example.org/paper", "citation_key": "Smith2025" }
}
```

## Step 2 — Fetch candidates and rank

Two bundled scripts. Candidate JSON shape: `{"generated_at", "date_window", "sources", "papers": [{title, abstract, authors, url, pdf_url, source, published}]}`.

**2.1 arXiv** (the primary source — "today's papers"):

Run from the **project root** (the directory containing `skills/`); script paths point into
this skill's `scripts/` folder:

```powershell
python .\skills\research-daily-ideas\scripts\fetch_arxiv_candidates.py `
   --days 2 --max-candidates 100 `
   --category cs.AI --category cs.LG --category cs.CV --category cs.CL `
   --output .\research-daily-ideas\artifacts\<DATE>\arxiv_candidates.json
```

- Default window is the last 1-3 days (`--days`); widen only if the user asks.
- `--max-candidates` is a **per-category** cap (4 categories × 100 → up to 400 candidates
  before de-duplication), not a total.
- Pick categories from the topic (Mode A) or from the corpus's dominant areas (Mode B);
  `cs.AI cs.LG cs.CL cs.CV` is the safe default.
- If the topic is non-CS (e.g. bio/med), also collect candidates from bioRxiv/medRxiv via
  WebSearch/WebFetch and normalize them into the same candidate shape
  → `ARTIFACTS/<DATE>/web_candidates.json`.

**2.2 Web sources (optional, topic-driven):** for a specific TOPIC, optionally supplement with
recently accepted/proceedings papers (CVPR, ECCV, NeurIPS, ICLR, AAAI…) via WebSearch/WebFetch,
normalized into `web_candidates.json`. Always preserve abstracts. Skip this for broad `all`
runs — the arXiv feed is enough.

**2.3 Merge + rank:** merge `arxiv_candidates.json` (+ `web_candidates.json` if present) into
`ARTIFACTS/<DATE>/candidate_papers.json` (dedupe by normalized title; keep the most complete
record), then rank against the corpus. The fetch script can do the merge for you — re-run
step 2.1 with `--existing .\research-daily-ideas\artifacts\<DATE>\web_candidates.json` and
`--output .\research-daily-ideas\artifacts\<DATE>\candidate_papers.json`; otherwise merge by hand:

```powershell
python .\skills\research-daily-ideas\scripts\rank_candidates.py `
   --corpus      .\research-daily-ideas\artifacts\<DATE>\zotero_corpus.json `
   --candidates  .\research-daily-ideas\artifacts\<DATE>\candidate_papers.json `
   --output      .\research-daily-ideas\artifacts\<DATE>\ranked_papers.json `
   --top-k <TOP_K>
```

The ranker de-duplicates, drops papers already in the corpus, embeds `title + abstract`, and
scores `100 * (0.65*weighted_corpus_sim + 0.35*max_corpus_sim)`; each ranked paper carries
`score` and `matched_corpus` (top interest-library neighbors — use these in step 6 to explain
*why* a paper matters to the user).

**Verification gate:** before step 3, read the top papers' abstracts and confirm they actually
fit the topic / user interests. Demote or drop clearly off-topic hits (re-rank manually by
editing `ranked_papers.json`). Never let a score alone decide.

## Step 3 — Download paper sources (script)

```powershell
python .\skills\research-daily-ideas\scripts\download_paper_sources.py `
   --ranked    .\research-daily-ideas\artifacts\<DATE>\ranked_papers.json `
   --date      <DATE> `
   --artifacts .\research-daily-ideas\artifacts
```

For every ranked paper the script (resume-safe — existing `figures.json` skips the paper):

- downloads the **PDF** → `ARTIFACTS/<DATE>/papers/{paper_id}/paper.pdf`
- downloads and extracts the **arXiv source package** → `.../papers/{paper_id}/source/`
  (non-arXiv papers skip this; they get PDF text extraction instead)
- writes a readable **`text_dump.txt`** (main .tex with preamble/comments stripped, `\input`
  inlined, capped at ~100k chars) — this is the primary analysis input
- extracts figure references from the LaTeX (filename + caption, heuristic type label:
  Task / Method / Result), copies the figure files to `.../papers/{paper_id}/figures/`, and
  converts vector figures to embeddable raster: **PDF→PNG via PyMuPDF @200dpi, EPS→PNG via
  Ghostscript**; PNG/JPG/SVG are kept as-is
- writes `.../papers/{paper_id}/figures.json` (per-figure `local_path`, `embeddable_path`,
  `format`, `caption`, `type`) and a global `download_manifest.json`

`paper_id` is the arXiv ID (`2401.12345`) when available, else a title slug.

## Step 4 — Deep per-paper analysis (agent)

For each paper in `ranked_papers.json` (**in rank order**), produce one analysis entry using
the local artifacts from step 3. **No Ollama, no API — the agent does the reading and
writing.** Work in **batches of ~5 papers** and append each batch's entries to
`ARTIFACTS/<DATE>/analyzed_papers.json` as you go — an interrupted run keeps the
highest-ranked analyses on disk.

Inputs per paper (under `ARTIFACTS/<DATE>/papers/{paper_id}/`):
- `text_dump.txt` — primary input (LaTeX body or PDF text). If both are empty, fall back to
  the abstract and mark the entry `analysis_depth: "abstract-only"`.
- `figures.json` — the extracted figure list with captions and type hints.
- `paper.pdf` / `source/` — consult for anything the dump is missing (tables, equations).

Writing rules:
- **Language:** all narrative fields in fluent Chinese; paper titles, tags, and figure
  captions stay in their original English.
- **Figures:** pick at most one **task_figure** (teaser/problem/results figure) and one
  **methodology** (architecture/pipeline/framework figure) using the `type` hint + caption +
  filename; verify by actually looking at the image file when ambiguous. Keep `filename`
  (original path in source) AND `embeddable_path` (the converted/copy under `figures/`).
  If no suitable figure exists, use empty strings — never fabricate.
- **Depth:** substantially more than an abstract digest — background, specific problem,
  motivation, concrete method (name the components/losses/metrics where the source shows them),
  2-3 contributions, 1-2 limitations, and three transferability angles (model ideas / research
  direction / visualization).

**Per-paper entry schema** (all entries in `ARTIFACTS/<DATE>/analyzed_papers.json`):

```json
{
  "paper_id": "2401.12345",
  "title": "Paper title",
  "authors": "Author A, Author B",
  "date": "2026-08-24",
  "url": "https://arxiv.org/abs/2401.12345",
  "source": "arxiv:cs.CV",
  "rank": 1,
  "score": 91.2,
  "matched_corpus_titles": ["Nearest Zotero paper title", "..."],
  "domain": "多模态学习 / 3D 人脸动画",
  "topic": "3d-facial-animation",
  "tags": ["multimodal", "3d-face", "video-generation"],
  "quality_score": 8.8,
  "one_line_summary": "一句话中文总结。",
  "research_background": "中文：研究背景。",
  "research_problem": "中文：具体研究问题。",
  "motivation": "中文：动机与价值。",
  "method_detail": "中文：方法细节（组件、损失、指标、消融结论）。",
  "task_figure": {
    "filename": "figures/teaser.pdf",
    "embeddable_path": "research-daily-ideas/artifacts/2026-08-24/papers/2401.12345/figures/teaser.png",
    "format": "png",
    "caption": "Original English caption."
  },
  "methodology": {
    "filename": "figures/pipeline.pdf",
    "embeddable_path": "research-daily-ideas/artifacts/2026-08-24/papers/2401.12345/figures/pipeline.png",
    "format": "png",
    "caption": "Original English caption."
  },
  "main_contributions": ["贡献 1", "贡献 2"],
  "limitations": ["局限 1"],
  "transferability_model_ideas": "中文：模型思路可迁移到何处。",
  "transferability_directions": "中文：研究方向可迁移到何处。",
  "transferability_visualization": "中文：可视化/评估思路可借鉴之处。",
  "analysis_depth": "full"
}
```

`domain` and `topic` must match the PKBase's SCHEMA taxonomy (pick the closest existing
domain/topic from step 0; if genuinely new, note it for step 5 to register in SCHEMA).
`matched_corpus_titles` comes from the ranked paper's `matched_corpus` — it powers step 6.
`quality_score` (1-10) follows the rubric in
[references/paper-analysis.md](./references/paper-analysis.md).

## Step 5 — Ingest analyses into PKBase

File every analyzed paper into the PKBase **using the existing page types — no new structure
is needed**: each paper is a *source*, its figures are *assets*, its durable knowledge becomes
*concept* pages. Follow `wiki-pk-base` conventions exactly (see
[references/pkbase-integration.md](./references/pkbase-integration.md) for the per-paper recipe).

Per paper (using `domain`/`topic` from step 4):
1. **Raw (immutable):** copy `paper.pdf` →
   `raw/papers/<domain>/<topic>/YYYYMMDD-arxiv-<paper_id>.pdf`, and the embeddable figures →
   `raw/assets/<domain>/<topic>/<paper_id>_task.png` / `<paper_id>_method.png`
   (copy, never move; collision → `-2` suffix).
2. **Source summary:** create `wiki/sources/<domain>/<topic>/<paper-slug>.md` at the SCHEMA's
   depth level, with frontmatter (`title`, `domain`, `topic`, `created`, `source`, `depth`,
   `tags`, `quality_score`, `arxiv_id`), the Chinese analysis content, an ASCII diagram of the
   method, and **embedded figures** `![[<paper_id>_task.png]]` (Obsidian resolves by file
   name). Keep original figure captions as quoted text.
3. **Concept pages:** extract 2-5 granular concepts (algorithm, architecture component,
   dataset/benchmark, key limitation…). For each: search the whole `wiki/` first — update an
   existing concept (append insights, add to `sources:`, bump `updated`) or create
   `wiki/concepts/<domain>/<topic>/<concept-name>.md`. Every page gets ≥2 `[[wikilinks]]`.
4. **Navigation:** add new pages to `index.md` (correct domain/topic section, one line each
   with summary + tags), append the run's batch to `log.md`
   (`## [DATE] ingest | Daily papers <DATE> (N papers)` with per-paper detail), and — per the
   PKBase web rule — **rebuild the site** so it shows the new pages: prefer
   `site/rebuild_site.py` when the PKBase has one
   (`python <PKBASE_PATH>\site\rebuild_site.py <PKBASE_PATH>` — regenerates `data.js`, bumps
   `?v=`, prints the report line); otherwise regenerate `site/data.js` manually per the
   `wiki-pk-base` rebuild procedure.

Tags must come from the SCHEMA taxonomy; register a new tag in SCHEMA *before* using it.
If a run would touch 10+ existing pages, confirm scope with the user first.

## Step 6 — Research ideas for the day's topic (agent)

Synthesize research ideas grounded in **three** inputs:

1. today's analyzed papers (`analyzed_papers.json` — esp. `limitations` and `transferability_*`),
2. the PKBase's existing knowledge on the topic (read `index.md` sections for the domain/topic,
   then the relevant concept + source pages — this is the "existing knowledge" the ideas must
   build on, not ignore),
3. the user's own interest signals (corpus `matched_corpus` neighbors, annotations/notes from
   step 1 when present).

Produce 3-8 ideas. Each idea must have:
- **一句话 idea（中文）+ 英文 title**
- **动机与空白** — what gap in today's papers or the PKBase it targets, citing specific
  papers/concepts (`[[wikilinks]]` to PKBase pages, arXiv IDs for today's papers)
- **具体做法** — a concrete, falsifiable research plan (method sketch, expected evaluation)
- **可行性** — difficulty / data / compute estimate, and which of today's papers' code or
  assets could be reused
- **与已有知识的衔接** — which existing PKBase concepts it extends, and which it would create

Write the ideas as a **query page** in the PKBase (durable, searchable, cross-linked):

```
wiki/queries/<domain>/<topic>/daily-<DATE>-<topic-slug>.md
```

frontmatter: `title: "每日研究想法 - <DATE> <Topic>"`, `domain`, `topic`, `created`,
`sources:` (today's paper source slugs + consulted concept pages), `tags` (taxonomy,
including `daily-ideas`).
Body: the 检索范围 block (date window, sources, TOP_K, topic), then the ideas, then a
`## 今日论文速览` section (rank, title, one_line_summary, quality_score per paper) so the page
is self-contained. Add it to `index.md` → Queries, log it, and **rebuild the site** if you
haven't since step 5.

**Site display:** the `daily-<DATE>-*` slug (and the `daily-ideas` tag) makes this page the
site's **每日论文看看 / Daily Papers** entry for the day — the PKBase home shows it in that
standalone section (last 3) and, by design, excludes it from the 查询记录 / Queries column.

Then present in chat: the top 3-5 ideas in full, the rest as one-line summaries, plus the
run report (counts per step, paths, site rebuild line).

## Quality bar

- Every number in reports is real: state the exact date window, N candidates → N ranked →
  N downloaded → N analyzed → N filed.
- The analysis JSON must be complete for every downloaded paper; a paper with no source and no
  PDF text is still analyzed from the abstract, marked `analysis_depth: "abstract-only"`.
- Every PKBase page created/updated follows SCHEMA conventions (frontmatter, taxonomy tags,
  ≥2 wikilinks, depth level) — when in doubt, re-read the `wiki-pk-base` skill's templates.
- Every figure embedded in a PKBase page is a file that actually exists under `raw/assets/`
  (the pipeline's `embeddable_path` — never a URL, never a path into the transient
  `ARTIFACTS/` dir, never an unconverted PDF/EPS).
- Ideas are grounded: every idea cites at least one of (today's paper, PKBase page, user
  interest signal). No generic "apply X to Y" without a stated gap.
- The site is rebuilt at the end of the run — a PKBase site that lags the vault is a bug.

## Bundled assets

- [scripts/fetch_arxiv_candidates.py](./scripts/fetch_arxiv_candidates.py) — arXiv recent-paper fetch → candidate JSON (step 2.1)
- [scripts/rank_candidates.py](./scripts/rank_candidates.py) — weighted semantic ranking against the corpus (step 2.3)
- [scripts/download_paper_sources.py](./scripts/download_paper_sources.py) — source/PDF download, text dump, figure extraction + raster conversion (step 3)
- [references/paper-analysis.md](./references/paper-analysis.md) — step 4 depth guidelines and worked example
- [references/pkbase-integration.md](./references/pkbase-integration.md) — step 5 per-paper filing recipe + site rebuild checklist
- [references/research-ideas.md](./references/research-ideas.md) — step 6 idea taxonomy and quality rubric
- [requirements.txt](./requirements.txt) — Python dependencies
