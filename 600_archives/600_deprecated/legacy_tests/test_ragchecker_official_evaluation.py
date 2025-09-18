#!/usr/bin/env python3
"""
Tests for ragchecker_official_evaluation.py

Tests the official RAGChecker evaluation system that runs
comprehensive RAG evaluations using the RAGChecker framework.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRAGCheckerOfficialEvaluation:
    """Test cases for RAGChecker official evaluation system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_data = {
            "queries": [
                {
                    "query_id": "test_001",
                    "query": "What is the main purpose of this system?",
                    "expected_answer": "The system is designed for AI development tasks",
                    "context": "This is a test context for evaluation",
                }
            ],
            "metrics": {"precision": 0.85, "recall": 0.75, "f1_score": 0.80},
        }

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_help_flag(self, mock_config_loader):
        """Test main function shows help when --help flag is used."""
        with patch("sys.argv", ["ragchecker_official_evaluation.py", "--help"]):
            from scripts.evaluation.ragchecker_official_evaluation import main

            # Should not raise exception and should return 0
            result = main()
            assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_h_flag(self, mock_config_loader):
        """Test main function shows help when -h flag is used."""
        with patch("sys.argv", ["ragchecker_official_evaluation.py", "-h"]):
            from scripts.evaluation.ragchecker_official_evaluation import main

            result = main()
            assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_with_profile_gold(self, mock_config_loader):
        """Test main function with gold profile."""
        mock_config = {
            "profile": "gold",
            "use_bedrock": True,
            "bypass_cli": True,
            "stable": True,
        }
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "gold"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_with_profile_mock(self, mock_config_loader):
        """Test main function with mock profile."""
        mock_config = {
            "profile": "mock",
            "use_bedrock": False,
            "bypass_cli": True,
            "stable": True,
        }
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "mock"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_config_resolution_error(self, mock_config_loader):
        """Test main function handles config resolution error."""
        mock_config_loader.resolve_config.side_effect = SystemExit(1)

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "invalid"]
        ):
            from scripts.evaluation.ragchecker_official_evaluation import main

            result = main()
            assert result == 1

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_import_error(self, mock_config_loader):
        """Test main function handles import error."""
        mock_config = {"profile": "gold"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "gold"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_import.side_effect = ImportError("Module not found")

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 1

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_main_evaluation_error(self, mock_config_loader):
        """Test main function handles evaluation error."""
        mock_config = {"profile": "gold"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "gold"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.side_effect = Exception("Evaluation failed")
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 1

    def test_help_output_format(self):
        """Test that help output contains expected information."""
        with patch("sys.argv", ["ragchecker_official_evaluation.py", "--help"]):
            with patch("builtins.print") as mock_print:
                from scripts.evaluation.ragchecker_official_evaluation import main

                main()

                # Check that help information was printed
                mock_print.assert_called()
                calls = [call[0][0] for call in mock_print.call_args_list]
                help_text = " ".join(calls)

                assert "Usage:" in help_text
                assert "Profiles:" in help_text
                assert "gold" in help_text
                assert "mock" in help_text

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_profile_validation(self, mock_config_loader):
        """Test that profile validation works correctly."""
        # Test with valid profile
        mock_config = {"profile": "gold"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "gold"]
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0
                    mock_config_loader.resolve_config.assert_called_once()

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_bedrock_flag_handling(self, mock_config_loader):
        """Test that --use-bedrock flag is handled correctly."""
        mock_config = {"profile": "gold", "use_bedrock": True}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            ["ragchecker_official_evaluation.py", "--profile", "gold", "--use-bedrock"],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_stable_flag_handling(self, mock_config_loader):
        """Test that --stable flag is handled correctly."""
        mock_config = {"profile": "gold", "stable": True}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            ["ragchecker_official_evaluation.py", "--profile", "gold", "--stable"],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_bypass_cli_flag_handling(self, mock_config_loader):
        """Test that --bypass-cli flag is handled correctly."""
        mock_config = {"profile": "gold", "bypass_cli": True}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            ["ragchecker_official_evaluation.py", "--profile", "gold", "--bypass-cli"],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_lessons_mode_flag_handling(self, mock_config_loader):
        """Test that --lessons-mode flag is handled correctly."""
        mock_config = {"profile": "gold", "lessons_mode": "advisory"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            [
                "ragchecker_official_evaluation.py",
                "--profile",
                "gold",
                "--lessons-mode",
                "advisory",
            ],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_lessons_scope_flag_handling(self, mock_config_loader):
        """Test that --lessons-scope flag is handled correctly."""
        mock_config = {"profile": "gold", "lessons_scope": "profile"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            [
                "ragchecker_official_evaluation.py",
                "--profile",
                "gold",
                "--lessons-scope",
                "profile",
            ],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_lessons_window_flag_handling(self, mock_config_loader):
        """Test that --lessons-window flag is handled correctly."""
        mock_config = {"profile": "gold", "lessons_window": 5}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            [
                "ragchecker_official_evaluation.py",
                "--profile",
                "gold",
                "--lessons-window",
                "5",
            ],
        ):
            with patch("scripts.evaluation.ragchecker_official_evaluation.sys.path"):
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0

    def test_observability_initialization(self):
        """Test that observability is initialized correctly."""
        with patch(
            "scripts.evaluation.ragchecker_official_evaluation.get_logfire"
        ) as mock_get_logfire:
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.init_observability"
            ) as mock_init_obs:
                mock_logfire = Mock()
                mock_get_logfire.return_value = mock_logfire

                # Import the module to trigger observability initialization
                from scripts.evaluation.ragchecker_official_evaluation import logfire

                mock_get_logfire.assert_called_once()
                mock_init_obs.assert_called_once_with(service="ai-dev-tasks")

    def test_observability_import_error(self):
        """Test that observability import error is handled gracefully."""
        with patch(
            "scripts.evaluation.ragchecker_official_evaluation.get_logfire",
            side_effect=ImportError,
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.init_observability",
                side_effect=ImportError,
            ):
                # Import should not raise exception
                from scripts.evaluation.ragchecker_official_evaluation import logfire

                assert logfire is None

    def test_observability_init_error(self):
        """Test that observability initialization error is handled gracefully."""
        with patch(
            "scripts.evaluation.ragchecker_official_evaluation.get_logfire"
        ) as mock_get_logfire:
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.init_observability",
                side_effect=Exception,
            ):
                mock_logfire = Mock()
                mock_get_logfire.return_value = mock_logfire

                # Import should not raise exception
                from scripts.evaluation.ragchecker_official_evaluation import logfire

                assert logfire is not None


class TestRAGCheckerEvaluationIntegration:
    """Test cases for RAGChecker evaluation integration."""

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_full_evaluation_workflow(self, mock_config_loader):
        """Test full evaluation workflow with all components."""
        mock_config = {
            "profile": "gold",
            "use_bedrock": True,
            "bypass_cli": True,
            "stable": True,
            "lessons_mode": "advisory",
            "lessons_scope": "profile",
            "lessons_window": 5,
        }
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv",
            [
                "ragchecker_official_evaluation.py",
                "--profile",
                "gold",
                "--use-bedrock",
                "--bypass-cli",
                "--stable",
                "--lessons-mode",
                "advisory",
                "--lessons-scope",
                "profile",
                "--lessons-window",
                "5",
            ],
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    mock_module = Mock()
                    mock_module.main.return_value = 0
                    mock_import.return_value = mock_module

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 0
                    mock_config_loader.resolve_config.assert_called_once()
                    mock_import.assert_called_once()
                    mock_module.main.assert_called_once()

    @patch("scripts.evaluation.ragchecker_official_evaluation.config_loader")
    def test_evaluation_with_error_handling(self, mock_config_loader):
        """Test evaluation with comprehensive error handling."""
        mock_config = {"profile": "gold"}
        mock_config_loader.resolve_config.return_value = mock_config

        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "gold"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.sys.path"
            ) as mock_path:
                with patch(
                    "scripts.evaluation.ragchecker_official_evaluation.importlib.import_module"
                ) as mock_import:
                    # Test various error conditions
                    mock_import.side_effect = ImportError("Module not found")

                    from scripts.evaluation.ragchecker_official_evaluation import main

                    result = main()

                    assert result == 1

    def test_argument_parsing_edge_cases(self):
        """Test argument parsing with edge cases."""
        # Test with no arguments
        with patch("sys.argv", ["ragchecker_official_evaluation.py"]):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.config_loader"
            ) as mock_config_loader:
                mock_config_loader.resolve_config.side_effect = SystemExit(1)

                from scripts.evaluation.ragchecker_official_evaluation import main

                result = main()

                assert result == 1

        # Test with invalid profile
        with patch(
            "sys.argv", ["ragchecker_official_evaluation.py", "--profile", "invalid"]
        ):
            with patch(
                "scripts.evaluation.ragchecker_official_evaluation.config_loader"
            ) as mock_config_loader:
                mock_config_loader.resolve_config.side_effect = SystemExit(1)

                from scripts.evaluation.ragchecker_official_evaluation import main

                result = main()

                assert result == 1


if __name__ == "__main__":
    pytest.main([__file__])
