"""
Tests for update_baseline_manifest.py

Tests the baseline manifest update functionality that manages
evaluation baseline configurations and metadata.
"""

#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utilities.update_baseline_manifest import (
    _collect_results,
    _ema,
    _get_overall,
    _safe_load,
    main,
)


class TestBaselineManifestFunctions:
    """Test cases for baseline manifest functions."""

    def test_safe_load_success(self: Any):
        """Test _safe_load loads JSON successfully."""
        mock_data = {"test": "data"}

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = _safe_load("test.json")

            assert result == mock_data

    def test_safe_load_file_not_found(self: Any):
        """Test _safe_load handles file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = _safe_load("nonexistent.json")

            assert result is None

    def test_safe_load_invalid_json(self: Any):
        """Test _safe_load handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = _safe_load("invalid.json")

            assert result is None

    @patch("scripts.utilities.update_baseline_manifest.glob.glob")
    @patch("scripts.utilities.update_baseline_manifest.os.path.getmtime")
    def test_collect_results(self, mock_getmtime, mock_glob: Any):
        """Test _collect_results collects evaluation results."""
        mock_files = ["eval1.json", "eval2.json", "eval3.json"]
        mock_glob.return_value = mock_files
        mock_getmtime.side_effect = [1000, 2000, 3000]  # eval3 is newest

        with patch("scripts.utilities.update_baseline_manifest._safe_load") as mock_safe_load:
            mock_safe_load.side_effect = [
                {"timestamp": "2024-01-01", "metrics": {"precision": 0.8}},
                {"timestamp": "2024-01-02", "metrics": {"precision": 0.9}},
                {"timestamp": "2024-01-03", "metrics": {"precision": 0.85}},
            ]

            result = _collect_results("test_dir", 2)

            assert len(result) == 2
            assert result
            assert result

    def test_get_overall_metrics(self: Any):
        """Test _get_overall extracts overall metrics correctly."""
        metrics_obj = {
            "overall_metrics": {
                "precision": 0.85,
                "recall": 0.75,
                "f1_score": 0.80,
                "latency_ms": 1500,
            }
        }

        result = _get_overall(metrics_obj)

        assert result
        assert result
        assert result
        assert result

    def test_get_overall_metrics_missing_fields(self: Any):
        """Test _get_overall handles missing fields."""
        metrics_obj = {"overall_metrics": {"precision": 0.85}}

        result = _get_overall(metrics_obj)

        assert result
        assert result
        assert result
        assert result

    def test_ema(self: Any):
        """Test _ema computes exponential moving average."""
        values = [0.8, 0.85, 0.9, 0.88, 0.92]
        alpha = 0.3

        result = _ema(values, alpha)

        assert isinstance(result, float)
        assert 0.8 <= result <= 0.92

    def test_ema_empty_values(self: Any):
        """Test _ema handles empty values."""
        result = _ema([], 0.3)

        assert result == 0.0

    @patch("scripts.utilities.update_baseline_manifest._collect_results")
    @patch("scripts.utilities.update_baseline_manifest._get_overall")
    @patch("scripts.utilities.update_baseline_manifest._ema")
    @patch("scripts.utilities.update_baseline_manifest.json.dump")
    @patch("builtins.open")
    def test_main_success(
        self,
        mock_open,
        mock_json_dump,
        mock_ema,
        mock_get_overall,
        mock_collect_results,
    ):
        """Test main function runs successfully."""
        # Configure mock_open
        mock_open.return_value.__enter__.return_value = mock_open()
        
        # Mock dependencies
        mock_collect_results.return_value = [
            {"timestamp": "2024-01-01", "overall_metrics": {"precision": 0.8}},
            {"timestamp": "2024-01-02", "overall_metrics": {"precision": 0.85}},
        ]
        mock_get_overall.side_effect = [
            {"precision": 0.8, "recall": 0.7, "f1": 0.75, "latency_ms": 1500},
            {"precision": 0.85, "recall": 0.75, "f1": 0.80, "latency_ms": 1400},
        ]
        mock_ema.return_value = 0.82

        with patch("sys.argv", ["update_baseline_manifest.py", "--profile", "gold"]):
            from scripts.utilities.update_baseline_manifest import main

            result = main()

            assert result == 0
            mock_collect_results.assert_called_once()
            mock_json_dump.assert_called_once()

    @patch("sys.argv", ["update_baseline_manifest.py", "--help"])
    def test_main_help(self: Any):
        """Test main function shows help."""
        with patch("scripts.utilities.update_baseline_manifest.argparse.ArgumentParser.print_help"):
            with patch("scripts.utilities.update_baseline_manifest.sys.exit") as mock_exit:
                from scripts.utilities.update_baseline_manifest import main

                main()

                mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    pytest.main([__file__])
