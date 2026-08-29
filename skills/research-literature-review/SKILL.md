---
name: research-literature-review
description: "collect, normalize, de-duplicate, and organize research papers into a single output: a direction-focused background review that captures the existing research foundation for a topic or a user-written research-direction overview. Reads the user's Zotero library, their Obsidian vault (including a PKBase knowledge base), and web sources; can file the finished review into a PKBase as a comparison page. Use when user asks to find papers, do a literature review, collect related work, compare recent papers, understand what a paper says, or needs to build prior-work coverage, map existing literature, expand a research-direction summary into retrieval facets, gather papers from zotero, obsidian, and web sources, or export structured json files for downstream analysis."
version: 2.1.0
author: Zhihao Li
license: MIT
argument-hint: "topic: '3D Facial Animation' | overview: <user research-direction text>"
metadata:
  tags: [research, literature-review, survey, zotero, obsidian, pkbase]
  category: research
  related_skills: [wiki-pk-base, research-daily-ideas, zotero]
  hermes:
    tags: [Research, Literature, Review]
---
# Research Literature Review

Research topic: $ARGUMENTS

(If `$ARGUMENTS` is empty, ask the user for the topic or derive it from the surrounding
conversation.)

## Constants

- **REVIEW_TOPIC** - a short topic label for the main direction
- **TOPIC_OVERVIEW** - optional user-written research direction overview; may be several sentences or paragraphs
- **FOUNDATION_OUTPUT_JSON** - `artifacts/<DATE>-<topic-slug>/research_foundation_review.json`
  (relative to the **project root**, the directory containing `skills/`; `<DATE>` = run date
  `YYYY-MM-DD`, `<topic-slug>` = kebab-case `REVIEW_TOPIC` — one folder per review, never
  overwrite a previous run's output)
- **SCHEMA_VERSION** - `1.0`

## Goal

Produce a structured JSON file that uses one canonical paper schema:

1. `research_foundation_review.json`: existing research foundation for the main direction

## Input interpretation

Treat topic input as one of three modes:

1. keyword topic only
2. user-written overview only
3. both keyword topic and user-written overview

When `TOPIC_OVERVIEW` is provided, do not treat it as raw search text only. First extract:

- problem setting
- target tasks
- method families
- application domains
- benchmarks or data signals
- synonyms and adjacent terms
- explicit exclusions if the overview mentions them

Use these extracted facets to drive Step 1 retrieval. If the user only provides a long research-direction description and no short topic label, derive a concise `REVIEW_TOPIC` from the overview.

## Shared canonical paper JSON schema

All retained items from all sources must be normalized into this shared structure.

```json
{
  "id": "stable-paper-id",
  "title": "Paper title",
  "authors": ["Author A", "Author B"],
  "year": 2025,
  "venue": "Conference or journal",
  "abstract": "Abstract text",
  "url": "https://example.org/paper",
  "pdf_url": "https://example.org/paper.pdf",
  "pdf_path": "raw/papers/<domain>/<topic>/20260101-arxiv-2501-01234.pdf",
  "doi": "10.1000/example",
  "arxiv_id": "2501.01234",
  "citation_key": "Smith2025",
  "bibtex": "@article{Smith2025, ...}",
  "pkbase_page": "wiki/sources/<domain>/<topic>/<source-slug>.md",
  "source": ["zotero", "web"],
  "source_priority": 1,
  "topic_tags": ["planning", "diffusion"],
  "paper_role": "survey",
  "source_metadata": {
    "zotero": {},
    "obsidian": {},
    "web": {}
  },
  "problem": "What gap does it address?",
  "method": "Core technical contribution (1-2 sentences)",
  "results": "Key numbers/claims",
  "relevance": "How does it relate to our work?",
  "summary": "Short normalized summary if available",
  "notes": "Merged notes, highlights, or user insights if available"
}
```

### Schema rules

- Use one common schema for all sources.
- Put source-specific fields under `source_metadata.<source>`.
- Allow missing fields to be `null`, omitted, or empty.
- `abstract` must preserve all original sentences from the collected source materials verbatim.
- `source` must list all contributing sources for the merged record.
- `source_priority` must use the highest-priority contributing source:
  - `1` = Zotero
  - `2` = Obsidian
  - `3` = Web
- `topic_tags` should capture the topic, derived facet, or matched latest direction.
- `paper_role` should help explain why the paper is retained. Use values such as `survey`, `milestone`, `benchmark`, `method`, `application`, or `latest`.
- `pdf_path` holds the **local** PDF path when one exists (a Zotero attachment or a PKBase
  `raw/papers/...` file), otherwise `null` — never fabricate a path.
- `pkbase_page` holds the path of the paper's existing PKBase source page
  (`wiki/sources/<domain>/<topic>/<slug>.md`) when the paper has already been ingested
  there, otherwise `null`.
- **Language:** narrative fields (`problem`, `method`, `results`, `relevance`, `summary`,
  `notes`) are written in fluent Chinese; titles, venues, author names, tags, and abstracts
  stay in their original language.

### Stable ID rules

Generate `id` using the best available identifier in this order:

1. DOI
2. arXiv ID
3. normalized canonical URL
4. normalized title
5. title + first author + year

## Workflow

### Step 1: Collect the existing research foundation for the main direction

Goal: build a review-oriented corpus that reflects the existing research basis of the field, not only the latest papers.

1. Interpret `REVIEW_TOPIC` and `TOPIC_OVERVIEW`.
2. Derive review facets such as surveys, milestone methods, benchmarks, applications, and adjacent directions.
3. Collect papers from Zotero, PKBase/Obsidian, and web sources.
4. Normalize the collected records to the canonical JSON schema.
5. **Corpus size target:** aim for 30-80 merged papers. Coverage beats volume: every
   relevant survey, milestone method, and benchmark must be in the corpus; recent (last
   2 years) methods come from the web. Do not pad with loosely related papers.
6. **Verification gate:** before Step 2, read the abstracts of the top candidates and drop
   clearly off-topic hits. Never let keyword matching alone decide retention.

Based on the above canonical JSON schema, the final output JSON will use the following structure:

```json
{
  "review_topic": "Research topic",
  "topic_overview": "Optional user-written overview",
  "generated_at": "2026-03-31T12:00:00Z",
  "schema_version": "1.0",
  "input_mode": "keyword|overview|keyword+overview",
  "derived_facets": [
    {
      "facet": "planning under uncertainty",
      "why_included": "Appears explicitly in the overview",
      "keywords": ["uncertainty", "planning", "decision making"]
    }
  ],
  "source_status": {
    "zotero": "used|unavailable|no_match",
    "obsidian": "used|unavailable|no_match",
    "web": "used"
  },
  "review_summary": {
    "field_definition": "One-paragraph overview of the direction",
    "core_questions": ["What is the central problem?"],
    "method_families": ["diffusion", "world models"],
    "benchmark_signals": ["common datasets or evaluation setups"],
    "open_gaps": ["important unresolved issues"]
  },
  "papers": [
    {
      "id": "stable-paper-id",
      "title": "Paper title",
      "authors": ["Author A", "Author B"],
      "year": 2025,
      "venue": "Conference or journal",
      "abstract": "Abstract text",
      "url": "https://example.org/paper",
      "pdf_url": "https://example.org/paper.pdf",
      "pdf_path": "raw/papers/<domain>/<topic>/20260101-arxiv-2501-01234.pdf",
      "doi": "10.1000/example",
      "arxiv_id": "2501.01234",
      "citation_key": "Smith2025",
      "bibtex": "@article{Smith2025, ...}",
      "source": ["zotero", "web"],
      "source_priority": 1,
      "topic_tags": ["diffusion", "planning"],
      "paper_role": "survey",
      "source_metadata": {
        "zotero": {},
        "web": {}
      },
      "problem": "What gap does it address?",
      "method": "Core technical contribution (1-2 sentences)",
      "results": "Key numbers/claims",
      "relevance": "How does it relate to our work?",
      "summary": "Short normalized summary if available",
      "notes": "Merged notes, highlights, or user insights if available"
    }
  ]
}
```

#### Data Sources

This skill checks sources in priority order. All are optional except Web.

| Priority | Source     | ID           | What it provides                                                                  |
| -------- | ---------- | ------------ | --------------------------------------------------------------------------------- |
| 1        | Zotero     | `zotero`   | collections, tags, annotations, citation metadata, BibTeX                         |
| 2        | Obsidian   | `obsidian` | research notes, summaries, ratings, wikilinks, local metadata (PKBase vaults: source/concept pages + raw PDF paths) |
| 3        | Web search | `web`      | arXiv, Semantic Scholar, Google Scholar, conference accepted papers / proceedings |

If Zotero or Obsidian tools are unavailable, skip them but **always report it** in the final
output (set `source_status` to `unavailable`).

Practical retrieval notes learned in use:

- For Zotero, a short topic query plus one or two adjacent facet queries often finds better coverage than a single broad search string.
- For recent methods, semantic search is usually better than title search for broad topic discovery; then fetch item metadata for the shortlisted papers.
- If Obsidian MCP returns repeated directory errors or becomes unreachable, stop retrying that source and continue with Zotero/Web only.
- If web search tooling is limited, the arXiv API is a reliable fallback for recent papers and benchmark/milestone discovery.
- Zotero semantic search uses relevance scoring that can miss papers even when they are in the library. After semantic search, ALWAYS do targeted title-based searches for specific papers mentioned in the user's topic overview or related work tables — these are high-priority must-include papers that semantic search may not surface.
- When the user provides a topic overview with a related work table or method names, extract those paper titles/keywords and search for each one individually in Zotero. This catches milestone and key-method papers that semantic search ranking may bury.

#### 1: Zotero

If available (using the Zotero MCP tools, `mcp__zotero__*`):

- Use the Zotero MCP tools to retrieve items from the user's Zotero library
- Prioritize retrieving metadata, annotations, tags, and collection information for the topic/facets derived in Step 1
- **Rank and select, don't dump:** score each candidate item with the auditable weight
  formula used by the `research-daily-ideas` skill (annotation / tag / collection / recency signals —
  see its Step 1) and keep the top ~15 per facet; a review corpus is a curated set, not the
  whole library
- **Resolve local PDFs:** when an item has a local PDF attachment, record its path in
  `pdf_path` (later PKBase filing can copy it instead of re-downloading)
- Normalize each retrieved item into the canonical schema
- Store Zotero-specific fields (like collections, tags, and annotations) under `source_metadata.zotero`
- The final deduplication and merging with other sources will be handled in the subsequent steps

Example Zotero-specific fields:

```json
{
  "added_date": "2026-03-27T10:20:30Z",
  "collections": ["Collection/Path"],
  "tags": ["llm", "reasoning"],
  "annotations": [
    {
      "page": 3,
      "text": "Important highlighted sentence",
      "comment": "Why this matters",
      "color": "#ffd400"
    }
  ]
}
```

#### 2: Obsidian (including PKBase vaults)

If available:

- Resolve the vault via `$OBSIDIAN_VAULT_PATH` (or the user's known vault location).
- **If the vault is a PKBase** (a `SCHEMA.md` sits at the vault root — the user's PKBase is
  their Obsidian vault), it is the richest local source:
  - read `wiki/sources/<domain>/<topic>/*.md` — frontmatter gives `title`, `domain`,
    `topic`, `tags` (→ `topic_tags`), and `source:` (the raw PDF path → `pdf_path`); the
    body is a ready-made Chinese summary (→ `summary` / `notes`)
  - read the relevant `wiki/concepts/<domain>/<topic>/` pages for the field's current state
    (feeds `review_summary.method_families` / `open_gaps`)
  - set `source_metadata.obsidian.note_path` and `pkbase_page` to the wiki page path (the
    paper is already filed)
  - skip the vault's sibling translation files (`<slug>.en.md` / `<slug>.zh.md`) — the base
    page is canonical
- **Otherwise**, fall back to the classic layout: only retrieve data from the
  `ResearchPapers` directory
- search topic-related notes and overview-derived facet keywords
- check relevant tags; read summaries, insights, and wikilinks
- map notes to specific papers when possible
- normalize each retained paper into the canonical schema
- store Obsidian-specific fields under `source_metadata.obsidian`
- only create a paper record when the note can be mapped confidently to a specific paper

Example Obsidian-specific fields:

```json
{
  "note_title": "Diffusion Planning Notes",
  "note_path": "ResearchPapers/diffusion-planning.md",
  "summary": "User's summary or interpretation",
  "tags": ["paper-review", "planning"],
  "wikilinks": ["RelatedNoteA", "RelatedNoteB"],
  "frontmatter": {
    "status": "reading",
    "rating": 4,
    "paper_url": "https://example.org/paper"
  }
}
```

#### 3: Web

Always available:

- for arXiv fetching, use this skill's **bundled script**
  (`scripts/fetch_arxiv_candidates.py` — identical to the `research-daily-ideas` skill's copy, so this
  skill is self-contained even when `research-daily-ideas` is not installed):
  `python .\skills\research-literature-review\scripts\fetch_arxiv_candidates.py --category <cat> --days <n> --max-candidates <n> --output .\artifacts\<DATE>-<topic-slug>\arxiv_candidates.json`
  — handles rate limiting and retries; the only pip dependency is `pyyaml` (the rest is
  stdlib). Use the raw arXiv API / WebFetch only as a last resort.
- search for surveys, tutorials, literature reviews, benchmark papers, and representative venue papers from the last 2 years
- include milestone papers and field-defining baselines outside the latest 2 years when needed
- check official accepted papers or proceedings pages for the most relevant conference and journal venues
- use Semantic Scholar, Google Scholar, and official venue pages when helpful

Common conferences to check when relevant:

- computer vision:
  - CVPR
  - ICCV
  - ECCV
- AI / ML:
  - NeurIPS
  - ICML
  - ICLR
  - AAAI
  - IJCAI
- graphics / generative:
  - SIGGRAPH
  - SIGGRAPH Asia

Normalize each retained web result into the canonical schema and store web-specific provenance under `source_metadata.web`.

Example Web-specific fields:

```json
{
  "discovery_source": "arxiv",
  "search_query": "diffusion model planning",
  "published_date": "2025-02-10",
  "updated_date": "2025-02-15",
  "categories": ["cs.CV", "cs.LG"],
  "official_venue_page": "https://cvpr.thecvf.com/"
}
```

### Step 2: De-duplicate and merge all normalized records

After collecting and normalizing all source results, merge them into one final paper list and save them to `FOUNDATION_OUTPUT_JSON`.

Use this de-duplication priority:

1. exact DOI match
2. exact arXiv ID match
3. exact normalized URL match
4. highly similar normalized title match
5. fallback: title + first author + year

When duplicates are found within one output:

- keep one merged canonical record
- merge `source` into one combined list
- merge all source-specific data into `source_metadata`
- prefer richer bibliographic metadata from Zotero
- prefer user's summaries and interpretations from Obsidian/PKBase
- prefer freshest publication metadata from Web or arXiv
- prefer an existing local `pdf_path` (Zotero attachment / PKBase `raw/`) over a download URL
- never discard annotations, tags, note summaries, or provenance if they can be preserved

**PKBase cross-check:** for each merged record, check whether the paper already has a source
page in the PKBase (search `wiki/sources/` by arXiv ID, then normalized title). If yes, set
`pkbase_page` to that page's path — Step 4 links it instead of re-summarizing it.

If fields conflict:

- prefer DOI and arXiv ID as highest-trust identifiers
- prefer the longer non-empty abstract
- prefer the more complete author list
- prefer official venue names and official paper URLs


### Step 3: Analyze and Synthesize

After merging, for each relevant paper (from all sources), extract and populate these analytical fields in the canonical JSON:

- `problem`: What gap does it address?
- `method`: Core technical contribution (1-2 sentences).
- `results`: Key numbers/claims.
- `relevance`: How does it relate to our work?
- `summary`: A short normalized summary if enough information exists.
- `notes`: Merged highlights, comments, or user notes when useful.

Finally, synthesize the findings to populate the top-level `review_summary` in the `FOUNDATION_OUTPUT_JSON`:

- Group papers by approach or method families.
- Identify consensus vs disagreements in the field (core questions).
- Find open gaps that our work could fill.

### Step 4: File the review into PKBase (optional — when a PKBase is involved)

When a PKBase is available (the Obsidian vault read in Step 1 is one, or `$PKBASE_PATH`
resolves to an existing vault — default `~/PKBase`), file the finished review durably. Ask
the user if the intent is ambiguous; default to filing when the review is substantial
(10+ merged papers).

1. **Classify:** pick the domain/topic per the PKBase's `SCHEMA.md` (closest existing one;
   if genuinely new, propose it to the user and register it in `SCHEMA.md → ## Domains &
   Topics` before filing).
2. **Comparison page:** create `wiki/comparisons/<domain>/<topic>/<review-slug>.md`
   (`<review-slug>` = kebab-case topic + date, e.g. `20260829-3d-facial-animation-background`),
   per the `wiki-pk-base` comparison-page conventions:
   - frontmatter: `title`, `domain`, `topic`, `created`, `sources:` (plain paths of the
     `wiki/sources/...` pages drawn from), `tags` (SCHEMA taxonomy only — register new tags
     there first)
   - body: the `review_summary` content (field definition, method families, core questions,
     open gaps), then a per-paper table (title, year, venue, role, one-line relevance) where
     each paper links to its source page when `pkbase_page` is set
     (`[[wiki/sources/<domain>/<topic>/<slug>|Title]]`), else to its URL
   - ≥2 `[[wikilinks]]` to existing pages (PKBase rule)
   - papers already in the PKBase are **linked, never re-summarized**; newly found papers
     are recorded by URL only — ingesting them is a separate `wiki-pk-base` `add` run, done
     only when the user asks
3. **Navigation:** add the page to `index.md` (Comparisons section, one line with summary +
   tags) and append to `log.md`:
   `## [<DATE>] create | Literature review: <REVIEW_TOPIC>` with the page path and paper
   count.
4. **Site rebuild:** prefer `site/rebuild_site.py` when present
   (`python <PKBASE_PATH>\site\rebuild_site.py <PKBASE_PATH>`); otherwise regenerate
   `site/data.js` per the `wiki-pk-base` rebuild procedure. Include the report line
   `site rebuilt (N pages, M raw files)`.

## Output expectations

When reporting results to the user:

- say which sources were successfully used
- say if Zotero or Obsidian were unavailable
- report how many raw results were collected from each source
- report how many merged papers remained after de-duplication
- report where the final JSON file was saved
- if Step 4 ran: report the comparison page path, the index/log updates, and the site
  rebuild line

If Zotero BibTeX was exported, include a `references.bib` snippet for direct use in paper writing.

## Bundled assets

- [scripts/fetch_arxiv_candidates.py](./scripts/fetch_arxiv_candidates.py) — arXiv recent-paper fetch → candidate JSON (Step 1, web source). Identical to the `research-daily-ideas` skill's copy; keep the two in sync if one is updated.
