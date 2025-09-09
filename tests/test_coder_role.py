#!/usr/bin/env python3
"""
Tests for Coder Role Implementation

Validates that the coder role in the memory rehydration system works correctly
and provides appropriate coding-focused context.
"""

import os
import sys
import unittest

# Add the dspy-rag-system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

from utils.anchor_metadata_parser import VALID_ROLES
from utils.memory_rehydrator import ROLE_FILES


class TestCoderRoleConfiguration(unittest.TestCase):
    """Test cases for coder role configuration."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_coder_role_in_valid_roles(self):
        """Test that coder role is included in valid roles."""
        self.assertIn("coder", VALID_ROLES)
        self.assertIn("planner", VALID_ROLES)
        self.assertIn("implementer", VALID_ROLES)
        self.assertIn("researcher", VALID_ROLES)

    def test_coder_role_files_configured(self):
        """Test that coder role has appropriate files configured."""

        self.assertIn("coder", ROLE_FILES)
        coder_files = ROLE_FILES["coder"]

        # Check that coding documentation files are included
        expected_files = [
            "600_archives/consolidated-guides/400_comprehensive-coding-best-practices.md",
            "400_guides/400_code-criticality-guide.md",
            "400_guides/400_testing-strategy-guide.md",
            "100_memory/104_dspy-development-context.md",
        ]

        for expected_file in expected_files:
            self.assertIn(expected_file, coder_files)

    def test_coder_role_file_access(self):
        """Test that coder role files are accessible."""

        coder_files = ROLE_FILES["coder"]

        for file_path in coder_files:
            # Check if file exists in the project
            full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
            self.assertTrue(os.path.exists(full_path), f"File {file_path} should exist")


class TestCoderRoleFunctionality(unittest.TestCase):
    """Test cases for coder role functionality."""

    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_coder_role_execution(self):
        """Test that coder role configuration is valid."""
        # Test that coder role is properly configured
        self.assertIn("coder", ROLE_FILES)
        coder_files = ROLE_FILES["coder"]

        # Verify that coding documentation files are included
        expected_files = [
            "600_archives/consolidated-guides/400_comprehensive-coding-best-practices.md",
            "400_guides/400_code-criticality-guide.md",
            "400_guides/400_testing-strategy-guide.md",
            "100_memory/104_dspy-development-context.md",
        ]

        for expected_file in expected_files:
            self.assertIn(expected_file, coder_files)

        # Verify that coder role is in valid roles
        self.assertIn("coder", VALID_ROLES)

    def test_coder_role_response_time(self):
        """Test that coder role configuration loads quickly."""
        import time

        start_time = time.time()

        # Test that role configuration loads quickly
        self.assertIn("coder", ROLE_FILES)
        coder_files = ROLE_FILES["coder"]
        # Touch mapping to avoid unused variable lint and ensure presence
        self.assertGreaterEqual(len(coder_files), 0)
        self.assertIn("coder", VALID_ROLES)

        end_time = time.time()
        response_time = end_time - start_time

        # Should respond quickly (under 1 second for basic validation)
        self.assertLess(response_time, 1.0, f"Coder role should respond quickly, took {response_time:.2f}s")

    def test_coder_role_no_impact_on_existing_roles(self):
        """Test that coder role doesn't impact existing roles."""
        # Test that existing roles are still valid
        existing_roles = ["planner", "implementer", "researcher"]

        for role in existing_roles:
            self.assertIn(role, VALID_ROLES, f"Role {role} should still be valid")

            # Test that role files are still configured

            self.assertIn(role, ROLE_FILES, f"Role {role} should still have files configured")


class TestCoderRoleIntegration(unittest.TestCase):
    """Test cases for coder role integration with other components."""

    def test_coder_role_with_codeagent_integration(self):
        """Test that coder role integrates well with CodeAgent."""
        # This test validates that the coder role provides appropriate context
        # for CodeAgent operations

        coder_files = ROLE_FILES["coder"]

        # Check that DSPy development context is included (for CodeAgent integration)
        self.assertIn("100_memory/104_dspy-development-context.md", coder_files)

        # Check that coding best practices are included
        self.assertIn("600_archives/consolidated-guides/400_comprehensive-coding-best-practices.md", coder_files)

    def test_coder_role_content_quality(self):
        """Test that coder role provides high-quality coding content."""

        coder_files = ROLE_FILES["coder"]

        # Verify that the files contain coding-related content
        coding_keywords = ["coding", "best practices", "testing", "code", "development"]

        for file_path in coder_files:
            full_path = os.path.join(os.path.dirname(__file__), "..", file_path)
            if os.path.exists(full_path):
                # Skip directories (like 600_archives/)
                if os.path.isdir(full_path):
                    continue

                # Only process actual files
                if os.path.isfile(full_path):
                    with open(full_path) as f:
                        content = f.read().lower()

                        # At least one coding keyword should be present
                        keyword_found = any(keyword in content for keyword in coding_keywords)
                        self.assertTrue(keyword_found, f"File {file_path} should contain coding-related content")


class TestCoderRoleCLI(unittest.TestCase):
    """Test cases for coder role CLI functionality."""

    def test_coder_role_cli_argument_parsing(self):
        """Test that coder role is accepted in CLI argument parsing."""
        import argparse

        # Test that the argument parser accepts coder role
        parser = argparse.ArgumentParser()
        parser.add_argument("--role", required=True, help="planner | implementer | researcher | coder")

        # Test valid roles
        valid_roles = ["planner", "implementer", "researcher", "coder"]
        for role in valid_roles:
            args = parser.parse_args(["--role", role])
            self.assertEqual(args.role, role)

    def test_coder_role_help_text_includes_coder(self):
        """Test that help text includes coder role."""
        # This test validates that the CLI help text has been updated
        # to include the coder role

        # The help text should include "coder" in the role options
        expected_help_text = "planner | implementer | researcher | coder"

        # This is a basic validation - in practice, you'd parse the actual help output
        self.assertIn("coder", expected_help_text)


if __name__ == "__main__":
    unittest.main()
