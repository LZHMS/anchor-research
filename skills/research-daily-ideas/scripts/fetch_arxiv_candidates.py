#!/usr/bin/env python3
"""Fetch recent arXiv papers into a normalized candidate-paper JSON file."""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_API = "https://export.arxiv.org/api/query"
DEFAULT_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def _coerce_authors(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(";") if item.strip()]
    return []


def _coerce_paper(item: dict, default_source: str = "") -> dict | None:
    title = (item.get("title") or "").strip()
    abstract = (item.get("abstract") or item.get("summary") or "").strip()
    if not title:
        return None
    return {
        "title": title,
        "abstract": abstract,
        "authors": _coerce_authors(item.get("authors")),
        "url": item.get("url") or item.get("abs_url") or "",
        "pdf_url": item.get("pdf_url") or "",
        "source": item.get("source") or default_source,
        "published": item.get("published") or item.get("date") or "",
    }


def _paper_completeness(paper: dict) -> tuple[int, int]:
    fields = ["abstract", "authors", "url", "pdf_url", "source", "published"]
    filled = 0
    for field in fields:
        value = paper.get(field)
        if isinstance(value, list):
            filled += 1 if value else 0
        else:
            filled += 1 if str(value or "").strip() else 0
    return filled, len((paper.get("abstract") or "").strip())


def _prefer_better(existing: dict, candidate: dict) -> dict:
    return candidate if _paper_completeness(candidate) > _paper_completeness(existing) else existing


def _dedupe_papers(papers: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for paper in papers:
        key = _normalize_title(paper.get("title", ""))
        if not key:
            continue
        current = deduped.get(key)
        deduped[key] = paper if current is None else _prefer_better(current, paper)
    return list(deduped.values())


def _load_json_list(path: str) -> list[dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        for key in ("papers", "candidates", "items"):
            if isinstance(payload.get(key), list):
                items = payload[key]
                break
        else:
            raise ValueError(f"Unsupported candidate JSON structure in {path}")
    else:
        raise ValueError(f"Unsupported candidate JSON structure in {path}")
    return [item for item in items if isinstance(item, dict)]


def fetch_arxiv_recent(category: str, days: int, max_results: int) -> list[dict]:
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days)
    query = (
        f"cat:{category} AND "
        f"submittedDate:[{start_dt.strftime('%Y%m%d')}0000 TO {end_dt.strftime('%Y%m%d')}2359]"
    )
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"

    root = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                root = ET.parse(response).getroot()
            break
        except Exception as exc:
            if attempt < 2 and getattr(exc, "code", None) in (403, 429):
                wait = 10 * (attempt + 1)
                print(f"[warn] arXiv rate-limited ({exc}); retrying in {wait}s...")
                time.sleep(wait)
                continue
            print(f"[warn] Failed to fetch arXiv category {category}: {exc}")
            return []
    if root is None:
        return []

    papers: list[dict] = []
    for entry in root.findall("atom:entry", ARXIV_NS):
        entry_id = entry.findtext("atom:id", "", ARXIV_NS)
        arxiv_id = entry_id.split("/")[-1].split("v")[0] if entry_id else ""
        paper = _coerce_paper(
            {
                "title": entry.findtext("atom:title", "", ARXIV_NS).replace("\n", " ").strip(),
                "abstract": entry.findtext("atom:summary", "", ARXIV_NS).replace("\n", " ").strip(),
                "authors": [
                    author.findtext("atom:name", "", ARXIV_NS)
                    for author in entry.findall("atom:author", ARXIV_NS)
                ],
                "url": entry_id,
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else "",
                "source": f"arxiv:{category}",
                "published": entry.findtext("atom:published", "", ARXIV_NS),
            },
            default_source=f"arxiv:{category}",
        )
        if paper:
            papers.append(paper)
        time.sleep(0.05)
    return papers


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch recent arXiv papers into a candidate JSON file")
    parser.add_argument("--config", default=None, help="Optional YAML config path")
    parser.add_argument(
        "--output",
        default="artifacts/arxiv_candidates.json",
        help="Output candidate JSON path",
    )
    parser.add_argument("--days", type=int, default=None, help="Look-back window for fetched papers")
    parser.add_argument("--max-candidates", type=int, default=None, help="Max results fetched per category")
    parser.add_argument("--category", action="append", dest="categories", help="arXiv category, repeatable")
    parser.add_argument(
        "--existing",
        default=None,
        help="Optional existing candidate JSON path to merge with before writing output",
    )
    args = parser.parse_args()

    config = _load_config(args.config)
    source_cfg = _as_dict(config.get("sources", {}))
    arxiv_cfg = _as_dict(config.get("arxiv", {}))

    days = args.days or int(source_cfg.get("days", 2))
    max_candidates = args.max_candidates or int(source_cfg.get("max_candidates", 100))
    categories = args.categories or arxiv_cfg.get("categories") or DEFAULT_CATEGORIES

    papers: list[dict] = []
    for i, category in enumerate(categories):
        if i:
            time.sleep(3)  # arXiv API politeness: ~3s between requests
        print(f"Fetching arXiv category {category}...")
        papers.extend(fetch_arxiv_recent(category=category, days=days, max_results=max_candidates))

    if args.existing:
        existing = [_coerce_paper(item) for item in _load_json_list(args.existing)]
        papers.extend(item for item in existing if item)

    deduped = _dedupe_papers(papers)
    now = datetime.now(timezone.utc)
    payload = {
        "generated_at": now.isoformat(),
        "date_window": {
            "days": days,
            "start": (now - timedelta(days=days)).date().isoformat(),
            "end": now.date().isoformat(),
        },
        "sources": [f"arxiv:{category}" for category in categories],
        "papers": deduped,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(deduped)} candidate papers -> {output_path}")
    for index, paper in enumerate(deduped[:5], start=1):
        print(f"#{index:02d} {paper['title']}")


if __name__ == "__main__":
    main()
