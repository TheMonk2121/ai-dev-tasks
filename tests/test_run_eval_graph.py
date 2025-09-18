"""
Tests for run_eval_graph.py

Comprehensive tests for the graph-based evaluation runner.
Tests cover graph execution, state persistence, and CLI interface.
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

from scripts.evaluation.run_eval_graph import main


class TestRunEvalGraph:
    """Test cases for run_eval_graph.py main function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_success(self, mock_persistence_class, mock_build_graph):
        """Test main function runs successfully."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_node2 = Mock()
        mock_node3 = Mock()

        # Mock node 1 (load cases)
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, mock_node2, mock_node3]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"test": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        # Mock node 2 (retrieve)
        mock_candidates = [{"doc": "test_doc", "score": 0.8}]
        mock_node2.run.return_value = mock_candidates

        # Mock node 3 (score)
        mock_result = Mock()
        mock_result.model_dump_json.return_value = json.dumps({"score": 0.85, "status": "success"})
        mock_node3.run.return_value = mock_result

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify graph was built
                    mock_build_graph.assert_called_once()

                    # Verify persistence was created
                    mock_persistence_class.assert_called_once_with("test_run")

                    # Verify nodes were called
                    mock_node1.run.assert_called_once_with("test.jsonl")
                    mock_node2.run.assert_called_once_with("What is the purpose?")
                    mock_node3.run.assert_called_once()

                    # Verify snapshots were created
                    assert mock_persistence.snapshot_node.call_count == 2
                    assert mock_persistence.snapshot_end.call_count == 1

                    # Verify output was written
                    mock_print.assert_called()

                    # Should not exit with error
                    mock_exit.assert_not_called()

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_no_cases_loaded(self, mock_persistence_class, mock_build_graph):
        """Test main function handles no cases loaded."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_node1.run.return_value = []  # No cases loaded
        mock_graph.nodes = [mock_node1]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence_class.return_value = mock_persistence

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("scripts.evaluation.run_eval_graph.SystemExit") as mock_system_exit:
                    main()

                    # Should exit with error due to no cases
                    mock_system_exit.assert_called_once_with("No cases loaded")

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_default_arguments(self, mock_persistence_class, mock_build_graph):
        """Test main function with default arguments."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, Mock(), Mock()]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"test": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        with patch("sys.argv", ["run_eval_graph.py"]):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch(
                    "scripts.evaluation.run_eval_graph.time.time",
                    return_value=1234567890,
                ):
                    with patch("builtins.print") as mock_print:
                        main()

                        # Verify default run_id was generated
                        mock_persistence_class.assert_called_once_with("run_1234567890")

                        # Verify default gold file was used
                        mock_node1.run.assert_called_once_with("evals/gold/v1/gold_cases.jsonl")

                        # Verify default output directory was used
                        mock_print.assert_called()
                        print_calls = [result.get("key", "")
                        assert any("metrics/graph_runs" in call for call in print_calls)

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_custom_arguments(self, mock_persistence_class, mock_build_graph):
        """Test main function with custom arguments."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, Mock(), Mock()]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"test": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        custom_run_id = "custom_run_123"
        custom_gold_file = "custom_gold.jsonl"
        custom_output = "custom_output_dir"

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                custom_run_id,
                "--gold-file",
                custom_gold_file,
                "--out",
                custom_output,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify custom arguments were used
                    mock_persistence_class.assert_called_once_with(custom_run_id)
                    mock_node1.run.assert_called_once_with(custom_gold_file)

                    # Verify custom output directory was used
                    print_calls = [result.get("key", "")
                    assert any(custom_output in call for call in print_calls)

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_graph_execution_flow(self, mock_persistence_class, mock_build_graph):
        """Test main function executes graph nodes in correct order."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_node2 = Mock()
        mock_node3 = Mock()

        # Mock node 1 (load cases)
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, mock_node2, mock_node3]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"test": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        # Mock node 2 (retrieve)
        mock_candidates = [{"doc": "test_doc", "score": 0.8}]
        mock_node2.run.return_value = mock_candidates

        # Mock node 3 (score)
        mock_result = Mock()
        mock_result.model_dump_json.return_value = json.dumps({"score": 0.85, "status": "success"})
        mock_node3.run.return_value = mock_result

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify execution order
                    mock_node1.run.assert_called_once_with("test.jsonl")
                    mock_node2.run.assert_called_once_with("What is the purpose?")
                    mock_node3.run.assert_called_once()

                    # Verify snapshot calls
                    snapshot_calls = mock_persistence.snapshot_node.call_args_list
                    assert len(snapshot_calls) == 2

                    # First snapshot should be for retrieve stage
                    first_call = result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")

                    # Second snapshot should be for score stage
                    second_call = result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")
                    assert result.get("key", "")

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_output_file_creation(self, mock_persistence_class, mock_build_graph):
        """Test main function creates output file correctly."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, Mock(), Mock()]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"snapshot": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        # Mock node 3 (score)
        mock_result = Mock()
        mock_result.model_dump_json.return_value = json.dumps({"score": 0.85, "status": "success"})
        mock_graph.result.get("key", "")

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("json.dumps") as mock_json_dumps:
                            mock_json_dumps.return_value = '{"test": "output"}'

                            main()

                            # Verify output file was created
                            mock_file.assert_called_once()
                            file_path = mock_file.result.get("key", "")
                            assert str(file_path).endswith("test_run.json")

                            # Verify JSON was written
                            mock_json_dumps.assert_called_once()
                            json_data = mock_json_dumps.result.get("key", "")
                            assert result.get("key", "")
                            assert "snapshots" in json_data
                            assert "result" in json_data

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_node_execution_error(self, mock_persistence_class, mock_build_graph):
        """Test main function handles node execution error."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, Mock(), Mock()]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        # Mock node 2 to raise exception
        mock_graph.result.get("key", "")

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("scripts.evaluation.run_eval_graph.SystemExit") as mock_system_exit:
                    main()

                    # Should exit with error due to node execution failure
                    mock_system_exit.assert_called_once()

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_main_persistence_error(self, mock_persistence_class, mock_build_graph):
        """Test main function handles persistence error."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            }
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, Mock(), Mock()]

        mock_build_graph.return_value = mock_graph

        # Mock persistence to raise exception
        mock_persistence_class.side_effect = Exception("Persistence error")

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "test_run",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("scripts.evaluation.run_eval_graph.SystemExit") as mock_system_exit:
                    main()

                    # Should exit with error due to persistence error
                    mock_system_exit.assert_called_once()

    @patch("sys.argv", ["run_eval_graph.py", "--help"])
    def test_main_help(self):
        """Test main function shows help."""
        with patch("scripts.evaluation.run_eval_graph.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)


class TestRunEvalGraphIntegration:
    """Integration tests for run_eval_graph.py."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    @patch("scripts.evaluation.run_eval_graph.build_graph")
    @patch("scripts.evaluation.run_eval_graph.PgStatePersistence")
    def test_full_workflow_integration(self, mock_persistence_class, mock_build_graph):
        """Test full workflow integration."""
        # Mock graph
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_node2 = Mock()
        mock_node3 = Mock()

        # Mock node 1 (load cases)
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "mode": "reader",
                "tags": ["test"],
            },
            {
                "id": "test_002",
                "query": "How does it work?",
                "mode": "retrieval",
                "tags": ["test"],
            },
        ]
        mock_node1.run.return_value = mock_cases
        mock_graph.nodes = [mock_node1, mock_node2, mock_node3]

        mock_build_graph.return_value = mock_graph

        # Mock persistence
        mock_persistence = Mock()
        mock_persistence.snapshot_node.return_value = "snapshot_id_1"
        mock_persistence.snapshot_end.return_value = None
        mock_persistence.load_all.return_value = [{"snapshot": "data"}]
        mock_persistence_class.return_value = mock_persistence

        # Mock context manager for record_run
        mock_persistence.record_run.return_value.__enter__ = Mock()
        mock_persistence.record_run.return_value.__exit__ = Mock()

        # Mock node 2 (retrieve)
        mock_candidates = [{"doc": "test_doc", "score": 0.8}]
        mock_node2.run.return_value = mock_candidates

        # Mock node 3 (score)
        mock_result = Mock()
        mock_result.model_dump_json.return_value = json.dumps({"score": 0.85, "status": "success"})
        mock_node3.run.return_value = mock_result

        with patch(
            "sys.argv",
            [
                "run_eval_graph.py",
                "--run-id",
                "integration_test",
                "--gold-file",
                "test.jsonl",
                "--out",
                self.temp_dir,
            ],
        ):
            with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("json.dumps") as mock_json_dumps:
                            mock_json_dumps.return_value = '{"test": "output"}'

                            main()

                            # Verify all components were called
                            mock_build_graph.assert_called_once()
                            mock_persistence_class.assert_called_once_with("integration_test")

                            # Verify nodes were executed
                            mock_node1.run.assert_called_once_with("test.jsonl")
                            mock_node2.run.assert_called_once_with("What is the purpose?")
                            mock_node3.run.assert_called_once()

                            # Verify output was created
                            mock_file.assert_called_once()
                            mock_json_dumps.assert_called_once()

                            # Should complete successfully
                            mock_exit.assert_not_called()

    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        output_dir = Path(self.temp_dir) / "new_output_dir"

        with patch("scripts.evaluation.run_eval_graph.build_graph") as mock_build_graph:
            with patch("scripts.evaluation.run_eval_graph.PgStatePersistence") as mock_persistence_class:
                # Mock graph
                mock_graph = Mock()
                mock_node1 = Mock()
                mock_cases = [
                    {
                        "id": "test_001",
                        "query": "What is the purpose?",
                        "mode": "reader",
                        "tags": ["test"],
                    }
                ]
                mock_node1.run.return_value = mock_cases
                mock_graph.nodes = [mock_node1, Mock(), Mock()]
                mock_build_graph.return_value = mock_graph

                # Mock persistence
                mock_persistence = Mock()
                mock_persistence.snapshot_node.return_value = "snapshot_id_1"
                mock_persistence.snapshot_end.return_value = None
                mock_persistence.load_all.return_value = [{"snapshot": "data"}]
                mock_persistence_class.return_value = mock_persistence

                # Mock context manager for record_run
                mock_persistence.record_run.return_value.__enter__ = Mock()
                mock_persistence.record_run.return_value.__exit__ = Mock()

                # Mock node 3 (score)
                mock_result = Mock()
                mock_result.model_dump_json.return_value = json.dumps({"score": 0.85, "status": "success"})
                mock_graph.result.get("key", "")

                with patch(
                    "sys.argv",
                    [
                        "run_eval_graph.py",
                        "--run-id",
                        "test_run",
                        "--gold-file",
                        "test.jsonl",
                        "--out",
                        str(output_dir),
                    ],
                ):
                    with patch("scripts.evaluation.run_eval_graph.sys.exit") as mock_exit:
                        with patch("builtins.print") as mock_print:
                            with patch("builtins.open", mock_open()) as mock_file:
                                with patch("json.dumps") as mock_json_dumps:
                                    mock_json_dumps.return_value = '{"test": "output"}'

                                    main()

                                    # Verify output directory was created
                                    assert output_dir.exists()

                                    # Verify output file was created in the directory
                                    mock_file.assert_called_once()
                                    file_path = mock_file.result.get("key", "")
                                    assert str(file_path).startswith(str(output_dir))


if __name__ == "__main__":
    pytest.main([__file__])
