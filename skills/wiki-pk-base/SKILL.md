---
name: wiki-pk-base
description: "An automated skill to build and maintain a persistent, interlinked Markdown knowledge base for any domain or topic. It ingests raw sources, compiles them into a structured wiki, supports querying, and lints for consistency."
version: 1.0.0
author: Zhihao Li
license: MIT
metadata:
  hermes:
    tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative]
    category: research
    related_skills: [pdf, obsidian, arxiv, agentic-research-ideas]
---

# LLM Wiki for Personal Knowledge Base (PKBase)

Build and maintain a persistent, compounding knowledge base as interlinked markdown files based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## PKBase Config

- **Location:** Set via `PKBASE_PATH` environment variable (e.g. in `~/.hermes/.env`). If unset, defaults to `~/PKBase`:

```bash
PKBASE="${PKBASE_PATH:-$HOME/PKBase}"
```

- **Depth Level:** Set via `DEPTH_LEVEL` environment variable (e.g. in `~/.hermes/.env`) for the user's preferred depth level. If none is set, default to 500 (College level).

The PKBase is just a directory of markdown files — open it in Obsidian, VS Code, or any editor. No database, no special tooling required.

## Architecture: Three Layers

```
PKBase/                    # Personal Knowledge Base
├── SCHEMA.md              # Conventions, structure rules, taxonomy, extraction rules
├── index.md               # Sectioned content catalog with one-line summaries
├── log.md                 # Chronological action log (append-only, rotated yearly)
├── raw/                   # Layer 1: Immutable source material
│   ├── articles/          # Web articles, clippings
│   ├── papers/            # PDFs, arXiv papers
│   ├── transcripts/       # Meeting notes, interviews
│   └── assets/            # Images, diagrams referenced by sources
├── wiki/                  # Layer 2: Agent-owned knowledge base
│   ├── index.md           # Master index. Always keep updated
│   ├── sources/           # Source summaries classified by domain and topic
│   │   └── <domain>/
│   │       └── <topic>/
│   │           └── <source-slug>.md   # Comprehensive source summary
│   ├── concepts/          # Unified concept articles classified by domain and topic
│   │   └── <domain>/
│   │       └── <topic>/
│   │           └── <concept-name>.md  # Merged knowledge about a specific concept
│   ├── comparisons/       # Layer 2: Side-by-side analyses
│   └── queries/           # Layer 2: Filed query results worth keeping
```

**Layer 1 — Raw Sources:** Immutable source material. The agent reads but never modifies these.
**Layer 2 — The Wiki:** Agent-owned markdown knowledge structured to combine knowledge across sources.

For every injected source, the agent must:
1. extract the source's **domain**
2. extract the source's **topic**
3. Create or update a **source summary** at `wiki/sources/<domain>/<topic>/<source-slug>.md`
4. Create or update **concept articles** at `wiki/concepts/<domain>/<topic>/<concept-name>.md`. **CRITICAL:** If a concept already exists from a previous source, append/merge the new insights into the existing concept file, adding the new source to its frontmatter. Do not create duplicates.

Example:
```
wiki/
├── index.md
├── sources/
│   └── agents/
│       └── discovery/
│           ├── ietf-draft-narajala-ans.md
│           └── w3c-discovery-rfc.md
└── concepts/
    └── agents/
        └── discovery/
            ├── agent-discovery.md         # Synthesizes knowledge from BOTH ietf-draft and w3c-discovery
            ├── agent-identity.md
            └── agent-name-service.md
```

**Layer 3 — The Schema:** `SCHEMA.md` defines structure, conventions, and tag taxonomy.

## Resuming an Existing PKBASE (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

1. **Read `SCHEMA.md`** — understand the domain, conventions, and tag taxonomy.
2. **Read `index.md`** — learn what pages exist and their summaries.
3. **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
PKBASE="${PKBASE_PATH:-$HOME/PKBase}"
# Orientation reads at session start
read_file "$PKBASE/SCHEMA.md"
read_file "$PKBASE/index.md"
read_file "$PKBASE/log.md" offset=<last 30 lines>
```

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick `search_files` for the topic
at hand before creating anything new.

## Initializing a New PKBASE

When the user asks to create or start a PKBASE:

1. Determine the PKBASE path (from `$PKBASE_PATH` env var, or ask the user; default `~/PKBase`)
2. Ask the user what domain and possible topics the PKBASE covers — be specific
3. Create the directory structure above using provided domain and topics. If topics is not available, just create the domain structure
4. Write `SCHEMA.md` customized to the domain and topics (see template below)
5. Write initial `index.md` with sectioned header
6. Write initial `log.md` with creation entry
7. Confirm the wiki is ready and suggest first sources to ingest

### SCHEMA.md Template

Adapt to the user's domain and topics. The schema constrains agent behavior and ensures consistency across the PKBase folder structure:

```md
# PKBase Schema

## Domains & Topics
[Define the scope of this knowledge base. List the primary domains and their sub-topics.]

Example:
- Domain: `agents`
  - Topics: `discovery`, `identity-trust`, `architecture`
- Domain: `programming`
  - Topics: `theory-building`, `design-patterns`

## Conventions
- Directory structure MUST follow: `wiki/sources/<domain>/<topic>/` (for summaries) and `wiki/concepts/<domain>/<topic>/` (for concepts)
- File names: lowercase, hyphens, no spaces (e.g., `agent-discovery.md`)
- Every wiki page (summary, concept, etc.) starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating an existing concept page with information from a new source, append the new insights cleanly, append the new source to the `sources:` frontmatter array, and bump the `updated` date. Do NOT overwrite the entire file causing loss of existing knowledge.
- Every new domain, topic, and wiki page must be added to the main `index.md` under the correct section
- Every action must be appended to `log.md`

## Depth Levels
The chosen depth level applies to BOTH the `summary.md` and the individual concept articles (`<concept-name>.md`). A single paragraph is never enough. Use extensive details, formulas, structure, and methodologies. Break summaries down into multiple specific sections or bulleted insights.
- **100**: Explain like I'm 12 (Feynman technique, analogies, no jargon). Provide multiple angles and examples.
- **300**: College level (technical but accessible, assumes some background). Detail multiple facets, but avoid deepest math.
- **500**: Expert deep-dive (full technical detail, assumes domain expertise). Must include comprehensive, multi-point, structured summaries. Adapt the details rigorously to the source type (e.g., for ML papers: include specific loss functions, architectural parameters, methodology steps, and ablation findings. For non-ML articles, transcripts, or essays: include comprehensive logical breakdowns, specific arguments, nuanced historical contexts, or critical decisions).

## Source Summary Format
For each raw source ingested, create a single `<source-slug>.md` summary file inside `wiki/sources/<domain>/<topic>/`. The summary depth is controlled by `Depth Level` in the above config setting.

### ASCII Diagrams (required in every summary)
Every source summary must include at least one ASCII diagram, regardless of depth level.
Choose the most appropriate type(s):
- **Sequence diagram**: for protocols, request/response flows, multi-step interactions
- **Architecture/block diagram**: for system components, layers, data flow
- **Flowchart**: for decision logic, algorithms, processes

Use simple ASCII box-drawing characters. Example:

\`\`\`
  +------------------+
  |   Raw Audio      |
  +--------+---------+
           |
  +--------v---------+     +------------------+
  |   HuBERT Encoder |     |  Style Reference |
  |  (Trainable TF)  |     |     Video        |
  +--------+---------+     +--------+---------+
           |                        |
           | A_{-Tp:Tw}             |
           |               +--------v---------+
           |               |  Style Encoder   |
           |               | (4-layer TF +    |
           |               |  contrastive)    |
           |               +--------+---------+
           |                        |
           |                        | s (128-dim)
           |                        |
  +--------v------------------------v---------+
  |         Transformer Decoder               |
  |  8-layer, alignment mask, windowing       |
  |  Inputs: X^n, X^0_{-Tp:0}, A, s, β, n    |
  +-------------------+-----------------------+
                      |
                      | X̂^0_{0:Tw}
                      v
  +-------------------------------------------+
  |    Geometric Losses (vertex, vel, smooth) |
  |    on zero-head-posed FLAME mesh          |
  +-------------------------------------------+
                      |
                      v
              [Renoise to X^{n-1}]
              [Repeat N=500 steps]
\`\`\`

Keep diagrams under 70 characters wide. Use them to reinforce the text, not replace it. At minimum include one diagram per summary.

\`\`\`yaml
---
title: "Source Summary: <Source Title>"
domain: [e.g., agents]
topic: [e.g., discovery]
created: YYYY-MM-DD
source: raw/<articles|papers|transcripts>/<filename.md>
depth: <100|300|500>
articles_created: [article-one.md, article-two.md, ...]
---

# <Source Title> - Summary

<Summary content written at the configured depth level>

## What This Source Covers
- <bullet summary of main topics>

## Wiki Articles From This Source
- [Article One](article-one.md) - one line description
- [Article Two](article-two.md) - one line description
\`\`\`


## Article Format
Each wiki article must follow this format:

\`\`\`markdown
---
title: <Concept Name>
domain: [e.g., agents]
topic: [e.g., discovery]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/filename.md, ...]
related: [other-article](other-article.md), [another-article](another-article.md)
tags: [concept-specific-tag, broader-topic-tag, genai-category-tag]
---

# <Concept Name>

<Encyclopedia-style summary written at the configured depth level. You can and should use ## H2 and ### H3 headers to structure this summary logically when appropriate, rather than keeping it as a single block of text.>

## Key Points
- ...

## Related Concepts
- [linked article](linked-article.md) - brief note on relationship

## Sources
- raw/filename.md - what this source contributed
\`\`\`

## Tag Taxonomy
Every article must have a `tags` field in its frontmatter with 3-7 lowercase-kebab-case tags:
1. **Broader topic tags**: the larger area it belongs to (e.g., `ai-agents`, `software-engineering-philosophy`)
2. **Content-specific tags**: what this article covers (e.g., `pki`, `dns`, `tacit-knowledge`)

[Define 10-20 top-level tags. Add new tags here BEFORE using them.]

Example for AI/ML:
- Models: model, architecture, benchmark, training
- People/Orgs: person, company, lab, open-source
- Techniques: optimization, fine-tuning, inference, alignment, data
- Meta: comparison, timeline, controversy, prediction

Rule: every tag on a page must appear in this taxonomy. Reuse existing tags across articles to build a coherent taxonomy. If a new tag is needed, add it here first, then use it. This prevents tag sprawl.

## Page Types & Structure
- **Source Summary Page (`sources/<domain>/<topic>/<source-slug>.md`)**: Main objective digest of the source written at the configured depth level.
- **Concept Pages (`concepts/<domain>/<topic>/<concept-name>.md`)**: Key entities and concepts extracted from the sources. Must be merged/appended to when overlapping topics are found across multiple sources. Include:
  - Definition / explanation
  - Key facts and dates
  - Related concepts/entities (`[[wikilinks]]`)
- **Comparison Pages (`wiki/comparisons/`)**: Side-by-side analyses spanning multiple sources.

## Update Policy
When new information conflicts with existing knowledge across sources:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources in the synthesis concept page. Mark the disagreement explicitly under a dedicated `## Synthesis & Contradictions` header.
3. Mark the contradiction in frontmatter: `contradictions: [source-slug-1, source-slug-2]`
4. Flag for user review in the lint report

```

### index.md Template

The index is sectioned by Domain and Topic. Each source entry should keep its tags in the index so `query` can use them later. Each entry is one line: wikilink + summary + tags.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its domain and topic with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total sources: N | Total pages: M

## Domains & Topics

### [Domain Name 1] (e.g., agents)
#### [Topic Name 1] (e.g., discovery)

**Sources**
- [[sources/agents/discovery/source-slug|Source Title]] - One line summary of the source | tags: [tag-one, tag-two]

**Concepts**
- [[concepts/agents/discovery/concept-name|Concept Name]] - One line summary of the concept | tags: [tag-one, tag-two]

## Comparisons
<!-- Alphabetical within section -->

## Queries
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections by first letter or sub-domain. When the index exceeds 200 entries total, create a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: add, ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.

## [YYYY-MM-DD] create | Wiki initialized
- Domains & Topics configured
- Structure created with SCHEMA.md, index.md, log.md

## [YYYY-MM-DD] ingest | [Source Title]
- Domain: [domain] | Topic: [topic]
- Created/Updated Source: sources/[domain]/[topic]/[source-slug].md
- Created Concept: concepts/[domain]/[topic]/[new-concept].md
- Appended to Concept: concepts/[domain]/[topic]/[existing-concept].md
```

## Core Operations

To trigger these operations, instruct the agent with the operation name, for example: "Please `add` this source" or "Run a `lint` on my wiki". If your environment supports parameterized skill invocations, use the specified argument format.

### 1. Process

**Command Argument:** `process <raw file path>`

Process a single unprocessed raw file and compile it into wiki articles.

- **Input:** A path to one file under `raw/`
- **Output:** Updated wiki pages, index entries, and a log entry for that file
- **Usage:** This command is reusable and can be called directly or by `add` / `ingest`

- **Phase 1: Read the source**
  - Read the full raw file
  - Derive a source slug from the raw filename (strip the `YYYYMMDD-` date prefix if present, otherwise use the filename as is)
  - Determine the source's domain and topic

- **Phase 2: Build or update wiki content**
  - **Determine Location:** Create the source folder: `wiki/domains/<domain>/<topic>/<source-slug>/`
  - **New concepts:** Extract 3-10 highly granular key concepts from the raw file. Adapt the concept type to the source material:
    - *For ML / Technical papers:* specific algorithms, architecture sub-components, datasets, distinct limitations, loss functions, or mathematical derivations.
    - *For general articles, transcripts, or essays:* primary arguments, mental models, key historical events, decision-making frameworks, or underlying principles.
    Break concepts down as far as they logically go rather than grouping them into a few broad topics.
  - **For each concept:**
    - Use `search_files` to check if a wiki article already exists anywhere in `wiki/`
    - If yes: update and expand the article, add new source to frontmatter, update the `updated` date
    - If no: create a new article inside `wiki/domains/<domain>/<topic>/<source-slug>/`
  - **Cross-reference:** Every new or updated page must link to at least 2 other pages via [[wikilinks]].
  - **Backlink enforcement:** If linked pages do not link back, add backlinks in those related pages using relative paths across folders.
  - **Tags:** Use only tags defined in SCHEMA taxonomy. If a new tag is needed, add it to SCHEMA first with a short definition, then use it in articles.
  - **Media integration:** Embed extracted original media files (images, videos, etc., located in `raw/assets/`) into the `summary.md` and concept wiki pages where they are contextually relevant. Use Obsidian-style media links (e.g., `![[filename.ext]]`).
  - **Summary:** Create `wiki/domains/<domain>/<topic>/<source-slug>/summary.md` at the configured depth level

- **Phase 3: Update navigation**
  - Add new pages to `index.md` under the correct Domain and Topic section, alphabetically
  - Update the "Total pages" count and "Last updated" date in index header

### 2. Add

**Command Argument:** `add [URL | file path | pasted text]`

When the user provides a source (URL, file, paste), integrate it into the wiki:

- **Phase 1: Capture the raw source**
  - **Original Files Constraint**: ALWAYS save the original files (PDFs, images, videos, audio) directly into the appropriate `raw/` subdirectory (e.g., `raw/papers/` for PDFs, `raw/images/` for Images, `raw/assets/` for media) in addition to extracting their text.
  - URL → use `web_extract` to get markdown, save to `raw/articles/`
  - PDF → save the original `.pdf` file to `raw/papers/`, then use `web_extract` (handles PDFs) to extract text, and save the markdown to `raw/papers/`
  - Images/Videos/Audio → save the original media files to `raw/assets/`
  - Pasted text → save to appropriate `raw/<articles|papers|transcripts>/` subdirectory
  - Name the file descriptively using the format `YYYYMMDD-[author/source]-[topic-slug].[ext]`.
    Examples:
    - `raw/articles/20260419-karpathy-llm-wiki.md`
    - `raw/papers/20260408-arxiv-2509-07367.md`

- **Phase 2: Check what already exists**
  - Read `wiki/index.md` to understand existing articles
  - Read `wiki/log.md` to understand what has been done before

- **Phase 3: Write or update wiki pages**
For each unprocessed raw source file, call the reusable `process` command to process that file.

- **Phase 4: Append to `log.md`**
  - Append to `log.md`: `## [YYYY-MM-DD] Add | Source Title` and log the Domain/Topic along with all created/updated files.
    ```md
    ## [YYYY-MM-DD] Add | <source description>
    - Domain: <domain>
    - Topic: <topic>
    - Processed: raw/<articles|papers|transcripts>/<filename>
    - Folder: wiki/domains/<domain>/<topic>/<source-slug>/
    - Created: <list of new wiki articles>
    - Summary: wiki/domains/<domain>/<topic>/<source-slug>/summary.md (depth: <100|300|500>)
    - Updated: <list of updated wiki articles>
    ```

- **Phase 5: Report what changed**
  - List every file created or updated to the user, including their full paths within the domain structure.

A single source can trigger updates across 5-15 wiki pages. This is normal and desired — it's the compounding effect.

### 3. Ingest

**Command Argument:** `ingest`

Process all unprocessed files in `raw/` and compile them into wiki articles.

- **Phase 1: Find unprocessed files**
  1. List all files in `raw/`
  2. Read `log.md` to find which files have already been processed
  3. Identify files in `raw/` that are NOT mentioned in `log.md`

If all files are already processed, tell the user "Nothing new to ingest." and stop.

- **Phase 2: Read existing wiki state**
  1. Read `wiki/index.md` to understand existing articles and categories
  2. Scan `wiki/` for existing article folders and files

- **Phase 3: Process each new raw file**
For each unprocessed raw file, call the reusable `process` command with that file path.

- **Phase 4: Append to `log.md`**
  - Append to `log.md` as a batch summary with one per-source block:
    ```md
    ## [YYYY-MM-DD] Ingest | Batch Summary
    - <source description>
      - Domain: <domain>
      - Topic: <topic>
      - Processed: raw/<articles|papers|transcripts>/<filename>
      - Folder: wiki/domains/<domain>/<topic>/<source-slug>/
      - Created files: <list of new wiki articles>
      - Summary: wiki/domains/<domain>/<topic>/<source-slug>/summary.md (depth: <100|300|500>)
      - Updated files: <list of updated wiki articles>
    - <source description>
      - ...
    ```

- **Phase 5: Report what changed**
  - List every file created or updated to the user, including their full paths within the domain structure.

### 4. Query

**Command Argument:** `query [your question]`

When the user asks a question about the knowledge base. Searches wiki articles and synthesizes an answer with references.

- **Phase 1: Read `index.md`** to identify relevant pages.
- **Phase 2: Search by tags**: identify tags most relevant to the question, then find articles sharing those tags in `index.md`.
- **Phase 3: For wikis with 100+ pages**, also `search_files` across all `.md` files for keywords related to the question — the index alone may miss relevant content.
- **Phase 4: Read the most relevant wiki articles** using `read_file`. If wiki articles reference `raw/` sources and more detail is needed, read those too.
- **Phase 5: Synthesize an answer** from the compiled knowledge. Cite the wiki pages you drew from: "Based on [[page-a]] and [[page-b]]..."
- **Phase 6: File valuable answers back** — if the answer is a substantial comparison, deep dive, or novel synthesis, create a page in `queries/` or `comparisons/`. Don't file trivial lookups — only answers that would be painful to re-derive.
- **Phase 7: Update `log.md`** with the query and whether it was filed.
    ```md
    ## [YYYY-MM-DD] Query | <question summary>
    - Query: <user question>
    - Domain: <domain>
    - Topic: <topic>
    - Pages reviewed:
      - <wiki page links or paths>
    - Filed: <yes|no>
    - Filed files:
      - <list of new or updated query/comparison files, if any>
    ```

#### Tag-based search

First search `index.md` tags to find related content that keyword search might miss. For
example, if the user asks about "how agents verify each other", search for tags like
`agent-identity`, `pki`, `trust` in the index to find relevant articles even if they don't
contain those exact words.

When multiple articles share tags, they likely cover related aspects of the same topic.
Follow tag clusters to build a more complete answer.

#### Rules
- Every claim in your answer must trace to a specific wiki article or raw source
- Cite sources at the end using wikilinks (`[[link]]`) to the wiki files
- If the knowledge base has no relevant content, say so clearly
- Do not make things up or add information beyond what is in the wiki
- Keep the answer concise and direct

### 5. Lint

**Command Argument:** `lint`

When the user asks to run a health check on the wiki, run the checks below in order. All checks target markdown pages under `wiki/`.

- **Phase 1: Broken Wikilinks**
  - Scan all wiki articles for `[[wikilink]]` syntax that point to files that do not exist.
  - Report each finding as:
  ```
  BROKEN LINK: [[wikilink]] in wiki/domains/<domain>/<topic>/<source-slug>/some-article.md
  ```

- **Phase 2: Legacy Markdown Links**
  - Scan all wiki articles for explicit markdown links `[text](path.md)`.
  - These should be converted to Obsidian-style `[[link]]` syntax to match the PKBase standard.
  - Report each finding as:
  ```
  LEGACY LINK: [text](path.md) in wiki/<source-slug>/some-article.md — convert to [[link]]
  ```

- **Phase 3: Missing articles (concept frequency audit)**
  - Build a concept/term frequency map across different wiki articles.
  - Flag terms that appear in 3+ distinct articles but do not have a dedicated wiki page.
  - Use normalized terms (case-folded, punctuation-trimmed) and ignore stopwords/common jargon.
  - Report each finding as:
  ```
  MISSING ARTICLE: "<concept>" mentioned in N articles but has no wiki page
  ```

- **Phase 4: Index consistency (`wiki/index.md` vs filesystem)**
  - Compare index entries against actual files under `wiki/`.
  - Detect:
    - files that exist but are not listed in index
    - files listed in index but missing on disk
    - summary files listed but absent
  - Report each finding as:
  ```
  INDEX STALE: wiki/<source-slug>/<file>.md exists but not in index
  INDEX GHOST: wiki/<source-slug>/<file>.md listed in index but file missing
  ```

- **Phase 5: Source traceability (`frontmatter.sources`)**
  - Ensure every wiki article has at least one source in frontmatter.
  - Validate that each source path points to an existing file under `raw/`.
  - Report each finding as:
  ```
  NO SOURCE: wiki/<source-slug>/<file>.md has no sources listed
  MISSING SOURCE: wiki/<source-slug>/<file>.md references raw/<file>.md which does not exist
  ```

- **Phase 6: Folder structure validation**
  - For each source folder under `wiki/`, verify:
    - a summary file named `summary-<folder-name>.md` exists
    - at least one non-summary article file exists
  - Report each finding as:
  ```
  MISSING SUMMARY: wiki/<source-slug>/ has no summary-<source-slug>.md
  EMPTY FOLDER: wiki/<source-slug>/ has no article files
  ```

- **Phase 7: Stale backlinks (`related:` validation)**
  - Parse `related:` entries in frontmatter and verify each referenced article exists.
  - Report each finding as:
  ```
  STALE BACKLINK: wiki/<source-slug>/<file>.md links to a non-existent article
  ```

- **Phase 8: Optional integrity checks**
  - Tag audit: list tags in use and flag tags not declared in `SCHEMA.md` taxonomy.
  - Log rotation: if `log.md` exceeds 500 entries, rotate to `log-YYYY.md`.

- **Phase 9: Lint report + logging**
  - Group findings by severity priority:
    1. broken links / missing sources / stale backlinks
    2. index ghosts/stale entries
    3. missing articles
    4. legacy markdown links / style issues
  - Include exact file paths and actionable fixes.
  - Append to `log.md`:
  ```md
  ## [YYYY-MM-DD] lint | N issues found
  - Broken wikilinks: <count>
  - Legacy markdown links: <count>
  - Missing articles: <count>
  - Index stale/ghost entries: <count>
  - Source traceability issues: <count>
  - Folder structure issues: <count>
  - Stale backlinks: <count>
  ```

#### Suggestions

Based on findings, suggest up to 5 new articles that would most strengthen the knowledge base. Prioritize:
1. Concepts referenced by many articles but lacking their own page
2. Bridging articles that would connect isolated clusters
3. Foundational concepts assumed but not explained

Format:
```
SUGGESTED ARTICLES
1. <concept-name>.md - <why it would help>
2. ...
```

#### Auto-fix option

After reporting, ask the user if they want to auto-fix:
- Convert legacy markdown links `[text](path.md)` to Obsidian-style `[[wikilinks]]`
- Add missing articles to the index
- Remove ghost entries from the index
- Update the article count and date in the index

## Working with the Wiki

### Searching

Use these tool patterns to navigate the PKBase efficiently:

```bash
# Find pages by content within the PKBase
search_files "transformer" path="$PKBASE/wiki" file_glob="*.md"

# Find pages by filename
search_files "*.md" target="files" path="$PKBASE/wiki"

# Find pages by frontmatter tag
search_files "tags:.*alignment" path="$PKBASE/wiki" file_glob="*.md"

# Read recent log activity
read_file "$PKBASE/log.md" offset=<last 20 lines>
```

### Archiving

When content is fully superseded or the domains/topics scope changes:
1. Create a `_archive/` directory at the PKBase root if it doesn't exist.
2. Move the page to `_archive/` while preserving its domain structure (e.g., move to `_archive/domains/agents/discovery/old-slug/old-concept.md`).
3. Remove the corresponding entry from `wiki/index.md`.
4. Update any pages that linked to it — replace the `[[wikilink]]` with plain text + "(archived)".
5. Append an archive action to `log.md`.

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` folder holds images referenced via `![[image.png]]`

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

### Obsidian Headless (servers and headless machines)

On machines without a display, use `obsidian-headless` instead of the desktop app.
It syncs vaults via Obsidian Sync without a GUI — perfect for agents running on
servers that write to the wiki while Obsidian desktop reads it on another device.

**Setup:**
```bash
# Requires Node.js 22+
npm install -g obsidian-headless

# Login (requires Obsidian account with Sync subscription)
ob login --email <email> --password '<password>'

# Create a remote vault for the wiki
ob sync-create-remote --name "LLM Wiki"

# Connect the wiki directory to the vault
cd ~/wiki
ob sync-setup --vault "<vault-id>"

# Initial sync
ob sync

# Continuous sync (foreground — use systemd for background)
ob sync --continuous
```

**Continuous background sync via systemd:**
```ini
# ~/.config/systemd/user/obsidian-wiki-sync.service
[Unit]
Description=Obsidian LLM Wiki Sync
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/ob sync --continuous
WorkingDirectory=/home/user/wiki
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now obsidian-wiki-sync
# Enable linger so sync survives logout:
sudo loginctl enable-linger $USER
```

This lets the agent write to `~/wiki` on a server while you browse the same
vault in Obsidian on your laptop/phone — changes appear within seconds.

## Pitfalls

- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Always orient first** — read SCHEMA + index + recent log before any operation in a new session.
  Skipping this causes duplicates and missed cross-references.
- **Always update index.md and log.md** — skipping this makes the wiki degrade. These are the
  navigational backbone.
- **Don't create pages for passing mentions** — follow the Page Thresholds in SCHEMA.md. A name
  appearing once in a footnote doesn't warrant an entity page.
- **Don't create pages without cross-references** — isolated pages are invisible. Every page must
  link to at least 2 other pages.
- **Frontmatter is required** — it enables search, filtering, and staleness detection.
- **Tags must come from the taxonomy** — freeform tags decay into noise. Add new tags to SCHEMA.md
  first, then use them.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY.md` and start fresh.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
