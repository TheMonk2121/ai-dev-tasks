#!/usr/bin/env python3
"""
Performance tests for Session Registry System.

Tests the performance characteristics of the session registry:
- Load testing with multiple sessions
- Memory usage optimization
- Response time validation
- Scalability testing
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import psutil
import pytest

# Import the session registry system
from scripts.session_registry import SessionRegistry


class TestSessionRegistryPerformance:
    """Performance tests for SessionRegistry class."""

    @pytest.fixture
    def temp_registry_path(self):
        """Create a temporary registry file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(
                '{"sessions": {}, "last_updated": "2025-08-21T00:00:00Z", "total_sessions": 0, "active_sessions": 0}'
            )
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def registry(self, temp_registry_path):
        """Create a SessionRegistry instance for testing."""
        return SessionRegistry(registry_path=temp_registry_path)

    def test_session_registration_performance(self, registry):
        """Test performance of session registration operations."""
        start_time = time.time()

        # Register 100 sessions
        for i in range(100):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
                tags=[f"tag-{i}", "performance-test"],
            )

        end_time = time.time()
        registration_time = end_time - start_time

        # Performance assertion: 100 sessions should register in under 1 second
        assert registration_time < 1.0, f"Session registration took {registration_time:.3f}s, expected < 1.0s"
        assert len(registry.sessions) == 100

    def test_session_lookup_performance(self, registry):
        """Test performance of session lookup operations."""
        # Register 100 sessions
        for i in range(100):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
            )

        start_time = time.time()

        # Perform 1000 session lookups
        for _ in range(1000):
            session_id = f"B-{1000 + (_ % 100)}"
            session = registry.get_session_info(session_id)
            assert session is not None

        end_time = time.time()
        lookup_time = end_time - start_time

        # Performance assertion: 1000 lookups should complete in under 0.1 seconds
        assert lookup_time < 0.1, f"Session lookup took {lookup_time:.3f}s, expected < 0.1s"

    def test_context_tagging_performance(self, registry):
        """Test performance of context tagging operations."""
        # Register 50 sessions
        for i in range(50):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
            )

        start_time = time.time()

        # Add tags to all sessions
        for i in range(50):
            backlog_id = f"B-{1000 + i}"
            tags = [f"performance-tag-{i}", f"category-{i % 5}"]
            registry.add_context_tags(backlog_id, tags)

        end_time = time.time()
        tagging_time = end_time - start_time

        # Performance assertion: Tagging 50 sessions should complete in under 0.5 seconds
        assert tagging_time < 0.5, f"Context tagging took {tagging_time:.3f}s, expected < 0.5s"

    def test_session_filtering_performance(self, registry):
        """Test performance of session filtering operations."""
        # Register 200 sessions with various tags
        for i in range(200):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
                tags=[f"category-{i % 10}", f"priority-{i % 3}"],
            )

        start_time = time.time()

        # Perform multiple filtering operations
        for category in range(10):
            sessions = registry.get_sessions_by_context([f"category-{category}"])
            assert len(sessions) == 20  # 200 sessions / 10 categories

        end_time = time.time()
        filtering_time = end_time - start_time

        # Performance assertion: 10 filtering operations should complete in under 0.1 seconds
        assert filtering_time < 0.1, f"Session filtering took {filtering_time:.3f}s, expected < 0.1s"

    def test_memory_usage_optimization(self, registry):
        """Test memory usage optimization."""
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Register 1000 sessions
        for i in range(1000):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
                tags=[f"memory-test-{i % 100}"],
            )

        # Get memory usage after registration
        after_registration_memory = process.memory_info().rss
        memory_increase = after_registration_memory - initial_memory

        # Memory assertion: 1000 sessions should use less than 10MB additional memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        assert memory_increase_mb < 10, f"Memory increase: {memory_increase_mb:.2f}MB, expected < 10MB"

    def test_persistence_performance(self, temp_registry_path):
        """Test performance of registry persistence operations."""
        registry = SessionRegistry(registry_path=temp_registry_path)

        # Register 500 sessions
        for i in range(500):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
                tags=[f"persistence-test-{i % 50}"],
            )

        start_time = time.time()

        # Save registry
        registry.save_registry()

        end_time = time.time()
        save_time = end_time - start_time

        # Performance assertion: Saving 500 sessions should complete in under 0.5 seconds
        assert save_time < 0.5, f"Registry save took {save_time:.3f}s, expected < 0.5s"

        # Test load performance
        start_time = time.time()

        # Load registry
        new_registry = SessionRegistry(registry_path=temp_registry_path)

        end_time = time.time()
        load_time = end_time - start_time

        # Performance assertion: Loading 500 sessions should complete in under 0.5 seconds
        assert load_time < 0.5, f"Registry load took {load_time:.3f}s, expected < 0.5s"
        assert len(new_registry.sessions) == 500

    def test_concurrent_session_operations(self, registry):
        """Test performance under concurrent session operations."""
        import threading

        results = []
        errors = []

        def register_sessions(start_idx, count):
            """Register a batch of sessions."""
            try:
                for i in range(count):
                    registry.register_session(
                        backlog_id=f"B-{start_idx + i}",
                        pid=12345 + start_idx + i,
                        worklog_path=f"artifacts/worklogs/B-{start_idx + i}.md",
                        tags=[f"concurrent-test-{start_idx + i}"],
                    )
                results.append(f"Batch {start_idx}-{start_idx + count - 1} completed")
            except Exception as e:
                errors.append(f"Batch {start_idx}-{start_idx + count - 1} failed: {e}")

        # Create 5 threads, each registering 20 sessions
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_sessions, args=(i * 20, 20))
            threads.append(thread)

        start_time = time.time()

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        concurrent_time = end_time - start_time

        # Performance assertion: Concurrent registration should complete in under 1 second
        assert concurrent_time < 1.0, f"Concurrent registration took {concurrent_time:.3f}s, expected < 1.0s"
        assert len(registry.sessions) == 100
        assert len(errors) == 0, f"Concurrent operations failed: {errors}"

    def test_cleanup_performance(self, registry):
        """Test performance of cleanup operations."""
        # Register 1000 sessions and complete them
        for i in range(1000):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
            )
            registry.update_session_status(f"B-{1000 + i}", "completed")

        # Set old timestamps for cleanup
        for backlog_id in registry.sessions:
            old_session = registry.sessions[backlog_id]
            old_session.start_time = "2025-08-14T00:00:00Z"  # 7+ days old

        start_time = time.time()

        # Run cleanup
        registry.cleanup_completed_sessions()

        end_time = time.time()
        cleanup_time = end_time - start_time

        # Performance assertion: Cleanup of 1000 sessions should complete in under 1 second
        assert cleanup_time < 1.0, f"Cleanup took {cleanup_time:.3f}s, expected < 1.0s"
        assert len(registry.sessions) == 0

    def test_process_validation_performance(self, registry):
        """Test performance of process validation operations."""
        # Register 100 sessions
        for i in range(100):
            registry.register_session(
                backlog_id=f"B-{1000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{1000 + i}.md",
            )

        # Mock process validation to simulate real-world conditions
        with patch("psutil.Process") as mock_process:
            mock_process.return_value.is_running.return_value = False

            start_time = time.time()

            # Run process validation
            registry.validate_processes()

            end_time = time.time()
            validation_time = end_time - start_time

            # Performance assertion: Process validation of 100 sessions should complete in under 0.5 seconds
            assert validation_time < 0.5, f"Process validation took {validation_time:.3f}s, expected < 0.5s"

            # Verify all sessions are marked as orphaned
            for session in registry.sessions.values():
                assert session.status == "orphaned"

    def test_scalability_limits(self, registry):
        """Test scalability limits of the session registry."""
        # Test with realistic number of sessions (50 is our expected maximum)
        realistic_session_count = 50

        start_time = time.time()

        # Register 50 sessions (realistic maximum for our use case)
        for i in range(realistic_session_count):
            registry.register_session(
                backlog_id=f"B-{10000 + i}",
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/B-{10000 + i}.md",
                tags=[f"scalability-test-{i % 10}"],
            )

        end_time = time.time()
        registration_time = end_time - start_time

        # Scalability assertion: 50 sessions should register in under 1 second
        assert registration_time < 1.0, f"Realistic-scale registration took {registration_time:.3f}s, expected < 1.0s"
        assert len(registry.sessions) == realistic_session_count

        # Test memory usage at realistic scale
        process = psutil.Process(os.getpid())
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)

        # Memory assertion: 50 sessions should use less than 1000MB (realistic for test environment)
        assert memory_usage_mb < 1000, f"Memory usage: {memory_usage_mb:.2f}MB, expected < 1000MB"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
