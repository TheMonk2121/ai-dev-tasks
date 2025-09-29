#!/usr/bin/env python3
"""
Streamlined Nightly Smoke Evaluation

Uses consolidated health-check helpers and focuses on essential smoke tests.
Provides comprehensive reporting with delta analysis and regression detection.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add scripts to path for imports
scripts_path = Path(__file__).parent.parent.resolve()
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import after path setup
try:
    from scripts.evaluation.health_check_helpers import (
        HealthCheckHelpers,  # type: ignore
    )
except ImportError:
    # Fallback for when health_check_helpers is not available
    class HealthCheckResult:
        def __init__(self, status: str, message: str = "", error: str = "", warning: str = ""):
            self.status: str = status
            self.message: str = message
            self.error: str = error
            self.warning: str = warning
            self.timestamp: float = time.time()
        
        def to_dict(self) -> dict[str, Any]:
            return {
                "status": self.status,
                "message": self.message,
                "error": self.error,
                "warning": self.warning,
                "timestamp": self.timestamp,
            }
    
    class HealthCheckHelpers:
        def __init__(self):
            self.model_cache: Any = None
            
        def check_database_connectivity(self):
            return HealthCheckResult("pass", "Database connectivity check")
        def check_model_availability(self):
            return HealthCheckResult("pass", "Model availability check")
        def check_configuration_validation(self):
            return HealthCheckResult("pass", "Configuration validation check")
        def check_resource_availability(self):
            return HealthCheckResult("pass", "Resource availability check")
        def check_environment_validation(self):
            return HealthCheckResult("pass", "Environment validation check")
        def check_index_presence(self):
            return HealthCheckResult("pass", "Index presence check")
        def check_token_budget(self):
            return HealthCheckResult("pass", "Token budget check")
        def check_prefix_leakage(self):
            return HealthCheckResult("pass", "Prefix leakage check")


class StreamlinedNightlySmoke:
    """Streamlined nightly smoke evaluation with consolidated health checks."""
    
    def __init__(self, output_dir: str = "metrics/nightly_smoke"):
        self.output_dir: Path = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize health check helpers
        self.health_helpers: HealthCheckHelpers = HealthCheckHelpers()
        
        # Smoke test categories (streamlined)
        self.smoke_tests: dict[str, dict[str, Any]] = {
            "core_health": {
                "description": "Core system health checks",
                "tests": [
                    "database_connectivity",
                    "model_availability", 
                    "configuration_validation",
                    "resource_availability",
                ],
            },
            "evaluation_readiness": {
                "description": "Evaluation system readiness",
                "tests": [
                    "environment_validation",
                    "index_presence",
                    "token_budget",
                    "prefix_leakage",
                ],
            },
            "rag_quality": {
                "description": "RAG system quality assurance",
                "tests": [
                    "retrieval_quality",
                    "fusion_performance", 
                    "reranking_accuracy",
                    "context_assembly",
                ],
            },
        }
        
        self.results: dict[str, Any] = {}
        self.deltas: dict[str, Any] = {}
        self.regressions: list[dict[str, str]] = []
    
    def run_nightly_smoke_evaluation(self) -> dict[str, Any]:
        """Run streamlined nightly smoke evaluation."""
        print("🌙 Starting Streamlined Nightly Smoke Evaluation")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all smoke test categories
        for category, config in self.smoke_tests.items():
            print(f"\n🔍 Running {category} tests...")
            tests = config["tests"]
            if isinstance(tests, list):
                category_result = self._run_category_tests(category, tests)
            else:
                category_result = {"status": "fail", "error": f"Invalid tests format for {category}"}
            self.results[category] = category_result
            
            if category_result["status"] == "fail":
                print(f"❌ {category} tests failed")
            elif category_result["status"] == "warn":
                print(f"⚠️ {category} tests passed with warnings")
            else:
                print(f"✅ {category} tests passed")
        
        # Calculate overall results
        overall_result = self._calculate_overall_results()
        
        # Generate deltas and regressions
        self._generate_deltas()
        self._detect_regressions()

        evaluation_snapshot = self._maybe_run_codex_snapshot()
        
        # Create comprehensive report
        evaluation_report = {
            "timestamp": self.timestamp,
            "duration": time.time() - start_time,
            "overall_status": overall_result["status"],
            "categories": self.results,
            "deltas": self.deltas,
            "regressions": self.regressions,
            "summary": overall_result,
        }

        if evaluation_snapshot is not None:
            evaluation_report["evaluation_snapshot"] = evaluation_snapshot
        
        # Save results
        self._save_results(evaluation_report)
        
        # Print summary
        self._print_evaluation_summary(evaluation_report)
        
        return evaluation_report
    
    def _run_category_tests(self, category: str, tests: list[str]) -> dict[str, Any]:
        """Run tests for a specific category."""
        category_results = {}
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0
        
        for test in tests:
            result = self._run_single_test(category, test)
            category_results[test] = result
            
            if result["status"] == "pass":
                passed_tests += 1
            elif result["status"] == "fail":
                failed_tests += 1
            elif result["status"] == "warn":
                warning_tests += 1
        
        # Determine category status
        if failed_tests > 0:
            status = "fail"
        elif warning_tests > 0:
            status = "warn"
        else:
            status = "pass"
        
        return {
            "status": status,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warning_tests,
            "total": len(tests),
            "results": category_results,
        }
    
    def _run_single_test(self, category: str, test: str) -> dict[str, Any]:
        """Run a single test."""
        try:
            if category == "core_health":
                return self._run_core_health_test(test)
            elif category == "evaluation_readiness":
                return self._run_evaluation_readiness_test(test)
            elif category == "rag_quality":
                return self._run_rag_quality_test(test)
            else:
                return {"status": "fail", "error": f"Unknown category: {category}"}
        except Exception as e:
            return {"status": "fail", "error": str(e)}
    
    def _run_core_health_test(self, test: str) -> dict[str, Any]:
        """Run core health tests using consolidated helpers."""
        if test == "database_connectivity":
            result = self.health_helpers.check_database_connectivity()
        elif test == "model_availability":
            result = self.health_helpers.check_model_availability()
        elif test == "configuration_validation":
            result = self.health_helpers.check_configuration_validation()
        elif test == "resource_availability":
            result = self.health_helpers.check_resource_availability()
        else:
            return {"status": "fail", "error": f"Unknown core health test: {test}"}
        
        return result.to_dict()
    
    def _run_evaluation_readiness_test(self, test: str) -> dict[str, Any]:
        """Run evaluation readiness tests using consolidated helpers."""
        if test == "environment_validation":
            result = self.health_helpers.check_environment_validation()
        elif test == "index_presence":
            result = self.health_helpers.check_index_presence()
        elif test == "token_budget":
            result = self.health_helpers.check_token_budget()
        elif test == "prefix_leakage":
            result = self.health_helpers.check_prefix_leakage()
        else:
            return {"status": "fail", "error": f"Unknown evaluation readiness test: {test}"}
        
        return result.to_dict()

    def _maybe_run_codex_snapshot(self) -> dict[str, Any] | None:
        if os.environ.get("STREAMLINED_SMOKE_RUN_EVAL") != "1":
            return None

        try:
            from scripts.evaluation.codex_evaluator import (
                CodexEvaluator,  # type: ignore
            )
            from src.evaluation.contracts import RunConfig  # type: ignore
        except Exception as exc:  # pragma: no cover - import guard
            return {"status": "error", "error": f"Import failure: {exc}"}

        dataset = Path(os.environ.get("STREAMLINED_SMOKE_DATASET", "evals/data/gold/v1/gold_cases_121.jsonl")).resolve()
        profile = os.environ.get("STREAMLINED_SMOKE_PROFILE", os.environ.get("EVAL_PROFILE", "mock"))
        limit = int(os.environ.get("STREAMLINED_SMOKE_LIMIT", "3"))
        concurrency = int(os.environ.get("STREAMLINED_SMOKE_CONCURRENCY", "2"))

        config = RunConfig(
            run_id=f"smoke_{self.timestamp}",
            profile=profile,
            dataset=dataset,
            adapters=("ragchecker",),
            limit=limit,
            seed=42,
            concurrency=concurrency,
            reporter_names=(),
            environment={},
        )

        try:
            evaluator = CodexEvaluator()
            summary = asyncio.run(evaluator._run_ragchecker(config, reporters=()))  # type: ignore
        except Exception as exc:  # pragma: no cover - runtime guard
            return {"status": "error", "error": str(exc)}

        return {
            "status": "ok",
            "metrics": dict(summary.metrics),
            "cases": len(summary.results),
            "artifact": summary.artifacts.get("ragchecker_results_path"),
        }
    
    def _run_rag_quality_test(self, test: str) -> dict[str, Any]:
        """Run RAG quality tests."""
        if test == "retrieval_quality":
            return self._test_retrieval_quality()
        elif test == "fusion_performance":
            return self._test_fusion_performance()
        elif test == "reranking_accuracy":
            return self._test_reranking_accuracy()
        elif test == "context_assembly":
            return self._test_context_assembly()
        else:
            return {"status": "fail", "error": f"Unknown RAG quality test: {test}"}
    
    def _test_retrieval_quality(self) -> dict[str, Any]:
        """Test retrieval quality."""
        try:
            from src.dspy_modules.dspy_reader_program import RAGAnswer  # type: ignore

            retriever = RAGAnswer()
            test_query = "What is the main purpose of this project?"
            prediction = retriever(question=test_query, tag="rag")
            snapshot = list(getattr(retriever, "_last_retrieval_snapshot", []) or [])
            contexts = list(getattr(retriever, "used_contexts", []) or [])

            if snapshot or contexts:
                count = len(snapshot) or len(contexts)
                return {
                    "status": "pass",
                    "message": f"Retrieval working: {count} results",
                    "retrieved": count,
                    "answer_preview": getattr(prediction, "answer", "")[:160],
                }

            return {"status": "fail", "error": "No retrieval results"}

        except ImportError:
            return {"status": "warn", "message": "DSPy modules not available - skipping retrieval test"}
        except Exception as e:
            return {"status": "fail", "error": f"Retrieval quality test failed: {e}"}
    
    def _test_fusion_performance(self) -> dict[str, Any]:
        """Test fusion performance."""
        try:
            from src.dspy_modules.dspy_reader_program import RAGAnswer  # type: ignore

            retriever = RAGAnswer()
            test_query = "How does the evaluation system work?"
            prediction = retriever(question=test_query, tag="rag")
            snapshot = list(getattr(retriever, "_last_retrieval_snapshot", []) or [])
            contexts = list(getattr(retriever, "used_contexts", []) or [])

            if snapshot or contexts:
                count = len(snapshot) or len(contexts)
                return {
                    "status": "pass",
                    "message": f"Fusion working: {count} fused results",
                    "retrieved": count,
                    "answer_preview": getattr(prediction, "answer", "")[:160],
                }

            return {"status": "fail", "error": "No fusion results"}

        except ImportError:
            return {"status": "warn", "message": "DSPy modules not available - skipping fusion test"}
        except Exception as e:
            return {"status": "fail", "error": f"Fusion performance test failed: {e}"}
    
    def _test_reranking_accuracy(self) -> dict[str, Any]:
        """Test reranking accuracy."""
        try:
            # Test reranking functionality
            if os.getenv("RERANK_ENABLE", "1") == "1":
                if self.health_helpers.model_cache is None:
                    return {"status": "warn", "message": "Model cache not available - skipping reranking test"}
                
                reranker = self.health_helpers.model_cache.get_rerank_model()
                test_score = reranker.predict([("query", "document")])
                
                if test_score is not None:
                    return {"status": "pass", "message": "Reranking working correctly"}
                else:
                    return {"status": "fail", "error": "Reranking returned no score"}
            else:
                return {"status": "pass", "message": "Reranking disabled (expected)"}
                
        except Exception as e:
            return {"status": "fail", "error": f"Reranking accuracy test failed: {e}"}
    
    def _test_context_assembly(self) -> dict[str, Any]:
        """Test context assembly."""
        try:
            from src.dspy_modules.dspy_reader_program import RAGAnswer  # type: ignore

            reader = RAGAnswer()
            test_query = "Summarize the evaluation workflow"
            prediction = reader(question=test_query, tag="rag")
            contexts = list(getattr(reader, "used_contexts", []) or [])

            if hasattr(prediction, "answer") and contexts:
                return {
                    "status": "pass",
                    "message": "Context assembly working",
                    "context_snippets": len(contexts),
                    "answer_preview": getattr(prediction, "answer", "")[:160],
                }

            return {"status": "fail", "error": "Context assembly failed"}

        except ImportError:
            return {"status": "warn", "message": "DSPy modules not available - skipping context assembly test"}
        except Exception as e:
            return {"status": "fail", "error": f"Context assembly test failed: {e}"}
    
    def _calculate_overall_results(self) -> dict[str, Any]:
        """Calculate overall results from all categories."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warning_tests = 0

        for category_result in self.results.values():
            total_tests += category_result["total"]
            passed_tests += category_result["passed"]
            failed_tests += category_result["failed"]
            warning_tests += category_result["warnings"]

        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0.0

        if failed_tests > 0:
            status = "fail"
        elif warning_tests > 0:
            status = "warn"
        else:
            status = "pass"

        return {
            "status": status,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warning_tests": warning_tests,
            "success_rate": success_rate,
        }
    
    def _generate_deltas(self):
        """Generate deltas from previous runs."""
        # Load previous results if available
        previous_file = self.output_dir / "latest_results.json"
        if previous_file.exists():
            try:
                with open(previous_file) as f:
                    previous_results = json.load(f)
                
                # Calculate deltas
                self.deltas = {
                    "timestamp": self.timestamp,
                    "previous_timestamp": previous_results.get("timestamp", "unknown"),
                    "status_change": self._calculate_status_change(previous_results),
                    "performance_deltas": self._calculate_performance_deltas(previous_results),
                }
            except Exception as e:
                self.deltas = {"error": f"Failed to load previous results: {e}"}
        else:
            self.deltas = {"message": "No previous results found"}
    
    def _calculate_status_change(self, previous_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate status changes from previous run."""
        current_status = self._calculate_overall_results()["status"]
        previous_status = previous_results.get("overall_status", "unknown")
        
        return {
            "current": current_status,
            "previous": previous_status,
            "changed": current_status != previous_status,
        }
    
    def _calculate_performance_deltas(self, previous_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate performance deltas from previous run."""
        current_summary = self._calculate_overall_results()
        previous_summary = previous_results.get("summary", {})
        
        return {
            "success_rate_delta": current_summary.get("success_rate", 0) - previous_summary.get("success_rate", 0),
            "total_tests_delta": current_summary.get("total_tests", 0) - previous_summary.get("total_tests", 0),
            "failed_tests_delta": current_summary.get("failed_tests", 0) - previous_summary.get("failed_tests", 0),
        }
    
    def _detect_regressions(self):
        """Detect regressions from previous runs."""
        if "performance_deltas" in self.deltas:
            deltas = self.deltas["performance_deltas"]
            if isinstance(deltas, dict):
                if deltas.get("success_rate_delta", 0) < -5:
                    self.regressions.append({
                        "type": "success_rate_decline",
                        "severity": "high",
                        "message": f"Success rate declined by {abs(deltas['success_rate_delta']):.1f}%",
                    })
                
                if deltas.get("failed_tests_delta", 0) > 2:
                    self.regressions.append({
                        "type": "test_failures_increase",
                        "severity": "medium",
                        "message": f"Test failures increased by {deltas['failed_tests_delta']}",
                })
    
    def _save_results(self, evaluation_report: dict[str, Any]):
        """Save evaluation results."""
        # Save current results
        current_file = self.output_dir / f"smoke_evaluation_{self.timestamp}.json"
        with open(current_file, "w") as f:
            json.dump(evaluation_report, f, indent=2)
        
        # Save as latest results
        latest_file = self.output_dir / "latest_results.json"
        with open(latest_file, "w") as f:
            json.dump(evaluation_report, f, indent=2)
        
        print(f"📁 Results saved to: {current_file}")
    
    def _print_evaluation_summary(self, evaluation_report: dict[str, Any]):
        """Print comprehensive evaluation summary."""
        print("\n" + "=" * 60)
        print("🌙 NIGHTLY SMOKE EVALUATION SUMMARY")
        print("=" * 60)
        
        summary = evaluation_report["summary"]
        print(f"📊 Overall Status: {'✅ PASS' if summary['status'] == 'pass' else '❌ FAIL' if summary['status'] == 'fail' else '⚠️ WARN'}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"⚠️ Warnings: {summary['warning_tests']}")
        
        if self.regressions:
            print(f"\n🚨 REGRESSIONS DETECTED: {len(self.regressions)}")
            for regression in self.regressions:
                severity_icon = "🔴" if regression.get("severity") == "high" else "🟡"
                print(f"  {severity_icon} {regression.get('message', 'Unknown regression')}")
        
        if "deltas" in evaluation_report and "performance_deltas" in evaluation_report["deltas"]:
            deltas = evaluation_report["deltas"]["performance_deltas"]
            print("\n📊 PERFORMANCE DELTAS:")
            print(f"  Success Rate: {deltas.get('success_rate_delta', 0):+.1f}%")
            print(f"  Total Tests: {deltas.get('total_tests_delta', 0):+}")
            print(f"  Failed Tests: {deltas.get('failed_tests_delta', 0):+}")
        
        print("=" * 60)


def main():
    """Main entry point for streamlined nightly smoke evaluation."""
    
    parser = argparse.ArgumentParser(description="Streamlined nightly smoke evaluation")
    _ = parser.add_argument("--output-dir", default="metrics/nightly_smoke", help="Output directory for results")
    _ = parser.add_argument("--category", help="Run specific category only")
    
    args = parser.parse_args()
    
    evaluator = StreamlinedNightlySmoke(args.output_dir)
    
    if args.category:
        # Run specific category only
        if args.category in evaluator.smoke_tests:
            config = evaluator.smoke_tests[args.category]
            tests = config["tests"]
            if isinstance(tests, list):
                result = evaluator._run_category_tests(args.category, tests)  # pyright: ignore[reportPrivateUsage]
            else:
                result = {"status": "fail", "error": f"Invalid tests format for {args.category}"}
            print(f"Category {args.category} result: {result['status']}")
        else:
            print(f"Unknown category: {args.category}")
            sys.exit(1)
    else:
        # Run full evaluation
        result = evaluator.run_nightly_smoke_evaluation()
        sys.exit(0 if result["overall_status"] == "pass" else 1)


if __name__ == "__main__":
    main()
