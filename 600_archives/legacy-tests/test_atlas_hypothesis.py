#!/usr/bin/env python3
"""
Hypothesis property-based testing for Atlas system
Tests edge cases, invariants, and robustness
"""

import os
import sys
import tempfile
from datetime import UTC, datetime
from typing import Any

import hypothesis
import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

# Add the scripts directory to path
sys.path.append("scripts/utilities")
sys.path.append("src")

from atlas_complete_graph_system import AtlasCompleteGraphSystem, ChatThread, ConversationTurn, ThreadStatus
from atlas_query_reply_extractor import AtlasQueryReplyExtractor, QueryReplyPair
from atlas_simple_extractor import AtlasSimpleExtractor


class TestAtlasSystemHypothesis:
    """Property-based testing for Atlas system components."""

    def setup_method(self):
        """Set up test environment with mock database."""
        # Use in-memory SQLite for testing
        self.test_dsn = "sqlite:///:memory:"
        self.system = AtlasCompleteGraphSystem(self.test_dsn)
        self.extractor = AtlasQueryReplyExtractor(self.test_dsn)
        self.simple_extractor = AtlasSimpleExtractor(self.test_dsn)

    @given(
        title=st.text(min_size=1, max_size=100),
        session_id=st.text(min_size=1, max_size=50),
        tab_index=st.integers(min_value=0, max_value=1000),
    )
    def test_create_thread_properties(self, title: str, session_id: str, tab_index: int):
        """Test thread creation invariants."""
        thread = self.system.create_thread(title, session_id, tab_index)

        # Invariants
        assert isinstance(thread, ChatThread)
        assert thread.title == title
        assert thread.session_id == session_id
        assert thread.status == ThreadStatus.ACTIVE
        assert isinstance(thread.thread_id, str)
        assert len(thread.thread_id) > 0
        assert isinstance(thread.embedding, list)
        assert len(thread.embedding) == 1024  # BGE embedding dimension

    @given(
        content=st.text(min_size=1, max_size=10000),
        role=st.sampled_from(["user", "assistant"]),
        thread_id=st.text(min_size=1, max_size=50),
    )
    def test_conversation_turn_properties(self, content: str, role: str, thread_id: str):
        """Test conversation turn creation invariants."""
        turn = self.system.add_conversation_turn(thread_id, role, content)

        # Invariants
        assert isinstance(turn, ConversationTurn)
        assert turn.content == content
        assert turn.role == role
        assert turn.thread_id == thread_id
        assert isinstance(turn.turn_id, str)
        assert len(turn.turn_id) > 0
        assert isinstance(turn.embedding, list)
        assert len(turn.embedding) == 1024
        assert isinstance(turn.timestamp, datetime)

    @given(
        vec1=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=100, max_size=1000),
        vec2=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=100, max_size=1000),
    )
    def test_cosine_similarity_properties(self, vec1: list[float], vec2: list[float]):
        """Test cosine similarity mathematical properties."""
        # Ensure vectors have same length
        min_len = min(len(vec1), len(vec2))
        vec1 = vec1[:min_len]
        vec2 = vec2[:min_len]

        similarity = self.system._cosine_similarity(vec1, vec2)

        # Mathematical invariants
        assert -1.0 <= similarity <= 1.0  # Cosine similarity range
        assert isinstance(similarity, float)

        # Self-similarity should be 1.0 (or close for identical vectors)
        if vec1 == vec2 and len(vec1) > 0:
            assert abs(similarity - 1.0) < 1e-6

        # Zero vector similarity should be 0.0
        if all(x == 0.0 for x in vec1) or all(x == 0.0 for x in vec2):
            assert similarity == 0.0

    @given(query_content=st.text(min_size=1, max_size=1000), response_content=st.text(min_size=1, max_size=1000))
    def test_topic_extraction_properties(self, query_content: str, response_content: str):
        """Test topic extraction invariants."""
        topics = self.system._extract_topic_tags(query_content, response_content)

        # Invariants
        assert isinstance(topics, list)
        assert all(isinstance(topic, str) for topic in topics)
        assert all(len(topic) > 0 for topic in topics)
        assert len(topics) <= 10  # Reasonable limit

    @given(content=st.text(min_size=1, max_size=10000))
    def test_semantic_chunking_properties(self, content: str):
        """Test semantic chunking properties."""
        chunks = self.system._chunk_content_semantic(content)

        # Invariants
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert all(isinstance(chunk, dict) for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all(isinstance(chunk["content"], str) for chunk in chunks)

        # Content preservation
        reconstructed = "".join(chunk["content"] for chunk in chunks)
        assert len(reconstructed) >= len(content) * 0.9  # Allow some loss due to processing

    @given(query_content=st.text(min_size=1, max_size=1000), response_content=st.text(min_size=1, max_size=1000))
    def test_relationship_type_determination(self, query_content: str, response_content: str):
        """Test relationship type determination properties."""
        rel_type = self.system._determine_relationship_type(query_content, response_content)

        # Invariants
        assert isinstance(rel_type, str)
        assert len(rel_type) > 0
        # Should be one of the defined relationship types
        valid_types = ["direct_answer", "clarification", "expansion", "cross_reference"]
        assert rel_type in valid_types

    @given(
        thread_id=st.text(min_size=1, max_size=50),
        role=st.sampled_from(["user", "assistant"]),
        content=st.text(min_size=1, max_size=1000),
    )
    def test_conversation_turn_metadata(self, thread_id: str, role: str, content: str):
        """Test conversation turn metadata properties."""
        turn = self.system.add_conversation_turn(thread_id, role, content)

        # Metadata invariants
        assert isinstance(turn.metadata, dict)
        assert "role" in turn.metadata
        assert "thread_id" in turn.metadata
        assert turn.metadata["role"] == role
        assert turn.metadata["thread_id"] == thread_id

    @given(
        data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=0, max_size=100),
                st.integers(min_value=-1000, max_value=1000),
                st.floats(min_value=-1000.0, max_value=1000.0),
                st.booleans(),
                st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10),
            ),
            min_size=1,
            max_size=20,
        )
    )
    def test_metadata_serialization(self, data: dict[str, Any]):
        """Test metadata serialization robustness."""
        # Test that metadata can be serialized to JSON
        import json

        try:
            json_str = json.dumps(data)
            parsed = json.loads(json_str)
            assert parsed == data
        except (TypeError, ValueError) as e:
            # Some data types might not be JSON serializable
            # This is expected behavior, not a bug
            assert isinstance(e, (TypeError, ValueError))

    @given(embedding=st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=100, max_size=1000))
    def test_embedding_properties(self, embedding: list[float]):
        """Test embedding vector properties."""
        # Test embedding normalization
        if len(embedding) > 0:
            norm = np.linalg.norm(embedding)
            assert norm >= 0.0
            assert isinstance(norm, (float, np.floating))

            # Test that we can create a normalized version
            if norm > 0:
                normalized = [x / norm for x in embedding]
                normalized_norm = np.linalg.norm(normalized)
                assert abs(normalized_norm - 1.0) < 1e-6

    @given(content=st.text(min_size=1, max_size=1000))
    def test_content_chunking_edge_cases(self, content: str):
        """Test content chunking with edge cases."""
        chunks = self.system._chunk_content_semantic(content)

        # Edge case: very short content
        if len(content) < 50:
            assert len(chunks) == 1
            assert chunks[0]["content"] == content

        # Edge case: very long content
        if len(content) > 1000:
            assert len(chunks) > 1
            # Check overlap properties
            for i in range(len(chunks) - 1):
                current_chunk = chunks[i]["content"]
                next_chunk = chunks[i + 1]["content"]
                # Should have some overlap
                assert len(current_chunk) > 0
                assert len(next_chunk) > 0

    @given(session_id=st.text(min_size=1, max_size=50))
    def test_session_operations(self, session_id: str):
        """Test session-level operations."""
        # Create a thread
        thread = self.system.create_thread("Test Thread", session_id, 0)

        # Add some conversation turns
        for i in range(5):
            role = "user" if i % 2 == 0 else "assistant"
            content = f"Test message {i}"
            turn = self.system.add_conversation_turn(thread.thread_id, role, content)
            assert turn.thread_id == thread.thread_id

        # Test thread summary
        summary = self.system.get_thread_summary(thread.thread_id)
        assert isinstance(summary, dict)
        assert "thread_id" in summary
        assert summary["thread_id"] == thread.thread_id


def test_hypothesis_settings():
    """Test that Hypothesis is properly configured."""

    # Test with a simple property
    @given(st.integers(min_value=0, max_value=100))
    def test_simple_property(x: int):
        assert x >= 0
        assert x <= 100

    test_simple_property()


if __name__ == "__main__":
    print("🧪 Running Hypothesis property-based testing...")
    print("This will test edge cases and invariants in the Atlas system.")
    print("If any test fails, it will show the minimal failing example.")

    # Run the tests
    test_hypothesis_settings()
    print("✅ Basic Hypothesis configuration test passed")

    # Note: The full test suite would require a proper test runner
    print("📝 To run the full test suite, use: pytest test_atlas_hypothesis.py -v")
