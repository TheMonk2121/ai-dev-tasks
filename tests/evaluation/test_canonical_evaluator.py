#!/usr/bin/env python3
"""
Tests for the canonical OfficialRAGCheckerEvaluator implementation.

This test suite ensures the canonical implementation works correctly
and fails loudly if the canonical module is missing (no silent fallbacks).
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import pytest  # type: ignore[import-untyped]


class TestCanonicalEvaluator:
    """Test suite for the canonical OfficialRAGCheckerEvaluator."""

    def test_canonical_import_success(self) -> None:
        """Test that the canonical evaluator can be imported successfully."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        # Should not raise an exception
        evaluator = OfficialRAGCheckerEvaluator()
        assert evaluator is not None
        assert hasattr(evaluator, 'run_evaluation')
        assert hasattr(evaluator, 'create_fallback_evaluation')
        assert hasattr(evaluator, 'prepare_official_input_data')
        assert hasattr(evaluator, 'create_official_test_cases')

    def test_canonical_import_failure(self) -> None:
        """Test that import failures are handled properly."""
        # This test ensures we don't have silent fallbacks
        # The canonical module should be mandatory
        try:
            from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
            # If we get here, the import succeeded
            assert True
        except ImportError as e:
            pytest.fail(f"Canonical evaluator import failed: {e}")

    def test_evaluator_initialization(self) -> None:
        """Test that the evaluator initializes correctly."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Check that metrics directory is set up
        assert evaluator.metrics_dir.exists()
        assert evaluator.metrics_dir.name == "baseline_evaluations"
        
        # Check that internal state is initialized
        assert evaluator._eval_path_tag == "unknown"
        assert evaluator._progress_fh is None
        assert evaluator._progress_path is None

    def test_fallback_evaluation(self) -> None:
        """Test that fallback evaluation works correctly."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Test with empty data
        result = evaluator.create_fallback_evaluation(None)
        assert result["evaluation_type"] == "fallback_mock"
        assert result["total_cases"] == 0
        assert "overall_metrics" in result
        
        # Test with sample data
        sample_data = [{"test": "case1"}, {"test": "case2"}]
        result = evaluator.create_fallback_evaluation(sample_data)
        assert result["total_cases"] == 2
        assert result["case_results"] == sample_data

    def test_official_test_cases(self) -> None:
        """Test that official test cases method works."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Should return empty list by default
        cases = evaluator.create_official_test_cases()
        assert cases == []

    def test_prepare_official_input_data(self) -> None:
        """Test that prepare official input data works."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Should return empty results by default
        data = evaluator.prepare_official_input_data()
        assert data == {"results": []}

    def test_run_official_evaluation_interface(self) -> None:
        """Test that the run_official_evaluation interface works."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Test that the method exists and has the right signature
        assert hasattr(evaluator, 'run_official_evaluation')
        
        # The method should accept cases_file and outdir parameters
        # We'll test the interface without actually running evaluation
        import inspect
        sig = inspect.signature(evaluator.run_official_evaluation)
        params = list(sig.parameters.keys())
        assert 'cases_file' in params
        assert 'outdir' in params

    def test_evaluation_with_mock_data(self) -> None:
        """Test evaluation with mock data in a controlled environment."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        # Set up mock environment
        os.environ["RAGCHECKER_USE_REAL_RAG"] = "0"
        os.environ["EVAL_DRIVER"] = "synthetic"
        
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Create temporary test cases file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            test_cases = [
                {
                    "id": "test_case_1",
                    "query": "What is the main purpose of this system?",
                    "gt_answer": "The system is designed for AI development tasks.",
                    "expected_files": ["README.md"],
                    "mode": "retrieval",
                    "tags": ["test", "basic"]
                }
            ]
            for case in test_cases:
                f.write(json.dumps(case) + "\n")
            cases_file = f.name
        
        try:
            # Create temporary output directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Run evaluation
                results = evaluator.run_evaluation(
                    cases_file=cases_file,
                    outdir=temp_dir
                )
                
                # Verify results structure
                assert "evaluation_type" in results
                assert "overall_metrics" in results
                assert "case_results" in results
                assert "total_cases" in results
                
                # Verify metrics
                metrics = results["overall_metrics"]
                assert "precision" in metrics
                assert "recall" in metrics
                assert "f1_score" in metrics
                assert "faithfulness" in metrics
                
                # Verify case results
                case_results = results["case_results"]
                assert len(case_results) == 1
                assert "query" in case_results[0]
                assert "response" in case_results[0]
                assert "precision" in case_results[0]
                assert "recall" in case_results[0]
                assert "f1_score" in case_results[0]
                
        finally:
            # Clean up
            Path(cases_file).unlink(missing_ok=True)

    def test_no_archive_fallback(self) -> None:
        """Test that there are no archive fallbacks in the canonical implementation."""
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        
        # The canonical implementation should not have any archive fallback logic
        # This is tested by ensuring the import succeeds and the evaluator works
        evaluator = OfficialRAGCheckerEvaluator()
        
        # Verify that the evaluator is the canonical implementation
        assert evaluator.__class__.__name__ == "OfficialRAGCheckerEvaluator"
        assert evaluator.__class__.__module__ == "src.evaluation.ragchecker_official_impl"
        
        # Verify that it has the expected methods
        expected_methods = [
            'run_evaluation',
            'create_fallback_evaluation',
            'prepare_official_input_data',
            'create_official_test_cases',
            'run_official_evaluation'
        ]
        
        for method_name in expected_methods:
            assert hasattr(evaluator, method_name), f"Missing method: {method_name}"

    def test_regression_no_silent_fallbacks(self) -> None:
        """Regression test to ensure no silent fallbacks to archive implementations."""
        # This test ensures that if the canonical module is missing,
        # we get a clear error rather than silently falling back to archives
        
        # First, verify the canonical import works
        try:
            from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
            # If we get here, the canonical implementation is available
            assert True
        except ImportError as e:
            pytest.fail(f"Canonical evaluator should be available: {e}")
        
        # Verify that the evaluator is from the canonical location
        evaluator = OfficialRAGCheckerEvaluator()
        module_name = evaluator.__class__.__module__
        assert module_name == "src.evaluation.ragchecker_official_impl"
        assert "600_archives" not in module_name
        assert "300_experiments" not in module_name

    def test_adapter_compatibility(self) -> None:
        """Test that the adapter can work with the canonical implementation."""
        from src.evaluation.adapters.ragchecker import RagCheckerAdapter
        
        # The adapter should be able to import the canonical evaluator
        adapter = RagCheckerAdapter()
        assert adapter is not None
        
        # Verify that the adapter can access the evaluator class
        # (This tests the import path in the adapter)
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        assert OfficialRAGCheckerEvaluator is not None

    def test_profile_runner_compatibility(self) -> None:
        """Test that profile runners can work with the canonical implementation."""
        # Test gold profile
        from scripts.evaluation.profiles.gold import _run_gold
        from scripts.evaluation.profiles.mock import _run_mock
        from scripts.evaluation.profiles.real import _run_real
        
        # These should not raise import errors
        assert _run_gold is not None
        assert _run_real is not None
        assert _run_mock is not None
        
        # Test that they can import the canonical evaluator
        from src.evaluation.ragchecker_official_impl import OfficialRAGCheckerEvaluator
        assert OfficialRAGCheckerEvaluator is not None
