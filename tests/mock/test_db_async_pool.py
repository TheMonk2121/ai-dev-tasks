"""
Unit tests for Database Async Pool component.
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.memory.db_async_pool import (
    ensure_thread_exists,
    get_parent_turn,
    get_pool,
    insert_ai_turn,
    insert_user_turn,
    next_seq,
)


@pytest.mark.unit
class TestDatabaseAsyncPool:
    """Test Database Async Pool functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Mock environment variables
        self.original_dsn = os.environ.get("POSTGRES_DSN", "")

    def teardown_method(self):
        """Clean up test environment."""
        if self.original_dsn:
            os.environ["POSTGRES_DSN"] = self.original_dsn
        elif "POSTGRES_DSN" in os.environ:
            del os.environ["POSTGRES_DSN"]

    def test_get_pool_initialization(self):
        """Test that get_pool initializes the pool correctly."""
        # Reset the global pool
        import scripts.utilities.memory.db_async_pool

        scripts.utilities.memory.db_async_pool.pool = None

        with patch("scripts.utilities.memory.db_async_pool.AsyncConnectionPool") as mock_pool_class:
            with patch("scripts.utilities.memory.db_async_pool.DB_DSN", "mock://test"):
                mock_pool = MagicMock()
                mock_pool_class.return_value = mock_pool

                pool = get_pool()

                assert pool == mock_pool
                mock_pool_class.assert_called_once_with(
                    "mock://test",
                    min_size=1,
                    max_size=10,
                )

    def test_get_pool_reuse(self):
        """Test that get_pool reuses the same pool instance."""
        # Reset the global pool
        import scripts.utilities.memory.db_async_pool

        scripts.utilities.memory.db_async_pool.pool = None

        with patch("scripts.utilities.memory.db_async_pool.AsyncConnectionPool") as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool_class.return_value = mock_pool

            pool1 = get_pool()
            pool2 = get_pool()

            assert pool1 == pool2
            # Should only be called once
            mock_pool_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_thread_exists_new_thread(self):
        """Test ensuring a new thread exists."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the database query - thread doesn't exist
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []

        thread_id = "test_thread_123"
        result = await ensure_thread_exists(mock_conn, thread_id)

        assert result == thread_id

        # Should execute the insert query
        mock_cursor.execute.assert_called()
        # Check that the insert query was called with correct parameters
        call_args = mock_cursor.execute.call_args
        assert "INSERT INTO atlas_thread" in result.get("key", "")
        assert thread_id in result.get("key", "")

    @pytest.mark.asyncio
    async def test_ensure_thread_exists_existing_thread(self):
        """Test ensuring an existing thread exists."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        thread_id = "existing_thread_456"

        result = await ensure_thread_exists(mock_conn, thread_id)

        assert result == thread_id

        # Should execute the insert query (with ON CONFLICT DO UPDATE)
        insert_calls = [call for call in mock_cursor.execute.call_args_list if "INSERT INTO atlas_thread" in str(call)]
        assert len(insert_calls) == 1
        # Check that the insert query was called with correct parameters
        call_args = str(mock_cursor.execute.call_args)
        assert thread_id in call_args

    @pytest.mark.asyncio
    async def test_insert_user_turn_success(self):
        """Test successful user turn insertion."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        thread_id = "test_thread_789"
        content = "Test user message"
        metadata = {"test": True, "role": "user"}

        result_turn_id, result_seq = await insert_user_turn(
            mock_conn, thread_id=thread_id, content=content, metadata=metadata
        )

        assert result_turn_id.startswith("turn_")
        assert result_seq >= 0

        # Should execute the insert query
        mock_cursor.execute.assert_called()
        call_args = str(mock_cursor.execute.call_args)
        assert "INSERT INTO atlas_conversation_turn" in call_args
        assert thread_id in call_args
        assert content in call_args
        # Check that metadata contains the role
        assert any("role" in str(param) and "user" in str(param) for param in mock_cursor.execute.call_args[0])

    @pytest.mark.asyncio
    async def test_insert_ai_turn_success(self):
        """Test successful AI turn insertion."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        # Mock parent turn lookup - this will be called multiple times with different queries
        def mock_fetchone():
            # First call: get_parent_turn
            if not hasattr(mock_fetchone, "call_count"):
                mock_fetchone.call_count = 0
            mock_fetchone.call_count += 1

            if mock_fetchone.call_count == 1:
                return ("parent_turn_123", "parent_thread_456", "user")
            elif mock_fetchone.call_count == 2:
                return (5,)  # next_seq call
            else:
                return None

        mock_cursor.fetchone.side_effect = mock_fetchone

        parent_turn_id = "parent_turn_123"
        content = "Test AI response"
        metadata = {"test": True, "role": "assistant"}
        status = "final"

        result_turn_id, result_thread_id, result_seq = await insert_ai_turn(
            mock_conn,
            parent_turn_id=parent_turn_id,
            content=content,
            metadata=metadata,
            status=status,
        )

        assert result_turn_id.startswith("turn_")
        assert result_thread_id == "parent_thread_456"
        assert result_seq >= 0

        # Should execute the parent lookup and insert queries
        assert mock_cursor.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_insert_ai_turn_invalid_parent(self):
        """Test AI turn insertion with invalid parent."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        # Mock parent turn not found
        mock_cursor.fetchone.return_value = None

        parent_turn_id = "invalid_parent_123"
        content = "Test AI response"
        metadata = {"test": True}
        status = "final"

        with pytest.raises(ValueError, match="unknown_query_turn_id"):
            await insert_ai_turn(
                mock_conn,
                parent_turn_id=parent_turn_id,
                content=content,
                metadata=metadata,
                status=status,
            )

    @pytest.mark.asyncio
    async def test_get_parent_turn_success(self):
        """Test successful parent turn retrieval."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock parent turn data
        mock_cursor.fetchone.return_value = (
            "parent_turn_123",
            "parent_thread_456",
            "user",
        )

        turn_id = "parent_turn_123"
        result = await get_parent_turn(mock_conn, turn_id)

        assert result is not None
        assert result["turn_id"] == "parent_turn_123"
        assert result["thread_id"] == "parent_thread_456"
        assert result["role"] == "user"

    @pytest.mark.asyncio
    async def test_get_parent_turn_not_found(self):
        """Test parent turn retrieval when not found."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock parent turn not found
        mock_cursor.fetchone.return_value = None

        turn_id = "nonexistent_turn_123"
        result = await get_parent_turn(mock_conn, turn_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_next_seq_success(self):
        """Test successful sequence number generation."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock sequence query result
        mock_cursor.fetchone.return_value = (5,)

        thread_id = "test_thread_123"
        result = await next_seq(mock_conn, thread_id)

        assert result == 5  # Should be the count

        # Should execute the sequence query
        mock_cursor.execute.assert_called()
        call_args = str(mock_cursor.execute.call_args)
        assert "SELECT COUNT(*)" in call_args
        assert thread_id in call_args

    @pytest.mark.asyncio
    async def test_next_seq_empty_thread(self):
        """Test sequence number generation for empty thread."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock sequence query result - no existing turns
        mock_cursor.fetchone.return_value = (None,)

        thread_id = "empty_thread_123"
        result = await next_seq(mock_conn, thread_id)

        assert result == 0  # Should be 0 for empty thread

    def test_pool_initialization_with_custom_dsn(self):
        """Test pool initialization with custom DSN."""
        # Reset the global pool
        import scripts.utilities.memory.db_async_pool

        scripts.utilities.memory.db_async_pool.pool = None

        custom_dsn = "postgresql://custom:test@localhost/test"

        with patch("scripts.utilities.memory.db_async_pool.AsyncConnectionPool") as mock_pool_class:
            with patch("scripts.utilities.memory.db_async_pool.DB_DSN", custom_dsn):
                mock_pool = MagicMock()
                mock_pool_class.return_value = mock_pool

                pool = get_pool()

                assert pool == mock_pool
                mock_pool_class.assert_called_once_with(
                    custom_dsn,
                    min_size=1,
                    max_size=10,
                )

    @pytest.mark.asyncio
    async def test_concurrent_pool_access(self):
        """Test that concurrent access to get_pool works correctly."""
        # Reset the global pool
        import scripts.utilities.memory.db_async_pool

        scripts.utilities.memory.db_async_pool.pool = None

        with patch("scripts.utilities.memory.db_async_pool.AsyncConnectionPool") as mock_pool_class:
            mock_pool = MagicMock()
            mock_pool_class.return_value = mock_pool

            # Simulate concurrent access
            async def get_pool_concurrent():
                return get_pool()

            tasks = [get_pool_concurrent() for _ in range(5)]
            results = await asyncio.gather(*tasks)

            # All results should be the same pool instance
            assert all(result == mock_pool for result in results)
            # Pool should only be created once
            mock_pool_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_metadata_serialization(self):
        """Test that metadata is properly serialized."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        thread_id = "test_thread_metadata"
        content = "Test message"
        metadata = {
            "string_value": "test",
            "int_value": 42,
            "float_value": 3.14,
            "bool_value": True,
            "list_value": [1, 2, 3],
            "dict_value": {"nested": "value"},
        }

        await insert_user_turn(mock_conn, thread_id=thread_id, content=content, metadata=metadata)

        # Check that metadata was passed correctly
        call_args = mock_cursor.execute.call_args
        # The metadata is wrapped in Jsonb, so check if any parameter contains the metadata
        assert any(str(param).find("string_value") > -1 for param in call_args[0])

    @pytest.mark.asyncio
    async def test_empty_metadata_handling(self):
        """Test handling of empty metadata."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        thread_id = "test_thread_empty_metadata"
        content = "Test message"
        metadata = {}

        result_turn_id, result_seq = await insert_user_turn(
            mock_conn, thread_id=thread_id, content=content, metadata=metadata
        )

        assert result_turn_id.startswith("turn_")
        assert result_seq >= 0

        # Should still execute the insert query
        mock_cursor.execute.assert_called()

    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of large content."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_conn.cursor = MagicMock(return_value=mock_cursor)
        mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_cursor.__aexit__ = AsyncMock(return_value=None)

        # Mock the transaction context manager
        mock_transaction = AsyncMock()
        mock_conn.transaction = MagicMock(return_value=mock_transaction)
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)

        thread_id = "test_thread_large_content"
        content = "x" * 10000  # Large content
        metadata = {"size": len(content)}

        result_turn_id, result_seq = await insert_user_turn(
            mock_conn, thread_id=thread_id, content=content, metadata=metadata
        )

        assert result_turn_id.startswith("turn_")
        assert result_seq >= 0

        # Should execute the insert query with large content
        call_args = str(mock_cursor.execute.call_args)
        assert content in call_args
