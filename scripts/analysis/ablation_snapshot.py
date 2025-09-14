from __future__ import annotations

import json
import os
import sys
from typing import Any, Optional, Union

from _bootstrap import ROOT, SRC  # noqa: F401
from evals.gold import gold_hit
from scripts.migrate_to_pydantic_evals import load_eval_cases

from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import per_file_cap

#!/usr/bin/env python3
"""
Ablation snapshot for retrieval-13of13-stable.
Runs progressive feature ablation to establish provenance.
"""

# bootstrap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Ablation stages
ABLATION_STAGES = [
    {
        "name": "base",
        "description": "Base retrieval (no optimizations)",
        "config": {
            "w_path": 1.0,
            "w_short": 1.0,
            "w_title": 1.0,
            "w_bm25": 1.0,
            "w_vec": 1.0,
            "adjacency_db": False,
            "per_file_cap": 10,
        },
    },
    {
        "name": "path_tsv",
        "description": "Base + path_tsv column",
        "config": {
            "w_path": 2.0,
            "w_short": 1.0,
            "w_title": 1.0,
            "w_bm25": 1.0,
            "w_vec": 1.0,
            "adjacency_db": False,
            "per_file_cap": 10,
        },
    },
    {
        "name": "phrases",
        "description": "Base + path_tsv + phrase hints",
        "config": {
            "w_path": 2.0,
            "w_short": 1.8,
            "w_title": 1.4,
            "w_bm25": 1.0,
            "w_vec": 1.0,
            "adjacency_db": False,
            "per_file_cap": 10,
        },
    },
    {
        "name": "mmr_cap",
        "description": "Base + path_tsv + phrases + MMR/cap",
        "config": {
            "w_path": 2.0,
            "w_short": 1.8,
            "w_title": 1.4,
            "w_bm25": 1.0,
            "w_vec": 1.0,
            "adjacency_db": False,
            "per_file_cap": 5,
        },
    },
    {
        "name": "adjacency",
        "description": "Base + path_tsv + phrases + MMR/cap + adjacency",
        "config": {
            "w_path": 2.0,
            "w_short": 1.8,
            "w_title": 1.4,
            "w_bm25": 1.0,
            "w_vec": 1.0,
            "adjacency_db": True,
            "per_file_cap": 5,
        },
    },
    {
        "name": "fname_prior",
        "description": "Base + path_tsv + phrases + MMR/cap + adjacency + fname_prior",
        "config": {
            "w_path": 2.0,
            "w_short": 1.8,
            "w_title": 1.4,
            "w_bm25": 1.0,
            "w_vec": 1.1,
            "adjacency_db": True,
            "per_file_cap": 4,
        },
    },
]

def eval_stage(stage: dict[str, Any], cases: list[Any]) -> dict[str, Any]:
    """Evaluate a single ablation stage."""
    config = stage["config"]
    hits = 0
    tag_hits = {}
    tag_total = {}

    for case in cases:
        try:
            tag = getattr(case, "tag", None)
            if not tag:
                tags_list = getattr(case, "tags", []) or []
                tag = tags_list[0] if tags_list else "rag_qa_single"
            qs = build_channel_queries(case.query, tag)
            rows = run_fused_query(
                qs["short"],
                qs["title"],
                qs["bm25"],
                getattr(case, "qvec", None),
                k=25,
                use_mmr=True,
                weights={k: v for k, v in config.items() if k.startswith("w_")},
                tag=tag,
                fname_regex=qs.get("fname_regex"),
                adjacency_db=config.get("adjacency_db", False),
                cold_start=bool(qs.get("cold_start", False)),
            )

            # Apply per-file cap

            rows = per_file_cap(rows, cap=config.get("per_file_cap", 5))

            hit = int(gold_hit(case.id, rows))
            hits += hit

            # Track per-tag
            if tag not in tag_hits:
                tag_hits[tag] = 0
                tag_total[tag] = 0
            tag_hits[tag] += hit
            tag_total[tag] += 1

        except Exception as e:
            print(f"Error evaluating case {case.id}: {e}")

    total_cases = len(cases)
    micro_avg = hits / total_cases if total_cases > 0 else 0.0

    # Calculate per-tag averages
    per_tag = {}
    for tag in tag_total:
        per_tag[tag] = tag_hits[tag] / tag_total[tag] if tag_total[tag] > 0 else 0.0

    macro_avg = sum(per_tag.values()) / len(per_tag) if per_tag else 0.0

    return {
        "stage": stage["name"],
        "description": stage["description"],
        "config": config,
        "hits": hits,
        "total_cases": total_cases,
        "micro_avg": micro_avg,
        "macro_avg": macro_avg,
        "per_tag": per_tag,
        "tag_hits": tag_hits,
        "tag_total": tag_total,
    }

def main():
    """Run ablation snapshot."""
    print("🔍 Running ablation snapshot for retrieval-13of13-stable...")
    print("=" * 60)

    cases = load_eval_cases("gold")
    print(f"Loaded {len(cases)} evaluation cases")

    results = []
    baseline_hits = None

    for i, stage in enumerate(ABLATION_STAGES):
        print(f"\n[{i+1}/{len(ABLATION_STAGES)}] Testing: {stage['name']}")
        print(f"Description: {stage['description']}")

        result = eval_stage(stage, cases)
        results.append(result)

        if baseline_hits is None:
            baseline_hits = result["hits"]

        delta = result["hits"] - baseline_hits
        print(f"Results: {result['hits']}/{result['total_cases']} hits (Δ{delta:+d})")
        print(f"Micro: {result['micro_avg']:.3f}, Macro: {result['macro_avg']:.3f}")

        # Show per-tag breakdown
        for tag, avg in result["per_tag"].items():
            print(f"  {tag}: {avg:.3f}")

    # Calculate deltas
    print("\n" + "=" * 60)
    print("📊 ABLATION SUMMARY")
    print("=" * 60)

    for i, result in enumerate(results):
        if i == 0:
            delta = 0
            delta_pct = 0.0
        else:
            delta = result["hits"] - results[0]["hits"]
            delta_pct = (delta / results[0]["hits"]) * 100 if results[0]["hits"] > 0 else 0.0

        print(
            f"{result['stage']:12} | {result['hits']:2d}/{result['total_cases']:2d} | "
            f"Δ{delta:+3d} ({delta_pct:+5.1f}%) | {result['micro_avg']:.3f} | {result['macro_avg']:.3f}"
        )

    # Save results
    output_file = "ABLATION_SNAPSHOT_retrieval-13of13-stable.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tag": "retrieval-13of13-stable",
                "commit": "f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8",
                "timestamp": "2025-09-07T00:00:00Z",
                "total_cases": len(cases),
                "stages": results,
                "summary": {
                    "baseline_hits": results[0]["hits"],
                    "final_hits": results[-1]["hits"],
                    "total_improvement": results[-1]["hits"] - results[0]["hits"],
                    "improvement_pct": (
                        ((results[-1]["hits"] - results[0]["hits"]) / results[0]["hits"]) * 100
                        if results[0]["hits"] > 0
                        else 0.0
                    ),
                },
            },
            f,
            indent=2,
        )

    print(f"\n✅ Ablation snapshot saved to: {output_file}")
    print(
        f"📈 Total improvement: {results[-1]['hits'] - results[0]['hits']:+d} hits "
        f"({((results[-1]['hits'] - results[0]['hits']) / results[0]['hits']) * 100 if results[0]['hits'] > 0 else 0.0:+.1f}%)"
    )

if __name__ == "__main__":
    main()
