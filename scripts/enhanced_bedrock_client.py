#!/usr/bin/env python3
"""
Enhanced AWS Bedrock Client with Multi-Key Load Balancing
Implements advanced rate limiting, multi-key rotation, and adaptive retry logic
to optimize RAGChecker performance and handle API rate limits effectively.
"""

import asyncio
import json
import logging
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

# Import BedrockUsage from the standard client to avoid duplication
try:
    from scripts.bedrock_client import BedrockUsage
except ImportError:
    # Fallback for when running from different directory
    import os
    import sys

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.bedrock_client import BedrockUsage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeyStatus(Enum):
    """Status of an API key for load balancing decisions."""

    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    COOLDOWN = "cooldown"


@dataclass
class KeyMetrics:
    """Track performance metrics for each API key."""

    key_id: str
    region: str
    status: KeyStatus = KeyStatus.ACTIVE
    request_count: int = 0
    error_count: int = 0
    rate_limit_count: int = 0
    total_tokens: int = 0
    last_request_time: float = 0.0
    cooldown_until: float = 0.0
    avg_response_time: float = 0.0
    success_rate: float = 1.0

    def update_success(self, response_time: float, tokens: int):
        """Update metrics after successful request."""
        self.request_count += 1
        self.total_tokens += tokens
        self.last_request_time = time.time()

        # Update average response time (exponential moving average)
        alpha = 0.1
        self.avg_response_time = alpha * response_time + (1 - alpha) * self.avg_response_time

        # Update success rate
        self.success_rate = (self.request_count - self.error_count) / self.request_count

        # Reset status if was in error/cooldown
        if self.status in [KeyStatus.ERROR, KeyStatus.COOLDOWN]:
            self.status = KeyStatus.ACTIVE

    def update_error(self, error_type: str):
        """Update metrics after error."""
        self.error_count += 1
        if error_type == "ThrottlingException":
            self.rate_limit_count += 1
            self.status = KeyStatus.RATE_LIMITED
            # Set cooldown based on error count
            cooldown_duration = min(60 * (2**self.rate_limit_count), 3600)  # Max 1 hour
            self.cooldown_until = time.time() + cooldown_duration
        else:
            self.status = KeyStatus.ERROR
            # Shorter cooldown for other errors
            self.cooldown_until = time.time() + 30

    def is_available(self) -> bool:
        """Check if key is available for requests."""
        if self.status == KeyStatus.COOLDOWN:
            return time.time() >= self.cooldown_until
        return self.status == KeyStatus.ACTIVE

    def get_health_score(self) -> float:
        """Calculate health score for load balancing (higher is better)."""
        if not self.is_available():
            return 0.0

        # Base score from success rate
        score = self.success_rate

        # Bonus for low error rate
        if self.error_count == 0:
            score += 0.2

        # Bonus for recent activity (avoid stale keys)
        time_since_last = time.time() - self.last_request_time
        if time_since_last < 300:  # 5 minutes
            score += 0.1

        # Penalty for high rate limiting
        if self.rate_limit_count > 0:
            score -= min(self.rate_limit_count * 0.1, 0.5)

        return max(0.0, min(1.0, score))


# BedrockUsage imported from scripts.bedrock_client to avoid duplication


class MultiKeyLoadBalancer:
    """
    Intelligent load balancer for multiple Bedrock API keys.
    Implements health-based routing and adaptive rate limiting.
    """

    def __init__(self, api_keys: list[dict[str, str]]):
        """
        Initialize load balancer with API key configurations.

        Args:
            api_keys: List of dicts with 'key_id', 'region', 'access_key', 'secret_key'
        """
        self.api_keys = api_keys
        self.key_metrics: dict[str, KeyMetrics] = {}
        self._lock = asyncio.Lock()

        # Initialize metrics for each key
        for key_config in api_keys:
            key_id = key_config["key_id"]
            self.key_metrics[key_id] = KeyMetrics(key_id=key_id, region=key_config["region"])

        logger.info(f"MultiKeyLoadBalancer initialized with {len(api_keys)} keys")

    async def get_best_key(self) -> tuple[str, dict[str, str]]:
        """Get the healthiest available API key."""
        async with self._lock:
            available_keys = [
                (key_config["key_id"], key_config)
                for key_config in self.api_keys
                if self.key_metrics[key_config["key_id"]].is_available()
            ]

            if not available_keys:
                # All keys are in cooldown, wait for the earliest one
                earliest_key = min(self.key_metrics.values(), key=lambda k: k.cooldown_until)
                wait_time = earliest_key.cooldown_until - time.time()
                if wait_time > 0:
                    logger.warning(f"All keys in cooldown, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    return await self.get_best_key()

            # Sort by health score and select the best
            available_keys.sort(key=lambda x: self.key_metrics[x[0]].get_health_score(), reverse=True)

            best_key_id, best_config = available_keys[0]
            logger.debug(f"Selected key {best_key_id} (score: {self.key_metrics[best_key_id].get_health_score():.3f})")
            return best_key_id, best_config

    async def update_key_metrics(
        self, key_id: str, success: bool, response_time: float = 0.0, tokens: int = 0, error_type: str = ""
    ):
        """Update metrics for a key after request completion."""
        async with self._lock:
            if key_id in self.key_metrics:
                if success:
                    self.key_metrics[key_id].update_success(response_time, tokens)
                else:
                    self.key_metrics[key_id].update_error(error_type)

    def get_status_summary(self) -> dict[str, Any]:
        """Get summary of all key statuses for monitoring."""
        return {
            key_id: {
                "status": metrics.status.value,
                "request_count": metrics.request_count,
                "error_count": metrics.error_count,
                "rate_limit_count": metrics.rate_limit_count,
                "success_rate": metrics.success_rate,
                "health_score": metrics.get_health_score(),
                "cooldown_remaining": max(0, metrics.cooldown_until - time.time()),
            }
            for key_id, metrics in self.key_metrics.items()
        }


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts based on API response patterns.
    Implements exponential backoff with jitter and circuit breaker patterns.
    """

    def __init__(self, base_rps: float = 0.5, max_rps: float = 2.0):
        self.base_rps = base_rps
        self.max_rps = max_rps
        self.current_rps = base_rps
        self.min_interval = 1.0 / max_rps
        self._last_request = 0.0
        self._lock = asyncio.Lock()

        # Circuit breaker state
        self.failure_count = 0
        self.success_count = 0
        self.circuit_open = False
        self.circuit_open_until = 0.0

        # Adaptive parameters
        self.success_threshold = 10
        self.failure_threshold = 3
        self.circuit_timeout = 60  # seconds

    async def acquire(self) -> float:
        """Acquire rate limit slot with adaptive timing."""
        async with self._lock:
            now = time.time()

            # Check circuit breaker
            if self.circuit_open:
                if now < self.circuit_open_until:
                    wait_time = self.circuit_open_until - now
                    logger.warning(f"Circuit breaker open, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                else:
                    self.circuit_open = False
                    logger.info("Circuit breaker closed, resuming normal operation")

            # Rate limiting
            wait_time = max(0.0, (self._last_request + self.min_interval) - now)
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            self._last_request = time.time()
            return self._last_request

    def record_success(self):
        """Record successful request for adaptive adjustment."""
        self.success_count += 1
        self.failure_count = 0

        # Gradually increase rate if consistently successful
        if self.success_count >= self.success_threshold:
            self.current_rps = min(self.max_rps, self.current_rps * 1.1)
            self.min_interval = 1.0 / self.current_rps
            self.success_count = 0
            logger.debug(f"Rate increased to {self.current_rps:.2f} RPS")

    def record_failure(self):
        """Record failed request for adaptive adjustment."""
        self.failure_count += 1
        self.success_count = 0

        # Decrease rate on failures
        self.current_rps = max(self.base_rps, self.current_rps * 0.8)
        self.min_interval = 1.0 / self.current_rps

        # Open circuit breaker if too many failures
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            self.circuit_open_until = time.time() + self.circuit_timeout
            logger.warning(f"Circuit breaker opened for {self.circuit_timeout}s due to {self.failure_count} failures")

    def get_status(self) -> dict[str, Any]:
        """Get current rate limiter status."""
        return {
            "current_rps": self.current_rps,
            "base_rps": self.base_rps,
            "max_rps": self.max_rps,
            "circuit_open": self.circuit_open,
            "circuit_open_until": self.circuit_open_until,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
        }


class EnhancedBedrockClient:
    """
    Enhanced Bedrock client with multi-key load balancing and adaptive rate limiting.

    Features:
    - Multi-key rotation for higher throughput
    - Health-based load balancing
    - Adaptive rate limiting with circuit breaker
    - Intelligent retry logic with exponential backoff
    - Comprehensive monitoring and metrics
    """

    # Claude 3.5 Sonnet pricing (as of 2024)
    INPUT_TOKEN_COST = 3.00 / 1_000_000  # $3.00 per 1M input tokens
    OUTPUT_TOKEN_COST = 15.00 / 1_000_000  # $15.00 per 1M output tokens

    def __init__(
        self,
        api_keys: list[dict[str, str]] | None = None,
        model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0",
        max_retries: int = 4,
        timeout: int = 300,
        usage_log_file: str | None = None,
    ):
        """
        Initialize enhanced Bedrock client.

        Args:
            api_keys: List of API key configs, or use environment variables
            model_id: Claude model identifier
            max_retries: Maximum retry attempts
            timeout: Request timeout in seconds
            usage_log_file: Path to usage log file
        """
        # Model ID override from environment
        self.model_id = os.getenv("BEDROCK_MODEL_ID", model_id)
        self.max_retries = max_retries
        self.timeout = timeout
        self.connect_timeout = int(os.getenv("BEDROCK_CONNECT_TIMEOUT", "30"))
        self.usage_log_file = usage_log_file or "metrics/enhanced_bedrock_usage.json"

        # Prometheus-style counters for observability
        self.counters = {
            "requests_total": 0,
            "retries_total": 0,
            "throttles_total": 0,
            "errors_total": 0,
            "key_success": {},
            "key_failure": {},
            "latency_sum": 0.0,
            "latency_count": 0,
        }

        # Initialize API keys from environment if not provided
        if api_keys is None:
            api_keys = self._load_api_keys_from_env()

        # Initialize components
        self.load_balancer = MultiKeyLoadBalancer(api_keys)
        self.rate_limiter = AdaptiveRateLimiter(
            base_rps=float(os.getenv("BEDROCK_BASE_RPS", "0.5")), max_rps=float(os.getenv("BEDROCK_MAX_RPS", "2.0"))
        )

        # Usage tracking
        self.session_usage = BedrockUsage()

        logger.info(f"EnhancedBedrockClient initialized with {len(api_keys)} keys")

    def _load_api_keys_from_env(self) -> list[dict[str, str]]:
        """Load API key configurations from environment variables."""
        api_keys = []

        # Check for multiple key configurations
        key_index = 0
        while True:
            # Use traditional AWS access keys (primary method)
            access_key = os.getenv(f"AWS_ACCESS_KEY_ID_{key_index}" if key_index > 0 else "AWS_ACCESS_KEY_ID")
            secret_key = os.getenv(f"AWS_SECRET_ACCESS_KEY_{key_index}" if key_index > 0 else "AWS_SECRET_ACCESS_KEY")
            region = os.getenv(f"AWS_REGION_{key_index}" if key_index > 0 else "AWS_REGION", "us-east-1")

            # Skip placeholder values and empty keys
            if (
                not access_key
                or not secret_key
                or access_key == "your_primary_access_key_here"
                or access_key == "your_secondary_access_key_here"
                or access_key == "your_tertiary_access_key_here"
                or secret_key == "your_primary_secret_key_here"
                or secret_key == "your_secondary_secret_key_here"
                or secret_key == "your_tertiary_secret_key_here"
            ):
                break

            api_keys.append(
                {"key_id": f"key_{key_index}", "access_key": access_key, "secret_key": secret_key, "region": region}
            )
            key_index += 1

        if not api_keys:
            # Fallback to single key
            primary_key = os.getenv("AWS_ACCESS_KEY_ID", "")
            primary_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
            primary_region = os.getenv("AWS_REGION", "us-east-1")

            if primary_key and primary_secret and primary_key != "your_primary_access_key_here":
                api_keys = [
                    {
                        "key_id": "key_0",
                        "access_key": primary_key,
                        "secret_key": primary_secret,
                        "region": primary_region,
                    }
                ]
            else:
                raise ValueError(
                    "No valid AWS credentials found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
                )

        logger.info(f"Loaded {len(api_keys)} API key configurations")
        return api_keys

    async def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ) -> tuple[str, BedrockUsage]:
        """
        Invoke Claude model with enhanced error handling and load balancing.

        Args:
            prompt: User prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt

        Returns:
            Tuple of (response_text, usage_info)
        """
        start_time = time.time()

        for attempt in range(self.max_retries):
            # Initialize variables with defaults (Strategy #1 from web search)
            key_id = "unknown"
            key_config = None

            try:
                # Get rate limit slot
                await self.rate_limiter.acquire()

                # Get best available API key with error handling (Strategy #4 from web search)
                try:
                    key_id, key_config = await self.load_balancer.get_best_key()
                except Exception as e:
                    logger.error(f"Failed to get API key from load balancer: {e}")
                    key_id = "load_balancer_error"
                    raise Exception(f"Load balancer failed: {e}")

                if not key_id or not key_config:
                    logger.error("Failed to get available API key from load balancer")
                    key_id = "no_keys_available"
                    raise Exception("No available API keys")

                # Create Bedrock client for this key
                bedrock_client = self._create_bedrock_client(key_config)

                # Prepare request
                request_body = self._prepare_request_body(prompt, max_tokens, temperature, system_prompt)

                # Make request with explicit content types
                response = bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                )

                # Process response
                response_text, usage_info = self._process_response(response)

                # Update metrics
                response_time = time.time() - start_time
                await self.load_balancer.update_key_metrics(
                    key_id, True, response_time, usage_info.input_tokens + usage_info.output_tokens
                )
                self.rate_limiter.record_success()

                # Update observability counters
                self._update_counters(key_id, True, response_time)

                # Update session usage
                self._update_usage(usage_info)

                logger.info(
                    f"✅ Model invocation successful via {key_id} "
                    f"(tokens: {usage_info.input_tokens}→{usage_info.output_tokens})"
                )

                return response_text, usage_info

            except ClientError as e:
                # Safe error handling with .get() method (Strategy #3 from web search)
                error_code = e.response.get("Error", {}).get("Code", "Unknown")
                response_time = time.time() - start_time

                # Safe key_id access with fallback (Strategy #1 & #3 combined)
                safe_key_id = key_id if key_id and key_id != "unknown" else None
                if safe_key_id:
                    await self.load_balancer.update_key_metrics(safe_key_id, False, response_time, 0, error_code)
                    # Update observability counters
                    self._update_counters(safe_key_id, False, response_time)
                self.rate_limiter.record_failure()

                # Enhanced throttling taxonomy - treat various rate limit messages as retryable
                is_retryable = self._is_retryable_error(error_code, str(e))

                if is_retryable:
                    # Rate limiting - use exponential backoff with jitter
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    logger.warning(f"Rate limited via {key_id or 'unknown'}, waiting {wait_time:.2f}s before retry")
                    await asyncio.sleep(wait_time)
                    continue
                elif error_code == "ValidationException":
                    # Don't retry validation errors
                    logger.error(f"Validation error via {key_id or 'unknown'}: {e}")
                    raise
                else:
                    # Other client errors - retry with backoff
                    if attempt < self.max_retries - 1:
                        wait_time = (2**attempt) + random.uniform(0, 1)
                        logger.warning(
                            f"Client error {error_code} via {key_id or 'unknown'}, retrying in {wait_time:.2f}s"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for client error via {key_id or 'unknown'}: {e}")
                        raise

            except Exception as e:
                response_time = time.time() - start_time
                # Safe key_id access with fallback (Strategy #1 & #3 combined)
                safe_key_id = key_id if key_id and key_id != "unknown" else None
                if safe_key_id:
                    await self.load_balancer.update_key_metrics(safe_key_id, False, response_time, 0, "Unknown")
                    # Update observability counters
                    self._update_counters(safe_key_id, False, response_time)
                self.rate_limiter.record_failure()

                if attempt < self.max_retries - 1:
                    wait_time = (2**attempt) + random.uniform(0, 1)
                    logger.warning(f"Unexpected error via {key_id or 'unknown'}, retrying in {wait_time:.2f}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Max retries exceeded for error via {key_id or 'unknown'}: {e}")
                    raise

        raise Exception("All retry attempts failed")

    def _create_bedrock_client(self, key_config: dict[str, str]):
        """Create Bedrock client for specific API key configuration."""
        config = Config(
            region_name=key_config["region"],
            retries={"max_attempts": 10, "mode": "adaptive"},  # Use AWS adaptive retry mode
            read_timeout=self.timeout,
            connect_timeout=self.connect_timeout,
        )

        # Use traditional AWS access keys
        return boto3.client(
            "bedrock-runtime",
            config=config,
            aws_access_key_id=key_config["access_key"],
            aws_secret_access_key=key_config["secret_key"],
            region_name=key_config["region"],
        )

    def _prepare_request_body(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Prepare request body for Bedrock API with top-level system prompt."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Use top-level system prompt instead of stuffing into messages
        if system_prompt:
            body["system"] = system_prompt

        return body

    def _process_response(self, response) -> tuple[str, BedrockUsage]:
        """Process Bedrock API response and extract text/usage."""
        response_body = json.loads(response["body"].read())

        # Extract text
        content = response_body.get("content", [])
        if content and len(content) > 0:
            response_text = content[0].get("text", "")
        else:
            response_text = ""

        # Extract usage
        usage_info = self._extract_usage(response_body)

        return response_text, usage_info

    def _extract_usage(self, response_body: dict[str, Any]) -> BedrockUsage:
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

    def _update_usage(self, usage_info: BedrockUsage):
        """Update session usage tracking."""
        self.session_usage.input_tokens += usage_info.input_tokens
        self.session_usage.output_tokens += usage_info.output_tokens
        self.session_usage.request_count += usage_info.request_count
        self.session_usage.total_cost += usage_info.total_cost
        self.session_usage.timestamp = datetime.now().isoformat()

    async def invoke_with_json_prompt(
        self, prompt: str, max_tokens: int = 150, temperature: float = 0.0
    ) -> tuple[str, BedrockUsage]:
        """Invoke model with structured JSON prompt for reliable parsing."""
        # JSON mode fast-path: temperature=0.0 by default for structured extraction
        json_system_prompt = (
            "You are a helpful assistant that always responds with valid JSON. "
            "Structure your responses as requested in the prompt. "
            "Ensure all JSON is properly formatted and parseable."
        )

        json_prompt = f"{prompt}\n\nRespond with valid JSON only."

        return await self.invoke_model(
            prompt=json_prompt, max_tokens=max_tokens, temperature=temperature, system_prompt=json_system_prompt
        )

    def _is_retryable_error(self, error_code: str, error_message: str) -> bool:
        """Check if error is retryable based on enhanced throttling taxonomy."""
        retryable_codes = ["ThrottlingException"]
        retryable_messages = ["ModelCurrentlyLoading", "Rate exceeded", "Too Many Requests", "throttle", "rate limit"]

        # Check error code
        if error_code in retryable_codes:
            return True

        # Check error message for retryable patterns
        error_lower = error_message.lower()
        return any(pattern.lower() in error_lower for pattern in retryable_messages)

    def _update_counters(self, key_id: str, success: bool, response_time: float):
        """Update Prometheus-style counters for observability."""
        self.counters["requests_total"] += 1

        if success:
            self.counters["key_success"][key_id] = self.counters["key_success"].get(key_id, 0) + 1
        else:
            self.counters["key_failure"][key_id] = self.counters["key_failure"].get(key_id, 0) + 1
            self.counters["errors_total"] += 1

        # Update latency metrics
        self.counters["latency_sum"] += response_time
        self.counters["latency_count"] += 1

        # Log to rolling file for cost audits
        self._log_usage_to_file(key_id, success, response_time)

    def _log_usage_to_file(self, key_id: str, success: bool, response_time: float):
        """Log usage to rolling file for post-hoc cost audits."""
        try:
            log_file = f"metrics/enhanced_bedrock_usage_{datetime.now().strftime('%Y-%m-%d')}.log"
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, "a") as f:
                timestamp = datetime.now().isoformat()
                status = "SUCCESS" if success else "FAILURE"
                f.write(f"{timestamp},{key_id},{status},{response_time:.3f}\n")

        except Exception as e:
            logger.warning(f"Failed to log usage to file: {e}")

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive status of the enhanced client."""
        # Calculate average latency
        avg_latency = 0.0
        if self.counters["latency_count"] > 0:
            avg_latency = self.counters["latency_sum"] / self.counters["latency_count"]

        return {
            "load_balancer": self.load_balancer.get_status_summary(),
            "rate_limiter": self.rate_limiter.get_status(),
            "session_usage": self.session_usage.to_dict(),
            "total_keys": len(self.load_balancer.api_keys),
            "counters": {
                **self.counters,
                "avg_latency": avg_latency,
            },
        }

    def save_usage_log(self):
        """Save usage log to file."""
        os.makedirs(os.path.dirname(self.usage_log_file), exist_ok=True)

        with open(self.usage_log_file, "w") as f:
            json.dump(self.session_usage.to_dict(), f, indent=2)

        logger.info(f"Usage log saved to {self.usage_log_file}")

    # Sync wrappers for backward compatibility with existing RAGChecker code
    def invoke_model_sync(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ) -> tuple[str, BedrockUsage]:
        """Synchronous wrapper for invoke_model - for RAGChecker compatibility."""
        return asyncio.run(self.invoke_model(prompt, max_tokens, temperature, system_prompt))

    def invoke_with_json_prompt_sync(
        self, prompt: str, max_tokens: int = 150, temperature: float = 0.1
    ) -> tuple[str, BedrockUsage]:
        """Synchronous wrapper for invoke_with_json_prompt - for RAGChecker compatibility."""
        return asyncio.run(self.invoke_with_json_prompt(prompt, max_tokens, temperature))


class SyncBedrockClientWrapper:
    """Synchronous wrapper for EnhancedBedrockClient to work with RAGChecker."""

    def __init__(self, *args, **kwargs):
        self._async_client = EnhancedBedrockClient(*args, **kwargs)

    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.1,
        system_prompt: str | None = None,
    ) -> tuple[str, BedrockUsage]:
        """Synchronous invoke_model for RAGChecker compatibility."""
        return asyncio.run(self._async_client.invoke_model(prompt, max_tokens, temperature, system_prompt))

    def invoke_with_json_prompt(
        self, prompt: str, max_tokens: int = 150, temperature: float = 0.1
    ) -> tuple[str, BedrockUsage]:
        """Synchronous invoke_with_json_prompt for RAGChecker compatibility."""
        return asyncio.run(self._async_client.invoke_with_json_prompt(prompt, max_tokens, temperature))

    def get_status(self):
        """Get status from the underlying async client."""
        return self._async_client.get_status()

    def save_usage_log(self):
        """Save usage log from the underlying async client."""
        return self._async_client.save_usage_log()

    def test_connection(self) -> bool:
        """Test if the client can connect to Bedrock."""
        try:
            # Try a simple test call to verify connection
            test_result, _ = self.invoke_model("test", max_tokens=1)
            return True
        except Exception:
            return False


# Convenience function for easy integration
def create_enhanced_bedrock_client(api_keys: list[dict[str, str]] | None = None, **kwargs) -> EnhancedBedrockClient:
    """Create and configure an enhanced Bedrock client."""
    return EnhancedBedrockClient(api_keys=api_keys, **kwargs)


if __name__ == "__main__":
    # Example usage and testing
    async def test_client():
        # Example API key configuration
        api_keys = [
            {
                "key_id": "key_1",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_1", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_1", ""),
                "region": "us-east-1",
            },
            {
                "key_id": "key_2",
                "access_key": os.getenv("AWS_ACCESS_KEY_ID_2", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY_2", ""),
                "region": "us-west-2",
            },
        ]

        client = EnhancedBedrockClient(api_keys=api_keys)

        try:
            response, usage = await client.invoke_model(prompt="Hello, how are you today?", max_tokens=50)
            print(f"Response: {response}")
            print(f"Usage: {usage}")

            # Get status
            status = client.get_status()
            print(f"Status: {json.dumps(status, indent=2)}")

        except Exception as e:
            print(f"Error: {e}")

    # Run test if executed directly
    asyncio.run(test_client())
