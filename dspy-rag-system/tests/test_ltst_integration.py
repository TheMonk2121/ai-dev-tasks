"""
Integration Tests for LTST Memory System

This module tests the complete LTST Memory System integration,
including end-to-end workflows, performance benchmarks, and error scenarios.
"""

import os
import sys
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.context_merger import ContextMergeResult
from utils.conversation_storage import ConversationMessage
from utils.ltst_memory_system import LTSTMemorySystem, MemoryOperation, SystemHealth
from utils.memory_rehydrator import RehydrationResult


class TestLTSTIntegration(unittest.TestCase):
    """Integration tests for LTST Memory System."""

    def setUp(self):
        """Set up test environment."""
        self.mock_db_manager = Mock()
        self.ltst_system = LTSTMemorySystem(self.mock_db_manager)

    def test_system_initialization(self):
        """Test system initialization and component setup."""
        # Verify all components are initialized
        self.assertIsNotNone(self.ltst_system.conversation_storage)
        self.assertIsNotNone(self.ltst_system.context_merger)
        self.assertIsNotNone(self.ltst_system.memory_rehydrator)

        # Verify configuration
        self.assertTrue(self.ltst_system.enable_caching)
        self.assertTrue(self.ltst_system.enable_monitoring)
        self.assertEqual(self.ltst_system.max_operation_history, 1000)
        self.assertEqual(self.ltst_system.default_session_timeout, timedelta(hours=24))

    def test_end_to_end_conversation_workflow(self):
        """Test complete conversation workflow."""
        session_id = "test_session_001"
        user_id = "test_user_001"

        # Step 1: Store conversation messages
        with (
            patch.object(self.ltst_system.conversation_storage, "create_session", return_value=True),
            patch.object(self.ltst_system.conversation_storage, "store_message", return_value=True),
        ):

            # Store human message
            success1 = self.ltst_system.store_conversation_message(
                session_id=session_id,
                user_id=user_id,
                role="human",
                content="Hello, how are you?",
                message_type="message",
            )
            self.assertTrue(success1)

            # Store AI response
            success2 = self.ltst_system.store_conversation_message(
                session_id=session_id,
                user_id=user_id,
                role="ai",
                content="I'm doing well, thank you! How can I help you today?",
                message_type="message",
            )
            self.assertTrue(success2)

        # Step 2: Store context
        with patch.object(self.ltst_system.conversation_storage, "store_context", return_value=True):
            context_success = self.ltst_system.store_context(
                session_id=session_id,
                context_type="preference",
                context_key="language",
                context_value="English",
                relevance_score=0.9,
            )
            self.assertTrue(context_success)

        # Step 3: Retrieve conversation history
        with patch.object(self.ltst_system.conversation_storage, "get_messages") as mock_get_messages:
            mock_messages = [
                ConversationMessage(
                    session_id=session_id,
                    role="human",
                    content="Hello, how are you?",
                    message_type="message",
                    message_index=1,
                ),
                ConversationMessage(
                    session_id=session_id,
                    role="ai",
                    content="I'm doing well, thank you! How can I help you today?",
                    message_type="message",
                    message_index=2,
                ),
            ]
            mock_get_messages.return_value = mock_messages

            history = self.ltst_system.retrieve_conversation_history(session_id, limit=10)
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0].role, "human")
            self.assertEqual(history[1].role, "ai")

        # Step 4: Merge contexts
        with patch.object(self.ltst_system.context_merger, "merge_contexts") as mock_merge:
            mock_result = ContextMergeResult(
                merged_contexts=[],
                total_contexts_processed=1,
                contexts_merged=0,
                contexts_preserved=1,
                merge_time_ms=50.0,
                relevance_threshold=0.7,
                similarity_threshold=0.8,
            )
            mock_merge.return_value = mock_result

            merge_result = self.ltst_system.merge_contexts(session_id)
            self.assertEqual(merge_result.total_contexts_processed, 1)
            self.assertEqual(merge_result.contexts_preserved, 1)

        # Step 5: Rehydrate memory
        with patch.object(self.ltst_system.memory_rehydrator, "rehydrate_memory") as mock_rehydrate:
            mock_rehydration_result = RehydrationResult(
                session_id=session_id,
                user_id=user_id,
                rehydrated_context="Test context",
                conversation_history=mock_messages,
                user_preferences={},
                project_context={},
                relevant_contexts=[],
                merged_contexts=[],
                session_continuity_score=0.8,
                context_relevance_scores={"overall": 0.7},
                rehydration_time_ms=100.0,
                cache_hit=False,
                metadata={},
            )
            mock_rehydrate.return_value = mock_rehydration_result

            rehydration_result = self.ltst_system.rehydrate_memory(
                session_id=session_id, user_id=user_id, current_message="What's next?"
            )
            self.assertEqual(rehydration_result.session_id, session_id)
            self.assertEqual(rehydration_result.user_id, user_id)
            self.assertFalse(rehydration_result.cache_hit)

    def test_performance_benchmarks(self):
        """Test that the system meets performance benchmarks."""
        session_id = "perf_test_session"
        user_id = "perf_test_user"

        # Test message storage performance
        with (
            patch.object(self.ltst_system.conversation_storage, "create_session", return_value=True),
            patch.object(self.ltst_system.conversation_storage, "store_message", return_value=True),
        ):

            start_time = time.time()
            success = self.ltst_system.store_conversation_message(
                session_id=session_id, user_id=user_id, role="human", content="Performance test message"
            )
            duration_ms = (time.time() - start_time) * 1000

            self.assertTrue(success)
            self.assertLess(duration_ms, 200)  # Should complete within 200ms

        # Test conversation retrieval performance
        with patch.object(self.ltst_system.conversation_storage, "get_messages", return_value=[]):
            start_time = time.time()
            history = self.ltst_system.retrieve_conversation_history(session_id)
            duration_ms = (time.time() - start_time) * 1000

            self.assertLess(duration_ms, 2000)  # Should complete within 2 seconds

        # Test memory rehydration performance
        with patch.object(self.ltst_system.memory_rehydrator, "rehydrate_memory") as mock_rehydrate:
            mock_result = RehydrationResult(
                session_id=session_id,
                user_id=user_id,
                rehydrated_context="Test context",
                conversation_history=[],
                user_preferences={},
                project_context={},
                relevant_contexts=[],
                merged_contexts=[],
                session_continuity_score=0.8,
                context_relevance_scores={"overall": 0.7},
                rehydration_time_ms=100.0,
                cache_hit=False,
                metadata={},
            )
            mock_rehydrate.return_value = mock_result

            start_time = time.time()
            result = self.ltst_system.rehydrate_memory(session_id, user_id)
            duration_ms = (time.time() - start_time) * 1000

            self.assertLess(duration_ms, 5000)  # Should complete within 5 seconds

    def test_error_scenarios_and_recovery(self):
        """Test error scenarios and recovery mechanisms."""
        session_id = "error_test_session"
        user_id = "error_test_user"

        # Test database connection failure
        with patch.object(
            self.ltst_system.conversation_storage, "create_session", side_effect=Exception("Database error")
        ):
            success = self.ltst_system.store_conversation_message(
                session_id=session_id, user_id=user_id, role="human", content="Test message"
            )
            self.assertFalse(success)

        # Test context storage failure
        with patch.object(self.ltst_system.conversation_storage, "store_context", return_value=False):
            success = self.ltst_system.store_context(
                session_id=session_id, context_type="test", context_key="key", context_value="value"
            )
            self.assertFalse(success)

        # Test conversation retrieval failure
        with patch.object(
            self.ltst_system.conversation_storage, "get_messages", side_effect=Exception("Retrieval error")
        ):
            history = self.ltst_system.retrieve_conversation_history(session_id)
            self.assertEqual(history, [])

        # Test context merging failure
        with patch.object(self.ltst_system.context_merger, "merge_contexts", side_effect=Exception("Merge error")):
            with self.assertRaises(Exception):
                self.ltst_system.merge_contexts(session_id)

        # Test memory rehydration failure
        with patch.object(
            self.ltst_system.memory_rehydrator, "rehydrate_memory", side_effect=Exception("Rehydration error")
        ):
            with self.assertRaises(Exception):
                self.ltst_system.rehydrate_memory(session_id, user_id)

    def test_data_integrity(self):
        """Test data integrity across operations."""
        session_id = "integrity_test_session"
        user_id = "integrity_test_user"

        # Test message storage and retrieval integrity
        test_message = "Test message for integrity check"

        with (
            patch.object(self.ltst_system.conversation_storage, "create_session", return_value=True),
            patch.object(self.ltst_system.conversation_storage, "store_message", return_value=True),
            patch.object(self.ltst_system.conversation_storage, "get_messages") as mock_get_messages,
        ):

            # Store message
            success = self.ltst_system.store_conversation_message(
                session_id=session_id, user_id=user_id, role="human", content=test_message
            )
            self.assertTrue(success)

            # Mock retrieval to verify content
            mock_messages = [
                ConversationMessage(
                    session_id=session_id, role="human", content=test_message, message_type="message", message_index=1
                )
            ]
            mock_get_messages.return_value = mock_messages

            # Retrieve and verify
            history = self.ltst_system.retrieve_conversation_history(session_id)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0].content, test_message)
            self.assertEqual(history[0].role, "human")

        # Test context storage and retrieval integrity
        test_context_key = "test_key"
        test_context_value = "test_value"

        with patch.object(self.ltst_system.conversation_storage, "store_context", return_value=True):
            success = self.ltst_system.store_context(
                session_id=session_id,
                context_type="test",
                context_key=test_context_key,
                context_value=test_context_value,
                relevance_score=0.8,
            )
            self.assertTrue(success)

    def test_system_health_monitoring(self):
        """Test system health monitoring functionality."""
        # Test health check with mock database connection
        with (
            patch.object(self.ltst_system, "_check_database_connection", return_value=True),
            patch.object(self.ltst_system, "_get_active_sessions_count", return_value=5),
        ):

            health = self.ltst_system.get_system_health()

            self.assertTrue(health.database_connected)
            self.assertEqual(health.active_sessions, 5)
            self.assertIsInstance(health.cache_size, int)
            self.assertIsInstance(health.total_operations, int)
            self.assertIsInstance(health.error_rate, float)
            self.assertIsInstance(health.average_response_time_ms, float)
            self.assertIsInstance(health.component_status, dict)

        # Test health check with database failure
        with patch.object(self.ltst_system, "_check_database_connection", return_value=False):
            health = self.ltst_system.get_system_health()

            self.assertFalse(health.database_connected)
            # When database is disconnected, error rate should be 1.0 (all operations fail)
            # But if no operations have been recorded yet, error rate will be 0.0
            # So we need to add some failed operations first
            self.ltst_system._record_operation("test", "session", "user", 10.0, False, "Database error")
            health = self.ltst_system.get_system_health()
            self.assertEqual(health.error_rate, 1.0)

    def test_operation_monitoring(self):
        """Test operation monitoring and statistics."""
        session_id = "monitor_test_session"
        user_id = "monitor_test_user"

        # Perform some operations
        with (
            patch.object(self.ltst_system.conversation_storage, "create_session", return_value=True),
            patch.object(self.ltst_system.conversation_storage, "store_message", return_value=True),
        ):

            # Store a message
            self.ltst_system.store_conversation_message(
                session_id=session_id, user_id=user_id, role="human", content="Test message"
            )

            # Verify operation was recorded
            self.assertGreater(len(self.ltst_system.operation_history), 0)

            # Check operation details
            last_operation = self.ltst_system.operation_history[-1]
            self.assertEqual(last_operation.operation_type, "store")
            self.assertEqual(last_operation.session_id, session_id)
            self.assertEqual(last_operation.user_id, user_id)
            self.assertTrue(last_operation.success)
            self.assertGreater(last_operation.duration_ms, 0)

        # Test operation history trimming
        # Add many operations using the proper method to trigger trimming
        original_history_size = len(self.ltst_system.operation_history)

        for i in range(1100):  # More than max_operation_history
            self.ltst_system._record_operation(
                operation_type="test", session_id=f"session_{i}", user_id=f"user_{i}", duration_ms=10.0, success=True
            )

        # Verify history was trimmed
        self.assertLessEqual(len(self.ltst_system.operation_history), self.ltst_system.max_operation_history)

    def test_cleanup_functionality(self):
        """Test cleanup functionality across all components."""
        # Test cleanup with mock components
        with (
            patch.object(self.ltst_system.conversation_storage, "cleanup_expired_data", return_value=True),
            patch.object(self.ltst_system.context_merger, "cleanup_expired_cache", return_value=5),
            patch.object(self.ltst_system.memory_rehydrator, "cleanup_expired_cache", return_value=3),
        ):

            cleanup_stats = self.ltst_system.cleanup_expired_data()

            self.assertIn("conversation_context", cleanup_stats)
            self.assertIn("context_cache", cleanup_stats)
            self.assertIn("rehydration_cache", cleanup_stats)
            self.assertEqual(cleanup_stats["context_cache"], 5)
            self.assertEqual(cleanup_stats["rehydration_cache"], 3)

    def test_search_functionality(self):
        """Test conversation search functionality."""
        session_id = "search_test_session"
        query = "test query"

        with patch.object(self.ltst_system.conversation_storage, "search_messages") as mock_search:
            mock_results = [
                (
                    ConversationMessage(
                        session_id=session_id,
                        role="human",
                        content="This is a test message",
                        message_type="message",
                        message_index=1,
                    ),
                    0.85,
                )
            ]
            mock_search.return_value = mock_results

            results = self.ltst_system.search_conversations(query, session_id)

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0][0].content, "This is a test message")
            self.assertEqual(results[0][1], 0.85)

    def test_session_summary_functionality(self):
        """Test session summary functionality."""
        session_id = "summary_test_session"

        with patch.object(self.ltst_system.conversation_storage, "get_session_summary") as mock_summary:
            mock_summary_data = {
                "session_id": session_id,
                "message_count": 10,
                "human_message_count": 5,
                "ai_message_count": 5,
                "total_tokens": 1000,
                "average_message_length": 100,
                "session_duration": timedelta(hours=1),
                "context_count": 3,
                "last_summary_update": datetime.now(),
            }
            mock_summary.return_value = mock_summary_data

            summary = self.ltst_system.get_session_summary(session_id)

            self.assertIsNotNone(summary)
            self.assertEqual(summary["session_id"], session_id)
            self.assertEqual(summary["message_count"], 10)
            self.assertEqual(summary["human_message_count"], 5)
            self.assertEqual(summary["ai_message_count"], 5)

    def test_system_statistics(self):
        """Test system statistics generation."""
        with (
            patch.object(self.ltst_system, "get_system_health") as mock_health,
            patch.object(self.ltst_system.context_merger, "get_merge_statistics") as mock_merge_stats,
            patch.object(self.ltst_system.memory_rehydrator, "get_rehydration_statistics") as mock_rehydration_stats,
        ):

            # Mock health data
            mock_health_data = SystemHealth(
                database_connected=True,
                cache_size=10,
                active_sessions=5,
                total_operations=100,
                error_rate=0.05,
                average_response_time_ms=150.0,
                last_health_check=datetime.now(),
                component_status={"database": True, "storage": True},
            )
            mock_health.return_value = mock_health_data

            # Mock component statistics
            mock_merge_stats.return_value = {"cache_size": 5, "merge_count": 10}
            mock_rehydration_stats.return_value = {"cache_size": 5, "rehydration_count": 15}

            # Add some operation history
            for i in range(10):
                operation = MemoryOperation(
                    operation_type="store" if i % 2 == 0 else "retrieve",
                    session_id=f"session_{i}",
                    user_id=f"user_{i}",
                    timestamp=datetime.now(),
                    duration_ms=100.0 + i,
                    success=True,
                )
                self.ltst_system.operation_history.append(operation)

            stats = self.ltst_system.get_system_statistics()

            self.assertIn("health", stats)
            self.assertIn("components", stats)
            self.assertIn("operations", stats)
            self.assertTrue(stats["health"]["database_connected"])
            self.assertEqual(stats["health"]["active_sessions"], 5)
            self.assertEqual(stats["health"]["error_rate"], 0.05)

    def test_concurrent_operations(self):
        """Test system behavior under concurrent operations."""
        import threading

        results = []
        errors = []

        def store_message(session_id, user_id, content):
            try:
                with (
                    patch.object(self.ltst_system.conversation_storage, "create_session", return_value=True),
                    patch.object(self.ltst_system.conversation_storage, "store_message", return_value=True),
                ):
                    success = self.ltst_system.store_conversation_message(
                        session_id=session_id, user_id=user_id, role="human", content=content
                    )
                    results.append(success)
            except Exception as e:
                errors.append(str(e))

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=store_message, args=(f"concurrent_session_{i}", f"concurrent_user_{i}", f"Message {i}")
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))  # All operations should succeed
        self.assertEqual(len(errors), 0)  # No errors should occur


if __name__ == "__main__":
    unittest.main()
