#!/usr/bin/env python3
"""
Tests for the Model-Specific Error Handling System
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from utils.model_specific_handling import (
    ModelSpecificHandler,
    handle_model_error,
    get_model_config,
    list_available_models,
    ModelConfig,
    ModelErrorResponse,
)


class TestModelSpecificHandling:
    """Test cases for model-specific error handling"""

    def test_model_handler_initialization(self):
        """Test that the model handler initializes correctly"""
        handler = ModelSpecificHandler()
        assert handler is not None
        assert len(handler.model_configs) > 0
        assert isinstance(handler.error_history, list)

    def test_mistral_context_window_error(self):
        """Test handling of Mistral context window errors"""
        error_message = "Context window exceeded for mistral-7b-instruct"
        response = handle_model_error(error_message, "mistral-7b-instruct")

        assert response is not None
        assert "chunking" in response.recovery_action.lower()
        assert response.confidence > 0.8
        assert "minutes" in response.estimated_time

    def test_yi_coder_model_not_found(self):
        """Test handling of Yi-Coder model not found errors"""
        error_message = "Model not found: yi-coder-9b-chat"
        response = handle_model_error(error_message, "yi-coder-9b-chat")

        assert response is not None
        assert response.fallback_model is not None
        assert "codellama" in response.fallback_model.lower()

    def test_gpt_timeout_error(self):
        """Test handling of GPT timeout errors"""
        error_message = "Request timeout for gpt-3.5-turbo"
        response = handle_model_error(error_message, "gpt-3.5-turbo")

        assert response is not None
        assert response.adjusted_parameters.get("timeout_seconds") is not None
        assert response.adjusted_parameters.get("use_streaming") is True

    def test_gpt4_rate_limit_error(self):
        """Test handling of GPT-4 rate limit errors"""
        error_message = "Rate limit exceeded for gpt-4"
        response = handle_model_error(error_message, "gpt-4")

        assert response is not None
        assert "rate limiting" in response.recovery_action.lower()
        assert response.adjusted_parameters.get("retry_delay") == 60
        assert response.adjusted_parameters.get("use_queue") is True

    def test_claude_authentication_error(self):
        """Test handling of Claude authentication errors"""
        error_message = "Authentication failed for claude-3-sonnet"
        response = handle_model_error(error_message, "claude-3-sonnet")

        assert response is not None
        assert response.confidence > 0.8
        assert "minutes" in response.estimated_time

    def test_unknown_model_error(self):
        """Test handling of errors for unknown models"""
        error_message = "Some error occurred"
        response = handle_model_error(error_message, "unknown-model")

        assert response is not None
        # Should use default configuration
        assert "configuration" in response.recovery_action.lower()

    def test_unknown_error_type(self):
        """Test handling of unknown error types"""
        error_message = "Some completely unknown error"
        response = handle_model_error(error_message, "gpt-3.5-turbo")

        assert response is not None
        assert response.confidence < 0.5  # Lower confidence for unknown errors

    def test_model_config_retrieval(self):
        """Test retrieving model configurations"""
        config = get_model_config("mistral-7b-instruct")
        assert config is not None
        assert config.model_id == "mistral-7b-instruct"
        assert config.max_context_length == 4096
        assert config.timeout_seconds == 90
        assert len(config.fallback_models) > 0
        assert len(config.error_handling) > 0

    def test_available_models_list(self):
        """Test listing available models"""
        models = list_available_models()
        assert len(models) > 0
        assert "mistral-7b-instruct" in models
        assert "yi-coder-9b-chat" in models
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models
        assert "claude-3-sonnet" in models

    def test_error_classification(self):
        """Test error classification functionality"""
        handler = ModelSpecificHandler()

        # Test context window errors
        assert handler._classify_error("Context window exceeded") == "context_window_exceeded"
        assert handler._classify_error("Token limit reached") == "context_window_exceeded"

        # Test model not found errors
        assert handler._classify_error("Model not found") == "model_not_found"
        assert handler._classify_error("Model does not exist") == "model_not_found"

        # Test timeout errors
        assert handler._classify_error("Request timeout") == "timeout"
        assert handler._classify_error("Timed out") == "timeout"

        # Test rate limit errors
        assert handler._classify_error("Rate limit exceeded") == "rate_limit"
        assert handler._classify_error("HTTP 429") == "rate_limit"

        # Test authentication errors
        assert handler._classify_error("Authentication failed") == "authentication_error"
        assert handler._classify_error("Invalid key") == "authentication_error"

        # Test quota errors
        assert handler._classify_error("Quota exceeded") == "quota_exceeded"
        assert handler._classify_error("Billing error") == "quota_exceeded"

        # Test unknown errors
        assert handler._classify_error("Some random error") == "unknown_error"

    def test_fallback_model_selection(self):
        """Test fallback model selection"""
        handler = ModelSpecificHandler()
        config = handler.model_configs["mistral-7b-instruct"]

        # Test model not found scenario
        fallback = handler._select_fallback_model(config, "model_not_found")
        assert fallback is not None
        assert fallback in config.fallback_models

        # Test with context allowing fallback
        context = {"allow_fallback": True}
        fallback = handler._select_fallback_model(config, "timeout", context)
        assert fallback is not None

        # Test without context allowing fallback
        fallback = handler._select_fallback_model(config, "timeout", {})
        assert fallback is None

    def test_parameter_adjustment(self):
        """Test parameter adjustment based on error type"""
        handler = ModelSpecificHandler()
        config = handler.model_configs["gpt-3.5-turbo"]

        # Test context window exceeded
        adjustments = handler._adjust_parameters(config, "context_window_exceeded")
        assert adjustments.get("max_tokens") == config.max_tokens_per_request // 2
        assert adjustments.get("chunk_input") is True
        assert adjustments.get("use_streaming") is True

        # Test timeout
        adjustments = handler._adjust_parameters(config, "timeout")
        assert adjustments.get("timeout_seconds") == config.timeout_seconds * 2
        assert adjustments.get("max_tokens") == config.max_tokens_per_request // 2

        # Test rate limit
        adjustments = handler._adjust_parameters(config, "rate_limit")
        assert adjustments.get("retry_delay") == 60
        assert adjustments.get("max_retries") == 3
        assert adjustments.get("use_queue") is True

    def test_confidence_calculation(self):
        """Test confidence calculation for different error types"""
        handler = ModelSpecificHandler()
        config = handler.model_configs["gpt-3.5-turbo"]

        # Test high confidence errors
        assert handler._calculate_confidence("context_window_exceeded", config) == 0.9
        assert handler._calculate_confidence("authentication_error", config) == 0.9

        # Test medium confidence errors
        assert handler._calculate_confidence("timeout", config) == 0.7
        assert handler._calculate_confidence("rate_limit", config) == 0.8

        # Test low confidence errors
        assert handler._calculate_confidence("unknown_error", config) == 0.3

    def test_recovery_time_estimation(self):
        """Test recovery time estimation"""
        handler = ModelSpecificHandler()
        config = handler.model_configs["gpt-3.5-turbo"]

        # Test various error types
        assert "minutes" in handler._estimate_recovery_time("context_window_exceeded", config)
        assert "minutes" in handler._estimate_recovery_time("model_not_found", config)
        assert "minutes" in handler._estimate_recovery_time("timeout", config)
        assert "minutes" in handler._estimate_recovery_time("rate_limit", config)
        assert "minutes" in handler._estimate_recovery_time("unknown_error", config)

    def test_model_config_update(self):
        """Test updating model configurations"""
        handler = ModelSpecificHandler()

        # Create a new config
        new_config = ModelConfig(
            model_id="test-model",
            max_context_length=2048,
            max_tokens_per_request=1024,
            timeout_seconds=60,
            retry_strategy="exponential_backoff",
            fallback_models=["gpt-3.5-turbo"],
            error_handling={"test_error": "Test recovery action"},
        )

        # Update the config
        handler.update_model_config("test-model", new_config)

        # Verify the update
        updated_config = handler.get_model_config("test-model")
        assert updated_config is not None
        assert updated_config.model_id == "test-model"
        assert updated_config.max_context_length == 2048


if __name__ == "__main__":
    pytest.main([__file__])
