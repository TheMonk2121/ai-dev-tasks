#!/usr/bin/env python3
"""
Hydration Performance Benchmark
Comprehensive performance benchmarking for memory rehydrator
"""

import json
import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.utils.memory_rehydrator import build_hydration_bundle

def benchmark_bundle_creation():
    """Benchmark bundle creation performance across different scenarios"""
    print("📊 Benchmarking Bundle Creation Performance")
    print("=" * 50)

    test_cases = [
        ("planner", "strategic planning", 1200),
        ("implementer", "code implementation", 1200),
        ("planner", "priority assessment", 800),
        ("implementer", "debugging", 1000),
        ("planner", "architecture decision", 1500),
        ("implementer", "performance optimization", 1200),
    ]

    results = {}
    total_time = 0

    for role, task, budget in test_cases:
        print(f"\n🧪 Testing: {role} - {task}")

        # Warm up
        build_hydration_bundle(role=role, task="warmup", token_budget=100)

        # Benchmark
        start_time = time.time()
        bundle = build_hydration_bundle(role=role, task=task, token_budget=budget)
        end_time = time.time()

        creation_time = end_time - start_time
        total_time += creation_time

        result = {
            "creation_time": creation_time,
            "sections": bundle.meta.get("sections", 0),
            "tokens": bundle.meta.get("tokens_est", 0),
            "budget": budget,
            "efficiency": bundle.meta.get("tokens_est", 0) / budget,
            "elapsed_s": bundle.meta.get("elapsed_s", 0),
        }

        results[f"{role}_{task}"] = result

        print(f"  ✅ Time: {creation_time:.3f}s")
        print(f"  ✅ Sections: {result['sections']}")
        print(f"  ✅ Tokens: {result['tokens']}/{budget} ({result['efficiency']:.1%})")

    # Calculate statistics
    times = [r["creation_time"] for r in results.values()]
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    efficiencies = [r["efficiency"] for r in results.values()]
    avg_efficiency = sum(efficiencies) / len(efficiencies)

    print("\n📈 Performance Summary:")
    print(f"  Average creation time: {avg_time:.3f}s")
    print(f"  Min creation time: {min_time:.3f}s")
    print(f"  Max creation time: {max_time:.3f}s")
    print(f"  Average efficiency: {avg_efficiency:.1%}")
    print(f"  Total test time: {total_time:.3f}s")

    return {
        "results": results,
        "summary": {
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "avg_efficiency": avg_efficiency,
            "total_time": total_time,
        },
    }

def benchmark_memory_usage():
    """Benchmark memory usage during bundle creation"""
    print("\n📊 Benchmarking Memory Usage")
    print("=" * 50)

    try:
        import psutil  # type: ignore[import-untyped]

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory usage: {initial_memory:.1f} MB")

        # Create multiple bundles
        bundles = []
        memory_samples = []

        for i in range(10):
            # Sample memory before bundle creation
            memory_before = process.memory_info().rss / 1024 / 1024

            bundle = build_hydration_bundle(
                role="planner" if i % 2 == 0 else "implementer", task=f"memory test {i}", token_budget=1200
            )
            bundles.append(bundle)

            # Sample memory after bundle creation
            memory_after = process.memory_info().rss / 1024 / 1024
            memory_samples.append(memory_after - memory_before)

            print(f"  Bundle {i+1}: {memory_samples[-1]:.1f} MB increase")

        final_memory = process.memory_info().rss / 1024 / 1024
        total_increase = final_memory - initial_memory
        avg_increase = sum(memory_samples) / len(memory_samples)

        print("\n📈 Memory Summary:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Total increase: {total_increase:.1f} MB")
        print(f"  Average per bundle: {avg_increase:.1f} MB")
        print(f"  Bundles created: {len(bundles)}")

        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "total_increase_mb": total_increase,
            "avg_increase_mb": avg_increase,
            "bundles_created": len(bundles),
            "memory_samples": memory_samples,
        }

    except ImportError:
        print("⚠️  psutil not available, skipping memory benchmark")
        print("💡 To enable memory benchmarking, install psutil:")
        print("   pip install psutil")
        return None

def stress_test_concurrent_bundles():
    """Stress test with concurrent bundle creation"""
    print("\n🚀 Stress Testing Concurrent Bundles")
    print("=" * 50)

    try:
        import queue
        import threading

        results = []
        errors = []
        result_queue = queue.Queue()
        error_queue = queue.Queue()

        def create_bundle(role, task_id):
            try:
                start_time = time.time()
                bundle = build_hydration_bundle(role=role, task=f"stress test {task_id}", token_budget=1200)
                end_time = time.time()

                result = {
                    "task_id": task_id,
                    "role": role,
                    "creation_time": end_time - start_time,
                    "sections": bundle.meta.get("sections", 0),
                    "tokens": bundle.meta.get("tokens_est", 0),
                    "success": True,
                }
                result_queue.put(result)

            except Exception as e:
                error = {"task_id": task_id, "role": role, "error": str(e), "success": False}
                error_queue.put(error)

        # Create concurrent threads
        threads = []
        num_threads = 20

        print(f"Creating {num_threads} concurrent threads...")

        for i in range(num_threads):
            role = "planner" if i % 2 == 0 else "implementer"
            thread = threading.Thread(target=create_bundle, args=(role, i))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        while not result_queue.empty():
            results.append(result_queue.get())

        while not error_queue.empty():
            errors.append(error_queue.get())

        # Calculate statistics
        if results:
            times = [r["creation_time"] for r in results]
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            sections = [r["sections"] for r in results]
            avg_sections = sum(sections) / len(sections)
        else:
            avg_time = min_time = max_time = avg_sections = 0

        success_rate = len(results) / num_threads

        print("\n📈 Stress Test Results:")
        print(f"  Total requests: {num_threads}")
        print(f"  Successful: {len(results)}")
        print(f"  Failed: {len(errors)}")
        print(f"  Success rate: {success_rate:.1%}")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        print(f"  Average sections: {avg_sections:.1f}")

        if errors:
            print("\n❌ Errors encountered:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"  Task {error['task_id']}: {error['error']}")

        return {
            "total_requests": num_threads,
            "successful_requests": len(results),
            "failed_requests": len(errors),
            "success_rate": success_rate,
            "avg_creation_time": avg_time,
            "min_creation_time": min_time,
            "max_creation_time": max_time,
            "avg_sections": avg_sections,
            "errors": errors,
        }

    except Exception as e:
        print(f"❌ Stress test failed: {e}")
        return None

def benchmark_token_budgets():
    """Benchmark different token budgets"""
    print("\n💰 Benchmarking Token Budgets")
    print("=" * 50)

    test_budgets = [100, 500, 800, 1200, 2000, 5000]
    results = {}

    for budget in test_budgets:
        print(f"\n🧪 Testing budget: {budget} tokens")

        try:
            start_time = time.time()
            bundle = build_hydration_bundle(role="planner", task="token budget benchmark", token_budget=budget)
            end_time = time.time()

            tokens_used = bundle.meta.get("tokens_est", 0)
            efficiency = tokens_used / budget if budget > 0 else 0
            creation_time = end_time - start_time

            result = {
                "success": True,
                "tokens_used": tokens_used,
                "budget": budget,
                "efficiency": efficiency,
                "creation_time": creation_time,
                "sections": bundle.meta.get("sections", 0),
            }

            print(f"  ✅ Tokens used: {tokens_used}")
            print(f"  ✅ Efficiency: {efficiency:.1%}")
            print(f"  ✅ Creation time: {creation_time:.3f}s")
            print(f"  ✅ Sections: {result['sections']}")

        except Exception as e:
            result = {"success": False, "error": str(e), "budget": budget}
            print(f"  ❌ Failed: {e}")

        results[budget] = result

    # Calculate statistics
    successful_results = [r for r in results.values() if r["success"]]

    if successful_results:
        efficiencies = [r["efficiency"] for r in successful_results]
        times = [r["creation_time"] for r in successful_results]

        avg_efficiency = sum(efficiencies) / len(efficiencies)
        avg_time = sum(times) / len(times)

        print("\n📈 Token Budget Summary:")
        print(f"  Successful budgets: {len(successful_results)}/{len(test_budgets)}")
        print(f"  Average efficiency: {avg_efficiency:.1%}")
        print(f"  Average creation time: {avg_time:.3f}s")

    return results

def generate_performance_report():
    """Generate comprehensive performance report"""
    print("🚀 Generating Comprehensive Performance Report")
    print("=" * 60)

    # Run all benchmarks
    bundle_performance = benchmark_bundle_creation()
    memory_usage = benchmark_memory_usage()
    stress_results = stress_test_concurrent_bundles()
    token_budgets = benchmark_token_budgets()

    # Generate summary
    summary = {
        "timestamp": time.time(),
        "bundle_performance": bundle_performance,
        "memory_usage": memory_usage,
        "stress_test": stress_results,
        "token_budgets": token_budgets,
        "overall_summary": {},
    }

    # Calculate overall metrics
    if bundle_performance:
        summary["overall_summary"]["avg_creation_time"] = bundle_performance["summary"]["avg_time"]
        summary["overall_summary"]["avg_efficiency"] = bundle_performance["summary"]["avg_efficiency"]

    if memory_usage:
        summary["overall_summary"]["memory_efficiency"] = memory_usage["avg_increase_mb"]

    if stress_results:
        summary["overall_summary"]["stress_success_rate"] = stress_results["success_rate"]
        summary["overall_summary"]["concurrent_performance"] = stress_results["avg_creation_time"]

    # Performance assessment
    performance_score = 0
    assessments = []

    if bundle_performance and bundle_performance["summary"]["avg_time"] < 5.0:
        performance_score += 25
        assessments.append("✅ Bundle creation performance: EXCELLENT")
    elif bundle_performance and bundle_performance["summary"]["avg_time"] < 10.0:
        performance_score += 15
        assessments.append("⚠️  Bundle creation performance: GOOD")
    else:
        assessments.append("❌ Bundle creation performance: NEEDS IMPROVEMENT")

    if memory_usage and memory_usage["avg_increase_mb"] < 10.0:
        performance_score += 25
        assessments.append("✅ Memory efficiency: EXCELLENT")
    elif memory_usage and memory_usage["avg_increase_mb"] < 20.0:
        performance_score += 15
        assessments.append("⚠️  Memory efficiency: GOOD")
    elif memory_usage is None:
        assessments.append("⚠️  Memory efficiency: NOT TESTED (psutil not available)")
    else:
        assessments.append("❌ Memory efficiency: NEEDS IMPROVEMENT")

    if stress_results and stress_results["success_rate"] > 0.95:
        performance_score += 25
        assessments.append("✅ Stress test performance: EXCELLENT")
    elif stress_results and stress_results["success_rate"] > 0.90:
        performance_score += 15
        assessments.append("⚠️  Stress test performance: GOOD")
    else:
        assessments.append("❌ Stress test performance: NEEDS IMPROVEMENT")

    if bundle_performance and bundle_performance["summary"]["avg_efficiency"] > 0.7:
        performance_score += 25
        assessments.append("✅ Token efficiency: EXCELLENT")
    elif bundle_performance and bundle_performance["summary"]["avg_efficiency"] > 0.5:
        performance_score += 15
        assessments.append("⚠️  Token efficiency: GOOD")
    else:
        assessments.append("❌ Token efficiency: NEEDS IMPROVEMENT")

    summary["overall_summary"]["performance_score"] = performance_score
    summary["overall_summary"]["assessments"] = assessments

    # Print final report
    print("\n📊 FINAL PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Performance Score: {performance_score}/100")
    print(
        f"Grade: {'A' if performance_score >= 80 else 'B' if performance_score >= 60 else 'C' if performance_score >= 40 else 'D'}"
    )

    print("\nAssessments:")
    for assessment in assessments:
        print(f"  {assessment}")

    # Save report
    report_file = "hydration_performance_report.json"
    with open(report_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    return summary

def main():
    """Main benchmark runner"""
    print("🚀 Hydration Performance Benchmark Suite")
    print("=" * 60)

    try:
        report = generate_performance_report()

        # Return exit code based on performance
        performance_score = report["overall_summary"]["performance_score"]
        if performance_score >= 80:
            print("\n🎉 EXCELLENT PERFORMANCE!")
            return 0
        elif performance_score >= 60:
            print("\n✅ GOOD PERFORMANCE")
            return 0
        else:
            print("\n⚠️  PERFORMANCE NEEDS IMPROVEMENT")
            return 1

    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
