from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

#!/usr/bin/env python3
"""
Role Assignment Metadata System
-------------------------------
Metadata standards and parsing functions for automated role assignment in 600_archives.

This module defines the metadata format for specifying role access in archived files
and provides functions to parse and validate role assignments.
"""

# Valid roles in the system
VALID_ROLES = {"planner", "implementer", "researcher", "coder", "documentation"}

# Default role assignments for different file types
DEFAULT_ROLE_ASSIGNMENTS = {
    # PRDs and Task Lists
    "prd": {"planner", "implementer"},
    "task_list": {"planner", "implementer"},
    # Documentation
    "guide": {"documentation", "implementer"},
    "research": {"researcher", "documentation"},
    "memory": {"planner", "implementer", "documentation"},
    # Code and Scripts
    "script": {"coder", "implementer"},
    "test": {"coder", "implementer"},
    "config": {"coder", "implementer"},
    # Legacy and Archives
    "legacy": {"researcher", "documentation"},
    "archive": {"researcher", "documentation"},
    # Artifacts
    "artifact": {"planner", "implementer", "documentation"},
    "summary": {"planner", "implementer", "documentation"},
    "worklog": {"implementer", "documentation"},
}

# File extension to type mapping
FILE_EXTENSION_TYPES = {
    ".md": "documentation",
    ".py": "script",
    ".sh": "script",
    ".sql": "config",
    ".json": "config",
    ".yaml": "config",
    ".yml": "config",
    ".txt": "documentation",
    ".log": "artifact",
}

@dataclass
class RoleAssignment:
    """Represents a role assignment for a file."""

    roles: set[str]
    source: str  # "metadata", "content_analysis", "default", "manual"
    confidence: float  # 0.0 to 1.0
    metadata: dict | None = None

class RoleAssignmentMetadata:
    """Handles metadata parsing and role assignment for archived files."""

    # Metadata pattern for role access specification
    # Format: <!-- ROLE_ACCESS: ["role1", "role2"] -->
    ROLE_ACCESS_PATTERN = re.compile(r"<!--\s*ROLE_ACCESS:\s*\[([^\]]+)\]\s*-->", re.IGNORECASE)

    # Alternative format: <!-- ROLES: role1, role2 -->
    ROLES_PATTERN = re.compile(r"<!--\s*ROLES:\s*([^-->]+)\s*-->", re.IGNORECASE)

    def __init__(self):
        self.validation_errors: list[str] = []

    def parse_role_access_metadata(self, content: str) -> set[str] | None:
        """
        Parse role access metadata from file content.

        Args:
            content: File content as string

        Returns:
            Set of role names if found, None otherwise
        """
        # Try ROLE_ACCESS format first
        match = self.ROLE_ACCESS_PATTERN.search(content)
        if match:
            roles_str = match.group(1)
            return self._parse_roles_list(roles_str)

        # Try ROLES format
        match = self.ROLES_PATTERN.search(content)
        if match:
            roles_str = match.group(1)
            return self._parse_roles_list(roles_str)

        return None

    def _parse_roles_list(self, roles_str: str) -> set[str]:
        """
        Parse a comma-separated list of roles.

        Args:
            roles_str: Comma-separated role names

        Returns:
            Set of valid role names
        """
        # Clean and split the roles string
        roles = []
        for role in roles_str.split(","):
            role = role.strip().strip("\"'")
            if role:
                roles.append(role.lower())

        # Validate roles
        valid_roles = set()
        for role in roles:
            if role in VALID_ROLES:
                valid_roles.add(role)
            else:
                self.validation_errors.append(f"Invalid role: {role}")

        return valid_roles

    def get_default_roles_for_file(self, file_path: Path) -> set[str]:
        """
        Get default role assignments based on file path and type.

        Args:
            file_path: Path to the file

        Returns:
            Set of default role names
        """
        # Check file extension first
        ext = file_path.suffix.lower()
        if ext in FILE_EXTENSION_TYPES:
            file_type = FILE_EXTENSION_TYPES[ext]
            if file_type in DEFAULT_ROLE_ASSIGNMENTS:
                return DEFAULT_ROLE_ASSIGNMENTS[file_type].copy()

        # Check path components for type indicators
        path_parts = [part.lower() for part in file_path.parts]

        # Check for specific directories
        if "prds" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["prd"].copy()
        elif "task_lists" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["task_list"].copy()
        elif "legacy" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["legacy"].copy()
        elif "artifacts" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["artifact"].copy()
        elif "research" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["research"].copy()
        elif "guides" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["guide"].copy()
        elif "memory" in path_parts:
            return DEFAULT_ROLE_ASSIGNMENTS["memory"].copy()

        # Default fallback
        return {"planner", "implementer"}

    def analyze_content_for_roles(self, content: str, file_path: Path) -> set[str]:
        """
        Analyze file content to suggest appropriate roles.

        Args:
            content: File content as string
            file_path: Path to the file

        Returns:
            Set of suggested role names
        """
        content_lower = content.lower()
        suggested_roles = set()

        # Keyword-based role matching
        role_keywords = {
            "planner": [
                "backlog",
                "priority",
                "roadmap",
                "strategy",
                "planning",
                "requirements",
                "prd",
                "product",
                "business",
                "stakeholder",
            ],
            "implementer": [
                "implementation",
                "architecture",
                "system",
                "integration",
                "workflow",
                "automation",
                "dspy",
                "framework",
                "technical",
            ],
            "researcher": [
                "research",
                "analysis",
                "study",
                "investigation",
                "findings",
                "benchmark",
                "comparison",
                "evaluation",
                "experiment",
            ],
            "coder": [
                "code",
                "script",
                "function",
                "class",
                "test",
                "unit",
                "integration",
                "debug",
                "refactor",
                "optimize",
                "python",
            ],
            "documentation": [
                "documentation",
                "guide",
                "manual",
                "tutorial",
                "reference",
                "api",
                "specification",
                "standard",
                "format",
                "template",
            ],
        }

        # Count keyword matches for each role
        role_scores = {}
        for role, keywords in role_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                role_scores[role] = score

        # Add roles with significant keyword presence
        max_score = max(role_scores.values()) if role_scores else 0
        threshold = max(1, max_score // 2)  # At least half of max score

        for role, score in role_scores.items():
            if score >= threshold:
                suggested_roles.add(role)

        return suggested_roles

    def assign_roles_to_file(self, file_path: Path, content: str) -> RoleAssignment:
        """
        Assign roles to a file using metadata, content analysis, and defaults.

        Args:
            file_path: Path to the file
            content: File content as string

        Returns:
            RoleAssignment with assigned roles and metadata
        """
        self.validation_errors.clear()

        # 1. Check for explicit metadata first
        metadata_roles = self.parse_role_access_metadata(content)
        if metadata_roles:
            return RoleAssignment(
                roles=metadata_roles,
                source="metadata",
                confidence=1.0,
                metadata={"validation_errors": self.validation_errors.copy()},
            )

        # 2. Analyze content for role suggestions
        content_roles = self.analyze_content_for_roles(content, file_path)

        # 3. Get default roles
        default_roles = self.get_default_roles_for_file(file_path)

        # 4. Combine content analysis with defaults
        if content_roles:
            # Use content analysis as primary, supplement with defaults
            final_roles = content_roles.union(default_roles)
            confidence = min(0.8, len(content_roles) / len(VALID_ROLES))
            source = "content_analysis"
        else:
            # Use defaults only
            final_roles = default_roles
            confidence = 0.6
            source = "default"

        return RoleAssignment(
            roles=final_roles,
            source=source,
            confidence=confidence,
            metadata={"validation_errors": self.validation_errors.copy()},
        )

    def generate_metadata_template(self, roles: set[str]) -> str:
        """
        Generate metadata template for role access specification.

        Args:
            roles: Set of role names

        Returns:
            Metadata template string
        """
        roles_list = sorted(list(roles))
        return f"<!-- ROLE_ACCESS: {roles_list} -->"

    def validate_role_assignment(self, assignment: RoleAssignment) -> bool:
        """
        Validate a role assignment.

        Args:
            assignment: RoleAssignment to validate

        Returns:
            True if valid, False otherwise
        """
        # Check if all roles are valid
        invalid_roles = assignment.roles - VALID_ROLES
        if invalid_roles:
            self.validation_errors.append(f"Invalid roles: {invalid_roles}")
            return False

        # Check confidence range
        if not 0.0 <= assignment.confidence <= 1.0:
            self.validation_errors.append(f"Invalid confidence: {assignment.confidence}")
            return False

        # Check if at least one role is assigned
        if not assignment.roles:
            self.validation_errors.append("No roles assigned")
            return False

        return True

def main():
    """Test the role assignment metadata system."""
    metadata_system = RoleAssignmentMetadata()

    # Test metadata parsing
    test_content = """
    # Test File

    <!-- ROLE_ACCESS: ["planner", "implementer"] -->

    This is a test file for role assignment.
    """

    assignment = metadata_system.assign_roles_to_file(Path("test.md"), test_content)

    print(f"Assigned roles: {assignment.roles}")
    print(f"Source: {assignment.source}")
    print(f"Confidence: {assignment.confidence}")
    print(f"Valid: {metadata_system.validate_role_assignment(assignment)}")

    if metadata_system.validation_errors:
        print(f"Validation errors: {metadata_system.validation_errors}")

if __name__ == "__main__":
    main()
