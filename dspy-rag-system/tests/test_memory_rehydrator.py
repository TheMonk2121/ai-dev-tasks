"""
Tests for MemoryRehydrator class

This module tests the memory rehydration functionality for the LTST Memory System.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.conversation_storage import ConversationContext, ConversationMessage
from utils.memory_rehydrator import MemoryRehydrator, RehydrationRequest, RehydrationResult


class TestMemoryRehydrator(unittest.TestCase):
    """Test cases for MemoryRehydrator class."""

    def setUp(self):
        """Set up test environment."""
        self.mock_db_manager = Mock()
        self.memory_rehydrator = MemoryRehydrator(self.mock_db_manager)

    def test_init_defaults(self):
        """Test MemoryRehydrator initialization with defaults."""
        rehydrator = MemoryRehydrator()

        self.assertEqual(rehydrator.default_relevance_threshold, 0.7)
        self.assertEqual(rehydrator.default_similarity_threshold, 0.8)
        self.assertEqual(rehydrator.max_conversation_history, 50)
        self.assertEqual(rehydrator.max_context_length, 10000)
        self.assertEqual(rehydrator.session_continuity_window, timedelta(hours=24))
        self.assertEqual(rehydrator.cache_ttl, timedelta(minutes=15))

    def test_rehydration_request_creation(self):
        """Test RehydrationRequest creation."""
        request = RehydrationRequest(
            session_id="test_session",
            user_id="test_user",
            current_message="Hello world",
            context_types=["conversation", "preference"],
            max_context_length=5000,
            include_conversation_history=True,
            history_limit=10,
            relevance_threshold=0.8,
            similarity_threshold=0.9,
        )

        self.assertEqual(request.session_id, "test_session")
        self.assertEqual(request.user_id, "test_user")
        self.assertEqual(request.current_message, "Hello world")
        self.assertEqual(request.context_types, ["conversation", "preference"])
        self.assertEqual(request.max_context_length, 5000)
        self.assertTrue(request.include_conversation_history)
        self.assertEqual(request.history_limit, 10)
        self.assertEqual(request.relevance_threshold, 0.8)
        self.assertEqual(request.similarity_threshold, 0.9)

    def test_rehydration_request_defaults(self):
        """Test RehydrationRequest default values."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user")

        self.assertEqual(request.context_types, ["conversation", "preference", "project", "user_info"])
        self.assertEqual(request.max_context_length, 10000)
        self.assertTrue(request.include_conversation_history)
        self.assertEqual(request.history_limit, 20)
        self.assertEqual(request.relevance_threshold, 0.7)
        self.assertEqual(request.similarity_threshold, 0.8)
        self.assertEqual(request.metadata, {})

    def test_rehydration_result_creation(self):
        """Test RehydrationResult creation."""
        result = RehydrationResult(
            session_id="test_session",
            user_id="test_user",
            rehydrated_context="Test context",
            conversation_history=[],
            user_preferences={},
            project_context={},
            relevant_contexts=[],
            merged_contexts=[],
            session_continuity_score=0.8,
            context_relevance_scores={"overall": 0.7},
            rehydration_time_ms=100.5,
            cache_hit=False,
            metadata={"test": "data"},
        )

        self.assertEqual(result.session_id, "test_session")
        self.assertEqual(result.user_id, "test_user")
        self.assertEqual(result.rehydrated_context, "Test context")
        self.assertEqual(result.session_continuity_score, 0.8)
        self.assertEqual(result.rehydration_time_ms, 100.5)
        self.assertFalse(result.cache_hit)
        self.assertIn("test", result.metadata)

    def test_generate_cache_key(self):
        """Test cache key generation."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user", current_message="Hello world")

        cache_key = self.memory_rehydrator._generate_cache_key(request)

        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 64)  # SHA-256 hash length

    def test_detect_session_continuity_no_sessions(self):
        """Test session continuity detection with no recent sessions."""
        with patch.object(self.memory_rehydrator.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            continuity_score = self.memory_rehydrator._detect_session_continuity("test_session", "test_user")

            self.assertEqual(continuity_score, 0.0)

    def test_detect_session_continuity_current_session(self):
        """Test session continuity detection with current session."""
        mock_session = {
            "session_id": "test_session",
            "last_activity": datetime.now(),
            "session_name": "Test Session",
            "context_summary": "Test context",
        }

        with patch.object(self.memory_rehydrator.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [mock_session]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            continuity_score = self.memory_rehydrator._detect_session_continuity("test_session", "test_user")

            self.assertEqual(continuity_score, 0.9)

    def test_get_conversation_history(self):
        """Test conversation history retrieval."""
        mock_messages = [
            {
                "session_id": "test_session",
                "role": "human",
                "content": "Hello",
                "message_type": "message",
                "message_index": 1,
                "parent_message_id": None,
                "metadata": {},
                "embedding": None,
                "relevance_score": 0.8,
                "is_context_message": False,
                "timestamp": datetime.now(),
            },
            {
                "session_id": "test_session",
                "role": "ai",
                "content": "Hi there!",
                "message_type": "message",
                "message_index": 2,
                "parent_message_id": None,
                "metadata": {},
                "embedding": None,
                "relevance_score": 0.8,
                "is_context_message": False,
                "timestamp": datetime.now(),
            },
        ]

        with patch.object(self.memory_rehydrator.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = mock_messages
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            history = self.memory_rehydrator._get_conversation_history("test_session", 10)

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].role, "human")
            self.assertEqual(history[0].content, "Hello")
            self.assertEqual(history[1].role, "ai")
            self.assertEqual(history[1].content, "Hi there!")

    def test_get_user_preferences(self):
        """Test user preferences retrieval."""
        mock_preferences = [
            {"preference_key": "language", "preference_value": "English", "metadata": {"confidence": 0.9}},
            {"preference_key": "theme", "preference_value": "dark", "metadata": {"confidence": 0.8}},
        ]

        with patch.object(self.memory_rehydrator.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = mock_preferences
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            preferences = self.memory_rehydrator._get_user_preferences("test_user")

            self.assertEqual(len(preferences), 2)
            self.assertEqual(preferences["language"]["value"], "English")
            self.assertEqual(preferences["theme"]["value"], "dark")

    def test_calculate_context_relevance_scores(self):
        """Test context relevance score calculation."""
        conversation_history = [
            ConversationMessage(session_id="test_session", role="human", content="Hello", relevance_score=0.8),
            ConversationMessage(session_id="test_session", role="ai", content="Hi there!", relevance_score=0.9),
        ]

        user_preferences = {"language": {"value": "English"}}
        project_context = {"current_task": {"content": "Test task", "relevance": 0.7}}
        relevant_contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="conversation",
                context_key="key1",
                context_value="Test context",
                relevance_score=0.8,
            )
        ]

        scores = self.memory_rehydrator._calculate_context_relevance_scores(
            conversation_history, user_preferences, project_context, relevant_contexts, "Current message"
        )

        self.assertIn("conversation_history", scores)
        self.assertIn("user_preferences", scores)
        self.assertIn("project_context", scores)
        self.assertIn("relevant_contexts", scores)
        self.assertIn("overall", scores)

        self.assertGreater(scores["overall"], 0.0)
        self.assertLessEqual(scores["overall"], 1.0)

    def test_merge_rehydrated_context(self):
        """Test rehydrated context merging."""
        conversation_history = [
            ConversationMessage(session_id="test_session", role="human", content="Hello", relevance_score=0.8),
            ConversationMessage(session_id="test_session", role="ai", content="Hi there!", relevance_score=0.9),
        ]

        user_preferences = {"language": {"value": "English"}}
        project_context = {"current_task": {"content": "Test task", "relevance": 0.7}}
        relevant_contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="conversation",
                context_key="key1",
                context_value="Test context",
                relevance_score=0.8,
            )
        ]

        merged_context = self.memory_rehydrator._merge_rehydrated_context(
            conversation_history, user_preferences, project_context, relevant_contexts, "Current message", 10000
        )

        self.assertIn("Conversation History:", merged_context)
        self.assertIn("User Preferences:", merged_context)
        self.assertIn("Project Context:", merged_context)
        self.assertIn("Relevant Context:", merged_context)
        self.assertIn("Current Message:", merged_context)
        self.assertIn("Hello", merged_context)
        self.assertIn("Hi there!", merged_context)

    def test_merge_rehydrated_context_truncation(self):
        """Test rehydrated context truncation."""
        # Create a very long context
        long_content = "Very long content " * 1000

        merged_context = self.memory_rehydrator._merge_rehydrated_context(
            [], {}, {"test": {"content": long_content, "relevance": 0.7}}, [], "Current message", 1000  # Short limit
        )

        self.assertLess(len(merged_context), 1100)  # Allow some buffer
        self.assertIn("[Content truncated", merged_context)

    def test_rehydrate_memory_cache_hit(self):
        """Test memory rehydration with cache hit."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user")

        cached_result = RehydrationResult(
            session_id="test_session",
            user_id="test_user",
            rehydrated_context="Cached context",
            conversation_history=[],
            user_preferences={},
            project_context={},
            relevant_contexts=[],
            merged_contexts=[],
            session_continuity_score=0.8,
            context_relevance_scores={"overall": 0.7},
            rehydration_time_ms=50.0,
            cache_hit=True,
            metadata={},
        )

        with patch.object(self.memory_rehydrator, "_get_cached_rehydration", return_value=cached_result):
            result = self.memory_rehydrator.rehydrate_memory(request)

            self.assertEqual(result, cached_result)
            self.assertTrue(result.cache_hit)

    def test_rehydrate_memory_full_process(self):
        """Test full memory rehydration process."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user", current_message="Hello world")

        # Mock all the internal methods
        with (
            patch.object(self.memory_rehydrator, "_get_cached_rehydration", return_value=None),
            patch.object(self.memory_rehydrator, "_detect_session_continuity", return_value=0.8),
            patch.object(self.memory_rehydrator, "_get_conversation_history", return_value=[]),
            patch.object(self.memory_rehydrator, "_get_user_preferences", return_value={}),
            patch.object(self.memory_rehydrator, "_get_project_context", return_value={}),
            patch.object(self.memory_rehydrator, "_get_relevant_contexts", return_value=[]),
            patch.object(self.memory_rehydrator, "_calculate_context_relevance_scores", return_value={"overall": 0.7}),
            patch.object(self.memory_rehydrator, "_merge_rehydrated_context", return_value="Merged context"),
            patch.object(self.memory_rehydrator, "_cache_rehydration"),
        ):

            result = self.memory_rehydrator.rehydrate_memory(request)

            self.assertEqual(result.session_id, "test_session")
            self.assertEqual(result.user_id, "test_user")
            self.assertEqual(result.rehydrated_context, "Merged context")
            self.assertEqual(result.session_continuity_score, 0.8)
            self.assertFalse(result.cache_hit)
            self.assertGreater(result.rehydration_time_ms, 0)

    def test_get_rehydration_statistics(self):
        """Test rehydration statistics generation."""
        stats = self.memory_rehydrator.get_rehydration_statistics()

        self.assertIn("cache_size", stats)
        self.assertIn("cache_ttl_seconds", stats)
        self.assertIn("default_relevance_threshold", stats)
        self.assertIn("default_similarity_threshold", stats)
        self.assertIn("max_conversation_history", stats)
        self.assertIn("max_context_length", stats)
        self.assertIn("session_continuity_window_hours", stats)

    def test_cleanup_expired_cache(self):
        """Test cache cleanup functionality."""
        # Add some expired cache entries
        self.memory_rehydrator.rehydration_cache["expired_key"] = Mock()
        self.memory_rehydrator.cache_timestamps["expired_key"] = datetime.now() - timedelta(hours=1)

        # Add a fresh cache entry
        self.memory_rehydrator.rehydration_cache["fresh_key"] = Mock()
        self.memory_rehydrator.cache_timestamps["fresh_key"] = datetime.now()

        cleaned = self.memory_rehydrator.cleanup_expired_cache()

        self.assertEqual(cleaned, 1)
        self.assertNotIn("expired_key", self.memory_rehydrator.rehydration_cache)
        self.assertIn("fresh_key", self.memory_rehydrator.rehydration_cache)

    def test_error_handling(self):
        """Test error handling in memory rehydration."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user")

        with patch.object(self.memory_rehydrator, "_get_cached_rehydration", side_effect=Exception("Database error")):
            with self.assertRaises(Exception):
                self.memory_rehydrator.rehydrate_memory(request)

    def test_performance_benchmarks(self):
        """Test that rehydration meets performance benchmarks."""
        request = RehydrationRequest(session_id="test_session", user_id="test_user")

        # Mock all methods to return minimal data
        with (
            patch.object(self.memory_rehydrator, "_get_cached_rehydration", return_value=None),
            patch.object(self.memory_rehydrator, "_detect_session_continuity", return_value=0.8),
            patch.object(self.memory_rehydrator, "_get_conversation_history", return_value=[]),
            patch.object(self.memory_rehydrator, "_get_user_preferences", return_value={}),
            patch.object(self.memory_rehydrator, "_get_project_context", return_value={}),
            patch.object(self.memory_rehydrator, "_get_relevant_contexts", return_value=[]),
            patch.object(self.memory_rehydrator, "_calculate_context_relevance_scores", return_value={"overall": 0.7}),
            patch.object(self.memory_rehydrator, "_merge_rehydrated_context", return_value="Test context"),
            patch.object(self.memory_rehydrator, "_cache_rehydration"),
        ):

            start_time = datetime.now()
            result = self.memory_rehydrator.rehydrate_memory(request)
            end_time = datetime.now()

            # Should complete within 5 seconds (5000ms)
            duration_ms = (end_time - start_time).total_seconds() * 1000
            self.assertLess(duration_ms, 5000)

            # Should have reasonable rehydration time
            self.assertLess(result.rehydration_time_ms, 5000)

    def test_session_similarity_calculation(self):
        """Test session similarity calculation."""
        session1 = {"session_name": "Test Project Discussion", "context_summary": "Working on LTST memory system"}

        session2 = {"session_name": "Project Discussion", "context_summary": "LTST memory system implementation"}

        similarity = self.memory_rehydrator._calculate_session_similarity(session1, session2)

        # Should have some similarity due to common words
        self.assertGreater(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_session_similarity_no_overlap(self):
        """Test session similarity with no overlap."""
        session1 = {"session_name": "Test Project", "context_summary": "Working on memory system"}

        session2 = {"session_name": "Different Topic", "context_summary": "Completely unrelated content"}

        similarity = self.memory_rehydrator._calculate_session_similarity(session1, session2)

        # Should have low similarity
        self.assertLess(similarity, 0.5)


if __name__ == "__main__":
    unittest.main()
