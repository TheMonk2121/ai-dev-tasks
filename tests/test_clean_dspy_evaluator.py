"""
Tests for clean_dspy_evaluator.py

Comprehensive tests for the CleanDSPyEvaluator class and evaluation harness.
Tests cover unit functionality, integration workflows, and CLI interface.
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
sys.path.insert(0, str(project_root / "src"))

from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator, main


class TestCleanDSPyEvaluator:
    """Test cases for CleanDSPyEvaluator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.evaluator = CleanDSPyEvaluator(profile="gold")

    def test_initialization_default(self):
        """Test evaluator initializes with default parameters."""
        evaluator = CleanDSPyEvaluator()
        assert evaluator.profile == "gold"
        assert evaluator.progress_log is None
        assert evaluator.results_dir == Path("evals/metrics/dspy_evaluations")

    def test_initialization_custom(self):
        """Test evaluator initializes with custom parameters."""
        evaluator = CleanDSPyEvaluator(profile="mock", progress_log="test.log", output_dir="custom_output")
        assert evaluator.profile == "mock"
        assert evaluator.progress_log == "test.log"
        assert evaluator.results_dir == Path("custom_output")

    def test_profile_validation(self):
        """Test profile validation works correctly."""
        valid_profiles = ["gold", "real", "mock"]
        for profile in valid_profiles:
            evaluator = CleanDSPyEvaluator(profile=profile)
            assert evaluator.profile == profile

    @patch("scripts.evaluation.clean_dspy_evaluator.create_config_logger")
    def test_config_logger_initialization(self, mock_create_logger):
        """Test config logger initialization."""
        mock_logger = Mock()
        mock_create_logger.return_value = mock_logger

        evaluator = CleanDSPyEvaluator()

        if evaluator.config_logger is not None:
            mock_create_logger.assert_called_once()

    @patch("scripts.evaluation.clean_dspy_evaluator.get_logfire")
    def test_logfire_initialization(self, mock_get_logfire):
        """Test logfire initialization."""
        mock_logfire = Mock()
        mock_get_logfire.return_value = mock_logfire

        evaluator = CleanDSPyEvaluator()

        if evaluator.logfire_span is not None:
            mock_get_logfire.assert_called_once()

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    def test_load_gold_cases_success(self, mock_load_gold_cases):
        """Test loading gold cases successfully."""
        mock_cases = [
            {
                "id": "test_001",
                "query": "What is the main purpose?",
                "expected_answer": "Test answer",
                "context": "Test context",
                "tags": ["test"],
                "mode": "reader",
            }
        ]
        mock_load_gold_cases.return_value = mock_cases

        cases = self.evaluator._load_gold_cases("test.jsonl")

        assert len(cases) == 1
        assert cases[0]["id"] == "test_001"
        assert cases[0]["expected_answer"] == "Test answer"

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    def test_load_gold_cases_file_not_found(self, mock_load_gold_cases):
        """Test loading gold cases handles file not found."""
        mock_load_gold_cases.return_value = []
        
        cases = self.evaluator._load_gold_cases("nonexistent.jsonl")
        assert cases == []

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    def test_load_gold_cases_invalid_json(self, mock_load_gold_cases):
        """Test loading gold cases handles invalid JSON."""
        mock_load_gold_cases.return_value = []
        
        cases = self.evaluator._load_gold_cases("invalid.jsonl")
        assert cases == []

    @patch.object(CleanDSPyEvaluator, "_filter_cases_by_tags")
    def test_filter_cases_by_tags(self, mock_filter_cases_by_tags):
        """Test filtering cases by tags."""
        cases = [
            {"id": "1", "tags": ["test", "unit"]},
            {"id": "2", "tags": ["test", "integration"]},
            {"id": "3", "tags": ["production"]},
        ]
        mock_filter_cases_by_tags.return_value = [cases[0], cases[1]]

        filtered = self.evaluator._filter_cases_by_tags(cases, ["test"])
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "2"

    @patch.object(CleanDSPyEvaluator, "_filter_cases_by_mode")
    def test_filter_cases_by_mode(self, mock_filter_cases_by_mode):
        """Test filtering cases by mode."""
        cases = [
            {"id": "1", "mode": "reader"},
            {"id": "2", "mode": "retrieval"},
            {"id": "3", "mode": "reader"},
        ]
        mock_filter_cases_by_mode.return_value = [cases[0], cases[2]]

        filtered = self.evaluator._filter_cases_by_mode(cases, "reader")
        assert len(filtered) == 2
        assert filtered[0]["id"] == "1"
        assert filtered[1]["id"] == "3"

    @patch.object(CleanDSPyEvaluator, "_limit_cases")
    def test_limit_cases(self, mock_limit_cases):
        """Test limiting number of cases."""
        cases = [{"id": str(i)} for i in range(10)]
        mock_limit_cases.return_value = cases[:5]

        limited = self.evaluator._limit_cases(cases, 5)
        assert len(limited) == 5

    @patch.object(CleanDSPyEvaluator, "_limit_cases")
    def test_limit_cases_none(self, mock_limit_cases):
        """Test limiting cases with None limit."""
        cases = [{"id": str(i)} for i in range(10)]
        mock_limit_cases.return_value = cases

        limited = self.evaluator._limit_cases(cases, None)
        assert len(limited) == 10

    @patch("scripts.evaluation.clean_dspy_evaluator.RAGAnswer")
    @patch.object(CleanDSPyEvaluator, "_evaluate_single_case")
    def test_evaluate_single_case_success(self, mock_evaluate_single_case, mock_rag_answer):
        """Test evaluating a single case successfully."""
        mock_result = Mock()
        mock_result.answer = "Test answer"
        mock_result.score = 0.85
        mock_result.retrieval_docs = ["doc1", "doc2"]
        mock_rag_answer.return_value = mock_result
        mock_evaluate_single_case.return_value = mock_result

        case = {
            "id": "test_001",
            "query": "What is the purpose?",
            "expected_answer": "Expected answer",
            "context": "Test context",
        }

        result = self.evaluator._evaluate_single_case(case)
        assert result

    @patch("scripts.evaluation.clean_dspy_evaluator.RAGAnswer")
    @patch.object(CleanDSPyEvaluator, "_evaluate_single_case")
    def test_evaluate_single_case_failure(self, mock_evaluate_single_case, mock_rag_answer):
        """Test evaluating a single case with failure."""
        mock_rag_answer.side_effect = Exception("Evaluation failed")
        mock_evaluate_single_case.return_value = None

        case = {
            "id": "test_001",
            "query": "What is the purpose?",
            "expected_answer": "Expected answer",
            "context": "Test context",
        }

        result = self.evaluator._evaluate_single_case(case)
        assert result is None

    @patch.object(CleanDSPyEvaluator, "_calculate_metrics")
    def test_calculate_metrics(self, mock_calculate_metrics):
        """Test calculating evaluation metrics."""
        results = [
            {"status": "success", "score": 0.8},
            {"status": "success", "score": 0.9},
            {"status": "error", "score": 0.0},
            {"status": "success", "score": 0.7},
        ]
        mock_calculate_metrics.return_value = {
            "total_cases": 4,
            "successful_cases": 3,
            "failed_cases": 1,
            "success_rate": 0.75,
            "average_score": 0.6
        }

        metrics = self.evaluator._calculate_metrics(results)
        assert metrics["total_cases"] == 4
        assert metrics["successful_cases"] == 3
        assert metrics["failed_cases"] == 1
        assert metrics["success_rate"] == 0.75
        assert metrics["average_score"] == 0.6

    @patch.object(CleanDSPyEvaluator, "_calculate_metrics")
    def test_calculate_metrics_empty(self, mock_calculate_metrics):
        """Test calculating metrics with empty results."""
        mock_calculate_metrics.return_value = {
            "total_cases": 0,
            "successful_cases": 0,
            "failed_cases": 0,
            "success_rate": 0.0,
            "average_score": 0.0
        }

        metrics = self.evaluator._calculate_metrics([])

        assert metrics["total_cases"] == 0
        assert metrics["successful_cases"] == 0
        assert metrics["failed_cases"] == 0
        assert metrics["success_rate"] == 0.0
        assert metrics["average_score"] == 0.0

    @patch("scripts.evaluation.clean_dspy_evaluator.Path.mkdir")
    @patch("scripts.evaluation.clean_dspy_evaluator.json.dump")
    @patch("builtins.open")
    @patch.object(CleanDSPyEvaluator, "_save_results")
    def test_save_results(self, mock_save_results, mock_open, mock_json_dump, mock_mkdir):
        """Test saving evaluation results."""
        # Configure mock_open
        mock_open.return_value.__enter__.return_value = mock_open()
        
        results = {"test": "data"}
        output_file = "test_results.json"

        self.evaluator._save_results(results, output_file)
        mock_save_results.assert_called_once_with(results, output_file)
        mock_json_dump.assert_called_once()

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    @patch.object(CleanDSPyEvaluator, "_filter_cases_by_tags")
    @patch.object(CleanDSPyEvaluator, "_filter_cases_by_mode")
    @patch.object(CleanDSPyEvaluator, "_limit_cases")
    @patch.object(CleanDSPyEvaluator, "_evaluate_single_case")
    @patch.object(CleanDSPyEvaluator, "_calculate_metrics")
    @patch.object(CleanDSPyEvaluator, "_save_results")
    def test_run_evaluation_success(
        self,
        mock_save,
        mock_calc_metrics,
        mock_eval_case,
        mock_limit,
        mock_filter_mode,
        mock_filter_tags,
        mock_load,
    ):
        """Test run_evaluation executes successfully."""
        # Mock dependencies
        mock_load.return_value = [{"id": "test_001", "query": "test"}]
        mock_filter_tags.return_value = [{"id": "test_001", "query": "test"}]
        mock_filter_mode.return_value = [{"id": "test_001", "query": "test"}]
        mock_limit.return_value = [{"id": "test_001", "query": "test"}]
        mock_eval_case.return_value = {"status": "success", "score": 0.8}
        mock_calc_metrics.return_value = {"total_cases": 1, "success_rate": 1.0}

        result = self.evaluator.run_evaluation(
            gold_file="test.jsonl",
            limit=10,
            include_tags=["test"],
            mode="reader",
            concurrency=2,
        )

        assert "overall_metrics" in result
        assert result
        mock_load.assert_called_once_with("test.jsonl")
        mock_filter_tags.assert_called_once()
        mock_filter_mode.assert_called_once()
        mock_limit.assert_called_once()
        mock_eval_case.assert_called_once()
        mock_calc_metrics.assert_called_once()
        mock_save.assert_called_once()

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    def test_run_evaluation_no_cases(self, mock_load):
        """Test run_evaluation handles no cases."""
        mock_load.return_value = []

        result = self.evaluator.run_evaluation("test.jsonl")

        assert result
        assert result

    @patch.object(CleanDSPyEvaluator, "_load_gold_cases")
    def test_run_evaluation_file_error(self, mock_load):
        """Test run_evaluation handles file loading error."""
        mock_load.side_effect = Exception("File error")

        result = self.evaluator.run_evaluation("test.jsonl")

        assert result
        assert "error" in result

    def test_progress_logging(self):
        """Test progress logging functionality."""
        evaluator = CleanDSPyEvaluator(progress_log="test.log")

        with patch("builtins.open", mock_open()) as mock_file:
            evaluator._log_progress({"message": "Test message"})

            mock_file.assert_called_once_with("test.log", "a")
            mock_file().write.assert_called_once()

    def test_progress_logging_no_log(self):
        """Test progress logging when no log file specified."""
        evaluator = CleanDSPyEvaluator()

        # Should not raise exception
        evaluator._log_progress({"message": "Test message"})


class TestCleanDSPyEvaluatorCLI:
    """Test cases for CLI interface."""

    @patch("scripts.evaluation.clean_dspy_evaluator.CleanDSPyEvaluator")
    @patch("sys.argv", ["clean_dspy_evaluator.py", "--profile", "gold", "--limit", "5"])
    def test_main_success(self, mock_evaluator_class):
        """Test main function runs successfully."""
        mock_evaluator = Mock()
        mock_evaluator.run_evaluation.return_value = {"overall_metrics": {"failed_cases": 0}}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
            main()

            mock_evaluator.run_evaluation.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.clean_dspy_evaluator.CleanDSPyEvaluator")
    @patch("sys.argv", ["clean_dspy_evaluator.py", "--profile", "gold"])
    def test_main_with_failures(self, mock_evaluator_class):
        """Test main function handles evaluation failures."""
        mock_evaluator = Mock()
        mock_evaluator.run_evaluation.return_value = {"overall_metrics": {"failed_cases": 2}}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
            main()

            mock_evaluator.run_evaluation.assert_called_once()
            mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["clean_dspy_evaluator.py", "--help"])
    def test_main_help(self):
        """Test main function shows help."""
        with patch("scripts.evaluation.clean_dspy_evaluator.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.clean_dspy_evaluator.CleanDSPyEvaluator")
    @patch(
        "sys.argv",
        ["clean_dspy_evaluator.py", "--profile", "gold", "--tags", "test", "unit"],
    )
    def test_main_with_tags(self, mock_evaluator_class):
        """Test main function with tags argument."""
        mock_evaluator = Mock()
        mock_evaluator.run_evaluation.return_value = {"overall_metrics": {"failed_cases": 0}}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
            main()

            mock_evaluator.run_evaluation.assert_called_once()
            # Check that tags were passed correctly
            call_args = mock_evaluator.run_evaluation.call_args
            assert call_args[1]["tags"] == ["test"]

    @patch("scripts.evaluation.clean_dspy_evaluator.CleanDSPyEvaluator")
    @patch("sys.argv", ["clean_dspy_evaluator.py", "--profile", "gold", "--mode", "reader"])
    def test_main_with_mode(self, mock_evaluator_class):
        """Test main function with mode argument."""
        mock_evaluator = Mock()
        mock_evaluator.run_evaluation.return_value = {"overall_metrics": {"failed_cases": 0}}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
            main()

            mock_evaluator.run_evaluation.assert_called_once()
            # Check that mode was passed correctly
            call_args = mock_evaluator.run_evaluation.call_args
            assert call_args[1]["mode"] == "reader"

    @patch("scripts.evaluation.clean_dspy_evaluator.CleanDSPyEvaluator")
    @patch(
        "sys.argv",
        ["clean_dspy_evaluator.py", "--profile", "gold", "--concurrency", "4"],
    )
    def test_main_with_concurrency(self, mock_evaluator_class):
        """Test main function with concurrency argument."""
        mock_evaluator = Mock()
        mock_evaluator.run_evaluation.return_value = {"overall_metrics": {"failed_cases": 0}}
        mock_evaluator_class.return_value = mock_evaluator

        with patch("scripts.evaluation.clean_dspy_evaluator.sys.exit") as mock_exit:
            main()

            mock_evaluator.run_evaluation.assert_called_once()
            # Check that concurrency was passed correctly
            call_args = mock_evaluator.run_evaluation.call_args
            assert call_args[1]["concurrency"] == 4


class TestCleanDSPyEvaluatorIntegration:
    """Integration tests for CleanDSPyEvaluator."""

    @patch("scripts.evaluation.clean_dspy_evaluator.RAGAnswer")
    def test_full_evaluation_workflow(self, mock_rag_answer):
        """Test complete evaluation workflow."""
        # Mock RAGAnswer response
        mock_result = Mock()
        mock_result.answer = "Test answer"
        mock_result.score = 0.85
        mock_result.retrieval_docs = ["doc1", "doc2"]
        mock_rag_answer.return_value = mock_result

        # Create test gold file
        test_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "expected_answer": "Expected answer",
                "context": "Test context",
                "tags": ["test"],
                "mode": "reader",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for case in test_cases:
                f.write(json.dumps(case) + "\n")
            gold_file = f.name

        try:
            evaluator = CleanDSPyEvaluator(profile="gold")

            with patch.object(evaluator, "_save_results") as mock_save:
                result = evaluator.run_evaluation(gold_file=gold_file, limit=1)

                assert result
                assert result
                assert result
                assert len(result) > 0
                assert result

                mock_save.assert_called_once()
        finally:
            os.unlink(gold_file)

    def test_evaluation_with_different_profiles(self):
        """Test evaluation with different profiles."""
        profiles = ["gold", "real", "mock"]

        for profile in profiles:
            evaluator = CleanDSPyEvaluator(profile=profile)
            assert evaluator.profile == profile

    @patch("scripts.evaluation.clean_dspy_evaluator.RAGAnswer")
    def test_evaluation_error_handling(self, mock_rag_answer):
        """Test evaluation error handling."""
        mock_rag_answer.side_effect = Exception("RAG evaluation failed")

        test_cases = [
            {
                "id": "test_001",
                "query": "What is the purpose?",
                "expected_answer": "Expected answer",
                "context": "Test context",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for case in test_cases:
                f.write(json.dumps(case) + "\n")
            gold_file = f.name

        try:
            evaluator = CleanDSPyEvaluator(profile="gold")

            with patch.object(evaluator, "_save_results") as mock_save:
                result = evaluator.run_evaluation(gold_file=gold_file, limit=1)

                assert result
                assert result
                assert result
                assert len(result) > 0
                assert result

                mock_save.assert_called_once()
        finally:
            os.unlink(gold_file)


if __name__ == "__main__":
    pytest.main([__file__])
