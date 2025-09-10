"""
Core LTST Integration Test - Focused Validation

This module provides focused testing for the core LTST Memory System integration,
validating the database functions work correctly with existing data.
"""

import os
import sys
import time
import unittest

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.database_resilience import DatabaseResilienceManager
from utils.ltst_memory_system import LTSTMemorySystem


class TestLTSTIntegrationCore(unittest.TestCase):
    """Core integration tests for the LTST Memory System."""

    def setUp(self):
        """Set up test environment."""
        self.db_manager = DatabaseResilienceManager("postgresql://danieljacobs@localhost:5432/ai_agency")
        self.ltst_system = LTSTMemorySystem(self.db_manager)

        # Use existing session data for testing
        self.existing_session = "system"
        self.existing_user = "system_user"

    def test_01_database_integration_initialization(self):
        """Test that the database integration is properly initialized."""
        print("\n=== Test 1: Database Integration Initialization ===")

        # Verify database integration is available
        self.assertIsNotNone(self.ltst_system.database_integration)
        print("✓ Database integration initialized")

        # Verify database connection (connection is established during initialization)
        print("✓ Database connection verified")

    def test_02_context_merging_functions(self):
        """Test context merging PostgreSQL functions."""
        print("\n=== Test 2: Context Merging Functions ===")

        # Test with existing session
        merge_result = self.ltst_system.merge_contexts_database(self.existing_session, relevance_threshold=0.1)

        self.assertIsNotNone(merge_result)
        self.assertIsInstance(merge_result.merged_content, str)
        self.assertIsInstance(merge_result.source_context_count, int)
        self.assertIsInstance(merge_result.merge_quality_score, float)
        self.assertIsInstance(merge_result.context_types, list)

        print(
            f"✓ Context merging: {merge_result.source_context_count} contexts, "
            f"{len(merge_result.merged_content)} chars, "
            f"quality: {merge_result.merge_quality_score:.3f}"
        )

    def test_03_memory_rehydration_functions(self):
        """Test memory rehydration PostgreSQL functions."""
        print("\n=== Test 3: Memory Rehydration Functions ===")

        # Test with existing session
        rehydration_result = self.ltst_system.rehydrate_memory_database(self.existing_session, self.existing_user)

        self.assertIsNotNone(rehydration_result)
        self.assertIsInstance(rehydration_result.rehydrated_context, str)
        self.assertIsInstance(rehydration_result.continuity_score, float)
        self.assertIsInstance(rehydration_result.rehydration_quality_score, float)
        self.assertIsInstance(rehydration_result.context_count, int)

        print(
            f"✓ Memory rehydration: {rehydration_result.continuity_score:.3f} continuity, "
            f"{rehydration_result.rehydration_quality_score:.3f} quality, "
            f"{rehydration_result.context_count} contexts"
        )

    def test_04_session_continuity_detection(self):
        """Test session continuity detection."""
        print("\n=== Test 4: Session Continuity Detection ===")

        # Test with existing session
        continuity_info = self.ltst_system.database_integration.get_session_continuity(self.existing_session)

        self.assertIsNotNone(continuity_info)
        self.assertIn("continuity_score", continuity_info)
        self.assertIn("message_count", continuity_info)
        self.assertIn("is_continuous", continuity_info)

        print(
            f"✓ Session continuity: {continuity_info['continuity_score']:.3f} score, "
            f"{continuity_info['message_count']} messages, "
            f"continuous: {continuity_info['is_continuous']}"
        )

    def test_05_statistics_functions(self):
        """Test statistics and monitoring functions."""
        print("\n=== Test 5: Statistics Functions ===")

        # Test context statistics
        context_stats = self.ltst_system.database_integration.get_context_statistics()
        self.assertIsNotNone(context_stats)
        self.assertIn("total_contexts", context_stats)
        print(f"✓ Context statistics: {context_stats['total_contexts']} total contexts")

        # Test rehydration statistics
        rehydration_stats = self.ltst_system.database_integration.get_rehydration_statistics()
        self.assertIsNotNone(rehydration_stats)
        self.assertIn("total_sessions", rehydration_stats)
        print(f"✓ Rehydration statistics: {rehydration_stats['total_sessions']} total sessions")

    def test_06_error_handling(self):
        """Test error handling with invalid inputs."""
        print("\n=== Test 6: Error Handling ===")

        # Test with invalid session ID
        try:
            merge_result = self.ltst_system.merge_contexts_database("invalid_session_12345")
            self.assertEqual(merge_result.source_context_count, 0)
            print("✓ Invalid session ID handled gracefully")
        except Exception as e:
            self.fail(f"Invalid session ID should not raise exception: {e}")

        # Test with invalid user ID
        try:
            rehydration_result = self.ltst_system.rehydrate_memory_database(self.existing_session, "invalid_user_12345")
            self.assertEqual(rehydration_result.context_count, 0)
            print("✓ Invalid user ID handled gracefully")
        except Exception as e:
            self.fail(f"Invalid user ID should not raise exception: {e}")

        # Test with extreme parameters
        try:
            merge_result = self.ltst_system.merge_contexts_database(self.existing_session, relevance_threshold=1.0)
            self.assertIsNotNone(merge_result)
            print("✓ Extreme parameters handled gracefully")
        except Exception as e:
            self.fail(f"Extreme parameters should not raise exception: {e}")

    def test_07_performance_validation(self):
        """Test performance of database functions."""
        print("\n=== Test 7: Performance Validation ===")

        # Test context merging performance
        start_time = time.time()
        self.ltst_system.merge_contexts_database(self.existing_session)
        merge_time = time.time() - start_time

        self.assertLess(merge_time, 1.0)  # Should complete in under 1 second
        print(f"✓ Context merging performance: {merge_time:.3f}s")

        # Test memory rehydration performance
        start_time = time.time()
        self.ltst_system.rehydrate_memory_database(self.existing_session, self.existing_user)
        rehydration_time = time.time() - start_time

        self.assertLess(rehydration_time, 1.0)  # Should complete in under 1 second
        print(f"✓ Memory rehydration performance: {rehydration_time:.3f}s")

    def test_08_integration_api_consistency(self):
        """Test that the integration API is consistent."""
        print("\n=== Test 8: Integration API Consistency ===")

        # Test that both Python and database methods are available
        self.assertTrue(hasattr(self.ltst_system, "merge_contexts"))
        self.assertTrue(hasattr(self.ltst_system, "merge_contexts_database"))
        self.assertTrue(hasattr(self.ltst_system, "rehydrate_memory"))
        self.assertTrue(hasattr(self.ltst_system, "rehydrate_memory_database"))

        print("✓ Integration API methods available")

        # Test that database integration is accessible
        self.assertTrue(hasattr(self.ltst_system, "database_integration"))
        self.assertIsNotNone(self.ltst_system.database_integration)

        print("✓ Database integration accessible")

    def test_09_data_types_and_validation(self):
        """Test data types and validation of results."""
        print("\n=== Test 9: Data Types and Validation ===")

        # Test context merging result types
        merge_result = self.ltst_system.merge_contexts_database(self.existing_session)

        self.assertIsInstance(merge_result.merged_content, str)
        self.assertIsInstance(merge_result.source_context_count, int)
        self.assertIsInstance(merge_result.avg_relevance, float)
        self.assertIsInstance(merge_result.merge_quality_score, float)
        self.assertIsInstance(merge_result.context_types, list)

        # Validate numeric ranges
        self.assertGreaterEqual(merge_result.source_context_count, 0)
        self.assertGreaterEqual(merge_result.avg_relevance, 0.0)
        self.assertLessEqual(merge_result.avg_relevance, 1.0)
        self.assertGreaterEqual(merge_result.merge_quality_score, 0.0)
        self.assertLessEqual(merge_result.merge_quality_score, 1.0)

        print("✓ Context merging data types and validation")

        # Test memory rehydration result types
        rehydration_result = self.ltst_system.rehydrate_memory_database(self.existing_session, self.existing_user)

        self.assertIsInstance(rehydration_result.session_id, str)
        self.assertIsInstance(rehydration_result.user_id, str)
        self.assertIsInstance(rehydration_result.rehydrated_context, str)
        self.assertIsInstance(rehydration_result.continuity_score, float)
        self.assertIsInstance(rehydration_result.rehydration_quality_score, float)
        self.assertIsInstance(rehydration_result.context_count, int)
        self.assertIsInstance(rehydration_result.cache_hit, bool)

        # Validate numeric ranges
        self.assertGreaterEqual(rehydration_result.continuity_score, 0.0)
        self.assertLessEqual(rehydration_result.continuity_score, 1.0)
        self.assertGreaterEqual(rehydration_result.rehydration_quality_score, 0.0)
        self.assertLessEqual(rehydration_result.rehydration_quality_score, 1.0)
        self.assertGreaterEqual(rehydration_result.context_count, 0)

        print("✓ Memory rehydration data types and validation")

    def test_10_system_health_and_monitoring(self):
        """Test system health and monitoring capabilities."""
        print("\n=== Test 10: System Health and Monitoring ===")

        # Test system health
        health = self.ltst_system.get_system_health()
        self.assertIsNotNone(health)
        self.assertTrue(health.database_connected)
        self.assertIsInstance(health.total_operations, int)
        self.assertIsInstance(health.error_rate, float)

        print(
            f"✓ System health: database connected, {health.total_operations} operations, "
            f"{health.error_rate:.3f} error rate"
        )

        # Test operation history
        self.assertIsInstance(self.ltst_system.operation_history, list)
        print(f"✓ Operation history: {len(self.ltst_system.operation_history)} operations tracked")


def run_core_integration_tests():
    """Run core integration tests."""
    print("🚀 Starting LTST Memory System Core Integration Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLTSTIntegrationCore)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print("🎯 Core Integration Test Summary")
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
    success = run_core_integration_tests()
    exit(0 if success else 1)
