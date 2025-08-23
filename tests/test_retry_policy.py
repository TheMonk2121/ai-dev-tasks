#!/usr/bin/env python3
"""
Test suite for retry policy functionality.
"""

import json
import os
import sys
import time
from unittest.mock import patch

# Add the dspy-rag-system directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))

import pytest
from requests.exceptions import Timeout
from src.utils.retry_wrapper import (
    AuthenticationError,
    DataStoreError,
    RetryableError,
    handle_retryable_errors,
    is_fatal_error,
    load_error_policy,
    retry,
    retry_database,
    retry_http,
    retry_llm,
)


class TestRetryDecorator:
    """Test retry decorator functionality"""

    def test_successful_call_on_first_attempt(self):
        """Test that successful calls return immediately"""

        @retry(max_retries=3)
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_successful_call_after_retries(self):
        """Test that calls succeed after some retries"""
        call_count = 0

        @retry(max_retries=3)
        def failing_then_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = failing_then_successful()
        assert result == "success"
        assert call_count == 3

    def test_failure_after_max_retries(self):
        """Test that failure occurs after max retries"""
        call_count = 0

        @retry(max_retries=2)
        def always_failing():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_failing()

        assert call_count == 3  # Initial + 2 retries

    def test_backoff_timing(self):
        """Test exponential backoff timing"""
        call_times = []

        @retry(max_retries=3, backoff_factor=2.0)
        def failing_function():
            call_times.append(time.time())
            raise ValueError("Fails")

        with pytest.raises(ValueError):
            failing_function()

        # Check that delays increase exponentially
        assert len(call_times) == 4  # Initial + 3 retries

        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
        assert delays[0] >= 1.0  # 2^0 = 1 second
        assert delays[1] >= 2.0  # 2^1 = 2 seconds
        assert delays[2] >= 4.0  # 2^2 = 4 seconds

class TestErrorPolicyLoading:
    """Test error policy loading from configuration"""

    def test_load_error_policy_from_config(self):
        """Test loading error policy from system.json"""
        with patch("builtins.open") as mock_open:
            mock_config = {
                "error_policy": {
                    "max_retries": 5,
                    "backoff_factor": 1.5,
                    "timeout_seconds": 60,
                    "fatal_errors": ["CustomError", "AnotherError"],
                }
            }
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_config)

            policy = load_error_policy()

            assert policy["max_retries"] == 5
            assert policy["backoff_factor"] == 1.5
            assert policy["timeout_seconds"] == 60
            assert policy["fatal_errors"] == ["CustomError", "AnotherError"]

    def test_load_error_policy_with_missing_config(self):
        """Test loading with missing config file"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            policy = load_error_policy()

            assert policy["max_retries"] == 3
            assert policy["backoff_factor"] == 2.0
            assert policy["timeout_seconds"] == 30
            assert "ResourceBusyError" in policy["fatal_errors"]

    def test_load_error_policy_with_invalid_json(self):
        """Test loading with invalid JSON"""
        with patch("builtins.open") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid json"

            policy = load_error_policy()

            assert policy["max_retries"] == 3
            assert policy["backoff_factor"] == 2.0

class TestFatalErrorHandling:
    """Test that fatal errors don't retry"""

    def test_fatal_error_raises_immediately(self):
        """Test that fatal errors raise immediately without retrying"""
        call_count = 0

        @retry(max_retries=3, fatal_errors=["ValueError"])
        def function_with_fatal_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fatal error")

        with pytest.raises(ValueError, match="Fatal error"):
            function_with_fatal_error()

        assert call_count == 1  # Should not retry

    def test_non_fatal_error_retries(self):
        """Test that non-fatal errors retry"""
        call_count = 0

        @retry(max_retries=2, fatal_errors=["TypeError"])
        def function_with_retryable_error():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Retryable error")

        with pytest.raises(RuntimeError, match="Retryable error"):
            function_with_retryable_error()

        assert call_count == 3  # Should retry

    def test_custom_fatal_error_types(self):
        """Test custom fatal error types"""
        call_count = 0

        @retry(max_retries=2, fatal_errors=["CustomError"])
        def function_with_custom_error():
            nonlocal call_count
            call_count += 1
            raise CustomError("Custom fatal error")

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError, match="Custom fatal error"):
            function_with_custom_error()

        assert call_count == 1  # Should not retry

class TestRetryConvenienceFunctions:
    """Test convenience retry functions"""

    def test_retry_http_function(self):
        """Test retry_http convenience function"""
        call_count = 0

        @retry_http
        def http_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("HTTP error")

        with pytest.raises(RuntimeError):
            http_function()

        assert call_count == 4  # 3 retries + 1 initial

    def test_retry_database_function(self):
        """Test retry_database convenience function"""
        call_count = 0

        @retry_database
        def db_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("DB error")

        with pytest.raises(RuntimeError):
            db_function()

        assert call_count == 4  # 3 retries + 1 initial

    def test_retry_llm_function(self):
        """Test retry_llm convenience function"""
        call_count = 0

        @retry_llm
        def llm_function():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("LLM error")

        with pytest.raises(RuntimeError):
            llm_function()

        assert call_count == 3  # 2 retries + 1 initial

class TestIsFatalError:
    """Test fatal error detection"""

    def test_exact_type_match(self):
        """Test exact type name matching"""
        error = ValueError("test")
        fatal_errors = ["ValueError", "TypeError"]

        assert is_fatal_error(error, fatal_errors)

    def test_string_in_type_name(self):
        """Test string matching in type name"""
        error = ValueError("test")
        fatal_errors = ["Value", "Type"]

        assert is_fatal_error(error, fatal_errors)

    def test_fatal_exception_types(self):
        """Test built-in fatal exception types"""
        auth_error = AuthenticationError("auth failed")
        data_error = DataStoreError("db failed")

        assert is_fatal_error(auth_error, [])
        assert is_fatal_error(data_error, [])

    def test_non_fatal_error(self):
        """Test non-fatal error detection"""
        error = RuntimeError("runtime error")
        fatal_errors = ["ValueError", "TypeError"]

        assert not is_fatal_error(error, fatal_errors)

class TestJitter:
    """Test jitter functionality"""

    def test_jitter_adds_randomness(self):
        """Test that jitter adds random delay"""
        call_times = []

        @retry(max_retries=2, backoff_factor=1.0, jitter=True)
        def jitter_test():
            call_times.append(time.time())
            raise RuntimeError("test")

        with pytest.raises(RuntimeError):
            jitter_test()

        # Check that delays are not exactly 1 second
        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
        assert delays[0] > 1.0  # Should have jitter added
        assert delays[1] > 1.0  # Should have jitter added

    def test_no_jitter(self):
        """Test that jitter can be disabled"""
        call_times = []

        @retry(max_retries=2, backoff_factor=1.0, jitter=False)
        def no_jitter_test():
            call_times.append(time.time())
            raise RuntimeError("test")

        with pytest.raises(RuntimeError):
            no_jitter_test()

        # Delays should be closer to exact values without jitter
        delays = [call_times[i] - call_times[i - 1] for i in range(1, len(call_times))]
        assert abs(delays[0] - 1.0) < 0.1  # Should be close to 1 second
        assert abs(delays[1] - 1.0) < 0.1  # Should be close to 1 second

class TestErrorHandling:
    """Test error handling utilities"""

    def test_handle_retryable_errors_success(self):
        """Test successful execution"""

        def successful_func():
            return "success"

        result = handle_retryable_errors(successful_func)
        assert result == "success"

    def test_handle_retryable_errors_retryable(self):
        """Test retryable error handling"""

        def failing_func():
            raise Timeout("timeout")

        with pytest.raises(RetryableError):
            handle_retryable_errors(failing_func)

    def test_handle_retryable_errors_fatal(self):
        """Test fatal error handling"""

        def fatal_func():
            raise ValueError("fatal")

        with pytest.raises(ValueError):
            handle_retryable_errors(fatal_func)

if __name__ == "__main__":
    pytest.main([__file__])
