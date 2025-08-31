#!/usr/bin/env python3
"""
Coder Role Baseline Evaluation

Establishes baseline performance metrics for the Coder role before implementing
Vector-Based System Mapping & Dependency Visualization enhancements.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

# Add the dspy-rag-system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

try:
    from utils.anchor_metadata_parser import VALID_ROLES
    from utils.memory_rehydrator import MemoryRehydrator, build_hydration_bundle
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Using fallback evaluation...")


class CoderRoleBaselineEvaluator:
    """Evaluates baseline performance of Coder role before B-1047 enhancements."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "baseline_type": "Coder Role Performance",
            "metrics": {},
        }

    def evaluate_role_availability(self) -> Dict[str, Any]:
        """Evaluate if Coder role is available and properly configured."""
        start_time = time.time()

        try:
            # Check if coder role is in valid roles
            coder_available = "coder" in VALID_ROLES if "VALID_ROLES" in globals() else False

            # Check for coder-specific files
            coder_files = []
            coder_file_paths = [
                "100_memory/100_dspy-role-communication-guide.md",
                "100_memory/100_role-system-alignment-guide.md",
                "artifacts/session_memory/coder.json",
                "artifacts/session_memory/coder.txt",
            ]

            for file_path in coder_file_paths:
                if os.path.exists(file_path):
                    coder_files.append(file_path)

            end_time = time.time()

            return {
                "status": "PASS" if coder_available and len(coder_files) > 0 else "FAIL",
                "coder_available": coder_available,
                "coder_files_found": len(coder_files),
                "coder_files": coder_files,
                "evaluation_time": end_time - start_time,
            }

        except Exception as e:
            return {"status": "ERROR", "error": str(e), "evaluation_time": time.time() - start_time}

    def evaluate_memory_rehydration_performance(self) -> Dict[str, Any]:
        """Evaluate memory rehydration performance for Coder role."""
        start_time = time.time()

        try:
            # Test memory rehydration with coder role
            if "MemoryRehydrator" in globals():
                rehydrator = MemoryRehydrator()

                # Test basic rehydration
                test_query = "current project status and core documentation"
                test_role = "coder"

                rehydration_start = time.time()
                result = rehydrator.rehydrate(test_query, test_role)
                rehydration_time = time.time() - rehydration_start

                return {
                    "status": "PASS",
                    "rehydration_time": rehydration_time,
                    "result_available": result is not None,
                    "result_type": type(result).__name__ if result else None,
                }
            else:
                # Fallback test
                return {"status": "SKIP", "reason": "MemoryRehydrator not available", "rehydration_time": 0.0}

        except Exception as e:
            return {"status": "ERROR", "error": str(e), "rehydration_time": time.time() - start_time}

    def evaluate_context_quality(self) -> Dict[str, Any]:
        """Evaluate the quality of context provided by Coder role."""
        start_time = time.time()

        try:
            # Check coder-specific context files
            context_quality_metrics = {
                "role_instructions_available": False,
                "technical_standards_available": False,
                "safety_protocols_available": False,
                "quality_gates_available": False,
                "testing_guide_available": False,
            }

            # Check for key coder role files
            coder_files_to_check = [
                "100_memory/100_dspy-role-communication-guide.md",
                "100_memory/100_role-system-alignment-guide.md",
            ]

            for file_path in coder_files_to_check:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        # Check for key content indicators
                        if "CODER_ROLE" in content or "coder" in content.lower():
                            context_quality_metrics["role_instructions_available"] = True

                        if "technical" in content.lower() and "standard" in content.lower():
                            context_quality_metrics["technical_standards_available"] = True

                        if "safety" in content.lower() and "protocol" in content.lower():
                            context_quality_metrics["safety_protocols_available"] = True

                        if "quality" in content.lower() and "gate" in content.lower():
                            context_quality_metrics["quality_gates_available"] = True

                        if "test" in content.lower() and "guide" in content.lower():
                            context_quality_metrics["testing_guide_available"] = True

            end_time = time.time()

            total_available = sum(context_quality_metrics.values())
            quality_score = total_available / len(context_quality_metrics)

            return {
                "status": "PASS" if quality_score >= 0.6 else "PARTIAL",
                "quality_score": quality_score,
                "metrics": context_quality_metrics,
                "evaluation_time": end_time - start_time,
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "quality_score": 0.0,
                "evaluation_time": time.time() - start_time,
            }

    def evaluate_system_integration(self) -> Dict[str, Any]:
        """Evaluate how well Coder role integrates with existing systems."""
        start_time = time.time()

        try:
            integration_metrics = {
                "memory_system_integration": False,
                "workflow_integration": False,
                "documentation_integration": False,
                "testing_integration": False,
            }

            # Check memory system integration
            if os.path.exists("artifacts/session_memory/coder.json"):
                integration_metrics["memory_system_integration"] = True

            # Check workflow integration
            if os.path.exists("000_core/000_backlog.md"):
                with open("000_core/000_backlog.md", "r", encoding="utf-8") as f:
                    content = f.read()
                    if "coder" in content.lower():
                        integration_metrics["workflow_integration"] = True

            # Check documentation integration
            if os.path.exists("400_guides/400_00_getting-started-and-index.md"):
                with open("400_guides/400_00_getting-started-and-index.md", "r", encoding="utf-8") as f:
                    content = f.read()
                    if "coder" in content.lower():
                        integration_metrics["documentation_integration"] = True

            # Check testing integration
            if os.path.exists("tests/test_coder_role_performance.py"):
                integration_metrics["testing_integration"] = True

            end_time = time.time()

            total_integrated = sum(integration_metrics.values())
            integration_score = total_integrated / len(integration_metrics)

            return {
                "status": "PASS" if integration_score >= 0.5 else "PARTIAL",
                "integration_score": integration_score,
                "metrics": integration_metrics,
                "evaluation_time": end_time - start_time,
            }

        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e),
                "integration_score": 0.0,
                "evaluation_time": time.time() - start_time,
            }

    def run_baseline_evaluation(self) -> Dict[str, Any]:
        """Run complete baseline evaluation."""
        print("🔍 Running Coder Role Baseline Evaluation...")
        print("=" * 60)

        # Run all evaluations
        self.results["metrics"]["role_availability"] = self.evaluate_role_availability()
        self.results["metrics"]["memory_rehydration"] = self.evaluate_memory_rehydration_performance()
        self.results["metrics"]["context_quality"] = self.evaluate_context_quality()
        self.results["metrics"]["system_integration"] = self.evaluate_system_integration()

        # Calculate overall score
        scores = []
        for metric_name, metric_data in self.results["metrics"].items():
            if "score" in metric_data:
                scores.append(metric_data["score"])
            elif metric_data.get("status") == "PASS":
                scores.append(1.0)
            elif metric_data.get("status") == "PARTIAL":
                scores.append(0.5)
            else:
                scores.append(0.0)

        overall_score = sum(scores) / len(scores) if scores else 0.0
        self.results["overall_score"] = overall_score

        # Determine overall status
        if overall_score >= 0.8:
            overall_status = "EXCELLENT"
        elif overall_score >= 0.6:
            overall_status = "GOOD"
        elif overall_score >= 0.4:
            overall_status = "FAIR"
        else:
            overall_status = "NEEDS_IMPROVEMENT"

        self.results["overall_status"] = overall_status

        return self.results

    def save_results(self, output_file: str = "metrics/coder_role_baseline_evaluation.json"):
        """Save evaluation results to file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"📊 Results saved to: {output_file}")

    def print_summary(self):
        """Print evaluation summary."""
        print("\n" + "=" * 60)
        print("📊 CODER ROLE BASELINE EVALUATION SUMMARY")
        print("=" * 60)

        print(f"📅 Timestamp: {self.results['timestamp']}")
        print(f"🎯 Project: {self.results['project']}")
        print(f"📈 Overall Score: {self.results['overall_score']:.2f}/1.00")
        print(f"🏆 Overall Status: {self.results['overall_status']}")

        print("\n📋 Detailed Metrics:")
        for metric_name, metric_data in self.results["metrics"].items():
            status = metric_data.get("status", "UNKNOWN")
            score = metric_data.get("score", "N/A")
            time_taken = metric_data.get("evaluation_time", 0)

            print(f"  • {metric_name.replace('_', ' ').title()}: {status} (Score: {score}, Time: {time_taken:.3f}s)")

        print("\n🎯 Vector-Based System Mapping Enhancement Goals:")
        print("  • Improve system integration score")
        print("  • Enhance context quality through vector-based mapping")
        print("  • Optimize memory rehydration performance")
        print("  • Strengthen coder role capabilities")


def main():
    """Main evaluation function."""
    evaluator = CoderRoleBaselineEvaluator()
    results = evaluator.run_baseline_evaluation()
    evaluator.save_results()
    evaluator.print_summary()

    return results


if __name__ == "__main__":
    main()
