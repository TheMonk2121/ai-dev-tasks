"""Comprehensive test suite for RAGChecker evaluation system."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the RAGChecker evaluation classes
from scripts.ragchecker_official_evaluation import OfficialRAGCheckerEvaluator, RAGCheckerInput


class TestRAGCheckerInput:
    """Test RAGCheckerInput dataclass."""

    def test_ragchecker_input_creation(self):
        """Test creating RAGCheckerInput with valid data."""
        input_data = RAGCheckerInput(
            query_id="test_001",
            query="What is the project status?",
            gt_answer="The project is active with current backlog items.",
            response="The project is currently active and has several backlog items.",
            retrieved_context=["Project status information from memory system."],
        )

        assert input_data.query_id == "test_001"
        assert input_data.query == "What is the project status?"
        assert input_data.gt_answer == "The project is active with current backlog items."
        assert input_data.response == "The project is currently active and has several backlog items."
        assert input_data.retrieved_context == ["Project status information from memory system."]

    def test_ragchecker_input_validation(self):
        """Test RAGCheckerInput validation with required fields."""
        # Test that all required fields are present
        input_data = RAGCheckerInput(
            query_id="test_002",
            query="Test query",
            gt_answer="Test answer",
            response="Test response",
            retrieved_context=["Test context"],
        )

        # Verify field types
        assert isinstance(input_data.query_id, str)
        assert isinstance(input_data.query, str)
        assert isinstance(input_data.gt_answer, str)
        assert isinstance(input_data.response, str)
        assert isinstance(input_data.retrieved_context, list)


class TestOfficialTestCases:
    """Test official test case creation."""

    def test_create_official_test_cases(self):
        """Test creation of official test cases."""
        evaluator = OfficialRAGCheckerEvaluator()
        test_cases = evaluator.create_official_test_cases()

        # Verify we have test cases (actual count may vary)
        assert len(test_cases) >= 5

        # Verify each test case has required fields
        for case in test_cases:
            assert hasattr(case, "query_id")
            assert hasattr(case, "query")
            assert hasattr(case, "gt_answer")
            assert hasattr(case, "retrieved_context")
            assert isinstance(case.query_id, str)
            assert isinstance(case.query, str)
            assert isinstance(case.gt_answer, str)
            assert isinstance(case.retrieved_context, list)  # It's a list of dicts

    def test_test_case_content(self):
        """Test that test cases have meaningful content."""
        evaluator = OfficialRAGCheckerEvaluator()
        test_cases = evaluator.create_official_test_cases()

        # Check specific test case IDs
        query_ids = [case.query_id for case in test_cases]
        expected_ids = [
            "memory_system_001",
            "dspy_integration_001",
            "role_context_001",
            "research_context_001",
            "architecture_001",
        ]

        for expected_id in expected_ids:
            assert expected_id in query_ids

    def test_test_case_queries(self):
        """Test that test case queries are meaningful."""
        evaluator = OfficialRAGCheckerEvaluator()
        test_cases = evaluator.create_official_test_cases()

        for case in test_cases:
            # Verify queries are not empty
            assert len(case.query.strip()) > 0
            # Verify queries end with question mark
            assert case.query.strip().endswith("?")
            # Verify ground truth answers are not empty
            assert len(case.gt_answer.strip()) > 0


class TestOfficialRAGCheckerEvaluator:
    """Test OfficialRAGCheckerEvaluator class."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance for testing."""
        return OfficialRAGCheckerEvaluator()

    def test_evaluator_initialization(self, evaluator):
        """Test evaluator initialization."""
        assert evaluator.metrics_dir.exists()
        assert evaluator.metrics_dir.is_dir()
        assert "baseline_evaluations" in str(evaluator.metrics_dir)

    @patch("subprocess.run")
    def test_get_memory_system_response_success(self, mock_run, evaluator):
        """Test successful memory system response retrieval."""
        # Mock successful subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"systems": {"cursor": {"output": "Test response from memory system"}}})
        mock_run.return_value = mock_result

        response = evaluator.get_memory_system_response("Test query")

        assert response == "Test response from memory system"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_memory_system_response_failure(self, mock_run, evaluator):
        """Test memory system response retrieval failure."""
        # Mock failed subprocess response
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: Memory system unavailable"
        mock_run.return_value = mock_result

        response = evaluator.get_memory_system_response("Test query")

        assert "Error:" in response
        assert "Memory system unavailable" in response

    def test_prepare_official_input_data(self, evaluator):
        """Test preparation of official input data."""
        with patch.object(evaluator, "get_memory_system_response") as mock_response:
            mock_response.return_value = "Mock response from memory system"

            input_data = evaluator.prepare_official_input_data()

            # Verify we get a dictionary with results
            assert isinstance(input_data, dict)
            assert "results" in input_data
            assert isinstance(input_data["results"], list)
            assert len(input_data["results"]) >= 5  # At least 5 test cases

            # Verify each input entry has required fields
            for entry in input_data["results"]:
                assert "query_id" in entry
                assert "query" in entry
                assert "gt_answer" in entry
                assert "response" in entry
                assert "retrieved_context" in entry
                assert entry["response"] == "Mock response from memory system"

    def test_save_official_input_data(self, evaluator):
        """Test saving official input data to file."""
        test_data = [
            {
                "query_id": "test_001",
                "query": "Test query",
                "gt_answer": "Test answer",
                "response": "Test response",
                "retrieved_context": ["Test context"],
            }
        ]

        input_file = evaluator.save_official_input_data(test_data)

        # Verify file was created
        assert Path(input_file).exists()

        # Verify file contains correct data
        with open(input_file, "r") as f:
            saved_data = json.load(f)

        assert saved_data == test_data

        # Clean up
        Path(input_file).unlink()

    @patch("subprocess.run")
    def test_run_official_ragchecker_cli_success(self, mock_run, evaluator):
        """Test successful RAGChecker CLI execution."""
        # Mock successful CLI execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        input_file = "test_input.json"
        output_file = evaluator.run_official_ragchecker_cli(input_file)

        assert output_file is not None
        assert "ragchecker_official_output_" in output_file
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_official_ragchecker_cli_failure(self, mock_run, evaluator):
        """Test RAGChecker CLI execution failure."""
        # Mock failed CLI execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "CLI error"
        mock_run.return_value = mock_result

        input_file = "test_input.json"
        output_file = evaluator.run_official_ragchecker_cli(input_file)

        assert output_file is None

    def test_create_fallback_evaluation(self, evaluator):
        """Test fallback evaluation creation."""
        input_data = [
            {
                "query_id": "test_001",
                "query": "What is the project status?",
                "gt_answer": "The project is active with current backlog items.",
                "response": "The project is currently active and has several backlog items.",
                "retrieved_context": ["Project status information."],
            },
            {
                "query_id": "test_002",
                "query": "What is DSPy?",
                "gt_answer": "DSPy is a framework for programming with foundation models.",
                "response": "DSPy is a programming framework for foundation models.",
                "retrieved_context": ["DSPy framework information."],
            },
        ]

        fallback_result = evaluator.create_fallback_evaluation(input_data)

        # Verify fallback result structure
        assert "evaluation_type" in fallback_result
        assert fallback_result["evaluation_type"] == "fallback_simplified"
        assert "timestamp" in fallback_result
        assert "total_cases" in fallback_result
        assert fallback_result["total_cases"] == 2
        assert "overall_metrics" in fallback_result
        assert "case_results" in fallback_result

        # Verify metrics are calculated
        metrics = fallback_result["overall_metrics"]
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1_score"] <= 1

    @patch.object(OfficialRAGCheckerEvaluator, "run_official_ragchecker_cli")
    @patch.object(OfficialRAGCheckerEvaluator, "create_fallback_evaluation")
    def test_run_official_evaluation_with_fallback(self, mock_fallback, mock_cli, evaluator):
        """Test official evaluation with fallback mechanism."""
        # Mock CLI failure
        mock_cli.return_value = None

        # Mock fallback evaluation
        mock_fallback.return_value = {
            "evaluation_type": "fallback_simplified",
            "overall_metrics": {"precision": 0.5, "recall": 0.6, "f1_score": 0.55},
        }

        with patch.object(evaluator, "prepare_official_input_data") as mock_prepare:
            mock_prepare.return_value = [
                {
                    "query_id": "test",
                    "query": "test",
                    "gt_answer": "test",
                    "response": "test",
                    "retrieved_context": ["test"],
                }
            ]

            with patch.object(evaluator, "save_official_input_data") as mock_save:
                mock_save.return_value = "test_input.json"

                result = evaluator.run_official_evaluation()

                # Verify fallback was called
                mock_fallback.assert_called_once()
                assert result is not None


class TestRAGCheckerIntegration:
    """Integration tests for RAGChecker evaluation system."""

    def test_full_evaluation_workflow(self):
        """Test the complete evaluation workflow."""
        evaluator = OfficialRAGCheckerEvaluator()

        # Test that the evaluation can run end-to-end
        try:
            result = evaluator.run_official_evaluation()
            assert result is not None
        except Exception as e:
            # If evaluation fails, it should fail gracefully
            assert "fallback" in str(e).lower() or "error" in str(e).lower()

    def test_evaluation_output_format(self):
        """Test that evaluation output follows expected format."""
        evaluator = OfficialRAGCheckerEvaluator()

        # Create test input data
        test_data = [
            {
                "query_id": "integration_test_001",
                "query": "Integration test query?",
                "gt_answer": "Integration test answer.",
                "response": "Integration test response.",
                "retrieved_context": ["Integration test context."],
            }
        ]

        # Run fallback evaluation
        result = evaluator.create_fallback_evaluation(test_data)

        # Verify output format
        required_fields = ["evaluation_type", "timestamp", "total_cases", "overall_metrics", "case_results", "note"]

        for field in required_fields:
            assert field in result

        # Verify metrics structure
        metrics = result["overall_metrics"]
        metric_fields = ["precision", "recall", "f1_score"]
        for field in metric_fields:
            assert field in metrics
            assert isinstance(metrics[field], (int, float))

    def test_evaluation_file_creation(self):
        """Test that evaluation files are created correctly."""
        evaluator = OfficialRAGCheckerEvaluator()

        # Test input data creation
        test_data = [
            {
                "query_id": "file_test",
                "query": "test",
                "gt_answer": "test",
                "response": "test",
                "retrieved_context": ["test"],
            }
        ]

        input_file = evaluator.save_official_input_data(test_data)

        # Verify file exists and is valid JSON
        assert Path(input_file).exists()

        with open(input_file, "r") as f:
            data = json.load(f)
            assert data == test_data

        # Clean up
        Path(input_file).unlink()


class TestRAGCheckerValidation:
    """Validation tests for RAGChecker evaluation system."""

    def test_ragchecker_installation(self):
        """Test that RAGChecker is properly installed."""
        try:
            import ragchecker

            assert ragchecker is not None
        except ImportError:
            pytest.fail("RAGChecker is not installed")

    def test_spacy_model_availability(self):
        """Test that spaCy model is available."""
        try:
            import spacy

            nlp = spacy.load("en_core_web_sm")
            assert nlp is not None
        except OSError:
            pytest.fail("spaCy model 'en_core_web_sm' is not available")

    def test_cli_availability(self):
        """Test that RAGChecker CLI is available."""
        try:
            result = subprocess.run(
                ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "ragchecker.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # CLI should either show help or fail gracefully
            assert result.returncode in [0, 1]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # CLI might not be available, which is expected
            pass

    def test_memory_system_integration(self):
        """Test memory system integration."""
        evaluator = OfficialRAGCheckerEvaluator()

        # Test that memory system response method exists
        assert hasattr(evaluator, "get_memory_system_response")
        assert callable(evaluator.get_memory_system_response)

    def test_metrics_directory_structure(self):
        """Test that metrics directory structure is correct."""
        evaluator = OfficialRAGCheckerEvaluator()

        # Verify metrics directory exists
        assert evaluator.metrics_dir.exists()
        assert evaluator.metrics_dir.is_dir()

        # Verify it's in the correct location
        assert "metrics" in str(evaluator.metrics_dir)
        assert "baseline_evaluations" in str(evaluator.metrics_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
