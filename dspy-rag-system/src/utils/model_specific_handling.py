#!/usr/bin/env python3
"""
Model-Specific Error Handling System

This module provides model-specific error handling and recovery strategies
for different AI models in the DSPy RAG system.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    model_id: str
    max_context_length: int
    max_tokens_per_request: int
    timeout_seconds: int
    retry_strategy: str
    fallback_models: List[str]
    error_handling: Dict[str, str]

@dataclass
class ModelErrorResponse:
    """Response from model-specific error handling"""
    recovery_action: str
    fallback_model: Optional[str]
    adjusted_parameters: Dict[str, Any]
    confidence: float
    estimated_time: str

class ModelSpecificHandler:
    """Handles model-specific errors and provides recovery strategies"""

    def __init__(self):
        self.model_configs = self._load_model_configs()
        self.error_history = []

    def _load_model_configs(self) -> Dict[str, ModelConfig]:
        """Load model-specific configurations"""
        configs = {
            "mistral-7b-instruct": ModelConfig(
                model_id="mistral-7b-instruct",
                max_context_length=4096,
                max_tokens_per_request=2048,
                timeout_seconds=90,
                retry_strategy="exponential_backoff",
                fallback_models=["llama2-7b-chat", "gpt-3.5-turbo"],
                error_handling={
                    "context_window_exceeded": "Reduce input length or implement chunking",
                    "model_not_found": "Use fallback model",
                    "timeout": "Increase timeout or retry with smaller context",
                    "rate_limit": "Implement exponential backoff"
                }
            ),
            "yi-coder-9b-chat": ModelConfig(
                model_id="yi-coder-9b-chat",
                max_context_length=8192,
                max_tokens_per_request=4096,
                timeout_seconds=120,
                retry_strategy="exponential_backoff",
                fallback_models=["codellama-7b-instruct", "gpt-4"],
                error_handling={
                    "context_window_exceeded": "Split code into smaller chunks",
                    "model_not_found": "Use CodeLlama fallback",
                    "timeout": "Reduce code complexity or use smaller model",
                    "rate_limit": "Implement request queuing"
                }
            ),
            "gpt-3.5-turbo": ModelConfig(
                model_id="gpt-3.5-turbo",
                max_context_length=4096,
                max_tokens_per_request=2048,
                timeout_seconds=60,
                retry_strategy="linear_backoff",
                fallback_models=["gpt-4", "claude-3-sonnet"],
                error_handling={
                    "context_window_exceeded": "Truncate input or use streaming",
                    "model_not_found": "Use GPT-4 fallback",
                    "timeout": "Reduce request size",
                    "rate_limit": "Implement rate limiting"
                }
            ),
            "gpt-4": ModelConfig(
                model_id="gpt-4",
                max_context_length=8192,
                max_tokens_per_request=4096,
                timeout_seconds=120,
                retry_strategy="exponential_backoff",
                fallback_models=["gpt-3.5-turbo", "claude-3-sonnet"],
                error_handling={
                    "context_window_exceeded": "Use function calling or chunking",
                    "model_not_found": "Use GPT-3.5 fallback",
                    "timeout": "Optimize prompt or reduce complexity",
                    "rate_limit": "Implement sophisticated rate limiting"
                }
            ),
            "claude-3-sonnet": ModelConfig(
                model_id="claude-3-sonnet",
                max_context_length=200000,
                max_tokens_per_request=4096,
                timeout_seconds=300,
                retry_strategy="exponential_backoff",
                fallback_models=["gpt-4", "gpt-3.5-turbo"],
                error_handling={
                    "context_window_exceeded": "Use Claude's large context window",
                    "model_not_found": "Use GPT-4 fallback",
                    "timeout": "Reduce input size or complexity",
                    "rate_limit": "Implement Claude-specific rate limiting"
                }
            )
        }

        # Load additional model configs from file if available
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'model_configs.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    custom_configs = json.load(f)
                    for config_data in custom_configs:
                        config = ModelConfig(**config_data)
                        configs[config.model_id] = config
        except Exception as e:
            logger.warning(f"Could not load custom model configs: {e}")

        return configs

    def handle_model_error(self, error_message: str, model_id: str,
                          context: Dict[str, Any] = None) -> ModelErrorResponse:
        """
        Handle model-specific errors and provide recovery strategies
        
        Args:
            error_message: The error message
            model_id: The model that caused the error
            context: Optional context information
            
        Returns:
            ModelErrorResponse with recovery strategy
        """
        # Get model configuration
        model_config = self.model_configs.get(model_id)
        if not model_config:
            # Use default configuration
            model_config = self.model_configs.get("gpt-3.5-turbo")

        # Determine error type
        error_type = self._classify_error(error_message)

        # Get recovery action
        recovery_action = model_config.error_handling.get(error_type, "Check model configuration")

        # Determine fallback model
        fallback_model = self._select_fallback_model(model_config, error_type, context)

        # Adjust parameters based on error
        adjusted_parameters = self._adjust_parameters(model_config, error_type, context)

        # Calculate confidence
        confidence = self._calculate_confidence(error_type, model_config)

        # Estimate recovery time
        estimated_time = self._estimate_recovery_time(error_type, model_config)

        # Log error handling
        logger.info(f"Model-specific error handling: {model_id} -> {error_type}")
        logger.info(f"Recovery action: {recovery_action}")
        if fallback_model:
            logger.info(f"Fallback model: {fallback_model}")

        return ModelErrorResponse(
            recovery_action=recovery_action,
            fallback_model=fallback_model,
            adjusted_parameters=adjusted_parameters,
            confidence=confidence,
            estimated_time=estimated_time
        )

    def _classify_error(self, error_message: str) -> str:
        """Classify the type of error based on the message"""
        error_message_lower = error_message.lower()

        if any(phrase in error_message_lower for phrase in ["context window", "token limit", "too many tokens"]):
            return "context_window_exceeded"
        elif any(phrase in error_message_lower for phrase in ["model not found", "model does not exist", "model unavailable"]):
            return "model_not_found"
        elif any(phrase in error_message_lower for phrase in ["timeout", "timed out", "request timeout"]):
            return "timeout"
        elif any(phrase in error_message_lower for phrase in ["rate limit", "too many requests", "429"]):
            return "rate_limit"
        elif any(phrase in error_message_lower for phrase in ["authentication", "auth", "invalid key"]):
            return "authentication_error"
        elif any(phrase in error_message_lower for phrase in ["quota", "billing", "payment"]):
            return "quota_exceeded"
        else:
            return "unknown_error"

    def _select_fallback_model(self, model_config: ModelConfig, error_type: str,
                              context: Dict[str, Any] = None) -> Optional[str]:
        """Select an appropriate fallback model"""
        if error_type == "model_not_found" and model_config.fallback_models:
            # Return the first available fallback
            return model_config.fallback_models[0]

        # For other errors, only suggest fallback if context indicates it's appropriate
        if context and context.get('allow_fallback', False):
            return model_config.fallback_models[0] if model_config.fallback_models else None

        return None

    def _adjust_parameters(self, model_config: ModelConfig, error_type: str,
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Adjust model parameters based on error type"""
        adjustments = {}

        if error_type == "context_window_exceeded":
            adjustments["max_tokens"] = model_config.max_tokens_per_request // 2
            adjustments["chunk_input"] = True
            adjustments["use_streaming"] = True

        elif error_type == "timeout":
            adjustments["timeout_seconds"] = model_config.timeout_seconds * 2
            adjustments["max_tokens"] = model_config.max_tokens_per_request // 2
            adjustments["use_streaming"] = True

        elif error_type == "rate_limit":
            adjustments["retry_delay"] = 60  # 1 minute delay
            adjustments["max_retries"] = 3
            adjustments["use_queue"] = True

        return adjustments

    def _calculate_confidence(self, error_type: str, model_config: ModelConfig) -> float:
        """Calculate confidence in the recovery strategy"""
        # Higher confidence for well-known error types
        confidence_map = {
            "context_window_exceeded": 0.9,
            "model_not_found": 0.8,
            "timeout": 0.7,
            "rate_limit": 0.8,
            "authentication_error": 0.9,
            "quota_exceeded": 0.9,
            "unknown_error": 0.3
        }

        return confidence_map.get(error_type, 0.5)

    def _estimate_recovery_time(self, error_type: str, model_config: ModelConfig) -> str:
        """Estimate recovery time based on error type"""
        time_map = {
            "context_window_exceeded": "5-15 minutes",
            "model_not_found": "1-5 minutes",
            "timeout": "10-30 minutes",
            "rate_limit": "15-45 minutes",
            "authentication_error": "5-20 minutes",
            "quota_exceeded": "30-60 minutes",
            "unknown_error": "15-60 minutes"
        }

        return time_map.get(error_type, "15-30 minutes")

    def get_model_config(self, model_id: str) -> Optional[ModelConfig]:
        """Get configuration for a specific model"""
        return self.model_configs.get(model_id)

    def list_available_models(self) -> List[str]:
        """List all available model configurations"""
        return list(self.model_configs.keys())

    def update_model_config(self, model_id: str, config: ModelConfig):
        """Update model configuration"""
        self.model_configs[model_id] = config
        logger.info(f"Updated configuration for model: {model_id}")

# Global instance
model_handler = ModelSpecificHandler()

def handle_model_error(error_message: str, model_id: str,
                      context: Dict[str, Any] = None) -> ModelErrorResponse:
    """
    Convenience function to handle model-specific errors
    
    Args:
        error_message: The error message
        model_id: The model that caused the error
        context: Optional context information
        
    Returns:
        ModelErrorResponse with recovery strategy
    """
    return model_handler.handle_model_error(error_message, model_id, context)

def get_model_config(model_id: str) -> Optional[ModelConfig]:
    """Get configuration for a specific model"""
    return model_handler.get_model_config(model_id)

def list_available_models() -> List[str]:
    """List all available model configurations"""
    return model_handler.list_available_models()

def update_model_config(model_id: str, config: ModelConfig):
    """Update model configuration"""
    model_handler.update_model_config(model_id, config)
