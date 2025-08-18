#!/usr/bin/env python3
"""
A/B Testing Script for Entity Expansion
---------------------------------------
Run baseline and variant tests to measure entity expansion effectiveness.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

from utils.memory_rehydrator import rehydrate


def load_query_set(file_path: str) -> list[dict[str, Any]]:
    """Load queries from JSONL file."""
    queries = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line:
                queries.append(json.loads(line))
    return queries


def run_test(queries: list[dict[str, Any]], use_entity_expansion: bool, test_name: str) -> dict[str, Any]:
    """Run a test with the given queries and entity expansion setting."""
    print(f"\n🧪 Running {test_name} test...")
    print(f"   Entity expansion: {'enabled' if use_entity_expansion else 'disabled'}")
    print(f"   Queries: {len(queries)}")

    results = {
        "test_name": test_name,
        "use_entity_expansion": use_entity_expansion,
        "query_count": len(queries),
        "total_entities_found": 0,
        "total_chunks_added": 0,
        "total_expansion_latency_ms": 0.0,
        "total_tokens": 0,
        "queries_with_entities": 0,
        "queries_with_expansion": 0,
        "errors": 0,
    }

    for i, query_data in enumerate(queries):
        query = query_data["query"]
        qid = query_data.get("qid", f"Q{i+1}")

        print(f"   Processing {qid}: {query[:50]}...")

        try:
            bundle = rehydrate(
                query=query,
                use_entity_expansion=use_entity_expansion,
                max_tokens=1200,  # Target token limit
                role="planner",
            )

            # Extract metrics
            entities_found = bundle.meta.get("entities_found", 0)
            chunks_added = bundle.meta.get("chunks_added", 0)
            expansion_latency = bundle.meta.get("expansion_latency_ms", 0.0)
            tokens = bundle.meta.get("evidence_tokens", 0) + bundle.meta.get("pins_tokens", 0)

            # Update totals
            results["total_entities_found"] += entities_found
            results["total_chunks_added"] += chunks_added
            results["total_expansion_latency_ms"] += expansion_latency
            results["total_tokens"] += tokens

            if entities_found > 0:
                results["queries_with_entities"] += 1

            if chunks_added > 0:
                results["queries_with_expansion"] += 1

            print(
                f"     Entities: {entities_found}, "
                f"Chunks added: {chunks_added}, "
                f"Latency: {expansion_latency:.2f}ms, "
                f"Tokens: {tokens}"
            )

        except Exception as e:
            print(f"     ❌ Error: {e}")
            results["errors"] += 1

    # Calculate averages
    if results["query_count"] > 0:
        results["avg_entities_per_query"] = results["total_entities_found"] / results["query_count"]
        results["avg_chunks_added_per_query"] = results["total_chunks_added"] / results["query_count"]
        results["avg_expansion_latency_ms"] = results["total_expansion_latency_ms"] / results["query_count"]
        results["avg_tokens_per_query"] = results["total_tokens"] / results["query_count"]
        results["entity_query_ratio"] = results["queries_with_entities"] / results["query_count"]
        results["expansion_query_ratio"] = results["queries_with_expansion"] / results["query_count"]

    return results


def main():
    """Run A/B testing for entity expansion."""
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/ab_test_entity_expansion.py <query_set_file>")
        print("Example: python3 scripts/ab_test_entity_expansion.py dspy-rag-system/tests/queries/QUERY_SET_1.jsonl")
        sys.exit(1)

    query_file = sys.argv[1]

    if not os.path.exists(query_file):
        print(f"❌ Query file not found: {query_file}")
        sys.exit(1)

    print("🚀 Entity Expansion A/B Testing")
    print("=" * 50)

    # Load queries
    queries = load_query_set(query_file)
    print(f"📋 Loaded {len(queries)} queries from {query_file}")

    # Run baseline test (no entity expansion)
    baseline_results = run_test(queries, use_entity_expansion=False, test_name="Baseline")

    # Run variant test (with entity expansion)
    variant_results = run_test(queries, use_entity_expansion=True, test_name="Variant")

    # Generate comparison
    print("\n📊 A/B Test Results")
    print("=" * 50)

    comparison = {"baseline": baseline_results, "variant": variant_results, "improvements": {}}

    # Calculate improvements
    if baseline_results["avg_entities_per_query"] > 0:
        comparison["improvements"]["entity_detection"] = (
            (variant_results["avg_entities_per_query"] - baseline_results["avg_entities_per_query"])
            / baseline_results["avg_entities_per_query"]
            * 100
        )

    if baseline_results["avg_chunks_added_per_query"] > 0:
        comparison["improvements"]["chunk_expansion"] = (
            (variant_results["avg_chunks_added_per_query"] - baseline_results["avg_chunks_added_per_query"])
            / baseline_results["avg_chunks_added_per_query"]
            * 100
        )

    # Print results table
    print("| Metric | Baseline | Variant | Δ |")
    print("|---|---:|---:|---:|")

    metrics = [
        ("avg_entities_per_query", "Avg Entities/Query"),
        ("avg_chunks_added_per_query", "Avg Chunks Added"),
        ("avg_expansion_latency_ms", "Avg Latency (ms)"),
        ("avg_tokens_per_query", "Avg Tokens"),
        ("entity_query_ratio", "Entity Query Ratio"),
        ("expansion_query_ratio", "Expansion Query Ratio"),
    ]

    for key, label in metrics:
        baseline_val = baseline_results.get(key, 0)
        variant_val = variant_results.get(key, 0)

        if baseline_val > 0:
            delta = ((variant_val - baseline_val) / baseline_val) * 100
            delta_str = f"{delta:+.1f}%"
        else:
            delta_str = "n/a"

        print(f"| {label} | {baseline_val:.3f} | {variant_val:.3f} | {delta_str} |")

    # Print summary
    print("\n📈 Summary:")
    print(f"   Entity detection: {variant_results['queries_with_entities']}/{variant_results['query_count']} queries")
    print(
        f"   Expansion occurred: {variant_results['queries_with_expansion']}/{variant_results['query_count']} queries"
    )
    print(f"   Average expansion latency: {variant_results['avg_expansion_latency_ms']:.2f}ms")
    print(f"   Errors: {baseline_results['errors'] + variant_results['errors']}")

    # Save results
    output_file = f"ab_test_results_{int(time.time())}.json"
    with open(output_file, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")
    print("🔧 Use: python3 scripts/summarize_ab.py baseline.json variant.json")


if __name__ == "__main__":
    main()
