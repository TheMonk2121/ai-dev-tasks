#!/usr/bin/env python3
"""
Performance Monitor for RAGChecker Pydantic Integration

Tracks validation overhead over time and provides alerts when performance degrades.
"""

import json
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

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

# Import the models we want to monitor
from ragchecker_pydantic_models import create_ragchecker_input, create_ragchecker_metrics, create_ragchecker_result


@dataclass
class PerformanceRecord:
    """Performance record for a single validation operation"""

    timestamp: str
    operation: str
    duration: float
    overhead_percent: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PerformanceSummary:
    """Performance summary for a time period"""

    start_time: str
    end_time: str
    total_operations: int
    avg_duration: float
    avg_overhead: float
    success_rate: float
    error_count: int
    performance_trend: str  # "improving", "stable", "degrading"


class PerformanceMonitor:
    """Monitors performance of RAGChecker validation systems"""

    def __init__(self, data_file: str = "performance_data.json"):
        """Initialize performance monitor"""
        self.data_file = Path(data_file)
        self.records: List[PerformanceRecord] = []
        self.alert_thresholds = {
            "overhead_threshold": 3.0,  # 3% overhead threshold
            "duration_threshold": 0.001,  # 1ms duration threshold
            "error_rate_threshold": 0.05,  # 5% error rate threshold
        }
        self._load_data()

    def _load_data(self) -> None:
        """Load performance data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.records = [PerformanceRecord(**record) for record in data.get("records", [])]
            except Exception as e:
                print(f"Warning: Could not load performance data: {e}")

    def _save_data(self) -> None:
        """Save performance data to file"""
        try:
            data = {"records": [asdict(record) for record in self.records], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save performance data: {e}")

    def record_operation(
        self,
        operation: str,
        duration: float,
        overhead_percent: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Record a performance measurement"""
        record = PerformanceRecord(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            duration=duration,
            overhead_percent=overhead_percent,
            success=success,
            error_message=error_message,
        )

        self.records.append(record)

        # Keep only last 1000 records to prevent file from growing too large
        if len(self.records) > 1000:
            self.records = self.records[-1000:]

        self._save_data()

    def benchmark_operation(self, operation_name: str, operation_func, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark a specific operation"""
        print(f"🧪 Benchmarking {operation_name}...")

        durations = []
        overheads = []
        errors = 0

        for i in range(iterations):
            try:
                start_time = time.time()
                operation_func()
                end_time = time.time()

                duration = end_time - start_time
                durations.append(duration)

                # Calculate overhead (assuming baseline is 0.0001s)
                baseline = 0.0001
                overhead = ((duration - baseline) / baseline) * 100 if baseline > 0 else 0
                overheads.append(overhead)

                # Record the operation
                self.record_operation(operation_name, duration, overhead, success=True)

            except Exception as e:
                errors += 1
                self.record_operation(operation_name, 0.0, 0.0, success=False, error_message=str(e))

        avg_duration = statistics.mean(durations) if durations else 0.0
        avg_overhead = statistics.mean(overheads) if overheads else 0.0
        success_rate = (iterations - errors) / iterations

        results = {
            "operation": operation_name,
            "iterations": iterations,
            "avg_duration": avg_duration,
            "avg_overhead": avg_overhead,
            "success_rate": success_rate,
            "error_count": errors,
        }

        print(
            f"✅ {operation_name}: {avg_duration:.6f}s avg, {avg_overhead:.2f}% overhead, {success_rate:.1%} success rate"
        )

        return results

    def run_performance_suite(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark suite"""
        print("🚀 Running Performance Benchmark Suite")
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

        # Benchmark all operations
        benchmarks = {}

        # Basic Pydantic models
        benchmarks["basic_input"] = self.benchmark_operation(
            "Basic Pydantic Input", lambda: create_ragchecker_input(**test_input_data)
        )

        benchmarks["basic_metrics"] = self.benchmark_operation(
            "Basic Pydantic Metrics", lambda: create_ragchecker_metrics(**test_metrics_data)
        )

        benchmarks["basic_result"] = self.benchmark_operation(
            "Basic Pydantic Result", lambda: create_ragchecker_result(**test_result_data)
        )

        # Constitution-aware models
        benchmarks["constitution_input"] = self.benchmark_operation(
            "Constitution-Aware Input", lambda: create_constitution_aware_input(**test_input_data)
        )

        benchmarks["constitution_metrics"] = self.benchmark_operation(
            "Constitution-Aware Metrics", lambda: create_constitution_aware_metrics(**test_metrics_data)
        )

        benchmarks["constitution_result"] = self.benchmark_operation(
            "Constitution-Aware Result", lambda: create_constitution_aware_result(**test_result_data)
        )

        # Error taxonomy models
        benchmarks["error_taxonomy_input"] = self.benchmark_operation(
            "Error Taxonomy Input", lambda: create_error_taxonomy_aware_input(**test_input_data)
        )

        benchmarks["error_taxonomy_metrics"] = self.benchmark_operation(
            "Error Taxonomy Metrics", lambda: create_error_taxonomy_aware_metrics(**test_metrics_data)
        )

        benchmarks["error_taxonomy_result"] = self.benchmark_operation(
            "Error Taxonomy Result", lambda: create_error_taxonomy_aware_result(**test_result_data)
        )

        # Calculate summary statistics
        all_durations = [b["avg_duration"] for b in benchmarks.values()]
        all_overheads = [b["avg_overhead"] for b in benchmarks.values()]
        all_success_rates = [b["success_rate"] for b in benchmarks.values()]

        summary = {
            "total_operations": len(benchmarks),
            "avg_duration": statistics.mean(all_durations),
            "avg_overhead": statistics.mean(all_overheads),
            "avg_success_rate": statistics.mean(all_success_rates),
            "max_overhead": max(all_overheads),
            "min_overhead": min(all_overheads),
            "benchmarks": benchmarks,
        }

        print("\n📊 Performance Summary:")
        print(f"Average Duration: {summary['avg_duration']:.6f}s")
        print(f"Average Overhead: {summary['avg_overhead']:.2f}%")
        print(f"Average Success Rate: {summary['avg_success_rate']:.1%}")
        print(f"Overhead Range: {summary['min_overhead']:.2f}% - {summary['max_overhead']:.2f}%")

        return summary

    def get_performance_summary(self, hours: int = 24) -> PerformanceSummary:
        """Get performance summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_records = [record for record in self.records if datetime.fromisoformat(record.timestamp) > cutoff_time]

        if not recent_records:
            return PerformanceSummary(
                start_time=cutoff_time.isoformat(),
                end_time=datetime.now().isoformat(),
                total_operations=0,
                avg_duration=0.0,
                avg_overhead=0.0,
                success_rate=1.0,
                error_count=0,
                performance_trend="stable",
            )

        durations = [r.duration for r in recent_records if r.success]
        overheads = [r.overhead_percent for r in recent_records if r.success]
        success_count = sum(1 for r in recent_records if r.success)
        error_count = sum(1 for r in recent_records if not r.success)

        avg_duration = statistics.mean(durations) if durations else 0.0
        avg_overhead = statistics.mean(overheads) if overheads else 0.0
        success_rate = success_count / len(recent_records)

        # Determine performance trend
        if len(recent_records) >= 20:
            first_half = recent_records[: len(recent_records) // 2]
            second_half = recent_records[len(recent_records) // 2 :]

            first_avg = statistics.mean([r.duration for r in first_half if r.success])
            second_avg = statistics.mean([r.duration for r in second_half if r.success])

            if second_avg < first_avg * 0.9:
                trend = "improving"
            elif second_avg > first_avg * 1.1:
                trend = "degrading"
            else:
                trend = "stable"
        else:
            trend = "stable"

        return PerformanceSummary(
            start_time=cutoff_time.isoformat(),
            end_time=datetime.now().isoformat(),
            total_operations=len(recent_records),
            avg_duration=avg_duration,
            avg_overhead=avg_overhead,
            success_rate=success_rate,
            error_count=error_count,
            performance_trend=trend,
        )

    def check_alerts(self) -> List[str]:
        """Check for performance alerts"""
        alerts = []
        summary = self.get_performance_summary()

        if summary.avg_overhead > self.alert_thresholds["overhead_threshold"]:
            alerts.append(
                f"⚠️ High overhead detected: {summary.avg_overhead:.2f}% (threshold: {self.alert_thresholds['overhead_threshold']}%)"
            )

        if summary.avg_duration > self.alert_thresholds["duration_threshold"]:
            alerts.append(
                f"⚠️ Slow performance detected: {summary.avg_duration:.6f}s (threshold: {self.alert_thresholds['duration_threshold']}s)"
            )

        if summary.success_rate < (1 - self.alert_thresholds["error_rate_threshold"]):
            alerts.append(
                f"⚠️ High error rate detected: {(1-summary.success_rate)*100:.1f}% (threshold: {self.alert_thresholds['error_rate_threshold']*100}%)"
            )

        if summary.performance_trend == "degrading":
            alerts.append("⚠️ Performance is degrading over time")

        return alerts

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        summary = self.get_performance_summary()
        alerts = self.check_alerts()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": asdict(summary),
            "alerts": alerts,
            "alert_count": len(alerts),
            "recommendations": self._generate_recommendations(summary, alerts),
        }

        return report

    def _generate_recommendations(self, summary: PerformanceSummary, alerts: List[str]) -> List[str]:
        """Generate recommendations based on performance data"""
        recommendations = []

        if summary.avg_overhead > 3.0:
            recommendations.append("🔧 Consider implementing validation caching to reduce overhead")

        if summary.avg_duration > 0.001:
            recommendations.append("🔧 Profile validation bottlenecks and optimize slow operations")

        if summary.success_rate < 0.95:
            recommendations.append("🔧 Investigate validation errors and improve error handling")

        if summary.performance_trend == "degrading":
            recommendations.append("🔧 Monitor system resources and check for memory leaks")

        if not recommendations:
            recommendations.append("✅ Performance is within acceptable limits")

        return recommendations


def main():
    """Run performance monitoring"""
    monitor = PerformanceMonitor()

    # Run performance suite
    suite_results = monitor.run_performance_suite()

    # Generate report
    report = monitor.generate_report()

    print("\n📋 Performance Report:")
    print(f"Total Operations: {report['summary']['total_operations']}")
    print(f"Average Duration: {report['summary']['avg_duration']:.6f}s")
    print(f"Average Overhead: {report['summary']['avg_overhead']:.2f}%")
    print(f"Success Rate: {report['summary']['success_rate']:.1%}")
    print(f"Performance Trend: {report['summary']['performance_trend']}")

    if report["alerts"]:
        print(f"\n🚨 Alerts ({report['alert_count']}):")
        for alert in report["alerts"]:
            print(f"  {alert}")

    print("\n🎯 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")

    return report


if __name__ == "__main__":
    main()
