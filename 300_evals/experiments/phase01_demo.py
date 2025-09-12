#!/usr/bin/env python3
"""
Simple Phase 0/1 Component Demo

Tests individual components without full integration complexity.
"""

import sys
from pathlib import Path

# Add paths for our components
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_telemetry_logger():
    """Test the telemetry request logger."""
    print("🧪 Testing Telemetry Logger...")

    try:
        from telemetry.request_logger import CanaryTagger, RequestLog

        # Test canary tagger
        tagger = CanaryTagger(enabled=True, sample_pct=50)  # 50% for demo

        # Test some queries
        test_queries = ["What is DSPy?", "How does RAG work?", "Explain embeddings"]

        for query in test_queries:
            tag = tagger.get_tag(query)
            should_tag = tagger.should_tag_request(query)
            print(f"  Query: {query[:20]}... → Canary: {should_tag}, Tag: {tag}")

        # Test request log structure
        log_entry = RequestLog(query="Test query", answer="Test answer", confidence=0.85)

        print(f"  ✅ RequestLog created: {log_entry.request_id[:8]}...")
        return True

    except Exception as e:
        print(f"  ❌ Telemetry test failed: {e}")
        return False

def test_windowing():
    """Test document windowing."""
    print("🧪 Testing Document Windowing...")

    try:
        from retrieval.windowing import create_windower

        # Create windower
        windower = create_windower({"window_size_tokens": 50, "overlap_pct": 33})  # Small for demo

        # Test candidates
        test_candidates = [
            {
                "document_id": "doc1",
                "text": "This is a test document with multiple sentences. It contains information about DSPy and RAG systems. We want to test how the windowing works with overlapping segments. The system should create proper windows for retrieval.",
                "score": 0.8,
            },
            {"document_id": "doc2", "text": "Short doc.", "score": 0.6},
        ]

        # Create windows
        windows = windower.create_windows(test_candidates, max_windows_per_doc=3)

        print(f"  ✅ Created {len(windows)} windows from {len(test_candidates)} candidates")
        for window in windows:
            print(f"    {window.window_id}: {len(window.text)} chars, tokens {window.start_token}-{window.end_token}")

        return True

    except Exception as e:
        print(f"  ❌ Windowing test failed: {e}")
        return False

def test_deduplication():
    """Test near-duplicate suppression."""
    print("🧪 Testing Near-Duplicate Suppression...")

    try:
        from retrieval.deduplication import create_deduplicator

        # Create deduplicator
        deduplicator = create_deduplicator(
            {"method": "simple", "threshold": 0.9}  # Use simple hash method for reliability
        )

        # Test candidates with duplicates
        test_candidates = [
            {"id": "1", "text": "This is a test document about DSPy", "score": 0.9},
            {"id": "2", "text": "This is a different document about RAG", "score": 0.8},
            {"id": "3", "text": "This is a test document about DSPy", "score": 0.7},  # Exact duplicate
            {"id": "4", "text": "Another unique document about embeddings", "score": 0.6},
        ]

        # Filter duplicates
        filtered = deduplicator.filter_duplicates(test_candidates, text_field="text")

        print(f"  ✅ Filtered {len(test_candidates)} → {len(filtered)} candidates")
        print(f"    Removed {len(test_candidates) - len(filtered)} near-duplicates")

        return True

    except Exception as e:
        print(f"  ❌ Deduplication test failed: {e}")
        return False

def test_evaluation_metrics():
    """Test enhanced evaluation metrics."""
    print("🧪 Testing Enhanced Evaluation Metrics...")

    try:
        from evaluation.enhanced_metrics import (
            CoverageCalculator,
            ECECalculator,
            NDCGCalculator,
            SpanMatcher,
        )

        # Test NDCG
        relevances = [1.0, 0.8, 0.6, 0.4, 0.2]
        ideal = [1.0, 1.0, 0.8, 0.6, 0.4]
        ndcg = NDCGCalculator.ndcg(relevances, ideal, k=5)
        print(f"  NDCG@5: {ndcg:.3f}")

        # Test coverage
        sub_claims = ["DSPy is a framework", "DSPy optimizes prompts", "DSPy uses metrics"]
        retrieved_spans = [
            "DSPy is a powerful framework for optimization",
            "The system optimizes prompts automatically",
        ]
        coverage, supported = CoverageCalculator.calculate_coverage(sub_claims, retrieved_spans, threshold=0.3)
        print(f"  Coverage: {coverage:.3f} ({len(supported)}/{len(sub_claims)} claims supported)")

        # Test exact match
        exact = SpanMatcher.exact_match("DSPy framework", "dspy framework")
        print(f"  Exact Match: {exact}")

        # Test span support
        support = SpanMatcher.span_support("DSPy optimizes prompts", retrieved_spans)
        print(f"  Span Support: {support:.3f}")

        # Test ECE
        confidences = [0.9, 0.8, 0.7, 0.6, 0.5]
        correctness = [True, True, False, True, False]
        ece = ECECalculator.calculate_ece(confidences, correctness)
        print(f"  ECE: {ece:.3f}")

        print("  ✅ All metrics computed successfully")
        return True

    except Exception as e:
        print(f"  ❌ Evaluation metrics test failed: {e}")
        return False

def test_golden_queries():
    """Test loading golden query sets."""
    print("🧪 Testing Golden Query Loading...")

    try:
        from evaluation.enhanced_metrics import load_golden_queries

        # Test loading golden queries
        golden_files = [
            "configs/eval/golden/novice_expert_queries.jsonl",
            "configs/eval/golden/hop_complexity_queries.jsonl",
        ]

        total_queries = 0
        for file_path in golden_files:
            if Path(file_path).exists():
                queries = load_golden_queries(file_path)
                total_queries += len(queries)
                print(f"  Loaded {len(queries)} queries from {Path(file_path).name}")

                # Show first query structure
                if queries:
                    first_query = queries[0]
                    print(f"    Sample: {first_query.query[:50]}...")
                    print(f"    Tags: {first_query.slice_tags}")
                    print(f"    Sub-claims: {len(first_query.sub_claims)}")

        print(f"  ✅ Loaded {total_queries} total golden queries")
        return total_queries > 0

    except Exception as e:
        print(f"  ❌ Golden queries test failed: {e}")
        return False

def main():
    """Run all component tests."""
    print("🚀 Phase 0/1 Component Demonstration")
    print("=" * 50)

    results = {
        "Telemetry Logger": test_telemetry_logger(),
        "Document Windowing": test_windowing(),
        "Near-Dup Suppression": test_deduplication(),
        "Evaluation Metrics": test_evaluation_metrics(),
        "Golden Query Sets": test_golden_queries(),
    }

    print("\n📊 Test Results:")
    print("-" * 30)

    passed = 0
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{component:<25} {status}")
        if success:
            passed += 1

    print(f"\n🎯 Summary: {passed}/{len(results)} components working")

    if passed == len(results):
        print("🎉 All Phase 0/1 components are functional!")
        print("Ready for integration and canary deployment.")
    else:
        print("⚠️  Some components need attention before full integration.")

    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
