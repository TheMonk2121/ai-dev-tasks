#!/usr/bin/env python3
"""
A/B harness for namespace reserved slots (2 vs 3).
Reports hit@3 (if gold exists) and ns@3 per query and aggregated.
"""

from __future__ import annotations

import os
import sys


from dotenv import load_dotenv

sys.path.append("src")
from dspy_modules.vector_store import HybridVectorStore


def _hit_at_k(rows: list[dict], gold_ids: set[int] | None, k: int = 3):
    if not gold_ids:
        return None
    top = rows[:k]
    return 1.0 if any(r.get("document_id") in gold_ids for r in top) else 0.0


def _ns_at_k(rows: list[dict], ns_token: str | None, k: int = 3):
    if not ns_token:
        return None
    ns = ns_token.lower()

    def _m(r: dict) -> bool:
        fp = (r.get("file_path") or "").lower()
        fn = (r.get("filename") or "").lower()
        return (ns in fp) or (ns in fn)

    return 1.0 if any(_m(r) for r in rows[:k]) else 0.0


def evaluate_config(
    queries: list[str],
    search_fn,
    ns_token_map: dict[str, str],
    gold_map: dict[str, set[int]] | None,
    ns_reserved: int = 2,
    limit: int = 8,
):
    assert 0 <= ns_reserved <= limit, "ns_reserved must be ≤ limit"
    hit_vals: list[float] = []
    ns_vals: list[float] = []
    per_query = []

    for q in queries:
        out = search_fn(q, ns_reserved=ns_reserved, limit=limit)
        rows = out.get("results", [])
        h = _hit_at_k(rows, (gold_map or {}).get(q), k=3)
        n = _ns_at_k(rows, (ns_token_map or {}).get(q), k=3)
        if h is not None:
            hit_vals.append(h)
        if n is not None:
            ns_vals.append(n)
        per_query.append({"q": q, "hit3": h, "ns3": n, "n_rows": len(rows)})

    hit3 = sum(hit_vals) / len(hit_vals) if hit_vals else None
    ns3 = sum(ns_vals) / len(ns_vals) if ns_vals else None
    return {"ns_reserved": ns_reserved, "hit@3": hit3, "ns@3": ns3, "details": per_query}


def run_ab_test(
    queries: list[str], search_fn, ns_token_map: dict[str, str], gold_map: dict[str, set[int]] | None, limit: int = 8
):
    cfg2 = evaluate_config(queries, search_fn, ns_token_map, gold_map, ns_reserved=2, limit=limit)
    cfg3 = evaluate_config(queries, search_fn, ns_token_map, gold_map, ns_reserved=3, limit=limit)

    def fmt(x):
        return "—" if x is None else f"{x:.2f}"

    print("A/B (ns_reserved=2 vs 3)")
    print(f"  hit@3: {fmt(cfg2['hit@3'])}  →  {fmt(cfg3['hit@3'])}")
    print(f"  ns@3 : {fmt(cfg2['ns@3'])}   →  {fmt(cfg3['ns@3'])}")

    print("\nQueries where ns@3 changed:")
    for a, b in zip(cfg2["details"], cfg3["details"]):
        if a["q"] == b["q"] and a["ns3"] != b["ns3"]:
            print(f"  - {a['q']}: ns@3 {a['ns3']} → {b['ns3']} | hit@3 {a['hit3']} → {b['hit3']}")

    pick = (
        3
        if ((cfg3.get("ns@3") or 0) > (cfg2.get("ns@3") or 0) and (cfg3.get("hit@3") or 0) >= (cfg2.get("hit@3") or 0))
        else 2
    )
    print(f"\nSuggested ns_reserved = {pick}")
    return cfg2, cfg3, pick


def main():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1

    vs = HybridVectorStore(db_url)

    # Define queries and namespace tokens for ns@3
    queries = [
        "What is DSPy according to 400_07_ai-frameworks-dspy.md?",
        "List the core workflow guides in 000_core.",
        "What is the CONTEXT_INDEX?",
        "Where are coding and prompting standards documented?",
        "Where is the governance and AI constitution guide?",
        "Describe the memory and context systems.",
        "Show the development workflow and standards.",
        "What is in the backlog?",
        "Where is the system overview and architecture?",
        "What's the project overview?",
        "Where is the context priority guide?",
        "Which guides are included in the getting started index?",
        "Where is memory context workflow documented?",
        "Where are dspy development details?",
        "Where is the codebase index discussed?",
    ]

    ns_token_map = {
        queries[0]: "400_guides",
        queries[1]: "000_core",
        queries[2]: "100_memory",
        queries[3]: "400_guides",
        queries[4]: "400_guides",
        queries[5]: "400_guides",
        queries[6]: "400_guides",
        queries[7]: "000_core",
        queries[8]: "400_guides",
        queries[9]: "400_guides",
        queries[10]: "400_guides",
        queries[11]: "400_guides",
        queries[12]: "100_memory",
        queries[13]: "100_memory",
        queries[14]: "100_memory",
    }

    def search_fn(q: str, ns_reserved: int = 2, limit: int = 8):
        return vs._hybrid_search(query=q, limit=limit)

    run_ab_test(queries, search_fn, ns_token_map, gold_map=None, limit=8)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
