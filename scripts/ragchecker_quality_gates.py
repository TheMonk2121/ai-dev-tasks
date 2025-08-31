#!/usr/bin/env python3
"""
RAGChecker Quality Gates Validation Script

This script validates RAGChecker evaluation results against configured quality gates
and provides detailed reporting for CI/CD integration.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class RAGCheckerQualityGates:
    """Quality gates validator for RAGChecker evaluation results."""

    def __init__(self, config_file: str = "config/ragchecker_quality_gates.json"):
        """Initialize quality gates validator with configuration."""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "gates_passed": 0,
            "gates_failed": 0,
            "total_gates": 0,
            "details": {},
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load quality gates configuration."""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            return config.get("ragchecker_quality_gates", {})
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid configuration file: {e}")
            sys.exit(1)

    def validate_evaluation_metrics(self, evaluation_file: str) -> Dict[str, Any]:
        """Validate evaluation metrics against quality gates."""
        try:
            with open(evaluation_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Evaluation file not found: {evaluation_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid evaluation file: {e}")
            return {}

        metrics = data.get("overall_metrics", {})
        thresholds = self.config.get("evaluation_thresholds", {})

        validation_results = {
            "evaluation_type": data.get("evaluation_type", "unknown"),
            "total_cases": data.get("total_cases", 0),
            "metrics_validation": {},
            "gates_passed": 0,
            "gates_failed": 0,
        }

        # Check if this is a fallback evaluation
        is_fallback = data.get("evaluation_type") == "fallback_simplified"
        threshold_key = "fallback_threshold" if is_fallback else "minimum"

        for metric_name, metric_value in metrics.items():
            if metric_name in thresholds:
                threshold_config = thresholds[metric_name]
                threshold_value = threshold_config.get(threshold_key, threshold_config.get("minimum", 0))

                # Determine if metric passes based on type
                if metric_name in ["precision", "recall", "f1_score", "context_utilization"]:
                    passed = metric_value >= threshold_value
                elif metric_name == "response_length":
                    passed = metric_value >= threshold_value
                else:
                    passed = True  # Unknown metric, assume pass

                validation_results["metrics_validation"][metric_name] = {
                    "value": metric_value,
                    "threshold": threshold_value,
                    "passed": passed,
                    "description": threshold_config.get("description", ""),
                    "target": threshold_config.get("target", 0),
                }

                if passed:
                    validation_results["gates_passed"] += 1
                else:
                    validation_results["gates_failed"] += 1

        return validation_results

    def validate_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics against quality gates."""
        thresholds = self.config.get("performance_thresholds", {})

        validation_results = {"performance_validation": {}, "gates_passed": 0, "gates_failed": 0}

        for metric_name, metric_value in performance_data.items():
            if metric_name in thresholds:
                threshold_config = thresholds[metric_name]

                # Determine if metric passes based on type
                if metric_name in ["evaluation_time", "memory_usage"]:
                    max_value = threshold_config.get("maximum", float("inf"))
                    passed = metric_value <= max_value
                elif metric_name == "throughput":
                    min_value = threshold_config.get("minimum", 0)
                    passed = metric_value >= min_value
                else:
                    passed = True

                validation_results["performance_validation"][metric_name] = {
                    "value": metric_value,
                    "threshold": threshold_config.get("maximum", threshold_config.get("minimum", 0)),
                    "passed": passed,
                    "description": threshold_config.get("description", ""),
                    "unit": threshold_config.get("unit", ""),
                }

                if passed:
                    validation_results["gates_passed"] += 1
                else:
                    validation_results["gates_failed"] += 1

        return validation_results

    def validate_test_requirements(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate test requirements against quality gates."""
        thresholds = self.config.get("test_requirements", {})

        validation_results = {"test_validation": {}, "gates_passed": 0, "gates_failed": 0}

        for metric_name, metric_value in test_results.items():
            if metric_name in thresholds:
                threshold_config = thresholds[metric_name]
                min_value = threshold_config.get("minimum", 0)
                passed = metric_value >= min_value

                validation_results["test_validation"][metric_name] = {
                    "value": metric_value,
                    "threshold": min_value,
                    "passed": passed,
                    "description": threshold_config.get("description", ""),
                    "unit": threshold_config.get("unit", ""),
                }

                if passed:
                    validation_results["gates_passed"] += 1
                else:
                    validation_results["gates_failed"] += 1

        return validation_results

    def generate_report(
        self, evaluation_file: str, performance_data: Optional[Dict] = None, test_results: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive quality gates report."""
        print("🔍 RAGChecker Quality Gates Validation")
        print("=" * 50)

        # Validate evaluation metrics
        eval_validation = self.validate_evaluation_metrics(evaluation_file)
        self.results["details"]["evaluation"] = eval_validation

        # Validate performance metrics if provided
        if performance_data:
            perf_validation = self.validate_performance_metrics(performance_data)
            self.results["details"]["performance"] = perf_validation

        # Validate test requirements if provided
        if test_results:
            test_validation = self.validate_test_requirements(test_results)
            self.results["details"]["tests"] = test_validation

        # Calculate totals
        total_passed = 0
        total_failed = 0

        for section in self.results["details"].values():
            total_passed += section.get("gates_passed", 0)
            total_failed += section.get("gates_failed", 0)

        self.results["gates_passed"] = total_passed
        self.results["gates_failed"] = total_failed
        self.results["total_gates"] = total_passed + total_failed

        # Print summary
        print("📊 Quality Gates Summary:")
        print(f"   ✅ Passed: {total_passed}")
        print(f"   ❌ Failed: {total_failed}")
        print(f"   📋 Total: {self.results['total_gates']}")

        # Print evaluation metrics details
        if "evaluation" in self.results["details"]:
            print("\n📈 Evaluation Metrics:")
            eval_details = self.results["details"]["evaluation"]
            for metric, details in eval_details.get("metrics_validation", {}).items():
                status = "✅" if details["passed"] else "❌"
                print(f"   {status} {metric}: {details['value']:.3f} (threshold: {details['threshold']:.3f})")

        # Print performance metrics details
        if "performance" in self.results["details"]:
            print("\n⚡ Performance Metrics:")
            perf_details = self.results["details"]["performance"]
            for metric, details in perf_details.get("performance_validation", {}).items():
                status = "✅" if details["passed"] else "❌"
                print(f"   {status} {metric}: {details['value']} {details['unit']}")

        # Print test requirements details
        if "tests" in self.results["details"]:
            print("\n🧪 Test Requirements:")
            test_details = self.results["details"]["tests"]
            for metric, details in test_details.get("test_validation", {}).items():
                status = "✅" if details["passed"] else "❌"
                print(f"   {status} {metric}: {details['value']}{details['unit']}")

        return self.results

    def save_report(self, output_file: str = "ragchecker_quality_gates_report.json"):
        """Save quality gates report to file."""
        try:
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 Quality gates report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")

    def check_ci_cd_gates(self, stage: str = "pre_commit") -> bool:
        """Check if quality gates pass for specific CI/CD stage."""
        ci_cd_config = self.config.get("ci_cd_gates", {}).get(stage, {})

        if not ci_cd_config.get("enabled", False):
            print(f"⚠️ Quality gates not enabled for stage: {stage}")
            return True

        required_gates = ci_cd_config.get("required_gates", [])
        minimum_passing = ci_cd_config.get("minimum_passing", 1)

        # Count passing gates
        passing_gates = 0
        for gate in required_gates:
            # Check if gate passed in any section
            for section in self.results["details"].values():
                if "metrics_validation" in section and gate in section["metrics_validation"]:
                    if section["metrics_validation"][gate]["passed"]:
                        passing_gates += 1
                        break
                elif "performance_validation" in section and gate in section["performance_validation"]:
                    if section["performance_validation"][gate]["passed"]:
                        passing_gates += 1
                        break
                elif "test_validation" in section and gate in section["test_validation"]:
                    if section["test_validation"][gate]["passed"]:
                        passing_gates += 1
                        break

        passed = passing_gates >= minimum_passing
        print(f"\n🎯 CI/CD Stage '{stage}' Quality Gates:")
        print(f"   Required gates: {required_gates}")
        print(f"   Passing gates: {passing_gates}")
        print(f"   Minimum required: {minimum_passing}")
        print(f"   Status: {'✅ PASSED' if passed else '❌ FAILED'}")

        return passed


def main():
    """Main function for quality gates validation."""
    parser = argparse.ArgumentParser(description="RAGChecker Quality Gates Validation")
    parser.add_argument("evaluation_file", help="Path to evaluation results JSON file")
    parser.add_argument(
        "--config", default="config/ragchecker_quality_gates.json", help="Path to quality gates configuration file"
    )
    parser.add_argument(
        "--output", default="ragchecker_quality_gates_report.json", help="Output file for quality gates report"
    )
    parser.add_argument(
        "--stage",
        default="pre_commit",
        choices=["pre_commit", "pull_request", "deployment"],
        help="CI/CD stage for quality gates validation",
    )
    parser.add_argument("--performance-data", help="JSON file with performance metrics")
    parser.add_argument("--test-results", help="JSON file with test results")

    args = parser.parse_args()

    # Load performance data if provided
    performance_data = None
    if args.performance_data:
        try:
            with open(args.performance_data, "r") as f:
                performance_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading performance data: {e}")

    # Load test results if provided
    test_results = None
    if args.test_results:
        try:
            with open(args.test_results, "r") as f:
                test_results = json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading test results: {e}")

    # Initialize quality gates validator
    validator = RAGCheckerQualityGates(args.config)

    # Generate and save report
    validator.generate_report(args.evaluation_file, performance_data, test_results)
    validator.save_report(args.output)

    # Check CI/CD gates
    ci_cd_passed = validator.check_ci_cd_gates(args.stage)

    # Exit with appropriate code
    if ci_cd_passed:
        print("\n✅ Quality gates validation passed")
        sys.exit(0)
    else:
        print("\n❌ Quality gates validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
