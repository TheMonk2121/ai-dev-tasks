from __future__ import annotations
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
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

class CoderRoleValidator:
    """Comprehensive validator for Coder Role implementation."""

    def __init__(self, project_root: Path):
        """Initialize the validator with project root."""
        self.project_root = project_root
        self.results: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "PENDING",
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "validation_results": {},
        }

    def validate_memory_rehydration_system(self) -> dict[str, Any]:
        """Validate memory rehydration system functionality."""
        print("🔍 Validating Memory Rehydration System...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        # Check script existence
        script_path = self.project_root / "scripts" / "memory_up.sh"
        if script_path.exists():
            result
        else:
            result
            result

        # Check DSPy memory rehydrator
        dspy_path = self.project_root / "src" / "utils" / "memory_rehydrator.py"
        if dspy_path.exists():
            result
        else:
            result
            result

        # Test command execution
        try:
            cmd_result = subprocess.run(
                [sys.executable, str(script_path), "coder", "validation test"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cmd_result.returncode == 0:
                result
                result
            else:
                result
                result

        except Exception as e:
            result
            result

        # Determine overall status
        if all(result
            result
        else:
            result

        return results

    def validate_role_instructions(self) -> dict[str, Any]:
        """Validate role instructions in memory rehydrator."""
        print("🔍 Validating Role Instructions...")

        results = {"status": "PENDING", "checks": {}, "errors": []}

        rehydrator_path = self.project_root / "src" / "utils" / "memory_rehydrator.py"

        if not rehydrator_path.exists():
            result
            result
            return results

        content = rehydrator_path.read_text()

        # Check for ROLE_INSTRUCTIONS
        if "ROLE_INSTRUCTIONS" in content:
            result
        else:
            result
            result

        # Check for coder role
        if '"coder"' in content:
            result
        else:
            result
            result

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
                result
            else:
                result
                result

        # Check for ROLE_FILES
        if "ROLE_FILES" in content:
            result
        else:
            result
            result

        # Check for required files in coder role
        required_files = [
            "Task-List-Chunk-Relationship-Visualization.md",
            "scripts/dependency_monitor.py",
            "400_guides/400_graph-visualization-guide.md",
        ]

        for file_path in required_files:
            if file_path in content:
                result
            else:
                result
                result

        # Determine overall status
        if all(result
            result
        else:
            result

        return results

    def validate_documentation_enhancements(self) -> dict[str, Any]:
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
                    result
                else:
                    result
                    result

            # Check ROLE_PINS
            if '"coder"' in content:
                result
            else:
                result
                result
        else:
            result
            result

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
                    result
                else:
                    result
                    result
        else:
            result
            result

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
                    result
                else:
                    result
                    result
        else:
            result
            result

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
                    result
                else:
                    result
                    result
        else:
            result
            result

        # Determine overall status
        if all(result
            result
        else:
            result

        return results

    def validate_metadata_tags(self) -> dict[str, Any]:
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
                    result
                else:
                    result
                    result

                if '"coder"' in content:
                    result
                else:
                    result
                    result
            else:
                result
                result

        # Determine overall status
        if all(result
            result
        else:
            result

        return results

    def run_integration_tests(self) -> dict[str, Any]:
        """Run integration tests and collect results."""
        print("🔍 Running Integration Tests...")

        results = {"status": "PENDING", "tests_passed": 0, "tests_failed": 0, "total_tests": 0, "errors": []}

        test_file = self.project_root / "tests" / "test_coder_role_integration.py"

        if not test_file.exists():
            result
            result
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
                    result
                    result
                elif "FAILED" in line:
                    result
                    result
                elif "ERROR" in line:
                    result
                    result

            if cmd_result.returncode == 0 and result
                result
            else:
                result
                if cmd_result.stderr:
                    result

        except Exception as e:
            result
            result

        return results

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        print("📊 Generating Validation Report...")

        # Run all validations
        self.result
        self.result
        self.result
        self.result
        self.result

        # Calculate overall status
        all_passed = all(result

        self.result

        # Count tests
        integration_results = self.result
        self.result
        self.result
        self.result

        # Generate report
        report = f"""
================================================================================
🧠 CODER ROLE IMPLEMENTATION VALIDATION REPORT
================================================================================
Timestamp: {self.result
Overall Status: {self.result

📊 SUMMARY
- Integration Tests: {self.result
- Validation Categories: {len(self.result

🔍 DETAILED RESULTS
"""

        for category, result in self.result
            status_emoji = "✅" if result:
            report += f"\n{status_emoji} {category.replace('_', ' ').title()}: {result

            if result:
                report += f"\n   Errors: {len(result
                for error in result.items()
                    report += f"\n     - {error}"
                if len(result
                    report += f"\n     ... and {len(result

        report += """

🎯 RECOMMENDATIONS
"""

        if self.result
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
- Memory Rehydrator: scripts/memory_up.sh
- DSPy Rehydrator: src/utils/memory_rehydrator.py

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
    if validator.result
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
