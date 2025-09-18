"""
Tests for run_eval.py

Comprehensive tests for the evaluation runner script.
Tests cover file handling, subprocess execution, and artifact management.
"""

#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "300_evals"))

from scripts.evaluation.run_eval import _latest_eval_file, main


class TestLatestEvalFile:
    """Test cases for _latest_eval_file function."""

    def test_latest_eval_file_success(self):
        """Test finding latest evaluation file successfully."""
        with patch("scripts.evaluation.run_eval.glob.glob") as mock_glob:
            mock_files = [
                "metrics/baseline_evaluations/eval_20240101_120000.json",
                "metrics/baseline_evaluations/eval_20240102_130000.json",
                "metrics/baseline_evaluations/eval_20240103_140000.json",
            ]
            mock_glob.return_value = mock_files

            with patch("scripts.evaluation.run_eval.os.path.getctime") as mock_getctime:
                mock_getctime.side_effect = [1000, 2000, 3000]  # Last file is newest

                result = _latest_eval_file("metrics/baseline_evaluations/eval_*.json")

                assert result == "metrics/baseline_evaluations/eval_20240103_140000.json"

    def test_latest_eval_file_no_files(self):
        """Test handling when no files found."""
        with patch("scripts.evaluation.run_eval.glob.glob") as mock_glob:
            mock_glob.return_value = []

            result = _latest_eval_file("nonexistent_pattern")

            assert result is None

    def test_latest_eval_file_single_file(self):
        """Test handling when only one file found."""
        with patch("scripts.evaluation.run_eval.glob.glob") as mock_glob:
            mock_files = ["metrics/baseline_evaluations/eval_20240101_120000.json"]
            mock_glob.return_value = mock_files

            with patch("scripts.evaluation.run_eval.os.path.getctime") as mock_getctime:
                mock_getctime.return_value = 1000

                result = _latest_eval_file("metrics/baseline_evaluations/eval_*.json")

                assert result == "metrics/baseline_evaluations/eval_20240101_120000.json"


class TestRunEvalMain:
    """Test cases for main function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    @patch("scripts.evaluation.run_eval.shutil.copy2")
    @patch("scripts.evaluation.run_eval.json.dump")
    @patch("builtins.open", mock_open())
    def test_main_success(
        self,
        mock_file,
        mock_json_dump,
        mock_copy,
        mock_mkdir,
        mock_latest_file,
        mock_subprocess,
    ):
        """Test main function runs successfully."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed successfully"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        with patch(
            "sys.argv",
            ["run_eval.py", "--output-root", self.temp_dir, "--tag", "TEST-001"],
        ):
            result = main()

            assert result == 0
            mock_subprocess.assert_called_once()
            mock_mkdir.assert_called()
            mock_latest_file.assert_called_once()
            mock_copy.assert_called_once()
            mock_json_dump.assert_called_once()

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_subprocess_failure(self, mock_mkdir, mock_subprocess):
        """Test main function handles subprocess failure."""
        # Mock subprocess failure
        mock_proc = Mock()
        mock_proc.returncode = 1
        mock_proc.stdout = "Evaluation failed"
        mock_proc.stderr = "Error message"
        mock_subprocess.return_value = mock_proc

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            with patch("builtins.print") as mock_print:
                result = main()

                assert result == 1
                mock_subprocess.assert_called_once()
                mock_print.assert_called()

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_no_eval_file_found(self, mock_mkdir, mock_latest_file, mock_subprocess):
        """Test main function when no evaluation file is found."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock no file found
        mock_latest_file.return_value = None

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            result = main()

            assert result == 0
            mock_subprocess.assert_called_once()
            mock_latest_file.assert_called_once()

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    @patch("scripts.evaluation.run_eval.shutil.copy2")
    @patch("scripts.evaluation.run_eval.json.dump")
    @patch("builtins.open", mock_open())
    def test_main_with_manifest_creation(
        self,
        mock_file,
        mock_json_dump,
        mock_copy,
        mock_mkdir,
        mock_latest_file,
        mock_subprocess,
    ):
        """Test main function creates manifest correctly."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        with patch(
            "sys.argv",
            ["run_eval.py", "--output-root", self.temp_dir, "--tag", "TEST-001"],
        ):
            with patch.dict(
                os.environ,
                {
                    "EVAL_MODE": "bedrock_only",
                    "CACHE_DISABLED": "1",
                    "AWS_REGION": "us-east-1",
                },
            ):
                result = main()

                assert result == 0
                mock_json_dump.assert_called_once()

                # Check manifest content
                call_args = mock_json_dump.call_args
                manifest_data = result.get("key", "")
                assert result.get("key", "")
                assert result.get("key", "")
                assert result.get("key", "")
                assert result.get("key", "")
                assert result.get("key", "")

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_subprocess_command_correct(self, mock_mkdir, mock_subprocess):
        """Test main function calls subprocess with correct command."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            main()

            # Check subprocess was called with correct command
            call_args = mock_subprocess.call_args
            command = result.get("key", "")
            assert command == [
                "python3",
                "scripts/ragchecker_official_evaluation.py",
                "--use-bedrock",
            ]
            assert result.get("key", "")
            assert result.get("key", "")

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_environment_variables_set(self, mock_mkdir, mock_subprocess):
        """Test main function sets environment variables correctly."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            with patch.dict(os.environ, {}, clear=True):
                main()

                # Check environment variables were set
                assert os.result.get("key", "")
                assert os.result.get("key", "")

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    @patch("scripts.evaluation.run_eval.shutil.copy2")
    def test_main_file_copy_success(self, mock_copy, mock_mkdir, mock_latest_file, mock_subprocess):
        """Test main function copies evaluation file successfully."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        with patch(
            "sys.argv",
            ["run_eval.py", "--output-root", self.temp_dir, "--tag", "TEST-001"],
        ):
            main()

            # Check file was copied
            mock_copy.assert_called_once()
            copy_args = mock_copy.call_args
            assert result.get("key", "")
            assert "TEST-001" in str(result.get("key", "")

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_default_arguments(self, mock_mkdir, mock_subprocess):
        """Test main function with default arguments."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        with patch("sys.argv", ["run_eval.py"]):
            main()

            # Check default values were used
            mock_mkdir.assert_called()
            # Should create directory with default output root and tag
            mkdir_calls = mock_mkdir.call_args_list
            assert any("metrics/baseline_evaluations" in str(call) for call in mkdir_calls)

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_custom_arguments(self, mock_mkdir, mock_subprocess):
        """Test main function with custom arguments."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        custom_output = "/custom/output"
        custom_tag = "CUSTOM-TAG"

        with patch(
            "sys.argv",
            ["run_eval.py", "--output-root", custom_output, "--tag", custom_tag],
        ):
            main()

            # Check custom values were used
            mock_mkdir.assert_called()
            mkdir_calls = mock_mkdir.call_args_list
            assert any(custom_output in str(call) for call in mkdir_calls)
            assert any(custom_tag in str(call) for call in mkdir_calls)

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    def test_main_subprocess_exception(self, mock_mkdir, mock_subprocess):
        """Test main function handles subprocess exception."""
        # Mock subprocess exception
        mock_subprocess.side_effect = subprocess.SubprocessError("Subprocess failed")

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            with patch("builtins.print") as mock_print:
                result = main()

                assert result == 1
                mock_print.assert_called()

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    @patch("scripts.evaluation.run_eval.shutil.copy2")
    def test_main_copy_exception(self, mock_copy, mock_mkdir, mock_latest_file, mock_subprocess):
        """Test main function handles file copy exception."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        # Mock copy exception
        mock_copy.side_effect = shutil.Error("Copy failed")

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            with patch("builtins.print") as mock_print:
                result = main()

                assert result == 0  # Should still succeed even if copy fails
                mock_copy.assert_called_once()

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    @patch("scripts.evaluation.run_eval.Path.mkdir")
    @patch("scripts.evaluation.run_eval.shutil.copy2")
    @patch("scripts.evaluation.run_eval.json.dump")
    @patch("builtins.open", mock_open())
    def test_main_manifest_creation_exception(
        self,
        mock_file,
        mock_json_dump,
        mock_copy,
        mock_mkdir,
        mock_latest_file,
        mock_subprocess,
    ):
        """Test main function handles manifest creation exception."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        # Mock JSON dump exception
        mock_json_dump.side_effect = json.JSONEncodeError("JSON error", "", 0)

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            with patch("builtins.print") as mock_print:
                result = main()

                assert result == 0  # Should still succeed even if manifest creation fails
                mock_json_dump.assert_called_once()


class TestRunEvalIntegration:
    """Integration tests for run_eval.py."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch("scripts.evaluation.run_eval.subprocess.run")
    @patch("scripts.evaluation.run_eval._latest_eval_file")
    def test_full_workflow_integration(self, mock_latest_file, mock_subprocess):
        """Test full workflow integration."""
        # Mock subprocess success
        mock_proc = Mock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Evaluation completed successfully"
        mock_proc.stderr = ""
        mock_subprocess.return_value = mock_proc

        # Mock latest file found
        mock_latest_file.return_value = "metrics/baseline_evaluations/eval_20240101_120000.json"

        with patch(
            "sys.argv",
            [
                "run_eval.py",
                "--output-root",
                self.temp_dir,
                "--tag",
                "INTEGRATION-TEST",
            ],
        ):
            with patch.dict(os.environ, {"EVAL_MODE": "bedrock_only", "CACHE_DISABLED": "1"}):
                result = main()

                assert result == 0
                mock_subprocess.assert_called_once()
                mock_latest_file.assert_called_once()

                # Check that output directory was created
                output_path = Path(self.temp_dir) / "INTEGRATION-TEST"
                assert output_path.exists()

    def test_environment_variable_persistence(self):
        """Test that environment variables persist after function execution."""
        original_env = os.environ.copy()

        try:
            with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
                with patch("scripts.evaluation.run_eval.subprocess.run") as mock_subprocess:
                    mock_proc = Mock()
                    mock_proc.returncode = 0
                    mock_proc.stdout = "Evaluation completed"
                    mock_proc.stderr = ""
                    mock_subprocess.return_value = mock_proc

                    main()

                    # Check environment variables are still set
                    assert os.result.get("key", "")
                    assert os.result.get("key", "")
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)

    @patch("scripts.evaluation.run_eval.subprocess.run")
    def test_error_handling_robustness(self, mock_subprocess):
        """Test error handling robustness with various failure scenarios."""
        # Test subprocess failure
        mock_proc = Mock()
        mock_proc.returncode = 1
        mock_proc.stdout = "Evaluation failed"
        mock_proc.stderr = "Error details"
        mock_subprocess.return_value = mock_proc

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            result = main()
            assert result == 1

        # Test subprocess exception
        mock_subprocess.side_effect = subprocess.SubprocessError("Subprocess error")

        with patch("sys.argv", ["run_eval.py", "--output-root", self.temp_dir]):
            result = main()
            assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])
