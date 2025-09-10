#!/usr/bin/env python3
"""
Test Enhanced Retrieval Pipeline and Answer Generator
"""

import sys
from pathlib import Path

# Add the dspy-rag-system src to path
# sys.path.insert(0, str(Path(__file__).parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project
from dspy_modules.enhanced_answer_generator import create_enhanced_generator
from dspy_modules.retrieval_pipeline import create_enhanced_pipeline


def test_enhanced_pipeline():
    """Test the enhanced retrieval pipeline"""

    print("🧪 Testing Enhanced Retrieval Pipeline")
    print("=" * 50)

    # Create enhanced pipeline
    pipeline = create_enhanced_pipeline(
        max_tokens=300, overlap_tokens=64, bm25_weight=0.55, dense_weight=0.35, metadata_weight=0.10
    )

    print("✅ Enhanced pipeline created")
    print(f"📊 Pipeline stats: {pipeline.get_pipeline_stats()}")

    # Test query classification
    test_queries = [
        "How do I implement a DSPy module?",
        "What is the architecture of the system?",
        "How do I fix this error?",
        "Explain the performance optimization",
    ]

    print("\n🔍 Testing query classification:")
    for query in test_queries:
        query_type = pipeline._classify_query(query)
        print(f"  '{query}' → {query_type}")

    return pipeline


def test_enhanced_generator():
    """Test the enhanced answer generator"""

    print("\n🧪 Testing Enhanced Answer Generator")
    print("=" * 50)

    # Create enhanced generator
    generator = create_enhanced_generator(
        min_citations=2, max_answer_length=500, enable_abstention=True, code_formatting=True
    )

    print("✅ Enhanced generator created")
    print(f"📊 Generator stats: {generator.get_generator_stats()}")

    # Test context validation
    print("\n🔍 Testing context validation:")

    # Insufficient context
    insufficient_chunks = [{"chunk_id": "test_1", "text": "Short text"}]
    has_context = generator._has_sufficient_context(insufficient_chunks)
    print(f"  Insufficient context: {has_context}")

    # Sufficient context
    sufficient_chunks = [
        {
            "chunk_id": "test_1",
            "text": "This is a longer text that provides sufficient context for answering the question.",
        },
        {"chunk_id": "test_2", "text": "Another chunk with additional information to support the answer."},
    ]
    has_context = generator._has_sufficient_context(sufficient_chunks)
    print(f"  Sufficient context: {has_context}")

    return generator


def test_integration():
    """Test pipeline and generator integration"""

    print("\n🧪 Testing Integration")
    print("=" * 50)

    create_enhanced_pipeline()
    generator = create_enhanced_generator()

    # Mock retrieval results (since we don't have real BM25/dense retrievers)
    mock_chunks = [
        {
            "chunk_id": "code_chunk_1",
            "text": 'def create_dspy_module(name: str):\n    """Create a DSPy module"""\n    return DSPyModule(name)',
            "chunk_type": "code_function",
            "score": 0.9,
            "metadata": {"is_complete_function": True, "stitching_key": "func_create_dspy_module"},
        },
        {
            "chunk_id": "doc_chunk_1",
            "text": "DSPy modules are the core building blocks of the framework. They encapsulate logic and can be composed together.",
            "chunk_type": "markdown_section",
            "score": 0.8,
            "metadata": {"is_complete_section": True, "stitching_key": "md_dspy_modules"},
        },
    ]

    # Test answer generation
    query = "How do I implement a DSPy module?"
    query_type = "implementation"

    print(f"🔍 Testing answer generation for: {query}")
    print(f"📊 Query type: {query_type}")
    print(f"📦 Retrieved chunks: {len(mock_chunks)}")

    # Generate answer
    result = generator.generate_enhanced_answer(query, mock_chunks, query_type)

    print("\n📝 Generated answer:")
    print("-" * 40)
    print(result["answer"])
    print("-" * 40)

    print("\n✅ Validation:")
    print(f"  Citations: {result['validation']['citations_count']}")
    print(f"  Sufficient context: {result['validation']['has_sufficient_context']}")
    print(f"  Meets citation requirement: {result['validation']['meets_citation_requirement']}")

    return result


def main():
    """Main test function"""

    try:
        print("🚀 Testing Enhanced RAG Pipeline Components")
        print("=" * 60)

        # Test individual components
        test_enhanced_pipeline()
        generator = test_enhanced_generator()

        # Test integration
        result = test_integration()

        print("\n🎯 Test Results Summary")
        print("=" * 30)
        print("✅ Enhanced pipeline: Working")
        print("✅ Enhanced generator: Working")
        print("✅ Integration: Working")
        print(f"✅ Answer quality: {result['validation']['meets_citation_requirement']}")
        print(f"✅ Citations: {result['validation']['citations_count']}/{generator.min_citations}")

        print("\n🚀 Ready for RAGChecker evaluation!")
        print("Expected improvements:")
        print("  - Better code-aware chunking")
        print("  - Structured answers with citations")
        print("  - Abstention for poor context")
        print("  - F1 target: 17.1% → 20.0%+")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
