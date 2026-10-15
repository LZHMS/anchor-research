# LaTeX Templates for ML/AI Conferences

This directory contains bundled LaTeX resources for several ML/AI venues. Inspect the actual venue/year/track instructions before selecting one; a historical template or page-limit table is not evidence of current compliance. Explicit supplied current templates take precedence.

---

## Host-neutral compilation

No editor, online service, package manager or agent framework is required. Use an available compiler appropriate to the selected template in the manuscript output workspace (default `DOCS_ROOT/research-paper-writing`), not inside this installed template directory. Inspect template instructions, licenses and build scripts before use; copy only required resources and preserve user assets.

Examples, only when the actual installed engine and template support them:

```sh
latexmk -pdf main.tex
```

Or, for a template requiring the traditional bibliography sequence:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Other templates may require a different engine or bibliography processor. Do not assume availability, enable shell escape, install packages automatically, change global environments or upload sources to obtain a build. Missing tools/packages are explicit blockers; ask for authorized environment provisioning separately.

Record the real command, cwd, engine/version, actual input hashes, exit code, complete log and final PDF digest in the manuscript build manifest. Check citations, cross-references, assets, page constraints and rendered output; command success alone is insufficient. Any input change invalidates the previous build correspondence. Failed/unavailable compilation cannot produce ready state or a poster offer. See the parent skill for the complete manifest/state and independent-review contracts.

---

## Available Templates

| Conference | Directory | Year | Source |
|------------|-----------|------|--------|
| ICML | `icml2026/` | 2026 | [Official ICML](https://icml.cc/Conferences/2026/AuthorInstructions) |
| ICLR | `iclr2026/` | 2026 | [Official GitHub](https://github.com/ICLR/Master-Template) |
| NeurIPS | `neurips2025/` | 2025 | Community template |
| ACL | `acl/` | 2025+ | [Official ACL](https://github.com/acl-org/acl-style-files) |
| AAAI | `aaai2026/` | 2026 | [AAAI Author Kit](https://aaai.org/authorkit26/) |
| COLM | `colm2025/` | 2025 | [Official COLM](https://github.com/COLM-org/Template) |

## Usage

### ICML 2026

```latex
\documentclass{article}
\usepackage{icml2026}  % For submission
% \usepackage[accepted]{icml2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `icml2026.sty` - Style file
- `icml2026.bst` - Bibliography style
- `example_paper.tex` - Example document

### ICLR 2026

```latex
\documentclass{article}
\usepackage[submission]{iclr2026_conference}  % For submission
% \usepackage[final]{iclr2026_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `iclr2026_conference.sty` - Style file
- `iclr2026_conference.bst` - Bibliography style
- `iclr2026_conference.tex` - Example document

### ACL Venues (ACL, EMNLP, NAACL)

```latex
\documentclass[11pt]{article}
\usepackage[review]{acl}  % For review
% \usepackage{acl}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `acl.sty` - Style file
- `acl_natbib.bst` - Bibliography style
- `acl_latex.tex` - Example document

### AAAI 2026

```latex
\documentclass[letterpaper]{article}
\usepackage[submission]{aaai2026}  % For submission
% \usepackage{aaai2026}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `aaai2026.sty` - Style file
- `aaai2026.bst` - Bibliography style

### COLM 2025

```latex
\documentclass{article}
\usepackage[submission]{colm2025_conference}  % For submission
% \usepackage[final]{colm2025_conference}  % For camera-ready

\begin{document}
% Your paper content
\end{document}
```

Key files:
- `colm2025_conference.sty` - Style file
- `colm2025_conference.bst` - Bibliography style

## Historical Page Limits Summary — Verify Current Requirements

| Conference | Submission | Camera-Ready | Notes |
|------------|-----------|--------------|-------|
| ICML 2026 | 8 pages | 9 pages | +unlimited refs/appendix |
| ICLR 2026 | 9 pages | 10 pages | +unlimited refs/appendix |
| NeurIPS 2025 | 9 pages | 9 pages | +checklist outside limit |
| ACL 2025 | 8 pages (long) | varies | +unlimited refs/appendix |
| AAAI 2026 | 7 pages | 8 pages | +unlimited refs/appendix |
| COLM 2025 | 9 pages | 10 pages | +unlimited refs/appendix |

## Common Issues

### Compilation Errors

1. **Missing packages/fonts**: Record the exact unavailable dependency and stop the affected build; do not automatically install or change the global environment.
2. **Bibliography errors**: Inspect the actual template's required processor/style and supplied bibliography resources.
3. **Font warnings**: Determine whether the output substituted fonts and whether it meets the actual template requirements; do not claim a checked final PDF without inspection.

### Anonymization

For submission, ensure:
- No author names in `\author{}`
- No acknowledgments section
- No grant numbers
- Use anonymous repositories
- Cite own work in third person

### Common LaTeX Packages

```latex
% Recommended packages (check compatibility with venue style)
\usepackage{amsmath,amsthm,amssymb}  % Math
\usepackage{graphicx}                 % Figures
\usepackage{booktabs}                 % Tables
\usepackage{hyperref}                 % Links
\usepackage{algorithm,algorithmic}    % Algorithms
\usepackage{natbib}                   % Citations
```

## Updating Templates

Templates are updated annually. Check official sources before each submission:

- ICML: https://icml.cc/
- ICLR: https://iclr.cc/
- NeurIPS: https://neurips.cc/
- ACL: https://github.com/acl-org/acl-style-files
- AAAI: https://aaai.org/
- COLM: https://colmweb.org/
