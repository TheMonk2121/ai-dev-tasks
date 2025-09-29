from __future__ import annotations

import os
import sys
from pathlib import Path

from ragchecker_precision_climb_v2_evaluation import PrecisionClimbV2Evaluator
from sentence_transformers import CrossEncoder

from cross_encoder_reranker import CrossEncoderReranker, EnhancedEvidenceFilter

#!/usr/bin/env python3
"""
Test Cross-Encoder Integration with Precision-Climb v2

Tests the cross-encoder reranking integration with the precision-climb evaluation system.
"""

# Add the precision climb config
sys.path.insert(0, str(Path(__file__).parent))

def test_cross_encoder_availability():
    """Test if cross-encoder components are available."""
    print("🧪 Testing Cross-Encoder Availability")
    print("=" * 50)

    # Test cross-encoder reranker
    try:

        print("✅ Cross-encoder reranker imported successfully")

        # Test initialization
        CrossEncoderReranker()
        print("✅ Cross-encoder reranker initialized")

        # Test enhanced filter
        EnhancedEvidenceFilter()
        print("✅ Enhanced evidence filter initialized")

        return True
    except ImportError as e:
        print(f"❌ Cross-encoder import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Cross-encoder initialization failed: {e}")
        return False

def test_sentence_transformers():
    """Test if sentence-transformers is available."""
    print("\n🧪 Testing Sentence-Transformers")
    print("=" * 50)

    try:

        print("✅ sentence-transformers imported successfully")

        # Test model loading
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        print("✅ Cross-encoder model loaded successfully")

        # Test prediction
        score = model.predict([("test query", "test candidate")])[0]
        print(f"✅ Cross-encoder prediction works: {score:.3f}")

        return True
    except ImportError as e:
        print(f"❌ sentence-transformers not available: {e}")
        print("💡 Install with: pip install sentence-transformers")
        return False
    except Exception as e:
        print(f"❌ Cross-encoder model loading failed: {e}")
        return False

def test_precision_climb_integration():
    """Test precision-climb integration with cross-encoder."""
    print("\n🧪 Testing Precision-Climb Integration")
    print("=" * 50)

    try:

        print("✅ Precision-climb evaluator imported successfully")

        # Test evaluator initialization
        evaluator = PrecisionClimbV2Evaluator()
        print("✅ Precision-climb evaluator initialized")

        # Test cross-encoder availability
        if evaluator.cross_encoder:
            print("✅ Cross-encoder available in evaluator")
        else:
            print("⚠️ Cross-encoder not available in evaluator")

        if evaluator.enhanced_filter:
            print("✅ Enhanced filter available in evaluator")
        else:
            print("⚠️ Enhanced filter not available in evaluator")

        return True
    except ImportError as e:
        print(f"❌ Precision-climb import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Precision-climb initialization failed: {e}")
        return False

def test_cross_encoder_functionality():
    """Test cross-encoder functionality."""
    print("\n🧪 Testing Cross-Encoder Functionality")
    print("=" * 50)

    # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    try:

        reranker = CrossEncoderReranker()

        # Test data
        query = "What is the memory system architecture?"
        candidates = [
            "The memory system uses a three-tier architecture with SQL, pgvector, and knowledge graph storage.",
            "Memory rehydration is handled by the unified orchestrator.",
            "The system supports both local and cloud-based memory storage.",
            "Cross-encoder reranking improves precision by reranking top candidates.",
        ]
        contexts = [
            "The memory system architecture consists of three main components: SQL database for structured data, pgvector for semantic embeddings, and knowledge graph for relational information.",
            "Memory rehydration is a critical process that restores context from previous sessions using the unified memory orchestrator.",
        ]

        # Test reranking
        reranked = reranker.rerank_candidates(query, candidates, contexts)

        print("📊 Reranking Results:")
        for i, (candidate, score) in enumerate(reranked, 1):
            print(f"  {i}. Score: {score:.3f} - {candidate[:60]}...")

        # Test cache stats
        stats = reranker.get_cache_stats()
        print(f"\n📊 Cache Stats: {stats['cache_size']} entries")

        return True
    except Exception as e:
        print(f"❌ Cross-encoder functionality test failed: {e}")
        return False

def test_enhanced_filtering():
    """Test enhanced filtering with cross-encoder."""
    print("\n🧪 Testing Enhanced Filtering")
    print("=" * 50)

    # Enable cross-encoder
    os.environ["RAGCHECKER_CROSS_ENCODER_ENABLED"] = "1"

    try:

        enhanced_filter = EnhancedEvidenceFilter()

        # Test data
        answer = "The memory system uses a three-tier architecture. Memory rehydration is handled by the unified orchestrator. The system supports both local and cloud-based storage. Cross-encoder reranking improves precision."
        contexts = [
            "The memory system architecture consists of three main components: SQL database for structured data, pgvector for semantic embeddings, and knowledge graph for relational information.",
            "Memory rehydration is a critical process that restores context from previous sessions using the unified memory orchestrator.",
        ]
        query = "What is the memory system architecture?"

        # Test filtering
        filtered = enhanced_filter.filter_with_cross_encoder(answer, contexts, query)

        print(f"📝 Original: {len(answer)} chars")
        print(f"📝 Filtered: {len(filtered)} chars")
        print(f"📝 Filtered text: {filtered[:200]}...")

        return True
    except Exception as e:
        print(f"❌ Enhanced filtering test failed: {e}")
        return False

def main():
    """Run all cross-encoder integration tests."""
    print("🚀 Cross-Encoder Integration Test Suite")
    print("=" * 60)

    tests = [
        ("Cross-Encoder Availability", test_cross_encoder_availability),
        ("Sentence-Transformers", test_sentence_transformers),
        ("Precision-Climb Integration", test_precision_climb_integration),
        ("Cross-Encoder Functionality", test_cross_encoder_functionality),
        ("Enhanced Filtering", test_enhanced_filtering),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Cross-encoder integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
