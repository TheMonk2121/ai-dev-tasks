#!/usr/bin/env python3.12.123.11
"""
Vector Store Performance Benchmark
Tests the optimized vector store with various scenarios
"""

import statistics
import time
import uuid

from src.dspy_modules.vector_store import HybridVectorStore

# Test configuration
CONNECTION_STRING = "postgresql://danieljacobs@localhost:5432/ai_agency"
TEST_DOCUMENTS = [
    {
        "content": (
            "Machine learning is a subset of artificial intelligence that enables "
            "computers to learn without being explicitly programmed."
        ),
        "metadata": {"source": "ml_intro", "category": "technology"},
    },
    {
        "content": "Deep learning uses neural networks with multiple layers to model complex patterns in data.",
        "metadata": {"source": "deep_learning", "category": "technology"},
    },
    {
        "content": "Natural language processing helps computers understand and generate human language.",
        "metadata": {"source": "nlp_basics", "category": "technology"},
    },
    {
        "content": "Vector databases store and retrieve high-dimensional vectors for similarity search.",
        "metadata": {"source": "vector_db", "category": "database"},
    },
    {
        "content": "PostgreSQL with pgvector extension provides efficient vector similarity search capabilities.",
        "metadata": {"source": "pgvector", "category": "database"},
    },
]


def benchmark_insertion(
    store: HybridVectorStore, documents: list[dict[str, Any]]
) -> dict[str, float]:
    """Benchmark document insertion performance"""
    print("🔧 Benchmarking document insertion...")

    start_time = time.time()
    insertion_times = []

    for i, doc in enumerate(documents):
        doc_start = time.time()

        # Create unique document ID
        doc_id = str(uuid.uuid4())

        # Insert document using forward method
        # Split content into chunks (simple split by sentences for demo)
        chunks = [doc["content"]]  # For now, treat entire content as one chunk
        metadata = {**doc["metadata"], "document_id": doc_id}
        result = store.forward(
            operation="store_chunks", chunks=chunks, metadata=metadata
        )

        # Verify insertion was successful
        if result.get("status") != "success":
            print(f"  ⚠️  Document {i+1}: Insertion failed - {result}")

        doc_time = time.time() - doc_start
        insertion_times.append(doc_time)

        print(f"  Document {i+1}: {doc_time:.3f}s")

    total_time = time.time() - start_time

    return {
        "total_time": total_time,
        "avg_time": statistics.mean(insertion_times),
        "min_time": min(insertion_times),
        "max_time": max(insertion_times),
        "documents_inserted": len(documents),
    }


def benchmark_vector_search(
    store: HybridVectorStore, queries: list[str]
) -> dict[str, float]:
    """Benchmark vector search performance"""
    print("🔍 Benchmarking vector search...")

    search_times = []

    for i, query in enumerate(queries):
        start_time = time.time()

        # Perform vector search
        results = store._vector_search(query, limit=5)

        search_time = time.time() - start_time
        search_times.append(search_time)

        print(f"  Query {i+1} ('{query}'): {search_time:.3f}s, {len(results)} results")

    return {
        "avg_time": statistics.mean(search_times),
        "min_time": min(search_times),
        "max_time": max(search_times),
        "queries_executed": len(queries),
    }


def benchmark_hybrid_search(
    store: HybridVectorStore, queries: list[str]
) -> dict[str, float]:
    """Benchmark hybrid search performance"""
    print("🔄 Benchmarking hybrid search...")

    search_times = []

    for i, query in enumerate(queries):
        start_time = time.time()

        # Perform hybrid search
        results = store._hybrid_search(query, limit=5)

        search_time = time.time() - start_time
        search_times.append(search_time)

        print(f"  Query {i+1} ('{query}'): {search_time:.3f}s, {len(results)} results")

    return {
        "avg_time": statistics.mean(search_times),
        "min_time": min(search_times),
        "max_time": max(search_times),
        "queries_executed": len(queries),
    }


def benchmark_cache_performance(
    store: HybridVectorStore, repeated_query: str
) -> dict[str, float]:
    """Benchmark query embedding cache performance"""
    print("💾 Benchmarking cache performance...")

    # First query (cache miss)
    start_time = time.time()
    _ = store._vector_search(
        repeated_query, limit=5
    )  # Use underscore to indicate intentionally unused
    first_query_time = time.time() - start_time

    # Second query (cache hit)
    start_time = time.time()
    _ = store._vector_search(
        repeated_query, limit=5
    )  # Use underscore to indicate intentionally unused
    second_query_time = time.time() - start_time

    cache_speedup = (
        first_query_time / second_query_time if second_query_time > 0 else float("inf")
    )

    print(f"  First query (cache miss): {first_query_time:.3f}s")
    print(f"  Second query (cache hit): {second_query_time:.3f}s")
    print(f"  Cache speedup: {cache_speedup:.1f}x")

    return {
        "cache_miss_time": first_query_time,
        "cache_hit_time": second_query_time,
        "speedup": cache_speedup,
    }


def main():
    """Run comprehensive benchmark"""
    print("🚀 Starting Vector Store Performance Benchmark")
    print("=" * 50)

    # Initialize vector store
    store = HybridVectorStore(CONNECTION_STRING)

    # Test queries
    test_queries = [
        "machine learning algorithms",
        "neural networks and deep learning",
        "natural language processing techniques",
        "vector database performance",
        "PostgreSQL vector search",
    ]

    # Run benchmarks
    print("\n📊 Running Benchmarks...")

    # 1. Insertion benchmark
    insertion_results = benchmark_insertion(store, TEST_DOCUMENTS)

    # 2. Vector search benchmark
    vector_results = benchmark_vector_search(store, test_queries)

    # 3. Hybrid search benchmark
    hybrid_results = benchmark_hybrid_search(store, test_queries)

    # 4. Cache performance benchmark
    cache_results = benchmark_cache_performance(store, "machine learning")

    # Print summary
    print("\n" + "=" * 50)
    print("📈 BENCHMARK SUMMARY")
    print("=" * 50)

    print("\n📝 Document Insertion:")
    print(f"  Total time: {insertion_results['total_time']:.3f}s")
    print(f"  Average per document: {insertion_results['avg_time']:.3f}s")
    print(f"  Documents inserted: {insertion_results['documents_inserted']}")

    print("\n🔍 Vector Search:")
    print(f"  Average query time: {vector_results['avg_time']:.3f}s")
    print(f"  Fastest query: {vector_results['min_time']:.3f}s")
    print(f"  Slowest query: {vector_results['max_time']:.3f}s")
    print(f"  Queries executed: {vector_results['queries_executed']}")

    print("\n🔄 Hybrid Search:")
    print(f"  Average query time: {hybrid_results['avg_time']:.3f}s")
    print(f"  Fastest query: {hybrid_results['min_time']:.3f}s")
    print(f"  Slowest query: {hybrid_results['max_time']:.3f}s")
    print(f"  Queries executed: {hybrid_results['queries_executed']}")

    print("\n💾 Cache Performance:")
    print(f"  Cache miss time: {cache_results['cache_miss_time']:.3f}s")
    print(f"  Cache hit time: {cache_results['cache_hit_time']:.3f}s")
    print(f"  Speedup: {cache_results['speedup']:.1f}x")

    # Performance assessment
    print("\n🎯 Performance Assessment:")
    if vector_results["avg_time"] < 0.1:
        print("  ✅ Vector search: EXCELLENT (< 100ms)")
    elif vector_results["avg_time"] < 0.5:
        print("  ✅ Vector search: GOOD (< 500ms)")
    else:
        print("  ⚠️  Vector search: NEEDS OPTIMIZATION (> 500ms)")

    if hybrid_results["avg_time"] < 0.2:
        print("  ✅ Hybrid search: EXCELLENT (< 200ms)")
    elif hybrid_results["avg_time"] < 1.0:
        print("  ✅ Hybrid search: GOOD (< 1s)")
    else:
        print("  ⚠️  Hybrid search: NEEDS OPTIMIZATION (> 1s)")

    if cache_results["speedup"] > 2.0:
        print("  ✅ Cache performance: EXCELLENT (> 2x speedup)")
    elif cache_results["speedup"] > 1.5:
        print("  ✅ Cache performance: GOOD (> 1.5x speedup)")
    else:
        print("  ⚠️  Cache performance: NEEDS INVESTIGATION")

    print("\n✅ Benchmark completed successfully!")


if __name__ == "__main__":
    main()
