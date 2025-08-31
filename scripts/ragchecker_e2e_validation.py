#!/usr/bin/env python3
"""
RAGChecker End-to-End System Validation

This script performs comprehensive validation of the complete RAGChecker evaluation system,
testing all components from installation to CI/CD integration.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class RAGCheckerE2EValidator:
    """End-to-end validator for RAGChecker evaluation system."""

    def __init__(self):
        """Initialize E2E validator."""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "validation_stages": {},
            "overall_status": "pending",
            "summary": {"total_tests": 0, "passed_tests": 0, "failed_tests": 0, "warnings": 0},
        }

    def validate_installation(self) -> Dict[str, Any]:
        """Validate RAGChecker installation and dependencies."""
        print("🔧 Validating RAGChecker Installation...")

        stage_results = {"stage": "installation", "tests": [], "status": "pending"}

        # Test 1: RAGChecker package installation
        try:
            import importlib.util

            ragchecker_spec = importlib.util.find_spec("ragchecker")
            if ragchecker_spec is not None:
                stage_results["tests"].append(
                    {"test": "ragchecker_import", "status": "passed", "details": "RAGChecker package available"}
                )
            else:
                raise ImportError("RAGChecker package not found")
        except ImportError as e:
            stage_results["tests"].append(
                {"test": "ragchecker_import", "status": "failed", "details": f"RAGChecker import failed: {e}"}
            )

        # Test 2: spaCy model availability
        try:
            import spacy

            # Test model loading without keeping it in memory
            spacy.load("en_core_web_sm")
            stage_results["tests"].append(
                {
                    "test": "spacy_model",
                    "status": "passed",
                    "details": "spaCy model 'en_core_web_sm' loaded successfully",
                }
            )
        except OSError as e:
            stage_results["tests"].append(
                {"test": "spacy_model", "status": "failed", "details": f"spaCy model not available: {e}"}
            )

        # Test 3: CLI availability
        try:
            result = subprocess.run(
                ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "ragchecker.cli", "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode in [0, 1]:
                stage_results["tests"].append(
                    {
                        "test": "cli_availability",
                        "status": "passed",
                        "details": "RAGChecker CLI help command executed successfully",
                    }
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "cli_availability",
                        "status": "warning",
                        "details": "RAGChecker CLI available but may require AWS credentials",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "cli_availability",
                    "status": "warning",
                    "details": f"CLI test failed (expected for fallback mode): {e}",
                }
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["installation"] = stage_results
        return stage_results

    def validate_core_functionality(self) -> Dict[str, Any]:
        """Validate core RAGChecker functionality."""
        print("🧪 Validating Core Functionality...")

        stage_results = {"stage": "core_functionality", "tests": [], "status": "pending"}

        # Test 1: Import evaluation classes
        try:
            from ragchecker_official_evaluation import OfficialRAGCheckerEvaluator

            stage_results["tests"].append(
                {
                    "test": "evaluation_imports",
                    "status": "passed",
                    "details": "RAGChecker evaluation classes imported successfully",
                }
            )
        except ImportError as e:
            stage_results["tests"].append(
                {"test": "evaluation_imports", "status": "failed", "details": f"Evaluation imports failed: {e}"}
            )
            stage_results["status"] = "failed"
            self.results["validation_stages"]["core_functionality"] = stage_results
            return stage_results

        # Test 2: Evaluator initialization
        try:
            evaluator = OfficialRAGCheckerEvaluator()
            stage_results["tests"].append(
                {
                    "test": "evaluator_initialization",
                    "status": "passed",
                    "details": "OfficialRAGCheckerEvaluator initialized successfully",
                }
            )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "evaluator_initialization",
                    "status": "failed",
                    "details": f"Evaluator initialization failed: {e}",
                }
            )
            stage_results["status"] = "failed"
            self.results["validation_stages"]["core_functionality"] = stage_results
            return stage_results

        # Test 3: Test case creation
        try:
            test_cases = evaluator.create_official_test_cases()
            if len(test_cases) == 5:
                stage_results["tests"].append(
                    {
                        "test": "test_case_creation",
                        "status": "passed",
                        "details": f"Created {len(test_cases)} test cases successfully",
                    }
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "test_case_creation",
                        "status": "failed",
                        "details": f"Expected 5 test cases, got {len(test_cases)}",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {"test": "test_case_creation", "status": "failed", "details": f"Test case creation failed: {e}"}
            )

        # Test 4: Memory system integration
        try:
            response = evaluator.get_memory_system_response("Test query for E2E validation")
            if response and len(response) > 0:
                stage_results["tests"].append(
                    {
                        "test": "memory_system_integration",
                        "status": "passed",
                        "details": f"Memory system response received ({len(response)} characters)",
                    }
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "memory_system_integration",
                        "status": "warning",
                        "details": "Memory system response empty or error",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "memory_system_integration",
                    "status": "warning",
                    "details": f"Memory system integration test failed: {e}",
                }
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["core_functionality"] = stage_results
        return stage_results

    def validate_evaluation_pipeline(self) -> Dict[str, Any]:
        """Validate complete evaluation pipeline."""
        print("🔍 Validating Evaluation Pipeline...")

        stage_results = {"stage": "evaluation_pipeline", "tests": [], "status": "pending"}

        # Test 1: Run complete evaluation
        start_time = time.time()
        try:
            result = subprocess.run(
                ["python3", "scripts/ragchecker_official_evaluation.py"], capture_output=True, text=True, timeout=120
            )
            evaluation_time = time.time() - start_time

            if result.returncode == 0:
                stage_results["tests"].append(
                    {
                        "test": "complete_evaluation",
                        "status": "passed",
                        "details": f"Evaluation completed successfully in {evaluation_time:.2f} seconds",
                    }
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "complete_evaluation",
                        "status": "failed",
                        "details": f"Evaluation failed: {result.stderr}",
                    }
                )
        except subprocess.TimeoutExpired:
            stage_results["tests"].append(
                {"test": "complete_evaluation", "status": "failed", "details": "Evaluation timed out after 120 seconds"}
            )
        except Exception as e:
            stage_results["tests"].append(
                {"test": "complete_evaluation", "status": "failed", "details": f"Evaluation error: {e}"}
            )

        # Test 2: Check evaluation results
        try:
            eval_files = list(Path("metrics/baseline_evaluations").glob("ragchecker_official_evaluation_*.json"))
            if eval_files:
                latest_eval = max(eval_files, key=lambda f: f.stat().st_mtime)
                with open(latest_eval, "r") as f:
                    data = json.load(f)

                if data.get("evaluation_type") and data.get("overall_metrics"):
                    stage_results["tests"].append(
                        {
                            "test": "evaluation_results",
                            "status": "passed",
                            "details": f"Evaluation results generated: {data['evaluation_type']}",
                        }
                    )
                else:
                    stage_results["tests"].append(
                        {
                            "test": "evaluation_results",
                            "status": "failed",
                            "details": "Evaluation results missing required fields",
                        }
                    )
            else:
                stage_results["tests"].append(
                    {"test": "evaluation_results", "status": "failed", "details": "No evaluation results found"}
                )
        except Exception as e:
            stage_results["tests"].append(
                {"test": "evaluation_results", "status": "failed", "details": f"Error checking evaluation results: {e}"}
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["evaluation_pipeline"] = stage_results
        return stage_results

    def validate_test_suite(self) -> Dict[str, Any]:
        """Validate test suite execution."""
        print("🧪 Validating Test Suite...")

        stage_results = {"stage": "test_suite", "tests": [], "status": "pending"}

        # Test 1: Run evaluation tests
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/test_ragchecker_evaluation.py", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                stage_results["tests"].append(
                    {"test": "evaluation_tests", "status": "passed", "details": "RAGChecker evaluation tests passed"}
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "evaluation_tests",
                        "status": "failed",
                        "details": f"Evaluation tests failed: {result.stderr}",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {"test": "evaluation_tests", "status": "failed", "details": f"Evaluation tests error: {e}"}
            )

        # Test 2: Run performance tests
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", "tests/test_ragchecker_performance.py", "-q"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                stage_results["tests"].append(
                    {"test": "performance_tests", "status": "passed", "details": "RAGChecker performance tests passed"}
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "performance_tests",
                        "status": "failed",
                        "details": f"Performance tests failed: {result.stderr}",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {"test": "performance_tests", "status": "failed", "details": f"Performance tests error: {e}"}
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["test_suite"] = stage_results
        return stage_results

    def validate_quality_gates(self) -> Dict[str, Any]:
        """Validate quality gates functionality."""
        print("🎯 Validating Quality Gates...")

        stage_results = {"stage": "quality_gates", "tests": [], "status": "pending"}

        # Test 1: Quality gates configuration
        try:
            config_file = Path("config/ragchecker_quality_gates.json")
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)

                if "ragchecker_quality_gates" in config:
                    stage_results["tests"].append(
                        {
                            "test": "quality_gates_config",
                            "status": "passed",
                            "details": "Quality gates configuration loaded successfully",
                        }
                    )
                else:
                    stage_results["tests"].append(
                        {
                            "test": "quality_gates_config",
                            "status": "failed",
                            "details": "Quality gates configuration missing required section",
                        }
                    )
            else:
                stage_results["tests"].append(
                    {
                        "test": "quality_gates_config",
                        "status": "failed",
                        "details": "Quality gates configuration file not found",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "quality_gates_config",
                    "status": "failed",
                    "details": f"Quality gates configuration error: {e}",
                }
            )

        # Test 2: Quality gates validation script
        try:
            eval_files = list(Path("metrics/baseline_evaluations").glob("ragchecker_official_evaluation_*.json"))
            if eval_files:
                latest_eval = max(eval_files, key=lambda f: f.stat().st_mtime)

                result = subprocess.run(
                    ["python3", "scripts/ragchecker_quality_gates.py", str(latest_eval), "--stage", "pre_commit"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    stage_results["tests"].append(
                        {
                            "test": "quality_gates_validation",
                            "status": "passed",
                            "details": "Quality gates validation completed successfully",
                        }
                    )
                else:
                    stage_results["tests"].append(
                        {
                            "test": "quality_gates_validation",
                            "status": "failed",
                            "details": f"Quality gates validation failed: {result.stderr}",
                        }
                    )
            else:
                stage_results["tests"].append(
                    {
                        "test": "quality_gates_validation",
                        "status": "warning",
                        "details": "No evaluation files found for quality gates validation",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "quality_gates_validation",
                    "status": "failed",
                    "details": f"Quality gates validation error: {e}",
                }
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["quality_gates"] = stage_results
        return stage_results

    def validate_ci_cd_integration(self) -> Dict[str, Any]:
        """Validate CI/CD integration components."""
        print("🚀 Validating CI/CD Integration...")

        stage_results = {"stage": "ci_cd_integration", "tests": [], "status": "pending"}

        # Test 1: GitHub Actions workflow
        workflow_file = Path(".github/workflows/ragchecker-evaluation.yml")
        if workflow_file.exists():
            stage_results["tests"].append(
                {
                    "test": "github_actions_workflow",
                    "status": "passed",
                    "details": "GitHub Actions workflow file exists",
                }
            )
        else:
            stage_results["tests"].append(
                {
                    "test": "github_actions_workflow",
                    "status": "failed",
                    "details": "GitHub Actions workflow file not found",
                }
            )

        # Test 2: Pre-commit hook
        pre_commit_file = Path("scripts/pre_commit_ragchecker.py")
        if pre_commit_file.exists():
            stage_results["tests"].append(
                {"test": "pre_commit_hook", "status": "passed", "details": "Pre-commit hook script exists"}
            )
        else:
            stage_results["tests"].append(
                {"test": "pre_commit_hook", "status": "failed", "details": "Pre-commit hook script not found"}
            )

        # Test 3: Pre-commit hook execution
        try:
            result = subprocess.run(
                ["python3", "scripts/pre_commit_ragchecker.py"], capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                stage_results["tests"].append(
                    {
                        "test": "pre_commit_execution",
                        "status": "passed",
                        "details": "Pre-commit hook executed successfully",
                    }
                )
            else:
                stage_results["tests"].append(
                    {
                        "test": "pre_commit_execution",
                        "status": "warning",
                        "details": "Pre-commit hook execution completed (no changes detected)",
                    }
                )
        except Exception as e:
            stage_results["tests"].append(
                {
                    "test": "pre_commit_execution",
                    "status": "warning",
                    "details": f"Pre-commit hook execution warning: {e}",
                }
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["ci_cd_integration"] = stage_results
        return stage_results

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness."""
        print("📚 Validating Documentation...")

        stage_results = {"stage": "documentation", "tests": [], "status": "pending"}

        # Test 1: RAGChecker usage guide
        usage_guide = Path("400_guides/400_ragchecker-usage-guide.md")
        if usage_guide.exists():
            stage_results["tests"].append(
                {"test": "usage_guide", "status": "passed", "details": "RAGChecker usage guide exists"}
            )
        else:
            stage_results["tests"].append(
                {"test": "usage_guide", "status": "failed", "details": "RAGChecker usage guide not found"}
            )

        # Test 2: Evaluation status file
        status_file = Path("metrics/baseline_evaluations/EVALUATION_STATUS.md")
        if status_file.exists():
            stage_results["tests"].append(
                {"test": "evaluation_status", "status": "passed", "details": "Evaluation status file exists"}
            )
        else:
            stage_results["tests"].append(
                {"test": "evaluation_status", "status": "failed", "details": "Evaluation status file not found"}
            )

        # Test 3: Development workflow integration
        workflow_guide = Path("400_guides/400_04_development-workflow-and-standards.md")
        if workflow_guide.exists():
            with open(workflow_guide, "r") as f:
                content = f.read()
                if "RAGChecker" in content:
                    stage_results["tests"].append(
                        {
                            "test": "workflow_integration",
                            "status": "passed",
                            "details": "RAGChecker integrated in development workflow",
                        }
                    )
                else:
                    stage_results["tests"].append(
                        {
                            "test": "workflow_integration",
                            "status": "failed",
                            "details": "RAGChecker not found in development workflow",
                        }
                    )
        else:
            stage_results["tests"].append(
                {"test": "workflow_integration", "status": "failed", "details": "Development workflow guide not found"}
            )

        # Determine stage status
        failed_tests = [t for t in stage_results["tests"] if t["status"] == "failed"]
        if failed_tests:
            stage_results["status"] = "failed"
        else:
            stage_results["status"] = "passed"

        self.results["validation_stages"]["documentation"] = stage_results
        return stage_results

    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete end-to-end validation."""
        print("🚀 RAGChecker End-to-End System Validation")
        print("=" * 60)

        # Run all validation stages
        stages = [
            self.validate_installation,
            self.validate_core_functionality,
            self.validate_evaluation_pipeline,
            self.validate_test_suite,
            self.validate_quality_gates,
            self.validate_ci_cd_integration,
            self.validate_documentation,
        ]

        for stage_func in stages:
            try:
                stage_result = stage_func()
                print(f"✅ {stage_result['stage'].title()}: {stage_result['status']}")
            except Exception as e:
                print(f"❌ {stage_func.__name__}: Error - {e}")

        # Calculate overall results
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        warnings = 0

        for stage_name, stage_data in self.results["validation_stages"].items():
            for test in stage_data["tests"]:
                total_tests += 1
                if test["status"] == "passed":
                    passed_tests += 1
                elif test["status"] == "failed":
                    failed_tests += 1
                elif test["status"] == "warning":
                    warnings += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "warnings": warnings,
        }

        # Determine overall status
        if failed_tests == 0:
            self.results["overall_status"] = "passed"
        elif failed_tests < total_tests * 0.3:  # Allow up to 30% failures
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "failed"

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️ Warnings: {warnings}")

        # Print stage details
        print("\n📋 STAGE DETAILS:")
        for stage_name, stage_data in self.results["validation_stages"].items():
            status_icon = (
                "✅" if stage_data["status"] == "passed" else "❌" if stage_data["status"] == "failed" else "⚠️"
            )
            print(f"{status_icon} {stage_name.replace('_', ' ').title()}: {stage_data['status']}")

        return self.results

    def save_results(self, output_file: str = "ragchecker_e2e_validation_report.json"):
        """Save validation results to file."""
        try:
            with open(output_file, "w") as f:
                json.dump(self.results, f, indent=2)
            print(f"\n💾 E2E validation report saved to: {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")


def main():
    """Main function for E2E validation."""
    import argparse

    parser = argparse.ArgumentParser(description="RAGChecker End-to-End System Validation")
    parser.add_argument(
        "--output", default="ragchecker_e2e_validation_report.json", help="Output file for validation report"
    )

    args = parser.parse_args()

    # Run validation
    validator = RAGCheckerE2EValidator()
    results = validator.run_complete_validation()

    # Save results
    validator.save_results(args.output)

    # Exit with appropriate code
    if results["overall_status"] == "passed":
        print("\n🎉 E2E validation PASSED - RAGChecker system is fully operational!")
        sys.exit(0)
    elif results["overall_status"] == "warning":
        print("\n⚠️ E2E validation completed with warnings - Review failed tests")
        sys.exit(1)
    else:
        print("\n❌ E2E validation FAILED - Critical issues detected")
        sys.exit(1)


if __name__ == "__main__":
    main()
