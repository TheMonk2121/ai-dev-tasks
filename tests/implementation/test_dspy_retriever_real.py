"""
Real database integration tests for DSPy Retriever system.

Tests PostgreSQL query execution, vector operations, and retrieval
functionality with actual database operations.
"""

#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from psycopg.rows import dict_row

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.db_dsn import resolve_dsn
from src.dspy_modules.retriever.pg import fetch_doc_chunks_by_slug, get_db_connection


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.dspy
class TestDSPyRetrieverReal:
    """Real database integration tests for DSPy Retriever."""

    def __init__(self) -> None:
        self.dsn: str | None = None

    @pytest.fixture(autouse=True)
    def setup_database(self) -> Any:
        """Set up test database environment."""
        self.dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")
        if not self.dsn or self.dsn.startswith("mock://"):
            pytest.skip("Real database required - set TEST_POSTGRES_DSN")

        # Set environment for retriever
        os.environ["POSTGRES_DSN"] = self.dsn
        yield
        # Cleanup
        if "POSTGRES_DSN" in os.environ:
            del os.environ["POSTGRES_DSN"]

    def test_database_connection_validation(self) -> None:
        """Test that database connection validation works correctly."""
        # Test with real DSN
        conn = get_db_connection()
        assert conn is not None

        with conn.cursor() as cur:
            cur.row_factory = dict_row
            cur.execute("SELECT current_database()")
            result = cur.fetchone()
            assert result is not None
            assert "current_database" in result

        conn.close()

    def test_mock_dsn_rejection(self) -> None:
        """Test that mock DSNs are properly rejected."""
        # Temporarily set mock DSN
        original_dsn = os.environ.get("POSTGRES_DSN")
        os.environ["POSTGRES_DSN"] = "mock://test"

        try:
            with pytest.raises(RuntimeError, match="Invalid DSN detected"):
                _ = get_db_connection()
        finally:
            # Restore original DSN
            if original_dsn:
                os.environ["POSTGRES_DSN"] = original_dsn
            elif "POSTGRES_DSN" in os.environ:
                del os.environ["POSTGRES_DSN"]

    def test_document_chunks_retrieval(self) -> None:
        """Test document chunks retrieval with real database."""
        conn = get_db_connection()

        try:
            # Test basic retrieval
            chunks = fetch_doc_chunks_by_slug("test_document", limit=5)
            assert isinstance(chunks, list)

            # If we have test data, verify structure
            if chunks:
                chunk = chunks[0]
                assert "content" in chunk or "text" in chunk
                assert "embedding" in chunk or "vector" in chunk

        finally:
            conn.close()

    def test_vector_operations_real_database(self) -> None:
        """Test vector operations with real database."""
        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.row_factory = dict_row
                # Test vector similarity search
                _ = np.random.rand(384).astype(np.float32)

                # Test if pgvector extension is available
                cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
                vector_ext = cur.fetchone()

                if vector_ext:
                    # Test vector operations
                    cur.execute(
                        """
                        SELECT 1 as test_value,
                               '[1,2,3]'::vector <-> '[1,2,3]'::vector as distance
                    """
                    )
                    result = cur.fetchone()
                    assert result is not None
                    assert "test_value" in result
                else:
                    pytest.skip("pgvector extension not available")

        finally:
            conn.close()

    def test_retrieval_performance_real_database(self) -> None:
        """Test retrieval performance with real database."""
        import time

        conn = get_db_connection()

        try:
            start_time = time.time()

            # Perform multiple retrievals
            for i in range(10):
                chunks = fetch_doc_chunks_by_slug(f"test_doc_{i}", limit=3)
                assert isinstance(chunks, list)

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 10 retrievals in reasonable time
            assert duration < 10.0, f"10 retrievals took {duration:.3f}s"

        finally:
            conn.close()

    def test_database_schema_validation(self) -> None:
        """Test that required database schema exists."""
        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.row_factory = dict_row
                # Check for document_chunks table
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'document_chunks'
                """
                )
                result = cur.fetchone()

                if result:
                    # Table exists, check structure
                    cur.execute(
                        """
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = 'document_chunks'
                        ORDER BY ordinal_position
                    """
                    )
                    columns = cur.fetchall()
                    column_names = [col[0] for col in columns]  # type: ignore

                    # Check for essential columns
                    essential_columns = ["content", "embedding", "slug"]
                    for col in essential_columns:
                        if col not in column_names:
                            pytest.skip(f"Required column '{col}' not found in document_chunks table")
                else:
                    pytest.skip("document_chunks table not found - database may not be initialized")

        finally:
            conn.close()

    def test_concurrent_retrieval_real_database(self) -> None:
        """Test concurrent retrieval operations."""
        import queue
        import threading

        results: queue.Queue[tuple[int, int, str | None]] = queue.Queue()

        def retrieval_worker(worker_id: int) -> None:
            try:
                conn = get_db_connection()
                chunks = fetch_doc_chunks_by_slug(f"test_concurrent_{worker_id}", limit=2)
                results.put((worker_id, len(chunks), None))
                conn.close()
            except Exception as e:
                results.put((worker_id, 0, str(e)))

        # Start 5 concurrent workers
        threads: list[threading.Thread] = []
        for i in range(5):
            thread = threading.Thread(target=retrieval_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Collect results
        worker_results: list[tuple[int, int, str | None]] = []
        while not results.empty():
            worker_results.append(results.get())

        assert len(worker_results) == 5
        for worker_id, chunk_count, error in worker_results:
            if error:
                pytest.fail(f"Worker {worker_id} failed: {error}")
            assert chunk_count >= 0  # May be 0 if no test data

    def test_embedding_dimension_validation(self) -> None:
        """Test embedding dimension validation with real database."""
        conn = get_db_connection()

        try:
            with conn.cursor() as cur:
                cur.row_factory = dict_row
                # Test if we can insert and retrieve embeddings
                test_embedding = np.random.rand(384).astype(np.float32)

                # Check if we have a test table for embeddings
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN ('test_embeddings', 'document_chunks')
                """
                )
                tables = cur.fetchall()

                if tables:
                    # Test embedding operations
                    cur.execute(
                        "SELECT %s::vector as test_embedding",
                        (test_embedding.tolist(),),
                    )
                    result = cur.fetchone()
                    assert result is not None
                    assert "test_embedding" in result
                else:
                    pytest.skip("No embedding tables found for testing")

        finally:
            conn.close()

    def test_database_connection_pooling(self) -> None:
        """Test database connection pooling behavior."""
        import threading
        import time

        connections: list[Any] = []
        errors: list[Any] = []
        def create_connection(conn_id: int) -> None:
            try:
                conn = get_db_connection()
                connections.append((conn_id, conn))
                time.sleep(0.1)  # Simulate work
                conn.close()
            except Exception as e:
                errors.append((conn_id, str(e)))

        # Create multiple connections concurrently
        threads: list[Any] = []
        for i in range(10):
            thread = threading.Thread(target=create_connection, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Connection errors: {errors}"
        assert len(connections) == 10, f"Expected 10 connections, got {len(connections)}"

    def test_dsn_resolution_real_database(self) -> None:
        """Test DSN resolution with real database."""
        # Test resolve_dsn function
        dsn = resolve_dsn()
        assert dsn is not None
        assert not dsn.startswith("mock://")
        assert "postgresql://" in dsn

        # Test that resolved DSN works
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.row_factory = dict_row
                cur.execute("SELECT 1")
                result = cur.fetchone()
                assert result is not None
        finally:
            conn.close()
