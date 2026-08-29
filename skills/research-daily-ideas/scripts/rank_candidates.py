#!/usr/bin/env python3
"""Rank candidate papers against a Zotero-style corpus."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

DEFAULT_MODEL = "jinaai/jina-embeddings-v5-text-nano"


def _load_config(path: str | None) -> dict:
    if not path:
        return {}
    return yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}


def _as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def _paper_text(paper: dict) -> str:
    title = (paper.get("title") or "").strip()
    abstract = (paper.get("abstract") or "").strip()
    return f"{title}\n\n{abstract}".strip()


def _coerce_authors(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(";") if item.strip()]
    return []


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_iso_datetime(value: str) -> datetime | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


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


def _load_json_list(path: str, expected_keys: tuple[str, ...]) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in expected_keys:
            if isinstance(data.get(key), list):
                items = data[key]
                break
        else:
            raise ValueError(f"Expected one of keys {expected_keys!r} in {path}")
    else:
        raise ValueError(f"Unsupported JSON structure in {path}")
    return [item for item in items if isinstance(item, dict)]


def _derive_weight_signals(item: dict) -> dict:
    raw_signals = item.get("weight_signals", {})
    signals = raw_signals if isinstance(raw_signals, dict) else {}

    annotation_count = int(_safe_float(signals.get("annotation_count"), len(item.get("annotations", []))))
    tag_signal = _clamp(_safe_float(signals.get("target_tag_match_score"), 0.0), 0.0, 1.0)
    collection_signal = _clamp(_safe_float(signals.get("target_collection_match_score"), 0.0), 0.0, 1.0)

    days_since_added = _safe_float(signals.get("days_since_added"), -1.0)
    if days_since_added < 0:
        added_dt = _parse_iso_datetime(str(item.get("added_date", "")))
        if added_dt is not None:
            now = datetime.now(timezone.utc)
            if added_dt.tzinfo is None:
                added_dt = added_dt.replace(tzinfo=timezone.utc)
            days_since_added = max(0.0, (now - added_dt).total_seconds() / 86400.0)
        else:
            days_since_added = 365.0

    recency_signal = _clamp(
        _safe_float(signals.get("recency_score"), 1.0 - min(days_since_added, 365.0) / 365.0),
        0.0,
        1.0,
    )
    annotation_signal = _clamp(annotation_count / 5.0, 0.0, 1.0)

    return {
        "annotation_count": annotation_count,
        "target_tag_match_score": round(tag_signal, 4),
        "target_collection_match_score": round(collection_signal, 4),
        "days_since_added": round(days_since_added, 2),
        "recency_score": round(recency_signal, 4),
        "annotation_score": round(annotation_signal, 4),
    }


def _resolve_weight(item: dict) -> tuple[float, dict]:
    explicit_weight = item.get("weight")
    if explicit_weight is not None:
        weight = _safe_float(explicit_weight, 1.0)
        return max(weight, 0.0), _derive_weight_signals(item)

    signals = _derive_weight_signals(item)
    weight = (
        1.0
        + 0.45 * signals["annotation_score"]
        + 0.20 * signals["target_tag_match_score"]
        + 0.20 * signals["target_collection_match_score"]
        + 0.15 * signals["recency_score"]
    )
    return round(weight, 4), signals


def rank_papers(
    corpus: list[dict],
    candidates: list[dict],
    model_name: str,
    top_k: int,
    corpus_top_k: int,
    neighbor_count: int,
) -> list[dict]:
    try:
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError:
        sys.exit("sentence-transformers and numpy are required: pip install sentence-transformers numpy")

    if not corpus:
        raise ValueError("Corpus is empty")
    if not candidates:
        return []

    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name, trust_remote_code=True)

    corpus_texts = [_paper_text(item) for item in corpus]
    candidate_texts = [_paper_text(item) for item in candidates]

    print(f"Encoding {len(corpus_texts)} corpus papers...")
    corpus_embeddings = np.asarray(
        model.encode(corpus_texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    )
    print(f"Encoding {len(candidate_texts)} candidate papers...")
    candidate_embeddings = np.asarray(
        model.encode(candidate_texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)
    )

    resolved_weights: list[float] = []
    resolved_signals: list[dict] = []
    for item in corpus:
        weight, signals = _resolve_weight(item)
        resolved_weights.append(weight)
        resolved_signals.append(signals)

    weights = np.asarray(resolved_weights, dtype=np.float32)
    if np.allclose(weights.sum(), 0.0):
        weights = np.ones(len(corpus), dtype=np.float32)

    results: list[dict] = []
    for paper, embedding in zip(candidates, candidate_embeddings):
        similarities = corpus_embeddings @ embedding
        top_indices = np.argsort(similarities)[::-1][: max(1, corpus_top_k)]
        top_similarities = similarities[top_indices]
        top_weights = weights[top_indices]

        max_similarity = float(top_similarities[0])
        weighted_similarity = float(np.average(top_similarities, weights=top_weights))
        score = 100.0 * (0.65 * weighted_similarity + 0.35 * max_similarity)

        matched_corpus = []
        for idx in top_indices[: max(1, neighbor_count)]:
            matched_corpus.append(
                {
                    "title": corpus[idx].get("title", ""),
                    "similarity": round(float(similarities[idx]), 4),
                    "weight": round(float(weights[idx]), 4),
                    "weight_signals": resolved_signals[idx],
                    "paths": corpus[idx].get("paths", []),
                }
            )

        enriched = dict(paper)
        enriched["score"] = round(score, 4)
        enriched["max_similarity"] = round(max_similarity, 4)
        enriched["weighted_similarity"] = round(weighted_similarity, 4)
        enriched["matched_corpus"] = matched_corpus
        results.append(enriched)

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank candidate papers against a Zotero-style corpus")
    parser.add_argument("--config", default=None, help="Optional YAML config path")
    parser.add_argument("--corpus", required=True, help="Corpus JSON path")
    parser.add_argument("--candidates", required=True, help="Candidate JSON path")
    parser.add_argument("--output", required=True, help="Output ranked JSON path")
    parser.add_argument("--top-k", type=int, default=None, help="Number of ranked papers to keep")
    parser.add_argument("--corpus-top-k", type=int, default=None, help="How many corpus neighbors contribute to scoring")
    parser.add_argument("--neighbor-count", type=int, default=None, help="How many matched corpus papers to store")
    parser.add_argument("--model", default=None, help="SentenceTransformer model name")
    args = parser.parse_args()

    config = _load_config(args.config)
    ranking_cfg = _as_dict(config.get("ranking", {}))
    embedding_cfg = _as_dict(config.get("embedding", {}))

    top_k = args.top_k or int(ranking_cfg.get("top_k", 20))
    corpus_top_k = args.corpus_top_k or int(ranking_cfg.get("corpus_top_k", 5))
    neighbor_count = args.neighbor_count or int(ranking_cfg.get("neighbor_count", 3))
    model_name = args.model or embedding_cfg.get("model") or DEFAULT_MODEL

    corpus = _load_json_list(args.corpus, expected_keys=("corpus", "papers", "items"))
    normalized_corpus_titles = {_normalize_title(item.get("title", "")) for item in corpus}

    raw_candidates = _load_json_list(args.candidates, expected_keys=("papers", "candidates", "items"))
    candidates = [_coerce_paper(item) for item in raw_candidates]
    candidates = [item for item in candidates if item]
    candidates = _dedupe_papers(candidates)
    candidates = [
        paper
        for paper in candidates
        if _normalize_title(paper.get("title", "")) not in normalized_corpus_titles
    ]

    ranked = rank_papers(
        corpus=corpus,
        candidates=candidates,
        model_name=model_name,
        top_k=top_k,
        corpus_top_k=corpus_top_k,
        neighbor_count=neighbor_count,
    )

    now = datetime.now(timezone.utc)
    payload = {
        "generated_at": now.isoformat(),
        "sources": sorted({paper.get("source", "") for paper in candidates if paper.get("source")}),
        "model": model_name,
        "candidates_considered": len(candidates),
        "papers": ranked,
    }

    candidate_payload = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    if isinstance(candidate_payload, dict) and isinstance(candidate_payload.get("date_window"), dict):
        payload["date_window"] = candidate_payload["date_window"]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Ranked {len(ranked)} papers -> {output_path}")
    for index, paper in enumerate(ranked[:5], start=1):
        print(f"#{index:02d} [{paper['score']:.2f}] {paper['title']}")


if __name__ == "__main__":
    main()
