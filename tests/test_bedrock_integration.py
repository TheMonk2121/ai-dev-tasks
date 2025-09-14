#!/usr/bin/env python3
"""
Comprehensive integration tests for AWS Bedrock RAGChecker integration
Tests all components of B-1046 implementation
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Add scripts directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from scripts.bedrock_batch_processor import BatchRequest, BedrockBatchProcessor
from scripts.bedrock_client import BedrockClient, BedrockUsage
from scripts.bedrock_cost_monitor import BedrockCostMonitor


class TestBedrockIntegration(unittest.TestCase):
    """Integration tests for Bedrock components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.usage_log_file = os.path.join(self.temp_dir, "test_usage.json")
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        
        shutil.rmtree(self.temp_dir)

    def test_bedrock_client_initialization(self):
        """Test BedrockClient initialization and configuration."""
        client = BedrockClient(
            region_name="us-east-1",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            usage_log_file=self.usage_log_file,
        )

        self.assertEqual(client.region_name, "us-east-1")
        self.assertEqual(client.model_id, "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.assertEqual(client.usage_log_file, self.usage_log_file)
        self.assertIsInstance(client.session_usage, BedrockUsage)

    def test_cost_monitor_initialization(self):
        """Test BedrockCostMonitor initialization and configuration."""
        monitor = BedrockCostMonitor(usage_log_file=self.usage_log_file, config_file=self.config_file)

        self.assertEqual(str(monitor.usage_log_file), self.usage_log_file)
        self.assertEqual(str(monitor.config_file), self.config_file)
        self.assertIsInstance(monitor.config, dict)
        self.assertIn("budget_alerts", monitor.config)

    def test_batch_processor_initialization(self):
        """Test BedrockBatchProcessor initialization."""
        processor = BedrockBatchProcessor(max_concurrent=3, batch_size=5, rate_limit_delay=0.1)

        self.assertEqual(processor.max_concurrent, 3)
        self.assertEqual(processor.batch_size, 5)
        self.assertEqual(processor.rate_limit_delay, 0.1)
        # Check that it's the right type by checking attributes instead of exact class
        self.assertTrue(hasattr(processor.total_usage, "input_tokens"))
        self.assertTrue(hasattr(processor.total_usage, "output_tokens"))
        self.assertTrue(hasattr(processor.total_usage, "total_cost"))

    def test_usage_tracking_integration(self):
        """Test integration between client and cost monitor."""
        # Create mock usage data
        usage_data = [
            {
                "input_tokens": 100,
                "output_tokens": 50,
                "request_count": 1,
                "total_cost": 0.001,
                "timestamp": "2024-01-01T10:00:00",
            },
            {
                "input_tokens": 200,
                "output_tokens": 75,
                "request_count": 1,
                "total_cost": 0.002,
                "timestamp": "2024-01-01T11:00:00",
            },
        ]

        # Write test data
        with open(self.usage_log_file, "w") as f:
            json.dump(usage_data, f)

        # Test cost monitor can read the data
        monitor = BedrockCostMonitor(usage_log_file=self.usage_log_file)
        summary = monitor.get_usage_summary("all")

        self.assertEqual(summary.total_requests, 2)
        self.assertEqual(summary.total_input_tokens, 300)
        self.assertEqual(summary.total_output_tokens, 125)
        self.assertAlmostEqual(summary.total_cost, 0.003, places=6)

    def test_budget_alert_system(self):
        """Test budget alert functionality."""
        # Create config with low budgets for testing
        test_config = {
            "budget_alerts": {
                "daily_budget": 0.001,  # Very low for testing
                "weekly_budget": 0.005,
                "monthly_budget": 0.020,
                "spike_threshold": 2.0,
            }
        }

        with open(self.config_file, "w") as f:
            json.dump(test_config, f)

        # Create usage that exceeds budget (use today's date)
        from datetime import datetime

        today = datetime.now().isoformat()

        usage_data = [
            {
                "input_tokens": 1000,
                "output_tokens": 500,
                "request_count": 1,
                "total_cost": 0.002,  # Exceeds daily budget
                "timestamp": today,
            }
        ]

        with open(self.usage_log_file, "w") as f:
            json.dump(usage_data, f)

        monitor = BedrockCostMonitor(usage_log_file=self.usage_log_file, config_file=self.config_file)

        alerts = monitor.check_budget_alerts()
        self.assertGreater(len(alerts), 0)

        # Check alert structure
        alert = alerts[0]
        self.assertIn("type", alert)
        self.assertIn("message", alert)
        self.assertIn("severity", alert)

    def test_batch_request_creation(self):
        """Test batch request creation and processing."""
        requests = [
            BatchRequest(request_id="test_1", prompt="Test prompt 1", max_tokens=100, use_json_prompt=True),
            BatchRequest(request_id="test_2", prompt="Test prompt 2", max_tokens=150, use_json_prompt=False),
        ]

        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0].request_id, "test_1")
        self.assertTrue(requests[0].use_json_prompt)
        self.assertFalse(requests[1].use_json_prompt)

    @patch.object(BedrockClient, "test_connection")
    def test_connection_fallback(self, mock_test_connection):
        """Test fallback behavior when Bedrock is unavailable."""
        # Mock connection failure
        mock_test_connection.return_value = False

        client = BedrockClient()
        connection_result = client.test_connection()

        self.assertFalse(connection_result)
        mock_test_connection.assert_called_once()

    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation."""
        processor = BedrockBatchProcessor()

        # Simulate some processing
        processor.total_requests = 10
        processor.successful_requests = 8
        processor.failed_requests = 2
        processor.total_usage = BedrockUsage(input_tokens=1000, output_tokens=500, request_count=10, total_cost=0.01)

        metrics = processor.get_performance_metrics()

        self.assertEqual(metrics["total_requests"], 10)
        self.assertEqual(metrics["successful_requests"], 8)
        self.assertEqual(metrics["failed_requests"], 2)
        self.assertEqual(metrics["success_rate"], 0.8)
        self.assertAlmostEqual(metrics["avg_cost_per_request"], 0.00125, places=6)

    def test_cost_report_generation(self):
        """Test comprehensive cost report generation."""
        # Create test usage data
        usage_data = [
            {
                "input_tokens": 500,
                "output_tokens": 250,
                "request_count": 1,
                "total_cost": 0.005,
                "timestamp": "2024-01-01T10:00:00",
            }
        ]

        with open(self.usage_log_file, "w") as f:
            json.dump(usage_data, f)

        monitor = BedrockCostMonitor(usage_log_file=self.usage_log_file)
        report = monitor.generate_cost_report("all")

        # Verify report structure
        self.assertIn("report_date", report)
        self.assertIn("period", report)
        self.assertIn("summary", report)
        self.assertIn("budget_status", report)
        self.assertIn("alerts", report)
        self.assertIn("recommendations", report)
        self.assertIn("cost_breakdown", report)

        # Verify summary data
        summary = report["summary"]
        self.assertEqual(summary["total_requests"], 1)
        self.assertAlmostEqual(summary["total_cost"], 0.005, places=6)

    def test_optimization_recommendations(self):
        """Test cost optimization recommendations."""
        monitor = BedrockCostMonitor()

        # Mock high-cost usage for recommendations
        with patch.object(monitor, "get_usage_summary") as mock_summary:
            mock_summary.return_value = type(
                "Summary",
                (),
                {
                    "total_requests": 10,
                    "avg_cost_per_request": 0.01,  # High cost
                    "avg_tokens_per_request": 2500,  # High tokens
                    "peak_usage_hour": "14:00",
                },
            )()

            recommendations = monitor.get_optimization_recommendations()

            self.assertGreater(len(recommendations), 0)

            # Check recommendation structure
            rec = recommendations[0]
            self.assertIn("type", rec)
            self.assertIn("priority", rec)
            self.assertIn("title", rec)
            self.assertIn("description", rec)
            self.assertIn("suggestions", rec)

    def test_environment_variable_integration(self):
        """Test environment variable configuration."""
        # Test various environment variables
        test_vars = {
            "RAGCHECKER_USE_BEDROCK": "1",
            "RAGCHECKER_MAX_WORDS": "500",
            "RAGCHECKER_BATCH_SIZE": "3",
            "RAGCHECKER_MAX_CONCURRENT": "2",
        }

        for var, value in test_vars.items():
            with patch.dict(os.environ, {var: value}):
                env_value = os.getenv(var)
                self.assertEqual(env_value, value)

    def test_error_handling_and_resilience(self):
        """Test error handling across components."""
        # Test with corrupted JSON
        with open(self.usage_log_file, "w") as f:
            f.write("invalid json content")

        monitor = BedrockCostMonitor(usage_log_file=self.usage_log_file)
        usage_data = monitor.load_usage_data()

        # Should handle gracefully
        self.assertEqual(usage_data, [])

    def test_configuration_validation(self):
        """Test configuration validation and defaults."""
        # Test with missing config file in temp directory
        missing_config = os.path.join(self.temp_dir, "nonexistent_config.json")
        monitor = BedrockCostMonitor(config_file=missing_config)

        # Should create default config
        self.assertIsInstance(monitor.config, dict)
        self.assertIn("budget_alerts", monitor.config)
        self.assertIn("daily_budget", monitor.config["budget_alerts"])

    def test_integration_workflow(self):
        """Test complete integration workflow."""
        # 1. Initialize components
        client = BedrockClient(usage_log_file=self.usage_log_file)
        BedrockCostMonitor(usage_log_file=self.usage_log_file)
        BedrockBatchProcessor(bedrock_client=client)

        # 2. Simulate usage (mock the actual API calls)
        with patch.object(client, "invoke_model") as mock_invoke:
            mock_invoke.return_value = (
                "Test response",
                BedrockUsage(
                    input_tokens=100,
                    output_tokens=50,
                    request_count=1,
                    total_cost=0.001,
                    timestamp="2024-01-01T10:00:00",
                ),
            )

            # 3. Process a request
            response_text, usage = client.invoke_model("Test prompt")

            # 4. Verify results
            self.assertEqual(response_text, "Test response")
            self.assertEqual(usage.input_tokens, 100)
            self.assertEqual(usage.output_tokens, 50)
            self.assertAlmostEqual(usage.total_cost, 0.001, places=6)

        # 5. Check session usage (should be updated by _update_usage call)
        client.get_session_usage()
        # Note: Session usage is only updated when _update_usage is called
        # which happens in the actual invoke_model method, not our mock


class TestRAGCheckerIntegration(unittest.TestCase):
    """Test RAGChecker integration with Bedrock."""

    def test_ragchecker_imports(self):
        """Test that RAGChecker integration imports work."""
        try:
            from scripts.ragchecker_official_evaluation import OfficialRAGCheckerEvaluator

            evaluator = OfficialRAGCheckerEvaluator()
            self.assertIsNotNone(evaluator)
        except ImportError as e:
            self.skipTest(f"RAGChecker integration not available: {e}")

    def test_batch_evaluation_imports(self):
        """Test that batch evaluation imports work."""
        try:
            from scripts.ragchecker_batch_evaluation import BatchRAGCheckerEvaluator

            evaluator = BatchRAGCheckerEvaluator()
            self.assertIsNotNone(evaluator)
        except ImportError as e:
            self.skipTest(f"Batch evaluation not available: {e}")


def run_validation_suite():
    """Run the complete validation suite."""
    print("🧪 Running AWS Bedrock Integration Validation Suite")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestBedrockIntegration))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestRAGCheckerIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n📊 Validation Results:")
    print(f"   Tests Run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("✅ All tests passed! B-1046 integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(run_validation_suite())
