#!/usr/bin/env python3
"""
Minimal gold-set evaluation: reports hit@K, ns@K, and MRR@topK using the
current HybridVectorStore (wrapper-enabled by env flags).
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional, Set

from dotenv import load_dotenv

sys.path.append("src")
import time

import psycopg2

from dspy_modules.vector_store import HybridVectorStore
from dspy_modules.wrapper_ns_helpers import extract_ns_tokens, normalize_ns_token

# ---- DEPRECATED: Gold cases now live in evals/gold/v1/gold_cases.jsonl ----
# Use src/utils/gold_loader.py from evaluation scripts instead of these hardcoded dicts.
#
# These were migrated to the unified gold dataset system on 2025-09-08.
# See evals/gold/v1/README.md for the new schema and usage.
#
# Legacy GOLD and ADDITIONAL_GOLD dicts removed to prevent drift and ensure
# all evaluations use the same question distribution for consistent metrics.


def match_gold(row: Dict[str, Any], gold: Dict[str, Any]) -> bool:
    if "doc_ids" in gold and row.get("document_id") in gold["doc_ids"]:
        return True
    if "filenames" in gold and row.get("filename") in gold["filenames"]:
        return True
    if "paths" in gold and row.get("file_path") in gold["paths"]:
        return True
    if "namespace" in gold:
        ns = str(gold["namespace"]).rstrip("/")
        fp = row.get("file_path") or ""
        # namespace inferred from first path segment
        if fp.split("/", 1)[0] == ns:
            return True
    return False


def ns_flag(row: Dict[str, Any], namespace: str) -> bool:
    ns = str(namespace).rstrip("/")
    fp = row.get("file_path") or ""
    return fp.split("/", 1)[0] == ns


def _get_existing_namespaces(db_url: str) -> Set[str]:
    try:
        with psycopg2.connect(db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT namespace FROM documents")
                return {r[0] for r in cur.fetchall() if r[0]}
    except Exception:
        return set()


def _intent_set(q: str, existing_namespaces: Set[str]) -> Set[str]:
    tokens = set(extract_ns_tokens(q))
    for w in q.lower().replace("\n", " ").split():
        nt = normalize_ns_token(w)
        if nt:
            tokens.add(nt)
    return {t for t in tokens if t in existing_namespaces}


def evaluate(search_fn, gold: Dict[str, Dict[str, Any]], top_k: int = 10, at_k: int = 3) -> Dict[str, float]:
    total = len(gold)
    hit_at_k = 0
    ns_at_k = 0
    mrr_sum = 0.0
    intent_hits = 0
    scoped = 0
    dup_rates: List[float] = []
    latencies: List[float] = []

    db_url = os.getenv("DATABASE_URL", "")
    existing_namespaces = _get_existing_namespaces(db_url) if db_url else set()

    for q, g in gold.items():
        t0 = time.time()
        rows: List[Dict[str, Any]] = search_fn(q, top_k)
        latencies.append(max(0.0, time.time() - t0))

        topk = rows[:at_k]
        if any(match_gold(r, g) for r in topk):
            hit_at_k += 1

        if "namespace" in g and any(ns_flag(r, g["namespace"]) for r in topk):
            ns_at_k += 1

        # intent@k using inferred/mapped namespaces
        intent = _intent_set(q, existing_namespaces)
        if intent:
            scoped += 1
            if any(ns_flag(r, ns) for ns in intent for r in topk):
                intent_hits += 1

        # dup rate @3
        ids = [r.get("document_id") for r in topk]
        unique = len({i for i in ids if i is not None}) or 1
        dup_rates.append(1.0 - (unique / max(1, len(ids))))

        rr: Optional[float] = None
        for i, r in enumerate(rows[:top_k]):
            if match_gold(r, g):
                rr = 1.0 / (i + 1)
                break
        if rr is not None:
            mrr_sum += rr

    # latency p95
    p95 = 0.0
    if latencies:
        lat_sorted = sorted(latencies)
        idx = int(0.95 * (len(lat_sorted) - 1))
        p95 = lat_sorted[idx]

    return {
        f"hit@{at_k}": (hit_at_k / total) if total else 0.0,
        f"ns@{at_k}": (ns_at_k / total) if total else 0.0,
        f"mrr@{top_k}": (mrr_sum / total) if total else 0.0,
        "intent@3": (intent_hits / scoped) if scoped else 0.0,
        "scoped_n": float(scoped),
        "dup_rate@3": sum(dup_rates) / len(dup_rates) if dup_rates else 0.0,
        "p95_latency_s": p95,
        "n": float(total),
    }


def make_search_fn(store: HybridVectorStore):
    def search_fn(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        out = store("search", query=query, limit=top_k)
        return out.get("results", []) if isinstance(out, dict) else []

    return search_fn


def main() -> int:
    load_dotenv()
    os.environ.setdefault("HYBRID_USE_WRAPPER", "1")
    os.environ.setdefault("NS_RESERVED", "2")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1

    store = HybridVectorStore(db_url)
    search_fn = make_search_fn(store)

    # Load gold cases from unified dataset
    try:
        from src.utils.gold_loader import filter_cases, load_gold_cases

        cases = load_gold_cases("evals/gold/v1/gold_cases.jsonl")
        # Filter for retrieval mode cases
        retrieval_cases = filter_cases(cases, mode="retrieval")

        # Convert to legacy format for compatibility
        gold_dict = {}
        for case in retrieval_cases:
            gold_dict[case.query] = {}
            if case.expected_files:
                gold_dict[case.query]["filenames"] = set(case.expected_files)
            if case.globs:
                gold_dict[case.query]["paths"] = set(case.globs)
            if case.category == "namespace":
                # Handle namespace cases
                gold_dict[case.query]["namespace"] = case.query.split()[-1].rstrip(".")

        metrics = evaluate(search_fn, gold_dict, top_k=10, at_k=3)
        print(metrics)
        return 0

    except ImportError:
        print("❌ New gold loader not available, falling back to empty evaluation")
        print("📝 Install the new gold system: evals/gold/v1/")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
