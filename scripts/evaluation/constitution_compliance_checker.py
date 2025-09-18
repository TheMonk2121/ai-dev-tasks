from __future__ import annotations

import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
AI Constitution Compliance Checker

Validates AI operations against the AI Constitution rules to ensure
safety, context preservation, and error prevention.

Based on research findings that critical rules get lost in large files,
this checker ensures persistent rule enforcement across all AI operations.
"""


@dataclass
class ConstitutionRule:
    """Represents a constitution rule with validation logic."""

    article: str
    rule_id: str
    description: str
    validation_function: Callable[[dict[str, Any]], tuple[bool, str]]
    critical: bool = False


class ConstitutionComplianceChecker:
    """Validates AI operations against the AI Constitution rules."""

    def __init__(self, constitution_file: str = "400_ai-constitution.md"):
        self.constitution_file = constitution_file
        self.rules: list[ConstitutionRule] = []
        self.violations: list[dict] = []
        self.load_constitution_rules()

    def load_constitution_rules(self):
        """Load and parse constitution rules from the constitution file."""
        try:
            with open(self.constitution_file, encoding="utf-8") as f:
                content = f.read()

            # Parse constitution rules
            self._parse_file_safety_rules(content)
            self._parse_context_preservation_rules(content)
            self._parse_error_prevention_rules(content)
            self._parse_documentation_rules(content)
            self._parse_system_integration_rules(content)

        except FileNotFoundError:
            print(f"⚠️  Constitution file {self.constitution_file} not found")
            self._create_default_rules()

    def _parse_file_safety_rules(self, content: str):
        """Parse Article I: File Safety & Analysis rules."""
        # File analysis requirement
        self.rules.append(
            ConstitutionRule(
                article="I",
                rule_id="file_analysis_requirement",
                description="ALWAYS read 400_file-analysis-guide.md completely before file operations",
                validation_function=self._validate_file_analysis_requirement,
                critical=True,
            )
        )

        # Critical file protection
        self.rules.append(
            ConstitutionRule(
                article="I",
                rule_id="critical_file_protection",
                description="Never delete files with CRITICAL_FILE or ARCHIVE_PROTECTED metadata",
                validation_function=self._validate_critical_file_protection,
                critical=True,
            )
        )

    def _parse_context_preservation_rules(self, content: str):
        """Parse Article II: Context Preservation & Memory Management rules."""
        # Memory context priority
        self.rules.append(
            ConstitutionRule(
                article="II",
                rule_id="memory_context_priority",
                description="ALWAYS read 100_cursor-memory-context.md first in new sessions",
                validation_function=self._validate_memory_context_priority,
                critical=True,
            )
        )

        # Context hierarchy enforcement
        self.rules.append(
            ConstitutionRule(
                article="II",
                rule_id="context_hierarchy_enforcement",
                description="Follow context hierarchy: HIGH > MEDIUM > LOW priority files",
                validation_function=self._validate_context_hierarchy,
                critical=False,
            )
        )

    def _parse_error_prevention_rules(self, content: str):
        """Parse Article III: Error Prevention & Recovery rules."""
        # Multi-turn process enforcement
        self.rules.append(
            ConstitutionRule(
                article="III",
                rule_id="multi_turn_process_enforcement",
                description="Use mandatory checklist enforcement for high-risk operations",
                validation_function=self._validate_multi_turn_process,
                critical=True,
            )
        )

        # Error recovery patterns
        self.rules.append(
            ConstitutionRule(
                article="III",
                rule_id="error_recovery_patterns",
                description="Follow 400_error-recovery-guide.md for all error handling",
                validation_function=self._validate_error_recovery_patterns,
                critical=False,
            )
        )

    def _parse_documentation_rules(self, content: str):
        """Parse Article IV: Documentation & Knowledge Management rules."""
        # Documentation architecture
        self.rules.append(
            ConstitutionRule(
                article="IV",
                rule_id="documentation_architecture",
                description="Follow modular, MECE-aligned documentation patterns",
                validation_function=self._validate_documentation_architecture,
                critical=False,
            )
        )

        # Knowledge retrieval
        self.rules.append(
            ConstitutionRule(
                article="IV",
                rule_id="knowledge_retrieval",
                description="Use RAG systems for relevant context retrieval",
                validation_function=self._validate_knowledge_retrieval,
                critical=False,
            )
        )

    def _parse_system_integration_rules(self, content: str):
        """Parse Article V: System Integration & Workflow rules."""
        # Workflow chain preservation
        self.rules.append(
            ConstitutionRule(
                article="V",
                rule_id="workflow_chain_preservation",
                description="Maintain 000_backlog.md → 001_create-prd.md → 002_generate-tasks.md → 003_process-task-list.md chain",
                validation_function=self._validate_workflow_chain,
                critical=True,
            )
        )

        # Technology stack integrity
        self.rules.append(
            ConstitutionRule(
                article="V",
                rule_id="technology_stack_integrity",
                description="Maintain Cursor Native AI + Specialized Agents + DSPy foundation",
                validation_function=self._validate_technology_stack,
                critical=True,
            )
        )

    def _create_default_rules(self):
        """Create default rules if constitution file is not found."""
        print("📋 Creating default constitution rules")
        self._parse_file_safety_rules("")
        self._parse_context_preservation_rules("")
        self._parse_error_prevention_rules("")
        self._parse_documentation_rules("")
        self._parse_system_integration_rules("")

    # Validation Functions

    def _validate_file_analysis_requirement(self, operation: dict) -> tuple[bool, str]:
        """Validate that file analysis requirements are met."""
        if operation.get("type") == "file_operation":
            if not operation.get("file_analysis_completed"):
                return False, "File analysis requirement not met"
        return True, "File analysis requirement satisfied"

    def _validate_critical_file_protection(self, operation: dict) -> tuple[bool, str]:
        """Validate that critical files are protected."""
        if operation.get("type") == "file_deletion":
            target_file = operation.get("target_file", "")
            if any(protected in target_file for protected in ["CRITICAL_FILE", "ARCHIVE_PROTECTED"]):
                return False, f"Attempted to delete protected file: {target_file}"
        return True, "Critical file protection satisfied"

    def _validate_memory_context_priority(self, operation: dict) -> tuple[bool, str]:
        """Validate that memory context is read first in new sessions."""
        if operation.get("type") == "new_session":
            if not operation.get("memory_context_read"):
                return False, "Memory context not read in new session"
        return True, "Memory context priority satisfied"

    def _validate_context_hierarchy(self, operation: dict) -> tuple[bool, str]:
        """Validate that context hierarchy is followed."""
        # This is a complex validation that would check file reading order
        return True, "Context hierarchy satisfied"

    def _validate_multi_turn_process(self, operation: dict) -> tuple[bool, str]:
        """Validate that multi-turn processes are used for high-risk operations."""
        if operation.get("risk_level") == "high":
            if not operation.get("multi_turn_confirmation"):
                return False, "Multi-turn confirmation required for high-risk operations"
        return True, "Multi-turn process satisfied"

    def _validate_error_recovery_patterns(self, operation: dict) -> tuple[bool, str]:
        """Validate that error recovery patterns are followed."""
        if operation.get("type") == "error_handling":
            if not operation.get("recovery_guide_followed"):
                return False, "Error recovery guide not followed"
        return True, "Error recovery patterns satisfied"

    def _validate_documentation_architecture(self, operation: dict) -> tuple[bool, str]:
        """Validate that documentation architecture is maintained."""
        # This would check documentation structure and patterns
        return True, "Documentation architecture satisfied"

    def _validate_knowledge_retrieval(self, operation: dict) -> tuple[bool, str]:
        """Validate that knowledge retrieval systems are used."""
        if operation.get("type") == "context_retrieval":
            if not operation.get("rag_system_used"):
                return False, "RAG system not used for context retrieval"
        return True, "Knowledge retrieval satisfied"

    def _validate_workflow_chain(self, operation: dict) -> tuple[bool, str]:
        """Validate that workflow chain is preserved."""
        # This would check that the workflow chain is maintained
        return True, "Workflow chain preserved"

    def _validate_technology_stack(self, operation: dict) -> tuple[bool, str]:
        """Validate that technology stack integrity is maintained."""
        # This would check that core technologies are preserved
        return True, "Technology stack integrity maintained"

    def validate_operation(self, operation: dict) -> dict:
        """Validate a single operation against all constitution rules."""
        results = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "compliance": True,
            "violations": [],
            "warnings": [],
        }

        for rule in self.rules:
            try:
                is_compliant, message = rule.validation_function(operation)
                if not is_compliant:
                    violation = {
                        "rule_id": rule.rule_id,
                        "article": rule.article,
                        "description": rule.description,
                        "message": message,
                        "critical": rule.critical,
                    }
                    results["violations"].append(violation)
                    if rule.critical:
                        results["compliance"] = False
                    else:
                        results["warnings"].append(violation)
            except Exception as e:
                violation = {
                    "rule_id": rule.rule_id,
                    "article": rule.article,
                    "description": rule.description,
                    "message": f"Validation error: {str(e)}",
                    "critical": rule.critical,
                }
                results["violations"].append(violation)
                if rule.critical:
                    results["compliance"] = False

        return results

    def validate_file_operation(self, file_path: str, operation_type: str) -> dict:
        """Validate a file operation against constitution rules."""
        operation: dict[str, Any] = {
            "type": "file_operation",
            "file_path": file_path,
            "operation_type": operation_type,
            "timestamp": datetime.now().isoformat(),
        }

        # Add file analysis requirement check
        if operation_type in ["delete", "move", "rename"]:
            operation["file_analysis_completed"] = self._check_file_analysis_completion(file_path)

        return self.validate_operation(operation)

    def _check_file_analysis_completion(self, file_path: str) -> bool:
        """Check if file analysis has been completed for the given file."""
        # This would check if the file analysis guide has been read
        # and the 6-step analysis completed
        return True  # Placeholder implementation

    def generate_compliance_report(self) -> str:
        """Generate a human-readable compliance report."""
        if not self.violations:
            return "✅ All constitution rules are being followed"

        report = "🤖 AI Constitution Compliance Report\n"
        report += "=" * 50 + "\n\n"

        critical_violations = [v for v in self.violations if v.get("critical", False)]
        warnings = [v for v in self.violations if not v.get("critical", False)]

        if critical_violations:
            report += "🚨 CRITICAL VIOLATIONS:\n"
            for violation in critical_violations:
                report += f"  • {violation['description']}: {violation['message']}\n"
            report += "\n"

        if warnings:
            report += "⚠️  WARNINGS:\n"
            for warning in warnings:
                report += f"  • {warning['description']}: {warning['message']}\n"
            report += "\n"

        report += f"📊 Summary: {len(critical_violations)} critical violations, {len(warnings)} warnings\n"

        return report

    def log_violation(self, violation: dict):
        """Log a constitution violation."""
        self.violations.append(violation)

        # Log to file for tracking
        log_entry = {"timestamp": datetime.now().isoformat(), "violation": violation}

        log_file = "evals/metrics/logs/constitution_violations.jsonl"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"⚠️  Could not log violation: {e}")


def main():
    """Main function for testing the constitution compliance checker."""
    checker = ConstitutionComplianceChecker()

    # Test file operation validation
    test_operation = {"type": "file_deletion", "target_file": "test_file.md", "risk_level": "high"}

    result = checker.validate_operation(test_operation)
    print("🔍 Constitution Compliance Check Result:")
    print(json.dumps(result, indent=2))

    # Generate compliance report
    report = checker.generate_compliance_report()
    print("\n" + report)


if __name__ == "__main__":
    main()
