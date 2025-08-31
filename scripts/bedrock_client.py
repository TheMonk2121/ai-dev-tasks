#!/usr/bin/env python3
"""
AWS Bedrock Client Integration Module
Provides BedrockClient class with Claude 3.5 Sonnet integration, retry logic, and cost tracking
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BedrockUsage:
    """Track Bedrock API usage for cost monitoring."""

    input_tokens: int = 0
    output_tokens: int = 0
    request_count: int = 0
    total_cost: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "request_count": self.request_count,
            "total_cost": self.total_cost,
            "timestamp": self.timestamp,
        }


class BedrockClient:
    """
    AWS Bedrock client with Claude 3.5 Sonnet integration.

    Features:
    - Retry logic with exponential backoff
    - Token usage tracking for cost monitoring
    - Structured JSON prompt support
    - Timeout and error handling
    - Rate limiting compliance
    """

    # Claude 3.5 Sonnet pricing (as of 2024)
    INPUT_TOKEN_COST = 3.00 / 1_000_000  # $3.00 per 1M input tokens
    OUTPUT_TOKEN_COST = 15.00 / 1_000_000  # $15.00 per 1M output tokens

    def __init__(
        self,
        region_name: str = "us-east-1",
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        max_retries: int = 3,
        timeout: int = 30,
        usage_log_file: Optional[str] = None,
    ):
        """
        Initialize Bedrock client.

        Args:
            region_name: AWS region for Bedrock service
            model_id: Claude 3.5 Sonnet model identifier
            max_retries: Maximum retry attempts for failed requests
            timeout: Request timeout in seconds
            usage_log_file: Path to usage log file for cost tracking
        """
        self.region_name = region_name
        self.model_id = model_id
        self.max_retries = max_retries
        self.timeout = timeout
        self.usage_log_file = usage_log_file or "metrics/bedrock_usage.json"

        # Initialize clients
        self._bedrock_runtime = None
        self._bedrock = None

        # Usage tracking
        self.session_usage = BedrockUsage()

        logger.info(f"BedrockClient initialized: {model_id} in {region_name}")

    @property
    def bedrock_runtime(self):
        """Lazy initialization of Bedrock Runtime client."""
        if self._bedrock_runtime is None:
            try:
                self._bedrock_runtime = boto3.client("bedrock-runtime", region_name=self.region_name)
                logger.info("Bedrock Runtime client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock Runtime client: {e}")
                raise
        return self._bedrock_runtime

    @property
    def bedrock(self):
        """Lazy initialization of Bedrock client."""
        if self._bedrock is None:
            try:
                self._bedrock = boto3.client("bedrock", region_name=self.region_name)
                logger.info("Bedrock client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {e}")
                raise
        return self._bedrock

    def test_connection(self) -> bool:
        """
        Test connection to Bedrock service.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test basic Bedrock access
            response = self.bedrock.list_foundation_models()
            models = response.get("modelSummaries", [])

            # Check if our target model is available
            model_available = any(model.get("modelId") == self.model_id for model in models)

            if model_available:
                logger.info(f"✅ Model {self.model_id} is available")
                return True
            else:
                logger.warning(f"❌ Model {self.model_id} not found in available models")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def invoke_model(
        self, prompt: str, max_tokens: int = 1000, temperature: float = 0.1, system_prompt: Optional[str] = None
    ) -> Tuple[str, BedrockUsage]:
        """
        Invoke Claude 3.5 Sonnet model with retry logic.

        Args:
            prompt: User prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            system_prompt: Optional system prompt

        Returns:
            Tuple of (response_text, usage_info)

        Raises:
            Exception: If all retry attempts fail
        """
        # Prepare request body
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Invoking model (attempt {attempt + 1}/{self.max_retries + 1})")

                response = self.bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    contentType="application/json",
                    accept="application/json",
                )

                # Parse response
                response_body = json.loads(response["body"].read())

                # Extract text and usage
                content = response_body.get("content", [])
                if content and len(content) > 0:
                    response_text = content[0].get("text", "")
                else:
                    response_text = ""

                # Track usage
                usage_info = self._extract_usage(response_body)
                self._update_usage(usage_info)

                logger.info(
                    f"✅ Model invocation successful (tokens: {usage_info.input_tokens}→{usage_info.output_tokens})"
                )
                return response_text, usage_info

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "Unknown")

                if error_code == "ThrottlingException":
                    # Rate limiting - wait and retry
                    wait_time = (2**attempt) + (time.time() % 1)  # Exponential backoff with jitter
                    logger.warning(f"Rate limited, waiting {wait_time:.2f}s before retry")
                    time.sleep(wait_time)
                    continue
                elif error_code == "ValidationException":
                    # Don't retry validation errors
                    logger.error(f"Validation error: {e}")
                    raise
                else:
                    # Other client errors - retry with backoff
                    if attempt < self.max_retries:
                        wait_time = (2**attempt) + (time.time() % 1)
                        logger.warning(f"Client error {error_code}, retrying in {wait_time:.2f}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for client error: {e}")
                        raise

            except Exception as e:
                if attempt < self.max_retries:
                    wait_time = (2**attempt) + (time.time() % 1)
                    logger.warning(f"Unexpected error, retrying in {wait_time:.2f}s: {e}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Max retries exceeded for error: {e}")
                    raise

        # Should never reach here due to raise in loop
        raise Exception("All retry attempts failed")

    def invoke_with_json_prompt(
        self, prompt: str, max_tokens: int = 150, temperature: float = 0.1
    ) -> Tuple[str, BedrockUsage]:
        """
        Invoke model with structured JSON prompt for reliable parsing.

        Args:
            prompt: Base prompt text
            max_tokens: Maximum tokens (increased for JSON responses)
            temperature: Sampling temperature

        Returns:
            Tuple of (response_text, usage_info)
        """
        json_system_prompt = (
            "You are a helpful assistant that always responds with valid JSON. "
            "Structure your responses as requested in the prompt. "
            "Ensure all JSON is properly formatted and parseable."
        )

        json_prompt = f"{prompt}\n\nRespond with valid JSON only."

        return self.invoke_model(
            prompt=json_prompt, max_tokens=max_tokens, temperature=temperature, system_prompt=json_system_prompt
        )

    def _extract_usage(self, response_body: Dict[str, Any]) -> BedrockUsage:
        """Extract usage information from response."""
        usage = response_body.get("usage", {})

        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        # Calculate cost
        input_cost = input_tokens * self.INPUT_TOKEN_COST
        output_cost = output_tokens * self.OUTPUT_TOKEN_COST
        total_cost = input_cost + output_cost

        return BedrockUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            request_count=1,
            total_cost=total_cost,
            timestamp=datetime.now().isoformat(),
        )

    def _update_usage(self, usage: BedrockUsage):
        """Update session usage tracking."""
        self.session_usage.input_tokens += usage.input_tokens
        self.session_usage.output_tokens += usage.output_tokens
        self.session_usage.request_count += usage.request_count
        self.session_usage.total_cost += usage.total_cost
        self.session_usage.timestamp = usage.timestamp

        # Log to file if configured
        if self.usage_log_file:
            self._log_usage(usage)

    def _log_usage(self, usage: BedrockUsage):
        """Log usage to file for cost monitoring."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.usage_log_file), exist_ok=True)

            # Load existing usage data
            usage_data = []
            if os.path.exists(self.usage_log_file):
                try:
                    with open(self.usage_log_file, "r") as f:
                        usage_data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    usage_data = []

            # Append new usage
            usage_data.append(usage.to_dict())

            # Write back to file
            with open(self.usage_log_file, "w") as f:
                json.dump(usage_data, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to log usage: {e}")

    def get_session_usage(self) -> BedrockUsage:
        """Get current session usage statistics."""
        return self.session_usage

    def get_total_usage(self) -> BedrockUsage:
        """Get total usage from log file."""
        if not os.path.exists(self.usage_log_file):
            return BedrockUsage()

        try:
            with open(self.usage_log_file, "r") as f:
                usage_data = json.load(f)

            total_usage = BedrockUsage()
            for entry in usage_data:
                total_usage.input_tokens += entry.get("input_tokens", 0)
                total_usage.output_tokens += entry.get("output_tokens", 0)
                total_usage.request_count += entry.get("request_count", 0)
                total_usage.total_cost += entry.get("total_cost", 0.0)

            return total_usage

        except Exception as e:
            logger.warning(f"Failed to read usage log: {e}")
            return BedrockUsage()


def main():
    """Test the BedrockClient functionality."""
    print("🧪 Testing BedrockClient...")

    try:
        # Initialize client
        client = BedrockClient()

        # Test connection
        if not client.test_connection():
            print("❌ Connection test failed")
            return 1

        # Test simple invocation
        print("\n🚀 Testing model invocation...")
        response, usage = client.invoke_model(prompt="What is 2+2? Respond briefly.", max_tokens=50)

        print(f"✅ Response: {response}")
        print(f"💰 Usage: {usage.input_tokens} input, {usage.output_tokens} output, ${usage.total_cost:.4f}")

        # Test JSON prompt
        print("\n📋 Testing JSON prompt...")
        json_response, json_usage = client.invoke_with_json_prompt(
            prompt='Calculate 5+5 and respond in this format: {"result": number, "explanation": "brief explanation"}',
            max_tokens=100,
        )

        print(f"✅ JSON Response: {json_response}")
        print(
            f"💰 JSON Usage: {json_usage.input_tokens} input, {json_usage.output_tokens} output, ${json_usage.total_cost:.4f}"
        )

        # Show session usage
        session_usage = client.get_session_usage()
        print(f"\n📊 Session Total: ${session_usage.total_cost:.4f} ({session_usage.request_count} requests)")

        return 0

    except NoCredentialsError:
        print("❌ AWS credentials not configured")
        print("💡 Run: python3 scripts/bedrock_setup_guide.py")
        return 1
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
