#!/usr/bin/env python3
"""
Smoke test for prefilter recovery after BM25 hinting fix.
Tests the surgical patch implementation with low concurrency.
"""

import os
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from _bootstrap import ROOT, SRC  # ensure imports work
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap

from evals.gold import gold_hit
from scripts.migrate_to_pydantic_evals import load_eval_cases

## Cases now come from evals/load_cases with CASES_FILE env var


def pretty_row(r: dict[str, Any]) -> str:
    return (
        f"{(r.get('file_path') or r.get('filename') or '')} | score={r.get('score',0):.3f} "
        f"path={r.get('s_path',0):.3f} short={r.get('s_short',0):.3f} "
        f"title={r.get('s_title',0):.3f} bm25={r.get('s_bm25',0):.3f} vec={r.get('s_vec',0):.3f}"
    )


def run_case(case: Any) -> tuple[str, list[dict[str, Any]]]:
    """
    Run a single evaluation case.

    Args:
        case: Evaluation case dictionary

    Returns:
        Tuple of (case_id, list_of_rows)
    """
    try:
        qs = build_channel_queries(case.query, case.tag)
        lim = load_limits(case.tag)
        rows = run_fused_query(
            qs["short"],
            qs["title"],
            qs["bm25"],
            case.qvec,
            k=lim["shortlist"],
            use_mmr=False,
            tag=case.tag,
            return_components=True,
            fname_regex=qs.get("fname_regex"),
            adjacency_db=True,
        )
        rows = mmr_rerank(rows, alpha=0.85, per_file_penalty=0.10, k=lim["shortlist"])
        rows = per_file_cap(rows, cap=5)[: lim["topk"]]
        if not rows:
            print(f"Case {case.id}: 0 rows (empty query? q_short='{qs['short'][:80]}', q_bm25='{qs['bm25'][:80]}')")
        return case.id, rows
    except Exception as e:
        print(f"Error running case {getattr(case,'id',None)}: {e}")
        print(traceback.format_exc())
        return getattr(case, "id", "unknown"), []


def main():
    """Run smoke test with low concurrency."""
    print("🔥 Running smoke test for prefilter recovery...")
    print("=" * 50)

    cases = load_eval_cases("gold_standard")
    print(f"Loaded {len(cases)} evaluation cases")

    hits = 0
    total_cases = len(cases)

    # Run with low concurrency (max_workers=3) as specified
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(run_case, cases))

    for case_id, rows in results:
        hit = gold_hit(case_id, rows)
        hits += int(hit)
        status = "✅ HIT" if hit else "❌ MISS"
        print(f"Case {case_id}: {status} ({len(rows)} chunks retrieved)")
        for r in rows[:5]:
            print("   ", pretty_row(r))

    print("=" * 50)
    print(f"Prefilter hits: {hits}/{total_cases}")

    # Target after revert should be at least baseline (≈4/30)
    # Typical outcome with short/title hinting: 8–14/30
    if hits >= 4:
        print("✅ Recovery successful - at least baseline performance restored")
    else:
        print("⚠️  Recovery incomplete - may need additional tuning")

    return hits, total_cases


if __name__ == "__main__":
    main()
