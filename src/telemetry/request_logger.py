"""
Per-request telemetry logging for RAG pipeline observability.

Captures the full query → answer pipeline with structured logging:
- Query and intent
- Candidates (BM25, vector) with scores
- Fusion ranks and final candidates
- Rerank scores and selected spans
- Generated answer and confidence
- User feedback/actions (when available)

Supports canary tagging and A/B testing analysis.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

import aiofiles


@dataclass
class RequestLog:
    """Structured log entry for a single RAG request."""

    # Request identification
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    canary_tag: str | None = None

    # Pipeline stages
    query: str = ""
    intent: str | None = None

    # Retrieval results
    bm25_candidates: list[dict[str, Any]] = field(default_factory=list)
    vector_candidates: list[dict[str, Any]] = field(default_factory=list)
    fusion_ranks: list[dict[str, Any]] = field(default_factory=list)

    # Reranking
    rerank_scores: list[dict[str, Any]] = field(default_factory=list)
    selected_spans: list[dict[str, Any]] = field(default_factory=list)

    # Generation
    answer: str = ""
    confidence: float | None = None
    abstain: bool = False
    abstain_reason: str | None = None

    # User feedback (when available)
    user_action: str | None = None  # thumbs_up, thumbs_down, edit, etc.
    user_feedback: str | None = None

    # Performance metrics
    stage_timings: dict[str, float] = field(default_factory=dict)
    total_latency_ms: float | None = None


class RequestLogger:
    """Async request logger with configurable output and canary support."""

    def __init__(
        self,
        log_path: str = "metrics/logs/requests.jsonl",
        enabled: bool = True,
        buffer_size: int = 100,
        flush_interval: float = 5.0,
    ):
        self.log_path = Path(log_path)
        self.enabled = enabled
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval

        self._buffer: list[RequestLog] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_task: asyncio.Task | None = None

        # Ensure log directory exists
        if self.enabled:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

    async def start(self) -> None:
        """Start the background flush task."""
        if self.enabled and not self._flush_task:
            self._flush_task = asyncio.create_task(self._flush_worker())

    async def stop(self) -> None:
        """Stop logging and flush remaining entries."""
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None

        # Final flush
        if self._buffer:
            await self._flush_buffer()

    async def log_request(self, request_log: RequestLog) -> None:
        """Log a request asynchronously."""
        if not self.enabled:
            return

        async with self._buffer_lock:
            self._buffer.append(request_log)

            # Immediate flush if buffer is full
            if len(self._buffer) >= self.buffer_size:
                await self._flush_buffer()

    async def _flush_worker(self) -> None:
        """Background worker to flush logs periodically."""
        try:
            while True:
                await asyncio.sleep(self.flush_interval)
                async with self._buffer_lock:
                    if self._buffer:
                        await self._flush_buffer()
        except asyncio.CancelledError:
            # Final flush on cancellation
            async with self._buffer_lock:
                if self._buffer:
                    await self._flush_buffer()
            raise

    async def _flush_buffer(self) -> None:
        """Flush buffered logs to disk."""
        if not self._buffer:
            return

        try:
            # Convert to JSONL format
            lines = []
            for entry in self._buffer:
                line = json.dumps(asdict(entry), ensure_ascii=False)
                lines.append(line)

            # Append to log file
            async with aiofiles.open(self.log_path, "a", encoding="utf-8") as f:
                await f.write("\n".join(lines) + "\n")

            # Clear buffer
            self._buffer.clear()

        except Exception as e:
            # Log error but don't crash the application
            print(f"Failed to flush request logs: {e}")


class CanaryTagger:
    """Utility for tagging requests for canary/A/B testing."""

    def __init__(self, enabled: bool = False, sample_pct: int = 10, tag_name: str = "canary"):
        self.enabled = enabled
        self.sample_pct = sample_pct
        self.tag_name = tag_name
        self._counter = 0

    def should_tag_request(self, request_id: str) -> bool:
        """Determine if a request should be tagged for canary."""
        if not self.enabled:
            return False

        # Simple deterministic sampling based on request_id hash
        hash_val = hash(request_id) % 100
        return hash_val < self.sample_pct

    def get_tag(self, request_id: str) -> str | None:
        """Get canary tag for a request."""
        return self.tag_name if self.should_tag_request(request_id) else None


# Global logger instance (initialized on first use)
_global_logger: RequestLogger | None = None


def get_request_logger(config: dict[str, Any] | None = None) -> RequestLogger:
    """Get or create the global request logger."""
    global _global_logger

    if _global_logger is None:
        if config:
            _global_logger = RequestLogger(
                log_path=config.get("log_path", "metrics/logs/requests.jsonl"),
                enabled=config.get("enabled", True),
                buffer_size=config.get("buffer_size", 100),
                flush_interval=config.get("flush_interval", 5.0),
            )
        else:
            _global_logger = RequestLogger()

    return _global_logger


async def log_rag_request(
    query: str,
    answer: str,
    *,
    request_id: str | None = None,
    canary_tag: str | None = None,
    confidence: float | None = None,
    stage_timings: dict[str, float] | None = None,
    **kwargs: Any,
) -> str:
    """
    Convenience function to log a RAG request.

    Returns the request_id for correlation.
    """
    logger = get_request_logger()

    if not request_id:
        request_id = str(uuid.uuid4())

    log_entry = RequestLog(
        request_id=request_id,
        canary_tag=canary_tag,
        query=query,
        answer=answer,
        confidence=confidence,
        stage_timings=stage_timings or {},
        **kwargs,
    )

    await logger.log_request(log_entry)
    return request_id
