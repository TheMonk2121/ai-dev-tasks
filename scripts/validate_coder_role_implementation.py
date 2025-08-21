#!/usr/bin/env python3
"""
Comprehensive validation script for Coder Role implementation.

This script validates all aspects of the enhanced coder role implementation:
- Memory rehydration functionality
- Role-specific instructions
- File analysis integration
- Testing strategy compliance
- Best practices enforcement
- Documentation completeness
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class CoderRoleValidator:
    """Comprehensive validator for Coder Role implementation."""

    def __init__(self, project_root: Path):
        """Initialize the validator with project root."""
        self.project_root = project_root
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PENDING",
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "validation_results": {},
        }

    def validate_memory_rehydration_system(self) -> Dict[str, Any]:
        """Validate memory rehydration system functionality."""
        print("🔍 Validating Memory Rehydration System...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        # Check script existence
        script_path = self.project_root / "scripts" / "cursor_memory_rehydrate.py"
        if script_path.exists():
            results["checks"]["script_exists"] = True
        else:
            results["checks"]["script_exists"] = False
            results["errors"].append("Memory rehydrator script not found")

        # Check DSPy memory rehydrator
        dspy_path = self.project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"
        if dspy_path.exists():
            results["checks"]["dspy_rehydrator_exists"] = True
        else:
            results["checks"]["dspy_rehydrator_exists"] = False
            results["errors"].append("DSPy memory rehydrator not found")

        # Test command execution
        try:
            cmd_result = subprocess.run(
                [sys.executable, str(script_path), "coder", "validation test"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cmd_result.returncode == 0:
                results["checks"]["command_execution"] = True
                results["checks"]["output_produced"] = "MEMORY REHYDRATION BUNDLE" in cmd_result.stdout
            else:
                results["checks"]["command_execution"] = False
                results["errors"].append(f"Command execution failed: {cmd_result.stderr}")

        except Exception as e:
            results["checks"]["command_execution"] = False
            results["errors"].append(f"Command execution error: {e}")

        # Determine overall status
        if all(results["checks"].values()) and not results["errors"]:
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"

        return results

    def validate_role_instructions(self) -> Dict[str, Any]:
        """Validate role instructions in memory rehydrator."""
        print("🔍 Validating Role Instructions...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        rehydrator_path = self.project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"

        if not rehydrator_path.exists():
            results["status"] = "FAIL"
            results["errors"].append("Memory rehydrator file not found")
            return results

        content = rehydrator_path.read_text()

        # Check for ROLE_INSTRUCTIONS
        if "ROLE_INSTRUCTIONS" in content:
            results["checks"]["role_instructions_exists"] = True
        else:
            results["checks"]["role_instructions_exists"] = False
            results["errors"].append("ROLE_INSTRUCTIONS dictionary not found")

        # Check for coder role
        if '"coder"' in content:
            results["checks"]["coder_role_defined"] = True
        else:
            results["checks"]["coder_role_defined"] = False
            results["errors"].append("Coder role not defined in ROLE_INSTRUCTIONS")

        # Check for required categories
        required_categories = [
            "focus",
            "context",
            "validation",
            "required_standards",
            "safety_protocol",
            "quality_gates",
            "testing_guide",
            "tool_usage",
        ]

        for category in required_categories:
            if f'"{category}":' in content:
                results["checks"][f"category_{category}"] = True
            else:
                results["checks"][f"category_{category}"] = False
                results["errors"].append(f"Missing category: {category}")

        # Check for ROLE_FILES
        if "ROLE_FILES" in content:
            results["checks"]["role_files_exists"] = True
        else:
            results["checks"]["role_files_exists"] = False
            results["errors"].append("ROLE_FILES dictionary not found")

        # Check for required files in coder role
        required_files = [
            "Task-List-Chunk-Relationship-Visualization.md",
            "scripts/dependency_monitor.py",
            "400_guides/400_graph-visualization-guide.md",
        ]

        for file_path in required_files:
            if file_path in content:
                results["checks"][f"file_{file_path.replace('/', '_').replace('.', '_')}"] = True
            else:
                results["checks"][f"file_{file_path.replace('/', '_').replace('.', '_')}"] = False
                results["errors"].append(f"Required file not found in ROLE_FILES: {file_path}")

        # Determine overall status
        if all(results["checks"].values()) and not results["errors"]:
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"

        return results

    def validate_documentation_enhancements(self) -> Dict[str, Any]:
        """Validate documentation enhancements."""
        print("🔍 Validating Documentation Enhancements...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        # Check DSPy development context
        context_file = self.project_root / "100_memory" / "104_dspy-development-context.md"
        if context_file.exists():
            content = context_file.read_text()

            required_sections = [
                "COMPREHENSIVE CODER ROLE INSTRUCTIONS",
                "Core Coder Role Behavior - ALWAYS FOLLOW",
                "Technical Standards - REQUIRED",
                "Safety Protocol - BEFORE ANY CHANGES",
                "Quality Gates - MUST PASS",
                "CODER ROLE QUICK REFERENCE",
                "COMPREHENSIVE TESTING GUIDE",
                "TOOL USAGE GUIDE",
            ]

            for section in required_sections:
                if section in content:
                    results["checks"][f"context_{section.replace(' ', '_').replace('-', '_')}"] = True
                else:
                    results["checks"][f"context_{section.replace(' ', '_').replace('-', '_')}"] = False
                    results["errors"].append(f"Missing section in DSPy context: {section}")

            # Check ROLE_PINS
            if '"coder"' in content:
                results["checks"]["context_role_pins"] = True
            else:
                results["checks"]["context_role_pins"] = False
                results["errors"].append("Missing coder role in ROLE_PINS for DSPy context")
        else:
            results["checks"]["context_file_exists"] = False
            results["errors"].append("DSPy development context file not found")

        # Check comprehensive coding best practices
        best_practices_file = self.project_root / "400_guides" / "400_comprehensive-coding-best-practices.md"
        if best_practices_file.exists():
            content = best_practices_file.read_text()

            required_sections = [
                "CODER ROLE SPECIFIC GUIDANCE",
                "CODER ROLE IMPLEMENTATION PATTERNS",
                "Memory Rehydration Pattern",
                "Example-First Implementation Pattern",
                "Code Reuse Pattern (70/30 Rule)",
                "Test-First Development Pattern",
            ]

            for section in required_sections:
                if section in content:
                    results["checks"][f"best_practices_{section.replace(' ', '_').replace('-', '_')}"] = True
                else:
                    results["checks"][f"best_practices_{section.replace(' ', '_').replace('-', '_')}"] = False
                    results["errors"].append(f"Missing section in best practices: {section}")
        else:
            results["checks"]["best_practices_file_exists"] = False
            results["errors"].append("Comprehensive coding best practices file not found")

        # Check file analysis guide
        file_analysis_file = self.project_root / "400_guides" / "400_file-analysis-guide.md"
        if file_analysis_file.exists():
            content = file_analysis_file.read_text()

            required_sections = [
                "CODER ROLE SPECIFIC ANALYSIS",
                "Coder-Specific Safety Rules",
                "NEVER delete Tier 1 files",
                "Always check dependencies",
                "Use memory rehydration",
                "Follow the 70/30 rule",
            ]

            for section in required_sections:
                if section in content:
                    results["checks"][f"file_analysis_{section.replace(' ', '_').replace('-', '_')}"] = True
                else:
                    results["checks"][f"file_analysis_{section.replace(' ', '_').replace('-', '_')}"] = False
                    results["errors"].append(f"Missing section in file analysis: {section}")
        else:
            results["checks"]["file_analysis_file_exists"] = False
            results["errors"].append("File analysis guide not found")

        # Check testing strategy guide
        testing_strategy_file = self.project_root / "400_guides" / "400_testing-strategy-guide.md"
        if testing_strategy_file.exists():
            content = testing_strategy_file.read_text()

            required_sections = [
                "CODER ROLE TESTING REQUIREMENTS",
                "Test-First Development (TDD)",
                "Memory Rehydration",
                "Example-First Testing",
                "Code Reuse in Tests",
                "Function Length Validation",
            ]

            for section in required_sections:
                if section in content:
                    results["checks"][f"testing_strategy_{section.replace(' ', '_').replace('-', '_')}"] = True
                else:
                    results["checks"][f"testing_strategy_{section.replace(' ', '_').replace('-', '_')}"] = False
                    results["errors"].append(f"Missing section in testing strategy: {section}")
        else:
            results["checks"]["testing_strategy_file_exists"] = False
            results["errors"].append("Testing strategy guide not found")

        # Determine overall status
        if all(results["checks"].values()) and not results["errors"]:
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"

        return results

    def validate_metadata_tags(self) -> Dict[str, Any]:
        """Validate metadata tags for coder role inclusion."""
        print("🔍 Validating Metadata Tags...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        files_to_check = [
            ("Task-List-Chunk-Relationship-Visualization.md", "ROLE_PINS"),
            ("scripts/dependency_monitor.py", "ROLE_PINS"),
            ("400_guides/400_graph-visualization-guide.md", "ROLE_PINS"),
            ("100_memory/104_dspy-development-context.md", "ROLE_PINS"),
        ]

        for file_path, required_tag in files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()

                if required_tag in content:
                    results["checks"][f"tag_{file_path.replace('/', '_').replace('.', '_')}"] = True
                else:
                    results["checks"][f"tag_{file_path.replace('/', '_').replace('.', '_')}"] = False
                    results["errors"].append(f"Missing {required_tag} in {file_path}")

                if '"coder"' in content:
                    results["checks"][f"coder_role_{file_path.replace('/', '_').replace('.', '_')}"] = True
                else:
                    results["checks"][f"coder_role_{file_path.replace('/', '_').replace('.', '_')}"] = False
                    results["errors"].append(f"Missing coder role in {required_tag} for {file_path}")
            else:
                results["checks"][f"file_exists_{file_path.replace('/', '_').replace('.', '_')}"] = False
                results["errors"].append(f"File not found: {file_path}")

        # Determine overall status
        if all(results["checks"].values()) and not results["errors"]:
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"

        return results

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests and collect results."""
        print("🔍 Running Integration Tests...")

        results = {"status": "PENDING", "tests_passed": 0, "tests_failed": 0, "total_tests": 0, "errors": []}

        test_file = self.project_root / "tests" / "test_coder_role_integration.py"

        if not test_file.exists():
            results["status"] = "FAIL"
            results["errors"].append("Integration test file not found")
            return results

        try:
            cmd_result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse test results
            output_lines = cmd_result.stdout.split("\n")

            for line in output_lines:
                if "PASSED" in line:
                    results["tests_passed"] += 1
                    results["total_tests"] += 1
                elif "FAILED" in line:
                    results["tests_failed"] += 1
                    results["total_tests"] += 1
                elif "ERROR" in line:
                    results["tests_failed"] += 1
                    results["total_tests"] += 1

            if cmd_result.returncode == 0 and results["tests_failed"] == 0:
                results["status"] = "PASS"
            else:
                results["status"] = "FAIL"
                if cmd_result.stderr:
                    results["errors"].append(f"Test execution errors: {cmd_result.stderr}")

        except Exception as e:
            results["status"] = "FAIL"
            results["errors"].append(f"Test execution error: {e}")

        return results

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        print("📊 Generating Validation Report...")

        # Run all validations
        self.results["validation_results"]["memory_rehydration"] = self.validate_memory_rehydration_system()
        self.results["validation_results"]["role_instructions"] = self.validate_role_instructions()
        self.results["validation_results"]["documentation"] = self.validate_documentation_enhancements()
        self.results["validation_results"]["metadata_tags"] = self.validate_metadata_tags()
        self.results["validation_results"]["integration_tests"] = self.run_integration_tests()

        # Calculate overall status
        all_passed = all(result["status"] == "PASS" for result in self.results["validation_results"].values())

        self.results["overall_status"] = "PASS" if all_passed else "FAIL"

        # Count tests
        integration_results = self.results["validation_results"]["integration_tests"]
        self.results["tests_passed"] = integration_results["tests_passed"]
        self.results["tests_failed"] = integration_results["tests_failed"]
        self.results["total_tests"] = integration_results["total_tests"]

        # Generate report
        report = f"""
================================================================================
🧠 CODER ROLE IMPLEMENTATION VALIDATION REPORT
================================================================================
Timestamp: {self.results['timestamp']}
Overall Status: {self.results['overall_status']}

📊 SUMMARY
- Integration Tests: {self.results['tests_passed']}/{self.results['total_tests']} passed
- Validation Categories: {len(self.results['validation_results'])} checked

🔍 DETAILED RESULTS
"""

        for category, result in self.results["validation_results"].items():
            status_emoji = "✅" if result["status"] == "PASS" else "❌"
            report += f"\n{status_emoji} {category.replace('_', ' ').title()}: {result['status']}"

            if result.get("errors"):
                report += f"\n   Errors: {len(result['errors'])}"
                for error in result["errors"][:3]:  # Show first 3 errors
                    report += f"\n     - {error}"
                if len(result["errors"]) > 3:
                    report += f"\n     ... and {len(result['errors']) - 3} more"

        report += """

🎯 RECOMMENDATIONS
"""

        if self.results["overall_status"] == "PASS":
            report += """
✅ All validations passed! The Coder Role implementation is complete and ready for use.

🚀 Next Steps:
1. Use the enhanced coder role for development tasks
2. Monitor performance and gather feedback
3. Consider additional enhancements based on usage patterns
"""
        else:
            report += """
❌ Some validations failed. Please review and fix the issues above.

🔧 Common Fixes:
1. Check file paths and ensure all required files exist
2. Verify metadata tags are properly formatted
3. Run integration tests to identify specific failures
4. Review documentation for missing sections
"""

        report += f"""

📁 Validation Details
- Project Root: {self.project_root}
- Integration Test File: tests/test_coder_role_integration.py
- Memory Rehydrator: scripts/cursor_memory_rehydrate.py
- DSPy Rehydrator: dspy-rag-system/src/utils/memory_rehydrator.py

================================================================================
"""

        return report

    def save_results(self, output_file: Path) -> None:
        """Save validation results to JSON file."""
        output_file.write_text(json.dumps(self.results, indent=2))
        print(f"📄 Results saved to: {output_file}")

    def run_validation(self, save_results: bool = True) -> str:
        """Run complete validation and return report."""
        print("🚀 Starting Coder Role Implementation Validation...")

        report = self.generate_report()

        if save_results:
            results_file = self.project_root / "artifacts" / "coder_role_validation_results.json"
            results_file.parent.mkdir(exist_ok=True)
            self.save_results(results_file)

        return report


def main():
    """Main entry point for the validation script."""
    project_root = Path(__file__).parent.parent

    validator = CoderRoleValidator(project_root)
    report = validator.run_validation()

    print(report)

    # Exit with appropriate code
    if validator.results["overall_status"] == "PASS":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
