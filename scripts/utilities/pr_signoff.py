from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Literal, Optional

#!/usr/bin/env python3
"""
Multi-Role PR Sign-Off System v2.0
----------------------------------
Enhanced comprehensive review and cleanup workflow with 5-step strategic alignment,
stakeholder involvement, milestone tracking, and lessons learned generation.
"""

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


class RoleStatus(Enum):
    PENDING = auto()
    PASSED = auto()
    FAILED = auto()
    ERROR = auto()


@dataclass
class RoleValidationCheck:
    status: RoleStatus = RoleStatus.PENDING
    details: str = ""
    recommendations: list[str] = field(default_factory=list)


@dataclass
class RoleValidationResults:
    role: Literal["planner", "implementer", "coder", "researcher"]
    timestamp: datetime
    checks: dict[str, RoleValidationCheck]
    overall_status: RoleStatus = RoleStatus.PASSED


@dataclass
class SignOffEntry:
    role: Literal["planner", "implementer", "coder", "researcher"]
    approved: bool
    timestamp: datetime
    notes: str
    validation_results: RoleValidationResults


class PRSignOffSystemV2:
    """Enhanced, type-safe multi-role PR sign-off system."""

    REQUIRED_ROLES: list[Literal["planner", "implementer", "coder", "researcher"]] = [
        "planner",
        "implementer",
        "coder",
        "researcher",
    ]

    def __init__(self, pr_number: str, backlog_id: str | None = None):
        """
        Initialize PR sign-off system.

        Args:
            pr_number: GitHub PR number
            backlog_id: Optional backlog item ID
        """
        self.pr_number: str = pr_number
        self.backlog_id: str | None = backlog_id or self._extract_backlog_id()
        self.signoff_file: Path = Path(f"artifacts/pr_signoffs/PR-{pr_number}-signoff.json")
        self.worklog_path: Path | None = Path(f"artifacts/worklogs/{self.backlog_id}.md") if self.backlog_id else None

    def _extract_backlog_id(self) -> str | None:
        """
        Extract backlog ID from PR title or description.

        Returns:
            Extracted backlog ID or None if not found
        """
        try:
            result = subprocess.run(
                ["gh", "pr", "view", self.pr_number, "--json", "title,body"], capture_output=True, text=True, check=True
            )
            pr_data = json.loads(result.stdout)
            title_body = f"{pr_data.get('title', '')} {pr_data.get('body', '')}"

            match = re.search(r"B-\d+", title_body)
            return match.group(0) if match else None

        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return None

    def _load_signoff_state(self) -> dict[str, Any]:
        """
        Load existing sign-off state.

        Returns:
            Dictionary containing sign-off state
        """
        if self.signoff_file.exists():
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
        """
        Save sign-off state to file.

        Args:
            state: Sign-off state dictionary
        """
        self.signoff_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.signoff_file, "w") as f:
            json.dump(state, f, indent=2)

    def _run_role_validation(
        self, role: Literal["planner", "implementer", "coder", "researcher"]
    ) -> RoleValidationResults:
        """
        Run validation checks for a specific role.

        Args:
            role: Role to validate

        Returns:
            Validation results for the role
        """
        # Placeholder implementation - to be expanded with actual validation logic
        validation_results = RoleValidationResults(
            role=role,
            timestamp=datetime.now(),
            checks={},
            overall_status=RoleStatus.PASSED,  # Default to passed for now
        )

        return validation_results

    def sign_off(
        self, role: Literal["planner", "implementer", "coder", "researcher"], approved: bool = True, notes: str = ""
    ) -> SignOffEntry:
        """
        Sign off on PR closure for a specific role.

        Args:
            role: Role performing sign-off
            approved: Whether the role approves the PR
            notes: Additional notes for the sign-off

        Returns:
            Sign-off entry details
        """
        if role not in self.REQUIRED_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {self.REQUIRED_ROLES}")

        state = self._load_signoff_state()

        # Run validation checks
        validation_results = self._run_role_validation(role)

        # Create sign-off entry
        signoff_entry = SignOffEntry(
            role=role,
            approved=approved and validation_results.overall_status == RoleStatus.PASSED,
            timestamp=datetime.now(),
            notes=notes,
            validation_results=validation_results,
        )

        # Update state
        state["signoffs"][role] = {
            "approved": signoff_entry.approved,
            "timestamp": signoff_entry.timestamp.isoformat(),
            "notes": signoff_entry.notes,
            "validation_results": {
                "overall_status": signoff_entry.validation_results.overall_status.name,
                "checks": {k: v.__dict__ for k, v in signoff_entry.validation_results.checks.items()},
            },
        }

        # Check if all required roles have signed off
        all_approved = all(state["signoffs"].get(r, {}).get("approved", False) for r in self.REQUIRED_ROLES)

        if all_approved and len(state["signoffs"]) == len(self.REQUIRED_ROLES):
            state["status"] = "approved"
            state["approved_at"] = datetime.now().isoformat()

        self._save_signoff_state(state)
        return signoff_entry

    def get_status(self) -> dict[str, Any]:
        """
        Get current sign-off status.

        Returns:
            Dictionary containing current sign-off status
        """
        state = self._load_signoff_state()

        status_summary = {
            "pr_number": self.pr_number,
            "backlog_id": self.backlog_id,
            "overall_status": state["status"],
            "signoffs": {},
            "missing_roles": [],
            "can_close": False,
        }

        for role in self.REQUIRED_ROLES:
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
            self.REQUIRED_ROLES
        )

        return status_summary


def main():
    """Main CLI interface for PR sign-off system."""
    parser = argparse.ArgumentParser(description="Multi-Role PR Sign-Off System (v2)")
    parser.add_argument("pr_number", help="PR number to process")
    parser.add_argument("--backlog-id", help="Backlog item ID (auto-detected if not provided)")
    parser.add_argument("--role", choices=PRSignOffSystemV2.REQUIRED_ROLES, help="Role performing sign-off")
    parser.add_argument("--approve", action="store_true", help="Approve the sign-off")
    parser.add_argument("--notes", help="Notes for the sign-off")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    signoff_system = PRSignOffSystemV2(args.pr_number, args.backlog_id)

    if args.status:
        status = signoff_system.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.role:
        if not args.notes:
            args.notes = input(f"Enter notes for {args.role} sign-off: ")

        result = signoff_system.sign_off(args.role, args.approve, args.notes)
        print(f"✅ {args.role} sign-off {'approved' if result.approved else 'rejected'}")
        print(
            json.dumps(
                {
                    "role": result.role,
                    "approved": result.approved,
                    "timestamp": result.timestamp.isoformat(),
                    "notes": result.notes,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
