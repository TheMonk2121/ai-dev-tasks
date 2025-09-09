# DEPRECATED: This demo file is being archived. See 400_guides/ for essential examples.
#!/usr/bin/env python3
"""
Vector Database Foundation Enhancement Demo
Demonstrates the enhanced vector database capabilities including:
- Performance monitoring
- Caching
- Health checks
- Index management
- Optimization recommendations
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from dspy_modules.enhanced_vector_store import EnhancedVectorStore
from utils.logger import get_logger

logger = get_logger(__name__)


def demo_vector_enhancement():
    """Demonstrate vector database foundation enhancement capabilities"""

    # Initialize enhanced vector store
    db_connection = os.environ.get("POSTGRES_DSN")
    if not db_connection:
        logger.error("POSTGRES_DSN environment variable not set")
        return False

    vector_store = EnhancedVectorStore(db_connection)

    print("🚀 Vector Database Foundation Enhancement Demo")
    print("=" * 60)

    # 1. Health Status Check
    print("\n📊 1. Health Status Check")
    print("-" * 30)
    health = vector_store.get_health_status()
    print(f"Total Documents: {health.get('total_documents', 0)}")
    print(f"Total Chunks: {health.get('total_chunks', 0)}")
    print(f"Cache Entries: {health.get('cache_entries', 0)}")
    print(f"Performance Metrics: {health.get('performance_metrics', 0)}")
    print(f"Cache Cleanup Needed: {health.get('cache_cleanup_needed', 0)}")

    # 2. Performance Optimization
    print("\n⚡ 2. Performance Optimization")
    print("-" * 30)
    optimization = vector_store.optimize_performance()

    if optimization.get("index_creation"):
        print("📈 Index Creation Recommendations:")
        for index in optimization["index_creation"]:
            print(f"  - Create {index['type']} index on {index['table']}.{index['column']}")
            print(f"    Reason: {index['reason']}")

            # Create the recommended index
            success = vector_store.create_vector_index(index["table"], index["column"], index["type"])
            if success:
                print("    ✅ Successfully created index")
            else:
                print("    ❌ Failed to create index")

    if optimization.get("performance_issues"):
        print("⚠️  Performance Issues:")
        for issue in optimization["performance_issues"]:
            print(f"  - {issue['operation']}: {issue['suggestion']}")

    # 3. Simulate Document Addition
    print("\n📄 3. Simulate Document Addition")
    print("-" * 30)

    # Create sample documents with embeddings
    sample_documents = [
        {
            "filename": "sample_doc_1.txt",
            "file_path": "/path/to/sample_doc_1.txt",
            "file_type": "text",
            "file_size": 1024,
            "chunks": [
                {
                    "content": "This is a sample document about artificial intelligence and machine learning.",
                    "embedding": [0.1] * 384,  # Simplified embedding
                    "metadata": {"chunk_type": "text", "source": "sample"},
                },
                {
                    "content": "Machine learning algorithms can process large amounts of data efficiently.",
                    "embedding": [0.2] * 384,  # Simplified embedding
                    "metadata": {"chunk_type": "text", "source": "sample"},
                },
            ],
        },
        {
            "filename": "sample_doc_2.txt",
            "file_path": "/path/to/sample_doc_2.txt",
            "file_type": "text",
            "file_size": 2048,
            "chunks": [
                {
                    "content": "Vector databases are essential for modern AI applications.",
                    "embedding": [0.3] * 384,  # Simplified embedding
                    "metadata": {"chunk_type": "text", "source": "sample"},
                }
            ],
        },
    ]

    success = vector_store.add_documents(sample_documents)
    if success:
        print("✅ Successfully added sample documents")
    else:
        print("❌ Failed to add sample documents")

    # 4. Simulate Similarity Search
    print("\n🔍 4. Simulate Similarity Search")
    print("-" * 30)

    # Create sample query embedding
    query_embedding = [0.15] * 384  # Simplified embedding

    # First search (should be slower, no cache)
    print("Performing first search (no cache)...")
    start_time = time.time()
    results = vector_store.similarity_search(query_embedding, top_k=3)
    first_search_time = time.time() - start_time

    print(f"First search completed in {first_search_time:.3f}s")
    print(f"Found {len(results)} results")

    # Second search (should be faster, with cache)
    print("\nPerforming second search (with cache)...")
    start_time = time.time()
    results = vector_store.similarity_search(query_embedding, top_k=3)
    second_search_time = time.time() - start_time

    print(f"Second search completed in {second_search_time:.3f}s")
    print(f"Found {len(results)} results")

    if second_search_time < first_search_time:
        print(
            f"✅ Cache improved performance by {((first_search_time - second_search_time) / first_search_time * 100):.1f}%"
        )
    else:
        print("⚠️  Cache didn't improve performance (expected for small datasets)")

    # 5. Performance Metrics
    print("\n📈 5. Performance Metrics")
    print("-" * 30)

    metrics = vector_store.get_performance_metrics(hours=1)
    if metrics:
        for metric in metrics:
            print(f"Operation: {metric['operation_type']}")
            print(f"  Average Time: {metric['avg_execution_time_ms']:.2f}ms")
            print(f"  Max Time: {metric['max_execution_time_ms']}ms")
            print(f"  Operations: {metric['operation_count']}")
            print(f"  Cache Hit Rate: {metric['cache_hit_rate']:.2%}")
            print()
    else:
        print("No performance metrics available yet")

    # 6. Updated Health Status
    print("\n🏥 6. Updated Health Status")
    print("-" * 30)

    health = vector_store.get_health_status()
    print(f"Total Documents: {health.get('total_documents', 0)}")
    print(f"Total Chunks: {health.get('total_chunks', 0)}")
    print(f"Cache Entries: {health.get('cache_entries', 0)}")
    print(f"Performance Metrics: {health.get('performance_metrics', 0)}")

    # 7. Final Optimization Check
    print("\n🎯 7. Final Optimization Check")
    print("-" * 30)

    optimization = vector_store.optimize_performance()
    if optimization.get("performance_issues"):
        print("Performance Issues Found:")
        for issue in optimization["performance_issues"]:
            print(f"  - {issue['operation']}: {issue['suggestion']}")
    else:
        print("✅ No performance issues detected")

    print("\n🎉 Vector Database Foundation Enhancement Demo Complete!")
    print("=" * 60)

    return True


def main():
    """Main function"""
    try:
        success = demo_vector_enhancement()
        return success
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
