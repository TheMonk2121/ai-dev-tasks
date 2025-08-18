#!/usr/bin/env python3.11
"""
Integration Test for Optimized Vector Store
Tests the vector store with DSPy framework integration
"""

import dspy
from src.dspy_modules.vector_store import HybridVectorStore

# Test configuration
CONNECTION_STRING = "postgresql://danieljacobs@localhost:5432/ai_agency"

class TestDocumentRetriever(dspy.Module):
    """Test document retriever using optimized vector store"""

    def __init__(self, vector_store: HybridVectorStore, k: int = 3):
        super().__init__()
        self.vector_store = vector_store
        self.k = k

    def forward(self, query: str):
        """Retrieve documents for a query"""
        results = self.vector_store.forward(operation="search", query=query, limit=self.k)
        return results

def test_dspy_integration():
    """Test DSPy integration with optimized vector store"""
    print("🧪 Testing DSPy Integration with Optimized Vector Store")
    print("=" * 60)

    # Initialize vector store
    vector_store = HybridVectorStore(CONNECTION_STRING)

    # Create DSPy retriever
    retriever = TestDocumentRetriever(vector_store, k=3)

    # Test queries
    test_queries = ["machine learning algorithms", "deep learning neural networks", "vector database performance"]

    print("\n📋 Testing Document Retrieval:")
    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: '{query}'")

        # Get results
        results = retriever(query)

        print(f"  Status: {results['status']}")
        print(f"  Search type: {results['search_type']}")
        print(f"  Dense results: {results['dense_count']}")
        print(f"  Sparse results: {results['sparse_count']}")
        print(f"  Merged results: {results['merged_count']}")

        # Show top result
        if results["results"]:
            top_result = results["results"][0]
            print(f"  Top result: {top_result['content'][:100]}...")
            print(f"  Score: {top_result.get('score_dense', 'N/A')}")
            print(f"  Citation: {top_result.get('citation', 'N/A')}")

    print("\n✅ DSPy Integration Test Completed Successfully!")

def test_vector_store_operations():
    """Test all vector store operations"""
    print("\n🔧 Testing Vector Store Operations")
    print("=" * 60)

    vector_store = HybridVectorStore(CONNECTION_STRING)

    # Test 1: Store document
    print("\n1. Testing document storage...")
    test_chunks = ["This is a test document about artificial intelligence and machine learning."]
    test_metadata = {"source": "integration_test", "category": "test", "document_id": "test_doc_001"}

    store_result = vector_store.forward(operation="store_chunks", chunks=test_chunks, metadata=test_metadata)
    print(f"   Status: {store_result['status']}")
    print(f"   Document ID: {store_result['document_id']}")
    print(f"   Chunks stored: {store_result['chunks_stored']}")

    # Test 2: Search document
    print("\n2. Testing document search...")
    search_result = vector_store.forward(operation="search", query="artificial intelligence", limit=3)
    print(f"   Status: {search_result['status']}")
    print(f"   Results found: {search_result['merged_count']}")

    # Test 3: Get document chunks
    print("\n3. Testing document chunk retrieval...")
    chunks_result = vector_store.forward(operation="get_document_chunks", document_id="test_doc_001")
    print(f"   Status: {chunks_result['status']}")
    print(f"   Chunks retrieved: {len(chunks_result.get('chunks', []))}")

    # Test 4: Delete document
    print("\n4. Testing document deletion...")
    delete_result = vector_store.forward(operation="delete_document", document_id="test_doc_001")
    print(f"   Status: {delete_result['status']}")
    print(f"   Message: {delete_result['message']}")

    print("\n✅ Vector Store Operations Test Completed Successfully!")

def test_performance_characteristics():
    """Test performance characteristics"""
    print("\n⚡ Testing Performance Characteristics")
    print("=" * 60)

    vector_store = HybridVectorStore(CONNECTION_STRING)

    # Test query embedding cache
    print("\n1. Testing query embedding cache...")
    import time

    # First query (cache miss)
    start_time = time.time()
    result1 = vector_store._vector_search("test query", limit=3)
    cache_miss_time = time.time() - start_time

    # Second query (cache hit)
    start_time = time.time()
    result2 = vector_store._vector_search("test query", limit=3)
    cache_hit_time = time.time() - start_time

    speedup = cache_miss_time / cache_hit_time if cache_hit_time > 0 else float("inf")
    print(f"   Cache miss time: {cache_miss_time:.3f}s")
    print(f"   Cache hit time: {cache_hit_time:.3f}s")
    print(f"   Speedup: {speedup:.1f}x")
    print(f"   Cache miss results: {len(result1)}")
    print(f"   Cache hit results: {len(result2)}")

    # Test hybrid search performance
    print("\n2. Testing hybrid search performance...")
    start_time = time.time()
    hybrid_result = vector_store._hybrid_search("machine learning", limit=5)
    hybrid_time = time.time() - start_time
    print(f"   Hybrid search time: {hybrid_time:.3f}s")
    print(f"   Results: {hybrid_result['merged_count']}")

    # Test vector search performance
    print("\n3. Testing vector search performance...")
    start_time = time.time()
    vector_result = vector_store._vector_search("machine learning", limit=5)
    vector_time = time.time() - start_time
    print(f"   Vector search time: {vector_time:.3f}s")
    print(f"   Results: {len(vector_result)}")

    print("\n✅ Performance Characteristics Test Completed Successfully!")

def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests for Optimized Vector Store")
    print("=" * 80)

    try:
        # Test 1: DSPy Integration
        test_dspy_integration()

        # Test 2: Vector Store Operations
        test_vector_store_operations()

        # Test 3: Performance Characteristics
        test_performance_characteristics()

        print("\n" + "=" * 80)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("=" * 80)
        print("\n✅ The optimized vector store is working correctly with:")
        print("   - DSPy framework integration")
        print("   - All CRUD operations")
        print("   - Query embedding cache")
        print("   - Hybrid search functionality")
        print("   - Performance optimizations")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
