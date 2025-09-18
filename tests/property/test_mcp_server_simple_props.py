"""
Simple property-based tests for MCP server database operations.

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


@pytest.mark.prop
class TestMCPServerSimpleProperties:
    """Simple property-based tests for MCP server database operations."""

    def setup_method(self):
        """Set up test database connection."""
        # Use a test database URL if available, otherwise skip tests
        self.test_dsn = os.getenv("TEST_POSTGRES_DSN") or os.getenv("POSTGRES_DSN")
        if not self.test_dsn:
            pytest.skip("No test database configured")

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
        ),
        metadata=st.dictionaries(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            st.one_of(
                st.text(
                    max_size=100,
                    alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
                ),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_thread_creation_idempotent(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Thread creation should be idempotent - creating the same thread multiple times has the same effect."""

        async def _test():
            import psycopg
            from psycopg.types.json import Jsonb

            conn = await psycopg.AsyncConnection.connect(self.test_dsn)
            try:
                # Create thread first time
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                # Create same thread again
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                # Verify thread exists in database
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1 FROM atlas_thread WHERE thread_id = %s", (thread_id,))
                    assert await cur.fetchone() is not None
            finally:
                await conn.close()

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
        ),
        metadata=st.dictionaries(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            st.one_of(
                st.text(
                    max_size=100,
                    alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
                ),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_user_turn_creation_properties(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Test properties of user turn creation."""

        async def _test():
            import psycopg
            from psycopg.types.json import Jsonb

            conn = await psycopg.AsyncConnection.connect(self.test_dsn)
            try:
                # Ensure thread exists
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                # Create user turn
                turn_id = f"turn_{uuid.uuid4().hex}"
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn
                            (turn_id, thread_id, role, content, metadata)
                        VALUES
                            (%s, %s, 'user', %s, %s)
                        ON CONFLICT (turn_id) DO NOTHING
                        """,
                        (turn_id, thread_id, content, Jsonb(metadata)),
                    )

                # Verify properties
                assert turn_id.startswith("turn_"), "Turn ID should start with 'turn_'"
                assert len(turn_id) > 10, "Turn ID should be reasonably long"

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
            finally:
                await conn.close()

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        user_content=st.text(
            min_size=1,
            max_size=500,
            alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
        ),
        ai_content=st.text(
            min_size=1,
            max_size=500,
            alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
        ),
        metadata=st.dictionaries(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            st.one_of(
                st.text(
                    max_size=100,
                    alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
                ),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_conversation_turn_sequence_properties(
        self,
        thread_id: str,
        user_content: str,
        ai_content: str,
        metadata: dict[str, Any],
    ):
        """Test that conversation turns maintain proper sequence and relationships."""

        async def _test():
            import psycopg
            from psycopg.types.json import Jsonb

            conn = await psycopg.AsyncConnection.connect(self.test_dsn)
            try:
                # Ensure thread exists
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                # Create user turn
                user_turn_id = f"turn_{uuid.uuid4().hex}"
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn
                            (turn_id, thread_id, role, content, metadata)
                        VALUES
                            (%s, %s, 'user', %s, %s)
                        ON CONFLICT (turn_id) DO NOTHING
                        """,
                        (user_turn_id, thread_id, user_content, Jsonb(metadata)),
                    )

                # Create AI turn
                ai_turn_id = f"turn_{uuid.uuid4().hex}"
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn
                            (turn_id, thread_id, role, content, metadata)
                        VALUES
                            (%s, %s, 'assistant', %s, %s)
                        ON CONFLICT (turn_id) DO NOTHING
                        """,
                        (ai_turn_id, thread_id, ai_content, Jsonb(metadata)),
                    )

                # Verify properties
                assert ai_turn_id.startswith("turn_"), "AI turn ID should start with 'turn_'"
                assert user_turn_id.startswith("turn_"), "User turn ID should start with 'turn_'"

                # Verify both turns exist
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT turn_id, role FROM atlas_conversation_turn WHERE thread_id = %s ORDER BY timestamp",
                        (thread_id,),
                    )
                    turns = await cur.fetchall()
                    assert len(turns) == 2, "Both turns should exist"
                    assert result.get("key", "")
                    assert result.get("key", "")
            finally:
                await conn.close()

        asyncio.run(_test())

    @given(
        thread_id=st.text(
            min_size=1,
            max_size=64,
            alphabet=st.characters(min_codepoint=ord("a"), max_codepoint=ord("z")),
        ),
        content=st.text(
            min_size=1,
            max_size=1000,
            alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
        ),
        metadata=st.dictionaries(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            st.one_of(
                st.text(
                    max_size=100,
                    alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
                ),
                st.integers(),
                st.booleans(),
                st.floats(allow_infinity=False, allow_nan=False),
            ),
        ),
    )
    @settings(max_examples=5, deadline=5000)
    def test_metadata_serialization_properties(self, thread_id: str, content: str, metadata: dict[str, Any]):
        """Test that metadata is properly serialized and deserialized."""

        async def _test():
            import psycopg
            from psycopg.types.json import Jsonb

            conn = await psycopg.AsyncConnection.connect(self.test_dsn)
            try:
                # Ensure thread exists
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                # Create turn with metadata
                turn_id = f"turn_{uuid.uuid4().hex}"
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_conversation_turn
                            (turn_id, thread_id, role, content, metadata)
                        VALUES
                            (%s, %s, 'user', %s, %s)
                        ON CONFLICT (turn_id) DO NOTHING
                        """,
                        (turn_id, thread_id, content, Jsonb(metadata)),
                    )

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
            finally:
                await conn.close()

        asyncio.run(_test())

    @given(
        user_queries=st.lists(
            st.text(
                min_size=1,
                max_size=500,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            min_size=1,
            max_size=3,
        ),
        ai_responses=st.lists(
            st.text(
                min_size=1,
                max_size=500,
                alphabet=st.characters(min_codepoint=1, max_codepoint=1114111),
            ),
            min_size=1,
            max_size=3,
        ),
    )
    @settings(max_examples=3, deadline=10000)
    def test_conversation_sequence_properties(self, user_queries: list[str], ai_responses: list[str]):
        """Test properties of conversation sequences."""

        async def _test():
            import psycopg
            from psycopg.types.json import Jsonb

            thread_id = f"thread_{uuid.uuid4().hex[:8]}"

            conn = await psycopg.AsyncConnection.connect(self.test_dsn)
            try:
                # Ensure thread exists
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO atlas_thread(thread_id, session_id, tab_id, title, status, last_activity)
                        VALUES (%s, %s, %s, %s, %s, NOW())
                        ON CONFLICT (thread_id) DO UPDATE
                          SET last_activity = GREATEST(atlas_thread.last_activity, EXCLUDED.last_activity)
                        """,
                        (
                            thread_id,
                            f"session_{uuid.uuid4().hex[:8]}",
                            "cursor_tab",
                            f"Thread {thread_id}",
                            "active",
                        ),
                    )

                turn_ids = []

                # Create alternating user/AI turns
                for i, (query, response) in enumerate(zip(user_queries, ai_responses)):
                    # User turn
                    user_turn_id = f"turn_{uuid.uuid4().hex}"
                    async with conn.cursor() as cur:
                        await cur.execute(
                            """
                            INSERT INTO atlas_conversation_turn
                                (turn_id, thread_id, role, content, metadata)
                            VALUES
                                (%s, %s, 'user', %s, %s)
                            ON CONFLICT (turn_id) DO NOTHING
                            """,
                            (
                                user_turn_id,
                                thread_id,
                                query,
                                Jsonb({"sequence": i, "type": "user"}),
                            ),
                        )
                    turn_ids.append(user_turn_id)

                    # AI turn
                    ai_turn_id = f"turn_{uuid.uuid4().hex}"
                    async with conn.cursor() as cur:
                        await cur.execute(
                            """
                            INSERT INTO atlas_conversation_turn
                                (turn_id, thread_id, role, content, metadata)
                            VALUES
                                (%s, %s, 'assistant', %s, %s)
                            ON CONFLICT (turn_id) DO NOTHING
                            """,
                            (
                                ai_turn_id,
                                thread_id,
                                response,
                                Jsonb({"sequence": i, "type": "ai"}),
                            ),
                        )
                    turn_ids.append(ai_turn_id)

                # Verify sequence properties
                async with conn.cursor() as cur:
                    await cur.execute(
                        "SELECT turn_id, role, content FROM atlas_conversation_turn WHERE thread_id = %s ORDER BY timestamp",
                        (thread_id,),
                    )
                    turns = await cur.fetchall()

                    assert len(turns) == len(turn_ids), "All turns should be stored"

                    # Verify alternating pattern
                    for i, (turn_id, role, content) in enumerate(turns):
                        expected_role = "user" if i % 2 == 0 else "assistant"
                        assert role == expected_role, f"Turn {i} should have role {expected_role}"
            finally:
                await conn.close()

        asyncio.run(_test())
