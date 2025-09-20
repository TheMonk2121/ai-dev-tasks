"""
Tests for eval_optimization_suite.py

Comprehensive tests for the evaluation optimization suite.
Tests cover optimization components, configuration management, and reporting.
"""

#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "300_evals"))

from scripts.evaluation.eval_optimization_suite import (
    generate_optimization_report,
    main,
    run_baseline_eval,
    run_deterministic_few_shot_eval,
    setup_agent_memory_blueprint,
    setup_dataset_traps,
    setup_determinism_switches,
    setup_observability_traps,
    setup_tool_traps,
)


class TestOptimizationSetup:
    """Test cases for optimization setup functions."""

    def test_setup_determinism_switches(self):
        """Test setup_determinism_switches function."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        with patch("scripts.evaluation.eval_optimization_suite.DeterminismManager") as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            result = setup_determinism_switches(mock_config)

            assert result == mock_instance
            mock_manager.assert_called_once()

    def test_setup_dataset_traps(self):
        """Test setup_dataset_traps function."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        with patch("scripts.evaluation.eval_optimization_suite.DatasetTrapManager") as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            result = setup_dataset_traps(mock_config)

            assert result == mock_instance
            mock_manager.assert_called_once()

    def test_setup_tool_traps(self):
        """Test setup_tool_traps function."""
        with patch("scripts.evaluation.eval_optimization_suite.ToolTrapManager") as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            result = setup_tool_traps()

            assert result == mock_instance
            mock_manager.assert_called_once()

    def test_setup_observability_traps(self):
        """Test setup_observability_traps function."""
        with patch("scripts.evaluation.eval_optimization_suite.ObservabilityManager") as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            result = setup_observability_traps()

            assert result == mock_instance
            mock_manager.assert_called_once()

    def test_setup_agent_memory_blueprint(self):
        """Test setup_agent_memory_blueprint function."""
        with patch("scripts.evaluation.eval_optimization_suite.AgentMemoryManager") as mock_manager:
            mock_instance = Mock()
            mock_manager.return_value = mock_instance

            result = setup_agent_memory_blueprint()

            assert result == mock_instance
            mock_manager.assert_called_once()


class TestEvaluationRunners:
    """Test cases for evaluation runner functions."""

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_baseline_eval_success(self, mock_subprocess):
        """Test run_baseline_eval executes successfully."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = json.dumps({"precision": 0.85, "recall": 0.75, "f1_score": 0.80})
        mock_subprocess.return_value = mock_proc

        result = run_baseline_eval(mock_config, 10)

        assert result
        assert result
        assert result
        mock_subprocess.assert_called_once()

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_baseline_eval_failure(self, mock_subprocess):
        """Test run_baseline_eval handles subprocess failure."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess failure
        mock_proc = Mock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "Evaluation failed"
        mock_subprocess.return_value = mock_proc

        result = run_baseline_eval(mock_config, 10)

        assert result
        assert "Evaluation failed" in result
        mock_subprocess.assert_called_once()

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_deterministic_few_shot_eval_success(self, mock_subprocess):
        """Test run_deterministic_few_shot_eval executes successfully."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = json.dumps({"precision": 0.90, "recall": 0.80, "f1_score": 0.85})
        mock_subprocess.return_value = mock_proc

        result = run_deterministic_few_shot_eval(mock_config, 10)

        assert result
        assert result
        assert result
        mock_subprocess.assert_called_once()

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_deterministic_few_shot_eval_failure(self, mock_subprocess):
        """Test run_deterministic_few_shot_eval handles subprocess failure."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess failure
        mock_proc = Mock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        mock_proc.stderr = "Few-shot evaluation failed"
        mock_subprocess.return_value = mock_proc

        result = run_deterministic_few_shot_eval(mock_config, 10)

        assert result
        assert "Few-shot evaluation failed" in result
        mock_subprocess.assert_called_once()

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_baseline_eval_invalid_json(self, mock_subprocess):
        """Test run_baseline_eval handles invalid JSON output."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess with invalid JSON
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "invalid json"
        mock_subprocess.return_value = mock_proc

        result = run_baseline_eval(mock_config, 10)

        assert result
        assert "JSON" in result

    @patch("scripts.evaluation.eval_optimization_suite.subprocess.run")
    def test_run_deterministic_few_shot_eval_invalid_json(self, mock_subprocess):
        """Test run_deterministic_few_shot_eval handles invalid JSON output."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"

        # Mock subprocess with invalid JSON
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "invalid json"
        mock_subprocess.return_value = mock_proc

        result = run_deterministic_few_shot_eval(mock_config, 10)

        assert result
        assert "JSON" in result


class TestOptimizationReport:
    """Test cases for optimization report generation."""

    def test_generate_optimization_report_success(self):
        """Test generate_optimization_report creates report successfully."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"

        mock_determinism = Mock()
        mock_dataset = Mock()
        mock_tool = Mock()
        mock_observability = Mock()
        mock_memory = Mock()

        baseline_results = {"precision": 0.85, "recall": 0.75, "f1_score": 0.80}
        few_shot_results = {"precision": 0.90, "recall": 0.80, "f1_score": 0.85}

        report = generate_optimization_report(
            mock_config,
            mock_determinism,
            mock_dataset,
            mock_tool,
            mock_observability,
            mock_memory,
            baseline_results,
            few_shot_results,
        )

        assert "timestamp" in report
        assert "config_hash" in report
        assert "baseline_results" in report
        assert "few_shot_results" in report
        assert "optimization_summary" in report
        assert "recommendations" in report
        assert result
        assert result

    def test_generate_optimization_report_with_failures(self):
        """Test generate_optimization_report handles failed evaluations."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"

        mock_determinism = Mock()
        mock_dataset = Mock()
        mock_tool = Mock()
        mock_observability = Mock()
        mock_memory = Mock()

        baseline_results = {"status": "failed", "error": "Baseline evaluation failed"}
        few_shot_results = {"status": "failed", "error": "Few-shot evaluation failed"}

        report = generate_optimization_report(
            mock_config,
            mock_determinism,
            mock_dataset,
            mock_tool,
            mock_observability,
            mock_memory,
            baseline_results,
            few_shot_results,
        )

        assert "timestamp" in report
        assert "config_hash" in report
        assert "baseline_results" in report
        assert "few_shot_results" in report
        assert "optimization_summary" in report
        assert "recommendations" in report
        assert result
        assert result

    def test_generate_optimization_report_mixed_results(self):
        """Test generate_optimization_report with mixed success/failure results."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"

        mock_determinism = Mock()
        mock_dataset = Mock()
        mock_tool = Mock()
        mock_observability = Mock()
        mock_memory = Mock()

        baseline_results = {"precision": 0.85, "recall": 0.75, "f1_score": 0.80}
        few_shot_results = {"status": "failed", "error": "Few-shot evaluation failed"}

        report = generate_optimization_report(
            mock_config,
            mock_determinism,
            mock_dataset,
            mock_tool,
            mock_observability,
            mock_memory,
            baseline_results,
            few_shot_results,
        )

        assert "timestamp" in report
        assert "config_hash" in report
        assert "baseline_results" in report
        assert "few_shot_results" in report
        assert "optimization_summary" in report
        assert "recommendations" in report
        assert result
        assert result


class TestEvalOptimizationSuiteCLI:
    """Test cases for CLI interface."""

    @patch("scripts.evaluation.eval_optimization_suite.ConfigLockManager")
    @patch("scripts.evaluation.eval_optimization_suite.setup_determinism_switches")
    @patch("scripts.evaluation.eval_optimization_suite.setup_dataset_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_tool_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_observability_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_agent_memory_blueprint")
    @patch("scripts.evaluation.eval_optimization_suite.run_baseline_eval")
    @patch("scripts.evaluation.eval_optimization_suite.run_deterministic_few_shot_eval")
    @patch("scripts.evaluation.eval_optimization_suite.generate_optimization_report")
    @patch("builtins.open", mock_open())
    @patch("json.dump")
    def test_main_success(
        self,
        mock_json_dump,
        mock_file,
        mock_generate_report,
        mock_few_shot_eval,
        mock_baseline_eval,
        mock_memory,
        mock_observability,
        mock_tool,
        mock_dataset,
        mock_determinism,
        mock_config_manager,
    ):
        """Test main function runs successfully."""
        # Mock config manager
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"
        mock_config_manager.return_value.get_active_config.return_value = mock_config

        # Mock setup functions
        mock_determinism.return_value = Mock()
        mock_dataset.return_value = Mock()
        mock_tool.return_value = Mock()
        mock_observability.return_value = Mock()
        mock_memory.return_value = Mock()

        # Mock evaluation results
        mock_baseline_eval.return_value = {
            "precision": 0.85,
            "recall": 0.75,
            "f1_score": 0.80,
        }
        mock_few_shot_eval.return_value = {
            "precision": 0.90,
            "recall": 0.80,
            "f1_score": 0.85,
        }

        # Mock report generation
        mock_report = {"test": "report"}
        mock_generate_report.return_value = mock_report

        with patch(
            "sys.argv",
            [
                "eval_optimization_suite.py",
                "--num-queries",
                "10",
                "--output",
                "test_report.json",
            ],
        ):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                main()

                mock_config_manager.assert_called_once()
                mock_determinism.assert_called_once_with(mock_config)
                mock_dataset.assert_called_once_with(mock_config)
                mock_tool.assert_called_once()
                mock_observability.assert_called_once()
                mock_memory.assert_called_once()
                mock_baseline_eval.assert_called_once_with(mock_config, 10)
                mock_few_shot_eval.assert_called_once_with(mock_config, 10)
                mock_generate_report.assert_called_once()
                mock_json_dump.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.eval_optimization_suite.ConfigLockManager")
    def test_main_no_active_config(self, mock_config_manager):
        """Test main function handles no active configuration."""
        mock_config_manager.return_value.get_active_config.return_value = None

        with patch("sys.argv", ["eval_optimization_suite.py"]):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    mock_exit.assert_called_once_with(1)
                    mock_print.assert_called()

    @patch("scripts.evaluation.eval_optimization_suite.ConfigLockManager")
    @patch("scripts.evaluation.eval_optimization_suite.setup_determinism_switches")
    @patch("scripts.evaluation.eval_optimization_suite.setup_dataset_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_tool_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_observability_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_agent_memory_blueprint")
    @patch("scripts.evaluation.eval_optimization_suite.run_baseline_eval")
    @patch("scripts.evaluation.eval_optimization_suite.run_deterministic_few_shot_eval")
    @patch("scripts.evaluation.eval_optimization_suite.generate_optimization_report")
    def test_main_quiet_mode(
        self,
        mock_generate_report,
        mock_few_shot_eval,
        mock_baseline_eval,
        mock_memory,
        mock_observability,
        mock_tool,
        mock_dataset,
        mock_determinism,
        mock_config_manager,
    ):
        """Test main function in quiet mode."""
        # Mock config manager
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"
        mock_config_manager.return_value.get_active_config.return_value = mock_config

        # Mock setup functions
        mock_determinism.return_value = Mock()
        mock_dataset.return_value = Mock()
        mock_tool.return_value = Mock()
        mock_observability.return_value = Mock()
        mock_memory.return_value = Mock()

        # Mock evaluation results
        mock_baseline_eval.return_value = {
            "precision": 0.85,
            "recall": 0.75,
            "f1_score": 0.80,
        }
        mock_few_shot_eval.return_value = {
            "precision": 0.90,
            "recall": 0.80,
            "f1_score": 0.85,
        }

        # Mock report generation
        mock_report = {"test": "report"}
        mock_generate_report.return_value = mock_report

        with patch("sys.argv", ["eval_optimization_suite.py", "--quiet"]):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should not print anything in quiet mode
                    mock_print.assert_not_called()
                    mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.eval_optimization_suite.ConfigLockManager")
    @patch("scripts.evaluation.eval_optimization_suite.setup_determinism_switches")
    @patch("scripts.evaluation.eval_optimization_suite.setup_dataset_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_tool_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_observability_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_agent_memory_blueprint")
    @patch("scripts.evaluation.eval_optimization_suite.run_baseline_eval")
    @patch("scripts.evaluation.eval_optimization_suite.run_deterministic_few_shot_eval")
    @patch("scripts.evaluation.eval_optimization_suite.generate_optimization_report")
    def test_main_default_arguments(
        self,
        mock_generate_report,
        mock_few_shot_eval,
        mock_baseline_eval,
        mock_memory,
        mock_observability,
        mock_tool,
        mock_dataset,
        mock_determinism,
        mock_config_manager,
    ):
        """Test main function with default arguments."""
        # Mock config manager
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"
        mock_config_manager.return_value.get_active_config.return_value = mock_config

        # Mock setup functions
        mock_determinism.return_value = Mock()
        mock_dataset.return_value = Mock()
        mock_tool.return_value = Mock()
        mock_observability.return_value = Mock()
        mock_memory.return_value = Mock()

        # Mock evaluation results
        mock_baseline_eval.return_value = {
            "precision": 0.85,
            "recall": 0.75,
            "f1_score": 0.80,
        }
        mock_few_shot_eval.return_value = {
            "precision": 0.90,
            "recall": 0.80,
            "f1_score": 0.85,
        }

        # Mock report generation
        mock_report = {"test": "report"}
        mock_generate_report.return_value = mock_report

        with patch("sys.argv", ["eval_optimization_suite.py"]):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                main()

                # Check default num_queries (50)
                mock_baseline_eval.assert_called_once_with(mock_config, 50)
                mock_few_shot_eval.assert_called_once_with(mock_config, 50)
                mock_exit.assert_called_once_with(0)

    @patch("sys.argv", ["eval_optimization_suite.py", "--help"])
    def test_main_help(self):
        """Test main function shows help."""
        with patch("scripts.evaluation.eval_optimization_suite.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)


class TestEvalOptimizationSuiteIntegration:
    """Integration tests for eval_optimization_suite.py."""

    @patch("scripts.evaluation.eval_optimization_suite.ConfigLockManager")
    @patch("scripts.evaluation.eval_optimization_suite.setup_determinism_switches")
    @patch("scripts.evaluation.eval_optimization_suite.setup_dataset_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_tool_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_observability_traps")
    @patch("scripts.evaluation.eval_optimization_suite.setup_agent_memory_blueprint")
    @patch("scripts.evaluation.eval_optimization_suite.run_baseline_eval")
    @patch("scripts.evaluation.eval_optimization_suite.run_deterministic_few_shot_eval")
    def test_full_optimization_workflow(
        self,
        mock_few_shot_eval,
        mock_baseline_eval,
        mock_memory,
        mock_observability,
        mock_tool,
        mock_dataset,
        mock_determinism,
        mock_config_manager,
    ):
        """Test full optimization workflow integration."""
        # Mock config manager
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"
        mock_config_manager.return_value.get_active_config.return_value = mock_config

        # Mock setup functions
        mock_determinism.return_value = Mock()
        mock_dataset.return_value = Mock()
        mock_tool.return_value = Mock()
        mock_observability.return_value = Mock()
        mock_memory.return_value = Mock()

        # Mock evaluation results
        mock_baseline_eval.return_value = {
            "precision": 0.85,
            "recall": 0.75,
            "f1_score": 0.80,
        }
        mock_few_shot_eval.return_value = {
            "precision": 0.90,
            "recall": 0.80,
            "f1_score": 0.85,
        }

        with patch("sys.argv", ["eval_optimization_suite.py", "--num-queries", "25"]):
            with patch("scripts.evaluation.eval_optimization_suite.sys.exit") as mock_exit:
                with patch("scripts.evaluation.eval_optimization_suite.generate_optimization_report") as mock_generate:
                    mock_generate.return_value = {"test": "report"}

                    main()

                    # Verify all components were called
                    mock_config_manager.assert_called_once()
                    mock_determinism.assert_called_once_with(mock_config)
                    mock_dataset.assert_called_once_with(mock_config)
                    mock_tool.assert_called_once()
                    mock_observability.assert_called_once()
                    mock_memory.assert_called_once()
                    mock_baseline_eval.assert_called_once_with(mock_config, 25)
                    mock_few_shot_eval.assert_called_once_with(mock_config, 25)
                    mock_generate.assert_called_once()
                    mock_exit.assert_called_once_with(0)

    def test_optimization_report_structure(self):
        """Test optimization report structure and content."""
        mock_config = Mock()
        mock_config.chunk_version = "test_v1"
        mock_config.get_config_hash.return_value = "abc123"

        mock_determinism = Mock()
        mock_dataset = Mock()
        mock_tool = Mock()
        mock_observability = Mock()
        mock_memory = Mock()

        baseline_results = {"precision": 0.85, "recall": 0.75, "f1_score": 0.80}
        few_shot_results = {"precision": 0.90, "recall": 0.80, "f1_score": 0.85}

        report = generate_optimization_report(
            mock_config,
            mock_determinism,
            mock_dataset,
            mock_tool,
            mock_observability,
            mock_memory,
            baseline_results,
            few_shot_results,
        )

        # Check report structure
        required_fields = [
            "timestamp",
            "config_hash",
            "chunk_version",
            "baseline_results",
            "few_shot_results",
            "optimization_summary",
            "recommendations",
        ]

        for field in required_fields:
            assert field in report

        # Check optimization summary structure
        assert "performance_comparison" in result
        assert "improvement_areas" in result
        assert "optimization_score" in result

        # Check recommendations structure
        assert isinstance(result
        assert len(result


if __name__ == "__main__":
    pytest.main([__file__])
