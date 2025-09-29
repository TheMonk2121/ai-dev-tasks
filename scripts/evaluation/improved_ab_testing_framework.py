#!/usr/bin/env python3
"""
Improved A/B Testing Framework for RAGChecker Evaluation

Uses reusable API instead of subprocesses and supports bounded parallelism.
Provides direct integration with evaluation components for better performance.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np  # type: ignore[import-untyped]

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import evaluation modules after path setup
try:
    from scripts.evaluation.governance_gating_system import (
        GovernanceGatingSystem,  # type: ignore[import-untyped]
    )
    from scripts.evaluation.health_check_helpers import (
        HealthCheckHelpers,  # type: ignore[import-untyped]
    )
    from scripts.evaluation.streamlined_nightly_smoke import (
        StreamlinedNightlySmoke,  # type: ignore[import-untyped]
    )
except ImportError:
    # Create dummy classes for when imports fail
    class GovernanceGatingSystem:  # type: ignore
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ImportError("GovernanceGatingSystem not available")
    
    class HealthCheckHelpers:  # type: ignore
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ImportError("HealthCheckHelpers not available")
        
        def run_comprehensive_health_checks(self, *_args: Any, **_kwargs: Any) -> Any:
            raise ImportError("HealthCheckHelpers not available")
        
        def get_health_summary(self, *_args: Any, **_kwargs: Any) -> Any:
            raise ImportError("HealthCheckHelpers not available")
    
    class StreamlinedNightlySmoke:  # type: ignore
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise ImportError("StreamlinedNightlySmoke not available")
        
        def run_nightly_smoke_evaluation(self, *_args: Any, **_kwargs: Any) -> Any:
            raise ImportError("StreamlinedNightlySmoke not available")


@dataclass
class EvaluationConfig:
    """Configuration for a single evaluation run."""
    name: str
    scenario: str
    profile: str
    model: str | None = None
    fusion_weights: dict[str, float] | None = None
    output_file: str | None = None
    description: str = ""
    max_workers: int = 3
    timeout_seconds: int = 300


@dataclass
class EvaluationResults:
    """Results from a single evaluation run."""
    config_name: str
    precision: float
    recall: float
    f1: float
    latency_ms: float
    cases: int
    total_time_ms: float
    output_file: str
    timestamp: float
    success: bool
    error_message: str | None = None


class ImprovedABTestingFramework:
    """Improved A/B testing framework with reusable API and bounded parallelism."""
    
    def __init__(self, max_workers: int = 3, timeout_seconds: int = 300):
        self.max_workers: int = max_workers
        self.timeout_seconds: int = timeout_seconds
        self.health_helpers: HealthCheckHelpers = HealthCheckHelpers()
        self.governance_system: GovernanceGatingSystem = GovernanceGatingSystem("mock")
        
    def run_ab_test(self, baseline_config: EvaluationConfig, 
                   test_configs: list[EvaluationConfig],
                   output_dir: str = "metrics/ab_tests") -> dict[str, Any]:
        """Run A/B test comparing baseline against test configurations."""
        print("🧪 Starting Improved A/B Testing Framework")
        print("=" * 60)
        
        start_time = time.time()
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Run evaluations in parallel with bounded concurrency
        all_configs = [baseline_config] + test_configs
        results = self._run_evaluations_parallel(all_configs, output_path)
        
        # Analyze results
        analysis = self._analyze_results(results, baseline_config.name)
        
        # Generate comprehensive report
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration": time.time() - start_time,
            "baseline_config": asdict(baseline_config),
            "test_configs": [asdict(config) for config in test_configs],
            "results": [asdict(result) for result in results],
            "analysis": analysis,
            "summary": self._generate_summary(analysis),
        }
        
        # Save report
        report_file = output_path / f"ab_test_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _run_evaluations_parallel(self, configs: list[EvaluationConfig], 
                                 output_path: Path) -> list[EvaluationResults]:
        """Run evaluations in parallel with bounded concurrency."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all evaluation tasks
            future_to_config = {
                executor.submit(self._run_single_evaluation, config, output_path): config
                for config in configs
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_config, timeout=self.timeout_seconds):
                config = future_to_config[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ {config.name}: {result.f1:.3f} F1")
                except Exception as e:
                    print(f"❌ {config.name}: Failed - {e}")
                    # Create error result
                    error_result = EvaluationResults(
                        config_name=config.name,
                        precision=0.0,
                        recall=0.0,
                        f1=0.0,
                        latency_ms=0.0,
                        cases=0,
                        total_time_ms=0.0,
                        output_file="",
                        timestamp=time.time(),
                        success=False,
                        error_message=str(e)
                    )
                    results.append(error_result)
        
        return results
    
    def _run_single_evaluation(self, config: EvaluationConfig, 
                              output_path: Path) -> EvaluationResults:
        """Run a single evaluation using the reusable API."""
        start_time = time.time()
        
        try:
            # Set up environment for this configuration
            self._setup_evaluation_environment(config)
            
            # Run health checks first
            health_checks = self.health_helpers.run_comprehensive_health_checks()
            health_summary = self.health_helpers.get_health_summary(health_checks)
            
            if not health_summary["overall_healthy"]:
                raise RuntimeError(f"Health checks failed: {health_summary['failed_checks']} failures")
            
            # Run streamlined evaluation
            smoke_evaluator = StreamlinedNightlySmoke(str(output_path / config.name))
            smoke_result = smoke_evaluator.run_nightly_smoke_evaluation()
            
            # Extract metrics from smoke result
            summary = smoke_result.get("summary", {})
            success_rate = float(summary.get("success_rate", 0.0)) / 100.0
            precision = success_rate
            recall = success_rate
            f1 = success_rate
            cases = int(summary.get("total_tests", 0))
            
            # Calculate latency
            total_time = time.time() - start_time
            latency_ms = (total_time / cases) * 1000 if cases > 0 else 0.0
            
            # Save detailed results
            output_file = output_path / f"{config.name}_detailed_results.json"
            with open(output_file, "w") as f:
                json.dump(smoke_result, f, indent=2)
            
            return EvaluationResults(
                config_name=config.name,
                precision=precision,
                recall=recall,
                f1=f1,
                latency_ms=latency_ms,
                cases=cases,
                total_time_ms=total_time * 1000,
                output_file=str(output_file),
                timestamp=time.time(),
                success=True
            )
            
        except Exception as e:
            return EvaluationResults(
                config_name=config.name,
                precision=0.0,
                recall=0.0,
                f1=0.0,
                latency_ms=0.0,
                cases=0,
                total_time_ms=(time.time() - start_time) * 1000,
                output_file="",
                timestamp=time.time(),
                success=False,
                error_message=str(e)
            )
    
    def _setup_evaluation_environment(self, config: EvaluationConfig):
        """Set up environment variables for the evaluation configuration."""
        # Set profile-specific environment
        os.environ["EVAL_PROFILE"] = config.profile
        os.environ["EVAL_DRIVER"] = "dspy_rag" if config.profile != "mock" else "synthetic"
        os.environ["RAGCHECKER_USE_REAL_RAG"] = "1" if config.profile != "mock" else "0"
        
        # Set model-specific environment
        if config.model:
            os.environ["DSPY_MODEL"] = config.model
        
        # Set fusion weights if provided
        if config.fusion_weights:
            for key, value in config.fusion_weights.items():
                os.environ[f"FUSION_{key.upper()}"] = str(value)
        
        # Set other configuration
        os.environ["RETR_TOPK_VEC"] = "50"
        os.environ["RETR_TOPK_BM25"] = "50"
        os.environ["RERANK_ENABLE"] = "1"
    
    def _analyze_results(self, results: list[EvaluationResults], 
                        baseline_name: str) -> dict[str, Any]:
        """Analyze A/B test results with statistical significance testing."""
        # Find baseline result
        baseline_result = next((r for r in results if r.config_name == baseline_name), None)
        if not baseline_result:
            return {"error": "Baseline result not found"}
        
        # Compare each test configuration against baseline
        comparisons = []
        for result in results:
            if result.config_name == baseline_name:
                continue
            
            if not result.success:
                comparisons.append({
                    "test_name": result.config_name,
                    "status": "failed",
                    "error": result.error_message
                })
                continue
            
            # Calculate improvements
            precision_improvement = result.precision - baseline_result.precision
            recall_improvement = result.recall - baseline_result.recall
            f1_improvement = result.f1 - baseline_result.f1
            latency_change = result.latency_ms - baseline_result.latency_ms
            
            # Statistical significance (simplified - would need more data for real significance)
            significance = self._calculate_significance(baseline_result, result)
            
            comparisons.append({
                "test_name": result.config_name,
                "status": "success",
                "precision_improvement": precision_improvement,
                "recall_improvement": recall_improvement,
                "f1_improvement": f1_improvement,
                "latency_change": latency_change,
                "significance": significance,
                "baseline_metrics": {
                    "precision": baseline_result.precision,
                    "recall": baseline_result.recall,
                    "f1": baseline_result.f1,
                    "latency_ms": baseline_result.latency_ms
                },
                "test_metrics": {
                    "precision": result.precision,
                    "recall": result.recall,
                    "f1": result.f1,
                    "latency_ms": result.latency_ms
                }
            })
        
        return {
            "baseline_name": baseline_name,
            "baseline_metrics": {
                "precision": baseline_result.precision,
                "recall": baseline_result.recall,
                "f1": baseline_result.f1,
                "latency_ms": baseline_result.latency_ms,
                "cases": baseline_result.cases
            },
            "comparisons": comparisons,
            "total_tests": len(comparisons),
            "successful_tests": sum(1 for c in comparisons if c["status"] == "success"),
            "failed_tests": sum(1 for c in comparisons if c["status"] == "failed")
        }
    
    def _calculate_significance(self, baseline: EvaluationResults, 
                              test: EvaluationResults) -> dict[str, Any]:
        """Calculate statistical significance of differences."""
        # Simplified significance calculation
        # In a real implementation, you'd need multiple runs for proper statistical testing
        
        f1_improvement = test.f1 - baseline.f1
        precision_improvement = test.precision - baseline.precision
        recall_improvement = test.recall - baseline.recall
        
        # Simple thresholds for "significant" improvement
        f1_significant = abs(f1_improvement) > 0.05  # 5% improvement
        precision_significant = abs(precision_improvement) > 0.05
        recall_significant = abs(recall_improvement) > 0.05
        
        return {
            "f1_significant": f1_significant,
            "precision_significant": precision_significant,
            "recall_significant": recall_significant,
            "overall_significant": f1_significant or precision_significant or recall_significant,
            "f1_improvement": f1_improvement,
            "precision_improvement": precision_improvement,
            "recall_improvement": recall_improvement
        }
    
    def _generate_summary(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Generate summary of A/B test results."""
        if "error" in analysis:
            return {"status": "error", "message": analysis["error"]}
        
        comparisons = analysis.get("comparisons", [])
        successful_tests = [c for c in comparisons if c["status"] == "success"]
        
        # Find best performing test
        best_test = None
        if successful_tests:
            best_test = max(successful_tests, key=lambda x: x.get("f1_improvement", 0))
        
        # Calculate overall improvements
        if successful_tests:
            avg_f1_improvement = float(np.mean([c.get("f1_improvement", 0.0) for c in successful_tests]))
            avg_precision_improvement = float(np.mean([c.get("precision_improvement", 0.0) for c in successful_tests]))
            avg_recall_improvement = float(np.mean([c.get("recall_improvement", 0.0) for c in successful_tests]))
        else:
            avg_f1_improvement = 0.0
            avg_precision_improvement = 0.0
            avg_recall_improvement = 0.0
        
        return {
            "status": "success",
            "total_tests": analysis.get("total_tests", 0),
            "successful_tests": analysis.get("successful_tests", 0),
            "failed_tests": analysis.get("failed_tests", 0),
            "best_test": best_test["test_name"] if best_test else None,
            "best_f1_improvement": best_test.get("f1_improvement", 0) if best_test else 0,
            "avg_f1_improvement": avg_f1_improvement,
            "avg_precision_improvement": avg_precision_improvement,
            "avg_recall_improvement": avg_recall_improvement,
        }
    
    def _print_summary(self, report: dict[str, Any]):
        """Print comprehensive A/B test summary."""
        print("\n" + "=" * 60)
        print("🧪 A/B TEST SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        if summary["status"] == "error":
            print(f"❌ Error: {summary['message']}")
            return
        
        print(f"📊 Total Tests: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        
        if summary["best_test"]:
            print(f"🏆 Best Test: {summary['best_test']}")
            print(f"📈 Best F1 Improvement: {summary['best_f1_improvement']:.3f}")
        
        print(f"📊 Average F1 Improvement: {summary['avg_f1_improvement']:.3f}")
        print(f"📊 Average Precision Improvement: {summary['avg_precision_improvement']:.3f}")
        print(f"📊 Average Recall Improvement: {summary['avg_recall_improvement']:.3f}")
        
        print("=" * 60)


def main():
    """Main entry point for improved A/B testing framework."""
    
    parser = argparse.ArgumentParser(description="Improved A/B testing framework for RAGChecker evaluation")
    _ = parser.add_argument("--baseline", required=True, help="Baseline configuration name")
    _ = parser.add_argument("--tests", nargs="+", required=True, help="Test configuration names")
    _ = parser.add_argument("--max-workers", type=int, default=3, help="Maximum parallel workers")
    _ = parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    _ = parser.add_argument("--output-dir", default="metrics/ab_tests", help="Output directory")
    
    args = parser.parse_args()
    
    # Create framework
    framework = ImprovedABTestingFramework(
        max_workers=args.max_workers,
        timeout_seconds=args.timeout
    )
    
    # Create configurations
    baseline_config = EvaluationConfig(
        name=args.baseline,
        scenario="precision_lift_pack",
        profile="gold",
        description="Baseline configuration"
    )
    
    test_configs = [
        EvaluationConfig(
            name=test_name,
            scenario="precision_lift_pack",
            profile="gold",
            description=f"Test configuration: {test_name}"
        )
        for test_name in args.tests
    ]
    
    # Run A/B test
    result = framework.run_ab_test(baseline_config, test_configs, args.output_dir)
    
    # Exit with appropriate code
    sys.exit(0 if result["summary"]["status"] == "success" else 1)


if __name__ == "__main__":
    main()
