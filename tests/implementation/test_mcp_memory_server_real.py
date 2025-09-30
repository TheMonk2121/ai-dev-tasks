"""
Real database integration tests for MCP Memory Server.

Tests the complete MCP memory server workflow with actual database operations,
including conversation capture, thread management, and memory retrieval.
"""

#!/usr/bin/env python3

import asyncio
import os
import sys
import time
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi.testclient import TestClient

from scripts.utilities.memory.db_async_pool import (
    aget_pool,
    ensure_thread_exists,
    get_parent_turn,
    insert_ai_turn,
    insert_user_turn,
)
from scripts.utilities.memory.mcp_memory_server import (
    app,
    capture_ai_response,
    capture_user_query,
    get_cursor_integration,
    record_chat_history,
)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.mcp
class TestMCPMemoryServerReal:
    """Real database integration tests for MCP Memory Server."""

    def __init__(self):
        self.dsn: str | None = None

    @pytest.fixture(autouse=True)
    def setup_database(self):
        """Set up test database environment."""
        self.dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")
        if not self.dsn or self.dsn.startswith("mock://"):
            pytest.skip("Real database required - set TEST_POSTGRES_DSN")

        # Set environment for MCP server
        os.environ
        yield
        # Cleanup
        if "POSTGRES_DSN" in os.environ:
            del os.environ

    @pytest.mark.asyncio
    async def test_thread_management_real_database(self):
        """Test thread management with real database operations."""
        # Test thread creation
        thread_id = "test_thread_real_001"

        pool = await aget_pool()
        async with pool.connection() as conn:
            # Ensure thread exists
            created_thread_id = await ensure_thread_exists(conn, thread_id)
            assert created_thread_id == thread_id

            # Test thread retrieval
            retrieved_thread_id = await ensure_thread_exists(conn, thread_id)
            assert retrieved_thread_id == thread_id

    @pytest.mark.asyncio
    async def test_conversation_capture_real_database(self):
        """Test conversation capture with real database operations."""
        thread_id = "test_thread_real_002"

        pool = await aget_pool()
        async with pool.connection() as conn:
            # Ensure thread exists
            _ = await ensure_thread_exists(conn, thread_id)

            # Test user turn insertion
            user_content = "What is the current status of the project?"
            user_metadata = {"source": "test", "priority": "high"}

            turn_id, seq = await insert_user_turn(
                conn, thread_id=thread_id, content=user_content, metadata=user_metadata
            )

            assert turn_id is not None
            assert seq == 1

            # Test AI turn insertion
            ai_content = "The project is currently in development phase with 75% completion."
            ai_metadata = {"model": "claude-3", "confidence": 0.95}

            ai_turn_id, _, ai_seq = await insert_ai_turn(  # type: ignore[assignment]
                conn,
                explicit_thread_id=thread_id,
                content=ai_content,
                metadata=ai_metadata,
                parent_turn_id=turn_id,
            )

            assert ai_turn_id is not None
            assert ai_seq == 2

            # Test parent turn retrieval
            parent_turn = await get_parent_turn(conn, ai_turn_id)
            assert parent_turn is not None
            assert parent_turn["id"] == turn_id
            assert parent_turn["role"] == "user"
            assert parent_turn["content"] == "Test message"

    async def test_mcp_server_endpoints_real_database(self):
        """Test MCP server endpoints with real database operations."""
        client = TestClient(app)

        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "database" in health_data

        # Test memory query endpoint
        query_data = {
            "query": "What are the current project priorities?",
            "role": "planner",
            "limit": 10,
        }

        response = client.post("/memory/query", json=query_data)
        assert response.status_code == 200
        memory_data = response.json()
        assert "success" in memory_data
        assert "data" in memory_data

    @pytest.mark.asyncio
    async def test_conversation_workflow_real_database(self):
        """Test complete conversation workflow with real database."""
        # Initialize cursor integration
        integration = get_cursor_integration("test_workflow_thread")
        assert integration is not None
        assert integration.thread_id is not None

        # Test user query capture
        user_query = "How can I improve the test coverage?"
        user_metadata = {"test": True, "workflow": "integration"}

        result = await capture_user_query({"query": user_query, "metadata": user_metadata})  # type: ignore[assignment]
        assert result.success is True  # type: ignore[attr-defined]
        assert "turn_id" in result.data  # type: ignore[attr-defined]

        # Test AI response capture
        ai_response = "You can improve test coverage by adding more integration tests and property-based tests."
        ai_metadata = {"model": "claude-3", "test": True}

        result = await capture_ai_response({"response": ai_response, "metadata": ai_metadata})  # type: ignore[assignment]
        assert result.success is True  # type: ignore[attr-defined]
        assert "turn_id" in result.data  # type: ignore[attr-defined]

        # Test chat history recording
        chat_data = {
            "user_input": user_query,
            "system_output": ai_response,
            "project_dir": "/test/project",
            "file_operations": "test operations",
            "llm_name": "claude-3",
        }

        result = await record_chat_history(chat_data)  # type: ignore[assignment]
        assert result.success is True  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_concurrent_operations_real_database(self):
        """Test concurrent database operations with real database."""
        thread_id = "test_concurrent_thread"

        async def insert_turn(turn_num: int):
            pool = await aget_pool()
            async with pool.connection() as conn:
                _ = await ensure_thread_exists(conn, thread_id)

                content = f"Test message {turn_num}"
                metadata = {"turn_num": turn_num, "concurrent": True}

                turn_id, seq = await insert_user_turn(conn, thread_id=thread_id, content=content, metadata=metadata)
                return turn_id, seq

        # Run 5 concurrent insertions
        tasks = [insert_turn(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # Verify all insertions succeeded
        assert len(results) == 5
        for i, (turn_id, seq) in enumerate(results):
            assert turn_id is not None
            assert seq == i + 1

    @pytest.mark.asyncio
    async def test_database_performance_real_database(self):
        """Test database performance with real operations."""
        thread_id = "test_performance_thread"

        pool = await aget_pool()
        async with pool.connection() as conn:
            _ = await ensure_thread_exists(conn, thread_id)

            # Measure insertion performance
            start_time = time.time()

            for i in range(10):
                content = f"Performance test message {i}"
                metadata = {"performance_test": True, "iteration": i}

                turn_id, _ = await insert_user_turn(conn, thread_id=thread_id, content=content, metadata=metadata)
                assert turn_id is not None

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 10 insertions in reasonable time
            assert duration < 5.0, f"10 insertions took {duration:.3f}s"

            # Measure retrieval performance
            start_time = time.time()

            for i in range(10):
                _ = await get_parent_turn(conn, f"test_turn_{i}")
                # May be None for non-existent turns, that's OK

            end_time = time.time()
            duration = end_time - start_time

            # Should complete 10 retrievals quickly
            assert duration < 2.0, f"10 retrievals took {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_error_handling_real_database(self):
        """Test error handling with real database operations."""
        # Test with invalid thread ID
        pool = await aget_pool()
        async with pool.connection() as conn:
            # This should not raise an exception
            result = await get_parent_turn(conn, "non_existent_turn_id")
            assert result is None

            # Test with invalid parent turn ID for AI turn
            try:
                _ = await insert_ai_turn(
                    conn,
                    explicit_thread_id="test_error_thread",
                    content="Test content",
                    metadata={},
                    parent_turn_id="non_existent_parent",
                )
                pytest.fail("Should have raised ValueError for invalid parent")
            except ValueError as e:
                assert "Parent turn not found" in str(e)

    @pytest.mark.asyncio
    async def test_metadata_serialization_real_database(self):
        """Test metadata serialization with real database operations."""
        thread_id = "test_metadata_thread"

        pool = await aget_pool()
        async with pool.connection() as conn:
            _ = await ensure_thread_exists(conn, thread_id)

            # Test complex metadata serialization
            complex_metadata = {
                "unicode": "测试数据 🚀",
                "special_chars": "!@#$%^&*()",
                "large_data": "x" * 1000,
                "boolean": True,
                "null_value": None,
            }

            turn_id, _ = await insert_user_turn(
                conn,
                thread_id=thread_id,
                content="Test with complex metadata",
                metadata=complex_metadata,
            )

            assert turn_id is not None

            # Verify metadata was stored correctly by retrieving it
            # (This would require a retrieval function to be implemented)
            # For now, just verify the insertion succeeded
