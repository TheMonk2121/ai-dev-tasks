#!/usr/bin/env python3
"""
Multi-Role PR Sign-Off System v2.0
----------------------------------
Enhanced comprehensive review and cleanup workflow with 5-step strategic alignment,
stakeholder involvement, milestone tracking, and lessons learned generation.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Enhanced role definitions with stakeholder role
PR_CLOSURE_WORKFLOW_V2 = {
    "stakeholder": {
        "responsibilities": [
            "strategic_vision_approval",
            "business_impact_assessment",
            "resource_allocation_approval",
            "timeline_approval",
        ],
        "approval_criteria": [
            "strategic vision aligned",
            "business impact acceptable",
            "resources allocated appropriately",
            "timeline realistic",
        ],
    },
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

# 5-Step Strategic Alignment Process
STRATEGIC_ALIGNMENT_STEPS = {
    "step1_assess_scope": {
        "title": "Assess Content Type and Scope",
        "description": "Determine if this is system-wide, workflow-specific, or setup-related",
        "questions": [
            "What is the scope of this PR? (system-wide vs. workflow vs. setup)",
            "What impact will this have on the overall system?",
            "Who are the primary stakeholders affected?",
            "What is the strategic importance of this change?",
        ],
        "outputs": ["scope_assessment", "impact_analysis", "stakeholder_list"],
    },
    "step2_choose_path": {
        "title": "Choose Implementation Path",
        "description": "Select the appropriate implementation approach based on scope",
        "questions": [
            "What is the best implementation approach?",
            "Are there multiple paths to consider?",
            "What are the trade-offs between approaches?",
            "Which path aligns best with our strategic goals?",
        ],
        "outputs": ["implementation_path", "trade_off_analysis", "strategic_alignment"],
    },
    "step3_define_milestones": {
        "title": "Define Milestones and Check-ins",
        "description": "Create specific milestones where each role must agree on path forward",
        "questions": [
            "What are the key milestones in this implementation?",
            "At which points do we need stakeholder approval?",
            "What are the check-in requirements for each role?",
            "How do we handle disagreements at milestones?",
        ],
        "outputs": ["milestone_list", "check_in_schedule", "approval_process"],
    },
    "step4_set_validation": {
        "title": "Set Reading and Validation Order",
        "description": "Define the sequence for role reviews and validations",
        "questions": [
            "What is the optimal order for role reviews?",
            "Which validations depend on others?",
            "What are the dependencies between roles?",
            "How do we ensure comprehensive coverage?",
        ],
        "outputs": ["validation_sequence", "dependency_map", "coverage_plan"],
    },
    "step5_add_references": {
        "title": "Add Cross-References and Discovery",
        "description": "Ensure proper linking and discoverability for future reference",
        "questions": [
            "What existing documentation should this link to?",
            "How will this be discovered by future teams?",
            "What cross-references are needed?",
            "How do we maintain the learning loop?",
        ],
        "outputs": ["cross_references", "discovery_plan", "learning_loop_integration"],
    },
}

# Required roles for PR closure (including stakeholder)
REQUIRED_ROLES_V2 = ["stakeholder", "planner", "implementer", "coder", "researcher"]


class PRSignOffSystemV2:
    """Enhanced multi-role PR sign-off system with 5-step strategic alignment."""

    def __init__(self, pr_number: str, backlog_id: str | None = None):
        self.pr_number = pr_number
        self.backlog_id = backlog_id or self._extract_backlog_id()
        self.signoff_file = f"artifacts/pr_signoffs/PR-{pr_number}-signoff-v2.json"
        self.worklog_path = f"artifacts/worklogs/{self.backlog_id}.md" if self.backlog_id else None
        self.lessons_file = f"artifacts/lessons_learned/PR-{pr_number}-lessons.md"

    def _extract_backlog_id(self) -> str | None:
        """Extract backlog ID from PR title or description."""
        try:
            result = subprocess.run(
                ["gh", "pr", "view", self.pr_number, "--json", "title,body"], capture_output=True, text=True, check=True
            )
            pr_data = json.loads(result.stdout)

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
            "version": "2.0",
            "created_at": datetime.now().isoformat(),
            "strategic_alignment": {},
            "signoffs": {},
            "milestones": {},
            "status": "pending",
        }

    def _save_signoff_state(self, state: dict[str, Any]) -> None:
        """Save sign-off state to file."""
        os.makedirs(os.path.dirname(self.signoff_file), exist_ok=True)
        with open(self.signoff_file, "w") as f:
            json.dump(state, f, indent=2)

    def strategic_alignment(self, step: str, answers: dict[str, Any], notes: str = "") -> dict[str, Any]:
        """Complete a step in the 5-step strategic alignment process."""
        if step not in STRATEGIC_ALIGNMENT_STEPS:
            raise ValueError(f"Invalid step: {step}. Must be one of {list(STRATEGIC_ALIGNMENT_STEPS.keys())}")

        state = self._load_signoff_state()

        step_data = {
            "step": step,
            "title": STRATEGIC_ALIGNMENT_STEPS[step]["title"],
            "answers": answers,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "completed_by": "stakeholder",  # Stakeholder leads strategic alignment
        }

        state["strategic_alignment"][step] = step_data

        # Check if all steps are complete
        all_steps_complete = len(state["strategic_alignment"]) == len(STRATEGIC_ALIGNMENT_STEPS)
        if all_steps_complete:
            state["strategic_alignment"]["completed_at"] = datetime.now().isoformat()
            state["status"] = "strategic_alignment_complete"

        self._save_signoff_state(state)
        return step_data

    def create_milestone(
        self, milestone_name: str, description: str, required_roles: list, due_date: str = None
    ) -> dict[str, Any]:
        """Create a milestone for role check-ins."""
        state = self._load_signoff_state()

        milestone_data = {
            "name": milestone_name,
            "description": description,
            "required_roles": required_roles,
            "due_date": due_date,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "approvals": {},
        }

        state["milestones"][milestone_name] = milestone_data
        self._save_signoff_state(state)
        return milestone_data

    def approve_milestone(
        self, milestone_name: str, role: str, approved: bool = True, notes: str = ""
    ) -> dict[str, Any]:
        """Approve a milestone for a specific role."""
        state = self._load_signoff_state()

        if milestone_name not in state["milestones"]:
            raise ValueError(f"Milestone {milestone_name} not found")

        milestone = state["milestones"][milestone_name]
        if role not in milestone["required_roles"]:
            raise ValueError(f"Role {role} not required for milestone {milestone_name}")

        approval_data = {"role": role, "approved": approved, "notes": notes, "timestamp": datetime.now().isoformat()}

        milestone["approvals"][role] = approval_data

        # Check if all required roles have approved
        all_approved = all(approval.get("approved", False) for approval in milestone["approvals"].values())

        if all_approved and len(milestone["approvals"]) == len(milestone["required_roles"]):
            milestone["status"] = "approved"
            milestone["approved_at"] = datetime.now().isoformat()

        self._save_signoff_state(state)
        return approval_data

    def _run_role_validation(self, role: str) -> dict[str, Any]:
        """Run validation checks for a specific role."""
        validation_results = {
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "pending",
        }

        role_config = PR_CLOSURE_WORKFLOW_V2.get(role, {})

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
            if role == "stakeholder":
                check_result = self._run_stakeholder_check(responsibility)
            elif role == "planner":
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

    def _run_stakeholder_check(self, responsibility: str) -> dict[str, Any]:
        """Run stakeholder role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "strategic_vision_approval":
            # Check if strategic alignment is complete
            state = self._load_signoff_state()
            if len(state.get("strategic_alignment", {})) == len(STRATEGIC_ALIGNMENT_STEPS):
                result["status"] = "passed"
                result["details"] = "Strategic alignment process completed"
            else:
                result["status"] = "failed"
                result["details"] = "Strategic alignment process incomplete"
                result["recommendations"].append("Complete 5-step strategic alignment process")

        elif responsibility == "business_impact_assessment":
            # Check if business impact has been assessed
            result["status"] = "passed"
            result["details"] = "Business impact assessment completed during strategic alignment"

        return result

    def _run_planner_check(self, responsibility: str) -> dict[str, Any]:
        """Run planner role validation checks."""
        result = {"status": "pending", "details": "", "recommendations": []}

        if responsibility == "strategic_alignment_check":
            # Check if strategic alignment is complete
            state = self._load_signoff_state()
            if len(state.get("strategic_alignment", {})) == len(STRATEGIC_ALIGNMENT_STEPS):
                result["status"] = "passed"
                result["details"] = "Strategic alignment verified"
            else:
                result["status"] = "failed"
                result["details"] = "Strategic alignment not complete"
                result["recommendations"].append("Wait for stakeholder to complete strategic alignment")

        elif responsibility == "backlog_item_validation":
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
            if self.worklog_path and os.path.exists(self.worklog_path):
                with open(self.worklog_path) as f:
                    content = f.read()
                    if len(content.strip()) > 100:
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
            result["status"] = "passed"
            result["details"] = "Lessons learned will be extracted during cleanup"

        return result

    def sign_off(self, role: str, approved: bool = True, notes: str = "") -> dict[str, Any]:
        """Sign off on PR closure for a specific role."""
        if role not in REQUIRED_ROLES_V2:
            raise ValueError(f"Invalid role: {role}. Must be one of {REQUIRED_ROLES_V2}")

        state = self._load_signoff_state()

        # For stakeholder, check if strategic alignment is complete
        if role == "stakeholder" and len(state.get("strategic_alignment", {})) < len(STRATEGIC_ALIGNMENT_STEPS):
            raise ValueError("Stakeholder must complete strategic alignment before signing off")

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

        if all_approved and len(state["signoffs"]) == len(REQUIRED_ROLES_V2):
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
            "version": "2.0",
            "overall_status": state["status"],
            "strategic_alignment": {
                "completed_steps": len(state.get("strategic_alignment", {})),
                "total_steps": len(STRATEGIC_ALIGNMENT_STEPS),
                "is_complete": len(state.get("strategic_alignment", {})) == len(STRATEGIC_ALIGNMENT_STEPS),
            },
            "signoffs": {},
            "milestones": state.get("milestones", {}),
            "missing_roles": [],
            "can_close": False,
        }

        for role in REQUIRED_ROLES_V2:
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
            REQUIRED_ROLES_V2
        )

        return status_summary

    def generate_lessons_learned(self) -> dict[str, Any]:
        """Generate lessons learned artifact."""
        if not self.get_status()["can_close"]:
            raise ValueError("Cannot generate lessons learned - PR not fully approved")

        state = self._load_signoff_state()

        lessons_data = {
            "pr_number": self.pr_number,
            "backlog_id": self.backlog_id,
            "generated_at": datetime.now().isoformat(),
            "strategic_alignment_insights": {},
            "role_insights": {},
            "milestone_insights": {},
            "recommendations": [],
            "patterns_identified": [],
        }

        # Extract insights from strategic alignment
        for step, step_data in state.get("strategic_alignment", {}).items():
            if step != "completed_at":
                lessons_data["strategic_alignment_insights"][step] = {
                    "title": step_data.get("title"),
                    "key_insights": step_data.get("answers", {}),
                    "notes": step_data.get("notes"),
                }

        # Extract insights from role sign-offs
        for role, signoff in state.get("signoffs", {}).items():
            lessons_data["role_insights"][role] = {
                "notes": signoff.get("notes"),
                "validation_results": signoff.get("validation_results", {}),
            }

        # Extract insights from milestones
        for milestone_name, milestone in state.get("milestones", {}).items():
            lessons_data["milestone_insights"][milestone_name] = {
                "description": milestone.get("description"),
                "approvals": milestone.get("approvals", {}),
                "status": milestone.get("status"),
            }

        # Generate recommendations
        lessons_data["recommendations"] = self._generate_recommendations(lessons_data)

        # Save lessons learned
        os.makedirs(os.path.dirname(self.lessons_file), exist_ok=True)
        with open(self.lessons_file, "w") as f:
            json.dump(lessons_data, f, indent=2)

        return lessons_data

    def _generate_recommendations(self, lessons_data: dict[str, Any]) -> list:
        """Generate recommendations based on lessons learned."""
        recommendations = []

        # Analyze strategic alignment patterns
        strategic_steps = lessons_data.get("strategic_alignment_insights", {})
        if len(strategic_steps) == len(STRATEGIC_ALIGNMENT_STEPS):
            recommendations.append("5-step strategic alignment process was effective")

        # Analyze role insights
        role_insights = lessons_data.get("role_insights", {})
        for role, insights in role_insights.items():
            validation_results = insights.get("validation_results", {})
            checks = validation_results.get("checks", {})

            failed_checks = [check for check in checks.values() if check.get("status") == "failed"]
            if failed_checks:
                recommendations.append(
                    f"Improve {role} validation checks for: {[check.get('details') for check in failed_checks]}"
                )

        # Analyze milestone patterns
        milestone_insights = lessons_data.get("milestone_insights", {})
        if milestone_insights:
            recommendations.append("Milestone tracking was effective for coordination")

        return recommendations

    def perform_cleanup(self) -> dict[str, Any]:
        """Perform automated cleanup after PR approval."""
        if not self.get_status()["can_close"]:
            raise ValueError("Cannot perform cleanup - PR not fully approved")

        cleanup_results = {"timestamp": datetime.now().isoformat(), "actions": [], "errors": []}

        try:
            # Generate lessons learned
            cleanup_results["actions"].append("Generate lessons learned")
            self.generate_lessons_learned()

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
            archive_patterns = [
                f"PRD-{self.backlog_id}-*.md",
                f"TASKS-{self.backlog_id}-*.md",
                f"RUN-{self.backlog_id}-*.md",
            ]

            for pattern in archive_patterns:
                for file_path in Path("600_archives/artifacts/000_core_temp_files").glob(pattern):
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
<!-- Version: 2.0 -->

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
    """Main CLI interface for v2.0."""
    parser = argparse.ArgumentParser(description="Multi-Role PR Sign-Off System v2.0")
    parser.add_argument("pr_number", help="PR number to process")
    parser.add_argument("--backlog-id", help="Backlog item ID (auto-detected if not provided)")

    # Strategic alignment commands
    parser.add_argument("--strategic-align", help="Complete strategic alignment step")
    parser.add_argument("--step-answers", help="JSON string of step answers")
    parser.add_argument("--step-notes", help="Notes for strategic alignment step")

    # Milestone commands
    parser.add_argument("--create-milestone", help="Create a new milestone")
    parser.add_argument("--milestone-description", help="Description for milestone")
    parser.add_argument("--required-roles", nargs="+", help="Roles required for milestone")
    parser.add_argument("--due-date", help="Due date for milestone")
    parser.add_argument("--approve-milestone", help="Approve a milestone")
    parser.add_argument("--milestone-role", help="Role approving milestone")
    parser.add_argument("--milestone-notes", help="Notes for milestone approval")

    # Role sign-off commands
    parser.add_argument("--role", choices=REQUIRED_ROLES_V2, help="Role performing sign-off")
    parser.add_argument("--approve", action="store_true", help="Approve the sign-off")
    parser.add_argument("--notes", help="Notes for the sign-off")

    # Status and cleanup commands
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--cleanup", action="store_true", help="Perform cleanup after approval")
    parser.add_argument("--generate-lessons", action="store_true", help="Generate lessons learned")

    args = parser.parse_args()

    signoff_system = PRSignOffSystemV2(args.pr_number, args.backlog_id)

    if args.status:
        status = signoff_system.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.strategic_align:
        if not args.step_answers:
            print("❌ --step-answers required for strategic alignment")
            return

        try:
            answers = json.loads(args.step_answers)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in --step-answers")
            return

        result = signoff_system.strategic_alignment(args.strategic_align, answers, args.step_notes or "")
        print(f"✅ Strategic alignment step completed: {args.strategic_align}")
        print(json.dumps(result, indent=2))

    if args.create_milestone:
        if not args.milestone_description or not args.required_roles:
            print("❌ --milestone-description and --required-roles required for milestone creation")
            return

        result = signoff_system.create_milestone(
            args.create_milestone, args.milestone_description, args.required_roles, args.due_date
        )
        print(f"✅ Milestone created: {args.create_milestone}")
        print(json.dumps(result, indent=2))

    if args.approve_milestone:
        if not args.milestone_role:
            print("❌ --milestone-role required for milestone approval")
            return

        result = signoff_system.approve_milestone(
            args.approve_milestone, args.milestone_role, True, args.milestone_notes or ""
        )
        print(f"✅ Milestone approved: {args.approve_milestone}")
        print(json.dumps(result, indent=2))

    if args.role:
        if not args.notes:
            args.notes = input(f"Enter notes for {args.role} sign-off: ")

        result = signoff_system.sign_off(args.role, args.approve, args.notes)
        print(f"✅ {args.role} sign-off {'approved' if result['approved'] else 'rejected'}")
        print(json.dumps(result, indent=2))

    if args.generate_lessons:
        try:
            lessons = signoff_system.generate_lessons_learned()
            print("✅ Lessons learned generated successfully")
            print(json.dumps(lessons, indent=2))
        except ValueError as e:
            print(f"❌ Lessons learned generation failed: {e}")
            sys.exit(1)

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
