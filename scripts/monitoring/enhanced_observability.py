#!/usr/bin/env python3
"""
Enhanced Logfire Observability for Evaluation System

This module provides advanced observability features for our evaluation system,
including custom metrics, error tracking, performance monitoring, and alerting.
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any

import logfire

# Import existing observability
from scripts.monitoring.observability import get_logfire, init_observability


class EvaluationMetrics:
    """Enhanced metrics collection for evaluation system."""

    def __init__(self):
        self.logfire = get_logfire()
        self._counters: dict[str, int] = {}
        self._histograms: dict[str, list[float]] = {}
        self._gauges: dict[str, float] = {}

    def increment_counter(self, name: str, value: int = 1, tags: dict[str, str] = None):
        """Increment a counter metric."""
        self._counters[name] = self.result.get("key", "")
        self.logfire.info("metric.counter", name=name, value=value, tags=tags or {})

    def record_histogram(self, name: str, value: float, tags: dict[str, str] = None):
        """Record a histogram value."""
        if name not in self._histograms:
            self._histograms[name] = []
        self._histograms[name].append(value)
        self.logfire.info("metric.histogram", name=name, value=value, tags=tags or {})

    def set_gauge(self, name: str, value: float, tags: dict[str, str] = None):
        """Set a gauge metric."""
        self._gauges[name] = value
        self.logfire.info("metric.gauge", name=name, value=value, tags=tags or {})

    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics for all histograms."""
        stats = {}
        for name, values in self.histograms.items():
            if values:
                stats[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "p50": sorted(values)[len(values) // 2],
                    "p95": sorted(values)[int(len(values) * 0.95)],
                    "p99": sorted(values)[int(len(values) * 0.99)],
                }
        return stats


class EvaluationTracer:
    """Enhanced tracing for evaluation workflows."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.logfire = get_logfire()
        self._spans: list[Any] = []

    @contextmanager
    def trace_evaluation_phase(self, phase: str, **attributes):
        """Trace a complete evaluation phase."""
        with self.logfire.span(f"evaluation.phase.{phase}", run_id=self.run_id, phase=phase, **attributes) as span:
            start_time = time.time()
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                self.log_error(f"Phase {phase} failed", error=str(e), phase=phase)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration_seconds", duration)
                self.logfire.info(
                    f"evaluation.phase.{phase}.completed",
                    run_id=self.run_id,
                    phase=phase,
                    duration_seconds=duration,
                )

    @contextmanager
    def trace_case_processing(self, case_id: str, query: str, **attributes):
        """Trace individual case processing."""
        with self.logfire.span(
            "evaluation.case",
            run_id=self.run_id,
            case_id=case_id,
            query_length=len(query),
            **attributes,
        ) as span:
            start_time = time.time()
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                self.log_error(f"Case {case_id} failed", error=str(e), case_id=case_id)
                raise
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration_seconds", duration)

    def log_error(self, message: str, error: str, **context):
        """Log structured error information."""
        self.logfire.error(
            "evaluation.error",
            run_id=self.run_id,
            message=message,
            error=error,
            timestamp=datetime.now().isoformat(),
            **context,
        )

    def log_performance_alert(self, metric: str, value: float, threshold: float, **context):
        """Log performance alerts."""
        self.logfire.warn(
            "evaluation.performance_alert",
            run_id=self.run_id,
            metric=metric,
            value=value,
            threshold=threshold,
            severity="warning",
            **context,
        )


class EvaluationProfiler:
    """Performance profiling for evaluation system."""

    def __init__(self):
        self.logfire = get_logfire()
        self._timers: dict[str, float] = {}
        self._memory_usage: list[float] = []

    @contextmanager
    def profile_operation(self, operation: str, **attributes):
        """Profile a specific operation."""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        with self.logfire.span(f"profile.{operation}", **attributes) as span:
            try:
                yield span
            finally:
                duration = time.time() - start_time
                end_memory = self._get_memory_usage()
                memory_delta = end_memory - start_memory

                self._timers[operation] = duration
                self._memory_usage.append(memory_delta)

                span.set_attribute("duration_seconds", duration)
                span.set_attribute("memory_delta_mb", memory_delta)

                self.logfire.info(
                    f"profile.{operation}.completed",
                    operation=operation,
                    duration_seconds=duration,
                    memory_delta_mb=memory_delta,
                )

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary."""
        return {
            "timers": self._timers,
            "memory_usage": {
                "current_mb": self._get_memory_usage(),
                "avg_delta_mb": (sum(self._memory_usage) / len(self._memory_usage) if self._memory_usage else 0),
                "max_delta_mb": max(self._memory_usage) if self._memory_usage else 0,
            },
        }


class EvaluationAlerting:
    """Alerting system for evaluation metrics."""

    def __init__(self):
        self.logfire = get_logfire()
        self._thresholds = {
            "f1_score": {"warning": 0.5, "critical": 0.3},
            "latency_ms": {"warning": 5000, "critical": 10000},
            "precision": {"warning": 0.4, "critical": 0.2},
            "recall": {"warning": 0.4, "critical": 0.2},
            "faithfulness": {"warning": 0.6, "critical": 0.4},
        }

    def check_thresholds(self, metrics: dict[str, float], run_id: str, case_id: str = None):
        """Check metrics against thresholds and generate alerts."""
        context = {"run_id": run_id}
        if case_id:
            context["case_id"] = case_id

        for metric, value in metrics.items():
            if metric in self._thresholds:
                thresholds = self._thresholds[metric]

                if value <= thresholds.get("critical", 0.0):
                    self.logfire.error(
                        "evaluation.alert.critical",
                        metric=metric,
                        value=value,
                        threshold=thresholds.get("critical", 0.0),
                        severity="critical",
                        **context,
                    )
                elif value <= thresholds.get("warning", 0.0):
                    self.logfire.warn(
                        "evaluation.alert.warning",
                        metric=metric,
                        value=value,
                        threshold=thresholds.get("warning", 0.0),
                        severity="warning",
                        **context,
                    )

    def set_custom_threshold(self, metric: str, warning: float, critical: float):
        """Set custom thresholds for a metric."""
        self._thresholds[metric] = {"warning": warning, "critical": critical}


class EnhancedEvaluationLogger:
    """Enhanced logging for evaluation system."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.logfire = get_logfire()
        self.metrics = EvaluationMetrics()
        self.tracer = EvaluationTracer(run_id)
        self.profiler = EvaluationProfiler()
        self.alerting = EvaluationAlerting()

    def log_evaluation_start(self, profile: str, total_cases: int, **context):
        """Log evaluation start with enhanced context."""
        self.logfire.info(
            "evaluation.started",
            run_id=self.run_id,
            profile=profile,
            total_cases=total_cases,
            timestamp=datetime.now().isoformat(),
            **context,
        )
        self.metrics.increment_counter("evaluations_started", tags={"profile": profile})

    def log_evaluation_complete(self, overall_metrics: dict[str, float], **context):
        """Log evaluation completion with enhanced metrics."""
        self.logfire.info(
            "evaluation.completed",
            run_id=self.run_id,
            overall_metrics=overall_metrics,
            timestamp=datetime.now().isoformat(),
            **context,
        )

        # Check for performance alerts
        self.alerting.check_thresholds(overall_metrics, self.run_id)

        # Log performance summary
        perf_summary = self.profiler.get_performance_summary()
        self.logfire.info("evaluation.performance_summary", **perf_summary)

        # Log metrics summary
        metrics_summary = self.metrics.get_summary_stats()
        self.logfire.info("evaluation.metrics_summary", **metrics_summary)

    def log_case_start(self, case_id: str, query: str, **context):
        """Log case start with enhanced context."""
        self.logfire.info(
            "evaluation.case.started",
            run_id=self.run_id,
            case_id=case_id,
            query_length=len(query),
            **context,
        )
        self.metrics.increment_counter("cases_processed", tags={"case_id": case_id})

    def log_case_complete(self, case_id: str, metrics: dict[str, float], **context):
        """Log case completion with enhanced metrics."""
        self.logfire.info(
            "evaluation.case.completed",
            run_id=self.run_id,
            case_id=case_id,
            metrics=metrics,
            **context,
        )

        # Record histogram values
        for metric, value in metrics.items():
            self.metrics.record_histogram(f"case.{metric}", value, tags={"case_id": case_id})

        # Check for performance alerts
        self.alerting.check_thresholds(metrics, self.run_id, case_id)

    def log_retrieval_metrics(self, query: str, candidates: int, latency_ms: float, **context):
        """Log retrieval metrics with enhanced context."""
        self.logfire.info(
            "evaluation.retrieval",
            run_id=self.run_id,
            query_length=len(query),
            candidates=candidates,
            latency_ms=latency_ms,
            **context,
        )

        self.metrics.record_histogram("retrieval.latency_ms", latency_ms)
        self.metrics.record_histogram("retrieval.candidates", candidates)

    def log_reader_metrics(self, query: str, response: str, latency_ms: float, **context):
        """Log reader metrics with enhanced context."""
        self.logfire.info(
            "evaluation.reader",
            run_id=self.run_id,
            query_length=len(query),
            response_length=len(response),
            latency_ms=latency_ms,
            **context,
        )

        self.metrics.record_histogram("reader.latency_ms", latency_ms)
        self.metrics.record_histogram("reader.response_length", len(response))

    def log_error(self, error: Exception, context: dict[str, Any] = None):
        """Log structured error information."""
        self.tracer.log_error(message=str(error), error=type(error).__name__, **(context or {}))
        self.metrics.increment_counter("errors", tags={"error_type": type(error).__name__})


# Global instance for easy access
_enhanced_logger: EnhancedEvaluationLogger | None = None


def get_enhanced_logger(run_id: str = None) -> EnhancedEvaluationLogger:
    """Get or create enhanced evaluation logger."""
    global _enhanced_logger
    if _enhanced_logger is None or (run_id and _enhanced_logger.run_id != run_id):
        _enhanced_logger = EnhancedEvaluationLogger(run_id or f"run_{int(time.time())}")
    return _enhanced_logger
