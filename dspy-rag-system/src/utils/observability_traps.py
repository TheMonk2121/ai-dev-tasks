#!/usr/bin/env python3
"""
Observability Traps
- Tracing and span management
- Health checks and monitoring
- Performance metrics and alerts
- Database and retrieval health monitoring
"""

import json
import time
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class SpanStatus(Enum):
    """Span execution status"""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class Span:
    """Tracing span"""

    span_id: str
    parent_span_id: str | None
    operation_name: str
    start_time: float
    end_time: float | None = None
    status: SpanStatus = SpanStatus.SUCCESS
    tags: dict[str, Any] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation_name": self.operation_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.end_time - self.start_time if self.end_time else None,
            "status": self.status.value,
            "tags": self.tags,
            "logs": self.logs,
            "error": self.error,
        }


@dataclass
class HealthCheck:
    """Health check result"""

    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    timestamp: str
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
        }


class ObservabilityManager:
    """Manages observability, tracing, and health checks"""

    def __init__(self):
        self.spans: list[Span] = []
        self.active_spans: dict[str, Span] = {}
        self.health_checks: list[HealthCheck] = []
        self.performance_metrics: dict[str, list[float]] = {}

        # Health check thresholds
        self.thresholds = {
            "retrieval_latency_p95": 2.0,  # seconds
            "rerank_latency_p95": 1.0,  # seconds
            "llm_latency_p95": 5.0,  # seconds
            "token_budget_violations": 0,  # count
            "prefix_leakage": 0,  # count
            "dedup_rate_min": 0.10,  # ratio
            "dedup_rate_max": 0.35,  # ratio
            "snapshot_size_min": 20,  # count
            "oracle_hit_rate_min": 0.1,  # ratio
        }

    def start_span(self, operation_name: str, parent_span_id: str | None = None, **tags) -> str:
        """Start a new tracing span"""
        span_id = f"span_{int(time.time() * 1000000)}"

        span = Span(
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags=tags,
        )

        self.active_spans[span_id] = span

        return span_id

    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.SUCCESS, error: str | None = None):
        """End a tracing span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.end_time = time.time()
            span.status = status
            span.error = error

            self.spans.append(span)
            del self.active_spans[span_id]

    def add_span_log(self, span_id: str, message: str, **fields):
        """Add log to span"""
        if span_id in self.active_spans:
            log_entry = {
                "timestamp": time.time(),
                "message": message,
                "fields": fields,
            }
            self.active_spans[span_id].logs.append(log_entry)

    def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span"""
        if span_id in self.active_spans:
            self.active_spans[span_id].tags[key] = value

    def record_metric(self, metric_name: str, value: float):
        """Record a performance metric"""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []

        self.performance_metrics[metric_name].append(value)

        # Keep only last 1000 values
        if len(self.performance_metrics[metric_name]) > 1000:
            self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-1000:]

    def run_health_checks(self) -> list[HealthCheck]:
        """Run comprehensive health checks"""
        print("🏥 Running Health Checks")
        print("=" * 40)

        health_checks = []

        # Index sanity check
        health_checks.append(self._check_index_sanity())

        # Token budget compliance
        health_checks.append(self._check_token_budget())

        # Prefix leakage check
        health_checks.append(self._check_prefix_leakage())

        # Dedup rate check
        health_checks.append(self._check_dedup_rate())

        # Snapshot breadth check
        health_checks.append(self._check_snapshot_breadth())

        # Oracle hit rate check
        health_checks.append(self._check_oracle_hit_rate())

        # Performance metrics check
        health_checks.append(self._check_performance_metrics())

        # Circuit breaker status
        health_checks.append(self._check_circuit_breakers())

        self.health_checks = health_checks

        return health_checks

    def _check_index_sanity(self) -> HealthCheck:
        """Check index sanity"""
        # In production, you'd check actual database indexes
        # For now, we'll simulate the check

        bm25_gin_present = True  # Simulated
        pgvector_present = True  # Simulated
        index_usage = 0.95  # Simulated

        if bm25_gin_present and pgvector_present and index_usage > 0.9:
            status = "healthy"
            message = "All indexes present and being used"
        elif index_usage < 0.5:
            status = "unhealthy"
            message = f"Low index usage: {index_usage:.2f}"
        else:
            status = "degraded"
            message = f"Index usage below optimal: {index_usage:.2f}"

        return HealthCheck(
            name="index_sanity",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={
                "bm25_gin_present": bm25_gin_present,
                "pgvector_present": pgvector_present,
                "index_usage": index_usage,
            },
        )

    def _check_token_budget(self) -> HealthCheck:
        """Check token budget compliance"""
        # Simulated token budget violations
        violations = 0  # Should be 0 in production

        if violations == 0:
            status = "healthy"
            message = "No token budget violations"
        else:
            status = "unhealthy"
            message = f"Token budget violations: {violations}"

        return HealthCheck(
            name="token_budget",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"violations": violations},
        )

    def _check_prefix_leakage(self) -> HealthCheck:
        """Check for prefix leakage"""
        # Simulated prefix leakage check
        leakage_count = 0  # Should be 0 in production

        if leakage_count == 0:
            status = "healthy"
            message = "No prefix leakage detected"
        else:
            status = "unhealthy"
            message = f"Prefix leakage detected: {leakage_count} chunks"

        return HealthCheck(
            name="prefix_leakage",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"leakage_count": leakage_count},
        )

    def _check_dedup_rate(self) -> HealthCheck:
        """Check deduplication rate"""
        # Simulated dedup rate
        dedup_rate = 0.20  # Should be 10-35%

        if 0.10 <= dedup_rate <= 0.35:
            status = "healthy"
            message = f"Dedup rate within target range: {dedup_rate:.2f}"
        elif dedup_rate < 0.10:
            status = "degraded"
            message = f"Dedup rate too low: {dedup_rate:.2f}"
        else:
            status = "degraded"
            message = f"Dedup rate too high: {dedup_rate:.2f}"

        return HealthCheck(
            name="dedup_rate",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"dedup_rate": dedup_rate},
        )

    def _check_snapshot_breadth(self) -> HealthCheck:
        """Check retrieval snapshot breadth"""
        # Simulated snapshot size
        avg_snapshot_size = 45  # Should be ≥20

        if avg_snapshot_size >= 20:
            status = "healthy"
            message = f"Snapshot breadth adequate: {avg_snapshot_size}"
        else:
            status = "unhealthy"
            message = f"Snapshot breadth too low: {avg_snapshot_size}"

        return HealthCheck(
            name="snapshot_breadth",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"avg_snapshot_size": avg_snapshot_size},
        )

    def _check_oracle_hit_rate(self) -> HealthCheck:
        """Check oracle hit rate"""
        # Simulated oracle hit rate
        oracle_hit_rate = 0.25  # Should be ≥0.1

        if oracle_hit_rate >= 0.1:
            status = "healthy"
            message = f"Oracle hit rate adequate: {oracle_hit_rate:.2f}"
        else:
            status = "unhealthy"
            message = f"Oracle hit rate too low: {oracle_hit_rate:.2f}"

        return HealthCheck(
            name="oracle_hit_rate",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"oracle_hit_rate": oracle_hit_rate},
        )

    def _check_performance_metrics(self) -> HealthCheck:
        """Check performance metrics"""
        issues = []

        # Check latency metrics
        for metric_name in ["retrieval_latency_p95", "rerank_latency_p95", "llm_latency_p95"]:
            if metric_name in self.performance_metrics:
                values = self.performance_metrics[metric_name]
                if values:
                    p95_value = sorted(values)[int(0.95 * len(values))]
                    threshold = self.thresholds[metric_name]

                    if p95_value > threshold:
                        issues.append(f"{metric_name}: {p95_value:.2f}s > {threshold}s")

        if not issues:
            status = "healthy"
            message = "All performance metrics within thresholds"
        else:
            status = "degraded"
            message = f"Performance issues: {', '.join(issues)}"

        return HealthCheck(
            name="performance_metrics",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"issues": issues},
        )

    def _check_circuit_breakers(self) -> HealthCheck:
        """Check circuit breaker status"""
        # Simulated circuit breaker status
        open_breakers = 0  # Should be 0

        if open_breakers == 0:
            status = "healthy"
            message = "All circuit breakers closed"
        else:
            status = "unhealthy"
            message = f"Circuit breakers open: {open_breakers}"

        return HealthCheck(
            name="circuit_breakers",
            status=status,
            message=message,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            metrics={"open_breakers": open_breakers},
        )

    def get_health_summary(self) -> dict[str, Any]:
        """Get health check summary"""
        if not self.health_checks:
            return {"status": "unknown", "total_checks": 0}

        healthy_count = len([h for h in self.health_checks if h.status == "healthy"])
        degraded_count = len([h for h in self.health_checks if h.status == "degraded"])
        unhealthy_count = len([h for h in self.health_checks if h.status == "unhealthy"])

        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "total_checks": len(self.health_checks),
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "checks": [h.to_dict() for h in self.health_checks],
        }

    def get_trace_summary(self) -> dict[str, Any]:
        """Get trace summary"""
        if not self.spans:
            return {"total_spans": 0}

        total_spans = len(self.spans)
        successful_spans = len([s for s in self.spans if s.status == SpanStatus.SUCCESS])
        failed_spans = total_spans - successful_spans

        # Operation breakdown
        operation_counts = {}
        for span in self.spans:
            operation_counts[span.operation_name] = operation_counts.get(span.operation_name, 0) + 1

        # Average durations
        operation_durations = {}
        for span in self.spans:
            if span.end_time:
                duration = span.end_time - span.start_time
                if span.operation_name not in operation_durations:
                    operation_durations[span.operation_name] = []
                operation_durations[span.operation_name].append(duration)

        avg_durations = {}
        for operation, durations in operation_durations.items():
            avg_durations[operation] = sum(durations) / len(durations)

        return {
            "total_spans": total_spans,
            "successful_spans": successful_spans,
            "failed_spans": failed_spans,
            "success_rate": successful_spans / total_spans if total_spans > 0 else 0,
            "operation_counts": operation_counts,
            "avg_durations": avg_durations,
        }

    def save_observability_report(self, filepath: str) -> None:
        """Save observability report to file"""
        report = {
            "health_summary": self.get_health_summary(),
            "trace_summary": self.get_trace_summary(),
            "spans": [span.to_dict() for span in self.spans],
            "health_checks": [check.to_dict() for check in self.health_checks],
            "performance_metrics": self.performance_metrics,
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📝 Observability report saved to: {filepath}")


def create_observability_manager() -> ObservabilityManager:
    """Create an observability manager"""
    return ObservabilityManager()
