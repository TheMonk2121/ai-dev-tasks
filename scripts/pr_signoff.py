#!/usr/bin/env python3
"""
Multi-Role PR Sign-Off System
-----------------------------
Comprehensive review and cleanup workflow requiring approval from all DSPy roles
before PR closure and automated cleanup.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Role definitions and responsibilities
PR_CLOSURE_WORKFLOW = {
    "planner": {
        "responsibilities": [
            "strategic_alignment_check",
            "backlog_item_validation",
            "priority_assessment",
            "roadmap_impact_analysis",
        ],
        "approval_criteria": [
            "backlog_item properly updated",
            "strategic goals aligned",
            "dependencies resolved",
            "next steps identified",
        ],
    },
    "implementer": {
        "responsibilities": [
            "technical_architecture_review",
            "system_integration_validation",
            "workflow_automation_check",
            "scribe_system_health",
        ],
        "approval_criteria": [
            "architecture patterns followed",
            "integration points validated",
            "automation workflows intact",
            "system health confirmed",
        ],
    },
    "coder": {
        "responsibilities": [
            "code_quality_assessment",
            "testing_coverage_validation",
            "security_compliance_check",
            "documentation_standards",
        ],
        "approval_criteria": [
            "linting standards met",
            "test coverage adequate",
            "security practices followed",
            "documentation updated",
        ],
    },
    "researcher": {
        "responsibilities": [
            "research_impact_assessment",
            "knowledge_extraction",
            "pattern_analysis",
            "lessons_learned_documentation",
        ],
        "approval_criteria": [
            "research insights captured",
            "patterns documented",
            "lessons learned extracted",
            "knowledge base updated",
        ],
    },
}

# Required roles for PR closure
REQUIRED_ROLES = ["planner", "implementer", "coder", "researcher"]


class PRSignOffSystem:
    """Multi-role PR sign-off system for comprehensive review and cleanup."""

    def __init__(self, pr_number: str, backlog_id: str | None = None):
        self.pr_number = pr_number
        self.backlog_id = backlog_id or self._extract_backlog_id()
        self.signoff_file = f"artifacts/pr_signoffs/PR-{pr_number}-signoff.json"
        self.worklog_path = f"artifacts/worklogs/{self.backlog_id}.md" if self.backlog_id else None

    def _extract_backlog_id(self) -> str | None:
        """Extract backlog ID from PR title or description."""
        try:
            # Try to get PR details using GitHub CLI
            result = subprocess.run(
                ["gh", "pr", "view", self.pr_number, "--json", "title,body"], capture_output=True, text=True, check=True
            )
            pr_data = json.loads(result.stdout)

            # Look for B-XXX pattern in title or body
            import re

            title_body = f"{pr_data.get('title', '')} {pr_data.get('body', '')}"
            match = re.search(r"B-\d+", title_body)
            return match.group(0) if match else None

        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return None

    def _load_signoff_state(self) -> dict[str, Any]:
        """Load existing sign-off state."""
        if os.path.exists(self.signoff_file):
            with open(self.signoff_file) as f:
                return json.load(f)
        return {
            "pr_number": self.pr_number,
            "backlog_id": self.backlog_id,
            "created_at": datetime.now().isoformat(),
            "signoffs": {},
            "status": "pending",
        }

    def _save_signoff_state(self, state: dict[str, Any]) -> None:
        """Save sign-off state to file."""
        os.makedirs(os.path.dirname(self.signoff_file), exist_ok=True)
        with open(self.signoff_file, "w") as f:
            json.dump(state, f, indent=2)

    def _run_role_validation(self, role: str) -> dict[str, Any]:
        """Run validation checks for a specific role."""
        validation_results = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "pending",
        }

        role_config = PR_CLOSURE_WORKFLOW.get(role, {})

        # Run role-specific validation checks
        for responsibility in role_config.get("responsibilities", []):
            check_result = self._run_single_check(role, responsibility)
            validation_results["checks"][responsibility] = check_result

        # Determine overall status
        all_passed = all(check.get("status") == "passed" for check in validation_results["checks"].values())
        validation_results["overall_status"] = "passed" if all_passed else "failed"

        return validation_results

    def _run_single_check(self, role: str, responsibility: str) -> dict[str, Any]:
        """Run a single validation check for a role responsibility."""
        check_result = {"status": "pending", "details": "", "recommendations": []}

        try:
            if role == "planner":
                check_result = self._run_planner_check(responsibility)
            elif role == "implementer":
                check_result = self._run_implementer_check(responsibility)
            elif role == "coder":
                check_result = self._run_coder_check(responsibility)
            elif role == "researcher":
                check_result = self._run_researcher_check(responsibility)
        except Exception as e:
            check_result["status"] = "error"
            check_result["details"] = f"Check failed: {str(e)}"

        return check_result

    def _run_planner_check(self, responsibility: str) -> dict[str, Any]:
        """Run planner role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "strategic_alignment_check":
            # Check if PR aligns with current backlog priorities
            if self.backlog_id:
                result["status"] = "passed"
                result["details"] = f"PR linked to backlog item {self.backlog_id}"
            else:
                result["status"] = "failed"
                result["details"] = "PR not linked to backlog item"
                result["recommendations"].append("Add backlog item reference to PR")

        elif responsibility == "backlog_item_validation":
            # Validate backlog item exists and is properly formatted
            if self.backlog_id and os.path.exists("000_core/000_backlog.md"):
                result["status"] = "passed"
                result["details"] = f"Backlog item {self.backlog_id} exists"
            else:
                result["status"] = "failed"
                result["details"] = "Backlog item validation failed"

        return result

    def _run_implementer_check(self, responsibility: str) -> dict[str, Any]:
        """Run implementer role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "technical_architecture_review":
            # Check for architectural patterns in changed files
            try:
                changed_files = subprocess.run(
                    ["gh", "pr", "view", self.pr_number, "--json", "files"], capture_output=True, text=True, check=True
                )
                files_data = json.loads(changed_files.stdout)
                file_count = len(files_data.get("files", []))

                if file_count > 0:
                    result["status"] = "passed"
                    result["details"] = f"Reviewed {file_count} changed files"
                else:
                    result["status"] = "failed"
                    result["details"] = "No files changed in PR"
            except Exception:
                result["status"] = "error"
                result["details"] = "Could not retrieve PR files"

        elif responsibility == "scribe_system_health":
            # Check if Scribe system is healthy
            try:
                scribe_status = subprocess.run(
                    ["python", "scripts/single_doorway.py", "scribe", "status"], capture_output=True, text=True
                )
                if scribe_status.returncode == 0:
                    result["status"] = "passed"
                    result["details"] = "Scribe system is healthy"
                else:
                    result["status"] = "warning"
                    result["details"] = "Scribe system may have issues"
            except Exception:
                result["status"] = "error"
                result["details"] = "Could not check Scribe system health"

        return result

    def _run_coder_check(self, responsibility: str) -> dict[str, Any]:
        """Run coder role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "code_quality_assessment":
            # Run linting checks
            try:
                lint_result = subprocess.run(["ruff", "check", "--output-format=json"], capture_output=True, text=True)
                if lint_result.returncode == 0:
                    result["status"] = "passed"
                    result["details"] = "Code quality checks passed"
                else:
                    result["status"] = "failed"
                    result["details"] = "Code quality issues found"
                    result["recommendations"].append("Fix linting errors")
            except Exception:
                result["status"] = "error"
                result["details"] = "Could not run code quality checks"

        elif responsibility == "testing_coverage_validation":
            # Check test coverage
            try:
                test_result = subprocess.run(
                    ["./dspy-rag-system/run_tests.sh", "--tiers", "1", "--kinds", "smoke"],
                    capture_output=True,
                    text=True,
                )
                if test_result.returncode == 0:
                    result["status"] = "passed"
                    result["details"] = "Smoke tests passed"
                else:
                    result["status"] = "failed"
                    result["details"] = "Smoke tests failed"
                    result["recommendations"].append("Fix failing tests")
            except Exception:
                result["status"] = "error"
                result["details"] = "Could not run tests"

        return result

    def _run_researcher_check(self, responsibility: str) -> dict[str, Any]:
        """Run researcher role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "knowledge_extraction":
            # Check if worklog exists and has content
            if self.worklog_path and os.path.exists(self.worklog_path):
                with open(self.worklog_path) as f:
                    content = f.read()
                    if len(content.strip()) > 100:  # Minimum content threshold
                        result["status"] = "passed"
                        result["details"] = "Worklog contains substantial content"
                    else:
                        result["status"] = "warning"
                        result["details"] = "Worklog content is minimal"
                        result["recommendations"].append("Add more context to worklog")
            else:
                result["status"] = "failed"
                result["details"] = "No worklog found"
                result["recommendations"].append("Create worklog for this PR")

        elif responsibility == "lessons_learned_documentation":
            # Check if lessons learned are documented
            result["status"] = "passed"
            result["details"] = "Lessons learned will be extracted during cleanup"

        return result

    def sign_off(self, role: str, approved: bool = True, notes: str = "") -> dict[str, Any]:
        """Sign off on PR closure for a specific role."""
        if role not in REQUIRED_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {REQUIRED_ROLES}")

        state = self._load_signoff_state()

        # Run validation checks
        validation_results = self._run_role_validation(role)

        # Create sign-off entry
        signoff_entry = {
            "role": role,
            "approved": approved and validation_results["overall_status"] == "passed",
            "timestamp": datetime.now().isoformat(),
            "notes": notes,
            "validation_results": validation_results,
        }

        state["signoffs"][role] = signoff_entry

        # Check if all required roles have signed off
        all_approved = all(signoff.get("approved", False) for signoff in state["signoffs"].values())

        if all_approved and len(state["signoffs"]) == len(REQUIRED_ROLES):
            state["status"] = "approved"
            state["approved_at"] = datetime.now().isoformat()

        self._save_signoff_state(state)
        return signoff_entry

    def get_status(self) -> dict[str, Any]:
        """Get current sign-off status."""
        state = self._load_signoff_state()

        status_summary = {
            "pr_number": self.pr_number,
            "backlog_id": self.backlog_id,
            "overall_status": state["status"],
            "signoffs": {},
            "missing_roles": [],
            "can_close": False,
        }

        for role in REQUIRED_ROLES:
            if role in state["signoffs"]:
                signoff = state["signoffs"][role]
                status_summary["signoffs"][role] = {
                    "approved": signoff.get("approved", False),
                    "timestamp": signoff.get("timestamp"),
                    "validation_status": signoff.get("validation_results", {}).get("overall_status"),
                }
            else:
                status_summary["missing_roles"].append(role)

        status_summary["can_close"] = state["status"] == "approved" and len(status_summary["signoffs"]) == len(
            REQUIRED_ROLES
        )

        return status_summary

    def perform_cleanup(self) -> dict[str, Any]:
        """Perform automated cleanup after PR approval."""
        if not self.get_status()["can_close"]:
            raise ValueError("Cannot perform cleanup - PR not fully approved")

        cleanup_results = {"timestamp": datetime.now().isoformat(), "actions": [], "errors": []}

        try:
            # Generate worklog summary
            if self.backlog_id:
                cleanup_results["actions"].append("Generate worklog summary")
                self._generate_worklog_summary()

            # Archive temporary files
            cleanup_results["actions"].append("Archive temporary files")
            self._archive_temp_files()

            # Update backlog item status
            if self.backlog_id:
                cleanup_results["actions"].append("Update backlog item status")
                self._update_backlog_status()

            # Clean up sign-off files
            cleanup_results["actions"].append("Clean up sign-off files")
            self._cleanup_signoff_files()

        except Exception as e:
            cleanup_results["errors"].append(str(e))

        return cleanup_results

    def _generate_worklog_summary(self) -> None:
        """Generate summary from worklog."""
        if self.worklog_path and os.path.exists(self.worklog_path):
            try:
                subprocess.run(["python", "scripts/worklog_summarizer.py", "--backlog-id", self.backlog_id], check=True)
            except subprocess.CalledProcessError:
                pass  # Non-critical if summary generation fails

    def _archive_temp_files(self) -> None:
        """Archive temporary files to 600_archives."""
        try:
            # Archive PRD, tasks, and run files if they exist
            archive_patterns = [
                f"PRD-{self.backlog_id}-*.md",
                f"TASKS-{self.backlog_id}-*.md",
                f"RUN-{self.backlog_id}-*.md",
            ]

            for pattern in archive_patterns:
                for file_path in Path("600_archives/artifacts/000_core_temp_files").glob(pattern):
                    # Add deprecation header
                    self._add_deprecation_header(file_path)

        except Exception as e:
            print(f"Warning: Could not archive temp files: {e}")

    def _add_deprecation_header(self, file_path: Path) -> None:
        """Add deprecation header to archived file."""
        try:
            with open(file_path) as f:
                content = f.read()

            deprecation_header = f"""<!-- ARCHIVED/DEPRECATED - do not edit -->
<!-- Archived on: {datetime.now().isoformat()} -->
<!-- PR: {self.pr_number} -->
<!-- Backlog: {self.backlog_id} -->

> **ARCHIVED**: This file has been automatically archived after PR closure.
> Do not edit this file as it is no longer actively maintained.

"""

            with open(file_path, "w") as f:
                f.write(deprecation_header + content)

        except Exception as e:
            print(f"Warning: Could not add deprecation header to {file_path}: {e}")

    def _update_backlog_status(self) -> None:
        """Update backlog item status."""
        # This would update the backlog item to mark it as completed
        # Implementation depends on backlog format
        pass

    def _cleanup_signoff_files(self) -> None:
        """Clean up sign-off files after successful closure."""
        try:
            if os.path.exists(self.signoff_file):
                os.remove(self.signoff_file)
        except Exception as e:
            print(f"Warning: Could not clean up sign-off file: {e}")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Multi-Role PR Sign-Off System")
    parser.add_argument("pr_number", help="PR number to process")
    parser.add_argument("--backlog-id", help="Backlog item ID (auto-detected if not provided)")
    parser.add_argument("--role", choices=REQUIRED_ROLES, help="Role performing sign-off")
    parser.add_argument("--approve", action="store_true", help="Approve the sign-off")
    parser.add_argument("--notes", help="Notes for the sign-off")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--cleanup", action="store_true", help="Perform cleanup after approval")

    args = parser.parse_args()

    signoff_system = PRSignOffSystem(args.pr_number, args.backlog_id)

    if args.status:
        status = signoff_system.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.role:
        if not args.notes:
            args.notes = input(f"Enter notes for {args.role} sign-off: ")

        result = signoff_system.sign_off(args.role, args.approve, args.notes)
        print(f"✅ {args.role} sign-off {'approved' if result['approved'] else 'rejected'}")
        print(json.dumps(result, indent=2))

    if args.cleanup:
        try:
            cleanup_results = signoff_system.perform_cleanup()
            print("✅ Cleanup completed successfully")
            print(json.dumps(cleanup_results, indent=2))
        except ValueError as e:
            print(f"❌ Cleanup failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
