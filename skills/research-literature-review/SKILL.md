---
name: research-literature-review
description: "collect, normalize, de-duplicate, and organize research papers into a single output: a direction-focused background review that captures the existing research foundation for a topic or a user-written research-direction overview. Use when user asks to find papers, do a literature review, collect related work, compare recent papers, understand what a paper says, or needs to build prior-work coverage, map existing literature, expand a research-direction summary into retrieval facets, gather papers from zotero, obsidian, and web sources, or export structured json files for downstream analysis."
version: 2.0.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [Research, Literature, Review]
---
# Research Literature Review

Research topic: $ARGUMENTS

## Constants

- **REVIEW_TOPIC** - a short topic label for the main direction
- **TOPIC_OVERVIEW** - optional user-written research direction overview; may be several sentences or paragraphs
- **FOUNDATION_OUTPUT_JSON** - `artifacts/research_foundation_review.json`
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
  "pdf_path": "Local Path of Paper PDF",
  "doi": "10.1000/example",
  "arxiv_id": "2501.01234",
  "citation_key": "Smith2025",
  "bibtex": "@article{Smith2025, ...}",
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
3. Collect papers from Zotero, Obsidian, and web sources.
4. Normalize the collected records to the canonical JSON schema.

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
      "pdf_path": "Local Path of Paper PDF",
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
| 2        | Obsidian   | `obsidian` | research notes, summaries, ratings, wikilinks, local metadata                     |
| 3        | Web search | `web`      | arXiv, Semantic Scholar, Google Scholar, conference accepted papers / proceedings |

If Zotero or Obsidian tools are unavailable, skip them silently.

Practical retrieval notes learned in use:

- For Zotero, a short topic query plus one or two adjacent facet queries often finds better coverage than a single broad search string.
- For recent methods, semantic search is usually better than title search for broad topic discovery; then fetch item metadata for the shortlisted papers.
- If Obsidian MCP returns repeated directory errors or becomes unreachable, stop retrying that source and continue with Zotero/Web only.
- If web search tooling is limited, the arXiv API is a reliable fallback for recent papers and benchmark/milestone discovery.
- Zotero semantic search uses relevance scoring that can miss papers even when they are in the library. After semantic search, ALWAYS do targeted title-based searches for specific papers mentioned in the user's topic overview or related work tables — these are high-priority must-include papers that semantic search may not surface.
- When the user provides a topic overview with a related work table or method names, extract those paper titles/keywords and search for each one individually in Zotero. This catches milestone and key-method papers that semantic search ranking may bury.

#### 1: Zotero

If available (using `mcp-for-zotero` to fetch bibliographic data):

- Use the `mcp-for-zotero` tool to retrieve items from the user's Zotero library
- Prioritize retrieving metadata, annotations, tags, and collection information for the topic/facets derived in Step 1
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

#### 2: Obsidian

If available:

- only retrieve Obsidian data from the `ResearchPapers` directory
- search topic-related notes and overview-derived facet keywords within `ResearchPapers`
- check relevant tags
- read summaries, insights, and wikilinks
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
- prefer user's summaries and interpretations from Obsidian
- prefer freshest publication metadata from Web or arXiv
- never discard annotations, tags, note summaries, or provenance if they can be preserved

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

## Output expectations

When reporting results to the user:

- say which sources were successfully used
- say if Zotero or Obsidian were unavailable
- report how many raw results were collected from each source
- report how many merged papers remained after de-duplication
- report where the final JSON file was saved

If Zotero BibTeX was exported, include a `references.bib` snippet for direct use in paper writing.
