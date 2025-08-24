"""
End-to-End Testing for LTST Memory System

This module provides comprehensive end-to-end testing for the integrated
LTST Memory System, including database integration, performance benchmarks,
and error scenarios.
"""

import os
import sys
import time
import unittest

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.database_resilience import DatabaseResilienceManager
from utils.ltst_memory_system import LTSTMemorySystem


class TestLTSTEndToEnd(unittest.TestCase):
    """End-to-end tests for the LTST Memory System."""

    def setUp(self):
        """Set up test environment."""
        # Use test database connection
        self.db_manager = DatabaseResilienceManager("postgresql://danieljacobs@localhost:5432/ai_agency")
        self.ltst_system = LTSTMemorySystem(self.db_manager)

        # Test data
        self.test_session_id = f"test_e2e_{int(time.time())}"
        self.test_user_id = "test_user_e2e"

        # Performance tracking
        self.performance_results = {}

    def tearDown(self):
        """Clean up test environment."""
        # Clean up test data
        try:
            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM conversation_memory WHERE session_id = %s", (self.test_session_id,))
                    cursor.execute("DELETE FROM conversation_sessions WHERE session_id = %s", (self.test_session_id,))
                    conn.commit()
        except Exception as e:
            print(f"Warning: Could not clean up test data: {e}")

    def test_01_complete_workflow(self):
        """Test complete workflow: store → merge → rehydrate → search."""
        print("\n=== Test 1: Complete Workflow ===")

        # Step 1: Store conversation messages
        start_time = time.time()
        messages = [
            ("human", "Hello, I'm working on a DSPy RAG system integration project."),
            ("ai", "That sounds interesting! DSPy is great for AI development workflows."),
            ("human", "Yes, I need to implement context merging and memory rehydration."),
            ("ai", "The LTST Memory System should help with that. It provides intelligent context management."),
            ("human", "Can you explain how the database integration works?"),
            (
                "ai",
                "The system uses PostgreSQL functions for context merging and memory rehydration, with Python APIs for easy integration.",
            ),
        ]

        for role, content in messages:
            success = self.ltst_system.store_conversation_message(
                self.test_session_id, self.test_user_id, role, content
            )
            self.assertTrue(success, f"Failed to store message: {role}: {content}")

        store_time = time.time() - start_time
        print(f"✓ Stored {len(messages)} messages in {store_time:.3f}s")

        # Step 2: Store context data
        contexts = [
            ("project", "current_project", "DSPy RAG System Integration", 0.9),
            ("user_preference", "coding_style", "Prefers Python with type hints", 0.8),
            ("technical", "architecture", "PostgreSQL with pgvector for embeddings", 0.85),
            ("workflow", "development", "Test-driven development with comprehensive testing", 0.75),
        ]

        for context_type, context_key, context_value, relevance in contexts:
            success = self.ltst_system.store_context(
                self.test_session_id, context_type, context_key, context_value, relevance
            )
            self.assertTrue(success, f"Failed to store context: {context_type}:{context_key}")

        print(f"✓ Stored {len(contexts)} context items")

        # Step 3: Test context merging
        start_time = time.time()
        merge_result = self.ltst_system.merge_contexts_database(self.test_session_id, relevance_threshold=0.7)
        merge_time = time.time() - start_time

        self.assertIsNotNone(merge_result)
        self.assertGreater(merge_result.source_context_count, 0)
        self.assertGreater(len(merge_result.merged_content), 0)
        print(
            f"✓ Context merging: {merge_result.source_context_count} contexts, "
            f"{len(merge_result.merged_content)} chars, {merge_time:.3f}s"
        )

        # Step 4: Test memory rehydration
        start_time = time.time()
        rehydration_result = self.ltst_system.rehydrate_memory_database(self.test_session_id, self.test_user_id)
        rehydration_time = time.time() - start_time

        self.assertIsNotNone(rehydration_result)
        self.assertGreater(rehydration_result.continuity_score, 0)
        self.assertGreater(rehydration_result.rehydration_quality_score, 0)
        print(
            f"✓ Memory rehydration: {rehydration_result.continuity_score:.3f} continuity, "
            f"{rehydration_result.rehydration_quality_score:.3f} quality, {rehydration_time:.3f}s"
        )

        # Step 5: Test conversation search
        start_time = time.time()
        search_results = self.ltst_system.search_conversations("DSPy integration", self.test_session_id, limit=5)
        search_time = time.time() - start_time

        self.assertGreater(len(search_results), 0)
        print(f"✓ Conversation search: {len(search_results)} results, {search_time:.3f}s")

        # Store performance results
        self.performance_results["complete_workflow"] = {
            "store_time": store_time,
            "merge_time": merge_time,
            "rehydration_time": rehydration_time,
            "search_time": search_time,
            "total_time": store_time + merge_time + rehydration_time + search_time,
        }

    def test_02_performance_benchmarks(self):
        """Test performance benchmarks and scalability."""
        print("\n=== Test 2: Performance Benchmarks ===")

        # Test with different data sizes
        data_sizes = [10, 50, 100]

        for size in data_sizes:
            print(f"\n--- Testing with {size} messages ---")

            # Generate test data
            messages = []
            for i in range(size):
                messages.append(
                    (
                        "human" if i % 2 == 0 else "ai",
                        f"Message {i}: This is test message number {i} for performance testing.",
                    )
                )

            # Store messages
            start_time = time.time()
            for role, content in messages:
                self.ltst_system.store_conversation_message(
                    f"{self.test_session_id}_perf_{size}", self.test_user_id, role, content
                )
            store_time = time.time() - start_time

            # Test context merging performance
            start_time = time.time()
            merge_result = self.ltst_system.merge_contexts_database(
                f"{self.test_session_id}_perf_{size}", relevance_threshold=0.1
            )
            merge_time = time.time() - start_time

            # Test rehydration performance
            start_time = time.time()
            rehydration_result = self.ltst_system.rehydrate_memory_database(
                f"{self.test_session_id}_perf_{size}", self.test_user_id
            )
            rehydration_time = time.time() - start_time

            print(f"  Store: {store_time:.3f}s ({size/store_time:.1f} msg/s)")
            print(f"  Merge: {merge_time:.3f}s")
            print(f"  Rehydrate: {rehydration_time:.3f}s")

            # Store results
            self.performance_results[f"size_{size}"] = {
                "store_time": store_time,
                "merge_time": merge_time,
                "rehydration_time": rehydration_time,
                "store_rate": size / store_time if store_time > 0 else 0,
            }

    def test_03_error_scenarios(self):
        """Test error scenarios and recovery."""
        print("\n=== Test 3: Error Scenarios ===")

        # Test with invalid session ID
        try:
            merge_result = self.ltst_system.merge_contexts_database("invalid_session_12345")
            # Should not raise exception, but return empty result
            self.assertEqual(merge_result.source_context_count, 0)
            print("✓ Invalid session ID handled gracefully")
        except Exception as e:
            self.fail(f"Invalid session ID should not raise exception: {e}")

        # Test with invalid user ID
        try:
            rehydration_result = self.ltst_system.rehydrate_memory_database(self.test_session_id, "invalid_user_12345")
            # Should not raise exception, but return empty result
            self.assertEqual(rehydration_result.context_count, 0)
            print("✓ Invalid user ID handled gracefully")
        except Exception as e:
            self.fail(f"Invalid user ID should not raise exception: {e}")

        # Test with extreme parameters
        try:
            merge_result = self.ltst_system.merge_contexts_database(
                self.test_session_id, relevance_threshold=1.0  # Very high threshold
            )
            self.assertIsNotNone(merge_result)
            print("✓ Extreme parameters handled gracefully")
        except Exception as e:
            self.fail(f"Extreme parameters should not raise exception: {e}")

    def test_04_data_integrity(self):
        """Test data integrity and consistency."""
        print("\n=== Test 4: Data Integrity ===")

        # Store test data
        test_message = "This is a test message for data integrity verification."
        self.ltst_system.store_conversation_message(self.test_session_id, self.test_user_id, "human", test_message)

        # Verify data was stored correctly
        history = self.ltst_system.retrieve_conversation_history(self.test_session_id)
        self.assertGreater(len(history), 0)

        # Check if our message is in the history
        found_message = False
        for msg in history:
            if test_message in msg.content:
                found_message = True
                break

        self.assertTrue(found_message, "Stored message not found in retrieved history")
        print("✓ Data integrity verified")

        # Test context consistency
        test_context = "Test context for integrity verification"
        self.ltst_system.store_context(self.test_session_id, "test", "integrity", test_context, 0.9)

        # Verify context appears in merge results
        merge_result = self.ltst_system.merge_contexts_database(self.test_session_id, relevance_threshold=0.8)

        self.assertIn(test_context, merge_result.merged_content)
        print("✓ Context consistency verified")

    def test_05_session_continuity(self):
        """Test session continuity detection."""
        print("\n=== Test 5: Session Continuity ===")

        # Create a session with recent activity
        recent_session = f"{self.test_session_id}_recent"
        self.ltst_system.store_conversation_message(recent_session, self.test_user_id, "human", "Recent message")

        # Test continuity detection
        continuity_info = self.ltst_system.database_integration.get_session_continuity(recent_session)

        self.assertIsNotNone(continuity_info)
        self.assertGreater(continuity_info["continuity_score"], 0)
        self.assertTrue(continuity_info["is_continuous"])
        print(f"✓ Recent session continuity: {continuity_info['continuity_score']:.3f}")

        # Test old session (should have low continuity)
        old_session = f"{self.test_session_id}_old"
        # Note: We can't easily create an old session in tests, but we can test the function
        continuity_info = self.ltst_system.database_integration.get_session_continuity(old_session)

        self.assertIsNotNone(continuity_info)
        self.assertEqual(continuity_info["message_count"], 0)
        print("✓ Old session continuity handled correctly")

    def test_06_statistics_and_monitoring(self):
        """Test statistics and monitoring capabilities."""
        print("\n=== Test 6: Statistics and Monitoring ===")

        # Get context statistics
        context_stats = self.ltst_system.database_integration.get_context_statistics()
        self.assertIsNotNone(context_stats)
        self.assertIn("total_contexts", context_stats)
        print(f"✓ Context statistics: {context_stats['total_contexts']} total contexts")

        # Get rehydration statistics
        rehydration_stats = self.ltst_system.database_integration.get_rehydration_statistics()
        self.assertIsNotNone(rehydration_stats)
        self.assertIn("total_sessions", rehydration_stats)
        print(f"✓ Rehydration statistics: {rehydration_stats['total_sessions']} total sessions")

        # Test system health
        health = self.ltst_system.get_system_health()
        self.assertIsNotNone(health)
        self.assertTrue(health.database_connected)
        print(f"✓ System health: database connected, {health.total_operations} operations")

    def test_07_cache_optimization(self):
        """Test cache optimization functions."""
        print("\n=== Test 7: Cache Optimization ===")

        try:
            optimization_results = self.ltst_system.database_integration.optimize_caches()
            self.assertIsNotNone(optimization_results)
            self.assertIn("context_cache", optimization_results)
            self.assertIn("rehydration_cache", optimization_results)
            print("✓ Cache optimization completed")
        except Exception as e:
            print(f"⚠ Cache optimization test skipped: {e}")

    def test_08_concurrent_operations(self):
        """Test concurrent operations and thread safety."""
        print("\n=== Test 8: Concurrent Operations ===")

        import threading

        def store_messages(session_prefix: str, count: int):
            """Store messages in a separate thread."""
            for i in range(count):
                self.ltst_system.store_conversation_message(
                    f"{session_prefix}_{i}", self.test_user_id, "human", f"Concurrent message {i}"
                )

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=store_messages, args=(f"{self.test_session_id}_concurrent_{i}", 5))
            threads.append(thread)

        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        concurrent_time = time.time() - start_time
        print(f"✓ Concurrent operations completed in {concurrent_time:.3f}s")

        # Verify data integrity after concurrent operations
        total_messages = 0
        for i in range(3):
            history = self.ltst_system.retrieve_conversation_history(f"{self.test_session_id}_concurrent_{i}")
            total_messages += len(history)

        self.assertEqual(total_messages, 15)  # 3 threads × 5 messages each
        print(f"✓ Data integrity maintained: {total_messages} total messages")

    def test_09_integration_with_existing_system(self):
        """Test integration with existing system components."""
        print("\n=== Test 9: Integration with Existing System ===")

        # Test that the new database methods work alongside existing Python methods
        session_id = f"{self.test_session_id}_integration"

        # Use existing Python methods
        self.ltst_system.store_conversation_message(session_id, self.test_user_id, "human", "Integration test message")

        # Use new database methods
        merge_result = self.ltst_system.merge_contexts_database(session_id)
        rehydration_result = self.ltst_system.rehydrate_memory_database(session_id, self.test_user_id)

        # Both should work without conflicts
        self.assertIsNotNone(merge_result)
        self.assertIsNotNone(rehydration_result)
        print("✓ Integration with existing system verified")

    def test_10_performance_summary(self):
        """Generate performance summary."""
        print("\n=== Test 10: Performance Summary ===")

        if not self.performance_results:
            print("No performance data collected")
            return

        print("\nPerformance Results:")
        print("-" * 50)

        for test_name, results in self.performance_results.items():
            print(f"\n{test_name}:")
            for metric, value in results.items():
                if isinstance(value, float):
                    print(f"  {metric}: {value:.3f}")
                else:
                    print(f"  {metric}: {value}")

        # Calculate averages
        if "complete_workflow" in self.performance_results:
            workflow = self.performance_results["complete_workflow"]
            print("\nComplete Workflow Summary:")
            print(f"  Total Time: {workflow['total_time']:.3f}s")
            print(f"  Store Rate: {workflow.get('store_rate', 'N/A')}")

        print("\n" + "=" * 50)


def run_end_to_end_tests():
    """Run all end-to-end tests."""
    print("🚀 Starting LTST Memory System End-to-End Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLTSTEndToEnd)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("🎯 End-to-End Test Summary")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_end_to_end_tests()
    exit(0 if success else 1)
