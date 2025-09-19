"""
Cross-encoder reranking client with ONNX optimization and fallback.

Provides a high-performance reranking service with:
- ONNX-INT8 quantized cross-encoder models
- Micro-batching for efficiency
- Timeout handling with BM25 fallback
- Async support with worker pool management
- Circuit breaker pattern for resilience
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any

try:
    import numpy as np
    import onnxruntime as ort

    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    ort = None
    np = None

try:
    from transformers import AutoTokenizer

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    AutoTokenizer = None


@dataclass
class RerankResult:
    """Result from cross-encoder reranking."""

    query: str
    candidates: list[dict[str, Any]]
    scores: list[float]
    method: str  # "cross_encoder", "heuristic", "timeout_fallback"
    latency_ms: float
    error: str | None = None


class CircuitBreaker:
    """Simple circuit breaker for reranker resilience."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half_open

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == "open":
            # Check if we should try recovery
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == "half_open":
                self.state = "closed"
            self.failure_count = 0
            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise e


class ONNXCrossEncoder:
    """ONNX-optimized cross-encoder for fast reranking."""

    def __init__(
        self,
        model_path: str,
        tokenizer_name: str = "BAAI/bge-reranker-base",
        max_length: int = 512,
        device: str = "cpu",
    ):
        if not HAS_ONNX:
            raise ImportError("onnxruntime required for ONNXCrossEncoder")
        if not HAS_TRANSFORMERS:
            raise ImportError("transformers required for tokenizer")

        self.model_path = model_path
        self.max_length = max_length
        self.device = device

        # Initialize ONNX session
        providers = ["CPUExecutionProvider"]
        if device == "cuda":
            providers.insert(0, "CUDAExecutionProvider")

        self.session = ort.InferenceSession(model_path, providers=providers)

        # Initialize tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

        # Get input/output names
        self.input_names = [input.name for input in self.session.get_inputs()]
        self.output_names = [output.name for output in self.session.get_outputs()]

    def encode_pairs(self, query_doc_pairs: list[tuple[str, str]]) -> dict[str, Any]:
        """Tokenize query-document pairs for ONNX model."""

        queries = [pair[0] for pair in query_doc_pairs]
        documents = [pair[1] for pair in query_doc_pairs]

        # Tokenize pairs
        encoded = self.tokenizer(
            queries, documents, padding=True, truncation=True, max_length=self.max_length, return_tensors="np"
        )

        return {name: encoded[name] for name in self.input_names if name in encoded}

    def predict_scores(self, inputs: dict[str, Any]) -> Any:
        """Run ONNX inference to get relevance scores."""

        outputs = self.session.run(self.output_names, inputs)

        # Extract logits (assuming first output is logits)
        logits = outputs[0]

        # Apply softmax if needed (for classification models)
        if logits.shape[-1] > 1:
            # Multi-class: take positive class probability
            exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
            scores = probs[:, 1] if probs.shape[-1] == 2 else probs[:, -1]
        else:
            # Regression: use sigmoid
            scores = 1.0 / (1.0 + np.exp(-logits.flatten()))

        return scores

    def rerank(self, query: str, candidates: list[dict[str, Any]], text_field: str = "text") -> list[float]:
        """Rerank candidates using cross-encoder."""

        if not candidates:
            return []

        # Prepare query-document pairs
        query_doc_pairs = []
        for candidate in candidates:
            doc_text = candidate.get(text_field, "")
            query_doc_pairs.append((query, doc_text))

        # Encode and predict
        inputs = self.encode_pairs(query_doc_pairs)
        scores = self.predict_scores(inputs)

        return scores.tolist()


class CrossEncoderClient:
    """High-level client for cross-encoder reranking with fallback."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        onnx_path: str | None = None,
        micro_batch_size: int = 32,
        timeout_ms: int = 400,
        max_timeout_ms: int = 600,
        workers: int = 3,
        enable_circuit_breaker: bool = True,
    ):
        self.model_name = model_name
        self.onnx_path = onnx_path
        self.micro_batch_size = micro_batch_size
        self.timeout_ms = timeout_ms
        self.max_timeout_ms = max_timeout_ms
        self.workers = workers

        # Initialize components
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.circuit_breaker = CircuitBreaker() if enable_circuit_breaker else None
        self.cross_encoder: ONNXCrossEncoder | None = None

        # Initialize ONNX model if available
        if onnx_path and HAS_ONNX and HAS_TRANSFORMERS:
            try:
                self.cross_encoder = ONNXCrossEncoder(model_path=onnx_path, tokenizer_name=model_name)
            except Exception as e:
                print(f"Failed to load ONNX cross-encoder: {e}")
                self.cross_encoder = None

    async def rerank_async(
        self, query: str, candidates: list[dict[str, Any]], text_field: str = "text"
    ) -> RerankResult:
        """Async reranking with timeout and fallback."""

        start_time = time.time()

        try:
            # Try cross-encoder reranking with circuit breaker
            if self.cross_encoder and self.circuit_breaker:
                try:
                    scores = await self._rerank_with_timeout(query, candidates, text_field)

                    return RerankResult(
                        query=query,
                        candidates=candidates,
                        scores=scores,
                        method="cross_encoder",
                        latency_ms=(time.time() - start_time) * 1000,
                    )

                except Exception as e:
                    print(f"Cross-encoder reranking failed: {e}")

            # Fallback to heuristic reranking
            scores = await self._heuristic_fallback(query, candidates, text_field)

            return RerankResult(
                query=query,
                candidates=candidates,
                scores=scores,
                method="heuristic_fallback",
                latency_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            return RerankResult(
                query=query,
                candidates=candidates,
                scores=[0.0] * len(candidates),
                method="error_fallback",
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def _rerank_with_timeout(self, query: str, candidates: list[dict[str, Any]], text_field: str) -> list[float]:
        """Run cross-encoder with timeout."""

        if not self.cross_encoder:
            raise Exception("Cross-encoder not available")

        # Submit to thread pool with timeout
        loop = asyncio.get_event_loop()

        try:
            future = loop.run_in_executor(self.executor, self._rerank_batch, query, candidates, text_field)

            scores = await asyncio.wait_for(future, timeout=self.max_timeout_ms / 1000.0)

            return scores

        except TimeoutError:
            raise Exception(f"Reranking timeout after {self.max_timeout_ms}ms")

    def _rerank_batch(self, query: str, candidates: list[dict[str, Any]], text_field: str) -> list[float]:
        """Synchronous batch reranking with micro-batching."""

        if not candidates:
            return []

        all_scores = []

        # Process in micro-batches for efficiency
        for i in range(0, len(candidates), self.micro_batch_size):
            batch = candidates[i : i + self.micro_batch_size]
            batch_scores = self.cross_encoder.rerank(query, batch, text_field)
            all_scores.extend(batch_scores)

        return all_scores

    async def _heuristic_fallback(self, query: str, candidates: list[dict[str, Any]], text_field: str) -> list[float]:
        """Simple heuristic reranking fallback."""

        # Import here to avoid circular dependencies
        from .reranker import _score_rerank

        scores = []
        query_lower = query.lower()

        for candidate in candidates:
            text = candidate.get(text_field, "")
            score = _score_rerank(query_lower, text.lower())
            scores.append(score)

        # Normalize scores to 0-1 range
        if scores:
            min_score = min(scores)
            max_score = max(scores)
            if max_score > min_score:
                scores = [(s - min_score) / (max_score - min_score) for s in scores]

        return scores

    def close(self) -> None:
        """Clean up resources."""
        if self.executor:
            self.executor.shutdown(wait=True)


async def create_cross_encoder_client(config: dict[str, Any]) -> CrossEncoderClient:
    """Factory function to create a cross-encoder client from config."""

    return CrossEncoderClient(
        model_name=config.get("model_name", "BAAI/bge-reranker-base"),
        onnx_path=config.get("onnx_path"),
        micro_batch_size=config.get("micro_batch_size", 32),
        timeout_ms=config.get("timeout_ms", 400),
        max_timeout_ms=config.get("max_timeout_ms", 600),
        workers=config.get("workers", 3),
        enable_circuit_breaker=config.get("enable_circuit_breaker", True),
    )
