#!/usr/bin/env python3
"""
Comprehensive Unit Tests for LTST Memory System

This module provides comprehensive unit tests for all LTST Memory System components
including ConversationStorage, SessionManager, ContextMerger, and MemoryRehydrator.
"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.context_merger import ContextMerger, ContextMergeResult
from utils.conversation_storage import (
    ConversationContext,
    ConversationMessage,
    ConversationSession,
    ConversationStorage,
    UserPreference,
)
from utils.memory_rehydrator import MemoryRehydrator, RehydrationRequest, RehydrationResult
from utils.session_manager import SessionManager


class TestConversationStorage(unittest.TestCase):
    """Test ConversationStorage functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = ConversationStorage()
        self.test_session_id = "test_session_001"
        self.test_user_id = "test_user_001"

    def test_connection_management(self):
        """Test database connection management."""
        # Test connection
        self.assertTrue(self.storage.connect())
        self.assertIsNotNone(self.storage.connection)
        self.assertIsNotNone(self.storage.cursor)

        # Test disconnection
        self.storage.disconnect()
        # Note: Connection object may still exist but be closed
        self.assertIsNone(self.storage.cursor)

    def test_session_creation(self):
        """Test session creation and retrieval."""
        self.storage.connect()

        # Create test session
        session = ConversationSession(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            session_name="Test Session",
            session_type="conversation",
            status="active",
        )

        # Store session
        self.assertTrue(self.storage.create_session(session))

        # Retrieve session summary
        summary = self.storage.get_session_summary(self.test_session_id)
        self.assertIsNotNone(summary)
        if summary is not None:  # Type checker guard
            self.assertEqual(summary["session_id"], self.test_session_id)
            self.assertEqual(summary["user_id"], self.test_user_id)

        self.storage.disconnect()

    def test_message_storage(self):
        """Test message storage and retrieval."""
        self.storage.connect()

        # Create test message
        message = ConversationMessage(
            session_id=self.test_session_id, role="human", content="Test message content", message_type="message"
        )

        # Store message
        self.assertTrue(self.storage.store_message(message))

        # Retrieve messages
        messages = self.storage.retrieve_session_messages(self.test_session_id, limit=10)
        self.assertGreater(len(messages), 0)
        self.assertEqual(messages[0]["content"], "Test message content")

        self.storage.disconnect()

    def test_context_storage(self):
        """Test context storage and retrieval."""
        self.storage.connect()

        # Create test context
        context = ConversationContext(
            session_id=self.test_session_id,
            context_type="conversation",
            context_key="test_key",
            context_value="test_value",
            relevance_score=0.8,
        )

        # Store context
        self.assertTrue(
            self.storage.store_context(
                context.session_id,
                context.context_type,
                context.context_key,
                context.context_value,
                context.relevance_score,
            )
        )

        # Retrieve contexts
        contexts = self.storage.retrieve_context(self.test_session_id, "conversation", limit=10)
        self.assertGreater(len(contexts), 0)
        self.assertEqual(contexts[0]["context_value"], "test_value")

        self.storage.disconnect()

    def test_user_preference_storage(self):
        """Test user preference storage and retrieval."""
        self.storage.connect()

        # Create test preference
        preference = UserPreference(
            user_id=self.test_user_id,
            preference_key="test_pref",
            preference_value="test_value",
            preference_type="test",
            confidence_score=0.9,
        )

        # Store preference
        self.assertTrue(self.storage.store_user_preference(preference))

        # Retrieve preferences
        preferences = self.storage.retrieve_user_preferences(self.test_user_id, limit=10)
        self.assertGreater(len(preferences), 0)
        self.assertEqual(preferences[0]["preference_value"], "test_value")

        self.storage.disconnect()

    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        self.storage.connect()

        # Perform some operations
        session = ConversationSession(
            session_id="perf_test_session", user_id=self.test_user_id, session_name="Performance Test"
        )
        self.storage.create_session(session)

        # Check metrics
        metrics = self.storage.get_performance_metrics()
        self.assertIsNotNone(metrics)
        self.assertIn("operations", metrics)

        self.storage.disconnect()


class TestSessionManager(unittest.TestCase):
    """Test SessionManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = ConversationStorage()
        self.session_manager = SessionManager(self.storage)
        self.test_user_id = "test_user_002"

    def test_session_creation(self):
        """Test session creation."""
        self.storage.connect()

        # Create session
        session_id = self.session_manager.create_session(user_id=self.test_user_id, session_name="Test Session Manager")

        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)

        # Get session state
        session_state = self.session_manager.get_session_state(session_id)
        self.assertIsNotNone(session_state)
        if session_state is not None:  # Type checker guard
            self.assertEqual(session_state.user_id, self.test_user_id)
            self.assertTrue(session_state.is_active)

        self.storage.disconnect()

    def test_session_activity_tracking(self):
        """Test session activity tracking."""
        self.storage.connect()

        # Create session
        session_id = self.session_manager.create_session(self.test_user_id)

        # Update activity
        self.assertTrue(self.session_manager.update_session_activity(session_id, "message"))

        # Check updated state
        session_state = self.session_manager.get_session_state(session_id)
        if session_state is not None:  # Type checker guard
            self.assertEqual(session_state.message_count, 1)

        self.storage.disconnect()

    def test_session_insights(self):
        """Test session insights generation."""
        self.storage.connect()

        # Create session and add messages
        session_id = self.session_manager.create_session(self.test_user_id)

        # Add test messages
        for i in range(5):
            message = ConversationMessage(
                session_id=session_id, role="human", content=f"Test message {i} with technical details"
            )
            self.storage.store_message(message)
            self.session_manager.update_session_activity(session_id, "message")

        # Get insights
        insights = self.session_manager.get_session_insights(session_id)
        self.assertIsNotNone(insights)
        self.assertIn("message_count", insights)
        self.assertIn("user_engagement", insights)

        self.storage.disconnect()

    def test_session_cleanup(self):
        """Test session cleanup functionality."""
        self.storage.connect()

        # Create session
        session_id = self.session_manager.create_session(self.test_user_id)

        # Close session
        self.assertTrue(self.session_manager.close_session(session_id, "test_completed"))

        # Verify session is closed
        session_state = self.session_manager.get_session_state(session_id)
        if session_state is not None:  # Type checker guard
            self.assertFalse(session_state.is_active)

        self.storage.disconnect()

    def test_performance_metrics(self):
        """Test performance metrics."""
        self.storage.connect()

        # Perform operations
        session_id = self.session_manager.create_session(self.test_user_id)
        self.session_manager.update_session_activity(session_id, "message")

        # Get metrics
        metrics = self.session_manager.get_performance_metrics()
        self.assertIsNotNone(metrics)
        self.assertIn("session_operations", metrics)

        self.storage.disconnect()


class TestContextMerger(unittest.TestCase):
    """Test ContextMerger functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = ConversationStorage()
        self.context_merger = ContextMerger(self.storage)
        self.test_session_id = "test_session_003"

    def test_context_merging(self):
        """Test context merging functionality."""
        self.storage.connect()

        # Create test contexts
        contexts = []
        for i in range(5):
            context = ConversationContext(
                session_id=self.test_session_id,
                context_type="conversation",
                context_key=f"key_{i}",
                context_value=f"value_{i}",
                relevance_score=0.8 - (i * 0.1),
            )
            self.storage.store_context(
                context.session_id,
                context.context_type,
                context.context_key,
                context.context_value,
                context.relevance_score,
            )
            contexts.append(context)

        # Merge contexts
        merge_result = self.context_merger.merge_contexts(
            self.test_session_id, context_type="conversation", relevance_threshold=0.5
        )

        self.assertIsNotNone(merge_result)
        self.assertIsInstance(merge_result, ContextMergeResult)

        self.storage.disconnect()

    def test_user_preference_integration(self):
        """Test user preference integration in context merging."""
        self.storage.connect()

        # Create user preference
        preference = UserPreference(
            user_id="test_user_003",
            preference_key="technical",
            preference_value="high",
            preference_type="communication",
            confidence_score=0.9,
        )
        self.storage.store_user_preference(preference)

        # Create contexts with technical content
        context = ConversationContext(
            session_id=self.test_session_id,
            context_type="conversation",
            context_key="technical_key",
            context_value="This is a technical implementation detail",
            relevance_score=0.7,
        )
        self.storage.store_context(
            context.session_id,
            context.context_type,
            context.context_key,
            context.context_value,
            context.relevance_score,
        )

        # Merge with user preferences
        merge_result = self.context_merger.merge_with_user_preferences(
            self.test_session_id, "test_user_003", "conversation"
        )

        self.assertIsNotNone(merge_result)

        self.storage.disconnect()

    def test_cache_functionality(self):
        """Test caching functionality."""
        self.storage.connect()

        # Create test context
        context = ConversationContext(
            session_id=self.test_session_id,
            context_type="conversation",
            context_key="cache_test",
            context_value="cache test value",
            relevance_score=0.8,
        )
        self.storage.store_context(
            context.session_id,
            context.context_type,
            context.context_key,
            context.context_value,
            context.relevance_score,
        )

        # First merge (should cache)
        result1 = self.context_merger.merge_contexts(self.test_session_id, context_type="conversation")

        # Second merge (should use cache)
        result2 = self.context_merger.merge_contexts(self.test_session_id, context_type="conversation")

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)

        self.storage.disconnect()


class TestMemoryRehydrator(unittest.TestCase):
    """Test MemoryRehydrator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = ConversationStorage()
        self.rehydrator = MemoryRehydrator(self.storage)
        self.test_session_id = "test_session_004"
        self.test_user_id = "test_user_004"

    def test_memory_rehydration(self):
        """Test memory rehydration functionality."""
        self.storage.connect()

        # Create session and add content
        session = ConversationSession(
            session_id=self.test_session_id, user_id=self.test_user_id, session_name="Rehydration Test"
        )
        self.storage.create_session(session)

        # Add messages
        for i in range(3):
            message = ConversationMessage(session_id=self.test_session_id, role="human", content=f"Test message {i}")
            self.storage.store_message(message)

        # Create rehydration request
        request = RehydrationRequest(
            session_id=self.test_session_id,
            user_id=self.test_user_id,
            current_message="Test query",
            context_types=["conversation"],
            max_context_length=1000,
        )

        # Rehydrate memory
        result = self.rehydrator.rehydrate_memory(request)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, RehydrationResult)
        self.assertEqual(result.session_id, self.test_session_id)
        self.assertGreater(len(result.conversation_history), 0)

        self.storage.disconnect()

    def test_session_continuity_detection(self):
        """Test session continuity detection."""
        self.storage.connect()

        # Create session
        session = ConversationSession(
            session_id=self.test_session_id, user_id=self.test_user_id, session_name="Continuity Test"
        )
        self.storage.create_session(session)

        # Test continuity detection
        continuity_score = self.rehydrator._detect_session_continuity(self.test_session_id, self.test_user_id)

        self.assertIsInstance(continuity_score, float)
        self.assertGreaterEqual(continuity_score, 0.0)
        self.assertLessEqual(continuity_score, 1.0)

        self.storage.disconnect()

    def test_session_insights_integration(self):
        """Test session insights integration."""
        self.storage.connect()

        # Create session
        session = ConversationSession(
            session_id=self.test_session_id, user_id=self.test_user_id, session_name="Insights Test"
        )
        self.storage.create_session(session)

        # Add messages for insights
        for i in range(5):
            message = ConversationMessage(
                session_id=self.test_session_id,
                role="human",
                content=f"Technical message {i} with implementation details",
            )
            self.storage.store_message(message)

        # Get session insights
        insights = self.rehydrator.get_session_insights_for_rehydration(self.test_session_id, self.test_user_id)

        self.assertIsNotNone(insights)
        self.assertIn("session_metrics", insights)
        self.assertIn("conversation_analysis", insights)
        self.assertIn("user_patterns", insights)

        self.storage.disconnect()

    def test_cache_functionality(self):
        """Test rehydration cache functionality."""
        self.storage.connect()

        # Create session
        session = ConversationSession(
            session_id=self.test_session_id, user_id=self.test_user_id, session_name="Cache Test"
        )
        self.storage.create_session(session)

        # Create request
        request = RehydrationRequest(
            session_id=self.test_session_id, user_id=self.test_user_id, current_message="Cache test query"
        )

        # First rehydration (should cache)
        result1 = self.rehydrator.rehydrate_memory(request)

        # Second rehydration (should use cache)
        result2 = self.rehydrator.rehydrate_memory(request)

        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)

        self.storage.disconnect()


class TestIntegration(unittest.TestCase):
    """Test integration between components."""

    def setUp(self):
        """Set up test fixtures."""
        self.storage = ConversationStorage()
        self.session_manager = SessionManager(self.storage)
        self.context_merger = ContextMerger(self.storage)
        self.rehydrator = MemoryRehydrator(self.storage)
        self.test_user_id = "integration_test_user"

    def test_full_workflow(self):
        """Test complete LTST workflow."""
        self.storage.connect()

        # 1. Create session
        session_id = self.session_manager.create_session(user_id=self.test_user_id, session_name="Integration Test")

        # 2. Add messages
        for i in range(3):
            message = ConversationMessage(session_id=session_id, role="human", content=f"Integration test message {i}")
            self.storage.store_message(message)
            self.session_manager.update_session_activity(session_id, "message")

        # 3. Add contexts
        context = ConversationContext(
            session_id=session_id,
            context_type="conversation",
            context_key="integration_key",
            context_value="Integration test context",
            relevance_score=0.8,
        )
        self.storage.store_context(
            context.session_id,
            context.context_type,
            context.context_key,
            context.context_value,
            context.relevance_score,
        )

        # 4. Add user preferences
        preference = UserPreference(
            user_id=self.test_user_id,
            preference_key="test_pref",
            preference_value="test_value",
            preference_type="test",
            confidence_score=0.9,
        )
        self.storage.store_user_preference(preference)

        # 5. Test context merging
        merge_result = self.context_merger.merge_contexts(session_id, context_type="conversation")
        self.assertIsNotNone(merge_result)

        # 6. Test memory rehydration
        request = RehydrationRequest(
            session_id=session_id, user_id=self.test_user_id, current_message="Integration test query"
        )
        result = self.rehydrator.rehydrate_memory(request)
        self.assertIsNotNone(result)

        # 7. Test session insights
        insights = self.session_manager.get_session_insights(session_id)
        self.assertIsNotNone(insights)

        # 8. Cleanup
        self.session_manager.close_session(session_id, "integration_test_completed")

        self.storage.disconnect()

    def test_performance_under_load(self):
        """Test performance under simulated load."""
        self.storage.connect()

        # Create multiple sessions
        session_ids = []
        for i in range(5):
            session_id = self.session_manager.create_session(
                user_id=f"{self.test_user_id}_{i}", session_name=f"Load Test Session {i}"
            )
            session_ids.append(session_id)

            # Add messages to each session
            for j in range(10):
                message = ConversationMessage(
                    session_id=session_id, role="human", content=f"Load test message {j} for session {i}"
                )
                self.storage.store_message(message)

        # Test concurrent operations
        for session_id in session_ids:
            # Test session state retrieval
            state = self.session_manager.get_session_state(session_id)
            self.assertIsNotNone(state)

            # Test context merging
            merge_result = self.context_merger.merge_contexts(session_id, "conversation")
            self.assertIsNotNone(merge_result)

            # Test memory rehydration
            request = RehydrationRequest(session_id, f"{self.test_user_id}_0", "Load test")
            result = self.rehydrator.rehydrate_memory(request)
            self.assertIsNotNone(result)

        # Cleanup
        for session_id in session_ids:
            self.session_manager.close_session(session_id, "load_test_completed")

        self.storage.disconnect()


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestConversationStorage,
        TestSessionManager,
        TestContextMerger,
        TestMemoryRehydrator,
        TestIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


if __name__ == "__main__":
    # Run comprehensive tests
    result = run_comprehensive_tests()

    # Print summary
    print(f"\n{'='*60}")
    print("COMPREHENSIVE TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    # Exit with appropriate code
    sys.exit(len(result.failures) + len(result.errors))
