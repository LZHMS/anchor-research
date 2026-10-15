#!/usr/bin/env python3
"""Prepare grounded host-agent tasks and validate/aggregate their completed analyses.

This helper does not generate analysis or call a language model. Source retrieval uses
only the bundled research-daily-ideas downloader and obeys the review's source policy.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote


PAPER_SECTIONS = (
    "一句话总结", "研究背景", "研究问题", "研究动机", "方法机制", "主要贡献",
    "实验与结果", "局限性", "可迁移思路", "task_figure", "methodology", "证据与关联",
)
OVERVIEW_SECTIONS = (
    "检索分支", "领域定义与子方向", "核心科学问题", "数据集", "方法谱系",
    "评价指标", "开放研究缺口", "证据与覆盖局限",
)
EVIDENCE_LEVELS = ("full-text", "pkbase-note", "abstract-only", "metadata-only")
METADATA_LABELS = (
    ("作者",), ("年份", "年"), ("发表场所", "会议/期刊", "会议", "期刊", "出版场所"),
    ("领域",), ("标签",), ("质量评分", "质量分数"), ("证据等级", "证据级别"),
)
UNKNOWN = "未知"


class SummaryError(ValueError):
    """An actionable input, evidence, or result contract error."""


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SummaryError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SummaryError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review_digest(review: dict) -> str:
    payload = json.dumps(review, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def papers_with_ids(review: dict) -> list[tuple[str, dict]]:
    papers = review.get("papers", [])
    if not isinstance(papers, list):
        raise SummaryError("Input 'papers' must be a list.")
    found = set()
    result = []
    for index, paper in enumerate(papers):
        if not isinstance(paper, dict):
            raise SummaryError(f"Paper at index {index} must be an object.")
        pid = paper.get("id")
        if isinstance(pid, bool) or not isinstance(pid, (str, int)) or not str(pid).strip():
            raise SummaryError(f"Paper at index {index} requires a nonempty stable 'id'.")
        pid = str(pid)
        if pid in found:
            raise SummaryError(f"Duplicate paper ID: {pid!r}")
        found.add(pid)
        result.append((pid, paper))
    return result


def safe_stem(paper_id: str) -> str:
    readable = re.sub(r"[^A-Za-z0-9_-]+", "-", paper_id).strip("-_")[:64] or "unnamed"
    digest = hashlib.sha256(paper_id.encode("utf-8")).hexdigest()[:12]
    # The fixed prefix also prevents Windows device filenames, even for IDs like CON.
    return f"paper-{readable}-{digest}"


def task_paths(paper_id: str, out: Path) -> dict:
    stem = safe_stem(paper_id)
    return {
        "paper_id": paper_id,
        "context_path": str(out / "contexts" / f"{stem}.json"),
        "analysis_path": str(out / "papers" / f"{stem}.md"),
        "result_path": str(out / "papers" / f"{stem}.analysis.json"),
    }


def source_allowed(review: dict, name: str) -> bool:
    enabled = review.get("enabled_sources")
    if enabled is not None:
        if not isinstance(enabled, list):
            raise SummaryError("'enabled_sources' must be a list when present.")
        if name not in enabled:
            return False
    statuses = review.get("source_status", {})
    if not isinstance(statuses, dict):
        raise SummaryError("'source_status' must be an object when present.")
    status = statuses.get(name)
    if isinstance(status, dict):
        status = status.get("status")
    return status not in ("disabled", "unavailable")


def expanded_path(value: str, relative_to: Path) -> Path:
    path = Path(os.path.expandvars(value)).expanduser()
    return (path if path.is_absolute() else relative_to / path).resolve()


def accessible_directory(path: Path) -> bool:
    try:
        if not path.is_dir() or not os.access(path, os.R_OK | os.X_OK):
            return False
        # Actually open a directory iterator; os.access alone is insufficient on Windows.
        with os.scandir(path):
            pass
        return True
    except OSError:
        return False


def resolve_pkbase(explicit: str | None, allowed: bool, input_dir: Path) -> tuple[Path | None, list[str]]:
    warnings = []
    if explicit is not None:
        base = expanded_path(explicit, input_dir)
        if not accessible_directory(base):
            raise SummaryError(f"Explicit --pkbase is not an accessible directory: {base}")
        return base, warnings
    if not allowed:
        return None, warnings
    env_value = os.environ.get("PKBASE_PATH", "").strip()
    if env_value:
        base = expanded_path(env_value, input_dir)
        if accessible_directory(base):
            return base, warnings
        warnings.append(f"PKBASE_PATH is not an accessible directory: {base}")
    base = Path.home() / "PKBase"
    if accessible_directory(base):
        return base.resolve(), warnings
    warnings.append("No accessible PKBase directory resolved from PKBASE_PATH or ~/PKBase; no base was created.")
    return None, warnings


def provenance_base(paper: dict, fallback: Path | None, allowed: bool,
                    input_dir: Path, warnings: list[str]) -> Path | None:
    if not allowed:
        return None
    metadata = paper.get("source_metadata")
    pkmeta = metadata.get("pkbase", {}) if isinstance(metadata, dict) else {}
    value = pkmeta.get("base_path") if isinstance(pkmeta, dict) else None
    if isinstance(value, str) and value.strip():
        base = expanded_path(value, input_dir)
        if accessible_directory(base):
            return base
        warnings.append(f"Retained PKBase provenance directory is inaccessible: {base}")
        # Do not reinterpret a provenance-relative page in an unrelated fallback vault.
        return None
    return fallback


def resolve_local_file(value: object, input_dir: Path, project_root: Path,
                       base: Path | None, kind: str, warnings: list[str]) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = Path(os.path.expandvars(value)).expanduser()
    if raw.is_absolute():
        candidates = [raw]
    elif kind == "pkbase_page":
        candidates = [base / raw] if base else []
    elif value.replace("\\", "/").startswith("raw/"):
        candidates = ([base / raw] if base else []) + [input_dir / raw, project_root / raw]
    else:
        candidates = [input_dir / raw, project_root / raw] + ([base / raw] if base else [])
    for candidate in candidates:
        try:
            if candidate.is_file() and os.access(candidate, os.R_OK):
                return candidate.resolve()
        except OSError:
            continue
    warnings.append(f"Retained {kind} could not be resolved to an accessible file: {value}")
    return None


def retained_pdf_is_pkbase(paper: dict, value: object, input_dir: Path) -> bool:
    """Classify retained provenance lexically, without probing a disabled base."""
    if str(value).replace("\\", "/").startswith("raw/"):
        return True
    sources = paper.get("source", [])
    if isinstance(sources, str):
        sources = [sources]
    if isinstance(sources, list) and sources and all(source == "pkbase" for source in sources):
        return True
    metadata = paper.get("source_metadata")
    pkmeta = metadata.get("pkbase", {}) if isinstance(metadata, dict) else {}
    base_value = pkmeta.get("base_path") if isinstance(pkmeta, dict) else None
    if not isinstance(value, str) or not isinstance(base_value, str) or not base_value.strip():
        return False
    def lexical_path(raw: str) -> str:
        path = Path(os.path.expandvars(raw)).expanduser()
        if not path.is_absolute():
            path = input_dir / path
        return os.path.normcase(os.path.abspath(path))
    try:
        base_path, pdf_path = lexical_path(base_value), lexical_path(value)
        return os.path.commonpath((base_path, pdf_path)) == base_path
    except (OSError, ValueError):
        return False


def useful_text(text: str) -> bool:
    return bool(text.strip()) and any(character.isalnum() for character in text)


def pdf_text(path: Path, max_chars: int, warnings: list[str]) -> str:
    """Extract actual PDF pages, preserving page citations and detecting truncation."""
    available = False
    try:
        from pypdf import PdfReader
        available = True
        reader = PdfReader(str(path))
        parts, length = [], 0
        for number, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                part = f"[PDF page {number}]\n{text}"
                parts.append(part)
                length += len(part) + 2
            if length > max_chars:
                break
        text = "\n\n".join(parts)
        if useful_text(text):
            return text[:max_chars + 1]
        warnings.append(f"pypdf extracted no useful text from {path}; attempting PyMuPDF.")
    except ImportError:
        warnings.append("pypdf is unavailable; attempting PyMuPDF for PDF extraction.")
    except Exception as exc:
        warnings.append(f"pypdf extraction failed for {path}: {exc}; attempting PyMuPDF.")
    try:
        import fitz
        available = True
        parts, length = [], 0
        with fitz.open(str(path)) as document:
            for number, page in enumerate(document, 1):
                text = page.get_text() or ""
                if text.strip():
                    part = f"[PDF page {number}]\n{text}"
                    parts.append(part)
                    length += len(part) + 2
                if length > max_chars:
                    break
        text = "\n\n".join(parts)
        if useful_text(text):
            return text[:max_chars + 1]
        warnings.append(f"PyMuPDF extracted no useful text from {path}; scanned content may require OCR.")
    except ImportError:
        warnings.append("PyMuPDF is unavailable for PDF extraction.")
    except Exception as exc:
        warnings.append(f"PyMuPDF extraction failed for {path}: {exc}")
    if not available:
        warnings.append("Install pypdf or PyMuPDF to ground analysis in local PDF text.")
    return ""


def load_downloader():
    path = Path(__file__).resolve().parent.parent / "research-daily-ideas" / "scripts" / "download_paper_sources.py"
    if not path.is_file():
        raise SummaryError(f"Bundled paper downloader is missing: {path}")
    spec = importlib.util.spec_from_file_location("literature_summary_paper_sources", path)
    if spec is None or spec.loader is None:
        raise SummaryError(f"Cannot load bundled downloader: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def downloader_paper(paper: dict, warnings: list[str]) -> dict:
    normalized = dict(paper)
    aid = paper.get("arxiv_id")
    if aid:
        aid = str(aid).strip()
        aid = re.sub(r"^arxiv:\s*", "", aid, flags=re.IGNORECASE)
        aid = re.sub(r"^https?://(?:www\.)?arxiv\.org/(?:abs|pdf|html)/", "", aid)
        aid = re.sub(r"\.pdf$", "", aid)
        if re.fullmatch(r"(?:\d{4}\.\d{4,5}|[a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?", aid):
            normalized["url"] = f"https://arxiv.org/abs/{aid}"
            if not normalized.get("pdf_url"):
                normalized["pdf_url"] = f"https://arxiv.org/pdf/{aid}"
        else:
            warnings.append(f"Unrecognized explicit arxiv_id: {paper.get('arxiv_id')!r}; using retained URLs only.")
    if not normalized.get("pdf_url") and str(normalized.get("url", "")).split("?", 1)[0].lower().endswith(".pdf"):
        normalized["pdf_url"] = normalized["url"]
    # The downloader accepts abstract text, not null; the original record is preserved separately.
    if not isinstance(normalized.get("abstract"), str):
        normalized["abstract"] = ""
    if not isinstance(normalized.get("title"), str):
        normalized["title"] = "Unknown"
    return normalized


def downloaded_evidence(paper: dict, cache_dir: Path, max_chars: int,
                        warnings: list[str]) -> tuple[str, str | None, str | None, list]:
    try:
        downloader = load_downloader()
        normalized = downloader_paper(paper, warnings)
        entry = downloader.process_paper(normalized, cache_dir, timeout=60, max_chars=max_chars + 1)
        paper_dir = Path(entry["paper_dir"]).resolve() if entry.get("paper_dir") else None
        # Normal entries omit paper_dir; derive the same cache location from downloader helpers.
        if paper_dir is None:
            downloaded_id = downloader._arxiv_id(normalized) or downloader._paper_slug(normalized)
            paper_dir = cache_dir / "papers" / downloaded_id
        status = entry.get("status", "unknown")
        if status not in ("ok", "skipped-existing"):
            warnings.append(f"Bundled downloader reported {status}.")
        figures = []
        figures_path = paper_dir / "figures.json"
        if figures_path.is_file():
            try:
                figures = json.loads(figures_path.read_text(encoding="utf-8-sig"))
                if not isinstance(figures, list):
                    raise ValueError("expected a figure list")
            except (OSError, UnicodeError, ValueError) as exc:
                warnings.append(f"Cannot read downloaded figure metadata: {exc}")
                figures = []
        for figure in figures:
            if not isinstance(figure, dict):
                warnings.append("Downloader returned a malformed figure entry; retained without interpretation.")
                continue
            for key in ("local_path", "embeddable_path"):
                if figure.get(key):
                    figure_path = Path(figure[key])
                    if not figure_path.is_file():
                        warnings.append(f"Figure {key} is missing: {figure_path}")
                    else:
                        figure[key] = str(figure_path.resolve())
            if figure.get("note"):
                warnings.append(f"Figure availability: {figure['note']}")
        source_dir = paper_dir / "source"
        if source_dir.is_dir():
            tex_files = downloader._find_main_tex(source_dir)
            if tex_files:
                text = downloader._extract_latex_text(tex_files, source_dir, max_chars + 1)
                if useful_text(text):
                    return text, str(tex_files[0].resolve()), "latex", figures
                warnings.append("Downloaded LaTeX files yielded no useful text.")
        warnings.append("No usable downloaded LaTeX source; attempting the actual downloaded PDF, not text_dump.")
        pdf = paper_dir / "paper.pdf"
        if pdf.is_file():
            text = pdf_text(pdf, max_chars, warnings)
            if useful_text(text):
                return text, str(pdf.resolve()), "pdf", figures
        else:
            warnings.append("Bundled downloader did not provide an accessible PDF.")
        warnings.append("Download cache has no verified full text; text_dump may contain only the abstract and is not used as full-text evidence.")
        return "", None, None, figures
    except Exception as exc:
        warnings.append(f"Bundled source retrieval failed: {type(exc).__name__}: {exc}")
        return "", None, None, []


def prepare(review: dict, input_path: Path, out: Path, project_root: Path,
            pkbase: str | None, max_chars: int) -> dict:
    indexed = papers_with_ids(review)
    web_allowed = source_allowed(review, "web")
    pk_allowed = pkbase is not None or source_allowed(review, "pkbase")
    base, base_warnings = resolve_pkbase(pkbase, pk_allowed, project_root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "contexts").mkdir(exist_ok=True)
    (out / "papers").mkdir(exist_ok=True)
    tasks = []
    for pid, paper in indexed:
        warnings = list(base_warnings)
        paper_base = provenance_base(paper, base, pk_allowed, input_path.parent, warnings)
        page_path, page_text = None, ""
        if paper.get("pkbase_page"):
            if pk_allowed:
                page = resolve_local_file(paper["pkbase_page"], input_path.parent, project_root,
                                          paper_base, "pkbase_page", warnings)
                if page is not None:
                    try:
                        page_text = page.read_text(encoding="utf-8-sig")
                        page_path = str(page)
                        if not useful_text(page_text):
                            warnings.append(f"Retained PKBase source page is empty: {page}")
                    except (OSError, UnicodeError) as exc:
                        warnings.append(f"Cannot read retained PKBase source page {page}: {exc}")
            else:
                warnings.append("PKBase source reading is disabled; retained pkbase_page was not probed.")
        text, source_path, source_kind = "", None, None
        retained_figures = paper.get("figures")
        figures = list(retained_figures) if isinstance(retained_figures, list) else []
        if figures:
            warnings.append("Retained figure metadata is preserved from the input; availability/captions must be verified before embedding or attributing author claims.")
        pdf_value = paper.get("pdf_path")
        if pdf_value:
            is_pk_pdf = retained_pdf_is_pkbase(paper, pdf_value, input_path.parent)
            if is_pk_pdf and not pk_allowed:
                warnings.append("PKBase source reading is disabled; retained PKBase pdf_path was not probed.")
            else:
                pdf = resolve_local_file(pdf_value, input_path.parent, project_root,
                                         paper_base, "pdf_path", warnings)
                if pdf is not None:
                    text = pdf_text(pdf, max_chars, warnings)
                    if useful_text(text):
                        source_path, source_kind = str(pdf), "pdf"
        if not useful_text(text) and any(paper.get(key) for key in ("arxiv_id", "url", "pdf_url")):
            if web_allowed:
                text, source_path, source_kind, downloaded_figures = downloaded_evidence(
                    paper, out / "sources" / safe_stem(pid), max_chars, warnings)
                figures.extend(downloaded_figures)
            else:
                warnings.append("Web source retrieval is disabled or unavailable; no downloader/network request was made.")
        if useful_text(text):
            level = "full-text"
            if source_kind == "pdf":
                warnings.append("PDF evidence includes extractable text only; embedded figures, scanned pages, and formula layout may be unavailable.")
        elif useful_text(page_text):
            text, source_path, source_kind, level = page_text, page_path, "pkbase-note", "pkbase-note"
            warnings.append("No verified paper full text; the retained PKBase note is secondary grounding, not author full text.")
        elif isinstance(paper.get("abstract"), str) and useful_text(paper["abstract"]):
            text, source_kind, level = paper["abstract"], "abstract", "abstract-only"
            warnings.append("Only the abstract is available; methods, experiments, figures, and formulas beyond it are unverified.")
        else:
            text, source_kind, level = "", "metadata", "metadata-only"
            warnings.append("Evidence is insufficient: metadata/retained annotations only, with no usable full text, PKBase note, or abstract.")
        truncated = len(text) > max_chars
        if truncated:
            warnings.append(f"Source text was truncated to --max-chars={max_chars}; omitted content is unavailable to the paper agent.")
        task = task_paths(pid, out)
        task["evidence_level"] = level
        context = {
            "paper": paper,
            "review_topic": review.get("review_topic"),
            "derived_facets": review.get("derived_facets", []),
            "review_summary": review.get("review_summary", {}),
            "pkbase_page_path": page_path,
            "pkbase_page_text": page_text,
            "source_text": text[:max_chars],
            "source_path": source_path,
            "source_kind": source_kind,
            "evidence_level": level,
            "source_truncated": truncated,
            "figures": figures,
            "evidence_warnings": warnings,
            "enabled_sources": review.get("enabled_sources"),
            "source_status": review.get("source_status", {}),
        }
        task["context_sha256"] = review_digest(context)
        write_json(Path(task["context_path"]), context)
        tasks.append(task)
    overview_context = out / "overview_context.json"
    overview_path = out / "overview_summary.md"
    manifest = {
        "schema_version": 2,
        "input_path": str(input_path),
        "input_sha256": review_digest(review),
        "out_dir": str(out),
        "tasks": tasks,
        "overview_context_path": str(overview_context),
        "overview_path": str(overview_path),
        "overview_result_path": str(out / "overview_summary.analysis.json"),
    }
    write_json(overview_context, {"review": review, "tasks": tasks, "overview_path": str(overview_path)})
    write_json(out / "analysis_manifest.json", manifest)
    return manifest


def markdown_sections(path: Path, expected: tuple[str, ...]) -> tuple[str, str]:
    try:
        text = path.read_text(encoding="utf-8-sig").strip()
    except (OSError, UnicodeError) as exc:
        raise SummaryError(f"Required Markdown is missing/unreadable: {path}: {exc}") from exc
    if not text or text in ("{}", "[]", "null"):
        raise SummaryError(f"Required Markdown is empty or not an analysis: {path}")
    # Fenced code cannot satisfy headings or hide duplicate/missing report sections.
    outside_code = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s*(`{3,}|~{3,})", line)
        if match:
            delimiter = match.group(1)
            if fence is None:
                fence = delimiter[0]
            elif delimiter[0] == fence:
                fence = None
            outside_code.append("")
        else:
            outside_code.append(line if fence is None else "")
    visible = "\n".join(outside_code)
    headings = list(re.finditer(r"^##[ \t]+(.+?)[ \t]*$", visible, re.MULTILINE))
    names = tuple(match.group(1) for match in headings)
    if names != expected:
        raise SummaryError(f"Wrong/missing/duplicate Markdown sections in {path}: expected {list(expected)}, got {list(names)}")
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(visible)
        body = visible[match.end():end].strip()
        if not body or body in ("{}", "[]", "...", "…"):
            raise SummaryError(f"Empty analysis section '{match.group(1)}' in {path}")
    if not re.search(r"[\u3400-\u9fff]", visible):
        raise SummaryError(f"Expected Chinese narrative in {path}")
    return text, visible[:headings[0].start()]


def validate_paper_markdown(path: Path, paper: dict) -> str:
    text, header = markdown_sections(path, PAPER_SECTIONS)
    title = paper.get("title") or "未提供标题"
    if text.splitlines()[0] != f"# {title}":
        raise SummaryError(f"Analysis must start with original title '# {title}': {path}")
    for alternatives in METADATA_LABELS:
        if not any(re.search(rf"{re.escape(label)}(?:\*\*)?\s*[:：]", header) for label in alternatives):
            raise SummaryError(f"Missing Chinese metadata label {alternatives[0]!r} in {path}")
    return text


def validate_result(path: Path, pid: str, level: str) -> dict:
    result = read_json(path)
    if result.get("paper_id") != pid:
        raise SummaryError(f"Sidecar paper_id mismatch for {pid!r}: {path}")
    if result.get("evidence_level") != level:
        raise SummaryError(f"Sidecar evidence_level mismatch for {pid!r}: {path}")
    domain = result.get("domain")
    if not isinstance(domain, str) or not domain.strip():
        raise SummaryError(f"Sidecar domain must be a nonempty string: {path}")
    if "quality_score" not in result:
        raise SummaryError(f"Sidecar quality_score is required (number 0..10 or null): {path}")
    score = result["quality_score"]
    if score is not None and (isinstance(score, bool) or not isinstance(score, (int, float))
                              or not 0 <= score <= 10 or not math.isfinite(score)):
        raise SummaryError(f"Invalid quality_score (expected finite number 0..10 or null): {path}")
    return result


def table_text(value: object) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def markdown_link(label: str, path: Path, out: Path) -> str:
    portable = quote(path.relative_to(out).as_posix(), safe="/-_.")
    escaped = table_text(label).replace("[", "\\[").replace("]", "\\]")
    return f"[{escaped}]({portable})"


def count_values(papers: list[dict], field: str) -> Counter:
    counts = Counter({UNKNOWN: 0})
    for paper in papers:
        value = paper.get(field)
        values = value if isinstance(value, list) else [value]
        if not values:
            values = [None]
        for item in values:
            label = str(item).strip() if isinstance(item, (str, int, float)) and not isinstance(item, bool) else ""
            counts[label or UNKNOWN] += 1
    return counts


def count_table(title: str, counts: Counter) -> list[str]:
    lines = [f"## {title}", "", "| 分类 | 数量 |", "|---|---:|"]
    lines.extend(f"| {table_text(key)} | {counts[key]} |" for key in sorted(counts, key=str))
    return lines + [""]


def _validated_papers(review: dict, input_path: Path, out: Path) -> tuple[dict, list, list]:
    indexed = papers_with_ids(review)
    manifest = read_json(out / "analysis_manifest.json")
    if manifest.get("schema_version") != 2:
        raise SummaryError("Prepared manifest needs the current content-binding schema; run prepare again.")
    if manifest.get("input_path") != str(input_path) or manifest.get("out_dir") != str(out):
        raise SummaryError("Prepared manifest belongs to a different input/output location; run prepare for this input.")
    if manifest.get("input_sha256") != review_digest(review):
        raise SummaryError("Review input changed since prepare; prepare and review the affected analyses before finalize.")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != len(indexed):
        raise SummaryError("Manifest tasks do not cover every input paper exactly once.")
    completed = []
    for (pid, paper), task in zip(indexed, tasks):
        if not isinstance(task, dict):
            raise SummaryError("Every manifest task must be an object.")
        for key, expected in task_paths(pid, out).items():
            if task.get(key) != expected:
                raise SummaryError(f"Manifest {key} mismatch for paper {pid!r}; run prepare again.")
        level = task.get("evidence_level")
        if level not in EVIDENCE_LEVELS:
            raise SummaryError(f"Invalid manifest evidence level for {pid!r}: {level!r}")
        context = read_json(Path(task["context_path"]))
        if context.get("paper") != paper or context.get("evidence_level") != level:
            raise SummaryError(f"Prepared context differs from the input or manifest for {pid!r}.")
        if task.get("context_sha256") != review_digest(context):
            raise SummaryError(f"Prepared context content changed for {pid!r}; run prepare again.")
        validate_paper_markdown(Path(task["analysis_path"]), paper)
        result = validate_result(Path(task["result_path"]), pid, level)
        if result.get("context_sha256") != task["context_sha256"]:
            raise SummaryError(f"Paper analysis is stale for {pid!r}; re-analyze its current context before continuing.")
        completed.append((pid, paper, task, result))
    overview_path = out / "overview_summary.md"
    if (manifest.get("overview_path") != str(overview_path)
            or manifest.get("overview_context_path") != str(out / "overview_context.json")
            or manifest.get("overview_result_path") != str(out / "overview_summary.analysis.json")):
        raise SummaryError("Manifest overview paths do not match this output directory.")
    return manifest, indexed, completed


def _paper_snapshot(completed: list) -> list[dict]:
    return [
        {
            "paper_id": pid,
            "context_sha256": task["context_sha256"],
            "analysis_sha256": hashlib.sha256(Path(task["analysis_path"]).read_bytes()).hexdigest(),
            "result_sha256": review_digest(result),
        }
        for pid, _, task, result in completed
    ]


def _synthesize_input(review: dict, input_path: Path, out: Path) -> dict:
    manifest, _, completed = _validated_papers(review, input_path, out)
    snapshot = _paper_snapshot(completed)
    context = {
        "review": review,
        "input_sha256": review_digest(review),
        "tasks": manifest["tasks"],
        "paper_snapshots": snapshot,
        "papers_sha256": review_digest({"papers": snapshot}),
        "overview_path": manifest["overview_path"],
        "overview_result_path": manifest["overview_result_path"],
    }
    write_json(Path(manifest["overview_context_path"]), context)
    return context


def finalize(review: dict, input_path: Path, out: Path) -> dict:
    manifest, indexed, completed = _validated_papers(review, input_path, out)
    snapshot = _paper_snapshot(completed)
    papers_sha256 = review_digest({"papers": snapshot})
    overview_context = read_json(Path(manifest["overview_context_path"]))
    if (overview_context.get("review") != review
            or overview_context.get("tasks") != manifest["tasks"]
            or overview_context.get("input_sha256") != manifest["input_sha256"]
            or overview_context.get("paper_snapshots") != snapshot
            or overview_context.get("papers_sha256") != papers_sha256):
        raise SummaryError("Synthesis input is stale or unprepared; run --phase synthesize-input on the completed paper analyses.")
    overview_result = read_json(Path(manifest["overview_result_path"]))
    if (overview_result.get("input_sha256") != manifest["input_sha256"]
            or overview_result.get("papers_sha256") != papers_sha256):
        raise SummaryError("Overview analysis is stale; regenerate it from the current synthesis input.")
    overview_path = Path(manifest["overview_path"])
    markdown_sections(overview_path, OVERVIEW_SECTIONS)
    # No aggregate files are touched until every result and the synthesized overview pass.
    overview_link = markdown_link("研究领域综述", overview_path, out)
    index = ["# 全部论文分析索引", "", f"论文数：{len(completed)}。{overview_link}", "",
             "| 序号 | 论文 ID | 原始标题 | 领域 | 质量评分 | 证据等级 |", "|---:|---|---|---|---:|---|"]
    links = []
    for number, (pid, paper, task, result) in enumerate(completed, 1):
        title = str(paper.get("title") or "未提供标题")
        link = markdown_link(title, Path(task["analysis_path"]), out)
        score = result["quality_score"]
        quality = "未评分" if score is None else str(score)
        index.append(f"| {number} | {table_text(pid)} | {link} | {table_text(result['domain'])} | {quality} | {task['evidence_level']} |")
        links.append(f"{number}. {link}（ID：{table_text(pid)}；证据：{task['evidence_level']}）")
    if not completed:
        index += ["", "没有论文输入；没有生成或虚构单篇分析。"]
    papers = [paper for _, paper in indexed]
    domains = Counter({UNKNOWN: 0})
    evidence = Counter({level: 0 for level in EVIDENCE_LEVELS})
    evidence[UNKNOWN] = 0
    quality = Counter({"[0,4)": 0, "[4,7)": 0, "[7,10]": 0, "未评分": 0})
    for _, _, task, result in completed:
        domains[result["domain"].strip()] += 1
        evidence[task["evidence_level"]] += 1
        score = result["quality_score"]
        bucket = "未评分" if score is None else "[0,4)" if score < 4 else "[4,7)" if score < 7 else "[7,10]"
        quality[bucket] += 1
    report = ["# 文献分析统计报告", "", f"输入论文：{len(indexed)}；已验证分析：{len(completed)}。", "",
              f"{overview_link}；[全部论文索引](all_papers_analysis.md)。", "",
              "统计来源：角色、年份和发表场所来自原始输入；领域、质量评分来自已验证的分析 sidecar；证据等级来自准备清单。",
              "质量评分是基于证据的主观评价，不是引用量或影响力事实；未评分不计入数值分桶。多角色/多场所记录按每个原始分类计数。", ""]
    for title, counts in (
        ("论文角色", count_values(papers, "paper_role")),
        ("发表年份", count_values(papers, "year")),
        ("发表场所", count_values(papers, "venue")),
        ("领域", domains), ("质量分布", quality), ("证据覆盖", evidence),
    ):
        report.extend(count_table(title, counts))
    report += ["## 全部论文", ""] + (links or ["没有论文输入；无法推断研究趋势或质量分布。"])
    (out / "all_papers_analysis.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    (out / "aggregate_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"paper_count": len(completed), "index_path": str(out / "all_papers_analysis.md"),
            "report_path": str(out / "aggregate_report.md")}


def resolve_input(value: str | None, project_root: Path) -> Path:
    if value:
        path = expanded_path(value, project_root)
        if not path.is_file():
            raise SummaryError(f"Input is not an accessible file: {path}")
        return path
    path = project_root / "docs" / "research-literature-review" / "research_foundation_review.json"
    if not path.is_file():
        raise SummaryError(f"Canonical review JSON is missing: {path}; provide --input or update the literature review.")
    return path.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Review JSON; defaults to project docs/research-literature-review/research_foundation_review.json")
    parser.add_argument("--out", help="Output under project docs/research-literature-summary; defaults to that fixed skill directory")
    parser.add_argument("--phase", choices=("prepare", "synthesize-input", "finalize"), default="prepare",
                        help="Prepare paper contexts, bind completed papers for synthesis, or validate/aggregate completed results")
    parser.add_argument("--project-root", help="Current project root; defaults to the working directory, not the installed skill location")
    parser.add_argument("--pkbase", help="Explicit accessible PKBase directory (authorizes retained PKBase context reading)")
    parser.add_argument("--max-chars", type=int, default=100000, help="Maximum source-text characters per paper (default: 100000)")
    args = parser.parse_args()
    try:
        if args.max_chars < 1:
            raise SummaryError("--max-chars must be a positive integer.")
        project_root = (Path(args.project_root).expanduser().resolve() if args.project_root
                        else Path.cwd().resolve())
        input_path = resolve_input(args.input, project_root)
        output_root = project_root / "docs" / "research-literature-summary"
        out = expanded_path(args.out, project_root) if args.out else output_root
        if not out.is_relative_to(output_root):
            raise SummaryError(f"--out must be inside the current project's {output_root}: {out}")
        review = read_json(input_path)
        if args.phase == "prepare":
            manifest = prepare(review, input_path, out, project_root, args.pkbase, args.max_chars)
            print(f"Prepared {len(manifest['tasks'])} paper task(s): {out / 'analysis_manifest.json'}")
            print("Host: analyze each paper, run --phase synthesize-input, synthesize the overview and its sidecar, then finalize.")
        elif args.phase == "synthesize-input":
            context = _synthesize_input(review, input_path, out)
            print(f"Validated {len(context['tasks'])} paper output(s); synthesis input: {out / 'overview_context.json'}")
            print("Host: write overview_summary.md and overview_summary.analysis.json from this exact context, then finalize.")
        else:
            result = finalize(review, input_path, out)
            print(f"Validated and aggregated {result['paper_count']} paper analysis(es): {result['report_path']}")
        return 0
    except (SummaryError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
