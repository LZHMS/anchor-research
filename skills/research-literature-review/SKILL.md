---
name: research-literature-review
description: "collect, normalize, de-duplicate, and organize research papers into a single output: a direction-focused background review that captures the existing research foundation for a topic or a user-written research-direction overview. Optionally reads the user's Zotero library, PKBase knowledge base, Obsidian research notes, and web sources; every source can be enabled or disabled independently. Can file the finished review into a PKBase as a comparison page. Use when user asks to find papers, do a literature review, collect related work, compare recent papers, understand what a paper says, or needs to build prior-work coverage, map existing literature, expand a research-direction summary into retrieval facets, gather papers from zotero, pkbase, obsidian, and web sources, or export structured json files for downstream analysis."
version: 2.7.0
author: Zhihao Li
license: MIT
argument-hint: "topic: '3D Facial Animation' | overview: <user research-direction text> | sources: [zotero, pkbase, obsidian, web] | project: <current-project-root>"
metadata:
  tags: [research, literature-review, survey, zotero, obsidian, pkbase]
  category: research
  related_skills: [research-literature-summary, research-ideas, research-experiment-plannning, wiki-pk-base, research-daily-ideas, zotero]
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
- **ENABLED_SOURCES** - optional list of source IDs: `zotero`, `pkbase`, `obsidian`, `web`;
  defaults to all four when omitted; an explicit list enables only the listed sources
- **PROJECT_ROOT** - explicit `project`/project-root argument, otherwise an accepted
  handoff's bound `project_root`, otherwise the current working project directory;
  never infer it from the installed skill/script location. Resolve relative input/output
  arguments against this root.
- **DOCS_ROOT** - `{PROJECT_ROOT}/docs`.
- **REVIEW_DIR** - `{DOCS_ROOT}/research-literature-review`, the fixed current-material
  folder for this project.
- **FOUNDATION_OUTPUT_JSON** - `{REVIEW_DIR}/research_foundation_review.json`.
- **SKILL_DIR** - the installed directory containing this `SKILL.md`.
- **SCRIPT_PATH** - absolute installed skill asset path
  `{SKILL_DIR}/scripts/fetch_arxiv_candidates.py`; installed assets are not project roots.
  All review JSON and web intermediates, including `arxiv_candidates.json`, live in
  `REVIEW_DIR`, not the installed skill directory.
- **SCHEMA_VERSION** - `1.1`
- **CORPUS_STATE** - `{REVIEW_DIR}/CORPUS_STATE.json`, owned by this skill and maintained
  by the host assistant, not the retrieval script.

### Updating current project materials

Each execution updates `FOUNDATION_OUTPUT_JSON` and current web intermediates directly
in `REVIEW_DIR`; do not allocate date/suffix folders or search for a newest historical
review. Bind downstream work to the actual absolute input path and its canonical JSON
SHA256: UTF-8 `json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))`.
Changing the review invalidates a previously bound summary, pending choice, or proposal.
Disclose these stale downstream bindings; old summaries, selections, and review scores
are not approval of the updated corpus. Refresh/reconfirm downstream work against the
new content instead of silently reusing it. Do not automatically move or delete old
user-owned files or historical folders.

Before replacing previously approved material, preserve its exact bytes, approval and
explicit revision references; keep that accepted revision distinct from the new draft.
Preserving a revision does not permit historical/latest-by-mtime input discovery.

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

### Source selection

Resolve `ENABLED_SOURCES` before any retrieval, from `sources: [...]` or the user's explicit
source preferences. Every source is optional, including Web; do not require any tool or
local library to run this skill.

- Omitted `sources`: try all four sources that are available.
- Explicit `sources`: use only that list; never silently add a fallback source.
- Natural-language exclusions (e.g. "不要联网") disable the corresponding source (`web`),
  even when its tools are available.
- An empty list means no retrieval. Save an empty `papers` list and empty
  `review_summary` fields, report that no sources were selected, and do not invent a review.
- If enabled sources are unavailable or return no relevant papers, keep the same empty
  output behavior and report each source's status; do not enable an excluded source to
  reach the corpus size target.

Examples:

```yaml
sources: [pkbase]                  # PKBase only; no Zotero, Obsidian, or Web
sources: [zotero, pkbase, obsidian] # Local sources only
sources: [web]                     # Web only; no local libraries required
sources: []                        # No retrieval
```

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
  "source": ["zotero", "pkbase", "obsidian", "web"],
  "source_priority": 1,
  "topic_tags": ["planning", "diffusion"],
  "paper_role": "survey",
  "source_metadata": {
    "zotero": {},
    "pkbase": {},
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
- Put source-specific fields under `source_metadata.<source>`; include only contributing sources.
- Allow missing fields to be `null`, omitted, or empty.
- `abstract` must preserve all original sentences from the collected source materials verbatim.
- `source` must list all contributing sources for the merged record.
- `source_priority` must use the highest-priority contributing source:
  - `1` = Zotero
  - `2` = PKBase
  - `3` = Obsidian
  - `4` = Web
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
3. Resolve `ENABLED_SOURCES` and collect papers only from enabled, available sources.
4. Normalize the collected records to the canonical JSON schema.
5. **Corpus size target:** aim for 30-80 merged papers when the selected sources support
   that coverage. Prioritize relevant surveys, milestone methods, and benchmarks; seek
   recent (last 2 years) methods from the selected sources, using Web only if enabled.
   Report coverage limitations rather than padding or enabling excluded sources.
6. **Verification gate:** before Step 2, read the abstracts of the top candidates and drop
   clearly off-topic hits. When no abstract exists, verify against available local paper
   text or source notes; do not fetch from a disabled source. Never let keyword matching
   alone decide retention.

Based on the above canonical JSON schema, the final output JSON will use the following structure:

```json
{
  "review_topic": "Research topic",
  "topic_overview": "Optional user-written overview",
  "generated_at": "2026-03-31T12:00:00Z",
  "schema_version": "1.1",
  "input_mode": "keyword|overview|keyword+overview",
  "enabled_sources": ["zotero", "pkbase", "obsidian", "web"],
  "derived_facets": [
    {
      "facet": "planning under uncertainty",
      "why_included": "Appears explicitly in the overview",
      "keywords": ["uncertainty", "planning", "decision making"]
    }
  ],
  "source_status": {
    "zotero": "used",
    "pkbase": "used",
    "obsidian": "used",
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
      "pkbase_page": "wiki/sources/<domain>/<topic>/<source-slug>.md",
      "source": ["zotero", "pkbase", "obsidian", "web"],
      "source_priority": 1,
      "topic_tags": ["diffusion", "planning"],
      "paper_role": "survey",
      "source_metadata": {
        "zotero": {},
        "pkbase": {},
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
  ]
}
```

#### Data Sources

Check only enabled sources, in priority order. All four sources are optional.

| Priority | Source     | ID         | What it provides |
| -------- | ---------- | ---------- | ---------------- |
| 1        | Zotero     | `zotero`   | collections, tags, annotations, citation metadata, BibTeX |
| 2        | PKBase     | `pkbase`   | source summaries, concept/comparison pages, taxonomy, local raw paper paths |
| 3        | Obsidian   | `obsidian` | research notes, summaries, ratings, wikilinks, local metadata outside PKBase pages |
| 4        | Web search | `web`      | arXiv, Semantic Scholar, Google Scholar, conference accepted papers / proceedings |

Save the resolved list in `enabled_sources`. Always include all four IDs in `source_status`,
each with exactly one status:

- `disabled`: excluded by source selection; do not probe its tools, paths, or content.
- `unavailable`: enabled, but its tools or local files cannot be accessed.
- `no_match`: enabled and searched successfully, but no relevant paper or synthesis context
  was retained.
- `used`: enabled and contributed retained papers or synthesis context.

Skip unavailable sources and continue with the remaining enabled ones. Report every
source's status; unavailable Web is not fatal and disabled Web forbids web searches,
remote metadata/PDF fetching, and the arXiv script/API.

Practical retrieval notes learned in use:

- For Zotero, a short topic query plus one or two adjacent facet queries often finds better coverage than a single broad search string.
- For recent methods, semantic search is usually better than title search for broad topic discovery; then fetch item metadata for the shortlisted papers.
- If Obsidian MCP returns repeated directory errors or becomes unreachable, stop retrying that source and continue with the remaining enabled, available sources.
- If Web is enabled but web search tooling is limited, the arXiv API is a fallback for recent papers and benchmark/milestone discovery; if no web retrieval method is usable, mark Web `unavailable`.
- Zotero semantic search uses relevance scoring that can miss papers even when they are in the library. After semantic search, ALWAYS do targeted title-based searches for specific papers mentioned in the user's topic overview or related work tables — these are high-priority must-include papers that semantic search may not surface.
- When the user provides a topic overview with a related work table or method names, extract those paper titles/keywords and search for each one individually in Zotero. This catches milestone and key-method papers that semantic search ranking may bury.

#### 1: Zotero

If enabled and available (using the Zotero MCP tools, `mcp__zotero__*`):

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

#### 2: PKBase

If enabled and available, read the knowledge base directly with filesystem tools; Obsidian
MCP is not required.

- Resolve the PKBase directory (`BASE`) using this skill's path rules, not the
  `wiki-pk-base` instance-discovery rules:
  1. First extract a PKBase path explicitly provided in the user's input. Expand `~` and
     resolve relative paths against the working directory. Use it only if it is an actual
     directory; if the explicit path is missing, is a file, or cannot be accessed, mark
     `source_status.pkbase` as `unavailable` rather than silently switching bases.
  2. If the user provided no path, check `$PKBASE_PATH`. Use its expanded/resolved value
     only when it points to an actual accessible directory.
  3. If `$PKBASE_PATH` is unset, empty, or does not point to an accessible directory,
     check the default `~/PKBase` (expand `~` to the user's home directory).
  4. If neither fallback is an actual accessible directory, mark
     `source_status.pkbase` as `unavailable`, skip PKBase, and continue with other enabled
     sources. Do not create a directory or ask the user to configure one just to proceed.
  Do not infer a path from `$PKBASE_ROOT`, `<INSTANCE>_PATH`, an Obsidian vault, or child
  instance discovery. Apply these checks only when PKBase retrieval is enabled or the
  user explicitly requests PKBase filing.
- Read the instance's `SCHEMA.md`, `index.md`, and recent `log.md` first; use its taxonomy
  and index to identify topic/facet-related pages. Keep all paths scoped to that instance.
- Read matching `wiki/sources/<domain>/<topic>/*.md`: frontmatter supplies title, domain,
  topic, tags, and `source`; the body supplies the existing summary and notes.
- Follow `source` into `raw/papers/...` when needed for identifiers, abstracts, or evidence.
  Set `pdf_path` only when an actual local PDF exists; `source` may instead refer to
  extracted Markdown, so never assume it is a PDF.
- Read relevant `wiki/concepts/` and `wiki/comparisons/` pages as synthesis context for
  method families and open gaps. Only create a paper record when it maps confidently to a
  specific paper; a concept page itself is not a paper.
- Normalize retained papers with `source: ["pkbase"]`, `source_priority: 2`, and
  `pkbase_page` set to the existing source page path relative to the instance.
- Store provenance under `source_metadata.pkbase`, including the instance name/path,
  source page, raw source path, tags, frontmatter, and related concept/comparison pages.
- Skip sibling translation files (`<slug>.en.md` / `<slug>.zh.md`); the base page is canonical.
- Retrieval is read-only; filing the review is the separate optional Step 4.

Example PKBase-specific fields:

```json
{
  "instance": "ProBase",
  "base_path": "F:/PKBase/ProBase",
  "page_path": "wiki/sources/robotics/planning/diffusion-planning.md",
  "raw_source_path": "raw/papers/robotics/planning/20260101-arxiv-2501-01234.pdf",
  "tags": ["planning", "diffusion"],
  "concept_pages": ["wiki/concepts/robotics/planning/diffusion-planning.md"],
  "comparison_pages": [],
  "frontmatter": {
    "title": "Diffusion Planning",
    "domain": "robotics",
    "topic": "planning"
  }
}
```

#### 3: Obsidian

If enabled and available:

- Resolve the vault via `$OBSIDIAN_VAULT_PATH` (or the user's known vault location).
- Only retrieve paper notes from `ResearchPapers`; PKBase `wiki/` and `raw/` content is
  owned by the separate `pkbase` source, even when both sources point to the same vault.
  Do not read PKBase content via Obsidian when `pkbase` is disabled, and do not attribute
  the same PKBase page to both source IDs merely because it is opened in Obsidian.
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

#### 4: Web

If enabled and a web retrieval method is available:

- for arXiv fetching, use this skill's **bundled script**
  (`scripts/fetch_arxiv_candidates.py` — identical to the `research-daily-ideas` skill's copy, so this
  skill is self-contained even when `research-daily-ideas` is not installed):
  `python "<SCRIPT_PATH>" --category <cat> --days <n> --max-candidates <n> --output "<REVIEW_DIR>/arxiv_candidates.json"`
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

**PKBase cross-check:** only when `pkbase` is enabled and available, check each merged
record for an existing source page in the selected instance (search `wiki/sources/` by
arXiv ID, then normalized title). Merge any contributing PKBase metadata and provenance,
update `source` / `source_priority` and `source_status.pkbase`, and set `pkbase_page` —
Step 4 links it instead of re-summarizing it. Skip this retrieval when PKBase is disabled.

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

### Corpus result gate: approve scope before offering a summary

Apply the [shared human-anchor contract](../research-shared-references/anchor-gates.md); these
inline requirements remain binding if that reference is not installed. Retrieval,
de-duplication and technical synthesis may finish without output approval. An invocation
authorizes that work, not acceptance of the corpus that will result.

After Step 3, present the actual corpus and its path, retained-paper count, topic/facets,
exclusions, enabled/disabled/unavailable sources, coverage and evidence limitations.
Show the exact file-byte `corpus_sha256` and canonical review `input_sha256` and ask
whether the user accepts **this corpus scope, source policy and evidence limits** as
the input anchor for a deeper summary. This is not an assertion that every paper or
scientific claim is true, and it is not permission to enter the summary stage.

Persist host-owned `CORPUS_STATE.json` with actual `project_root`, `docs_root`,
`input_json`, `corpus_sha256`, `input_sha256`, `enabled_sources`, `source_status`,
`scope_constraints` (topic, overview, facets and exclusions), `evidence_limits`,
`status`, and:

```json
{
  "corpus_approval": {
    "approved": false,
    "corpus_sha256": "<actual review file-byte SHA256, or null until known>",
    "input_sha256": "<actual canonical review SHA256, or null until known>",
    "confirmation_reference": null
  }
}
```

Use `status: awaiting_corpus_approval` while waiting. Only an actual unambiguous user
acceptance of this displayed decision sets `corpus_approval.approved: true`,
`status: corpus_approved` and the real `confirmation_reference` (message/turn reference
or exact reply plus decision context). Re-read both digests before committing approval.
Unknown values stay null, never invented. Refusal sets `status: declined`, keeps
approval false and stops advancement; a requested revision remains unapproved.
Changed bytes, source policy, scope or limits set `status: stale`, invalidate affected
downstream bindings and require a freshly presented decision. Preserve prior accepted
revisions and their real confirmations; do not relabel them as approval of the draft.
Silence, timeout, autonomous mode, technical success and an earlier invocation are not
acceptance. Do not emit a next-stage offer or a ready/current approved anchor until
the matching user acceptance exists.

`CORPUS_STATE.json` is not part of `corpus_sha256` or canonical `input_sha256`; neither
the review JSON nor this state contains its own file hash. Once approved, a handoff
separately binds the actual state bytes as `corpus_state_sha256`.

### Step 4: File the review into PKBase (optional — when a PKBase is involved)

Filing is separate from source selection and corpus approval. Run it only on an explicit
user request or acceptance of a concrete filing scope (destination, page and navigation/
taxonomy/site changes). A substantial corpus, enabled `pkbase`, an existing base or a
supplied destination path alone does not grant permanent write permission. When `pkbase`
is disabled, skip all PKBase access unless the user explicitly requests saving there.
That request authorizes only destination resolution and existing-page lookup needed
for filing, not corpus retrieval; keep `source_status.pkbase` as `disabled` and do not
add PKBase provenance.
Resolve the destination `BASE` with the same user-input → `$PKBASE_PATH` → `~/PKBase`
directory checks defined in Step 1; reuse the resolved directory for retrieval and filing.
If no directory is available, skip filing and report why; do not initialize a new base.
Keep source-page paths and links scoped to the selected directory.

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
   (`python <BASE>\site\rebuild_site.py <BASE>`); otherwise regenerate
   `site/data.js` per the `wiki-pk-base` rebuild procedure. Include the report line
   `site rebuilt (N pages, M raw files)`.

## Output expectations

When reporting results to the user:

- report the resolved `enabled_sources` and all four source statuses
- say which sources were used, disabled, unavailable, or searched with no match
- report how many raw results were collected from each source (zero for disabled/unavailable
  sources), and any coverage limitations caused by source selection or availability
- report how many merged papers remained after de-duplication
- report where the final JSON file was saved
- say which current files were updated and disclose any previously bound downstream
  summary, candidate selection, or proposal made stale by changed review content
- distinguish technical completion from `CORPUS_STATE.status` and the actual pending or
  accepted corpus decision; do not claim user acceptance from successful collection
- if Step 4 ran: report the comparison page path, the index/log updates, and the site
  rebuild line

If Zotero BibTeX was exported, include a `references.bib` snippet for direct use in paper writing.

## Bundled assets

- [scripts/fetch_arxiv_candidates.py](./scripts/fetch_arxiv_candidates.py) — arXiv recent-paper fetch → candidate JSON (Step 1, web source). Identical to the `research-daily-ideas` skill's copy; keep the two in sync if one is updated.

## Next Step: Optional Handoff Confirmation Gate

The next skill is [research-literature-summary](../research-literature-summary/SKILL.md):
this skill collects and normalizes the corpus; that skill delegates one analysis agent
per paper and synthesizes the completed analyses into a deeper landscape.

### Offer the next skill only after the corpus result is approved

After reporting outputs and obtaining the separate corpus approval above, verify the
actual `FOUNDATION_OUTPUT_JSON` exists, parses, and contains at least one retained paper.
Read `CORPUS_STATE`: its actual project/path/source/scope bindings must match, and
`corpus_approval.approved` must be true with the real confirmation reference and matching
current byte `corpus_sha256` and canonical `input_sha256`. Only then offer the next step.
An empty, failed, unapproved, declined or stale corpus cannot produce a summary offer.

Resolve the saved JSON to an absolute path. Keep one pending anchor in the conversation
as `NEXT_SKILL_HANDOFF` (no extra state file is required), superseding any older unresolved
offer. Bind the actual full chat invocation and exact file bytes as well as the existing
canonical JSON digest. Directory inputs in later steps must enumerate their consumed
files; a folder name alone is not a content binding.

```json
{
  "from_skill": "research-literature-review",
  "to_skill": "research-literature-summary",
  "input_json": "<absolute path of the JSON actually saved in docs/research-literature-review>",
  "input_sha256": "<canonical JSON SHA256 of the saved review>",
  "corpus_state_path": "<actual absolute CORPUS_STATE.json>",
  "corpus_state_sha256": "<exact approved owner-state file-byte SHA256>",
  "project_root": "<actual absolute current project root>",
  "docs_root": "<actual absolute PROJECT_ROOT/docs>",
  "invocation": "/research-literature-summary input: \"<actual absolute JSON path>\" project: \"<actual absolute project root>\"",
  "artifacts": [
    {"role": "literature-review", "path": "<actual absolute JSON path>", "sha256": "<exact file byte SHA256>"},
    {"role": "corpus-approval-state", "path": "<actual absolute CORPUS_STATE.json>", "sha256": "<exact state file byte SHA256>"}
  ],
  "summary_dir": "<actual absolute PROJECT_ROOT/docs/research-literature-summary>",
  "status": "awaiting_confirmation"
}
```

Render the following recommendation with that **actual path**, not a placeholder or a
discovered historical review. This is a skill invocation in the chat, not a terminal command:

```text
下一步建议：research-literature-summary（逐篇分析并生成领域综述）
推荐调用：/research-literature-summary input: "<actual absolute JSON path>" project: "<actual absolute project root>"
是否现在执行？回复“可以”或“继续”即可；回复“暂时不要”则停在本次文献收集结果。
```

The visible skill name and input path identify the confirmation anchor. Displaying the
recommendation is not authorization to execute. If slash commands are not supported by
the host, the user can send `使用 research-literature-summary，input: "<actual absolute
JSON path>"`; the parent invokes the named skill through the host's normal skill loader.

### Cross the anchor only with the user's agreement

- A direct affirmative reply to the most recent unresolved anchor — for example
  `可以`, `继续`, `执行`, `好的`, or `yes` — authorizes this specific summary run.
  Interpret the complete reply: `可以，但先别执行` is not permission to start. Quoted
  examples, questions about the gate, and approval of another action are not consent.
- On agreement, set the anchor to `accepted` and revalidate the exact bound input path,
  every `artifacts` byte SHA256, canonical `input_sha256`, project/docs/output roots and
  invocation. A changed review or binding sets `stale`: disclose the changed binding,
  present a refreshed recommendation, and wait for a fresh specific confirmation.
  Re-read the bound corpus state and its actual `corpus_approval` against the current
  review, project, sources and scope; a matching JSON alone is not enough. Approval
  refusal or staleness stops advancement rather than refreshing consent silently.
  Otherwise
  load the `research-literature-summary` instructions, and immediately execute its full
  prepare → delegate → synthesize-input → synthesize + overview sidecar → finalize
  workflow with the bound `input_json`, `project_root`, and `summary_dir`.
  Stop on missing/mismatched bound artifacts or project/output paths; do not substitute
  a historical input. Do not ask for the input again or for the same confirmation twice.
- Carry the original review's source restrictions through its JSON. Agreement authorizes
  the summary workflow and draft outputs, not unrelated skills, relaxed source selection,
  or permanent PKBase filing.
- A refusal such as `不要`, `暂时不要`, or `no` changes the anchor to `declined` and ends
  the chain without starting the next skill.
- If no unresolved anchor exists, or the reply does not clearly refer to one specific
  anchor, do not infer permission from a bare affirmative. Clarify the intended action.
  A new review recommendation replaces an older unresolved review-to-summary anchor;
  never let agreement to the new recommendation run the older corpus.
- Once execution begins, set the anchor to `running`; on real successful completion set
  it to `completed`. If execution fails, set it to `failed`, report the actual failure,
  and do not claim the handoff completed. Accepted/running/completed/declined/failed
  anchors are not fresh permission for another run.
- Silence, timeout, or an autonomous-mode setting cannot approve this next skill.
  Interrupted work may resume only this same authorized execution with unchanged
  verified inputs; it cannot authorize a new stage or repeat a completed one.
- The user may instead invoke the summary skill directly. That requests stage entry;
  it does not bypass matching corpus approval. Genuine imported inputs require the
  summary receiver's separate explicit `input_anchor_approval`, not invented review
  history or an inferred approval from a supplied filename.

## Changes in 2.7.0

- Added host-owned content-bound corpus acceptance before the summary offer and matching
  producer/consumer state bindings; corpus acceptance and stage entry are separate.
- Permanent PKBase filing now requires explicit scope rather than source/path existence.
- Retrieval algorithms, canonical corpus schema, optional sources, PKBase resolution
  and bundled arXiv script/CLI are unchanged; approval is host workflow enforcement.
