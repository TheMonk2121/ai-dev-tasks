from __future__ import annotations
import asyncio
import json
import logging
import os
import random
import threading
import time
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
        import random
import sys
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Enhanced Bedrock Client with Intelligent Request Queue System
Optimized for RAGChecker evaluations with minimal rate limiting
"""

logger = logging.getLogger(__name__)

@dataclass
class QueuedRequest:
    """Represents a queued request with metadata"""

    request_id: str
    prompt: str
    max_tokens: int
    temperature: float
    system_prompt: str | None
    future: asyncio.Future
    loop: asyncio.AbstractEventLoop
    timestamp: float
    priority: int = 0  # Higher number = higher priority

class IntelligentBedrockQueue:
    """
    Intelligent request queue system that:
    1. Batches requests when possible
    2. Uses smart timing to avoid rate limits
    3. Implements request prioritization
    4. Provides fallback mechanisms
    """

    def __init__(self, api_keys: list[dict[str, str]]):
        self.api_keys = api_keys
        self.request_queue = Queue()
        self.processing = False
        self.worker_thread = None
        self.round_robin_index = 0

        # Retry and backoff configuration (tunable via env)
        self.max_retries = int(os.getenv("BEDROCK_MAX_RETRIES", "6"))
        self.base_backoff = float(os.getenv("BEDROCK_BASE_BACKOFF", "1.5"))
        self.max_backoff = float(os.getenv("BEDROCK_MAX_BACKOFF", "12.0"))

        # Smart timing parameters (conservative defaults)
        self.base_delay = float(os.getenv("BEDROCK_QUEUE_BASE_DELAY", "1.5"))  # Base delay between requests
        self.batch_size = int(os.getenv("BEDROCK_QUEUE_BATCH_SIZE", "1"))  # Process up to N requests in a batch
        self.batch_window = float(os.getenv("BEDROCK_QUEUE_BATCH_WINDOW", "1.5"))  # Time window for batching

        # Rate limit tracking
        self.last_request_time = 0
        self.request_count = 0
        self.window_start = time.time()
        self.window_duration = 60  # 1 minute window

        # Performance tracking
        self.success_count = 0
        self.error_count = 0
        self.total_requests = 0

        logger.info(f"IntelligentBedrockQueue initialized with {len(api_keys)} keys")
        try:
            model_id = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
            logger.info(f"Bedrock model configured: {model_id}")
        except Exception:
            pass

    def start_processing(self):
        """Start the background processing thread"""
        if not self.processing:
            self.processing = True
            self.worker_thread = threading.Thread(target=self._process_requests, daemon=True)
            self.worker_thread.start()
            logger.info("Request queue processing started")

    def stop_processing(self):
        """Stop the background processing thread"""
        self.processing = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Request queue processing stopped")

    async def submit_request(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        system_prompt: str | None = None,
        priority: int = 0,
    ) -> tuple[str, "BedrockUsage"]:
        """Submit a request to the queue and return the (text, usage)."""
        request_id = f"req_{int(time.time() * 1000)}"
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        request = QueuedRequest(
            request_id=request_id,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt,
            future=future,
            loop=loop,
            timestamp=time.time(),
            priority=priority,
        )

        self.request_queue.put(request)
        logger.debug(f"Request {request_id} queued with priority {priority}")

        # Start processing if not already running
        if not self.processing:
            self.start_processing()

        # Wait for result
        result = await future
        return result

    def _process_requests(self):
        """Background thread that processes requests from the queue"""
        batch = []
        last_batch_time = time.time()

        while self.processing:
            try:
                # Collect requests for batching
                current_time = time.time()

                # Try to get a request (non-blocking)
                try:
                    request = self.request_queue.get(timeout=0.1)
                    batch.append(request)
                except Empty:
                    pass

                # Process batch if:
                # 1. We have a full batch, OR
                # 2. We've waited long enough, OR
                # 3. We have high priority requests
                should_process = (
                    len(batch) >= self.batch_size
                    or (batch and current_time - last_batch_time >= self.batch_window)
                    or (batch and any(req.priority > 0 for req in batch))
                )

                if should_process and batch:
                    self._process_batch(batch)
                    batch = []
                    last_batch_time = current_time

                # Small delay to prevent busy waiting
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Error in request processing: {e}")
                # Clear any failed requests
                for request in batch:
                    if not request.future.done():
                        request.future.set_exception(e)
                batch = []

    def _process_batch(self, batch: list[QueuedRequest]):
        """Process a batch of requests"""
        logger.info(f"Processing batch of {len(batch)} requests")

        # Sort by priority (higher first)
        batch.sort(key=lambda x: x.priority, reverse=True)

        for request in batch:
            try:
                # Smart delay calculation
                delay = self._calculate_smart_delay()
                if delay > 0:
                    time.sleep(delay)

                # Process the request
                result_text, usage = self._process_single_request(request)
                # Resolve future from the owning event loop thread-safely
                request.loop.call_soon_threadsafe(request.future.set_result, (result_text, usage))

                self.success_count += 1
                logger.debug(f"Request {request.request_id} completed successfully")

            except Exception as e:
                logger.error(f"Request {request.request_id} failed: {e}")
                request.loop.call_soon_threadsafe(request.future.set_exception, e)
                self.error_count += 1

            finally:
                self.total_requests += 1

    def _calculate_smart_delay(self) -> float:
        """Calculate smart delay based on current load and rate limits"""
        current_time = time.time()

        # Reset window if needed
        if current_time - self.window_start >= self.window_duration:
            self.window_start = current_time
            self.request_count = 0

        # Base delay
        delay = self.base_delay

        # Increase delay if we're approaching rate limits
        if self.request_count > 10:  # Conservative limit
            delay *= 2

        # Add jitter to prevent thundering herd

        delay += random.uniform(0, 0.5)

        return delay

    def _process_single_request(self, request: QueuedRequest) -> tuple[str, "BedrockUsage"]:
        """Process a single request using round-robin keys with retries. Returns (text, usage)."""
        last_error: Exception | None = None

        for attempt in range(self.max_retries):
            # Select key via round-robin
            key_config = self.api_keys[self.round_robin_index % max(len(self.api_keys), 1)]

            # Create Bedrock client (use explicit creds if provided; otherwise default chain)
            config = Config(
                region_name=key_config.get("region", os.getenv("AWS_REGION", "us-east-1")),
                retries={"max_attempts": 0},  # we implement retries ourselves
                read_timeout=30,
                connect_timeout=10,
            )

            client_kwargs: dict[str, Any] = {
                "service_name": "bedrock-runtime",
                "config": config,
                "region_name": key_config.get("region", os.getenv("AWS_REGION", "us-east-1")),
            }
            # Only pass keys if present; else let boto3 resolve credentials
            if key_config.get("access_key") and key_config.get("secret_key"):
                client_kwargs.update(
                    {
                        "aws_access_key_id": key_config["access_key"],
                        "aws_secret_access_key": key_config["secret_key"],
                    }
                )

            client = boto3.client(**client_kwargs)

            # Prepare request body
            request_body = self._prepare_request_body(
                request.prompt, request.max_tokens, request.temperature, request.system_prompt
            )

            try:
                # Make the request
                response = client.invoke_model(
                    modelId=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
                    body=json.dumps(request_body),
                    contentType="application/json",
                    accept="application/json",
                )

                # Parse response
                response_body = json.loads(response["body"].read())
                content = response_body.get("content", [{}])[0].get("text", "")

                # Extract usage if available
                usage_obj = response_body.get("usage", {})
                input_tokens = int(usage_obj.get("input_tokens", 0) or 0)
                output_tokens = int(usage_obj.get("output_tokens", 0) or 0)

                # Pricing aligned with standard client
                INPUT_TOKEN_COST = 3.00 / 1_000_000
                OUTPUT_TOKEN_COST = 15.00 / 1_000_000
                total_cost = (input_tokens * INPUT_TOKEN_COST) + (output_tokens * OUTPUT_TOKEN_COST)

                usage = BedrockUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    request_count=1,
                    total_cost=total_cost,
                    timestamp="",
                )

                # Update tracking and advance RR index only on success
                self.last_request_time = time.time()
                self.request_count += 1
                self.round_robin_index = (self.round_robin_index + 1) % max(len(self.api_keys), 1)

                return content, usage

            except ClientError as e:
                last_error = e
                code = e.response.get("Error", {}).get("Code", "")
                msg = str(e)
                # Consider throttling / rate exceeded as retryable
                retryable = code in ("ThrottlingException",) or any(
                    s in msg for s in ["Too many requests", "Rate exceeded", "throttl", "429"]
                )
                if retryable and attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    backoff = min(self.base_backoff * (2**attempt), self.max_backoff)
                    jitter = random.uniform(0.0, 0.5)
                    sleep_for = backoff + jitter
                    logger.warning(
                        f"Request {request.request_id} throttled (attempt {attempt+1}/{self.max_retries}); "
                        f"backing off {sleep_for:.1f}s"
                    )
                    time.sleep(sleep_for)
                    continue
                # Other client errors: retry a few times with smaller backoff
                if attempt < self.max_retries - 1:
                    backoff = min(1.0 * (2**attempt), 6.0)
                    time.sleep(backoff)
                    continue
                # Exhausted
                raise
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    backoff = min(1.0 * (2**attempt), 6.0)
                    time.sleep(backoff)
                    continue
                raise

        # If we ever get here, raise the last error
        assert last_error is not None
        raise last_error

    def _prepare_request_body(
        self, prompt: str, max_tokens: int, temperature: float, system_prompt: str | None = None
    ) -> dict[str, Any]:
        """Prepare request body for Bedrock API"""
        messages = [{"role": "user", "content": prompt}]

        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        if system_prompt:
            body["system"] = system_prompt

        return body

    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_size": self.request_queue.qsize(),
            "total_requests": self.total_requests,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(self.total_requests, 1),
            "processing": self.processing,
        }

@dataclass
class BedrockUsage:
    """Lightweight usage tracker compatible with RAGChecker expectations."""

    input_tokens: int = 0
    output_tokens: int = 0
    request_count: int = 0
    total_cost: float = 0.0
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "request_count": self.request_count,
            "total_cost": self.total_cost,
            "timestamp": self.timestamp,
        }

# Synchronous wrapper for RAGChecker compatibility
class SyncBedrockQueueClient:
    """Synchronous wrapper for the async queue client"""

    def __init__(self, api_keys: list[dict[str, str]] | None = None, **kwargs):
        """Initialize with graceful fallback for RAGChecker compatibility"""
        try:
            if api_keys is None:
                # Load API keys from environment
                api_keys = self._load_api_keys_from_env()

            if not api_keys:
                raise ValueError("No valid API keys found")

            self.queue = IntelligentBedrockQueue(api_keys)
            self.queue.start_processing()
            logger.info(f"SyncBedrockQueueClient initialized with {len(api_keys)} keys")
            self.initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize queue client: {e}")
            self.initialized = False
            self.queue = None
            # Don't raise exception - allow graceful fallback

    def _load_api_keys_from_env(self) -> list[dict[str, str]]:
        """Load API key configurations from environment variables."""
        api_keys = []

        # Check for multiple key configurations (explicit env var credentials)
        key_index = 0
        while True:
            # Use traditional AWS access keys
            access_key = os.getenv(f"AWS_ACCESS_KEY_ID_{key_index}" if key_index > 0 else "AWS_ACCESS_KEY_ID")
            secret_key = os.getenv(f"AWS_SECRET_ACCESS_KEY_{key_index}" if key_index > 0 else "AWS_SECRET_ACCESS_KEY")
            region = os.getenv(f"AWS_REGION_{key_index}" if key_index > 0 else "AWS_REGION", "us-east-1")

            # Skip placeholder values and empty keys
            if (
                not access_key
                or not secret_key
                or access_key in ["your_primary_access_key_here", "your_access_key_here"]
                or secret_key in ["your_primary_secret_key_here", "your_secret_key_here"]
            ):
                break

            api_keys.append(
                {
                    "key_id": f"key_{key_index}",
                    "access_key": access_key,
                    "secret_key": secret_key,
                    "region": region,
                }
            )
            key_index += 1

        if not api_keys:
            # Fall back to default boto3 credential chain; require only region
            region = os.getenv("AWS_REGION", "us-east-1")
            logger.warning("No explicit AWS access keys found in env; falling back to default boto3 credentials chain")
            api_keys = [
                {
                    "key_id": "default_chain",
                    "access_key": None,  # signal to use default chain
                    "secret_key": None,
                    "region": region,
                }
            ]

        logger.info(f"Loaded {len(api_keys)} API key configurations")
        return api_keys

    def invoke_model(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        system_prompt: str | None = None,
        **kwargs,
    ) -> tuple[str, BedrockUsage]:
        """Synchronous model invocation that returns (text, usage)."""
        if not self.initialized or self.queue is None:
            raise RuntimeError("Queue client not properly initialized - cannot invoke model")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_text, usage = loop.run_until_complete(
                self.queue.submit_request(prompt, max_tokens, temperature, system_prompt=system_prompt)
            )
            return result_text, usage
        finally:
            loop.close()

    def invoke_with_json_prompt(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1,
        system_prompt: str | None = None,
        **kwargs,
    ) -> tuple[str, BedrockUsage]:
        """Synchronous JSON prompt invocation (returns text, usage)."""
        json_system_prompt = (
            "You are a helpful assistant that always responds with valid JSON. "
            "Structure your responses as requested in the prompt. "
            "Ensure all JSON is properly formatted and parseable."
        )
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        return self.invoke_model(json_prompt, max_tokens, temperature, system_prompt=json_system_prompt)

    def test_connection(self) -> bool:
        """Test if the client is properly initialized and can connect"""
        return self.initialized and self.queue is not None

    def get_stats(self) -> dict[str, Any]:
        """Get queue statistics"""
        if not self.initialized or self.queue is None:
            return {"error": "Queue client not initialized", "initialized": False}
        return self.queue.get_stats()

    def __del__(self):
        """Cleanup when client is destroyed"""
        if hasattr(self, "queue"):
            self.queue.stop_processing()
