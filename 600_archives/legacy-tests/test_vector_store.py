#!/usr/bin/env python3
"""
Comprehensive test suite for VectorStore module
Based on deep research analysis with all critical fixes
"""

# Import our VectorStore
import os
import time
import uuid

import numpy as np
import psycopg2
import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from src.dspy_modules.vector_store import HybridVectorStore, _get_model

# Test database configuration
POSTGRES_DSN = os.getenv("PG_DSN_TEST", "postgresql://danieljacobs@localhost:5432/ai_agency")


@pytest.fixture(scope="session")
def db_conn():
    """Create test database connection with pgvector setup"""
    try:
        conn = psycopg2.connect(POSTGRES_DSN)

        # Try to register pgvector adapter
        try:
            from pgvector.psycopg2 import register_vector

            register_vector(conn)
        except ImportError:
            print("Warning: pgvector not installed, some tests may fail")

        cur = conn.cursor()

        # Create minimal schema for testing
        cur.execute(
            """
            CREATE EXTENSION IF NOT EXISTS pgvector;

            CREATE TABLE IF NOT EXISTS documents (
                document_id text primary key,
                filename text,
                file_type text,
                file_size int,
                chunk_count int,
                metadata jsonb,
                updated_at timestamp default now()
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
                document_id text,
                chunk_index int,
                content text,
                embedding vector(384),
                primary key (document_id, chunk_index)
            );

            CREATE INDEX IF NOT EXISTS doc_chunks_embedding
            ON document_chunks USING ivfflat (embedding vector_l2_ops)
            WITH (lists = 100);
        """
        )
        conn.commit()

        yield conn

        # Cleanup
        cur.execute("DELETE FROM document_chunks")
        cur.execute("DELETE FROM documents")
        conn.commit()
        conn.close()

    except Exception as e:
        pytest.skip(f"Database connection failed: {e}")


@pytest.fixture
def store(db_conn):
    """Create HybridVectorStore instance for testing"""
    return HybridVectorStore(POSTGRES_DSN)


# ============================================================================
# UNIT TESTS
# ============================================================================


@pytest.mark.tier1
@pytest.mark.unit
def test_singleton_model():
    """Test that SentenceTransformer is a singleton to prevent repeated loads"""
    vs1 = HybridVectorStore(POSTGRES_DSN)
    vs2 = HybridVectorStore(POSTGRES_DSN)
    assert vs1.model is vs2.model  # Same object -> singleton


def test_connection_pool_singleton():
    """Test that connection pool is a singleton - SKIPPED: No longer using global pool"""
    pytest.skip("No longer using global connection pool")


@pytest.mark.tier1
@pytest.mark.smoke
def test_model_caching():
    """Test that model loading is cached"""
    model1 = _get_model("all-MiniLM-L6-v2")
    model2 = _get_model("all-MiniLM-L6-v2")
    assert model1 is model2  # Cached model


@pytest.mark.tier1
@pytest.mark.unit
def test_embedding_generation():
    """Test embedding generation with proper numpy types"""
    store = HybridVectorStore(POSTGRES_DSN)
    texts = ["hello world", "test embedding"]
    embeddings = store.model.encode(texts, convert_to_numpy=True)

    assert len(embeddings) == 2
    assert embeddings[0].dtype == np.float32 or embeddings[0].dtype == np.float64
    assert embeddings[0].shape[0] == 384  # all-MiniLM-L6-v2 dimension


def test_uuid_document_id():
    """Test that document IDs are UUIDs to prevent collisions"""
    store = HybridVectorStore(POSTGRES_DSN)
    chunks = ["test chunk"]
    metadata = {"filename": "test.txt"}

    result = store("store_chunks", chunks=chunks, metadata=metadata)
    assert result["status"] == "success"

    doc_id = result["document_id"]
    # Verify it's a valid UUID
    uuid.UUID(doc_id)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


@pytest.mark.tier1
@pytest.mark.integration
def test_store_and_search(store):
    """Test complete store and search workflow"""
    chunks = ["alpha bravo", "charlie delta", "echo foxtrot"]
    meta = {"filename": "test.txt", "file_size": 123}

    # Store chunks
    res = store("store_chunks", chunks=chunks, metadata=meta)
    assert res["status"] == "success"
    doc_id = res["document_id"]
    assert uuid.UUID(doc_id)  # Valid UUID

    # Search for content
    search = store("search", query="bravo", limit=2)
    assert search["status"] == "success"
    assert search["total_results"] >= 1
    assert search["results"][0]["content"] == "alpha bravo"
    assert search["results"][0]["similarity_score"] > 0.5


def test_delete_document(store):
    """Test document deletion"""
    chunks = ["one", "two"]
    meta = {"filename": "temp.txt"}

    # Store document
    doc_id = store("store_chunks", chunks=chunks, metadata=meta)["document_id"]

    # Delete document
    del_res = store("delete_document", document_id=doc_id)
    assert del_res["status"] == "success"

    # Verify document is gone
    fetch = store("get_document_chunks", document_id=doc_id)
    assert fetch["total_chunks"] == 0


def test_get_document_chunks(store):
    """Test retrieving document chunks"""
    chunks = ["first chunk", "second chunk", "third chunk"]
    meta = {"filename": "multi.txt"}

    # Store document
    doc_id = store("store_chunks", chunks=chunks, metadata=meta)["document_id"]

    # Retrieve chunks
    result = store("get_document_chunks", document_id=doc_id)
    assert result["status"] == "success"
    assert result["total_chunks"] == 3
    assert result["chunks"][0]["content"] == "first chunk"
    assert result["chunks"][1]["content"] == "second chunk"
    assert result["chunks"][2]["content"] == "third chunk"


def test_bulk_insert_performance(store):
    """Test bulk insert performance with many chunks"""
    # Create 100 chunks
    chunks = [f"chunk {i} with some content" for i in range(100)]
    meta = {"filename": "bulk_test.txt"}

    start_time = time.perf_counter()
    result = store("store_chunks", chunks=chunks, metadata=meta)
    end_time = time.perf_counter()

    assert result["status"] == "success"
    assert result["chunks_stored"] == 100

    # Performance check: should complete in reasonable time
    elapsed = end_time - start_time
    assert elapsed < 30.0  # Should complete within 30 seconds


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_connection_pool_reuse(store):
    """Test that connection pool reuse improves performance"""
    # First search (connection creation)
    t1 = time.perf_counter()
    store("search", query="pool test", limit=1)
    t2 = time.perf_counter()

    # Second search (pool reuse)
    t3 = time.perf_counter()
    store("search", query="pool test", limit=1)
    t4 = time.perf_counter()

    first_time = t2 - t1
    second_time = t4 - t3

    # Second search should be faster (crude but shows no reconnect cost)
    assert second_time < first_time * 2


def test_embedding_model_singleton_performance():
    """Test that singleton model prevents repeated loads"""
    # First load
    t1 = time.perf_counter()
    vs1 = HybridVectorStore(POSTGRES_DSN)
    t2 = time.perf_counter()

    # Second load (should be instant due to singleton)
    t3 = time.perf_counter()
    vs2 = HybridVectorStore(POSTGRES_DSN)
    t4 = time.perf_counter()

    first_load = t2 - t1
    second_load = t4 - t3

    # Second load should be much faster
    assert second_load < first_load * 0.1

    # Verify both instances share the same model (singleton behavior)
    assert vs1.model is vs2.model


# ============================================================================
# SECURITY TESTS
# ============================================================================


def test_sql_injection_not_possible(store):
    """Test that SQL injection attempts are handled safely"""
    evil_queries = [
        "anything' OR 1=1 -- ",
        "'; DROP TABLE document_chunks; --",
        "' UNION SELECT * FROM documents --",
        "'; INSERT INTO documents VALUES ('hacked', 'hacked', 'hacked', 0, 0, '{}'); --",
    ]

    for evil_query in evil_queries:
        res = store("search", query=evil_query, limit=1)
        assert res["status"] == "success"  # No crash
        # The evil query should just be treated as a normal search query


def test_input_validation():
    """Test input validation for various edge cases"""
    store = HybridVectorStore(POSTGRES_DSN)

    # Test with empty chunks
    res = store("store_chunks", chunks=[], metadata={})
    assert res["status"] == "success"  # Should handle gracefully

    # Test with None values
    res = store("search", query="", limit=0)
    assert res["status"] == "success"  # Should handle gracefully

    # Test with very long query
    long_query = "x" * 10000
    res = store("search", query=long_query, limit=1)
    assert res["status"] == "success"  # Should handle gracefully


# ============================================================================
# RESILIENCE TESTS
# ============================================================================


def test_database_connection_failure():
    """Test handling of database connection failures"""
    # Test with invalid connection string
    invalid_store = HybridVectorStore("postgresql://invalid:invalid@localhost:9999/invalid")

    res = invalid_store("search", query="test", limit=1)
    assert res["status"] == "error"
    assert "error" in res


def test_embedding_generation_failure():
    """Test handling of embedding generation failures"""
    store = HybridVectorStore(POSTGRES_DSN)

    # Test with problematic text (very long, special characters, etc.)
    problematic_chunks = [
        "x" * 100000,  # Very long text
        "",  # Empty text
        "🚀" * 1000,  # Many emojis
    ]

    # Should handle gracefully
    res = store("store_chunks", chunks=problematic_chunks, metadata={})
    # Should either succeed or fail gracefully, not crash
    assert res["status"] in ["success", "error"]


def test_partial_failure_scenarios(store):
    """Test partial failure scenarios"""
    # Test with mixed valid/invalid data
    chunks = ["valid chunk", "", "another valid chunk"]
    meta = {"filename": "partial_test.txt"}

    res = store("store_chunks", chunks=chunks, metadata=meta)
    # Should handle gracefully, either succeed or fail cleanly
    assert res["status"] in ["success", "error"]


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_unknown_operation():
    """Test handling of unknown operations"""
    store = HybridVectorStore(POSTGRES_DSN)

    with pytest.raises(ValueError, match="Unknown operation"):
        store("unknown_operation", some_param="value")


def test_missing_parameters():
    """Test handling of missing required parameters"""
    store = HybridVectorStore(POSTGRES_DSN)

    # Test missing chunks
    res = store("store_chunks", metadata={})
    assert res["status"] == "error"

    # Test missing query
    res = store("search", limit=1)
    assert res["status"] == "error"

    # Test missing document_id
    res = store("delete_document")
    assert res["status"] == "error"


def test_invalid_parameters():
    """Test handling of invalid parameter types"""
    store = HybridVectorStore(POSTGRES_DSN)

    # Test with non-string chunks
    res = store("store_chunks", chunks=[123, 456], metadata={})
    assert res["status"] == "error"

    # Test with non-string query
    res = store("search", query=123, limit=1)
    assert res["status"] == "error"


# ============================================================================
# STATISTICS TESTS
# ============================================================================


def test_get_stats(store):
    """Test database statistics retrieval"""
    # Store some test data first
    chunks = ["stats test chunk"]
    meta = {"filename": "stats_test.txt"}
    store("store_chunks", chunks=chunks, metadata=meta)

    # Get stats
    stats = store.get_stats()
    assert stats["status"] == "success"
    assert "total_chunks" in stats
    assert "total_documents" in stats
    assert "document_types" in stats
    assert stats["total_chunks"] >= 1
    assert stats["total_documents"] >= 1


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


def test_large_chunks(store):
    """Test handling of very large chunks"""
    large_chunk = "x" * 10000  # 10KB chunk
    chunks = [large_chunk]
    meta = {"filename": "large_test.txt"}

    res = store("store_chunks", chunks=chunks, metadata=meta)
    assert res["status"] == "success"


def test_many_small_chunks(store):
    """Test handling of many small chunks"""
    chunks = [f"chunk_{i}" for i in range(50)]
    meta = {"filename": "many_chunks.txt"}

    res = store("store_chunks", chunks=chunks, metadata=meta)
    assert res["status"] == "success"
    assert res["chunks_stored"] == 50


def test_special_characters(store):
    """Test handling of special characters in content"""
    special_chunks = [
        "Hello 世界! 🌍",
        "SQL: SELECT * FROM table;",
        "HTML: <script>alert('test')</script>",
        'JSON: {"key": "value"}',
        "Unicode: 🚀📚💻🎯",
    ]
    meta = {"filename": "special_chars.txt"}

    res = store("store_chunks", chunks=special_chunks, metadata=meta)
    assert res["status"] == "success"


# ============================================================================
# BENCHMARK TESTS
# ============================================================================


def test_search_performance_benchmark(store):
    """Benchmark search performance"""
    # Store some test data
    chunks = [f"benchmark chunk {i} with some content" for i in range(100)]
    meta = {"filename": "benchmark.txt"}
    store("store_chunks", chunks=chunks, metadata=meta)

    # Benchmark search performance
    queries = ["benchmark", "content", "test", "performance"]

    for query in queries:
        start_time = time.perf_counter()
        result = store("search", query=query, limit=10)
        end_time = time.perf_counter()

        elapsed = end_time - start_time
        assert elapsed < 5.0  # Should complete within 5 seconds
        assert result["status"] == "success"


def test_bulk_insert_benchmark(store):
    """Benchmark bulk insert performance"""
    # Create large dataset
    chunks = [f"bulk insert test chunk {i}" for i in range(500)]
    meta = {"filename": "bulk_benchmark.txt"}

    start_time = time.perf_counter()
    result = store("store_chunks", chunks=chunks, metadata=meta)
    end_time = time.perf_counter()

    elapsed = end_time - start_time
    assert result["status"] == "success"
    assert result["chunks_stored"] == 500
    assert elapsed < 60.0  # Should complete within 60 seconds


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("🚀 Running VectorStore comprehensive test suite...")

    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
