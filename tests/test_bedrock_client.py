#!/usr/bin/env python3
"""
Unit tests for BedrockClient
Tests client initialization, retry logic, token tracking, and error handling
"""

import json
import os

# Add scripts directory to path for imports
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.bedrock_client import BedrockClient, BedrockUsage


class TestBedrockUsage(unittest.TestCase):
    """Test BedrockUsage dataclass."""

    def test_usage_initialization(self):
        """Test BedrockUsage initialization."""
        usage = BedrockUsage()
        self.assertEqual(usage.input_tokens, 0)
        self.assertEqual(usage.output_tokens, 0)
        self.assertEqual(usage.request_count, 0)
        self.assertEqual(usage.total_cost, 0.0)
        self.assertEqual(usage.timestamp, "")

    def test_usage_to_dict(self):
        """Test BedrockUsage to_dict conversion."""
        usage = BedrockUsage(
            input_tokens=100, output_tokens=50, request_count=1, total_cost=0.001, timestamp="2024-01-01T00:00:00"
        )

        expected = {
            "input_tokens": 100,
            "output_tokens": 50,
            "request_count": 1,
            "total_cost": 0.001,
            "timestamp": "2024-01-01T00:00:00",
        }

        self.assertEqual(usage.to_dict(), expected)


class TestBedrockClient(unittest.TestCase):
    """Test BedrockClient functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary usage log file
        self.temp_dir = tempfile.mkdtemp()
        self.usage_log_file = os.path.join(self.temp_dir, "test_usage.json")

        # Initialize client with test configuration
        self.client = BedrockClient(
            region_name="us-east-1",
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            max_retries=2,
            timeout=10,
            usage_log_file=self.usage_log_file,
        )

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        if os.path.exists(self.usage_log_file):
            os.remove(self.usage_log_file)
        os.rmdir(self.temp_dir)

    def test_client_initialization(self):
        """Test BedrockClient initialization."""
        self.assertEqual(self.client.region_name, "us-east-1")
        self.assertEqual(self.client.model_id, "anthropic.claude-3-5-sonnet-20241022-v2:0")
        self.assertEqual(self.client.max_retries, 2)
        self.assertEqual(self.client.timeout, 10)
        self.assertEqual(self.client.usage_log_file, self.usage_log_file)

        # Check session usage is initialized
        self.assertIsInstance(self.client.session_usage, BedrockUsage)
        self.assertEqual(self.client.session_usage.request_count, 0)

    @patch("boto3.client")
    def test_bedrock_runtime_lazy_initialization(self, mock_boto_client):
        """Test lazy initialization of Bedrock Runtime client."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # First access should initialize
        runtime = self.client.bedrock_runtime
        self.assertEqual(runtime, mock_client)

        # Second access should return same instance
        runtime2 = self.client.bedrock_runtime
        self.assertEqual(runtime2, mock_client)

        # Should only call boto3.client once; allow extra kwargs like config
        mock_boto_client.assert_called_once()
        args, kwargs = mock_boto_client.call_args
        assert args[0] == "bedrock-runtime"
        assert kwargs.get("region_name") == "us-east-1"

    @patch("boto3.client")
    def test_bedrock_lazy_initialization(self, mock_boto_client):
        """Test lazy initialization of Bedrock client."""
        mock_client = Mock()
        mock_boto_client.return_value = mock_client

        # First access should initialize
        bedrock = self.client.bedrock
        self.assertEqual(bedrock, mock_client)

        # Second access should return same instance
        bedrock2 = self.client.bedrock
        self.assertEqual(bedrock2, mock_client)

        # Should only call boto3.client once; allow extra kwargs like config
        mock_boto_client.assert_called_once()
        args, kwargs = mock_boto_client.call_args
        assert args[0] == "bedrock"
        assert kwargs.get("region_name") == "us-east-1"

    @patch("boto3.client")
    def test_connection_test_success(self, mock_boto_client):
        """Test successful connection test."""
        # Mock bedrock client
        mock_bedrock = Mock()
        mock_bedrock.list_foundation_models.return_value = {
            "modelSummaries": [
                {"modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0"},
                {"modelId": "anthropic.claude-3-haiku-20240307-v1:0"},
            ]
        }
        mock_boto_client.return_value = mock_bedrock

        result = self.client.test_connection()
        self.assertTrue(result)
        mock_bedrock.list_foundation_models.assert_called_once()

    @patch("scripts.bedrock_client.BedrockClient.bedrock")
    def test_connection_test_model_not_found(self, mock_bedrock):
        """Test connection test when target model not available."""
        # Mock response without target model
        mock_bedrock.list_foundation_models.return_value = {
            "modelSummaries": [{"modelId": "anthropic.claude-3-haiku-20240307-v1:0"}]
        }

        result = self.client.test_connection()
        self.assertFalse(result)

    @patch("scripts.bedrock_client.BedrockClient.bedrock")
    def test_connection_test_exception(self, mock_bedrock):
        """Test connection test with exception."""
        mock_bedrock.list_foundation_models.side_effect = Exception("Connection failed")

        result = self.client.test_connection()
        self.assertFalse(result)

    def test_extract_usage(self):
        """Test usage extraction from response."""
        response_body = {"usage": {"input_tokens": 100, "output_tokens": 50}}

        usage = self.client._extract_usage(response_body)

        self.assertEqual(usage.input_tokens, 100)
        self.assertEqual(usage.output_tokens, 50)
        self.assertEqual(usage.request_count, 1)

        # Check cost calculation
        expected_cost = (100 * self.client.INPUT_TOKEN_COST) + (50 * self.client.OUTPUT_TOKEN_COST)
        self.assertAlmostEqual(usage.total_cost, expected_cost, places=6)

        # Check timestamp is set
        self.assertIsInstance(usage.timestamp, str)
        self.assertGreater(len(usage.timestamp), 0)

    def test_update_usage(self):
        """Test session usage update."""
        usage1 = BedrockUsage(
            input_tokens=100, output_tokens=50, request_count=1, total_cost=0.001, timestamp="2024-01-01T00:00:00"
        )

        usage2 = BedrockUsage(
            input_tokens=200, output_tokens=75, request_count=1, total_cost=0.002, timestamp="2024-01-01T01:00:00"
        )

        self.client._update_usage(usage1)
        self.client._update_usage(usage2)

        session_usage = self.client.get_session_usage()
        self.assertEqual(session_usage.input_tokens, 300)
        self.assertEqual(session_usage.output_tokens, 125)
        self.assertEqual(session_usage.request_count, 2)
        self.assertAlmostEqual(session_usage.total_cost, 0.003, places=6)
        self.assertEqual(session_usage.timestamp, "2024-01-01T01:00:00")

    def test_log_usage(self):
        """Test usage logging to file."""
        usage1 = BedrockUsage(
            input_tokens=100, output_tokens=50, request_count=1, total_cost=0.001, timestamp="2024-01-01T00:00:00"
        )

        usage2 = BedrockUsage(
            input_tokens=200, output_tokens=75, request_count=1, total_cost=0.002, timestamp="2024-01-01T01:00:00"
        )

        # Log usage entries
        self.client._log_usage(usage1)
        self.client._log_usage(usage2)

        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.usage_log_file))

        with open(self.usage_log_file, "r") as f:
            logged_data = json.load(f)

        self.assertEqual(len(logged_data), 2)
        self.assertEqual(logged_data[0]["input_tokens"], 100)
        self.assertEqual(logged_data[1]["input_tokens"], 200)

    def test_get_total_usage(self):
        """Test total usage calculation from log file."""
        # Create test usage log
        usage_data = [
            {"input_tokens": 100, "output_tokens": 50, "request_count": 1, "total_cost": 0.001},
            {"input_tokens": 200, "output_tokens": 75, "request_count": 1, "total_cost": 0.002},
        ]

        with open(self.usage_log_file, "w") as f:
            json.dump(usage_data, f)

        total_usage = self.client.get_total_usage()

        self.assertEqual(total_usage.input_tokens, 300)
        self.assertEqual(total_usage.output_tokens, 125)
        self.assertEqual(total_usage.request_count, 2)
        self.assertAlmostEqual(total_usage.total_cost, 0.003, places=6)

    def test_get_total_usage_no_file(self):
        """Test total usage when log file doesn't exist."""
        # Ensure file doesn't exist
        if os.path.exists(self.usage_log_file):
            os.remove(self.usage_log_file)

        total_usage = self.client.get_total_usage()

        self.assertEqual(total_usage.input_tokens, 0)
        self.assertEqual(total_usage.output_tokens, 0)
        self.assertEqual(total_usage.request_count, 0)
        self.assertEqual(total_usage.total_cost, 0.0)

    @patch("boto3.client")
    def test_invoke_model_success(self, mock_boto_client):
        """Test successful model invocation."""
        # Mock bedrock runtime client
        mock_runtime = Mock()
        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(
            {"content": [{"text": "Test response"}], "usage": {"input_tokens": 10, "output_tokens": 5}}
        ).encode()

        mock_runtime.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_runtime

        response_text, usage = self.client.invoke_model(prompt="Test prompt", max_tokens=100)

        self.assertEqual(response_text, "Test response")
        self.assertEqual(usage.input_tokens, 10)
        self.assertEqual(usage.output_tokens, 5)

        # Verify session usage was updated
        session_usage = self.client.get_session_usage()
        self.assertEqual(session_usage.input_tokens, 10)
        self.assertEqual(session_usage.output_tokens, 5)
        self.assertEqual(session_usage.request_count, 1)

    @patch("boto3.client")
    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_invoke_model_retry_on_throttling(self, mock_sleep, mock_boto_client):
        """Test retry logic on throttling exception."""
        from botocore.exceptions import ClientError

        # Mock bedrock runtime client
        mock_runtime = Mock()
        mock_boto_client.return_value = mock_runtime

        # First call fails with throttling, second succeeds
        throttling_error = ClientError(
            error_response={"Error": {"Code": "ThrottlingException"}}, operation_name="InvokeModel"
        )

        mock_response = {"body": Mock()}
        mock_response["body"].read.return_value = json.dumps(
            {"content": [{"text": "Success after retry"}], "usage": {"input_tokens": 10, "output_tokens": 5}}
        ).encode()

        mock_runtime.invoke_model.side_effect = [throttling_error, mock_response]

        response_text, usage = self.client.invoke_model(prompt="Test")

        self.assertEqual(response_text, "Success after retry")
        self.assertEqual(mock_runtime.invoke_model.call_count, 2)
        mock_sleep.assert_called_once()  # Should have slept once for retry

    def test_invoke_with_json_prompt(self):
        """Test JSON prompt invocation."""
        with patch.object(self.client, "invoke_model") as mock_invoke:
            mock_invoke.return_value = ('{"result": 42}', BedrockUsage())

            response, usage = self.client.invoke_with_json_prompt(prompt="Calculate something", max_tokens=150)

            # Verify invoke_model was called with JSON-specific parameters
            mock_invoke.assert_called_once()
            args, kwargs = mock_invoke.call_args

            self.assertIn("valid JSON", kwargs["prompt"])
            self.assertIn("Calculate something", kwargs["prompt"])
            self.assertEqual(kwargs["max_tokens"], 150)
            self.assertIsNotNone(kwargs["system_prompt"])
            self.assertIn("JSON", kwargs["system_prompt"])


class TestBedrockClientIntegration(unittest.TestCase):
    """Integration tests for BedrockClient (require AWS credentials)."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.client = BedrockClient()

    @unittest.skipUnless(
        os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"),
        "AWS credentials required for integration tests",
    )
    def test_real_connection(self):
        """Test real connection to AWS Bedrock (requires credentials)."""
        result = self.client.test_connection()
        # This will pass or fail based on actual AWS setup
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
