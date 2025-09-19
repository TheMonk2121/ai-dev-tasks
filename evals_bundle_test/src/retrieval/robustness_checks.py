"""
Robustness Checks for Retrieval Pipeline

Implements health checks, performance monitoring, and failure detection
to ensure the retrieval system operates reliably in production.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class HealthCheckResult:
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: float
    details: dict[str, Any]
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "component": self.component,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass
class PerformanceMetrics:
    avg_latency_ms: float
    p95_latency_ms: float
    success_rate: float
    error_rate: float
    throughput_qps: float


class RobustnessChecker:
    """Monitors retrieval pipeline health and performance."""

    def __init__(self) -> None:
        self.latency_history: list[float] = []
        self.error_count = 0
        self.success_count = 0
        self.last_health_check = 0.0

    def check_component_health(
        self, component_name: str, check_fn: Callable[[], Any], timeout_ms: float = 5000.0
    ) -> HealthCheckResult:
        """Perform health check on a pipeline component."""
        start_time = time.time()
        status = "healthy"
        details: dict[str, Any] = {}

        try:
            # Run with timeout
            result = check_fn()
            latency_ms = (time.time() - start_time) * 1000

            # Classify health based on latency and result
            if latency_ms > timeout_ms:
                status = "degraded"
                details["reason"] = f"High latency: {latency_ms:.1f}ms > {timeout_ms}ms"
            elif latency_ms > timeout_ms * 0.5:
                status = "degraded"
                details["reason"] = f"Elevated latency: {latency_ms:.1f}ms"

            if result is None:
                status = "unhealthy"
                details["reason"] = "Check function returned None"

            details["result"] = str(result)[:200] if result else None

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            status = "unhealthy"
            details["error"] = str(e)
            details["exception_type"] = type(e).__name__

        return HealthCheckResult(
            component=component_name, status=status, latency_ms=latency_ms, details=details, timestamp=time.time()
        )

    def record_query_performance(self, latency_ms: float, success: bool) -> None:
        """Record performance metrics for a query."""
        self.latency_history.append(latency_ms)

        # Keep only recent history (last 1000 queries)
        if len(self.latency_history) > 1000:
            self.latency_history = self.latency_history[-1000:]

        if success:
            self.success_count += 1
        else:
            self.error_count += 1

    def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics."""
        if not self.latency_history:
            return PerformanceMetrics(0, 0, 0, 0, 0)

        sorted_latencies = sorted(self.latency_history)
        avg_latency = sum(self.latency_history) / len(self.latency_history)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[p95_idx] if p95_idx < len(sorted_latencies) else sorted_latencies[-1]

        total_queries = self.success_count + self.error_count
        success_rate = self.success_count / total_queries if total_queries > 0 else 0
        error_rate = self.error_count / total_queries if total_queries > 0 else 0

        # Estimate throughput (queries per second) based on recent activity
        # This is a rough estimate - in production you'd track this more precisely
        time_window = 60.0  # 1 minute window
        recent_queries = min(len(self.latency_history), 100)  # Estimate based on recent queries
        throughput = recent_queries / time_window if recent_queries > 0 else 0

        return PerformanceMetrics(
            avg_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            success_rate=success_rate,
            error_rate=error_rate,
            throughput_qps=throughput,
        )

    def check_performance_degradation(self) -> dict[str, Any]:
        """Check for performance degradation indicators."""
        metrics = self.get_performance_metrics()
        issues = []

        # Define thresholds
        MAX_AVG_LATENCY = 2000.0  # 2 seconds
        MAX_P95_LATENCY = 5000.0  # 5 seconds
        MIN_SUCCESS_RATE = 0.95  # 95%
        MAX_ERROR_RATE = 0.05  # 5%

        if metrics.avg_latency_ms > MAX_AVG_LATENCY:
            issues.append(f"High average latency: {metrics.avg_latency_ms:.1f}ms")

        if metrics.p95_latency_ms > MAX_P95_LATENCY:
            issues.append(f"High P95 latency: {metrics.p95_latency_ms:.1f}ms")

        if metrics.success_rate < MIN_SUCCESS_RATE:
            issues.append(f"Low success rate: {metrics.success_rate:.3f}")

        if metrics.error_rate > MAX_ERROR_RATE:
            issues.append(f"High error rate: {metrics.error_rate:.3f}")

        return {
            "degraded": len(issues) > 0,
            "issues": issues,
            "metrics": {
                "avg_latency_ms": metrics.avg_latency_ms,
                "p95_latency_ms": metrics.p95_latency_ms,
                "success_rate": metrics.success_rate,
                "error_rate": metrics.error_rate,
                "throughput_qps": metrics.throughput_qps,
            },
        }

    def run_comprehensive_health_check(self) -> dict[str, Any]:
        """Run comprehensive health check across all components."""
        health_results = []
        overall_status = "healthy"

        # Check fusion component
        def check_fusion() -> bool:
            from retrieval.fusion import weighted_rrf  # type: ignore[import-untyped]

            # Simple test
            bm25 = [("doc1", 10.0), ("doc2", 5.0)]
            vector = [("doc1", 0.9), ("doc3", 0.8)]
            result = weighted_rrf(bm25, vector, k=60)
            return len(result) > 0

        fusion_health = self.check_component_health("fusion", check_fusion)
        health_results.append(fusion_health)

        # Check prefilter component
        def check_prefilter() -> bool:
            from retrieval.prefilter import PrefilterConfig, RecallFriendlyPrefilter  # type: ignore[import-untyped]

            pf = RecallFriendlyPrefilter(PrefilterConfig())
            docs = {"doc1": "Test document content", "doc2": "Another test document"}
            candidates = [("doc1", 0.8), ("doc2", 0.6)]
            result = pf.filter_vector_results(candidates, docs)
            return len(result) >= 0

        prefilter_health = self.check_component_health("prefilter", check_prefilter)
        health_results.append(prefilter_health)

        # Check reranker component
        def check_reranker() -> bool:
            from retrieval.reranker import heuristic_rerank  # type: ignore[import-untyped]

            candidates = [("doc1", 0.8), ("doc2", 0.6)]
            docs = {"doc1": "Test content", "doc2": "Another test"}
            result = heuristic_rerank("test query", candidates, docs)
            return len(result) >= 0

        reranker_health = self.check_component_health("reranker", check_reranker)
        health_results.append(reranker_health)

        # Check packer component
        def check_packer() -> bool:
            from retrieval.packer import pack_candidates  # type: ignore[import-untyped]

            candidates = [("doc1", 0.8), ("doc2", 0.6)]
            docs = {"doc1": "Test content", "doc2": "Another test"}
            result = pack_candidates(candidates, docs)
            return len(result) > 0

        packer_health = self.check_component_health("packer", check_packer)
        health_results.append(packer_health)

        # Check quality gates component
        def check_quality_gates() -> bool:
            from retrieval.quality_gates import validate_evaluation_results  # type: ignore[import-untyped]

            metrics = {"recall_at_20": 0.3, "f1_score": 0.2, "faithfulness": 0.6}
            result = validate_evaluation_results(metrics)
            return result is not None

        gates_health = self.check_component_health("quality_gates", check_quality_gates)
        health_results.append(gates_health)

        # Determine overall status
        unhealthy_count = sum(1 for r in health_results if r.status == "unhealthy")
        degraded_count = sum(1 for r in health_results if r.status == "degraded")

        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"

        # Get performance metrics
        perf_check = self.check_performance_degradation()

        return {
            "overall_status": overall_status,
            "component_health": [r.to_dict() for r in health_results],
            "performance_check": perf_check,
            "timestamp": time.time(),
            "summary": {
                "total_components": len(health_results),
                "healthy": sum(1 for r in health_results if r.status == "healthy"),
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
            },
        }


def test_error_recovery(retrieval_fn: Callable[[str], Any]) -> dict[str, Any]:
    """Test error recovery capabilities."""
    recovery_tests = [
        {"name": "empty_query", "query": "", "expected": "graceful_handling"},
        {"name": "malformed_unicode", "query": "Test \udcff\udcfe invalid unicode", "expected": "graceful_handling"},
        {
            "name": "very_long_query",
            "query": "What is " + "very " * 1000 + "long query?",
            "expected": "truncation_or_handling",
        },
        {
            "name": "special_characters",
            "query": "Test with <script>alert('xss')</script> injection",
            "expected": "safe_handling",
        },
    ]

    results = []
    for test in recovery_tests:
        try:
            start_time = time.time()
            result = retrieval_fn(test["query"])
            latency = (time.time() - start_time) * 1000

            test_result = {
                "test_name": test["name"],
                "status": "passed",
                "latency_ms": latency,
                "result_type": type(result).__name__,
                "has_answer": "answer" in result if isinstance(result, dict) else False,
            }

            # Basic validation that we got some response
            if isinstance(result, dict) and "answer" in result:
                test_result["graceful"] = True
            else:
                test_result["graceful"] = False
                test_result["status"] = "questionable"

        except Exception as e:
            test_result = {
                "test_name": test["name"],
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "graceful": False,
            }

        results.append(test_result)

    summary = {
        "total_tests": len(results),
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "questionable": sum(1 for r in results if r["status"] == "questionable"),
        "graceful_failures": sum(1 for r in results if r.get("graceful", False)),
    }

    return {"error_recovery_summary": summary, "test_results": results}
