#!/usr/bin/env python3
"""
Performance Tests for Coder Role Implementation

Validates that the coder role meets performance requirements and doesn't
impact the performance of existing roles.
"""

import gc
import os
import sys
import time
import unittest

import psutil

# Add the dspy-rag-system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

from utils.anchor_metadata_parser import VALID_ROLES
from utils.memory_rehydrator import ROLE_FILES


class TestCoderRolePerformance(unittest.TestCase):
    """Performance tests for coder role implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear any cached data
        gc.collect()

    def test_coder_role_configuration_load_time(self):
        """Test that coder role configuration loads quickly."""
        start_time = time.time()

        # Test configuration loading
        self.assertIn("coder", VALID_ROLES)
        coder_files = ROLE_FILES["coder"]

        end_time = time.time()
        load_time = end_time - start_time

        # Should load configuration in under 0.1 seconds
        self.assertLess(load_time, 0.1, f"Configuration loading took {load_time:.3f}s, should be under 0.1s")

    def test_coder_role_memory_usage(self):
        """Test that coder role doesn't use excessive memory."""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Load coder role configuration multiple times
        for _ in range(100):
            self.assertIn("coder", VALID_ROLES)
            coder_files = ROLE_FILES["coder"]

        # Force garbage collection
        gc.collect()

        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be minimal (under 1MB)
        self.assertLess(
            memory_increase,
            1024 * 1024,
            f"Memory usage increased by {memory_increase / 1024:.1f}KB, should be under 1MB",
        )

    def test_coder_role_file_access_performance(self):
        """Test that coder role file access is fast."""
        start_time = time.time()

        coder_files = ROLE_FILES["coder"]

        # Check file existence for all coder files
        for file_path in coder_files:
            full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
            self.assertTrue(os.path.exists(full_path))

        end_time = time.time()
        access_time = end_time - start_time

        # Should access all files in under 0.1 seconds
        self.assertLess(access_time, 0.1, f"File access took {access_time:.3f}s, should be under 0.1s")

    def test_coder_role_no_impact_on_existing_roles(self):
        """Test that coder role doesn't impact existing role performance."""
        existing_roles = ["planner", "implementer", "researcher"]

        # Test performance of existing roles
        for role in existing_roles:
            start_time = time.time()

            # Test role validation
            self.assertIn(role, VALID_ROLES)

            # Test file configuration access
            if role in ROLE_FILES:
                role_files = ROLE_FILES[role]

            end_time = time.time()
            role_time = end_time - start_time

            # Each role should load in under 0.01 seconds
            self.assertLess(role_time, 0.01, f"Role {role} took {role_time:.3f}s, should be under 0.01s")

    def test_coder_role_scalability(self):
        """Test that coder role scales well with multiple accesses."""
        start_time = time.time()

        # Access coder role configuration multiple times
        for _ in range(1000):
            self.assertIn("coder", VALID_ROLES)
            coder_files = ROLE_FILES["coder"]

        end_time = time.time()
        total_time = end_time - start_time

        # 1000 accesses should complete in under 1 second
        self.assertLess(total_time, 1.0, f"1000 accesses took {total_time:.3f}s, should be under 1.0s")

        # Average time per access should be under 1ms
        avg_time = total_time / 1000
        self.assertLess(avg_time, 0.001, f"Average access time {avg_time:.6f}s, should be under 1ms")


class TestCoderRoleBenchmarks(unittest.TestCase):
    """Benchmark tests for coder role performance."""

    def test_coder_role_benchmark_vs_existing_roles(self):
        """Benchmark coder role performance against existing roles."""
        roles = ["planner", "implementer", "researcher", "coder"]
        role_times = {}

        for role in roles:
            start_time = time.time()

            # Test role validation
            self.assertIn(role, VALID_ROLES)

            # Test file configuration access
            if role in ROLE_FILES:
                role_files = ROLE_FILES[role]

            end_time = time.time()
            role_times[role] = end_time - start_time

        # Coder role should be comparable to existing roles
        coder_time = role_times["coder"]
        avg_existing_time = sum(role_times[r] for r in ["planner", "implementer", "researcher"]) / 3

        # If all times are very fast (near 0), that's excellent performance
        if avg_existing_time < 0.000001:  # Less than 1 microsecond
            self.assertLess(coder_time, 0.000001, f"Coder role ({coder_time:.6f}s) should be very fast")
        else:
            # Coder role should not be more than 2x slower than average existing role
            self.assertLess(
                coder_time,
                avg_existing_time * 2,
                f"Coder role ({coder_time:.6f}s) is more than 2x slower than average existing role ({avg_existing_time:.6f}s)",
            )

    def test_coder_role_memory_efficiency(self):
        """Test memory efficiency of coder role configuration."""
        # Get memory usage before
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Load all role configurations
        all_roles = ["planner", "implementer", "researcher", "coder"]
        role_configs = {}

        for role in all_roles:
            self.assertIn(role, VALID_ROLES)
            if role in ROLE_FILES:
                role_configs[role] = ROLE_FILES[role]

        # Force garbage collection
        gc.collect()

        # Get memory usage after
        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory

        # Total memory usage for all roles should be under 5MB
        self.assertLess(
            memory_used, 5 * 1024 * 1024, f"Total memory usage {memory_used / 1024 / 1024:.1f}MB, should be under 5MB"
        )


if __name__ == "__main__":
    unittest.main()
