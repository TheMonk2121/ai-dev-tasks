#!/usr/bin/env python3.12
"""
Performance Benchmark Script for Critical Scripts

Measures execution time and resource usage of the top 5 most important scripts.
Helps identify optimization opportunities and track performance improvements.

Usage: python scripts/performance_benchmark.py [--script SCRIPT_NAME] [--iterations N]
"""

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Try to import psutil, fallback to basic monitoring if not available
try:
    import psutil  # type: ignore

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  psutil not available. Install with: pip install psutil>=5.9.0")
    print("   Resource monitoring will be limited to basic timing.\n")


@dataclass
class EfficiencyMetrics:
    """Efficiency metrics for test suites and scripts"""

    pass_rate: float
    failure_count: int
    error_count: int
    skipped_count: int
    code_coverage_percent: float
    line_coverage_percent: float
    memory_per_test_mb: float
    cpu_per_test_percent: float
    test_count: int
    avg_test_duration: float
    performance_score: float
    efficiency_score: float
    overall_score: float


@dataclass
class BenchmarkResult:
    script_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    success: bool
    error_message: str | None = None
    timestamp: datetime | None = None
    efficiency_metrics: EfficiencyMetrics | None = None


class ScriptBenchmarker:
    def __init__(self):
        # Use sys.executable to get the current Python interpreter
        import sys

        python_cmd = sys.executable

        self.critical_scripts = {
            "update_cursor_memory": {
                "command": [python_cmd, "scripts/update_cursor_memory.py"],
                "description": "Memory context updater",
            },
            "quick_conflict_check": {
                "command": [python_cmd, "scripts/quick_conflict_check.py", "--json"],
                "description": "Fast conflict detection",
            },
            "quick_conflict_check_optimized": {
                "command": [
                    python_cmd,
                    "scripts/optimized_quick_conflict_check.py",
                    "--json",
                ],
                "description": "Optimized fast conflict detection",
            },
            "process_tasks": {
                "command": [python_cmd, "scripts/process_tasks.py", "status"],
                "description": "Task execution engine",
            },
            "doc_coherence_validator": {
                "command": [
                    python_cmd,
                    "scripts/doc_coherence_validator.py",
                    "--dry-run",
                ],
                "description": "Documentation validator",
            },
            "doc_coherence_validator_optimized": {
                "command": [
                    python_cmd,
                    "scripts/optimized_doc_coherence_validator.py",
                    "--dry-run",
                ],
                "description": "Optimized documentation validator",
            },
            "conflict_audit": {
                "command": [python_cmd, "scripts/conflict_audit.py", "--json"],
                "description": "Comprehensive conflict audit",
            },
            "conflict_audit_optimized": {
                "command": [
                    python_cmd,
                    "scripts/optimized_conflict_audit.py",
                    "--json",
                ],
                "description": "Optimized comprehensive conflict audit",
            },
            # Nemo visualization system scripts
            "wake_up_nemo_parallel": {
                "command": ["./dspy-rag-system/wake_up_nemo.sh", "--parallel"],
                "description": "Wake up Nemo (parallel startup)",
                "timeout": 60,
            },
            "wake_up_nemo_sequential": {
                "command": ["./dspy-rag-system/wake_up_nemo.sh", "--sequential"],
                "description": "Wake up Nemo (sequential startup)",
                "timeout": 120,
            },
            "sleep_nemo_fast": {
                "command": ["./dspy-rag-system/sleep_nemo.sh", "--fast"],
                "description": "Sleep Nemo (fast shutdown)",
                "timeout": 30,
            },
            "sleep_nemo_graceful": {
                "command": ["./dspy-rag-system/sleep_nemo.sh", "--graceful"],
                "description": "Sleep Nemo (graceful shutdown)",
                "timeout": 60,
            },
            "nemo_status": {
                "command": ["./dspy-rag-system/wake_up_nemo.sh", "--status"],
                "description": "Nemo status check",
                "timeout": 10,
            },
            "nemo_api_test": {
                "command": ["./dspy-rag-system/wake_up_nemo.sh", "--test"],
                "description": "Nemo API test",
                "timeout": 15,
            },
        }

        self.results_dir = Path(".cache/benchmarks")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Efficiency scoring thresholds and weights
        self.efficiency_thresholds = {
            "pass_rate": 0.95,  # 95% pass rate target
            "execution_time": 30.0,  # 30 seconds max
            "memory_usage": 100.0,  # 100MB max
            "cpu_usage": 50.0,  # 50% max
            "coverage": 0.80,  # 80% coverage target
        }

        self.weights = {
            "performance": 0.3,
            "quality": 0.4,
            "coverage": 0.2,
            "efficiency": 0.1,
        }

    def get_process_metrics(self):
        """Get current process metrics, with fallback if psutil unavailable."""
        if PSUTIL_AVAILABLE:
            process = psutil.Process()  # type: ignore
            return {
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
            }
        else:
            return {"memory_mb": 0.0, "cpu_percent": 0.0}

    def calculate_performance_score(self, result: BenchmarkResult) -> float:
        """Calculate performance score based on execution time and resource usage"""
        time_score = max(
            0,
            1 - (result.execution_time / self.efficiency_thresholds["execution_time"]),
        )
        memory_score = max(
            0, 1 - (result.memory_usage_mb / self.efficiency_thresholds["memory_usage"])
        )
        cpu_score = max(
            0, 1 - (result.cpu_percent / self.efficiency_thresholds["cpu_usage"])
        )

        return time_score * 0.5 + memory_score * 0.3 + cpu_score * 0.2

    def calculate_quality_score(
        self, result: BenchmarkResult, all_results: list[BenchmarkResult]
    ) -> float:
        """Calculate quality score based on success rate and error handling"""
        if not all_results:
            return 1.0 if result.success else 0.0

        success_rate = sum(1 for r in all_results if r.success) / len(all_results)
        error_penalty = 0.1 if result.error_message else 0.0

        return max(0, success_rate - error_penalty)

    def calculate_coverage_score(self, result: BenchmarkResult) -> float:
        """Calculate coverage score (placeholder for now)"""
        # TODO: Integrate with coverage tools like coverage.py
        return 0.8  # Default 80% coverage assumption

    def calculate_efficiency_metrics(
        self, result: BenchmarkResult, all_results: list[BenchmarkResult]
    ) -> EfficiencyMetrics:
        """Calculate comprehensive efficiency metrics"""
        # Basic metrics
        test_count = len(all_results) if all_results else 1
        success_count = (
            sum(1 for r in all_results if r.success)
            if all_results
            else (1 if result.success else 0)
        )
        pass_rate = success_count / test_count if test_count > 0 else 0.0

        # Performance metrics
        performance_score = self.calculate_performance_score(result)
        quality_score = self.calculate_quality_score(result, all_results)
        coverage_score = self.calculate_coverage_score(result)

        # Efficiency score (resource usage per test)
        memory_per_test = result.memory_usage_mb / test_count
        cpu_per_test = result.cpu_percent / test_count
        avg_duration = result.execution_time / test_count

        # Overall efficiency score
        efficiency_score = (
            performance_score * self.weights["performance"]
            + quality_score * self.weights["quality"]
            + coverage_score * self.weights["coverage"]
        )

        return EfficiencyMetrics(
            pass_rate=pass_rate,
            failure_count=test_count - success_count,
            error_count=1 if result.error_message else 0,
            skipped_count=0,  # TODO: Track skipped tests
            code_coverage_percent=coverage_score * 100,
            line_coverage_percent=coverage_score * 100,
            memory_per_test_mb=memory_per_test,
            cpu_per_test_percent=cpu_per_test,
            test_count=test_count,
            avg_test_duration=avg_duration,
            performance_score=performance_score,
            efficiency_score=efficiency_score,
            overall_score=efficiency_score,
        )

    def benchmark_script(
        self, script_name: str, iterations: int = 1
    ) -> list[BenchmarkResult]:
        """Benchmark a single script multiple times."""
        if script_name not in self.critical_scripts:
            raise ValueError(f"Unknown script: {script_name}")

        script_config = self.critical_scripts[script_name]
        results = []

        print(f"Benchmarking {script_name} ({iterations} iterations)...")

        for i in range(iterations):
            print(f"  Iteration {i+1}/{iterations}...")

            # Start monitoring
            start_time = time.time()
            start_metrics = self.get_process_metrics()

            try:
                # Run the script
                result = subprocess.run(
                    script_config["command"],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                end_time = time.time()
                end_metrics = self.get_process_metrics()

                # For conflict check scripts, consider them successful if they complete
                # even if they find conflicts (non-zero exit code is expected)
                is_success = result.returncode == 0
                if script_name in ["quick_conflict_check", "conflict_audit"]:
                    is_success = result.returncode in [
                        0,
                        1,
                    ]  # 0 = no conflicts, 1 = conflicts found

                benchmark_result = BenchmarkResult(
                    script_name=script_name,
                    execution_time=end_time - start_time,
                    memory_usage_mb=end_metrics["memory_mb"]
                    - start_metrics["memory_mb"],
                    cpu_percent=end_metrics["cpu_percent"],
                    success=is_success,
                    error_message=result.stderr if not is_success else None,
                    timestamp=datetime.now(),
                )

                results.append(benchmark_result)

                if result.returncode != 0:
                    print(f"    ❌ Failed: {result.stderr[:100]}...")
                else:
                    print(f"    ✅ Success: {benchmark_result.execution_time:.2f}s")

                # Calculate efficiency metrics
                benchmark_result.efficiency_metrics = self.calculate_efficiency_metrics(
                    benchmark_result, results
                )

            except subprocess.TimeoutExpired:
                benchmark_result = BenchmarkResult(
                    script_name=script_name,
                    execution_time=300,
                    memory_usage_mb=0,
                    cpu_percent=0,
                    success=False,
                    error_message="Timeout after 5 minutes",
                    timestamp=datetime.now(),
                )
                results.append(benchmark_result)
                print("    ⏰ Timeout")

            except Exception as e:
                benchmark_result = BenchmarkResult(
                    script_name=script_name,
                    execution_time=0,
                    memory_usage_mb=0,
                    cpu_percent=0,
                    success=False,
                    error_message=str(e),
                    timestamp=datetime.now(),
                )
                results.append(benchmark_result)
                print(f"    ❌ Error: {e}")

        return results

    def generate_efficiency_report(self, results: list[BenchmarkResult]) -> dict:
        """Generate comprehensive efficiency report"""
        if not results:
            return {"error": "No results to analyze"}

        # Aggregate metrics
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        avg_execution_time = sum(r.execution_time for r in results) / total_tests
        avg_memory_usage = sum(r.memory_usage_mb for r in results) / total_tests
        avg_cpu_usage = sum(r.cpu_percent for r in results) / total_tests

        # Efficiency scores
        efficiency_scores = [
            r.efficiency_metrics.overall_score for r in results if r.efficiency_metrics
        ]
        avg_efficiency = (
            sum(efficiency_scores) / len(efficiency_scores)
            if efficiency_scores
            else 0.0
        )

        # Performance trends
        performance_scores = [
            r.efficiency_metrics.performance_score
            for r in results
            if r.efficiency_metrics
        ]
        avg_performance = (
            sum(performance_scores) / len(performance_scores)
            if performance_scores
            else 0.0
        )

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": (
                    successful_tests / total_tests if total_tests > 0 else 0.0
                ),
                "avg_execution_time": avg_execution_time,
                "avg_memory_usage_mb": avg_memory_usage,
                "avg_cpu_usage_percent": avg_cpu_usage,
                "avg_efficiency_score": avg_efficiency,
                "avg_performance_score": avg_performance,
            },
            "recommendations": self._generate_recommendations(results),
            "detailed_results": [
                {
                    "script_name": r.script_name,
                    "execution_time": r.execution_time,
                    "memory_usage_mb": r.memory_usage_mb,
                    "cpu_percent": r.cpu_percent,
                    "success": r.success,
                    "efficiency_score": (
                        r.efficiency_metrics.overall_score
                        if r.efficiency_metrics
                        else 0.0
                    ),
                    "performance_score": (
                        r.efficiency_metrics.performance_score
                        if r.efficiency_metrics
                        else 0.0
                    ),
                }
                for r in results
            ],
        }

    def _generate_recommendations(self, results: list[BenchmarkResult]) -> list[str]:
        """Generate improvement recommendations based on results"""
        recommendations = []

        # Check for performance issues
        slow_scripts = [
            r
            for r in results
            if r.execution_time > self.efficiency_thresholds["execution_time"]
        ]
        if slow_scripts:
            recommendations.append(
                f"Consider optimizing {len(slow_scripts)} slow scripts (>30s execution time)"
            )

        # Check for memory issues
        memory_hogs = [
            r
            for r in results
            if r.memory_usage_mb > self.efficiency_thresholds["memory_usage"]
        ]
        if memory_hogs:
            recommendations.append(
                f"Review memory usage in {len(memory_hogs)} scripts (>100MB)"
            )

        # Check for reliability issues
        failed_scripts = [r for r in results if not r.success]
        if failed_scripts:
            recommendations.append(
                f"Investigate {len(failed_scripts)} failed scripts for reliability improvements"
            )

        # Check for efficiency opportunities
        low_efficiency = [
            r
            for r in results
            if r.efficiency_metrics and r.efficiency_metrics.overall_score < 0.7
        ]
        if low_efficiency:
            recommendations.append(
                f"Focus on improving efficiency in {len(low_efficiency)} scripts (score < 0.7)"
            )

        if not recommendations:
            recommendations.append(
                "All scripts are performing well within efficiency targets"
            )

        return recommendations

    def benchmark_all(self, iterations: int = 1) -> dict[str, list[BenchmarkResult]]:
        """Benchmark all critical scripts."""
        all_results = {}

        for script_name in self.critical_scripts:
            all_results[script_name] = self.benchmark_script(script_name, iterations)

        return all_results

    def save_results(
        self, results: dict[str, list[BenchmarkResult]], filename: str | None = None
    ):
        """Save benchmark results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        filepath = self.results_dir / filename

        # Convert results to serializable format
        serializable_results = {}
        for script_name, script_results in results.items():
            serializable_results[script_name] = []
            for result in script_results:
                serializable_results[script_name].append(
                    {
                        "script_name": result.script_name,
                        "execution_time": result.execution_time,
                        "memory_usage_mb": result.memory_usage_mb,
                        "cpu_percent": result.cpu_percent,
                        "success": result.success,
                        "error_message": result.error_message,
                        "timestamp": (
                            result.timestamp.isoformat() if result.timestamp else None
                        ),
                    }
                )

        with open(filepath, "w") as f:
            json.dump(serializable_results, f, indent=2)

        print(f"Results saved to: {filepath}")
        return filepath

    def print_summary(self, results: dict[str, list[BenchmarkResult]]):
        """Print a summary of benchmark results."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        for script_name, script_results in results.items():
            if not script_results:
                continue

            successful_runs = [r for r in script_results if r.success]
            failed_runs = [r for r in script_results if not r.success]

            if successful_runs:
                avg_time = sum(r.execution_time for r in successful_runs) / len(
                    successful_runs
                )
                avg_memory = sum(r.memory_usage_mb for r in successful_runs) / len(
                    successful_runs
                )
                min_time = min(r.execution_time for r in successful_runs)
                max_time = max(r.execution_time for r in successful_runs)

                print(f"\n📊 {script_name}:")
                print(
                    f"   ✅ Successful runs: {len(successful_runs)}/{len(script_results)}"
                )
                print(
                    f"   ⏱️  Avg time: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)"
                )
                print(f"   💾 Avg memory: {avg_memory:.1f}MB")

                if failed_runs:
                    print(f"   ❌ Failed runs: {len(failed_runs)}")
                    for failed in failed_runs:
                        print(f"      - {failed.error_message}")
            else:
                print(f"\n❌ {script_name}: All runs failed")
                for failed in failed_runs:
                    print(f"   - {failed.error_message}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark critical scripts performance"
    )
    parser.add_argument("--script", help="Benchmark specific script only")
    parser.add_argument(
        "--iterations", type=int, default=3, help="Number of iterations per script"
    )
    parser.add_argument("--save", help="Save results to specific filename")

    args = parser.parse_args()

    benchmarker = ScriptBenchmarker()

    if args.script:
        if args.script not in benchmarker.critical_scripts:
            print(f"Unknown script: {args.script}")
            print(f"Available scripts: {list(benchmarker.critical_scripts.keys())}")
            return

        results = {
            args.script: benchmarker.benchmark_script(args.script, args.iterations)
        }
    else:
        results = benchmarker.benchmark_all(args.iterations)

    benchmarker.print_summary(results)

    # Generate and display efficiency report
    print("\n" + "=" * 60)
    print("EFFICIENCY ANALYSIS")
    print("=" * 60)

    # Flatten all results for efficiency analysis
    all_results = []
    for script_results in results.values():
        all_results.extend(script_results)

    efficiency_report = benchmarker.generate_efficiency_report(all_results)

    # Display summary
    summary = efficiency_report["summary"]
    print(f"\n📈 Overall Efficiency Score: {summary['avg_efficiency_score']:.3f}")
    print(f"🚀 Performance Score: {summary['avg_performance_score']:.3f}")
    print(f"✅ Success Rate: {summary['success_rate']:.1%}")
    print(f"⏱️  Avg Execution Time: {summary['avg_execution_time']:.2f}s")
    print(f"💾 Avg Memory Usage: {summary['avg_memory_usage_mb']:.1f}MB")

    # Display recommendations
    print("\n💡 Recommendations:")
    for rec in efficiency_report["recommendations"]:
        print(f"   • {rec}")

    # Display top performers
    detailed_results = efficiency_report["detailed_results"]
    top_performers = sorted(
        detailed_results, key=lambda x: x["efficiency_score"], reverse=True
    )[:3]
    print("\n🏆 Top Performers:")
    for i, result in enumerate(top_performers, 1):
        print(f"   {i}. {result['script_name']}: {result['efficiency_score']:.3f}")

    if args.save:
        benchmarker.save_results(results, args.save)
    else:
        benchmarker.save_results(results)


if __name__ == "__main__":
    main()
