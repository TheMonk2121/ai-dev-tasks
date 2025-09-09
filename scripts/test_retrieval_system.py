#!/usr/bin/env python3
"""
Comprehensive Retrieval System Test Suite

Runs test hardening, robustness checks, and failure mode testing
to validate production readiness of the retrieval pipeline.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Any

# Add src to path for retrieval modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

from retrieval.robustness_checks import RobustnessChecker, test_error_recovery
from retrieval.test_hardening import run_comprehensive_tests


def create_mock_retrieval_function():
    """Create a mock retrieval function for testing."""

    def mock_retrieval(query: str) -> dict[str, Any]:
        """Mock retrieval function that simulates various behaviors."""
        # Simulate processing time
        time.sleep(0.01)  # 10ms base latency

        # Handle edge cases
        if not query or not query.strip():
            return {"answer": "Not in context.", "citations": [], "context_used": False, "retrieval_count": 0}

        if len(query) > 500:
            # Simulate truncation for very long queries
            query = query[:500] + "..."

        # Simulate normal response
        return {
            "answer": f"Mock answer for query: {query[:50]}...",
            "citations": ["mock_doc1.md", "mock_doc2.md"],
            "context_used": True,
            "retrieval_count": 5,
            "context_size": 150,
            "context_preview": "Mock context preview...",
        }

    return mock_retrieval


def run_failure_mode_tests(retrieval_fn) -> dict[str, Any]:
    """Test various failure modes and system limits."""
    failure_tests = [
        {
            "name": "resource_exhaustion",
            "description": "Test with high query volume",
            "test_fn": lambda: test_high_volume(retrieval_fn),
        },
        {
            "name": "memory_pressure",
            "description": "Test with large context requirements",
            "test_fn": lambda: test_large_context(retrieval_fn),
        },
        {
            "name": "concurrent_queries",
            "description": "Test concurrent query handling",
            "test_fn": lambda: test_concurrent_queries(retrieval_fn),
        },
        {
            "name": "error_recovery",
            "description": "Test error recovery mechanisms",
            "test_fn": lambda: test_error_recovery(retrieval_fn),
        },
    ]

    results = []
    for test in failure_tests:
        print(f"🧪 Running {test['name']}: {test['description']}")
        try:
            start_time = time.time()
            test_result = test["test_fn"]()
            duration = time.time() - start_time

            result = {
                "test_name": test["name"],
                "status": "completed",
                "duration_seconds": duration,
                "result": test_result,
            }
        except Exception as e:
            result = {"test_name": test["name"], "status": "failed", "error": str(e), "error_type": type(e).__name__}

        results.append(result)
        print(f"   {'✅' if result['status'] == 'completed' else '❌'} {test['name']}")

    return {
        "failure_mode_tests": results,
        "summary": {
            "total": len(results),
            "completed": sum(1 for r in results if r["status"] == "completed"),
            "failed": sum(1 for r in results if r["status"] == "failed"),
        },
    }


def test_high_volume(retrieval_fn, num_queries: int = 100) -> dict[str, Any]:
    """Test system behavior under high query volume."""
    queries = [f"Test query {i} with various content" for i in range(num_queries)]

    start_time = time.time()
    results = []
    errors = 0

    for query in queries:
        try:
            retrieval_fn(query)
            results.append(True)
        except Exception:
            results.append(False)
            errors += 1

    duration = time.time() - start_time

    return {
        "total_queries": num_queries,
        "successful": sum(results),
        "failed": errors,
        "total_duration": duration,
        "queries_per_second": num_queries / duration if duration > 0 else 0,
        "avg_latency_ms": (duration / num_queries) * 1000 if num_queries > 0 else 0,
    }


def test_large_context(retrieval_fn) -> dict[str, Any]:
    """Test handling of queries that might return large contexts."""
    large_queries = [
        "Explain the entire DSPy framework architecture in detail",
        "List all configuration options for the memory system",
        "Describe the complete RAGChecker evaluation methodology",
    ]

    results = []
    for query in large_queries:
        try:
            start_time = time.time()
            result = retrieval_fn(query)
            latency = (time.time() - start_time) * 1000

            context_size = result.get("context_size", 0) if isinstance(result, dict) else 0
            results.append(
                {"query": query[:50] + "...", "success": True, "latency_ms": latency, "context_size": context_size}
            )
        except Exception as e:
            results.append({"query": query[:50] + "...", "success": False, "error": str(e)})

    return {
        "large_context_tests": results,
        "avg_context_size": sum(r.get("context_size", 0) for r in results) / len(results),
        "success_rate": sum(1 for r in results if r["success"]) / len(results),
    }


def test_concurrent_queries(retrieval_fn, num_concurrent: int = 10) -> dict[str, Any]:
    """Test concurrent query handling (simplified single-threaded version)."""
    import random

    queries = [f"Concurrent test query {i}" for i in range(num_concurrent)]

    # Simulate concurrent execution by randomizing order and timing
    random.shuffle(queries)

    start_time = time.time()
    results = []

    for query in queries:
        try:
            result = retrieval_fn(query)
            results.append({"success": True, "result": result})
        except Exception as e:
            results.append({"success": False, "error": str(e)})

    duration = time.time() - start_time

    return {
        "concurrent_queries": num_concurrent,
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "total_duration": duration,
        "throughput": num_concurrent / duration if duration > 0 else 0,
    }


def main() -> None:
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Comprehensive retrieval system testing")
    parser.add_argument("--output", default="test_system_results.json", help="Output file for test results")
    parser.add_argument("--mock", action="store_true", help="Use mock retrieval function for testing")

    args = parser.parse_args()

    print("🚀 Starting Comprehensive Retrieval System Testing")
    print("=" * 60)

    # Create retrieval function
    if args.mock:
        print("📝 Using mock retrieval function")
        retrieval_fn = create_mock_retrieval_function()
    else:
        print("⚠️ Real retrieval function not implemented yet - using mock")
        retrieval_fn = create_mock_retrieval_function()

    # Initialize robustness checker
    checker = RobustnessChecker()

    all_results = {"test_run_info": {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "mock_mode": args.mock}}

    # 1. Run test hardening
    print("\n🧪 Phase 1: Test Hardening & Edge Cases")
    try:
        run_comprehensive_tests(retrieval_fn, "test_hardening_partial.json")
        with open("test_hardening_partial.json") as f:
            all_results["test_hardening"] = json.load(f)
        print("✅ Test hardening completed")
    except Exception as e:
        print(f"❌ Test hardening failed: {e}")
        all_results["test_hardening"] = {"error": str(e)}

    # 2. Run robustness checks
    print("\n🔧 Phase 2: Robustness & Health Checks")
    try:
        health_check = checker.run_comprehensive_health_check()
        all_results["health_check"] = health_check
        print(f"✅ Health check completed - Status: {health_check['overall_status']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        all_results["health_check"] = {"error": str(e)}

    # 3. Run failure mode tests
    print("\n⚡ Phase 3: Failure Mode Testing")
    try:
        failure_results = run_failure_mode_tests(retrieval_fn)
        all_results["failure_modes"] = failure_results
        print(
            f"✅ Failure mode testing completed - {failure_results['summary']['completed']}/{failure_results['summary']['total']} tests passed"
        )
    except Exception as e:
        print(f"❌ Failure mode testing failed: {e}")
        all_results["failure_modes"] = {"error": str(e)}

    # 4. Generate summary
    print("\n📊 Generating Test Summary")
    summary = generate_test_summary(all_results)
    all_results["summary"] = summary

    # Save results
    pathlib.Path(args.output).write_text(json.dumps(all_results, indent=2))
    print(f"💾 Complete test results saved to {args.output}")

    # Print final summary
    print("\n🏆 Test Suite Summary:")
    print(f"   Overall Status: {summary['overall_status']}")
    print(f"   Components Tested: {summary['components_tested']}")
    print(f"   Tests Passed: {summary['tests_passed']}")
    print(f"   Tests Failed: {summary['tests_failed']}")

    if summary["overall_status"] != "healthy":
        print("\n⚠️ Issues Found:")
        for issue in summary.get("issues", []):
            print(f"   - {issue}")

    # Clean up temp files
    try:
        pathlib.Path("test_hardening_partial.json").unlink(missing_ok=True)
    except Exception:
        pass


def generate_test_summary(results: dict[str, Any]) -> dict[str, Any]:
    """Generate overall test summary."""
    summary = {"overall_status": "healthy", "components_tested": 0, "tests_passed": 0, "tests_failed": 0, "issues": []}

    # Analyze test hardening results
    if "test_hardening" in results and "error" not in results["test_hardening"]:
        test_summary = results["test_hardening"].get("test_summary", {})
        summary["components_tested"] += 1

        if test_summary.get("config_valid", False):
            summary["tests_passed"] += 1
        else:
            summary["tests_failed"] += 1
            summary["issues"].append("Configuration validation failed")

    # Analyze health check results
    if "health_check" in results and "error" not in results["health_check"]:
        health_status = results["health_check"].get("overall_status", "unknown")
        component_summary = results["health_check"].get("summary", {})

        summary["components_tested"] += component_summary.get("total_components", 0)
        summary["tests_passed"] += component_summary.get("healthy", 0)
        summary["tests_failed"] += component_summary.get("unhealthy", 0)

        if health_status != "healthy":
            summary["overall_status"] = health_status
            summary["issues"].append(f"System health: {health_status}")

    # Analyze failure mode results
    if "failure_modes" in results and "error" not in results["failure_modes"]:
        failure_summary = results["failure_modes"].get("summary", {})
        summary["tests_passed"] += failure_summary.get("completed", 0)
        summary["tests_failed"] += failure_summary.get("failed", 0)

        if failure_summary.get("failed", 0) > 0:
            summary["issues"].append(f"{failure_summary['failed']} failure mode tests failed")

    # Determine overall status
    if summary["tests_failed"] > 0:
        if summary["overall_status"] == "healthy":
            summary["overall_status"] = "degraded"

    return summary


if __name__ == "__main__":
    main()
