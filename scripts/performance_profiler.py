#!/usr/bin/env python3
"""
Performance Profiler for RAGChecker Pydantic Integration

Profiles validation performance and identifies bottlenecks for optimization.
"""

import cProfile
import io
import pstats
import time
from dataclasses import dataclass
from typing import Any, Dict, List

from ragchecker_constitution_validation import (
    create_constitution_aware_input,
    create_constitution_aware_metrics,
    create_constitution_aware_result,
)
from ragchecker_error_taxonomy import (
    create_error_taxonomy_aware_input,
    create_error_taxonomy_aware_metrics,
    create_error_taxonomy_aware_result,
)

# Import the models we want to profile
from ragchecker_pydantic_models import (
    create_ragchecker_input,
    create_ragchecker_metrics,
    create_ragchecker_result,
)


@dataclass
class PerformanceMetrics:
    """Performance metrics for validation"""

    operation: str
    iterations: int
    total_time: float
    avg_time: float
    overhead_percent: float
    memory_usage: float = 0.0


class PerformanceProfiler:
    """Profiles performance of RAGChecker validation systems"""

    def __init__(self):
        """Initialize profiler"""
        self.metrics: List[PerformanceMetrics] = []
        self.profiler = cProfile.Profile()

    def profile_operation(self, operation_name: str, operation_func, iterations: int = 1000) -> PerformanceMetrics:
        """Profile a specific operation"""
        print(f"🧪 Profiling {operation_name} with {iterations} iterations...")

        # Warm up
        for _ in range(10):
            operation_func()

        # Profile the operation
        self.profiler.enable()
        start_time = time.time()

        for _ in range(iterations):
            operation_func()

        end_time = time.time()
        self.profiler.disable()

        total_time = end_time - start_time
        avg_time = total_time / iterations

        # Calculate overhead (assuming baseline is 0.001ms per operation)
        baseline_time = 0.001 * iterations
        overhead_percent = ((total_time - baseline_time) / baseline_time) * 100 if baseline_time > 0 else 0

        metrics = PerformanceMetrics(
            operation=operation_name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            overhead_percent=overhead_percent,
        )

        self.metrics.append(metrics)
        print(f"✅ {operation_name}: {avg_time:.6f}s avg, {overhead_percent:.2f}% overhead")

        return metrics

    def get_profile_stats(self) -> str:
        """Get detailed profile statistics"""
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 functions
        return s.getvalue()

    def compare_implementations(self) -> Dict[str, Any]:
        """Compare performance of different implementations"""
        print("🚀 Comparing RAGChecker Implementation Performance")
        print("=" * 60)

        # Test data
        test_input_data = {
            "query_id": "test_001",
            "query": "What is RAGChecker?",
            "gt_answer": "RAGChecker is an evaluation framework.",
            "response": "RAGChecker evaluates RAG systems.",
            "retrieved_context": ["context1", "context2"],
        }

        test_metrics_data = {
            "precision": 0.8,
            "recall": 0.7,
            "f1_score": 0.75,
            "claim_recall": 0.8,
            "context_precision": 0.9,
            "context_utilization": 0.85,
            "noise_sensitivity": 0.2,
            "hallucination": 0.1,
            "self_knowledge": 0.9,
            "faithfulness": 0.95,
        }

        test_result_data = {
            "test_case_name": "test_case_001",
            "query": "What is RAGChecker?",
            "custom_score": 0.85,
            "ragchecker_scores": {"precision": 0.8, "recall": 0.7},
            "ragchecker_overall": 0.75,
            "comparison": {"difference": 0.1},
            "recommendation": "Improve recall by enhancing retrieval system",
        }

        # Profile basic Pydantic models
        basic_input_metrics = self.profile_operation(
            "Basic Pydantic Input", lambda: create_ragchecker_input(**test_input_data), iterations=1000
        )

        basic_metrics_metrics = self.profile_operation(
            "Basic Pydantic Metrics", lambda: create_ragchecker_metrics(**test_metrics_data), iterations=1000
        )

        basic_result_metrics = self.profile_operation(
            "Basic Pydantic Result", lambda: create_ragchecker_result(**test_result_data), iterations=1000
        )

        # Profile constitution-aware models
        constitution_input_metrics = self.profile_operation(
            "Constitution-Aware Input", lambda: create_constitution_aware_input(**test_input_data), iterations=1000
        )

        constitution_metrics_metrics = self.profile_operation(
            "Constitution-Aware Metrics",
            lambda: create_constitution_aware_metrics(**test_metrics_data),
            iterations=1000,
        )

        constitution_result_metrics = self.profile_operation(
            "Constitution-Aware Result", lambda: create_constitution_aware_result(**test_result_data), iterations=1000
        )

        # Profile error taxonomy models
        error_taxonomy_input_metrics = self.profile_operation(
            "Error Taxonomy Input", lambda: create_error_taxonomy_aware_input(**test_input_data), iterations=1000
        )

        error_taxonomy_metrics_metrics = self.profile_operation(
            "Error Taxonomy Metrics", lambda: create_error_taxonomy_aware_metrics(**test_metrics_data), iterations=1000
        )

        error_taxonomy_result_metrics = self.profile_operation(
            "Error Taxonomy Result", lambda: create_error_taxonomy_aware_result(**test_result_data), iterations=1000
        )

        # Calculate relative performance
        comparison = {
            "basic_pydantic": {
                "input": basic_input_metrics,
                "metrics": basic_metrics_metrics,
                "result": basic_result_metrics,
                "total_avg_time": (
                    basic_input_metrics.avg_time + basic_metrics_metrics.avg_time + basic_result_metrics.avg_time
                )
                / 3,
            },
            "constitution_aware": {
                "input": constitution_input_metrics,
                "metrics": constitution_metrics_metrics,
                "result": constitution_result_metrics,
                "total_avg_time": (
                    constitution_input_metrics.avg_time
                    + constitution_metrics_metrics.avg_time
                    + constitution_result_metrics.avg_time
                )
                / 3,
            },
            "error_taxonomy": {
                "input": error_taxonomy_input_metrics,
                "metrics": error_taxonomy_metrics_metrics,
                "result": error_taxonomy_result_metrics,
                "total_avg_time": (
                    error_taxonomy_input_metrics.avg_time
                    + error_taxonomy_metrics_metrics.avg_time
                    + error_taxonomy_result_metrics.avg_time
                )
                / 3,
            },
        }

        # Calculate overhead relative to basic Pydantic
        basic_avg = comparison["basic_pydantic"]["total_avg_time"]
        constitution_overhead = ((comparison["constitution_aware"]["total_avg_time"] - basic_avg) / basic_avg) * 100
        error_taxonomy_overhead = ((comparison["error_taxonomy"]["total_avg_time"] - basic_avg) / basic_avg) * 100

        comparison["overhead_analysis"] = {
            "constitution_aware_overhead": constitution_overhead,
            "error_taxonomy_overhead": error_taxonomy_overhead,
            "total_overhead": error_taxonomy_overhead,
        }

        print("\n📊 Performance Comparison Summary:")
        print(f"Basic Pydantic: {basic_avg:.6f}s avg")
        print(f"Constitution-Aware: +{constitution_overhead:.2f}% overhead")
        print(f"Error Taxonomy: +{error_taxonomy_overhead:.2f}% overhead")

        return comparison

    def generate_optimization_recommendations(self, comparison: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on performance analysis"""
        recommendations = []

        total_overhead = comparison["overhead_analysis"]["total_overhead"]

        if total_overhead > 3.0:
            recommendations.append(f"⚠️ Total overhead {total_overhead:.2f}% exceeds 3% target - optimization needed")

        if comparison["overhead_analysis"]["error_taxonomy_overhead"] > 10.0:
            recommendations.append("🔧 Error taxonomy overhead is high - consider lazy validation")

        if comparison["overhead_analysis"]["constitution_aware_overhead"] > 5.0:
            recommendations.append("🔧 Constitution validation overhead is high - consider caching")

        # Check individual component performance
        for impl_name, impl_data in comparison.items():
            if impl_name == "overhead_analysis":
                continue

            for component_name, metrics in impl_data.items():
                if component_name == "total_avg_time":
                    continue

                if metrics.avg_time > 0.001:  # More than 1ms
                    recommendations.append(
                        f"🔧 {impl_name} {component_name} is slow ({metrics.avg_time:.6f}s) - profile for bottlenecks"
                    )

        if not recommendations:
            recommendations.append("✅ Performance is within acceptable limits")

        return recommendations


def main():
    """Run performance profiling"""
    profiler = PerformanceProfiler()

    # Run performance comparison
    comparison = profiler.compare_implementations()

    # Generate recommendations
    recommendations = profiler.generate_optimization_recommendations(comparison)

    print("\n🎯 Optimization Recommendations:")
    for rec in recommendations:
        print(f"  {rec}")

    # Show detailed profile stats if overhead is high
    if comparison["overhead_analysis"]["total_overhead"] > 3.0:
        print("\n📋 Detailed Profile Statistics:")
        print(profiler.get_profile_stats())

    return comparison, recommendations


if __name__ == "__main__":
    main()
