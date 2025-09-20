"""
Tests for metrics_guard.py

Comprehensive tests for the metrics guard script.
Tests cover baseline compliance checking, metrics validation, and quality gates.
"""

#!/usr/bin/env python3

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "300_evals"))

from scripts.evaluation.metrics_guard import (
    check_baseline_compliance,
    check_quality_gates,
    main,
    validate_metrics_format,
)


class TestBaselineCompliance:
    """Test cases for baseline compliance checking."""

    def test_check_baseline_compliance_success(self: Any):
        """Test baseline compliance checking succeeds."""
        # Mock results file with good metrics
        mock_results: dict[str, object] = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            assert result is True

    def test_check_baseline_compliance_failure(self: Any):
        """Test baseline compliance checking fails when metrics are below baseline."""
        # Mock results file with poor metrics
        mock_results: dict[str, object] = {
            "overall_metrics": {
                "precision": 0.70,
                "recall": 0.65,
                "f1_score": 0.67,
                "accuracy": 0.75,
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            assert result is False

    def test_check_baseline_compliance_missing_metrics(self: Any):
        """Test baseline compliance checking handles missing metrics."""
        # Mock results file with missing metrics
        mock_results: dict[str, object] = {
            "overall_metrics": {
                "precision": 0.85
                # Missing other metrics
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            assert result is False

    def test_check_baseline_compliance_missing_baseline(self: Any):
        """Test baseline compliance checking handles missing baseline metrics."""
        # Mock results file with missing baseline
        mock_results: dict[str, object] = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            }
            # Missing baseline_metrics
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            assert result is False

    def test_check_baseline_compliance_invalid_json(self: Any):
        """Test baseline compliance checking handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = check_baseline_compliance("test_results.json")

            assert result is False

    def test_check_baseline_compliance_file_not_found(self: Any):
        """Test baseline compliance checking handles file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = check_baseline_compliance("nonexistent.json")

            assert result is False

    def test_check_baseline_compliance_edge_case_equal_metrics(self: Any):
        """Test baseline compliance checking with metrics equal to baseline."""
        # Mock results file with metrics equal to baseline
        mock_results = {
            "overall_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            assert result is True

    def test_check_baseline_compliance_mixed_metrics(self: Any):
        """Test baseline compliance checking with mixed metric performance."""
        # Mock results file with some metrics above and some below baseline
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,  # Above baseline
                "recall": 0.70,  # Below baseline
                "f1_score": 0.77,  # Equal to baseline
                "accuracy": 0.90,  # Above baseline
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_baseline_compliance("test_results.json")

            # Should fail because recall is below baseline
            assert result is False


class TestMetricsFormatValidation:
    """Test cases for metrics format validation."""

    def test_validate_metrics_format_success(self: Any):
        """Test metrics format validation succeeds."""
        # Mock results file with valid format
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
            "timestamp": "2024-01-01T12:00:00Z",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = validate_metrics_format("test_results.json")

            assert result is True

    def test_validate_metrics_format_missing_required_fields(self: Any):
        """Test metrics format validation fails with missing required fields."""
        # Mock results file with missing required fields
        mock_results = {
            "overall_metrics": {
                "precision": 0.85
                # Missing other required metrics
            }
            # Missing case_results and timestamp
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = validate_metrics_format("test_results.json")

            assert result is False

    def test_validate_metrics_format_invalid_metric_values(self: Any):
        """Test metrics format validation fails with invalid metric values."""
        # Mock results file with invalid metric values
        empty_cases: list[dict[str, object]] = []
        mock_results = {
            "overall_metrics": {
                "precision": "invalid",  # Should be float
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": empty_cases,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = validate_metrics_format("test_results.json")

            assert result is False

    def test_validate_metrics_format_invalid_case_results(self: Any):
        """Test metrics format validation fails with invalid case results."""
        # Mock results file with invalid case results
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [{"case_id": "test_001", "status": "success"}],  # Missing score
            "timestamp": "2024-01-01T12:00:00Z",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = validate_metrics_format("test_results.json")

            assert result is False

    def test_validate_metrics_format_invalid_json(self: Any):
        """Test metrics format validation handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = validate_metrics_format("test_results.json")

            assert result is False

    def test_validate_metrics_format_file_not_found(self: Any):
        """Test metrics format validation handles file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = validate_metrics_format("nonexistent.json")

            assert result is False


class TestQualityGates:
    """Test cases for quality gates checking."""

    def test_check_quality_gates_success(self: Any):
        """Test quality gates checking succeeds."""
        # Mock results file with good metrics
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is True

    def test_check_quality_gates_failure_low_precision(self: Any):
        """Test quality gates checking fails with low precision."""
        # Mock results file with low precision
        mock_results = {
            "overall_metrics": {
                "precision": 0.70,  # Below threshold
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.70},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_failure_low_recall(self: Any):
        """Test quality gates checking fails with low recall."""
        # Mock results file with low recall
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.70,  # Below threshold
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_failure_low_f1_score(self: Any):
        """Test quality gates checking fails with low F1 score."""
        # Mock results file with low F1 score
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.70,  # Below threshold
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_failure_high_failure_rate(self: Any):
        """Test quality gates checking fails with high failure rate."""
        # Mock results file with high failure rate
        mock_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "error", "score": 0.0},
                {"case_id": "test_003", "status": "error", "score": 0.0},
                {"case_id": "test_004", "status": "error", "score": 0.0},
            ],
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_missing_metrics(self: Any):
        """Test quality gates checking handles missing metrics."""
        # Mock results file with missing metrics
        empty_cases2: list[dict[str, object]] = []
        mock_results = {
            "overall_metrics": {
                "precision": 0.85
                # Missing other metrics
            },
            "case_results": empty_cases2,
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_results))):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_invalid_json(self: Any):
        """Test quality gates checking handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = check_quality_gates("test_results.json")

            assert result is False

    def test_check_quality_gates_file_not_found(self: Any):
        """Test quality gates checking handles file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = check_quality_gates("nonexistent.json")

            assert result is False


class TestMetricsGuardCLI:
    """Test cases for CLI interface."""

    @patch("scripts.evaluation.metrics_guard.check_baseline_compliance")
    @patch("scripts.evaluation.metrics_guard.validate_metrics_format")
    @patch("scripts.evaluation.metrics_guard.check_quality_gates")
    def test_main_success(self, mock_quality_gates: Any, mock_format: Any, mock_baseline: Any) -> Any:
        """Test main function runs successfully."""
        # Mock all checks to pass
        mock_baseline.return_value = True
        mock_format.return_value = True
        mock_quality_gates.return_value = True

        with patch("sys.argv", ["metrics_guard.py", "--results-file", "test_results.json"]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify all checks were called
                    mock_baseline.assert_called_once_with("test_results.json")
                    mock_format.assert_called_once_with("test_results.json")
                    mock_quality_gates.assert_called_once_with("test_results.json")

                    # Verify output was printed
                    mock_print.assert_called()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.metrics_guard.check_baseline_compliance")
    @patch("scripts.evaluation.metrics_guard.validate_metrics_format")
    @patch("scripts.evaluation.metrics_guard.check_quality_gates")
    def test_main_baseline_failure(self, mock_quality_gates: Any, mock_format: Any, mock_baseline: Any) -> Any:
        """Test main function handles baseline compliance failure."""
        # Mock baseline check to fail
        mock_baseline.return_value = False
        mock_format.return_value = True
        mock_quality_gates.return_value = True

        with patch("sys.argv", ["metrics_guard.py", "--results-file", "test_results.json"]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify all checks were called
                    mock_baseline.assert_called_once_with("test_results.json")
                    mock_format.assert_called_once_with("test_results.json")
                    mock_quality_gates.assert_called_once_with("test_results.json")

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)

    @patch("scripts.evaluation.metrics_guard.check_baseline_compliance")
    @patch("scripts.evaluation.metrics_guard.validate_metrics_format")
    @patch("scripts.evaluation.metrics_guard.check_quality_gates")
    def test_main_format_failure(self, mock_quality_gates: Any, mock_format: Any, mock_baseline: Any) -> Any:
        """Test main function handles format validation failure."""
        # Mock format check to fail
        mock_baseline.return_value = True
        mock_format.return_value = False
        mock_quality_gates.return_value = True

        with patch("sys.argv", ["metrics_guard.py", "--results-file", "test_results.json"]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify all checks were called
                    mock_baseline.assert_called_once_with("test_results.json")
                    mock_format.assert_called_once_with("test_results.json")
                    mock_quality_gates.assert_called_once_with("test_results.json")

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)

    @patch("scripts.evaluation.metrics_guard.check_baseline_compliance")
    @patch("scripts.evaluation.metrics_guard.validate_metrics_format")
    @patch("scripts.evaluation.metrics_guard.check_quality_gates")
    def test_main_quality_gates_failure(self, mock_quality_gates: Any, mock_format: Any, mock_baseline: Any) -> Any:
        """Test main function handles quality gates failure."""
        # Mock quality gates check to fail
        mock_baseline.return_value = True
        mock_format.return_value = True
        mock_quality_gates.return_value = False

        with patch("sys.argv", ["metrics_guard.py", "--results-file", "test_results.json"]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify all checks were called
                    mock_baseline.assert_called_once_with("test_results.json")
                    mock_format.assert_called_once_with("test_results.json")
                    mock_quality_gates.assert_called_once_with("test_results.json")

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)

    @patch("scripts.evaluation.metrics_guard.check_baseline_compliance")
    @patch("scripts.evaluation.metrics_guard.validate_metrics_format")
    @patch("scripts.evaluation.metrics_guard.check_quality_gates")
    def test_main_default_arguments(self, mock_quality_gates: Any, mock_format: Any, mock_baseline: Any) -> Any:
        """Test main function with default arguments."""
        # Mock all checks to pass
        mock_baseline.return_value = True
        mock_format.return_value = True
        mock_quality_gates.return_value = True

        with patch("sys.argv", ["metrics_guard.py"]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify default results file was used
                    mock_baseline.assert_called_once_with("metrics/baseline_evaluations/latest_results.json")
                    mock_format.assert_called_once_with("metrics/baseline_evaluations/latest_results.json")
                    mock_quality_gates.assert_called_once_with("metrics/baseline_evaluations/latest_results.json")

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)

    @patch("sys.argv", ["metrics_guard.py", "--help"])
    def test_main_help(self: Any):
        """Test main function shows help."""
        with patch("scripts.evaluation.metrics_guard.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)


class TestMetricsGuardIntegration:
    """Integration tests for metrics_guard.py."""

    temp_dir: str = ""

    def setup_method(self: Any):
        """Set up test fixtures."""
        self.temp_dir: Any = tempfile.mkdtemp()

    def teardown_method(self: Any):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def test_full_validation_workflow(self: Any):
        """Test full validation workflow integration."""
        # Create test results file
        test_results = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.80,
                "f1_score": 0.82,
                "accuracy": 0.90,
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
            "case_results": [
                {"case_id": "test_001", "status": "success", "score": 0.85},
                {"case_id": "test_002", "status": "success", "score": 0.80},
            ],
            "timestamp": "2024-01-01T12:00:00Z",
        }

        results_file = Path(self.temp_dir) / "test_results.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f)

        with patch("sys.argv", ["metrics_guard.py", "--results-file", str(results_file)]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)
                    mock_print.assert_called()

    def test_validation_with_realistic_metrics(self: Any):
        """Test validation with realistic metrics data."""
        # Create realistic test results file
        test_results = {
            "overall_metrics": {
                "precision": 0.87,
                "recall": 0.82,
                "f1_score": 0.84,
                "accuracy": 0.91,
                "failed_cases": 2,
                "total_cases": 50,
            },
            "baseline_metrics": {
                "precision": 0.80,
                "recall": 0.75,
                "f1_score": 0.77,
                "accuracy": 0.85,
            },
            "case_results": [
                {
                    "case_id": f"test_{i:03d}",
                    "status": "success",
                    "score": 0.8 + (i % 10) * 0.01,
                }
                for i in range(48)
            ]
            + [
                {"case_id": "test_049", "status": "error", "score": 0.0},
                {"case_id": "test_050", "status": "error", "score": 0.0},
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "evaluation_config": {"profile": "gold", "limit": 50, "concurrency": 4},
        }

        results_file = Path(self.temp_dir) / "realistic_results.json"
        with open(results_file, "w") as f:
            json.dump(test_results, f)

        with patch("sys.argv", ["metrics_guard.py", "--results-file", str(results_file)]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)
                    mock_print.assert_called()

    def test_validation_thresholds(self: Any):
        """Test validation with different threshold scenarios."""
        # Test case 1: Metrics just above thresholds
        test_results_1 = {
            "overall_metrics": {
                "precision": 0.751,  # Just above 0.75 threshold
                "recall": 0.701,  # Just above 0.70 threshold
                "f1_score": 0.726,  # Just above 0.72 threshold
                "accuracy": 0.851,  # Just above 0.85 threshold
            },
            "baseline_metrics": {
                "precision": 0.75,
                "recall": 0.70,
                "f1_score": 0.72,
                "accuracy": 0.85,
            },
            "case_results": [{"case_id": "test_001", "status": "success", "score": 0.75}],
            "timestamp": "2024-01-01T12:00:00Z",
        }

        results_file_1 = Path(self.temp_dir) / "threshold_test_1.json"
        with open(results_file_1, "w") as f:
            json.dump(test_results_1, f)

        with patch("sys.argv", ["metrics_guard.py", "--results-file", str(results_file_1)]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)
                    mock_print.assert_called()

    def test_error_handling_robustness(self: Any):
        """Test error handling robustness with various failure scenarios."""
        # Test case 1: Invalid JSON
        invalid_file = Path(self.temp_dir) / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json content")

        with patch("sys.argv", ["metrics_guard.py", "--results-file", str(invalid_file)]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)
                    mock_print.assert_called()

        # Test case 2: File not found
        nonexistent_file = Path(self.temp_dir) / "nonexistent.json"

        with patch("sys.argv", ["metrics_guard.py", "--results-file", str(nonexistent_file)]):
            with patch("scripts.evaluation.metrics_guard.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)
                    mock_print.assert_called()


if __name__ == "__main__":
    _: Any = pytest.main([__file__])
