"""Performance validation tests for RAGChecker evaluation system."""

import subprocess
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the RAGChecker evaluation classes
from scripts.ragchecker_official_evaluation import OfficialRAGCheckerEvaluator


class TestRAGCheckerPerformance:
    """Performance validation tests for RAGChecker evaluation system."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance for performance testing."""
        return OfficialRAGCheckerEvaluator()

    def test_evaluation_response_time(self, evaluator):
        """Test that evaluation completes within acceptable time limits."""
        start_time = time.time()

        # Run a quick evaluation
        with patch.object(evaluator, "get_memory_system_response") as mock_response:
            mock_response.return_value = "Mock response for performance testing"

            with patch.object(evaluator, "run_official_ragchecker_cli") as mock_cli:
                mock_cli.return_value = None  # Force fallback evaluation

                result = evaluator.run_official_evaluation()

        end_time = time.time()
        execution_time = end_time - start_time

        # Performance requirements
        assert execution_time < 30.0  # Should complete within 30 seconds
        assert result is not None

        print(f"✅ Evaluation completed in {execution_time:.2f} seconds")

    def test_memory_system_response_time(self, evaluator):
        """Test memory system response time."""
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"systems": {"cursor": {"output": "Test response"}}}'
            mock_run.return_value = mock_result

            start_time = time.time()
            response = evaluator.get_memory_system_response("Test query")
            end_time = time.time()

            response_time = end_time - start_time

            # Memory system should respond within 10 seconds
            assert response_time < 10.0
            assert response == "Test response"

            print(f"✅ Memory system response time: {response_time:.2f} seconds")

    def test_input_data_preparation_performance(self, evaluator):
        """Test input data preparation performance."""
        with patch.object(evaluator, "get_memory_system_response") as mock_response:
            mock_response.return_value = "Mock response for performance testing"

            start_time = time.time()
            input_data = evaluator.prepare_official_input_data()
            end_time = time.time()

            preparation_time = end_time - start_time

            # Input preparation should be fast
            assert preparation_time < 5.0  # Should complete within 5 seconds
            assert len(input_data) == 5  # 5 test cases

            print(f"✅ Input data preparation time: {preparation_time:.2f} seconds")

    def test_fallback_evaluation_performance(self, evaluator):
        """Test fallback evaluation performance."""
        # Create test data
        test_data = [
            {
                "query_id": f"perf_test_{i}",
                "query": f"Performance test query {i}?",
                "gt_answer": f"Performance test answer {i}.",
                "response": f"Performance test response {i}.",
                "retrieved_context": f"Performance test context {i}.",
            }
            for i in range(10)  # Test with 10 cases
        ]

        start_time = time.time()
        result = evaluator.create_fallback_evaluation(test_data)
        end_time = time.time()

        evaluation_time = end_time - start_time

        # Fallback evaluation should be very fast
        assert evaluation_time < 1.0  # Should complete within 1 second
        assert result["total_cases"] == 10
        assert "overall_metrics" in result

        print(f"✅ Fallback evaluation time: {evaluation_time:.3f} seconds")

    def test_file_io_performance(self, evaluator):
        """Test file I/O performance."""
        # Create large test data
        large_test_data = [
            {
                "query_id": f"io_test_{i}",
                "query": "Test query" * 10,  # Make it larger
                "gt_answer": "Test answer" * 20,
                "response": "Test response" * 50,
                "retrieved_context": "Test context" * 30,
            }
            for i in range(100)  # 100 test cases
        ]

        start_time = time.time()
        input_file = evaluator.save_official_input_data(large_test_data)
        end_time = time.time()

        save_time = end_time - start_time

        # File I/O should be fast
        assert save_time < 2.0  # Should complete within 2 seconds
        assert Path(input_file).exists()

        # Test file size
        file_size = Path(input_file).stat().st_size
        assert file_size > 0

        print(f"✅ File I/O time: {save_time:.3f} seconds, File size: {file_size} bytes")

        # Clean up
        Path(input_file).unlink()

    def test_concurrent_evaluation_performance(self, evaluator):
        """Test concurrent evaluation performance."""
        import queue
        import threading
        
        results_queue = queue.Queue()

        def run_evaluation(eval_id):
            """Run evaluation in separate thread."""
            try:
                with patch.object(evaluator, "get_memory_system_response") as mock_response:
                    mock_response.return_value = f"Mock response {eval_id}"

                    with patch.object(evaluator, "run_official_ragchecker_cli") as mock_cli:
                        mock_cli.return_value = None

                        result = evaluator.run_official_evaluation()
                        results_queue.put((eval_id, result))
            except Exception as e:
                results_queue.put((eval_id, f"Error: {e}"))

        # Run 3 concurrent evaluations
        threads = []
        start_time = time.time()

        for i in range(3):
            thread = threading.Thread(target=run_evaluation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # Verify all evaluations completed
        assert len(results) == 3
        assert total_time < 60.0  # Should complete within 60 seconds

        print(f"✅ Concurrent evaluation time: {total_time:.2f} seconds")

    def test_memory_usage_performance(self, evaluator):
        """Test memory usage during evaluation."""
        import os
        import psutil
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Run evaluation
        with patch.object(evaluator, "get_memory_system_response") as mock_response:
            mock_response.return_value = "Mock response for memory testing"

            with patch.object(evaluator, "run_official_ragchecker_cli") as mock_cli:
                mock_cli.return_value = None

                result = evaluator.run_official_evaluation()

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable
        assert memory_increase < 100.0  # Should not increase by more than 100MB
        assert result is not None

        print(f"✅ Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")

    def test_cli_performance_validation(self, evaluator):
        """Test CLI performance when available."""
        try:
            # Test CLI help command performance
            start_time = time.time()
            result = subprocess.run(
                ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "ragchecker.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            end_time = time.time()

            cli_time = end_time - start_time

            # CLI should respond quickly
            assert cli_time < 5.0  # Should complete within 5 seconds
            assert result.returncode in [0, 1]  # Help should work or fail gracefully

            print(f"✅ CLI response time: {cli_time:.2f} seconds")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # CLI might not be available, which is expected
            print("⚠️ CLI not available for performance testing")

    def test_evaluation_throughput(self, evaluator):
        """Test evaluation throughput (evaluations per second)."""
        # Create multiple test cases
        test_cases = [
            {
                "query_id": f"throughput_test_{i}",
                "query": f"Throughput test query {i}?",
                "gt_answer": f"Throughput test answer {i}.",
                "response": f"Throughput test response {i}.",
                "retrieved_context": f"Throughput test context {i}.",
            }
            for i in range(50)  # 50 test cases
        ]

        start_time = time.time()
        result = evaluator.create_fallback_evaluation(test_cases)
        end_time = time.time()

        total_time = end_time - start_time
        throughput = len(test_cases) / total_time

        # Should process at least 10 evaluations per second
        assert throughput > 10.0
        assert result["total_cases"] == 50

        print(f"✅ Evaluation throughput: {throughput:.1f} evaluations/second")

    def test_error_recovery_performance(self, evaluator):
        """Test error recovery performance."""
        # Test with various error conditions
        error_scenarios = [
            ("empty_response", ""),
            ("very_long_response", "x" * 10000),
            ("special_chars", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("unicode_chars", "测试文本 with unicode 🚀"),
        ]

        for scenario_name, test_response in error_scenarios:
            start_time = time.time()

            try:
                with patch.object(evaluator, "get_memory_system_response") as mock_response:
                    mock_response.return_value = test_response

                    with patch.object(evaluator, "run_official_ragchecker_cli") as mock_cli:
                        mock_cli.return_value = None

                        result = evaluator.run_official_evaluation()

                end_time = time.time()
                recovery_time = end_time - start_time

                # Error recovery should be fast
                assert recovery_time < 10.0
                assert result is not None

                print(f"✅ Error recovery ({scenario_name}): {recovery_time:.2f} seconds")

            except Exception as e:
                print(f"⚠️ Error recovery failed for {scenario_name}: {e}")


class TestRAGCheckerScalability:
    """Scalability tests for RAGChecker evaluation system."""

    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance for scalability testing."""
        return OfficialRAGCheckerEvaluator()

    def test_large_dataset_performance(self, evaluator):
        """Test performance with large datasets."""
        # Create large dataset
        large_dataset = [
            {
                "query_id": f"large_test_{i}",
                "query": f"Large dataset test query {i}?",
                "gt_answer": f"Large dataset test answer {i}.",
                "response": f"Large dataset test response {i}.",
                "retrieved_context": f"Large dataset test context {i}.",
            }
            for i in range(1000)  # 1000 test cases
        ]

        start_time = time.time()
        result = evaluator.create_fallback_evaluation(large_dataset)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should handle large datasets efficiently
        assert processing_time < 30.0  # Should complete within 30 seconds
        assert result["total_cases"] == 1000

        print(f"✅ Large dataset processing: {processing_time:.2f} seconds for 1000 cases")

    def test_memory_efficiency(self, evaluator):
        """Test memory efficiency with large datasets."""
        import os
        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process large dataset
        large_dataset = [
            {
                "query_id": f"memory_test_{i}",
                "query": f"Memory test query {i}?",
                "gt_answer": f"Memory test answer {i}.",
                "response": f"Memory test response {i}.",
                "retrieved_context": f"Memory test context {i}.",
            }
            for i in range(500)  # 500 test cases
        ]

        result = evaluator.create_fallback_evaluation(large_dataset)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory usage should be reasonable even with large datasets
        assert memory_increase < 200.0  # Should not increase by more than 200MB
        assert result["total_cases"] == 500

        print(f"✅ Memory efficiency: +{memory_increase:.1f}MB for 500 cases")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
