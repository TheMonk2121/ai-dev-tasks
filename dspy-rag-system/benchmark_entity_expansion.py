#!/usr/bin/env python3
"""
Entity Expansion Performance Benchmark
Simple benchmark to compare performance with and without entity expansion
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.memory_rehydrator import rehydrate

def benchmark_entity_expansion():
    """Benchmark entity expansion performance"""
    print("🚀 Entity Expansion Performance Benchmark")
    print("=" * 50)

    test_queries = [
        "How to use HybridVectorStore?",
        "What is the memory rehydrator system?",
        "How do I implement entity_overlay.py and memory_rehydrator.py?",
        "Explain the database_resilience.py module",
        "What are the patterns for entity extraction?",
    ]

    results = {
        "baseline": {"times": [], "entities": [], "chunks": [], "tokens": []},
        "variant": {"times": [], "entities": [], "chunks": [], "tokens": []},
    }

    print(f"\n🧪 Testing {len(test_queries)} queries...")

    for i, query in enumerate(test_queries, 1):
        print(f"\n  Query {i}: {query[:50]}...")

        # Baseline test (no entity expansion)
        start_time = time.time()
        baseline_bundle = rehydrate(query, use_entity_expansion=False, max_tokens=1200)
        baseline_time = time.time() - start_time

        # Variant test (with entity expansion)
        start_time = time.time()
        variant_bundle = rehydrate(query, use_entity_expansion=True, max_tokens=1200)
        variant_time = time.time() - start_time

        # Collect metrics
        baseline_tokens = baseline_bundle.meta.get("evidence_tokens", 0) + baseline_bundle.meta.get("pins_tokens", 0)
        variant_tokens = variant_bundle.meta.get("evidence_tokens", 0) + variant_bundle.meta.get("pins_tokens", 0)

        results["baseline"]["times"].append(baseline_time)
        results["baseline"]["entities"].append(0)  # No entities when disabled
        results["baseline"]["chunks"].append(0)  # No expansion when disabled
        results["baseline"]["tokens"].append(baseline_tokens)

        results["variant"]["times"].append(variant_time)
        results["variant"]["entities"].append(variant_bundle.meta.get("entities_found", 0))
        results["variant"]["chunks"].append(variant_bundle.meta.get("chunks_added", 0))
        results["variant"]["tokens"].append(variant_tokens)

        print(f"    Baseline: {baseline_time:.3f}s, {baseline_tokens} tokens")
        print(f"    Variant:  {variant_time:.3f}s, {variant_tokens} tokens")
        print(f"    Entities: {variant_bundle.meta.get('entities_found', 0)}")
        print(f"    Chunks:   {variant_bundle.meta.get('chunks_added', 0)}")

    # Calculate statistics
    print("\n📊 Performance Summary")
    print("=" * 50)

    for mode in ["baseline", "variant"]:
        times = results[mode]["times"]
        entities = results[mode]["entities"]
        chunks = results[mode]["chunks"]
        tokens = results[mode]["tokens"]

        avg_time = sum(times) / len(times)
        avg_entities = sum(entities) / len(entities)
        avg_chunks = sum(chunks) / len(chunks)
        avg_tokens = sum(tokens) / len(tokens)

        print(f"\n{mode.upper()} Results:")
        print(f"  Average time:     {avg_time:.3f}s")
        print(f"  Average entities: {avg_entities:.1f}")
        print(f"  Average chunks:   {avg_chunks:.1f}")
        print(f"  Average tokens:   {avg_tokens:.0f}")

    # Calculate differences
    baseline_avg_time = sum(results["baseline"]["times"]) / len(results["baseline"]["times"])
    variant_avg_time = sum(results["variant"]["times"]) / len(results["variant"]["times"])
    baseline_avg_tokens = sum(results["baseline"]["tokens"]) / len(results["baseline"]["tokens"])
    variant_avg_tokens = sum(results["variant"]["tokens"]) / len(results["variant"]["tokens"])

    time_diff = variant_avg_time - baseline_avg_time
    time_diff_pct = (time_diff / baseline_avg_time) * 100 if baseline_avg_time > 0 else 0
    token_diff = variant_avg_tokens - baseline_avg_tokens

    print("\n📈 Comparison:")
    print(f"  Time difference: {time_diff:.3f}s ({time_diff_pct:+.1f}%)")
    print(f"  Token difference: {token_diff:.0f} tokens")
    print(f"  Entity detection: {sum(results['variant']['entities'])} entities found")
    print(f"  Chunk expansion: {sum(results['variant']['chunks'])} chunks added")

    # Success criteria check
    print("\n🎯 Success Criteria Check:")
    print(f"  Time overhead < 200ms: {'✅' if time_diff < 0.2 else '❌'} ({time_diff*1000:.1f}ms)")
    print(f"  Token overhead < 200: {'✅' if abs(token_diff) < 200 else '❌'} ({token_diff:.0f} tokens)")
    print(f"  Entity detection > 0: {'✅' if sum(results['variant']['entities']) > 0 else '❌'}")

    return results

if __name__ == "__main__":
    benchmark_entity_expansion()
