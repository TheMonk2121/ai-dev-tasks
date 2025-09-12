from __future__ import annotations
import os
import sys
from pathlib import Path
        from dspy_modules.retriever.reranker_torch import get_model_info, is_available
        from dspy_modules.retriever.reranker_torch import rerank
        from dspy_modules.retriever.reranker_config import apply_reranker_config, load_reranker_config
        from dspy_modules.rag_pipeline import _load_reranker
#!/usr/bin/env python3
"""
Test script for PyTorch reranker integration.
Verifies that the reranker can be loaded and used correctly.
"""

# Add DSPy RAG system to path
dspy_rag_path = os.getenv("DSPY_RAG_PATH", "src")
if dspy_rag_path and dspy_rag_path not in sys.path:
    sys.path.insert(0, dspy_rag_path)

def test_reranker_availability():
    """Test if the reranker is available"""
    print("🧪 Testing reranker availability...")

    try:

        available = is_available()
        print(f"✅ Reranker available: {available}")

        if available:
            info = get_model_info()
            print(f"📊 Model info: {info}")
        else:
            print("⚠️ Reranker not available - dependencies may be missing")
            print("   Install with: pip install torch sentence-transformers")

        return available
    except Exception as e:
        print(f"❌ Error testing reranker availability: {e}")
        return False

def test_reranker_functionality():
    """Test basic reranker functionality"""
    print("\n🧪 Testing reranker functionality...")

    try:

        # Test data
        query = "How to implement a retriever?"
        candidates = [
            ("chunk1", "This is about implementing a retriever system with vector search."),
            ("chunk2", "The weather is nice today and the sun is shining."),
            ("chunk3", "A retriever implementation requires proper indexing and query processing."),
            ("chunk4", "Cooking recipes for pasta and Italian cuisine."),
            ("chunk5", "Retriever systems use embeddings and similarity search algorithms."),
        ]

        print(f"🔍 Query: {query}")
        print(f"📝 Candidates: {len(candidates)}")

        # Test reranking
        results = rerank(query, candidates, topk_keep=3, batch_size=2)

        print(f"✅ Reranking completed: {len(results)} results")
        for i, (chunk_id, text, score) in enumerate(results):
            print(f"  {i+1}. {chunk_id}: {score:.3f} - {text[:50]}...")

        return True

    except Exception as e:
        print(f"❌ Error testing reranker functionality: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("\n🧪 Testing configuration loading...")

    try:

        # Test default config
        config = load_reranker_config()
        print(f"✅ Default config loaded: {config}")

        # Test tag-specific config
        tag_config = load_reranker_config("rag_qa_single")
        print(f"✅ Tag config loaded: {tag_config}")

        # Test applying config
        apply_reranker_config(config)
        print("✅ Config applied to environment")

        return True

    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def test_pipeline_integration():
    """Test integration with the retrieval pipeline"""
    print("\n🧪 Testing pipeline integration...")

    try:
        # Test if the pipeline can load the reranker

        reranker = _load_reranker()
        if reranker is not None:
            print("✅ Pipeline can load reranker")
            return True
        else:
            print("⚠️ Pipeline could not load reranker")
            return False

    except Exception as e:
        print(f"❌ Error testing pipeline integration: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PyTorch Reranker Integration Test")
    print("=" * 50)

    tests = [
        ("Availability", test_reranker_availability),
        ("Functionality", test_reranker_functionality),
        ("Configuration", test_config_loading),
        ("Pipeline Integration", test_pipeline_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False

    print("\n📊 Test Results:")
    print("=" * 30)

    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False

    print(f"\n🎯 Overall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")

    if not all_passed:
        print("\n💡 Troubleshooting:")
        print("1. Install dependencies: pip install torch sentence-transformers")
        print("2. Check environment variables: RERANKER_MODEL, TORCH_DEVICE")
        print("3. Verify config files exist: configs/retriever_weights.yaml")

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)