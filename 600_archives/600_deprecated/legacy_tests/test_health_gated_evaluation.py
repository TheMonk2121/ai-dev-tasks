#!/usr/bin/env python3
"""
Tests for health_gated_evaluation.py

Tests the health-gated evaluation system that checks system health
before running evaluations.
"""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.evaluation.health_gated_evaluation import HealthGatedEvaluator


class TestHealthGatedEvaluator:
    """Test cases for HealthGatedEvaluator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = HealthGatedEvaluator()

    def test_initialization(self):
        """Test evaluator initializes correctly."""
        assert self.evaluator is not None
        assert hasattr(self.evaluator, "checks_enabled")
        assert isinstance(self.evaluator.checks_enabled, dict)

    def test_checks_enabled_structure(self):
        """Test that checks_enabled has expected structure."""
        expected_checks = [
            "database_connectivity",
            "memory_system_health",
            "evaluation_data_availability",
            "system_resources",
            "dependencies",
        ]

        for check in expected_checks:
            assert check in self.evaluator.checks_enabled
            assert isinstance(self.evaluator.checks_enabled[check], bool)

    @patch("scripts.evaluation.health_gated_evaluation.psycopg.connect")
    def test_database_connectivity_check_success(self, mock_connect):
        """Test database connectivity check passes."""
        # Mock successful database connection
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        result = self.evaluator._check_database_connectivity()
        assert result is True

    @patch("scripts.evaluation.health_gated_evaluation.psycopg.connect")
    def test_database_connectivity_check_failure(self, mock_connect):
        """Test database connectivity check fails."""
        # Mock database connection failure
        mock_connect.side_effect = Exception("Connection failed")

        result = self.evaluator._check_database_connectivity()
        assert result is False

    @patch("scripts.evaluation.health_gated_evaluation.os.path.exists")
    def test_memory_system_health_check_success(self, mock_exists):
        """Test memory system health check passes."""
        # Mock memory system files exist
        mock_exists.return_value = True

        result = self.evaluator._check_memory_system_health()
        assert result is True

    @patch("scripts.evaluation.health_gated_evaluation.os.path.exists")
    def test_memory_system_health_check_failure(self, mock_exists):
        """Test memory system health check fails."""
        # Mock memory system files don't exist
        mock_exists.return_value = False

        result = self.evaluator._check_memory_system_health()
        assert result is False

    @patch("scripts.evaluation.health_gated_evaluation.Path.exists")
    def test_evaluation_data_availability_check_success(self, mock_exists):
        """Test evaluation data availability check passes."""
        # Mock evaluation data files exist
        mock_exists.return_value = True

        result = self.evaluator._check_evaluation_data_availability()
        assert result is True

    @patch("scripts.evaluation.health_gated_evaluation.Path.exists")
    def test_evaluation_data_availability_check_failure(self, mock_exists):
        """Test evaluation data availability check fails."""
        # Mock evaluation data files don't exist
        mock_exists.return_value = False

        result = self.evaluator._check_evaluation_data_availability()
        assert result is False

    @patch("scripts.evaluation.health_gated_evaluation.psutil")
    def test_system_resources_check_success(self, mock_psutil):
        """Test system resources check passes."""
        # Mock sufficient system resources
        mock_psutil.virtual_memory.return_value.percent = 50.0
        mock_psutil.disk_usage.return_value.percent = 60.0

        result = self.evaluator._check_system_resources()
        assert result is True

    @patch("scripts.evaluation.health_gated_evaluation.psutil")
    def test_system_resources_check_failure(self, mock_psutil):
        """Test system resources check fails."""
        # Mock insufficient system resources
        mock_psutil.virtual_memory.return_value.percent = 95.0
        mock_psutil.disk_usage.return_value.percent = 90.0

        result = self.evaluator._check_system_resources()
        assert result is False

    @patch("scripts.evaluation.health_gated_evaluation.importlib.import_module")
    def test_dependencies_check_success(self, mock_import):
        """Test dependencies check passes."""
        # Mock successful imports
        mock_import.return_value = Mock()

        result = self.evaluator._check_dependencies()
        assert result is True

    @patch("scripts.evaluation.health_gated_evaluation.importlib.import_module")
    def test_dependencies_check_failure(self, mock_import):
        """Test dependencies check fails."""
        # Mock import failure
        mock_import.side_effect = ImportError("Module not found")

        result = self.evaluator._check_dependencies()
        assert result is False

    @patch.object(HealthGatedEvaluator, "_check_database_connectivity")
    @patch.object(HealthGatedEvaluator, "_check_memory_system_health")
    @patch.object(HealthGatedEvaluator, "_check_evaluation_data_availability")
    @patch.object(HealthGatedEvaluator, "_check_system_resources")
    @patch.object(HealthGatedEvaluator, "_check_dependencies")
    def test_run_health_checks_all_pass(
        self, mock_deps, mock_resources, mock_data, mock_memory, mock_db
    ):
        """Test run_health_checks when all checks pass."""
        # Mock all checks pass
        mock_db.return_value = True
        mock_memory.return_value = True
        mock_data.return_value = True
        mock_resources.return_value = True
        mock_deps.return_value = True

        is_healthy, failed_checks, warning_checks = self.evaluator.run_health_checks()

        assert is_healthy is True
        assert len(failed_checks) == 0
        assert len(warning_checks) == 0

    @patch.object(HealthGatedEvaluator, "_check_database_connectivity")
    @patch.object(HealthGatedEvaluator, "_check_memory_system_health")
    @patch.object(HealthGatedEvaluator, "_check_evaluation_data_availability")
    @patch.object(HealthGatedEvaluator, "_check_system_resources")
    @patch.object(HealthGatedEvaluator, "_check_dependencies")
    def test_run_health_checks_some_fail(
        self, mock_deps, mock_resources, mock_data, mock_memory, mock_db
    ):
        """Test run_health_checks when some checks fail."""
        # Mock some checks fail
        mock_db.return_value = False
        mock_memory.return_value = True
        mock_data.return_value = False
        mock_resources.return_value = True
        mock_deps.return_value = True

        is_healthy, failed_checks, warning_checks = self.evaluator.run_health_checks()

        assert is_healthy is False
        assert len(failed_checks) == 2
        assert "database_connectivity" in failed_checks
        assert "evaluation_data_availability" in failed_checks

    def test_should_proceed_with_evaluation_all_checks_enabled(self):
        """Test should_proceed_with_evaluation when all checks are enabled."""
        # Enable all checks
        for check in self.evaluator.checks_enabled:
            self.evaluator.checks_enabled[check] = True

        with patch.object(self.evaluator, "run_health_checks") as mock_run:
            mock_run.return_value = (True, [], [])

            result = self.evaluator.should_proceed_with_evaluation()
            assert result is True

    def test_should_proceed_with_evaluation_some_checks_disabled(self):
        """Test should_proceed_with_evaluation when some checks are disabled."""
        # Disable some checks
        self.evaluator.checks_enabled["database_connectivity"] = False
        self.evaluator.checks_enabled["memory_system_health"] = False

        with patch.object(self.evaluator, "run_health_checks") as mock_run:
            mock_run.return_value = (False, ["database_connectivity"], [])

            result = self.evaluator.should_proceed_with_evaluation()
            assert result is False

    @patch("builtins.print")
    def test_print_health_report_healthy(self, mock_print):
        """Test print_health_report when system is healthy."""
        self.evaluator.print_health_report(True, [], [])

        # Should print success message
        mock_print.assert_called()
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("✅ System is healthy" in call for call in calls)

    @patch("builtins.print")
    def test_print_health_report_unhealthy(self, mock_print):
        """Test print_health_report when system is unhealthy."""
        failed_checks = ["database_connectivity", "memory_system_health"]
        self.evaluator.print_health_report(False, failed_checks, [])

        # Should print failure message
        mock_print.assert_called()
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert any("❌ System health checks failed" in call for call in calls)


class TestHealthGatedEvaluationMain:
    """Test cases for the main function and CLI interface."""

    @patch("scripts.evaluation.health_gated_evaluation.HealthGatedEvaluator")
    @patch("sys.argv", ["health_gated_evaluation.py", "--check-only"])
    def test_main_check_only(self, mock_evaluator_class):
        """Test main function with --check-only flag."""
        mock_evaluator = Mock()
        mock_evaluator.run_health_checks.return_value = (True, [], [])
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.health_gated_evaluation.sys.exit") as mock_exit:
            from scripts.evaluation.health_gated_evaluation import main

            main()

            mock_evaluator.run_health_checks.assert_called_once()
            mock_evaluator.print_health_report.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.health_gated_evaluation.HealthGatedEvaluator")
    @patch("sys.argv", ["health_gated_evaluation.py"])
    def test_main_full_evaluation(self, mock_evaluator_class):
        """Test main function for full evaluation."""
        mock_evaluator = Mock()
        mock_evaluator.should_proceed_with_evaluation.return_value = True
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.health_gated_evaluation.sys.exit") as mock_exit:
            from scripts.evaluation.health_gated_evaluation import main

            main()

            mock_evaluator.should_proceed_with_evaluation.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.health_gated_evaluation.HealthGatedEvaluator")
    @patch(
        "sys.argv",
        ["health_gated_evaluation.py", "--disable-check", "database_connectivity"],
    )
    def test_main_disable_check(self, mock_evaluator_class):
        """Test main function with --disable-check flag."""
        mock_evaluator = Mock()
        mock_evaluator.checks_enabled = {"database_connectivity": True}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.health_gated_evaluation.sys.exit") as mock_exit:
            from scripts.evaluation.health_gated_evaluation import main

            main()

            # Check that the specified check was disabled
            assert mock_evaluator.checks_enabled["database_connectivity"] is False
            mock_exit.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
