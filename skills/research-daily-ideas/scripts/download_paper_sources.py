#!/usr/bin/env python3
"""
download_paper_sources.py — Download arXiv source packages for ranked papers.

For every paper in ranked_papers.json:
  1. Resolve the arXiv ID from the paper URL (new-style 2401.12345 and
     legacy cs/0303034 formats). Non-arXiv papers fall back to a plain
     PDF download when pdf_url is available.
  2. Download the full source package (tar.gz) and the PDF from arXiv.
  3. Extract the source into  papers/{paper_id}/source/
     and the PDF into       papers/{paper_id}/paper.pdf
  4. Produce a readable text dump (main .tex content, preamble stripped)
     at papers/{paper_id}/text_dump.txt for downstream analysis.
  5. Extract figure references (includegraphics + caption) from the LaTeX,
     copy the figure files into papers/{paper_id}/figures/, and convert
     vector formats (PDF/EPS) to PNG so they can be embedded in Obsidian
     markdown and PKBase wiki pages.
  6. Write a per-paper manifest papers/{paper_id}/figures.json and a
     global download_manifest.json.

Resume-safe: a paper whose figures.json already exists is skipped.

Usage:
    python scripts/download_paper_sources.py \
        --ranked  research-daily-ideas/artifacts/ranked_papers.json \
        --date    2026-08-24 \
        --artifacts research-daily-ideas/artifacts

Dependencies: requests (download), PyMuPDF (PDF->PNG), pypdf (PDF text
extraction for non-arXiv PDFs). All three are optional — the script
degrades gracefully when they are missing.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import warnings
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False

ARXIV_SOURCE_URL = "https://arxiv.org/e-print/{}"
ARXIV_PDF_URL = "https://arxiv.org/pdf/{}"
HEADERS = {"User-Agent": "Mozilla/5.0 (research bot; research-daily-ideas/1.0)"}

IMG_EXTS = (".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _arxiv_id(paper: dict) -> str | None:
    """Extract the arXiv ID (without version) from url/pdf_url, if any."""
    url = paper.get("url", "") or paper.get("pdf_url", "")
    m = re.search(r"arxiv\.org/(?:abs|pdf|html)/([0-9]{4}\.[0-9]+)", url)
    if m:
        return m.group(1)
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([a-z-]+/\d{7})", url)
    if m:
        return m.group(1)
    return None


def _paper_slug(paper: dict) -> str:
    """Fallback folder name for non-arXiv papers."""
    title = re.sub(r"[^a-z0-9]+", "-", (paper.get("title", "") or "").lower()).strip("-")
    return (title or "untitled")[:40]


def _http_download(url: str, dest: Path, timeout: int, retries: int = 3) -> bool:
    """Download url to dest with retries. Returns True on success."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    for attempt in range(retries):
        try:
            if HAS_REQUESTS:
                resp = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
                resp.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in resp.iter_content(65536):
                        f.write(chunk)
            else:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    with open(tmp, "wb") as f:
                        shutil.copyfileobj(r, f)
            tmp.rename(dest)
            return True
        except Exception as e:
            print(f"     [warn] download attempt {attempt + 1}/{retries} failed: {e}")
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
    return False


def _extract_source(tar_path: Path, extract_dir: Path) -> bool:
    """Extract an arXiv source package. Handles tar.gz/tar.bz2/zip/plain files."""
    extract_dir.mkdir(parents=True, exist_ok=True)
    head = tar_path.read_bytes()[:4]

    if head[:2] == b"\x1f\x8b" or head[:3] == b"BZh" or head[:2] == b"PK":
        for mode in ("r:gz", "r:bz2", "r:*"):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    with tarfile.open(tar_path, mode) as tar:
                        tar.extractall(extract_dir)
                return True
            except Exception:
                continue
    # Not an archive: arXiv sometimes serves a single .tex (or .pdf) file.
    if head.startswith(b"%PDF"):
        shutil.copy2(tar_path, extract_dir / "paper.pdf")
        return True
    # Plain text → single main.tex
    (extract_dir / "main.tex").write_bytes(tar_path.read_bytes())
    return True


# ─────────────────────────────────────────────────────────────────────────────
# LaTeX parsing
# ─────────────────────────────────────────────────────────────────────────────

def _find_main_tex(extract_dir: Path) -> list[Path]:
    """Return .tex files sorted by size (largest first = likely main file)."""
    tex_files = list(extract_dir.rglob("*.tex"))
    tex_files.sort(key=lambda p: p.stat().st_size, reverse=True)
    return tex_files


def _extract_latex_text(tex_files: list[Path], extract_dir: Path, max_chars: int) -> str:
    """Concatenate main .tex content, stripping the preamble and comments."""
    collected: list[str] = []
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
        # Inline \input{} / \include{} files so the dump is self-contained.
        tex_parent = tex.parent

        def _sub_included(m: re.Match, _p=tex_parent, _root=extract_dir) -> str:
            path = m.group(1).strip()
            for cand in (_p / path, _root / path):
                if cand.is_file():
                    try:
                        return cand.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        return ""
            return ""

        raw = re.sub(r"\\(?:input|include)\{([^}]+)\}", _sub_included, raw)
        collected.append(raw)
        total += len(raw)
        if total >= max_chars:
            break
    combined = "\n\n".join(collected)
    return combined[:max_chars]


# Figure keyword heuristics (checked against filename AND caption)
TASK_KW = ("teaser", "intro", "motivation", "concept", "task", "illustrat",
           "demonstrat", "visual comparison", "example", "fig1", "figure1",
           "problem", "setting", "application", "we present", "input and output")
METHOD_KW = ("method", "approach", "architecture", "pipeline", "framework",
             "model overview", "system overview", "overview of our", "overview of the",
             "proposed", "network", "consists of", "design", "arch", "model")
RESULT_KW = ("result", "exp", "compare", "ablat", "quantitative", "qualitative")


def _label_fig(fig: dict, idx: int) -> str:
    combined = fig["filename"].lower() + " " + fig.get("caption", "").lower()
    if any(k in combined for k in TASK_KW) and not any(k in combined for k in METHOD_KW):
        return "Task (问题/概念图)"
    if any(k in combined for k in METHOD_KW):
        return "Method (架构图)"
    if any(k in combined for k in RESULT_KW):
        return "Result (实验结果)"
    if idx == 0:
        return "Task (问题/概念图)"
    if idx == 1:
        return "Method (架构图)"
    return f"Figure {idx + 1}"


def _extract_figures(extract_dir: Path) -> list[dict]:
    """Extract figure references (filename + caption) from .tex files."""
    figures: list[dict] = []
    fig_pattern = re.compile(r"\\begin\{figure\*\?}(.*?)\\end\{figure\*\?}", re.DOTALL)
    include_pattern = re.compile(r"\\includegraphics(?:\[.*?\])?\{([^}]+)\}")
    caption_pattern = re.compile(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}")

    for tex_file in _find_main_tex(extract_dir):
        try:
            content = tex_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for match in fig_pattern.finditer(content):
            fig_body = match.group(1)
            inc = include_pattern.search(fig_body)
            cap = caption_pattern.search(fig_body)
            if inc and cap:
                filename = inc.group(1).strip()
                caption = re.sub(r"[{}\\]", "", cap.group(1)).strip()
                figures.append({"filename": filename, "caption": caption})
        if len(figures) >= 12:
            break

    labeled: list[dict] = []
    for i, fig in enumerate(figures[:12]):
        labeled.append({"type": _label_fig(fig, i), **fig})
    return labeled


def _copy_figure(fig: dict, extract_dir: Path, out_dir: Path) -> dict | None:
    """Locate the figure file inside the source tree and copy it to out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    src_rel = fig["filename"]
    name = Path(src_rel).name
    candidates: list[Path] = [extract_dir / src_rel]
    for ext in ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps", ".svg"):
        candidates += list(extract_dir.rglob(name + ext))
    found = next((c for c in candidates if c.is_file()), None)
    if not found:
        return None
    dest_name = re.sub(r"[/\\]", "_", src_rel)
    if not Path(dest_name).suffix and found.suffix:
        dest_name += found.suffix
    dest = out_dir / dest_name
    shutil.copy2(found, dest)
    return {**fig, "local_path": dest}


# ─────────────────────────────────────────────────────────────────────────────
# Figure conversion (vector → raster, for Obsidian/PKBase embedding)
# ─────────────────────────────────────────────────────────────────────────────

def _convert_figure(src: Path, out_dir: Path) -> dict:
    """Make a figure embeddable. Returns {embeddable_path, format, method, note}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()

    if ext in (".png", ".jpg", ".jpeg"):
        if src.parent != out_dir:
            shutil.copy2(src, out_dir / src.name)
        return {"embeddable_path": str(out_dir / src.name), "format": ext[1:], "method": "copy", "note": ""}

    if ext == ".svg":
        if src.parent != out_dir:
            shutil.copy2(src, out_dir / src.name)
        return {"embeddable_path": str(out_dir / src.name), "format": "svg", "method": "copy",
                "note": "SVG kept as-is; Obsidian renders it natively."}

    if ext == ".pdf":
        if not HAS_FITZ:
            return {"embeddable_path": None, "format": None, "method": None,
                    "note": "PyMuPDF (pip install PyMuPDF) not available — PDF not converted."}
        try:
            doc = fitz.open(src)
            page = doc[0]
            pix = page.get_pixmap(dpi=200)
            dest = out_dir / (src.stem + ".png")
            pix.save(dest)
            doc.close()
            return {"embeddable_path": str(dest), "format": "png", "method": "pymupdf@200dpi", "note": ""}
        except Exception as e:
            return {"embeddable_path": None, "format": None, "method": None, "note": f"PDF conversion failed: {e}"}

    if ext == ".eps":
        gs = shutil.which("gswin64c") or shutil.which("gs")
        if not gs:
            return {"embeddable_path": None, "format": None, "method": None,
                    "note": "Ghostscript not found — EPS not converted. Install Ghostscript or render manually."}
        try:
            dest = out_dir / (src.stem + ".png")
            subprocess.run(
                [gs, "-dNOPAUSE", "-dBATCH", "-dSAFER", "-dQUIET",
                 "-sDEVICE=png16m", "-r200", f"-sOutputFile={dest}", str(src)],
                check=True, capture_output=True, timeout=120,
            )
            return {"embeddable_path": str(dest), "format": "png", "method": "ghostscript@200dpi", "note": ""}
        except Exception as e:
            return {"embeddable_path": None, "format": None, "method": None, "note": f"EPS conversion failed: {e}"}

    return {"embeddable_path": None, "format": None, "method": None, "note": f"Unsupported figure format {ext}"}


def _pdf_to_text(pdf_path: Path, max_chars: int) -> str:
    """Extract text from a PDF (for non-arXiv papers without LaTeX source)."""
    if not HAS_PYPDF:
        return ""
    try:
        reader = PdfReader(str(pdf_path))
        parts = []
        total = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            parts.append(text)
            total += len(text)
            if total >= max_chars:
                break
        return "\n\n".join(parts)[:max_chars]
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Per-paper pipeline
# ─────────────────────────────────────────────────────────────────────────────

def process_paper(paper: dict, date_dir: Path, timeout: int, max_chars: int) -> dict:
    """Download + extract one paper. Returns a manifest entry."""
    aid = _arxiv_id(paper)
    title = paper.get("title", "Unknown")
    paper_id = aid or _paper_slug(paper)
    paper_dir = date_dir / "papers" / paper_id
    figures_manifest_path = paper_dir / "figures.json"

    if figures_manifest_path.exists():
        print(f"   [skip] {paper_id} already downloaded")
        return {"paper_id": paper_id, "title": title, "arxiv_id": aid, "status": "skipped-existing",
                "paper_dir": str(paper_dir)}

    print(f"\n   Downloading {paper_id}  {title[:60]}")
    paper_dir.mkdir(parents=True, exist_ok=True)
    entry: dict = {
        "paper_id": paper_id,
        "title": title,
        "arxiv_id": aid,
        "url": paper.get("url", ""),
        "pdf_url": paper.get("pdf_url", ""),
        "source": paper.get("source", ""),
        "published": paper.get("published", ""),
    }

    # ── PDF (always, for the raw/ archive copy) ────────────────────────────
    pdf_dest = paper_dir / "paper.pdf"
    if aid:
        ok = _http_download(ARXIV_PDF_URL.format(aid), pdf_dest, timeout)
        entry["pdf"] = str(pdf_dest) if ok else None
        if not ok:
            print(f"     [warn] PDF download failed for {aid}")
    else:
        pdf_url = paper.get("pdf_url", "")
        ok = _http_download(pdf_url, pdf_dest, timeout) if pdf_url else False
        entry["pdf"] = str(pdf_dest) if ok else None
        if not ok:
            print(f"     [warn] no PDF available for non-arXiv paper")

    # ── Source package (arXiv only) ─────────────────────────────────────────
    src_dir = paper_dir / "source"
    latex_text = ""

    if aid:
        tar_path = date_dir / "cache" / f"{aid}.tar.gz"
        if not (src_dir.exists() and any(src_dir.rglob("*.tex"))):
            if not _http_download(ARXIV_SOURCE_URL.format(aid), tar_path, timeout):
                entry["status"] = "source-failed"
                print(f"     [warn] source download failed for {aid}")
            else:
                _extract_source(tar_path, src_dir)
                tar_path.unlink(missing_ok=True)
        if src_dir.exists():
            tex_files = _find_main_tex(src_dir)
            if tex_files:
                latex_text = _extract_latex_text(tex_files, src_dir, max_chars)
                entry["tex_files"] = [str(p) for p in tex_files[:3]]
            else:
                entry["status"] = "no-latex"

    # ── Text dump for analysis ─────────────────────────────────────────────
    dump_path = paper_dir / "text_dump.txt"
    if latex_text:
        dump_path.write_text(latex_text, encoding="utf-8")
    elif pdf_dest.exists():
        pdf_text = _pdf_to_text(pdf_dest, max_chars)
        if pdf_text:
            dump_path.write_text(pdf_text, encoding="utf-8")
        else:
            dump_path.write_text(
                "(No LaTeX source and PDF text extraction unavailable — "
                "analyze from the abstract.)\n\n" + paper.get("abstract", ""),
                encoding="utf-8",
            )
    else:
        dump_path.write_text(paper.get("abstract", ""), encoding="utf-8")
    entry["text_dump"] = str(dump_path)

    # ── Figures ────────────────────────────────────────────────────────────
    figures: list[dict] = []
    if src_dir.exists():
        fig_out = paper_dir / "figures"
        for fig in _extract_figures(src_dir):
            copied = _copy_figure(fig, src_dir, fig_out)
            if copied:
                converted = _convert_figure(Path(copied["local_path"]), fig_out)
                copied.update(converted)
            else:
                copied = {**fig, "local_path": None, "embeddable_path": None,
                          "format": None, "method": None, "note": "figure file not found in source"}
            figures.append(copied)
    entry["figures_found"] = len(figures)
    entry.setdefault("status", "ok")
    figures_manifest_path.write_text(
        json.dumps(figures, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    entry["figures_json"] = str(figures_manifest_path)
    print(f"     ✓ {paper_id}: latex={bool(latex_text)}  figures={len(figures)}")
    return entry


def main() -> None:
    parser = argparse.ArgumentParser(description="Download arXiv sources + figures for ranked papers")
    parser.add_argument("--ranked", required=True, help="Path to ranked_papers.json")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Date string YYYY-MM-DD (default: today)")
    parser.add_argument("--artifacts", default="research-daily-ideas/artifacts",
                        help="Artifacts root (default: research-daily-ideas/artifacts)")
    parser.add_argument("--timeout", type=int, default=60, help="Per-request timeout seconds")
    parser.add_argument("--max-chars", type=int, default=100000,
                        help="Max characters for the per-paper text dump")
    args = parser.parse_args()

    ranked_path = Path(args.ranked)
    if not ranked_path.exists():
        sys.exit(f"[fatal] ranked papers file not found: {ranked_path}")
    payload = json.loads(ranked_path.read_text(encoding="utf-8"))
    papers = payload.get("papers") if isinstance(payload, dict) else payload
    if not papers:
        sys.exit("[fatal] no papers found in ranked file")

    date_dir = Path(args.artifacts) / args.date
    date_dir.mkdir(parents=True, exist_ok=True)

    print(f"[download_paper_sources] {len(papers)} papers → {date_dir}/papers/")
    print(f"  PyMuPDF: {'yes' if HAS_FITZ else 'NO (pip install PyMuPDF)'}  "
          f"pypdf: {'yes' if HAS_PYPDF else 'NO (pip install pypdf)'}  "
          f"requests: {'yes' if HAS_REQUESTS else 'NO (stdlib fallback)'}")

    manifest = []
    for i, paper in enumerate(papers, 1):
        print(f"\n#{i:02d}")
        manifest.append(process_paper(paper, date_dir, args.timeout, args.max_chars))

    manifest_path = date_dir / "download_manifest.json"
    manifest_path.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                    "date": args.date, "papers": manifest},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    ok = sum(1 for m in manifest if m["status"] in ("ok", "skipped-existing"))
    print(f"\n{'=' * 60}\n  Download complete: {ok}/{len(manifest)} papers ready\n"
          f"  Manifest: {manifest_path}\n{'=' * 60}")
    sys.exit(0)


if __name__ == "__main__":
    main()
