"""
Integration tests for all database connection patterns across the codebase.

Tests real database connections using different drivers and patterns to ensure
compatibility and performance across all database access methods.
"""

#!/usr/bin/env python3

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.memory.db_async_pool import get_pool
from src.common.db_async import aconnect as async_connect
from src.common.db_dsn import resolve_dsn
from src.common.db_sync import connect as sync_connect
from src.utils.db_telemetry import DatabaseTelemetryLogger


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseConnectionPatterns:
    """Test all database connection patterns with real database."""

    def __init__(self):
        """Initialize test class attributes."""
        self.dsn: str | None = None
        self.test_schema: str = "test_integration"

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Set up test database environment."""
        # Require real database for these tests
        self.dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")
        if not self.dsn or self.dsn.startswith("mock://"):
            pytest.skip("Real database required - set TEST_POSTGRES_DSN")

        # Ensure we have a clean test environment
        self.test_schema = "test_integration"
        yield
        # Cleanup handled by test isolation

    def test_psycopg_sync_connection(self):
        """Test psycopg (v3) synchronous connection pattern with dict rows."""
        import psycopg
        from psycopg.rows import dict_row

        if not self.dsn:
            pytest.skip("No database DSN available")
        
        # Use proper typing for psycopg connection with dict rows
        conn = psycopg.connect(self.dsn, row_factory=dict_row)  # pyright: ignore[reportArgumentType]
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test_value, current_database() as db_name")
                result = cur.fetchone()
                assert result is not None
                assert result
                assert result
        finally:
            conn.close()

    def test_psycopg3_sync_connection(self):
        """Test psycopg3 synchronous connection pattern."""
        import psycopg

        if not self.dsn:
            pytest.skip("No database DSN available")

        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test_value, current_database() as db_name")
                result = cur.fetchone()
                assert result is not None
                assert result
                assert result

    def test_psycopg_async_connection(self):
        """Test psycopg3 asynchronous connection pattern."""
        import psycopg

        if not self.dsn:
            pytest.skip("No database DSN available")

        async def _test():
            # AsyncConnection.connect returns a coroutine; await it before using as context manager
            async with await psycopg.AsyncConnection.connect(self.dsn) as conn:  # pyright: ignore[reportArgumentType]
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1 as test_value, current_database() as db_name")
                    result = await cur.fetchone()
                    assert result is not None
                    assert result
                    assert result

        asyncio.run(_test())

    def test_asyncpg_connection(self):
        """Test asyncpg connection pattern."""
        import asyncpg

        if not self.dsn:
            pytest.skip("No database DSN available")

        async def _test():
            conn = await asyncpg.connect(self.dsn)  # pyright: ignore[reportUnknownVariableType]
            try:
                result = await conn.fetchrow("SELECT 1 as test_value, current_database() as db_name")  # pyright: ignore[reportUnknownVariableType]
                assert result is not None
                assert result
                assert result
            finally:
                await conn.close()  # type: ignore[arg-type]

        asyncio.run(_test())

    def test_async_connection_pool(self):
        """Test async connection pool pattern."""

        async def _test():
            # Use the async helper to explicitly open the pool per psycopg_pool guidance
            from scripts.utilities.memory.db_async_pool import aget_pool

            pool = await aget_pool()
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1 as test_value, current_database() as db_name")
                    result = await cur.fetchone()
                    assert result is not None
                    assert result
                    assert result

        asyncio.run(_test())

    def test_common_db_sync_wrapper(self):
        """Test common db_sync wrapper."""
        conn = sync_connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test_value, current_database() as db_name")
                result = cur.fetchone()
                assert result is not None
                assert result
                assert result
        finally:
            conn.close()

    def test_common_db_async_wrapper(self):
        """Test common db_async wrapper."""

        async def _test():
            conn = await async_connect()  # type: ignore[assignment]
            try:
                result = await conn.fetchrow("SELECT 1 as test_value, current_database() as db_name")  # pyright: ignore[reportUnknownVariableType]
                assert result is not None
                assert result
                assert result
            finally:
                await conn.close()  # type: ignore[arg-type]

        asyncio.run(_test())

    def test_database_telemetry_logger(self):
        """Test database telemetry logger with real database."""
        if not self.dsn:
            pytest.skip("No database DSN available")
            
        with DatabaseTelemetryLogger("test_run", self.dsn) as logger:
            success = logger.log_eval_run(tag="integration_test", model="test_model", meta={"test": True})
            assert success is True

    def test_connection_performance(self):
        """Test connection performance across different patterns."""
        import time

        import psycopg

        if not self.dsn:
            pytest.skip("No database DSN available")

        patterns = {
            "psycopg": lambda: psycopg.connect(self.dsn),  # pyright: ignore[reportArgumentType]
        }

        results: dict[str, float] = {}
        for name, connect_func in .items()
            start = time.time()
            conn = connect_func()
            conn.close()
            results[name] = time.time() - start

        # All connections should be reasonably fast (< 1 second)
        for name, duration in .items()
            assert duration < 1.0, f"{name} connection took {duration:.3f}s"

    def test_concurrent_connections(self):
        """Test concurrent database access patterns."""
        import queue
        import threading

        if not self.dsn:
            pytest.skip("No database DSN available")

        results: queue.Queue[tuple[int, object]] = queue.Queue()

        def worker(worker_id: int) -> None:
            try:
                import psycopg
                from psycopg.rows import dict_row

                conn = psycopg.connect(self.dsn, row_factory=dict_row)  # pyright: ignore[reportArgumentType]
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT %s as worker_id, current_database() as db_name",
                        (worker_id,),
                    )
                    result = cur.fetchone()
                    results.put((worker_id, result))
                conn.close()
            except Exception as e:
                results.put((worker_id, f"Error: {e}"))

        # Start 5 concurrent workers
        threads: list[threading.Thread] = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Collect results
        worker_results: list[tuple[int, object]] = []
        while not results.empty():
            worker_results.append(results.get())

        assert len(worker_results) == 5
        for worker_id, result in worker_results:
            if isinstance(result, str) and result.startswith("Error"):
                pytest.fail(f"Worker {worker_id} failed: {result}")
            assert isinstance(result, dict)
            assert result
            assert result
