"""
Property-based tests for MCP server database operations.

Tests the MCP server's conversation capture, thread management, and database
operations using Hypothesis to ensure robustness across various scenarios.
"""

import asyncio
import json
import os

# Add project root to path for imports
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import functions that don't require pool initialization
from scripts.utilities.memory.db_async_pool import (
    ensure_thread_exists,
    get_parent_turn,
    insert_ai_turn,
    insert_user_turn,
    next_seq,
)


@pytest.mark.prop
class TestMCPServerProperties:
    """Property-based tests for MCP server database operations."""

    def setup_method(self):
        """Set up test database connection."""
        # Use a test database URL if available, otherwise skip tests
        self.test_dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")
        if not self.test_dsn:
            pytest.skip("No test database configured")

    async def get_pool(self):
        """Get or create test pool in async context."""
        if not hasattr(self, "_pool"):
            from scripts.utilities.memory.db_async_pool import aget_pool

            self._pool = await aget_pool()
        return self._pool

    def teardown_method(self):
        """Clean up test database connection."""
        if hasattr(self, "_pool"):
            asyncio.run(self._pool.close())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(min_size=1, max_size=1000),
        metadata=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans(), st.floats()),
        ),
    )
    @settings(max_examples=10, deadline=5000)
    def test_thread_creation_idempotent(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Thread creation should be idempotent - creating the same thread multiple times has the same effect."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Create thread first time
                tid1 = await ensure_thread_exists(conn, thread_id)

                # Create same thread again
                tid2 = await ensure_thread_exists(conn, thread_id)

                # Should return the same thread ID
                assert tid1 == tid2 == thread_id

                # Verify thread exists in database
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1 FROM atlas_thread WHERE thread_id = %s", (thread_id,))
                    assert await cur.fetchone() is not None

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(min_size=1, max_size=1000),
        metadata=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans(), st.floats()),
        ),
    )
    @settings(max_examples=10, deadline=5000)
    def test_user_turn_creation_properties(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Test properties of user turn creation."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Create user turn
                turn_id, seq = await insert_user_turn(conn, thread_id=tid, content=content, metadata=metadata)

                # Verify properties
                assert turn_id.startswith("turn_"), "Turn ID should start with 'turn_'"
                assert len(turn_id) > 10, "Turn ID should be reasonably long"
                assert seq >= 0, "Sequence number should be non-negative"

                # Verify turn exists in database
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT turn_id, thread_id, role, content, metadata FROM atlas_conversation_turn WHERE turn_id = %s",
                        (turn_id,),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "Turn should exist in database"
                    assert result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")
                    # Metadata should be properly serialized
                    assert isinstance(result.get("key", "")

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        user_content=st.text(min_size=1, max_size=500),
        ai_content=st.text(min_size=1, max_size=500),
        metadata=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans(), st.floats()),
        ),
    )
    @settings(max_examples=10, deadline=5000)
    def test_conversation_turn_sequence_properties(
        self,
        thread_id: str,
        user_content: str,
        ai_content: str,
        metadata: dict[str, Any],
    ):
        """Test that conversation turns maintain proper sequence and relationships."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Create user turn
                user_turn_id, user_seq = await insert_user_turn(
                    conn, thread_id=tid, content=user_content, metadata=metadata
                )

                # Create AI turn referencing user turn
                ai_turn_id, parent_tid, ai_seq = await insert_ai_turn(
                    conn,
                    parent_turn_id=user_turn_id,
                    content=ai_content,
                    metadata=metadata,
                    status="final",
                )

                # Verify properties
                assert ai_turn_id.startswith("turn_"), "AI turn ID should start with 'turn_'"
                assert parent_tid == tid, "Parent thread ID should match"
                assert ai_seq >= user_seq, "AI turn sequence should be >= user turn sequence"

                # Verify parent-child relationship
                parent_info = await get_parent_turn(conn, user_turn_id)
                assert parent_info is not None, "Parent turn should exist"
                assert result.get("key", "")
                assert result.get("key", "")
                assert result.get("key", "")

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(min_size=1, max_size=1000),
        metadata=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans(), st.floats()),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_duplicate_turn_id_handling(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Test that duplicate turn IDs are handled gracefully."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Create first turn
                turn_id1, seq1 = await insert_user_turn(conn, thread_id=tid, content=content, metadata=metadata)

                # Try to create turn with same ID (should be handled by ON CONFLICT DO NOTHING)
                # This tests the idempotency of turn creation
                turn_id2, seq2 = await insert_user_turn(
                    conn,
                    thread_id=tid,
                    content=content + " modified",
                    metadata=metadata,
                )

                # Turn IDs should be different (new UUID generated)
                assert turn_id1 != turn_id2, "Turn IDs should be unique"

                # Both turns should exist
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT COUNT(*) FROM atlas_conversation_turn WHERE thread_id = %s",
                        (tid,),
                    )
                    count = await cur.fetchone()[0]
                    assert count == 2, "Both turns should exist"

        asyncio.run(_test())

    @given(
        user_queries=st.lists(st.text(min_size=1, max_size=500), min_size=1, max_size=5),
        ai_responses=st.lists(st.text(min_size=1, max_size=500), min_size=1, max_size=5),
    )
    @settings(max_examples=5, deadline=10000)
    def test_conversation_sequence_properties(self, user_queries: list[str], ai_responses: list[str]):
        """Test properties of conversation sequences."""

        async def _test():
            pool = await self.get_pool()
            thread_id = f"thread_{uuid.uuid4().hex[:8]}"

            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                turn_ids = []

                # Create alternating user/AI turns
                for i, (query, response) in enumerate(zip(user_queries, ai_responses)):
                    # User turn
                    user_turn_id, user_seq = await insert_user_turn(
                        conn,
                        thread_id=tid,
                        content=query,
                        metadata={"sequence": i, "type": "user"},
                    )
                    turn_ids.append(user_turn_id)

                    # AI turn
                    ai_turn_id, parent_tid, ai_seq = await insert_ai_turn(
                        conn,
                        parent_turn_id=user_turn_id,
                        content=response,
                        metadata={"sequence": i, "type": "ai"},
                        status="final",
                    )
                    turn_ids.append(ai_turn_id)

                # Verify sequence properties
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT turn_id, role, content FROM atlas_conversation_turn WHERE thread_id = %s ORDER BY created_at",
                        (tid,),
                    )
                    turns = await cur.fetchall()

                    assert len(turns) == len(turn_ids), "All turns should be stored"

                    # Verify alternating pattern
                    for i, (turn_id, role, content) in enumerate(turns):
                        expected_role = "user" if i % 2 == 0 else "assistant"
                        assert role == expected_role, f"Turn {i} should have role {expected_role}"

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(min_size=1, max_size=1000),
    )
    @settings(max_examples=5, deadline=5000)
    def test_sequence_number_properties(self, thread_id: str, content: str):
        """Test that sequence numbers are properly managed."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Create multiple turns and verify sequence numbers
                sequences = []
                for i in range(3):
                    turn_id, seq = await insert_user_turn(
                        conn,
                        thread_id=tid,
                        content=f"{content} {i}",
                        metadata={"iteration": i},
                    )
                    sequences.append(seq)

                # Sequence numbers should be increasing
                assert sequences == sorted(sequences), "Sequence numbers should be increasing"
                assert all(seq >= 0 for seq in sequences), "All sequence numbers should be non-negative"

                # Verify sequence count matches turn count
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT COUNT(*) FROM atlas_conversation_turn WHERE thread_id = %s",
                        (tid,),
                    )
                    count = await cur.fetchone()[0]
                    assert count == len(sequences), "Turn count should match sequence count"

        asyncio.run(_test())

    @given(invalid_parent_turn_id=st.text(min_size=1, max_size=64))
    @settings(max_examples=5, deadline=5000)
    def test_invalid_parent_turn_handling(self, invalid_parent_turn_id: str):
        """Test that invalid parent turn IDs are handled properly."""

        async def _test():
            pool = await self.get_pool()
            thread_id = f"thread_{uuid.uuid4().hex[:8]}"

            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Try to create AI turn with invalid parent
                with pytest.raises(ValueError, match="Parent turn not found"):
                    await insert_ai_turn(
                        conn,
                        parent_turn_id=invalid_parent_turn_id,
                        content="test response",
                        metadata={},
                        status="final",
                    )

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(min_size=1, max_size=1000),
        metadata=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans(), st.floats()),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_metadata_serialization_properties(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Test that metadata is properly serialized and deserialized."""

        async def _test():
            pool = await self.get_pool()
            async with pool.connection() as conn:
                # Ensure thread exists
                tid = await ensure_thread_exists(conn, thread_id)

                # Create turn with metadata
                turn_id, seq = await insert_user_turn(conn, thread_id=tid, content=content, metadata=metadata)

                # Verify metadata is properly stored and retrieved
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT metadata FROM atlas_conversation_turn WHERE turn_id = %s",
                        (turn_id,),
                    )
                    row = await cur.fetchone()
                    assert row is not None, "Turn should exist"

                    stored_metadata = result.get("key", "")
                    assert isinstance(stored_metadata, dict), "Metadata should be a dictionary"

                    # Verify all original metadata keys are present
                    for key, value in \1.items()
                        assert key in stored_metadata, f"Key {key} should be in stored metadata"
                        assert stored_metadata[key] == value, f"Value for {key} should match"

        asyncio.run(_test())
