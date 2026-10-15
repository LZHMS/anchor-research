---
name: research-paper-poster
description: Organizes a verified final paper and its bound result data into a reviewed A0/A1 poster, editable LaTeX, preview, PPTX/SVG exports, and presentation notes. Terminal stage after manuscript writing.
version: 3.1.0
author: Zhihao Li
license: MIT
metadata:
  related_skills: [research-paper-plan, research-paper-writing]
  tags: [Research, Poster, Conference, LaTeX, Results, Visual Review]
---

# Research Paper Poster

Turn the **final matching manuscript and its exact underlying results** into a visual story understandable in 60 seconds. This is visual organization, not another experiment, dataset-selection, statistical-analysis, or paper-writing stage. The source paper, approved claims, uncertainty, limitations and data provenance remain authoritative.

Use host-provided file access, execution, questions, visual inspection and, when available, isolated independent review. No particular agent framework, service, model, operating system or host tool interface is required. Compilers, libraries, fonts and renderers are actual dependencies to inspect, not assumed capabilities.

Follow the [shared human anchor gates](../research-shared-references/anchor-gates.md); retain the explicit gates here if the reference is unavailable. This is not an autonomous publication pipeline: input acceptance, content/layout decisions and any external action have different scopes.

## 1. Scope, paths and authorization

Resolve `PROJECT_ROOT` from explicit input, then a valid accepted invocation, then the current working project. Never use the installed skill directory as the project. `DOCS_ROOT` defaults to `PROJECT_ROOT/docs`; inherit an explicitly bound override. Relative project inputs resolve against `PROJECT_ROOT`.

| Binding | Default |
|---|---|
| `PLAN_DIR` | `DOCS_ROOT/research-paper-plan` |
| `WRITING_DIR` | `DOCS_ROOT/research-paper-writing` |
| `POSTER_DIR` | `DOCS_ROOT/research-paper-poster` |
| `manuscript_manifest_path` | `WRITING_DIR/MANUSCRIPT_MANIFEST.json` |
| `writing_state_path` | `WRITING_DIR/WRITING_STATE.json` |
| `bundle_path` | `PLAN_DIR/PAPER_BUNDLE.json` |
| `paper_pdf_path`, `paper_tex_path` | Exact matching paths in the manuscript manifest; normally `WRITING_DIR/main.pdf`, `WRITING_DIR/main.tex` |

Respect explicitly bound existing sources and output paths without moving or deleting user material. Do not silently fall back to root-level `paper/`, `poster/`, dated directories, or whichever file looks newest. Follow actual TeX includes, bibliography and asset paths; do not assume `sections/*.tex` exists. Inspect existing outputs before changing them and preserve unrelated files. No automatic backup-directory recipe or overwrite of an unrelated poster.

### Entry is one authorized stage

A direct explicit request authorizes this stage once, not other stages. Otherwise require the unique latest unresolved bare-object `NEXT_SKILL_HANDOFF` from `research-paper-writing` to `research-paper-poster`, with:

- `from_skill`, `to_skill`, `project_root`, `docs_root`, `invocation`;
- `artifacts`: actual `{role,path,sha256}` entries for all control files and consumed sources/assets/results;
- `status: awaiting_confirmation`;
- `manuscript_manifest_path`, `writing_state_path`, `bundle_path`, `paper_pdf_path`, `paper_tex_path`, `asset_paths`, `target_venue`, and actual build/evidence limitations.

Echo its fully resolved recommended **chat invocation**, not a shell command. A direct unambiguous yes/可以/继续 to that unique offer consumes consent once. Refusal sets `declined`. Quoted or ambiguous assent, silence, timeout, autonomous mode, or already consumed assent never authorizes entry. Interpret the entire response; “yes, but do not execute yet” is not permission to execute.

Validate the exact bound bytes before writes/actions. Changed paths, hashes or semantic bindings make the offer `stale`; report the differences and require a fresh scoped invocation or refreshed offer and assent. Track `accepted`, `running`, `completed` or `failed` according to actual outcomes; pending checkpoints are not completion. Revalidate immediately before acting. A saved state can resume only the same authorized stage with unchanged inputs; age or an `in_progress` label is not authorization.

Example invocation shape (replace every value with actual resolved project paths before recommending it):

```text
/research-paper-poster project_root="<PROJECT_ROOT>" docs_root="<DOCS_ROOT>" manuscript_manifest_path="<WRITING_DIR>/MANUSCRIPT_MANIFEST.json" writing_state_path="<WRITING_DIR>/WRITING_STATE.json" bundle_path="<PLAN_DIR>/PAPER_BUNDLE.json" paper_pdf_path="<WRITING_DIR>/main.pdf" paper_tex_path="<WRITING_DIR>/main.tex" asset_paths=[<actual included source and asset paths>] target_venue="<known venue or generic>"
```

Outline approval authorizes neither writing nor poster generation; writing approval authorizes neither poster generation nor publication. This is the **terminal stage**. Do not issue a next-stage handoff, upload, submit, print, publish, notify a service, stage/commit/push, modify experiments, control training processes, or automatically install dependencies.

## 2. Hard input gate: verify final paper, build and results

Read all three stage contracts, not only the PDF. Required normal inputs are:

1. `MANUSCRIPT_MANIFEST.json` (`schema_version: 1`) and `WRITING_STATE.json` with `status: ready`, `compilation_status: succeeded`, the exact manifest digest, matching `bundle_sha256`, genuine completed review evidence and `manuscript_approval.approved: true` bound to that actual manifest SHA-256 with a real user confirmation reference. Review success alone is not manuscript acceptance.
2. The manifest's final paper PDF, TeX entry, **every actual include**, bibliography, figures, tables, other build inputs, build log/report and independent reviews. Validate the manifest's `sources`, `files`, real build command/cwd/engine/version/exit code/log digest, actual build-input hashes and final PDF correspondence. Manifest/state files cannot hash themselves cyclically.
3. The frozen `PAPER_BUNDLE.json` (`schema_version: 1`), its exact `PAPER_PLAN.md`, `RESULTS.json`, prepared tables/figures, analysis/source-data trace, and `PAPER_PLAN_STATE.json`. Verify current plan and bundle digests, ready state, independent evidence/code/narrative review and `outline_approval.approved` bound to the current bundle digest with an actual user confirmation reference.
4. Every consumed file in the bundle's `sources` and `derived` inventories, including original code/config/attempt bindings and completed machine-readable results, by exact path and SHA-256. Preserve `repo_path` and any supplied `code_paths`, `result_paths`, `report_paths`, `evidence_paths` provenance; reports and diagnostic recommendations are context, never measurements. Follow the bundle's actual source inventory rather than guessing these paths or collecting an entire repository.

Hash the actual file bytes, including actual UTF-8 artifact bytes, with no normalization or invented digest. Control digests must match both upstream state and the incoming artifact inventory. Trace manuscript numeric claims/captions through planned claim IDs, result/aggregate IDs, prepared figure/table IDs, transforms, and original source path/hash/locator. Inspect actual result values and actual final paper content; a self-reported success flag or a file's existence is not proof of correspondence. Growing logs must already be bound to frozen consumed snapshots with source identities/watermarks; never silently rebind to a newer window or reinterpret a reset/truncated log.

Direct existing manuscripts may supply **exact equivalent genuine** final-build, source/data-binding, approval and independent-review evidence instead of the canonical files. Enumerate and verify the equivalence and any absent context in `POSTER_REPORT.md`; do not fabricate a canonical history, invent approvals, or auto-rerun writing to fill gaps. Lack of genuine build/data/review evidence blocks entry. If the binding cannot establish that the PDF was actually built from the provided exact inputs, stop; do not choose the latest PDF, trust modification times, or compile different manuscript sources to manufacture correspondence.

**Fail entry** for uncompiled sources, PDF-only or source-only drafts, failed/stale builds, byte mismatches, unresolved mandatory manuscript reviews, unapproved current evidence, missing underlying data or unresolved paper/data discrepancies. Preserve all limitations; report exactly which evidence must be repaired upstream. Do not continue by dropping an inconvenient dataset, claim or failed result.

## 3. Portable prerequisites and design settings

Check capabilities without changing the environment. Record available executable/library/font versions and the exact commands/interpreter chosen. For example, an available Python interpreter can use `shutil.which` for executable discovery and `importlib.util.find_spec` for installed-module discovery; probe actual imports/versions before relying on them. Equivalent host-native discovery is fine. Never use automatic package installation, global environment changes, arbitrary template downloads or platform-specific path recipes.

Needed capabilities depend on requested formats:

- An available LaTeX engine and build driver, with the actual packages/fonts used by the selected source. `latexmk` with `pdflatex` is one option; a Unicode-capable engine and matching installed fonts may be needed for multilingual content. Inspect project configuration before selecting the engine.
- A PDF reader/renderer and page/metadata inspection; an available PDF library such as PyMuPDF can render previews, crop cards and export SVG. It is not guaranteed installed or universally compatible.
- A native PPTX writer such as `python-pptx`, plus an available presentation renderer/viewer for **actual export inspection**. Writing a ZIP/XML package alone does not prove correct presentation rendering.
- An SVG renderer/viewer, and actual image-inspection capability. A text-only file read or numeric geometry check is not visual review.

If a required dependency/capability is absent, record a precise blocker and preserve useful completed artifacts. Do not claim the format or stage complete. Any environment provisioning requires a separate explicit user-approved action, not an implicit skill step.

| Setting | Default / interpretation |
|---|---|
| Venue | Bound `target_venue`, otherwise clearly generic; verify actual venue/year size rules if supplied. Colors never imply official venue compliance. |
| Size | A0: 841 × 1189 mm; A1: 594 × 841 mm |
| Orientation | Landscape by default; actual venue/user constraints take precedence |
| Columns / rows | A0 landscape: 4 / 20; A0 portrait: 3 / 20; A1 landscape: 3 / 16; A1 portrait: 2 / 20 |
| Template | Optional actual bundled `templates/` or user-supplied template, inspected as design context, not assumed current venue requirements |
| Logos | Optional real, authorized assets matching actual affiliations; none if unverified |
| Exports | Default full suite below; honor an explicitly requested narrower suite and record its scope before production |
| `auto_proceed` | False; only an explicit request may waive **poster-internal** content/layout checkpoints |

Keep bundled `templates/` and `logos/` intact. A filename/affiliation resemblance is not permission or identity proof. Prefer vector logos or sufficient effective resolution at actual displayed size; inspect quality and rights. No invented affiliations, fake logos, decorative QR placeholders or implied repository links. Only include a QR code for a real authorized URL; actually generate it and verify its decoded destination. Omit QR/link blocks when no verified destination exists.

## 4. Extract and confirm the content story

Read the entire final PDF and actual TeX include graph, then the bound result evidence. Produce `POSTER_DIR/POSTER_CONTENT_PLAN.md` containing:

- Exact paper title, authors/affiliations, source PDF digest, venue/year if known, size/orientation and intended reader.
- A 60-second path: problem → key idea → method overview → strongest **already approved** evidence → limitations/takeaway. Do not force a positive finding; negative or inconclusive final findings are legitimate.
- Each card's text/caption, word budget, figure/table selection and placement; each numeric callout's claim/result/aggregate IDs and exact paper section/page/table/figure locator.
- A content-to-data map with original source path/hash/locator, valid denominator, uncertainty definition, dataset/task/split/protocol/budget and transformations. Retain exclusions and paper caveats where needed to interpret a number.
- The requested export suite, known format limitations, real template/logo/URL sources and permissions, and unresolved issues.

Target roughly **300–500 words** excluding references and necessary captions; use brief bullets and one-line takeaways rather than an abstract paragraph. Five-to-eight-word phrases are useful, not a rule that permits removing scientific qualifiers. Avoid dense copied paragraphs. Figures may occupy roughly 40–50% of usable area when evidence supports it, but no quota justifies invented charts. Select the real method/overview figure and main evidence first; include ablations or qualitative examples only when present and material. There is no mandatory figure count or mandatory statistical banner. Use headline numbers only when their baseline, denominator, uncertainty and limitations remain honest; otherwise use concise factual takeaways.

**Content checkpoint:** show the actual content plan, evidence map, selected figures, word count, requested formats and limitations, then wait for explicit confirmation unless the user explicitly waived this poster-internal checkpoint. Record the confirmation reference or waiver scope in state. Consent to content selection does not approve altered results.

### Permitted figure work

Reuse approved prepared figures/tables, making portable local copies under `POSTER_DIR/figures/` or `tables/` and recording original plus copy hashes. Do not modify source assets. Symlinks are not categorically unsupported by LaTeX, but packaged copies avoid unresolved external references; check actual resolution and permissions rather than asserting an operating-system limitation.

Restyling/replotting the **same exact approved data** is allowed only with runnable local source, recorded commands/dependencies, source IDs and transformations. Inspect inherited plotting code for side effects before execution. Preserve the selected comparisons, scales that affect interpretation, dataset/split, metric/direction/unit, aggregate membership, denominator and uncertainty semantics. Check generated numerical labels against bound records/aggregates and actually inspect the plot. No new training/inference/evaluation, statistical tests, claims, metrics, baselines, recomputed aggregates, seed selection, dataset selection, fabricated bars/curves, simulated results or selective smoothing. New evidence or semantic corrections return to planning/writing with fresh approval; this stage does not silently repair the paper.

## 5. Compose a real A0/A1 layout

Use a genuine inspected supplied template when appropriate. Otherwise **article + geometry + tcbposter** is a practical default if available. It avoids the overlay complexity of presentation classes; do not claim other classes always fail. Load only required libraries, rather than broad package bundles that introduce unnecessary dependencies. Plain `includegraphics` width/height constraints generally avoid needing an extra sizing package.

A minimal package foundation for A0 landscape is:

```latex
\documentclass{article}
\usepackage[paperwidth=1189mm,paperheight=841mm,margin=0mm]{geometry}
\usepackage{tcolorbox}
\tcbuselibrary{poster,skins,fitting}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage[table]{xcolor}
\pagestyle{empty}
```

This is package guidance, **not a completed poster**. When invoked, write a complete `POSTER_DIR/main.tex` with actual approved content, available fonts, style definitions, all posterboxes and one-page layout. Use `[table]{xcolor}` when using table row colors. Select fonts/encoding for the actual engine and language; do not blindly add incompatible font packages.

### Concrete layout rules

- Use a fine grid for explicit placement, e.g. `rows=20` and `between=rowN and rowM`; align all cards in a row band across columns. Reconcile actual grid coordinates with measured page/card bounds, not approximate row-height arithmetic.
- A0 portrait usually benefits from 2–3 columns, not a cramped 4-column default. A1 needs fewer columns or less content; do not just shrink A0 and assume readability.
- Allocate title, optional headline band and body deliberately. A portrait starting point is title to row4, optional callouts row4–row6, then shared body bands row6–row11, row11–row16, and row16–bottom. Omit/reallocate the callout band if it has no justified content.
- Fine grids reduce wasted blank bands, but **fixed-height cards can silently clip content even after successful compilation**. Inspect every bottom edge. Favor removing nonessential words over shrinking fonts.
- Start with about 70% card fill and deliberate gutters. Zero grid spacing can work when card padding provides separation; it is not a universal requirement. Keep related captions/figures consistently spaced, e.g. 3 mm after image, 2 mm after caption.
- Use high-contrast text and a restrained primary/secondary/accent palette. A dark title color such as `#1E293B`, secondary `#334155`, accent `#2563EB` and light background `#F8FAFC` is a generic starting point. Venue-inspired colors are optional design choices, not official branding.
- Subtle card tints, a left accent stripe (`borderline west={5pt}{0pt}{color}`) and restrained shadows can create hierarchy. White backgrounds are also valid. Inspect real contrast; do not rely on color alone to encode results. Test highlights around 18–25% tint and alternate table rows around 15% where appropriate; adapt after viewing.
- For A0 with literal article-class point sizes, start near title 84–90 pt, authors 40–42 pt, headings 40–42 pt, body 32–34 pt with 40–44 pt leading, captions 26–28 pt and callouts 66–72 pt. These are starting sizes, not a guarantee of readability; inspect actual-size crops and a distance-simulating full-page view. A1 sizing requires its own review.
- Keep tables small enough to read, with explicit units and uncertainty labels. Use only approved equations; split long equations or reduce surrounding content. Inline `\(\displaystyle ...\)` inside a centered `\parbox` can avoid display-math margins in narrow colorboxes; check real bounds rather than hiding overflow.

**Layout checkpoint:** present the actual card allocation, dimensions, palette, fonts and prepared assets before compilation. Wait for explicit approval unless this internal checkpoint was explicitly waived. Persist bindings to the exact content/layout approved. Material changes invalidate affected approval/review; do not silently reuse old confirmations.

## 6. Compile, inspect and independently review

Build only the poster, not the manuscript or experiments. Inspect selected build scripts for source writes, downloads, shell escape or other side effects first; do not enable unsafe execution automatically. With an available compatible setup, a concrete build command is `latexmk -pdf -interaction=nonstopmode -halt-on-error -recorder main.tex`, executed with `cwd=POSTER_DIR`; choose the corresponding supported engine option when needed. Record the actual command/cwd/engine/version, exit code, build log/hash, exact input hashes and produced PDF hash.

A successful exit code is necessary, not sufficient. On failure, inspect the first relevant error and apply a targeted fix; do not suppress errors or repeatedly retry unchanged builds. Missing dependencies are blockers, not permission to install. For missing files, inspect actual references and resolution; for overflow, reduce content or alter geometry deliberately. Rebuild after actual source/layout changes and retain useful bounded diagnostic evidence, not automatic directory backups.

Verify the produced PDF really corresponds to this build and:

- Opens successfully; has exactly one page; has intended MediaBox/CropBox, rotation and orientation.
- Measures the requested physical size (A0 landscape about 3370.39 × 2383.94 PDF points; A1 landscape about 2383.94 × 1683.78; reverse for portrait). Record measured dimensions and a documented small tolerance.
- Has no missing assets, unresolved references/citations, unexpected font substitutions or fatal build issues. Inspect font availability/embedding and actual image resolution; no unsupported universal “print-ready” guarantee.
- Has actual text, values, labels, captions and necessary limitations matching the approved content and source evidence.

### Actual visual review

Render the built final PDF into `poster_preview.png` and suitable full-resolution/card crops; 150–200 DPI is often adequate for overview review, with higher-resolution crops for text/plot labels. A renderer alone is not a reviewer. **Actually view the images** through available image capability, inspecting:

1. Every card's complete text, lower edge and figure bounds for clipping/overlap.
2. Title → idea → evidence → takeaway flow, alignment, gutters and whitespace balance.
3. Smallest plot labels, equations, table cells, references and body text at useful physical/distance scales; do not equate arbitrary “100% zoom” with actual A0 size.
4. Correct values, series/legend correspondence, axes/units/error bars, caveats, logos and real links.
5. Contrast, figure prominence and whether the 60-second story is understandable.

Record actual inspected image paths/hashes, capability used, concrete observations, fixes, and final verdict in `POSTER_VISUAL_REVIEW.md`. Scores are optional and never replace findings. If image inspection is unavailable, say **visual review unavailable/unverified**, leave the gate blocked, and do not invent a visual score or claim a text read is a visual review.

### Independent critical review

Use an available isolated reviewer capability or an actual separate reviewer, without prescribing a framework/model/profile. Provide the exact final content plan, PDF and rendered images, source, claim/data map, source limitations and build evidence. Request evidence-backed findings on content fidelity, statistical qualifiers, hierarchy, density, readability, clipping, figure integrity and export requirements. The reviewer must not modify upstream evidence, create missing measurements or approve user intent.

Save actual review reports under unused flat names `poster-review-0001.md`, `poster-review-0002.md`, etc. Include reviewer independence and exact reviewed artifact hashes. Apply mandatory fixes, then recompile, rerender and repeat affected reviews on the changed final artifacts. Missing independent capability or unresolved mandatory findings leaves `awaiting_review` or `blocked`, never an invented pass. Only export finalized reviewed content; later changes invalidate derived exports and affected reviews.

## 7. Produce and verify every requested export

Default final deliverables in `POSTER_DIR`:

| Artifact | Meaning and limits |
|---|---|
| `main.tex`, included files, `figures/`, `tables/`, optional `logos/` | Editable portable LaTeX source package with actual local asset bindings |
| `main.pdf` | Actual successfully built and reviewed single-page A0/A1 PDF |
| `poster_preview.png` | Actual rendered preview of that exact PDF |
| `poster.pptx` | Native text/shapes and embedded figures; **approximate layout**, not an automatic perfect LaTeX conversion |
| `poster_components.pptx` | Separate rasterized card images; cards movable/resizable, **text is not editable** |
| `poster.svg` | Vector-oriented PDF export; text may be outlines/paths and image content may remain raster |
| `POSTER_CONTENT_PLAN.md`, `POSTER_VISUAL_REVIEW.md`, `poster-review-NNNN.md` | Actual content, visual and independent-review evidence |
| `POSTER_SPEECH.md`, `POSTER_REPORT.md`, `POSTER_STATE.json` | Source-faithful presentation notes, provenance/export report and terminal readiness |
| `exports/` | Actual runnable project-specific export scripts, dependencies/commands, execution records, measured geometry and export-render inspection evidence |

Generate **real runnable scripts when performing the stage**, using the actual layout/assets; no placeholder helpers, fake success messages, omitted-card examples or dummy images. Record interpreter/library versions, input hashes, commands/exit codes and output hashes. A missing asset must fail clearly, not become a fabricated “[Image]” box. Never create empty outputs to satisfy a checklist.

### Native-text PPTX

Rebuild a single slide with positioned native text boxes/shapes, tables where supported, and actual image assets using the measured layout. Convert unsupported figure formats to suitable PNG or supported image formats with preserved aspect ratios; a common PPTX writer does not embed a PDF figure directly. Keep text native wherever supported; record equations or unusual symbols that require vector/raster assets rather than claiming all glyphs are editable text.

Use one canonical finalized content/layout representation shared with the reviewed TeX, or extract and verify the actual final source content explicitly. Do not parse arbitrary TeX with a superficial regular expression and assume correctness, or maintain an unverified divergent hardcoded transcript. Compare all native PPTX text/numbers/captions with the exact reviewed poster and its evidence map. Match physical slide size, fonts, relative placement and readable point sizes; LaTeX macros, shadows and equation typography may differ. **Render and inspect the actual saved PPTX**, not merely the PDF it imitates.

### Component-image PPTX

Render each real card/title/other visual region of the final PDF at an appropriate effective resolution (often 300 DPI), then add each as a separate picture shape at its measured position. Obtain actual page coordinates including margins, padding, shadows and non-card elements; do not assume `page_height / rows` exactly describes the grid. Record region IDs, page-coordinate rectangles, raster DPI and PDF hash. With PDF points converted to millimetres, use `mm = points × 25.4 / 72`; derive slide dimensions from the actual PDF, accounting for rotation/crop.

Verify regions cover all intended content exactly once except deliberate documented overlaps. Do not lose the background, footer, logo, arrows or card shadows; avoid seams, overlaps, double-rendered text and clipped glyphs. Each image card must be independently selectable. This export is not native editable text, and rasterization is not a promise of pixel perfection. Render the actual PPTX and compare it with the final PDF.

### SVG

Use an available real PDF-to-SVG converter, record options/version and export the one final page. For example, an available PyMuPDF library can use the page SVG export with text-as-paths chosen explicitly. Inspect the actual SVG viewport/viewBox, physical dimensions, fonts or outlined glyphs, image references and output encoding. Resolve external resources or embed them for portability; never claim universal editability or conversion reliability. Render the **saved SVG** in an available SVG renderer and compare its complete content, small labels and geometry to the final PDF.

### Export acceptance table — all rows required for requested formats

Record each actual check in `POSTER_REPORT.md` and state; success at conversion is not export verification:

- **All files:** exist, are nonempty, reopen with the relevant parser/viewer, have correct type and actual SHA-256; bind to the exact final reviewed source/PDF/content. Inventory all source dependencies and export scripts. No stale outputs from previous builds.
- **Source:** entry/includes/assets resolve from the packaged source layout; record successful actual poster build from those exact inputs without rewriting source content. Do not assert portable reproduction without checking dependencies and paths.
- **PDF/preview:** one page, correct physical size/orientation, successful build and metadata/font/image checks; preview was rendered from that exact final PDF and actually viewed.
- **Native PPTX:** one slide, intended dimensions, real native text elements, expected text/value/figure inventory, embedded supported assets, no out-of-slide shapes or broken relations; render and visually inspect the actual file for substitutions, clipping and content differences.
- **Component PPTX:** one slide, measured dimensions, expected separately movable image cards with correct bounds/coverage/resolution, no omissions; render and visually inspect the actual file against PDF.
- **SVG:** parses, correct viewport/dimensions, portable assets, recorded text/path semantics; render and visually inspect the actual SVG against PDF.
- **Every export rendering:** record output and inspected render hashes, actual inspection capability, content/geometry observations, fixes and verdict. Structural checks do not substitute for visual checks. If no presentation/SVG renderer or no image capability is available, that format remains unverified and requested completion is blocked.

Any later content/layout/asset change requires rebuilding and regenerating affected exports, then repeating the affected checks/reviews. Do not quietly remove a requested format to declare completion. A narrower suite needs explicit user scope change; optional unrequested formats are clearly marked not requested, not passed. Preserve existing good artifacts while reporting exact blockers.

## 8. Speech, report and terminal state

Write `POSTER_SPEECH.md` with a 60-second overview, a 2–3-minute walkthrough and likely questions/answers: problem, method/hero figure, exact headline evidence, limitations and takeaway. Link numerical statements to source IDs in notes; distinguish demonstrated results from speculation. Do not add new claims in spoken answers or invent future experiments as completed work. Refer to a paper/code link only if it really exists and is authorized.

`POSTER_REPORT.md` records resolved inputs/roots, entry evidence, data trace, approved content/layout, actual build/dependency details, all export methods/limitations, visual and independent findings/fixes, source permissions, checks actually executed, and blockers. Do not call a PDF printer-certified merely because it renders; note any venue/printer-specific bleed/color/profile requirements not verified. No printing or publication action follows this report.

Persist `POSTER_STATE.json` (`schema_version: 1`) with actual values, not aspirational checkboxes:

- `status`: `blocked`, `awaiting_confirmation`, `awaiting_review`, or `ready`; current `phase` and precise `blockers`.
- `project_root`, `docs_root`, actual `output_dir`, and exact input paths/digests: manuscript manifest, writing state, planning bundle/state/plan/results, paper TeX and PDF. Inventory consumed source files as `{role,path,sha256}` and preserve original code/result provenance, not retroactively current-code hashes.
- `authorization`: actual direct invocation reference or consumed handoff reference/status; content/layout approval references and exact content/layout hashes, or explicit scoped checkpoint waivers.
- `settings`: actual venue/size/orientation/dimensions/fonts; `requested_exports` with explicit user-approved scope.
- `build`: actual command/cwd/engine/version/exit code/log path/hash, input inventory and final PDF hash; real compilation status `succeeded`, `failed` or `unavailable`.
- `visual_review` and `independent_review`: actual report paths/hashes, reviewed artifact/render hashes, findings, resolution and `passed`, `pending`, `failed` or `unavailable` status.
- `exports`: each requested format's path/hash, source/PDF/content binding, structural checks, actual rendered preview paths/hashes, visual verdict, limitations and `verified`, `failed`, `unavailable` or `pending` status.
- `outputs`: actual `{role,path,sha256}` inventory including content plan, source/assets, build/export scripts/logs, speech, report and reviews. Do **not** include this mutable state file in its own hash inventory, create self hashes, or let reports and state hash each other cyclically.
- `terminal: true`, `next_skill: null`, and unresolved limitations even when ready.

Freeze final report/output bytes before binding them in state. `ready` means unchanged verified entry evidence, required content/layout approvals, actual successful current build, actual final visual review, completed independent review with mandatory issues resolved, speech/report/source package, and **every requested export really generated, reopened, structurally checked and visually inspected**. A pending review or missing export cannot be masked by a high aesthetic score. Mark an incoming handoff `completed` only when these actual authorized deliverables finish; otherwise accurately retain a waiting state or mark failure with blockers.

Final response: exact produced paths, actual requested-format verification results, editability limits, review evidence and remaining limitations/blockers. This ends the workflow; no publication handoff or automatic external action.

## Version and changes

### 3.1.0

- Requires actual human acceptance of the exact final manuscript, independently of stage-entry assent or a successful build; connects existing content/layout gates to the shared anchor-first contract.

### 3.0.0

- Replaced framework/service-specific orchestration with host-neutral capabilities and explicit one-stage authorization.
- Moved default sources/outputs to the shared docs stage directories; retained explicit bound paths and optional bundled templates/logos.
- Bound poster entry to genuine final manuscript build/review, planning approval/bundle and exact completed result data; prohibited stale/latest substitution and new experimental claims.
- Preserved practical A0/A1 typography, card-grid, clipping, figure, compilation and export guidance while removing automatic installation, backup recipes and unsupported platform/editability claims.
- Added actual visual plus independent review, per-format export verification, provenance/report/state readiness and an explicit terminal-stage boundary.
