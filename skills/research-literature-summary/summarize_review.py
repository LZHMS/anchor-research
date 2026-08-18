#!/usr/bin/env python3
"""
summarize_review.py - Automated analysis for literature reviews.
Generates an overall landscape summary and detailed per-paper analyses.
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import warnings
import tarfile
import re
import shutil

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import arxiv as arxiv_lib
    HAS_ARXIV = True
except ImportError:
    HAS_ARXIV = False

ARXIV_SOURCE_URL = "https://arxiv.org/e-print/{}"
HEADERS = {"User-Agent": "Mozilla/5.0 (research bot; paper-analyzer/1.0)"}

ANALYSIS_SYSTEM_EN = """\
You are an expert academic paper analyst who deeply understands AI/ML research.
Carefully read the provided paper information and return ONLY a structured Markdown report with EXACTLY these sections:

# Paper Title

**Authors:** ...
**Year:** ... | **Venue:** ...
**Domain:** ...
**Tags:** ...
**Quality Score:** .../10

## One-Line Summary
...

## Research Background
...

## Research Problem
...

## Motivation
...

## Main Contributions
- ...
- ...

## Limitations
- ...
- ...

## Transferability
- **Model Ideas:** ...
- **Research Directions:** ...
- **Visualization:** ...

Rules:
- Return ONLY the Markdown report, no extra text.
- All narrative fields MUST be completely in fluent English.
- tags must be concise English keywords.
"""

OVERALL_SUMMARY_SYSTEM = """You are an expert academic research architect.
Write a comprehensive Markdown report summarizing the overall research landscape based on the provided JSON data (`derived_facets`, `review_summary`, and paper metadata).
Use English. You MUST include the following structured sections:

# Research Landscape Summary

## Derived Facets
(Extract and summarize the derived facets from the input data)

## Field Definition & Related Subfields
(Define the field based on the review_summary. Identify related subfields and provide a brief introduction for each.)

## Core Scientific Questions
(What are the current core problems the field is focusing on?)

## Datasets
(List existing datasets mentioned in the data. For each, provide a brief introduction, identify whether it is likely open source, and highlight its core unique features compared to other datasets.)

## Methodology Lineages
(Identify existing method families/schools. For each, provide a brief introduction explaining *how* they work.)

## Evaluation Metrics 
(List existing evaluation metrics. For each, provide a brief introduction and its mathematical formula, if applicable/known.)

## Open Research Gaps
(Highlight the unresolved issues)
"""

PAPER_USER_TMPL = """\
Paper ID: {paper_id}
Full Source Text:
{source_section}

Title: {title}
Authors: {authors}
Year: {year}
Venue: {venue}

Abstract:
{abstract}

Problem (from review): {problem}
Method (from review): {method}
Results (from review): {results}
Relevance (from review): {relevance}
Summary (from review): {summary}

Perform deep analysis and return the structured Markdown report.
"""


# ────── Helper functions: arXiv parsing and downloading ──────

def _arxiv_id(paper: dict) -> str | None:
    url = paper.get("url", "") or paper.get("pdf_url", "")
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/([0-9]{4}\.[0-9]+)", url)
    return m.group(1) if m else None


def _download_source(aid: str, src_dir: Path, timeout: int = 60) -> bool:
    extract_dir = src_dir / aid
    tar_path    = src_dir / f"{aid}.tar.gz"

    if extract_dir.exists() and any(extract_dir.rglob("*.tex")):
        print(f"     [cache] Source already extracted: {aid}")
        return True

    src_dir.mkdir(parents=True, exist_ok=True)

    if not tar_path.exists() and HAS_REQUESTS:
        for attempt in range(3):
            try:
                print(f"     Downloading source (attempt {attempt+1}/3)...")
                resp = requests.get(ARXIV_SOURCE_URL.format(aid), headers=HEADERS, timeout=timeout, stream=True)
                resp.raise_for_status()
                tmp = tar_path.with_suffix(".tmp")
                with open(tmp, "wb") as f:
                    for chunk in resp.iter_content(65536):
                        f.write(chunk)
                tmp.rename(tar_path)
                print(f"     Downloaded: {tar_path.name} ({tar_path.stat().st_size // 1024} KB)")
                break
            except Exception as e:
                print(f"     [warn] requests attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    import time; time.sleep(5 * (attempt + 1))

    if not tar_path.exists() and HAS_ARXIV:
        try:
            print(f"     Trying arxiv library fallback...")
            client = arxiv_lib.Client()
            results = list(client.results(arxiv_lib.Search(id_list=[aid])))
            if results:
                results[0].download_source(dirpath=str(src_dir), filename=f"{aid}.tar.gz")
                print(f"     Downloaded via arxiv lib: {tar_path.stat().st_size // 1024} KB")
        except Exception as e:
            print(f"     [warn] arxiv library fallback failed: {e}")

    if not tar_path.exists():
        print(f"     [warn] Could not download source for {aid}")
        return False

    extract_dir.mkdir(parents=True, exist_ok=True)
    for mode in ("r:gz", "r:bz2", "r:*"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                with tarfile.open(tar_path, mode) as tar:
                    tar.extractall(extract_dir)
            img_count = len([f for f in extract_dir.rglob("*") if f.suffix.lower() in (".png", ".jpg", ".pdf", ".eps")])
            print(f"     Extracted -> {extract_dir.name}/  ({img_count} image files)")
            try:
                tar_path.unlink(missing_ok=True)
            except Exception:
                pass
            return True
        except Exception:
            continue

    print(f"     [warn] Extraction failed for {aid}")
    return False


def _find_main_tex(extract_dir: Path) -> list:
    tex_files = list(extract_dir.rglob("*.tex"))
    if not tex_files:
        return []
    tex_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return tex_files


def _extract_latex_text(tex_files: list, max_chars: int = 15000) -> str:
    collected = []
    total = 0
    for tex in tex_files:
        try:
            raw = tex.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        doc_start = raw.find(r"\begin{document}")
        if doc_start != -1:
            raw = raw[doc_start:]
        raw = re.sub(r"%[^\n]*", "", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        collected.append(raw)
        total += len(raw)
        if total >= max_chars:
            break
    combined = "\n\n".join(collected)
    return combined[:max_chars]


def _extract_figures(extract_dir: Path) -> list:
    figures = []
    fig_pattern = re.compile(r"\\begin\{figure\}(.*?)\\end\{figure\}", re.DOTALL)
    include_pattern = re.compile(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}")
    caption_pattern = re.compile(r"\\caption\{((?:[^{}]|\\{[^{}]*\\})*)\}")

    for tex_file in _find_main_tex(extract_dir):
        try:
            raw = tex_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for fig_match in fig_pattern.finditer(raw):
            fig_block = fig_match.group(1)
            inc_match = include_pattern.search(fig_block)
            cap_match = caption_pattern.search(fig_block)
            if inc_match:
                figures.append({
                    "filename": inc_match.group(1),
                    "caption": cap_match.group(1).strip() if cap_match else ""
                })
    return figures


def _copy_figures(figures: list, extract_dir: Path, out_dir: Path) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    updated = []
    for fig in figures:
        src_rel = fig["filename"]
        name = Path(src_rel).name
        candidates = [extract_dir / src_rel]
        for ext in ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"):
            candidates += list(extract_dir.rglob(name + ext))
        found = None
        for c in candidates:
            if c.is_file():
                found = c
                break
        if found:
            dest_name = re.sub(r"[/\\]", "_", src_rel)
            if not Path(dest_name).suffix and found.suffix:
                dest_name += found.suffix
            dest = out_dir / dest_name
            shutil.copy2(found, dest)
            updated.append({**fig, "local_path": str(dest)})
        else:
            updated.append({**fig, "local_path": None})
    return updated


# ────── LLM API ──────

def call_llm(system: str, user: str) -> str:
    """Calls LLM API (OpenAI-compatible with SSE streaming support, or Ollama)."""
    base_url = os.environ.get("LLM_BASE_URL", "http://localhost:11434").rstrip("/")
    api_key = os.environ.get("LLM_API_KEY", "")
    model = os.environ.get("LLM_MODEL", "qwen2.5:72b")
    timeout = int(os.environ.get("LLM_TIMEOUT", "300"))

    if "localhost:11434" in base_url or "api/chat" in base_url:
        # Ollama API
        url = f"{base_url}/api/chat" if "api/chat" not in base_url else base_url
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 32768}
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
    else:
        # OpenAI Compatible API (with streaming for llama.cpp servers)
        url = f"{base_url}/chat/completions" if "chat/completions" not in base_url else base_url
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "temperature": 0.1,
            "max_tokens": 16384,
            "stream": True
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")

            # Check if it's SSE stream or direct JSON
            if raw.startswith("data: "):
                # Parse SSE stream
                content_parts = []
                reasoning_parts = []
                for line in raw.split("\n"):
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                c = delta.get("content", "") or ""
                                r = delta.get("reasoning_content", "") or ""
                                if c:
                                    content_parts.append(c)
                                if r:
                                    reasoning_parts.append(r)
                        except json.JSONDecodeError:
                            continue
                content = "".join(content_parts)
                # For reasoning models like Qwen3.6, actual answer may be in reasoning_content
                # Extract the final JSON/output from reasoning if content is empty
                if not content.strip() and reasoning_parts:
                    reasoning_full = "".join(reasoning_parts)
                    # Try to find JSON in the reasoning output
                    json_match = re.search(r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', reasoning_full)
                    if json_match:
                        content = json_match.group(1)
                    else:
                        # Fallback: use last portion of reasoning as content
                        content = reasoning_full[-4000:]  # Last 4000 chars
            else:
                # Direct JSON response
                result = json.loads(raw)
                if "message" in result:  # Ollama
                    content = result["message"].get("content", "")
                elif "choices" in result:  # OpenAI non-streaming
                    content = result["choices"][0]["message"].get("content", "")
                else:
                    content = ""

            # Clean up markdown code blocks if the model outputs them around the JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return content.strip()
    except Exception as e:
        print(f"[LLM Error] {e}")
        return "{}"


# ────── Main workflow ──────

def main():
    parser = argparse.ArgumentParser(description="Analyze research foundation review output.")
    parser.add_argument("--input", required=True, help="Input research_foundation_review.json file")
    parser.add_argument("--obsidian-dir", required=True, help="Path to the Obsidian ResearchPapers directory")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"[Error] Input file {in_path} not found.")
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Determine topic for folder creation
    review_topic = data.get("review_topic", "Uncategorized").replace("/", "_").replace(" ", "_")
    out_dir = Path(args.obsidian_dir) / review_topic
    out_dir.mkdir(parents=True, exist_ok=True)

    papers_dir = out_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    papers = data.get("papers", [])

    # ── Stage 1: Overall landscape summary (skip if exists) ──
    summary_file = out_dir / "overview_summary.md"
    if summary_file.exists():
        print("[Stage 1] Overview summary already exists, skipping...")
    else:
        print("[Stage 1] Generating overall landscape summary...")
        review_summary = data.get("review_summary", {})
        derived_facets = data.get("derived_facets", [])

        user_msg = json.dumps({
            "derived_facets": derived_facets,
            "review_summary": review_summary,
            "paper_count": len(papers)
        }, indent=2)
        overall_summary = call_llm(OVERALL_SUMMARY_SYSTEM, user_msg)

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(overall_summary)
        print(f"  -> Generated {summary_file}")

    # ── Stage 2: Per-paper detailed analysis ──
    print("[Stage 2] Generating per-paper detailed analysis...")
    aggregated = []

    sources_dir = out_dir / "sources"
    figures_out_dir = out_dir / "figures"

    for i, paper in enumerate(papers):
        pid = paper.get("id", f"paper_{i}")
        pid_clean = str(pid).replace("/", "_")
        out_file = papers_dir / f"{pid_clean}.md"
        
        # Skip if already processed (resume from checkpoint)
        if out_file.exists():
            print(f"\n  -> Skipping [{i+1}/{len(papers)}]: {pid} (already processed)")
            aggregated.append({"paper_id": pid, "title": paper.get("title", ""), "tags": paper.get("topic_tags", [])})
            continue
        
        print(f"\n  -> Analyzing [{i+1}/{len(papers)}]: {pid}")

        # 1. Fetch Source (optional, adds LaTeX text to prompt)
        source_section = ""
        aid = _arxiv_id(paper)
        if aid:
            if _download_source(aid, sources_dir):
                extract_dir = sources_dir / aid
                tex_files = _find_main_tex(extract_dir)
                source_section = _extract_latex_text(tex_files)

                # Extract and copy figures locally
                extracted_figs = _extract_figures(extract_dir)
                if extracted_figs:
                    paper_fig_dir = figures_out_dir / pid_clean
                    _copy_figures(extracted_figs, extract_dir, paper_fig_dir)

        user_prompt = PAPER_USER_TMPL.format(
            paper_id=pid,
            source_section=source_section if source_section else "[No LaTeX source available for full-text analysis]",
            title=paper.get("title", ""),
            authors=", ".join(paper.get("authors", [])),
            year=paper.get("year", ""),
            venue=paper.get("venue", ""),
            abstract=paper.get("abstract", ""),
            problem=paper.get("problem", ""),
            method=paper.get("method", ""),
            results=paper.get("results", ""),
            relevance=paper.get("relevance", ""),
            summary=paper.get("summary", "")
        )

        result_md = call_llm(ANALYSIS_SYSTEM_EN, user_prompt)

        with open(out_file, "w", encoding="utf-8") as f:
            f.write(result_md)

        aggregated.append({"paper_id": pid, "title": paper.get("title", ""), "tags": paper.get("topic_tags", [])})

    # ── Stage 3: Aggregate Markdown Index ──
    agg_file = out_dir / "all_papers_analysis.md"
    with open(agg_file, "w", encoding="utf-8") as f:
        f.write("# All Papers Analysis Index\n\n")
        f.write("| Rank | Paper ID | Title | Tags |\n")
        f.write("|---|---|---|---|\n")
        for i, entry in enumerate(aggregated):
            pid = entry.get("paper_id", f"paper_{i}")
            pid_clean = str(pid).replace("/", "_")
            title = entry.get("title", "")
            tags = ", ".join(entry.get("tags", []))
            f.write(f"| {i+1} | [{pid}](papers/{pid_clean}.md) | {title} | {tags} |\n")
    print(f"  -> Aggregated index saved to {agg_file}")

    # ── Stage 4: Aggregate Report (Simplified for Markdown) ──
    print("[Stage 4] Generating aggregate report...")
    report_lines = ["# Aggregate Report\n"]
    report_lines.append(f"**Total papers analyzed:** {len(aggregated)}\n")
    
    report_lines.append("\n## Paper Index\n")
    for i, entry in enumerate(aggregated):
        pid = entry.get("paper_id", f"paper_{i}")
        pid_clean = str(pid).replace("/", "_")
        title = entry.get("title", "")
        report_lines.append(f"{i+1}. [{title}](papers/{pid_clean}.md)")

    report_file = out_dir / "aggregate_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"  -> Generated {report_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
