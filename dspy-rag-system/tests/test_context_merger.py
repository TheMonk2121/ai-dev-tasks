"""
Tests for ContextMerger class

This module tests the context merging functionality for the LTST Memory System.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.context_merger import ContextMerger, ContextMergeResult, MergedContext
from utils.conversation_storage import ConversationContext


class TestContextMerger(unittest.TestCase):
    """Test cases for ContextMerger class."""

    def setUp(self):
        """Set up test environment."""
        self.mock_db_manager = Mock()
        self.context_merger = ContextMerger(self.mock_db_manager)

    def test_init_defaults(self):
        """Test ContextMerger initialization with defaults."""
        merger = ContextMerger()

        self.assertEqual(merger.default_relevance_threshold, 0.7)
        self.assertEqual(merger.default_similarity_threshold, 0.8)
        self.assertEqual(merger.max_contexts_per_merge, 10)
        self.assertEqual(merger.max_merge_content_length, 5000)
        self.assertEqual(merger.cache_ttl, timedelta(minutes=30))

    def test_calculate_semantic_similarity(self):
        """Test semantic similarity calculation."""
        context1 = ConversationContext(
            session_id="test_session", context_type="test", context_key="key1", context_value="hello world test"
        )

        context2 = ConversationContext(
            session_id="test_session", context_type="test", context_key="key2", context_value="hello world example"
        )

        similarity = self.context_merger._calculate_semantic_similarity(context1, context2)

        # Should have some similarity due to "hello world"
        self.assertGreater(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)

    def test_calculate_semantic_similarity_no_overlap(self):
        """Test semantic similarity with no overlap."""
        context1 = ConversationContext(
            session_id="test_session", context_type="test", context_key="key1", context_value="hello world"
        )

        context2 = ConversationContext(
            session_id="test_session", context_type="test", context_key="key2", context_value="completely different"
        )

        similarity = self.context_merger._calculate_semantic_similarity(context1, context2)
        self.assertEqual(similarity, 0.0)

    def test_merge_context_content_single(self):
        """Test merging single context."""
        context = ConversationContext(
            session_id="test_session", context_type="test", context_key="key1", context_value="test content"
        )

        merged = self.context_merger._merge_context_content([context])
        self.assertEqual(merged, "test content")

    def test_merge_context_content_multiple(self):
        """Test merging multiple contexts."""
        contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key1",
                context_value="first content",
                relevance_score=0.9,
            ),
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key2",
                context_value="second content",
                relevance_score=0.7,
            ),
        ]

        merged = self.context_merger._merge_context_content(contexts)
        self.assertIn("first content", merged)
        self.assertIn("second content", merged)

    def test_select_relevant_contexts(self):
        """Test relevant context selection."""
        contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key1",
                context_value="high relevance",
                relevance_score=0.9,
            ),
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key2",
                context_value="low relevance",
                relevance_score=0.3,
            ),
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key3",
                context_value="medium relevance",
                relevance_score=0.7,
            ),
        ]

        relevant = self.context_merger._select_relevant_contexts(contexts, 0.7)

        self.assertEqual(len(relevant), 2)
        self.assertEqual(relevant[0].relevance_score, 0.9)
        self.assertEqual(relevant[1].relevance_score, 0.7)

    def test_group_similar_contexts(self):
        """Test grouping similar contexts."""
        contexts = [
            ConversationContext(
                session_id="test_session", context_type="test", context_key="key1", context_value="hello world test"
            ),
            ConversationContext(
                session_id="test_session", context_type="test", context_key="key2", context_value="hello world example"
            ),
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key3",
                context_value="completely different content",
            ),
        ]

        groups = self.context_merger._group_similar_contexts(contexts, 0.5)

        # Should have 2 groups: similar contexts and different context
        self.assertEqual(len(groups), 2)
        self.assertGreater(len(groups[0]), 1)  # Similar contexts grouped together

    def test_merge_contexts_empty(self):
        """Test merging empty context list."""
        with patch.object(self.context_merger, "_get_cached_contexts", return_value=None):
            with patch.object(self.context_merger.mock_db_manager, "get_connection") as mock_conn:
                mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = (
                    []
                )

                result = self.context_merger.merge_contexts("test_session")

                self.assertEqual(len(result.merged_contexts), 0)
                self.assertEqual(result.total_contexts_processed, 0)
                self.assertEqual(result.contexts_merged, 0)
                self.assertEqual(result.contexts_preserved, 0)

    def test_merge_contexts_single(self):
        """Test merging single context."""
        context = ConversationContext(
            session_id="test_session",
            context_type="test",
            context_key="key1",
            context_value="test content",
            relevance_score=0.8,
        )

        mock_row = {
            "session_id": context.session_id,
            "context_type": context.context_type,
            "context_key": context.context_key,
            "context_value": context.context_value,
            "relevance_score": context.relevance_score,
            "metadata": context.metadata,
            "expires_at": context.expires_at,
        }

        with patch.object(self.context_merger, "_get_cached_contexts", return_value=None):
            with patch.object(self.context_merger.mock_db_manager, "get_connection") as mock_conn:
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = [mock_row]
                mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

                result = self.context_merger.merge_contexts("test_session")

                self.assertEqual(len(result.merged_contexts), 1)
                self.assertEqual(result.contexts_preserved, 1)
                self.assertEqual(result.contexts_merged, 0)

    def test_merge_conversation_context(self):
        """Test conversation context merging."""
        mock_messages = [
            {"role": "human", "content": "Hello", "timestamp": datetime.now()},
            {"role": "ai", "content": "Hi there!", "timestamp": datetime.now()},
            {"role": "human", "content": "How are you?", "timestamp": datetime.now()},
        ]

        with patch.object(self.context_merger.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = mock_messages
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            result = self.context_merger.merge_conversation_context("test_session")

            self.assertIsNotNone(result)
            self.assertIn("User: Hello", result)
            self.assertIn("Assistant: Hi there!", result)
            self.assertIn("User: How are you?", result)

    def test_get_context_summary(self):
        """Test context summary generation."""
        mock_summary_data = [
            {"context_type": "conversation", "count": 5, "avg_relevance": 0.8},
            {"context_type": "preference", "count": 3, "avg_relevance": 0.9},
        ]

        with patch.object(self.context_merger.mock_db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = mock_summary_data
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            summary = self.context_merger.get_context_summary("test_session")

            self.assertEqual(summary["session_id"], "test_session")
            self.assertEqual(summary["total_contexts"], 8)
            self.assertIn("conversation", summary["context_types"])
            self.assertIn("preference", summary["context_types"])

    def test_cleanup_expired_cache(self):
        """Test cache cleanup functionality."""
        # Add some expired cache entries
        self.context_merger.context_cache["expired_key"] = ["data"]
        self.context_merger.cache_timestamps["expired_key"] = datetime.now() - timedelta(hours=1)

        # Add a fresh cache entry
        self.context_merger.context_cache["fresh_key"] = ["data"]
        self.context_merger.cache_timestamps["fresh_key"] = datetime.now()

        cleaned = self.context_merger.cleanup_expired_cache()

        self.assertEqual(cleaned, 1)
        self.assertNotIn("expired_key", self.context_merger.context_cache)
        self.assertIn("fresh_key", self.context_merger.context_cache)

    def test_get_merge_statistics(self):
        """Test merge statistics generation."""
        stats = self.context_merger.get_merge_statistics()

        self.assertIn("cache_size", stats)
        self.assertIn("default_relevance_threshold", stats)
        self.assertIn("default_similarity_threshold", stats)
        self.assertIn("max_contexts_per_merge", stats)
        self.assertIn("max_merge_content_length", stats)

    def test_cache_functionality(self):
        """Test caching functionality."""
        contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key1",
                context_value="cached content",
                relevance_score=0.8,
            )
        ]

        # Cache contexts
        self.context_merger._cache_contexts("test_session", "test", contexts)

        # Retrieve from cache
        cached = self.context_merger._get_cached_contexts("test_session", "test")

        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0].context_value, "cached content")

    def test_cache_expiration(self):
        """Test cache expiration."""
        contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key1",
                context_value="expired content",
                relevance_score=0.8,
            )
        ]

        # Cache with old timestamp
        self.context_merger._cache_contexts("test_session", "test", contexts)
        self.context_merger.cache_timestamps["test_session:test"] = datetime.now() - timedelta(hours=1)

        # Should not retrieve expired cache
        cached = self.context_merger._get_cached_contexts("test_session", "test")

        self.assertIsNone(cached)

    def test_merged_context_creation(self):
        """Test MergedContext creation."""
        source_contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key="key1",
                context_value="source content",
                relevance_score=0.8,
            )
        ]

        merged_context = MergedContext(
            session_id="test_session",
            context_type="test",
            merged_content="merged content",
            source_contexts=source_contexts,
            relevance_score=0.8,
            semantic_similarity=0.9,
            merge_timestamp=datetime.now(),
            metadata={"test": "data"},
        )

        self.assertEqual(merged_context.session_id, "test_session")
        self.assertEqual(merged_context.context_type, "test")
        self.assertEqual(merged_context.merged_content, "merged content")
        self.assertEqual(len(merged_context.source_contexts), 1)
        self.assertEqual(merged_context.relevance_score, 0.8)
        self.assertEqual(merged_context.semantic_similarity, 0.9)
        self.assertIn("test", merged_context.metadata)

    def test_context_merge_result_creation(self):
        """Test ContextMergeResult creation."""
        result = ContextMergeResult(
            merged_contexts=[],
            total_contexts_processed=10,
            contexts_merged=5,
            contexts_preserved=5,
            merge_time_ms=100.5,
            relevance_threshold=0.7,
            similarity_threshold=0.8,
        )

        self.assertEqual(result.total_contexts_processed, 10)
        self.assertEqual(result.contexts_merged, 5)
        self.assertEqual(result.contexts_preserved, 5)
        self.assertEqual(result.merge_time_ms, 100.5)
        self.assertEqual(result.relevance_threshold, 0.7)
        self.assertEqual(result.similarity_threshold, 0.8)

    def test_error_handling(self):
        """Test error handling in context merging."""
        with patch.object(self.context_merger, "_get_cached_contexts", side_effect=Exception("Database error")):
            with self.assertRaises(Exception):
                self.context_merger.merge_contexts("test_session")

    def test_performance_benchmarks(self):
        """Test that merging meets performance benchmarks."""
        # Create test contexts
        contexts = [
            ConversationContext(
                session_id="test_session",
                context_type="test",
                context_key=f"key{i}",
                context_value=f"content {i}",
                relevance_score=0.8,
            )
            for i in range(20)
        ]

        with patch.object(self.context_merger, "_get_cached_contexts", return_value=contexts):
            start_time = datetime.now()
            result = self.context_merger.merge_contexts("test_session")
            end_time = datetime.now()

            # Should complete within reasonable time (less than 1 second)
            duration_ms = (end_time - start_time).total_seconds() * 1000
            self.assertLess(duration_ms, 1000)

            # Should process all contexts
            self.assertEqual(result.total_contexts_processed, 20)


if __name__ == "__main__":
    unittest.main()
