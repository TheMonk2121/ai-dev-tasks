"""
Decision Performance Optimization and Benchmarking

This module provides performance optimization, caching strategies, and benchmarking
for decision intelligence operations to ensure p95 < 10ms warm and < 150ms cold targets.
"""

import json
import logging
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .context_merger import ContextMerger, MergedContext
from .conversation_storage import ConversationStorage


@dataclass
class PerformanceMetrics:
    """Performance metrics for decision operations"""

    operation_type: str
    timestamp: datetime
    execution_time_ms: float
    result_count: int
    cache_hit: bool
    session_id: str | None = None
    query_complexity: str = "simple"  # simple, medium, complex
    warm_cache: bool = True


@dataclass
class BenchmarkResult:
    """Results from a performance benchmark run"""

    benchmark_name: str
    timestamp: datetime
    total_operations: int
    warm_cache_metrics: list[PerformanceMetrics]
    cold_cache_metrics: list[PerformanceMetrics]
    cache_hit_rate: float
    performance_targets_met: dict[str, bool]
    recommendations: list[str]


class DecisionPerformanceOptimizer:
    """
    Optimizes and benchmarks decision retrieval performance.

    Implements:
    - Decision-specific caching strategies
    - Performance monitoring and regression detection
    - Warm vs cold cache benchmarking
    - Performance target validation
    """

    def __init__(self, storage: ConversationStorage, merger: ContextMerger):
        self.storage = storage
        self.merger = merger
        self.logger = logging.getLogger(__name__)

        # Performance targets
        self.performance_targets = {
            "warm": {"p50": 5, "p95": 10, "p99": 20},  # ms
            "cold": {"p50": 50, "p95": 150, "p99": 300},  # ms
        }

        # Cache configuration
        self.decision_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000

        # Performance monitoring
        self.performance_history = defaultdict(list)
        self.regression_threshold = 1.5  # 50% performance degradation

    def optimize_decision_retrieval(
        self, session_id: str, query_entities: list[str] | None = None, use_cache: bool = True
    ) -> tuple[list[MergedContext], bool]:
        """
        Optimized decision retrieval with caching and performance monitoring.

        Args:
            session_id: Session identifier
            query_entities: Entities for overlap scoring
            use_cache: Whether to use caching

        Returns:
            Tuple of (decisions, cache_hit)
        """
        start_time = time.time()
        cache_hit = False

        try:
            # Check cache first if enabled
            if use_cache:
                cache_key = self._generate_cache_key(session_id, query_entities)
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    cache_hit = True
                    execution_time = (time.time() - start_time) * 1000
                    self._record_performance_metric(
                        "decision_retrieval_cached", execution_time, len(cached_result), True, session_id
                    )
                    return cached_result, True

            # Perform actual retrieval
            merge_result = self.merger.merge_decision_contexts(session_id=session_id, query_entities=query_entities)

            decisions = merge_result.merged_contexts
            execution_time = (time.time() - start_time) * 1000

            # Cache the result if caching is enabled
            if use_cache and decisions:
                cache_key = self._generate_cache_key(session_id, query_entities)
                self._add_to_cache(cache_key, decisions)

            # Record performance metrics
            self._record_performance_metric("decision_retrieval", execution_time, len(decisions), cache_hit, session_id)

            return decisions, cache_hit

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._record_performance_metric("decision_retrieval_error", execution_time, 0, cache_hit, session_id)
            self.logger.error(f"Error in optimized decision retrieval: {e}")
            return [], cache_hit

    def _generate_cache_key(self, session_id: str, query_entities: list[str] | None) -> str:
        """Generate cache key for decision retrieval"""
        entities_str = "_".join(sorted(query_entities or []))
        return f"decisions:{session_id}:{entities_str}"

    def _get_from_cache(self, cache_key: str) -> list[MergedContext] | None:
        """Get decision results from cache"""
        if cache_key in self.decision_cache:
            cached_data = self.decision_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                return cached_data["data"]
            else:
                # Expired, remove from cache
                del self.decision_cache[cache_key]
        return None

    def _add_to_cache(self, cache_key: str, decisions: list[MergedContext]) -> None:
        """Add decision results to cache"""
        # Implement LRU eviction if cache is full
        if len(self.decision_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = min(self.decision_cache.keys(), key=lambda k: self.decision_cache[k]["timestamp"])
            del self.decision_cache[oldest_key]

        self.decision_cache[cache_key] = {"data": decisions, "timestamp": time.time()}

    def _record_performance_metric(
        self,
        operation_type: str,
        execution_time_ms: float,
        result_count: int,
        cache_hit: bool,
        session_id: str | None = None,
    ) -> None:
        """Record performance metric for monitoring"""
        metric = PerformanceMetrics(
            operation_type=operation_type,
            timestamp=datetime.now(),
            execution_time_ms=execution_time_ms,
            result_count=result_count,
            cache_hit=cache_hit,
            session_id=session_id,
        )

        self.performance_history[operation_type].append(metric)

        # Keep only last 1000 metrics per operation type
        if len(self.performance_history[operation_type]) > 1000:
            self.performance_history[operation_type] = self.performance_history[operation_type][-1000:]

    def run_performance_benchmark(
        self, session_id: str, benchmark_iterations: int = 100, warm_cache_ratio: float = 0.7
    ) -> BenchmarkResult:
        """
        Run comprehensive performance benchmark for decision operations.

        Args:
            session_id: Session to benchmark
            benchmark_iterations: Number of iterations to run
            warm_cache_ratio: Ratio of warm cache operations

        Returns:
            BenchmarkResult with comprehensive metrics
        """
        self.logger.info(f"Starting performance benchmark for session {session_id}")

        # Clear cache for cold cache testing
        self.decision_cache.clear()

        # Run warm cache operations
        warm_iterations = int(benchmark_iterations * warm_cache_ratio)
        cold_iterations = benchmark_iterations - warm_iterations

        warm_metrics = self._run_benchmark_iterations(session_id, warm_iterations, warm_cache=True)
        cold_metrics = self._run_benchmark_iterations(session_id, cold_iterations, warm_cache=False)

        # Calculate cache hit rate
        total_cache_hits = sum(1 for m in warm_metrics if m.cache_hit)
        cache_hit_rate = total_cache_hits / len(warm_metrics) if warm_metrics else 0.0

        # Validate performance targets
        performance_targets_met = self._validate_benchmark_targets(warm_metrics, cold_metrics)

        # Generate recommendations
        recommendations = self._generate_performance_recommendations(
            warm_metrics, cold_metrics, performance_targets_met
        )

        result = BenchmarkResult(
            benchmark_name=f"Decision Performance Benchmark - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            total_operations=benchmark_iterations,
            warm_cache_metrics=warm_metrics,
            cold_cache_metrics=cold_metrics,
            cache_hit_rate=cache_hit_rate,
            performance_targets_met=performance_targets_met,
            recommendations=recommendations,
        )

        self.logger.info(f"Benchmark completed: {benchmark_iterations} operations")
        self.logger.info(f"Cache hit rate: {cache_hit_rate:.2%}")

        return result

    def _run_benchmark_iterations(self, session_id: str, iterations: int, warm_cache: bool) -> list[PerformanceMetrics]:
        """Run benchmark iterations and collect metrics"""
        metrics = []

        for i in range(iterations):
            # Vary query complexity
            complexity = "simple" if i % 3 == 0 else "medium" if i % 3 == 1 else "complex"

            # Generate test entities based on complexity
            query_entities = self._generate_test_entities(complexity)

            # Run retrieval operation
            start_time = time.time()
            decisions, cache_hit = self.optimize_decision_retrieval(
                session_id=session_id, query_entities=query_entities, use_cache=warm_cache
            )
            execution_time = (time.time() - start_time) * 1000

            # Record metric
            metric = PerformanceMetrics(
                operation_type="decision_retrieval_benchmark",
                timestamp=datetime.now(),
                execution_time_ms=execution_time,
                result_count=len(decisions),
                cache_hit=cache_hit,
                session_id=session_id,
                query_complexity=complexity,
                warm_cache=warm_cache,
            )
            metrics.append(metric)

            # Small delay to avoid overwhelming the system
            if i % 10 == 0:
                time.sleep(0.001)

        return metrics

    def _generate_test_entities(self, complexity: str) -> list[str]:
        """Generate test entities based on complexity"""
        base_entities = ["python", "database", "debug", "performance"]

        if complexity == "simple":
            return [base_entities[0]] if base_entities else []
        elif complexity == "medium":
            return base_entities[:2] if len(base_entities) >= 2 else base_entities
        else:  # complex
            return base_entities

    def _validate_benchmark_targets(
        self, warm_metrics: list[PerformanceMetrics], cold_metrics: list[PerformanceMetrics]
    ) -> dict[str, bool]:
        """Validate if benchmark results meet performance targets"""
        validation = {}

        # Warm cache validation
        if warm_metrics:
            warm_times = [m.execution_time_ms for m in warm_metrics]
            validation.update(
                {
                    "warm_p50_target": statistics.median(warm_times) <= self.performance_targets["warm"]["p50"],
                    "warm_p95_target": self._calculate_percentile(warm_times, 95)
                    <= self.performance_targets["warm"]["p95"],
                    "warm_p99_target": self._calculate_percentile(warm_times, 99)
                    <= self.performance_targets["warm"]["p99"],
                }
            )

        # Cold cache validation
        if cold_metrics:
            cold_times = [m.execution_time_ms for m in cold_metrics]
            validation.update(
                {
                    "cold_p50_target": statistics.median(cold_times) <= self.performance_targets["cold"]["p50"],
                    "cold_p95_target": self._calculate_percentile(cold_times, 95)
                    <= self.performance_targets["cold"]["p95"],
                    "cold_p99_target": self._calculate_percentile(cold_times, 99)
                    <= self.performance_targets["cold"]["p99"],
                }
            )

        return validation

    def _calculate_percentile(self, values: list[float], percentile: int) -> float:
        """Calculate percentile from list of values"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        index = int(percentile / 100 * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _generate_performance_recommendations(
        self,
        warm_metrics: list[PerformanceMetrics],
        cold_metrics: list[PerformanceMetrics],
        targets_met: dict[str, bool],
    ) -> list[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Check warm cache performance
        if warm_metrics:
            warm_times = [m.execution_time_ms for m in warm_metrics]
            avg_warm = statistics.mean(warm_times)

            if avg_warm > 5:
                recommendations.append("Consider optimizing decision retrieval queries for warm cache scenarios")

            if not targets_met.get("warm_p95_target", True):
                recommendations.append("Warm cache p95 latency exceeds 10ms target - investigate query optimization")

        # Check cold cache performance
        if cold_metrics:
            cold_times = [m.execution_time_ms for m in cold_metrics]
            avg_cold = statistics.mean(cold_times)

            if avg_cold > 100:
                recommendations.append(
                    "Cold cache performance needs improvement - consider query optimization and indexing"
                )

            if not targets_met.get("cold_p95_target", True):
                recommendations.append(
                    "Cold cache p95 latency exceeds 150ms target - optimize database queries and indexes"
                )

        # Check cache effectiveness
        warm_cache_hits = sum(1 for m in warm_metrics if m.cache_hit)
        cache_hit_rate = warm_cache_hits / len(warm_metrics) if warm_metrics else 0.0

        if cache_hit_rate < 0.8:
            recommendations.append("Cache hit rate below 80% - consider increasing cache TTL or optimizing cache keys")

        # General recommendations
        if not any(targets_met.values()):
            recommendations.append("Multiple performance targets missed - comprehensive performance review recommended")

        if not recommendations:
            recommendations.append("All performance targets met - system performing well")

        return recommendations

    def detect_performance_regression(self, operation_type: str = "decision_retrieval") -> dict[str, Any] | None:
        """
        Detect performance regression by comparing recent vs historical performance.

        Args:
            operation_type: Type of operation to analyze

        Returns:
            Regression report if detected, None otherwise
        """
        if operation_type not in self.performance_history:
            return None

        metrics = self.performance_history[operation_type]
        if len(metrics) < 20:  # Need sufficient data
            return None

        # Split into recent and historical
        split_point = len(metrics) // 2
        historical = metrics[:split_point]
        recent = metrics[split_point:]

        # Calculate performance statistics
        historical_times = [m.execution_time_ms for m in historical]
        recent_times = [m.execution_time_ms for m in recent]

        historical_avg = statistics.mean(historical_times)
        recent_avg = statistics.mean(recent_times)

        # Check for regression
        if recent_avg > historical_avg * self.regression_threshold:
            return {
                "operation_type": operation_type,
                "regression_detected": True,
                "historical_average_ms": historical_avg,
                "recent_average_ms": recent_avg,
                "degradation_factor": recent_avg / historical_avg,
                "recommendation": "Investigate recent changes that may have caused performance degradation",
            }

        return None

    def get_performance_summary(self, operation_type: str = "decision_retrieval") -> dict[str, Any]:
        """Get performance summary for a specific operation type"""
        if operation_type not in self.performance_history:
            return {}

        metrics = self.performance_history[operation_type]
        if not metrics:
            return {}

        times = [m.execution_time_ms for m in metrics]
        cache_hits = sum(1 for m in metrics if m.cache_hit)

        return {
            "operation_type": operation_type,
            "total_operations": len(metrics),
            "cache_hit_rate": cache_hits / len(metrics),
            "latency_p50_ms": statistics.median(times),
            "latency_p95_ms": self._calculate_percentile(times, 95),
            "latency_p99_ms": self._calculate_percentile(times, 99),
            "average_latency_ms": statistics.mean(times),
            "min_latency_ms": min(times),
            "max_latency_ms": max(times),
            "last_updated": metrics[-1].timestamp.isoformat() if metrics else None,
        }

    def clear_performance_history(self, operation_type: str | None = None) -> None:
        """Clear performance history for specific operation type or all"""
        if operation_type:
            if operation_type in self.performance_history:
                del self.performance_history[operation_type]
        else:
            self.performance_history.clear()

        self.logger.info(f"Performance history cleared for {operation_type or 'all operations'}")

    def export_performance_data(self, filepath: str) -> None:
        """Export performance data to JSON file"""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "performance_targets": self.performance_targets,
                "cache_config": {
                    "ttl_seconds": self.cache_ttl,
                    "max_size": self.max_cache_size,
                    "current_size": len(self.decision_cache),
                },
                "performance_history": {
                    op_type: [
                        {
                            "timestamp": m.timestamp.isoformat(),
                            "execution_time_ms": m.execution_time_ms,
                            "result_count": m.result_count,
                            "cache_hit": m.cache_hit,
                            "session_id": m.session_id,
                            "query_complexity": m.query_complexity,
                            "warm_cache": m.warm_cache,
                        }
                        for m in metrics
                    ]
                    for op_type, metrics in self.performance_history.items()
                },
            }

            with open(filepath, "w") as f:
                json.dump(export_data, f, indent=2)

            self.logger.info(f"Performance data exported to {filepath}")
        except Exception as e:
            self.logger.error(f"Error exporting performance data: {e}")


def create_performance_benchmark_config() -> dict[str, Any]:
    """Create default performance benchmark configuration"""
    return {
        "benchmark_iterations": 100,
        "warm_cache_ratio": 0.7,
        "cache_ttl_seconds": 300,
        "max_cache_size": 1000,
        "regression_threshold": 1.5,
        "performance_targets": {"warm": {"p50": 5, "p95": 10, "p99": 20}, "cold": {"p50": 50, "p95": 150, "p99": 300}},
    }
