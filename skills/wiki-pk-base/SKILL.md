---
name: wiki-pk-base
description: "Build and maintain a personal knowledge base (PKBase) as interlinked markdown — an Obsidian-friendly vault — plus a static web showcase (site/) rebuilt from the vault after every operation. Use when the user wants to create/start a knowledge base or wiki, add or ingest a source (URL, PDF, pasted text, or a whole folder of files) into it, query/ask questions about it, lint/audit/health-check it, or view/preview the wiki as a website. Triggers on words like 'wiki', 'knowledge base', 'PKBase', 'ingest', 'add this source', 'my notes', 'view my wiki', or a question when an existing wiki is present. Unlike RAG, it compiles knowledge once into a persistent, cross-referenced vault that compounds over time."
version: 1.1.0
author: Zhihao Li
license: MIT
metadata:
  tags: [wiki, knowledge-base, research, notes, markdown, rag-alternative, obsidian]
  category: research
  related_skills: [pdf, obsidian, agentic-research-ideas]
  operations: [init, process, add, ingest, query, lint]
  config:
    path_env: PKBASE_PATH
    path_default: "~/PKBase"
    depth_level: "stored in SCHEMA.md (100 | 300 | 500)"
---

# LLM Wiki for Personal Knowledge Base (PKBase)

Build and maintain a persistent, compounding knowledge base as interlinked markdown files based on [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki compiles knowledge once and keeps it current. Cross-references are already there.
Contradictions have already been flagged. Synthesis reflects everything ingested.

**Division of labor:** The human curates sources and directs analysis. The agent summarizes, cross-references, files, and maintains consistency.

## When This Skill Activates

Use this skill when the user:
- Asks to create, build, or start a wiki or knowledge base
- Asks to ingest, add, or process a source — or a whole folder of files — into their wiki
- Asks a question and an existing wiki is present at the configured path
- Asks to lint, audit, or health-check their wiki
- References their wiki, knowledge base, or "notes" in a research context

## PKBase Config

- **Location:** Set via `PKBASE_PATH` environment variable, or specify the path directly in the conversation. If unset, defaults to `~/PKBase`:

```bash
PKBASE="${PKBASE_PATH:-$HOME/PKBase}"
```

- **Depth Level:** Stored inside the PKBase itself (`SCHEMA.md` → `## Configuration`). This keeps the PKBase fully self-contained and portable across any agent framework — no external env config required. Default: `500` (Expert deep-dive) if not specified.

The PKBase is just a directory of markdown files — open it in Obsidian, VS Code, or any editor. No database, no special tooling required. All configuration lives inside the PKBase directory, so it can be moved, cloned, or synced without losing settings.

## Architecture: Three Layers

```
PKBase/                    # Personal Knowledge Base
├── SCHEMA.md              # Conventions, structure rules, taxonomy, extraction rules
├── index.md               # Sectioned content catalog with one-line summaries (the single master index)
├── log.md                 # Chronological action log (append-only, rotated to log-YYYY-N-MMfirsttoMMlast.md at 500 entries)
├── site/                  # Static web showcase (copied from the skill's web-template at init; rebuilt by regenerating data.js)
├── raw/                   # Layer 1: Immutable source material (3-level: <material-type>/<domain>/<topic>/)
│   ├── articles/<domain>/<topic>/   # Web articles, clippings, blog posts
│   ├── papers/<domain>/<topic>/     # PDFs, arXiv papers (+ extracted .md alongside)
│   ├── transcripts/<domain>/<topic>/  # Meeting notes, interviews, video/podcast transcripts
│   ├── assets/<domain>/<topic>/      # Images, audio, video, diagrams referenced by sources
│   └── misc/<domain>/<topic>/        # Fallback for sources that fit no other category
├── wiki/                  # Layer 2: Agent-owned knowledge base
│   ├── sources/           # Source summaries classified by domain and topic
│   │   └── <domain>/
│   │       └── <topic>/
│   │           └── <source-slug>.md   # Comprehensive source summary
│   ├── concepts/          # Unified concept articles classified by domain and topic
│   │   └── <domain>/
│   │       └── <topic>/
│   │           └── <concept-name>.md  # Merged knowledge about a specific concept
│   ├── comparisons/       # Layer 2: Side-by-side analyses, by domain and topic
│   │   └── <domain>/
│   │       └── <topic>/
│   │           └── <comparison-slug>.md
│   └── queries/           # Layer 2: Filed query results worth keeping, by domain and topic
│       └── <domain>/
│           └── <topic>/
│               └── <query-slug>.md
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

## Web Site (static showcase)

`<PKBase>/site/` is a small self-contained static web site that displays the compiled wiki plus raw material status. It is a **build artifact of the vault**: the agent maintains it, never the user.

- **Origin:** the skill ships a template in `web-template/` (next to this SKILL.md: `index.html`, `style.css`, `app.js`, `data.js`, `README.md`). At **init**, copy the whole folder into `<PKBase>/site/`.
- **Rebuild rule:** every operation that changes vault state (`init`, `add`, `ingest`, `lint`, and any manual page/raw/log edit) finishes by **regenerating `site/data.js`** from the current vault. The other four files are stable template files — never hand-edit them inside a PKBase (if the skill's `web-template/` is updated, re-copy it and regenerate `data.js`).
- **No build step:** the site is vanilla JS + CSS, readable by double-clicking `site/index.html` (`file://` works). Visual style: an academic-homepage look (fixed light navbar, white rounded cards on a light-gray page, blue links, publication-style list rows — see `web-template/README.md` for the full design spec). Lato + LXGW WenKai GB Screen fonts, Font Awesome icons, and KaTeX (for `$...$` / `$$...$$` formulas) load from CDNs (Google Fonts / jsDelivr / Cloudflare) and degrade gracefully offline.
- **Bilingual UI (中文 / EN):** the site chrome (nav, section titles, stats, table headers, empty states, footer) is fully bilingual — toggle in the navbar (`.pk-lang`), persisted in `localStorage` (`pkbase_lang`), defaulting to the browser language. All UI strings live in the `I18N` dictionary at the top of `app.js` — **never hardcode Chinese/English text in view code**.
- **Bilingual vault content:** when `SCHEMA.md` has `bilingual: true`, the same toggle also switches **content language**: entries in `data.js` that carry translation fields (`title_en`, `description_en`, `body_en`, …) are shown in the matching UI language, and entries without them fall back to the base-language text. Translation fields come from the sibling translation files (`<slug>.en.md` / `<slug>.zh.md`, see `## Conventions` in the SCHEMA.md template) — the site never translates on the fly. If `bilingual` is `false` (default), content is always displayed **as written**.
- **Cache busting:** `index.html` loads local assets with `?v=` query strings (`data.js?v=<rebuild date>`, `app.js?v=<n>`, `style.css?v=<n>`) because browsers aggressively cache `file://` scripts. **Every rebuild must update the `data.js?v=` value** (use the rebuild date, e.g. `?v=20260819`) — otherwise users keep seeing the stale data. Bump the `app.js`/`style.css` versions when the template itself changes.
- **What `data.js` contains** — full schema in the file header; in short, `window.PKBASE_DATA = { meta, counts, pages: { sources|concepts|comparisons|queries: [Page] }, raw: [RawEntry], log: [LogEntry] }`:
  - `meta`: `name` / `description` from `SCHEMA.md`; `updated` = rebuild time
  - `pages.<type>[].file`: path relative to `wiki/<type>/` (`<domain>/<topic>/<slug>.md`); `domain` / `topic` parsed from the first two path segments; `body` = page markdown **without frontmatter**, kept verbatim including `[[wikilinks]]` (full wiki-relative form `[[sources/<domain>/<topic>/<slug>|label]]`) and `$...$` formulas
  - **Translation fields (only when `bilingual: true` in SCHEMA.md):** each entry may additionally carry `<field>_en` (or `<field>_zh`) sourced from the sibling translation file `<slug>.en.md`/`<slug>.zh.md` — Page: `title_en` / `description_en` / `body_en` (frontmatter + body, verbatim, same `[[wikilink]]`/`$...$` rules); `meta`: `name_en` / `description_en` (from `SCHEMA.md` `name_en:` / `description_en:` when provided); `raw[]`: `title_en` / `description_en` (optional annotation for the raw entry); `log[]`: `title_en` / `detail_en` (optional). Entries without the `_en` field show the original text in the EN view (graceful fallback) — never emit an empty translation field.
  - `raw[]`: one entry per file under `raw/` (including binary assets), `file` relative to `raw/`
  - `log[]`: recent entries from `log.md` + all `log-*.md`, newest first (last ~50)
  - `counts`: lengths of the above arrays (sources / concepts / comparisons / queries / raw / log)
- **Rebuild procedure:**
  1. Scan `wiki/{sources,concepts,comparisons,queries}/<domain>/<topic>/*.md` → parse frontmatter (title, description, tags, updated, source) and body. **Translation merge (only when `bilingual: true` in SCHEMA.md):** for each base page, also scan for its sibling translation file `<slug>.en.md` (or `<slug>.zh.md` when `default_lang: en`) in the **same directory** — do NOT list translation files as separate pages. When present, parse it the same way and copy its `title` / `description` / body into the base entry's `title_en` / `description_en` / `body_en` (or the `*_zh` equivalents) of the **same** entry; when absent, omit the field (the web UI falls back to the base language). Also read `name_en:` / `description_en:` from `SCHEMA.md` into `meta` when present.
  2. Scan `raw/` recursively → file list with material-type / domain / topic
  3. Read `log.md` + `log-*.md` → recent entries
  4. Write `site/data.js` (escape any `</script>` sequences inside strings as `<\/script>`), bump `meta.updated`
  5. Bump the `data.js?v=` query string in `site/index.html` to the rebuild date (cache busting — see above)
  6. Report "site rebuilt (N pages, M raw files)" in the operation's final report — do not add a separate log entry for the rebuild itself; it is part of the operation's report

## Raw Folder Organization (3-level, auto-classification)

`raw/` is **three levels deep**, mirroring the wiki's `<domain>/<topic>` so a source's raw file and its wiki summaries/concepts share the same categories:

```
raw/<material-type>/<domain>/<topic>/<filename>
```

- **Level 1 — material type:** `papers/`, `articles/`, `transcripts/`, `assets/`, `misc/` (auto-classified by extension/content below).
- **Level 2 — domain / Level 3 — topic:** the **same** domain and topic the source gets on the `wiki/` side. Reuse the SCHEMA domain/topic taxonomy.

The user can dump files anywhere (their own downloads folder, a project directory, …) and the agent files them into the right `raw/` path automatically; the user never has to pre-sort.

Example: a motion-generation paper lands at `raw/papers/multimodal-learning/interactive-motion/20260812-nvidia-ardy-interactive-motion-generation.md`, with its summary at `wiki/sources/multimodal-learning/interactive-motion/...`.

### Level-1 material-type taxonomy

| Subfolder | Holds | Typical extensions |
|---|---|---|
| `papers/` | Academic papers, technical reports, theses | `.pdf`, `.bib`, `.tex` (+ extracted `.md` alongside the PDF) |
| `articles/` | Web articles, blog posts, documentation clippings | `.md`, `.html`, `.txt`, `.rst` |
| `transcripts/` | Meeting notes, interviews, video/podcast transcripts | `.md`, `.txt`, `.vtt`, `.srt` |
| `assets/` | Images, audio, video, and other media referenced by sources | `.png`, `.jpg`, `.svg`, `.mp3`, `.wav`, `.mp4` |
| `misc/` | Anything that fits no other category | any |

### Classification rules (applied in order)

**Level 1 — material type:**
1. **Extension-first (deterministic):** images/audio/video → `assets/`; `.pdf`/`.bib`/`.tex` → `papers/`; `.html` → `articles/`; `.vtt`/`.srt` → `transcripts/`. Extracted text of a paper stays in `papers/` next to its PDF.
2. **Semantic fallback (content-based):** for ambiguous text files (`.md`/`.txt`), read the first ~50 lines — paper structure (abstract, numbered sections, references, arXiv id) → `papers/`; Q&A format, speaker labels, or timestamps → `transcripts/`; article/blog layout → `articles/`; anything else → `misc/`.

**Levels 2–3 — domain / topic:**
3. Derive the domain and topic from the content — the same determination used to place the source summary under `wiki/sources/<domain>/<topic>/`. Reuse the closest existing domain/topic from SCHEMA, or propose a new one (and add it to SCHEMA).
4. If it genuinely cannot be determined, fall back to `misc/uncategorized/uncategorized/` and correct it during processing.

**Override:** the user's stated material type, domain, or topic always wins.

### Copy & naming rules

- Files are **copied** into `raw/`, never moved — the user's original folder is left intact.
- Rename on copy to `YYYYMMDD-[author/source]-[topic-slug].[ext]` (date = the file's last-modified date if readable, else today) and place it at `raw/<material-type>/<domain>/<topic>/`.
- Never overwrite an existing `raw/` file: on name collision append `-2`, `-3`, …
- The material-type set (Level 1) is extensible per PKBase via `SCHEMA.md` → `## Raw Subdirectories` (e.g., add `raw/datasets/` for a data-centric domain).

## Resuming an Existing PKBASE (CRITICAL — do this every session)

When the user has an existing wiki, **always orient yourself before doing anything**:

1. **Read `SCHEMA.md`** — understand the domain, conventions, tag taxonomy, and the configured **depth level** (from the `## Configuration` section).
2. **Read `index.md`** — learn what pages exist and their summaries.
3. **Scan recent `log.md`** — read the last 20-30 entries to understand recent activity.

```bash
PKBASE="${PKBASE_PATH:-$HOME/PKBase}"
# Orientation reads at session start (with whatever file tools the environment provides):
#   $PKBASE/SCHEMA.md
#   $PKBASE/index.md
#   last ~30 lines of $PKBASE/log.md
```

`site/` is a **build artifact** — no orientation read needed. Any state-changing operation you run will regenerate `site/data.js`; if `site/` is missing (pre-web-template PKBase), the next `lint` will report and repair it.

Only after orientation should you ingest, query, or lint. This prevents:
- Creating duplicate pages for entities that already exist
- Missing cross-references to existing content
- Contradicting the schema's conventions
- Repeating work already logged

For large wikis (100+ pages), also run a quick file search for the topic
at hand before creating anything new.

## Initializing a New PKBASE

When the user asks to create or start a PKBASE:

1. Determine the PKBASE path (from `$PKBASE_PATH` env var, or ask the user; default `~/PKBase`)
2. Ask the user what domain and possible topics the PKBASE covers — be specific
3. Ask the user for their preferred **Depth Level** (`100` / `300` / `500`). Briefly explain each level (see `## Depth Levels` in the SCHEMA.md template below). If they are unsure, default to `500` (Expert deep-dive)
3b. Ask whether the PKBase should be **bilingual** (`bilingual: true` in SCHEMA.md, with `default_lang` set to the language the user will primarily write in — default `zh`). Explain: when enabled, each page can have an optional sibling translation file (`<slug>.en.md`) that the web site's language toggle loads; untranslated pages fall back to the base language. If they are unsure, default to `false`
4. Create the directory structure above using provided domain and topics. If topics is not available, just create the domain structure
5. Write `SCHEMA.md` customized to the domain, topics, **depth level**, and **bilingual** setting (see template below)
6. Write initial `index.md` with sectioned header
7. Write initial `log.md` with creation entry
8. **Create the web site:** copy the skill's `web-template/` folder (the one next to this SKILL.md) into `<PKBase>/site/`, then seed `site/data.js` from the fresh (empty) vault — `meta.name`/`meta.description` from `SCHEMA.md`, empty `pages`/`raw`/`log` arrays, zero `counts`. The site now exists and will be rebuilt by every subsequent state-changing operation (see `## Web Site (static showcase)`).
9. Confirm the wiki is ready and suggest first sources to ingest (mention that `site/index.html` previews the knowledge base)

### SCHEMA.md Template

Adapt to the user's domain and topics. The schema constrains agent behavior and ensures consistency across the PKBase folder structure:

```md
# PKBase Schema

## Configuration
- **depth_level**: <100|300|500>  <!-- Set during initialization: 100=Feynman, 300=College, 500=Expert -->
- **default_lang**: <zh|en>  <!-- Primary language the base wiki files are written in. Default: zh -->
- **bilingual**: <true|false>  <!-- When true, pages may carry a sibling translation file (<slug>.en.md when default_lang is zh, <slug>.zh.md when default_lang is en) that the web site loads on the matching language toggle. Default: false -->

## Domains & Topics
[Define the scope of this knowledge base. List the primary domains and their sub-topics.]

Example:
- Domain: `agents`
  - Topics: `discovery`, `identity-trust`, `architecture`
- Domain: `programming`
  - Topics: `theory-building`, `design-patterns`

## Conventions
- Directory structure MUST follow the three-level `wiki/<page-type>/<domain>/<topic>/` pattern for ALL page types: `wiki/sources/<domain>/<topic>/` (summaries), `wiki/concepts/<domain>/<topic>/` (concepts), `wiki/comparisons/<domain>/<topic>/` (comparisons), `wiki/queries/<domain>/<topic>/` (filed queries). No page lives directly under a `wiki/<page-type>/` root.
- File names: lowercase, hyphens, no spaces (e.g., `agent-discovery.md`)
- Every wiki page (summary, concept, etc.) starts with YAML frontmatter (see below)
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating an existing concept page with information from a new source, append the new insights cleanly, append the new source to the `sources:` frontmatter array, and bump the `updated` date. Do NOT overwrite the entire file causing loss of existing knowledge.
- Every new domain, topic, and wiki page must be added to the main `index.md` under the correct section
- Every action must be appended to `log.md`
- Raw files always live three levels deep at `raw/<material-type>/<domain>/<topic>/` (never at the `raw/` root); new files are auto-classified — material type by extension/content, domain+topic matching the wiki location
- **Formulas are always LaTeX, never code-style backticks.** Inline math: `$...$`; display math: `$$...$$`. Never wrap a formula in backticks (`` `...` ``) — that renders it as a monospace code span and Obsidian will not typeset it. Write `$x_{1:T} = [m_{\text{root},1:T};\, x_{\text{body},1:T}] \in \mathbb{R}^{T \times D}$`, not `` `x_{1:T} = [m_root; x_body]` ``. (ASCII diagrams stay in code fences — this rule is about math only.)
- All relative paths — in frontmatter (`sources:`, `related:`) and in `[[wikilinks]]` — are resolved from the PKBase root (e.g., `wiki/concepts/agents/discovery/agent-discovery.md`). In Obsidian, set the vault to the PKBase root so these resolve natively.
- **Bilingual pages (only when `bilingual: true`):** each base page `<slug>.md` (written in `default_lang`) MAY have a sibling translation file **in the same directory** named `<slug>.en.md` (when `default_lang: zh`) or `<slug>.zh.md` (when `default_lang: en`). The translation mirrors the base page's structure: same frontmatter fields (`title`, `description`) and the same body sections. The **base file is canonical** — it is the single source of truth for `index.md`, `log.md`, cross-references, and the primary language shown in Obsidian. Translations are **explicit files** written by the user or the agent on request — they are never auto-generated silently, and their `[[wikilinks]]`/`$...$` conventions must match the base page exactly. Translations are optional per page: a page with no translation simply falls back to its base language on the web toggle (see `## Web Site (static showcase)`).

## Page Thresholds
- A concept gets its own page when it is (a) the central subject of a source, or (b) discussed substantively in 2+ sources. A single passing mention (footnote, aside) does NOT warrant a page — link to the nearest existing page instead.
- When in doubt, merge into an existing concept page rather than creating a new one.

## Raw Subdirectories
Every raw file lives at three levels: `raw/<material-type>/<domain>/<topic>/<filename>`.
- **Level 1 (material type)** — default `papers/`, `articles/`, `transcripts/`, `assets/`, `misc/`; auto-classified (extension-first, then a semantic content fallback). Extend for this domain if needed (e.g., `raw/datasets/`).
- **Level 2 (domain) / Level 3 (topic)** — mirror the wiki's `<domain>/<topic>` (see "Domains & Topics" above) so raw material and its summaries/concepts share the same categories.

[Note any per-folder classification hints or domain-specific subfolders here.]

## Depth Levels
The chosen depth level applies to BOTH the source summary (`wiki/sources/<domain>/<topic>/<source-slug>.md`) and the individual concept articles (`<concept-name>.md`). A single paragraph is never enough. Use extensive details, formulas, structure, and methodologies. Break summaries down into multiple specific sections or bulleted insights.
- **100**: Explain like I'm 12 (Feynman technique, analogies, no jargon). Provide multiple angles and examples.
- **300**: College level (technical but accessible, assumes some background). Detail multiple facets, but avoid deepest math.
- **500**: Expert deep-dive (full technical detail, assumes domain expertise). Must include comprehensive, multi-point, structured summaries. Adapt the details rigorously to the source type (e.g., for ML papers: include specific loss functions, architectural parameters, methodology steps, and ablation findings. For non-ML articles, transcripts, or essays: include comprehensive logical breakdowns, specific arguments, nuanced historical contexts, or critical decisions).

## Source Summary Format
For each raw source ingested, create a single `<source-slug>.md` summary file inside `wiki/sources/<domain>/<topic>/`. The summary depth is controlled by the `depth_level` value in `SCHEMA.md` → `## Configuration`.

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
source: raw/<material-type>/<domain>/<topic>/<filename.md>
depth: <100|300|500>
articles_created: [article-one.md, article-two.md, ...]
---

# <Source Title> - Summary

<Summary content written at the configured depth level>

## What This Source Covers
- <bullet summary of main topics>

## Wiki Articles From This Source
- [[article-one]] - one line description
- [[article-two]] - one line description
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
sources: [raw/<material-type>/<domain>/<topic>/filename.md, ...]
related: [wiki/concepts/agents/discovery/other-article.md, wiki/concepts/agents/discovery/another-article.md]
tags: [concept-specific-tag, broader-topic-tag, genai-category-tag]
---

# <Concept Name>

<Encyclopedia-style summary written at the configured depth level. You can and should use ## H2 and ### H3 headers to structure this summary logically when appropriate, rather than keeping it as a single block of text.>

## Key Points
- ...

## Related Concepts
- [[linked-article]] - brief note on relationship

## Sources
- [[wiki/sources/<domain>/<topic>/<source-slug>|<Source Title>]] - what this source contributed
\`\`\`

**Frontmatter rule:** frontmatter values must be plain strings or flat string arrays — never `[[wikilinks]]`, markdown links, or nested arrays. `[[...]]` is only valid in markdown *body* text; in YAML it produces a nested array and breaks Obsidian Properties rendering of the entire frontmatter block. So `related:` and `sources:` store **plain paths** relative to the PKBase root (e.g., `wiki/concepts/agents/discovery/other-article.md`) — these are NOT clickable in Obsidian's Properties panel (a hard Obsidian limitation, not a bug), and they exist for Dataview queries and the agent's own path resolution. **The clickable links live in the body:** `## Related Concepts` and `## Sources` must use `[[wikilinks]]` (see the format above — `## Sources` links to the source-summary page, not the raw file). Both frontmatter paths and body `[[wikilinks]]` resolve from the PKBase root (the Obsidian vault root).

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
- **Comparison Pages (`wiki/comparisons/<domain>/<topic>/`)**: Side-by-side analyses spanning multiple sources. File at `wiki/comparisons/<domain>/<topic>/<comparison-slug>.md` using the same domain/topic as the sources compared. Frontmatter must list `sources:` (every raw source compared), `created`, and `tags`.
- **Query Pages (`wiki/queries/<domain>/<topic>/`)**: Filed query answers worth keeping. File at `wiki/queries/<domain>/<topic>/<query-slug>.md` using the domain/topic the query belongs to. Frontmatter must list `sources:` (the wiki pages or raw sources drawn from), `created`, and `tags`.

## Update Policy
When new information conflicts with existing knowledge across sources:
1. Check the dates — newer sources generally supersede older ones
2. If genuinely contradictory, note both positions with dates and sources in the synthesis concept page. Mark the disagreement explicitly under a dedicated `## Synthesis & Contradictions` header.
3. Mark the contradiction in frontmatter: `contradictions: [source-slug-1, source-slug-2]`
4. Flag for user review in the lint report

```

### index.md Template

The index lives at the PKBase root (alongside `SCHEMA.md` and `log.md`) — it is the single master index; there is no separate `wiki/index.md`. It is sectioned by Domain and Topic. Each source entry should keep its tags in the index so `query` can use them later. Each entry is one line: wikilink + summary + tags.

```markdown
# Wiki Index

> Content catalog. Every wiki page listed under its domain and topic with a one-line summary.
> Read this first to find relevant pages for any query.
> Last updated: YYYY-MM-DD | Total sources: N | Total pages: M

## Domains & Topics

### [Domain Name 1] (e.g., agents)
#### [Topic Name 1] (e.g., discovery)

**Sources**
- [[wiki/sources/agents/discovery/source-slug|Source Title]] - One line summary of the source | tags: [tag-one, tag-two]

**Concepts**
- [[wiki/concepts/agents/discovery/concept-name|Concept Name]] - One line summary of the concept | tags: [tag-one, tag-two]

## Comparisons
<!-- Alphabetical within section, grouped by domain/topic like the pages above -->
- [[wiki/comparisons/agents/discovery/discovery-mechanisms-comparison|Discovery Mechanisms Compared]] - One line summary | tags: [tag-one, tag-two]

## Queries
<!-- Alphabetical within section, grouped by domain/topic -->
- [[wiki/queries/agents/discovery/how-does-discovery-scale|How Does Discovery Scale?]] - One line summary | tags: [tag-one, tag-two]
```

**Scaling rule:** When any section exceeds 50 entries, split it into sub-sections by first letter or sub-domain. When the index exceeds 200 entries total, create a `_meta/topic-map.md` that groups pages by theme for faster navigation.

### log.md Template

```markdown
# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: add, ingest, update, query, lint, create, archive, delete
> When this file exceeds 500 entries, rotate: rename to `log-YYYY-N-MMfirsttoMMlast.md`, start fresh.
> - `N` = 1 + the number of existing `log-YYYY-*.md` files (next free sequence number).
> - `MMfirst` / `MMlast` = zero-padded months of the first and last entry in the file, taken from their `## [YYYY-MM-DD]` dates — e.g. `log-2026-1-01to04.md` covers Jan–Apr 2026.
> - If all entries fall in a single month, use just that month: `log-2026-1-03.md`.
> The rotated file is never overwritten.

## [YYYY-MM-DD] create | Wiki initialized
- Domains & Topics configured
- Depth level: <100|300|500>
- Structure created with SCHEMA.md, index.md, log.md, site/ (web showcase)

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
  - Determine the source's domain and topic — for an already-staged file, read them from its raw path `raw/<material-type>/<domain>/<topic>/`; otherwise derive them from the content

- **Phase 2: Build or update wiki content**
  - **Determine Location:** The source summary goes to `wiki/sources/<domain>/<topic>/<source-slug>.md`; each concept article goes to `wiki/concepts/<domain>/<topic>/<concept-name>.md`. Create the domain/topic directories as needed — no per-source folders.
  - **New concepts:** Extract 3-10 highly granular key concepts from the raw file. Adapt the concept type to the source material:
    - *For ML / Technical papers:* specific algorithms, architecture sub-components, datasets, distinct limitations, loss functions, or mathematical derivations.
    - *For general articles, transcripts, or essays:* primary arguments, mental models, key historical events, decision-making frameworks, or underlying principles.
    Break concepts down as far as they logically go rather than grouping them into a few broad topics.
  - **For each concept:**
    - Use the environment's file-search tool to check if a wiki article already exists anywhere in `wiki/`
    - If yes: update and expand the article, add new source to frontmatter, update the `updated` date
    - If no: create a new article at `wiki/concepts/<domain>/<topic>/<concept-name>.md`
  - **Cross-reference:** Every new or updated page must link to at least 2 other pages via [[wikilinks]].
  - **Backlink enforcement:** If linked pages do not link back, add backlinks in those related pages using relative paths across folders.
  - **Tags:** Use only tags defined in SCHEMA taxonomy. If a new tag is needed, add it to SCHEMA first with a short definition, then use it in articles.
  - **Media integration:** Embed extracted original media files (images, videos, etc., located in `raw/assets/<domain>/<topic>/`) into the source summary and concept wiki pages where they are contextually relevant. Use Obsidian-style media links (e.g., `![[filename.ext]]`) — these resolve by file name, so nesting does not break them.
  - **Summary:** Create the source summary at `wiki/sources/<domain>/<topic>/<source-slug>.md` at the configured depth level
  - **Translation (only when `bilingual: true` in SCHEMA.md):** if the user requested a translation for this source, or the PKBase's working pattern includes it, also create/update the sibling translation file `<slug>.en.md` (or `<slug>.zh.md` when `default_lang: en`) next to every page created/updated above, mirroring its structure (same frontmatter fields + same body sections). Never auto-translate silently without the user's intent — when in doubt, skip the translation and mention it in the report. When the base page is later updated, its translation file must be updated to stay in sync (checked by `lint` → Phase 8).

- **Phase 3: Update navigation**
  - Add new pages to `index.md` under the correct Domain and Topic section, alphabetically
  - Update the "Total pages" count and "Last updated" date in index header

- **Site rebuild:** when `add` / `ingest` call this command, they rebuild `site/data.js` in their final phase (see `## Web Site (static showcase)`). If `process` is called **directly** (not via add/ingest), regenerate `site/data.js` before reporting — the site must never lag behind the vault.

### 2. Add

**Command Argument:** `add [URL | file path | pasted text]`

When the user provides a source (URL, file, paste), integrate it into the wiki:

- **Phase 1: Capture the raw source**
  - **Original Files Constraint**: ALWAYS save the original files (PDFs, images, videos, audio) into the appropriate 3-level `raw/` path `raw/<material-type>/<domain>/<topic>/` — classify per "Raw Folder Organization (3-level, auto-classification)" above — in addition to extracting their text. File paths given by the user are **copied** into `raw/`; the original file is left in place.
  - URL → fetch the page to markdown (any web-extraction tool available in the environment), save under `raw/articles/<domain>/<topic>/`
  - PDF → copy the original `.pdf` to `raw/papers/<domain>/<topic>/`, extract its text, and save the markdown alongside in the same folder
  - Images/Videos/Audio → copy the original media files to `raw/assets/<domain>/<topic>/`
  - Pasted text → save under `raw/<articles|papers|transcripts>/<domain>/<topic>/` (use the semantic fallback to pick the material type)
  - Name the file descriptively using the format `YYYYMMDD-[author/source]-[topic-slug].[ext]`.
    Examples:
    - `raw/articles/multimodal-learning/interactive-motion/20260419-karpathy-llm-wiki.md`
    - `raw/papers/multimodal-learning/interactive-motion/20260408-arxiv-2509-07367.md`

- **Phase 2: Check what already exists**
  - Read `index.md` to understand existing articles
  - Read `log.md` to understand what has been done before

- **Phase 3: Write or update wiki pages**
For each unprocessed raw source file, call the reusable `process` command to process that file.

- **Phase 4: Append to `log.md`**
  - Append to `log.md`: `## [YYYY-MM-DD] Add | Source Title` and log the Domain/Topic along with all created/updated files.
    ```md
    ## [YYYY-MM-DD] Add | <source description>
    - Domain: <domain>
    - Topic: <topic>
    - Processed: raw/<material-type>/<domain>/<topic>/<filename>
    - Created: <list of new wiki articles>
    - Summary: wiki/sources/<domain>/<topic>/<source-slug>.md (depth: <100|300|500>)
    - Updated: <list of updated wiki articles>
    ```

- **Phase 5: Rebuild the web site** — regenerate `site/data.js` from the updated vault (see `## Web Site (static showcase)` → Rebuild procedure).

- **Phase 6: Report what changed**
  - List every file created or updated to the user, including their full paths within the domain structure, plus the site rebuild line ("site rebuilt (N pages, M raw files)").

A single source can trigger updates across 5-15 wiki pages. This is normal and desired — it's the compounding effect.

### 3. Ingest

**Command Argument:** `ingest [source folder path]`

Process all unprocessed files and compile them into wiki articles. Where the material comes from depends on the argument:

- **No argument (default):** process files already inside `raw/`.
- **A folder path** (any directory — typically the user's own pile of PDFs/articles living outside the PKBase): first **stage** the ingestible files from that folder into `raw/` (auto-classified into the 3-level path + renamed per "Raw Folder Organization (3-level, auto-classification)"), then process them. Originals are **copied, never moved or modified**.

- **Phase 0: Stage files into `raw/` (only when a folder path is given)**
  1. List the files in the folder (recursively).
  2. Skip non-ingestible files (spreadsheets, code, OS junk such as `Thumbs.db`/`.DS_Store`) and files already present in `raw/` (match by name + size).
  3. For each remaining file: pick its 3-level `raw/` path `raw/<material-type>/<domain>/<topic>/` (material type by extension-first/semantic fallback, domain+topic from the content — see "Raw Folder Organization (3-level, auto-classification)"), rename it to `YYYYMMDD-[author/source]-[topic-slug].[ext]`, and copy it there. On a name collision, append `-2`, `-3`, … — never overwrite.
  4. Report the staged files (`original path → raw path`) before processing continues.

- **Phase 1: Find unprocessed files**
  1. List all files in `raw/`
  2. Read `log.md` **and every rotated log (`log-*.md`)** to find which files have already been processed — after a rotation, most history lives in the rotated files, so checking only `log.md` would cause everything to be re-processed
  3. Identify files in `raw/` that are NOT mentioned in any log file

If all files are already processed, tell the user "Nothing new to ingest." and stop.

- **Phase 2: Read existing wiki state**
  1. Read `index.md` to understand existing articles and categories
  2. Scan `wiki/sources/` and `wiki/concepts/` for existing summary and concept pages

- **Phase 3: Process each new raw file**
For each unprocessed raw file, call the reusable `process` command with that file path.

- **Phase 4: Append to `log.md`**
  - Append to `log.md` as a batch summary with one per-source block:
    ```md
    ## [YYYY-MM-DD] Ingest | Batch Summary
    - Staged: <n> files copied from <source folder>   <!-- only when a folder path was given -->
    - <source description>
      - Domain: <domain>
      - Topic: <topic>
      - Processed: raw/<material-type>/<domain>/<topic>/<filename>
      - Created files: <list of new wiki articles>
      - Summary: wiki/sources/<domain>/<topic>/<source-slug>.md (depth: <100|300|500>)
      - Updated files: <list of updated wiki articles>
    - <source description>
      - ...
    ```

- **Phase 5: Rebuild the web site** — regenerate `site/data.js` from the updated vault (see `## Web Site (static showcase)` → Rebuild procedure).

- **Phase 6: Report what changed**
  - List every file created or updated to the user, including their full paths within the domain structure, plus the site rebuild line ("site rebuilt (N pages, M raw files)").

### 4. Query

**Command Argument:** `query [your question]`

When the user asks a question about the knowledge base. Searches wiki articles and synthesizes an answer with references.

- **Phase 1: Read `index.md`** to identify relevant pages.
- **Phase 2: Search by tags**: identify tags most relevant to the question, then find articles sharing those tags in `index.md`.
- **Phase 3: For wikis with 100+ pages**, also search across all `.md` files for keywords related to the question — the index alone may miss relevant content.
- **Phase 4: Read the most relevant wiki articles.** If wiki articles reference `raw/` sources and more detail is needed, read those too.
- **Phase 5: Synthesize an answer** from the compiled knowledge. Cite the wiki pages you drew from: "Based on [[page-a]] and [[page-b]]..."
- **Phase 6: File valuable answers back** — if the answer is a substantial comparison, deep dive, or novel synthesis, create a page at `wiki/queries/<domain>/<topic>/<query-slug>.md` or `wiki/comparisons/<domain>/<topic>/<comparison-slug>.md` (using the same three-level domain/topic structure). Don't file trivial lookups — only answers that would be painful to re-derive.
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
- **Phase 8: Rebuild the web site** — only if Phase 6 filed a page (vault state changed): regenerate `site/data.js` (see `## Web Site (static showcase)` → Rebuild procedure) and include the site rebuild line in the final answer.

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
  BROKEN LINK: [[wikilink]] in wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md
  ```

- **Phase 2: Legacy Markdown Links**
  - Scan all wiki articles for explicit markdown links `[text](path.md)`.
  - These should be converted to Obsidian-style `[[link]]` syntax to match the PKBase standard.
  - Report each finding as:
  ```
  LEGACY LINK: [text](path.md) in wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md — convert to [[link]]
  ```

- **Phase 3: Missing articles (concept frequency audit)**
  - Build a concept/term frequency map across different wiki articles.
  - Flag terms that appear in 3+ distinct articles but do not have a dedicated wiki page.
  - Use normalized terms (case-folded, punctuation-trimmed) and ignore stopwords/common jargon.
  - Report each finding as:
  ```
  MISSING ARTICLE: "<concept>" mentioned in N articles but has no wiki page
  ```

- **Phase 4: Index consistency (`index.md` vs filesystem)**
  - Compare index entries against actual files under `wiki/`.
  - Detect:
    - files that exist but are not listed in index
    - files listed in index but missing on disk
    - summary files listed but absent
  - Report each finding as:
  ```
  INDEX STALE: wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md exists but not in index
  INDEX GHOST: wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md listed in index but file missing
  ```

- **Phase 5: Source traceability (`frontmatter.sources`)**
  - Ensure every wiki page has at least one source in frontmatter (`source:` for source summaries, `sources:` for concept pages).
  - Validate that each source path points to an existing file under `raw/`.
  - Report each finding as:
  ```
  NO SOURCE: wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md has no source listed
  MISSING SOURCE: wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md references raw/<file>.md which does not exist
  ```

- **Phase 6: Summary completeness**
  - For each source recorded in `log.md` or any rotated log (`log-*.md`), verify:
    - a summary file exists at `wiki/sources/<domain>/<topic>/<source-slug>.md`
    - the summary's `articles_created:` frontmatter lists at least one concept page, and those pages exist on disk
  - Report each finding as:
  ```
  MISSING SUMMARY: raw source <filename> was logged but wiki/sources/<domain>/<topic>/<source-slug>.md does not exist
  EMPTY SUMMARY: wiki/sources/<domain>/<topic>/<source-slug>.md exists but created no concept pages
  ```

- **Phase 7: Stale backlinks (`related:` validation)**
  - Parse `related:` entries in frontmatter and verify each referenced article exists.
  - Report each finding as:
  ```
  STALE BACKLINK: wiki/<sources|concepts|comparisons|queries>/<domain>/<topic>/<file>.md links to a non-existent article
  ```

- **Phase 8: Optional integrity checks**
  - Tag audit: list tags in use and flag tags not declared in `SCHEMA.md` taxonomy.
  - Log rotation: if `log.md` exceeds 500 entries, rotate to `log-YYYY-N-MMfirsttoMMlast.md` (naming rule in the log.md template — never overwrite an existing rotated log).
  - **Translation sync (only when `bilingual: true` in SCHEMA.md):** for every base wiki page that has a sibling translation file (`<slug>.en.md` / `<slug>.zh.md`), compare timestamps: if the base page's `updated` frontmatter (or file mtime) is newer than the translation file's, the translation is stale. Report each finding as:
  ```
  STALE TRANSLATION: wiki/<type>/<domain>/<topic>/<slug>.md is newer than its <slug>.en.md — re-translate to sync
  ```
  Pages without a translation file are NOT an issue (translation is optional per page) — but if the user expected full coverage, list the untranslated count as a summary line in the report.

- **Phase 9: Web site sync check**
  - If `site/` is missing entirely, report `MISSING SITE: run init's step 8 (copy web-template, seed data.js)` — do not recreate it silently.
  - Compare `site/data.js` against the vault: page count per type vs. `wiki/<type>/**/*.md`, raw file count vs. `raw/` inventory, and `meta.updated`. If they diverge, report `STALE SITE: data.js has <n> pages but vault has <m>; regenerating`.
  - **Rebuild the site** as the final step of lint (regenerate `site/data.js` per `## Web Site (static showcase)` → Rebuild procedure), even when the report has zero issues — lint is the designated repair point for a drifted site.

- **Phase 10: Lint report + logging**
  - Group findings by severity priority:
    1. broken links / missing sources / stale backlinks
    2. index ghosts/stale entries
    3. missing articles
    4. legacy markdown links / style issues
  - Include exact file paths and actionable fixes, and end with the site rebuild line ("site rebuilt (N pages, M raw files)").
  - Append to `log.md`:
  ```md
  ## [YYYY-MM-DD] lint | N issues found
  - Broken wikilinks: <count>
  - Legacy markdown links: <count>
  - Missing articles: <count>
  - Index stale/ghost entries: <count>
  - Source traceability issues: <count>
  - Summary completeness issues: <count>
  - Stale backlinks: <count>
  - Stale translations: <count>   <!-- only when bilingual: true; omit the line otherwise -->
  - Site: <rebuilt|stale-rebuilt|missing>
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
- Regenerate `site/data.js` (already done in Phase 9; confirm the preview at `site/index.html`)

## Working with the Wiki

### Searching

Use the file tools available in your environment to navigate the PKBase efficiently:

- **Find pages by content:** full-text search `$PKBASE/wiki` for a keyword (e.g. "transformer") across `*.md` files
- **Find pages by filename:** list/glob `*.md` under `$PKBASE/wiki`
- **Find pages by frontmatter tag:** search for `tags:.*<tag>` under `$PKBASE/wiki`
- **Read recent log activity:** read the last ~20 lines of `$PKBASE/log.md`

### Archiving

When content is fully superseded or the domains/topics scope changes:
1. Create a `_archive/` directory at the PKBase root if it doesn't exist.
2. Move the page to `_archive/` while preserving its domain structure (e.g., move to `_archive/concepts/agents/discovery/old-concept.md`).
3. Remove the corresponding entry from `index.md`.
4. Update any pages that linked to it — replace the `[[wikilink]]` with plain text + "(archived)".
5. Append an archive action to `log.md`.

### Obsidian Integration

The wiki directory works as an Obsidian vault out of the box:
- `[[wikilinks]]` render as clickable links
- Graph View visualizes the knowledge network
- YAML frontmatter powers Dataview queries
- The `raw/assets/` tree holds images referenced via `![[image.png]]` (these resolve by file name, so the `<domain>/<topic>` nesting does not break them)

For best results:
- Set Obsidian's attachment folder to `raw/assets/`
- Enable "Wikilinks" in Obsidian settings (usually on by default)
- Install Dataview plugin for queries like `TABLE tags FROM "entities" WHERE contains(tags, "company")`

If using the Obsidian skill alongside this one, set `OBSIDIAN_VAULT_PATH` to the
same directory as the wiki path.

## Pitfalls

- **Never forget to rebuild the site** — every operation that changes vault state (`init`, `add`, `ingest`, a filed `query`, `lint`, or any direct page/raw/log edit) ends by regenerating `site/data.js`. A site that lags behind the vault is a stale artifact; `lint` detects and repairs this.
- **Never hand-edit `site/` files except `data.js`** — `index.html` / `style.css` / `app.js` / `README.md` come verbatim from the skill's `web-template/`; if they need to change, update the template and re-copy.
- **Never modify files in `raw/`** — sources are immutable. Corrections go in wiki pages.
- **Stage by copying, never by moving** — when ingesting from an external folder, the user's originals stay where they are; `raw/` receives copies. Never overwrite an existing `raw/` file (rename with `-2`, `-3`, …).
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
- **Translation files are siblings, never a separate tree** — a bilingual page's translation lives at `wiki/<type>/<domain>/<topic>/<slug>.en.md`, next to its base file. Never rename the base file, never nest translations in a separate folder, and never list them in `index.md` (the base page is the only indexed entry). The rebuild merges them into the **same** `data.js` entry (`title_en`/`description_en`/`body_en`) — if a rebuild emits a translation as its own page, the site will show duplicate entries.
- **Never translate silently** — translation files are explicit. Only create or update `<slug>.en.md` when the user asked for it (or the PKBase convention says to); base pages always stay in `default_lang`.
- **Keep pages scannable** — a wiki page should be readable in 30 seconds. Split pages over
  200 lines. Move detailed analysis to dedicated deep-dive pages.
- **Ask before mass-updating** — if an ingest would touch 10+ existing pages, confirm
  the scope with the user first.
- **Rotate the log** — when log.md exceeds 500 entries, rename it `log-YYYY-N-MMfirsttoMMlast.md` (sequence number + the month range of the entries it holds) and start fresh. Never overwrite a rotated log — it holds the processing history.
  The agent should check log size during lint.
- **Handle contradictions explicitly** — don't silently overwrite. Note both claims with dates,
  mark in frontmatter, flag for user review.
