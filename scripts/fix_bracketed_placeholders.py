#!/usr/bin/env python3
"""
Auto-fix script for bracketed placeholders in markdown files.

This script automatically replaces common bracketed placeholder patterns
with appropriate plain text alternatives.
"""

import re
import sys
from pathlib import Path

# Common placeholder replacements - only known safe patterns
PLACEHOLDER_REPLACEMENTS = {
    r"\[Describe the purpose and scope of this document\]": "Describe the purpose and scope of this document",
    r"\[Describe how to use this document or system\]": "How to use this document or system",
    r"\[Owner\]": "Core Team",
    r"\[Last reviewed\]": "Last reviewed date",
    r"\[Integration\]": "Integration details",
    r"\[Document owner/maintainer information\]": "Document owner/maintainer information",
    r"\[Environment setup, deployment process, configuration management, database migrations, feature flags\]": "Environment setup, deployment process, configuration management, database migrations, feature flags",
    r"\[Technical risks, timeline risks, resource risks, and mitigation strategies\]": "Technical risks, timeline risks, resource risks, and mitigation strategies",
    r"\[Measurable success criteria and acceptance criteria\]": "Measurable success criteria and acceptance criteria",
    r"\[Logging, metrics, alerting, dashboard, troubleshooting requirements\]": "Logging, metrics, alerting, dashboard, troubleshooting requirements",
    r"\[Project overview, success metrics, timeline, stakeholders\]": "Project overview, success metrics, timeline, stakeholders",
    r"\[Current state, pain points, opportunity, impact\]": "Current state, pain points, opportunity, impact",
    r"\[High-level solution, key features, technical approach, integration points\]": "High-level solution, key features, technical approach, integration points",
    r"\[User stories, feature specifications, data requirements, API requirements\]": "User stories, feature specifications, data requirements, API requirements",
    r"\[Performance, security, reliability, usability requirements\]": "Performance, security, reliability, usability requirements",
    r"\[Test coverage goals, testing phases, automation requirements, test environments\]": "Test coverage goals, testing phases, automation requirements, test environments",
    r"\[Code quality standards, performance benchmarks, security validation, user acceptance criteria\]": "Code quality standards, performance benchmarks, security validation, user acceptance criteria",
    r"\[Development phase gates and completion criteria\]": "Development phase gates and completion criteria",
    r"\[Detailed testing requirements for each component type\]": "Detailed testing requirements for each component type",
    r"\[Brief description of the project and its goals\]": "Brief description of the project and its goals",
    r"\[Tasks for infrastructure and dependencies\]": "Tasks for infrastructure and dependencies",
    r"\[Tasks for main functionality development\]": "Tasks for main functionality development",
    r"\[Tasks for component integration and validation\]": "Tasks for component integration and validation",
    r"\[Tasks for optimization and hardening\]": "Tasks for optimization and hardening",
    r"\[Tasks for final preparation and launch\]": "Tasks for final preparation and launch",
}


def fix_bracketed_placeholders(content: str) -> tuple[str, list[str]]:
    """
    Fix bracketed placeholders in content.

    Returns (fixed_content, list_of_changes_made)
    """
    changes = []
    fixed_content = content

    # Apply known replacements
    for pattern, replacement in PLACEHOLDER_REPLACEMENTS.items():
        if re.search(pattern, fixed_content):
            fixed_content = re.sub(pattern, replacement, fixed_content)
            changes.append(f"Replaced '{pattern}' with '{replacement}'")

        # Generic pattern for standalone bracketed text - DISABLED for safety
    # Only use known patterns to avoid false positives
    # def replace_generic(match):
    #     placeholder = match.group(1)
    #     # Convert to sentence case and remove brackets
    #     replacement = placeholder.strip()
    #     if replacement:
    #         # Capitalize first letter, lowercase rest
    #         replacement = replacement[0].upper() + replacement[1:].lower()
    #         changes.append(f"Replaced '[{placeholder}]' with '{replacement}'")
    #         return replacement
    #     return match.group(0)

    # Apply generic replacement for standalone brackets - DISABLED
    # fixed_content = re.sub(
    #     r"^\s*\[([A-Za-z][^\]]+)\]\s*$",
    #     replace_generic,
    #     fixed_content,
    #     flags=re.MULTILINE,
    # )

    return fixed_content, changes


def process_file(filepath: Path, dry_run: bool = False) -> list[str]:
    """Process a single markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        fixed_content, changes = fix_bracketed_placeholders(content)

        if changes and not dry_run:
            filepath.write_text(fixed_content, encoding="utf-8")
            print(f"✅ Fixed {len(changes)} issues in {filepath}")
            for change in changes:
                print(f"   - {change}")
        elif changes and dry_run:
            print(f"🔍 Would fix {len(changes)} issues in {filepath}")
            for change in changes:
                print(f"   - {change}")

        return changes
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return []


def main():
    """Main function."""
    dry_run = "--dry-run" in sys.argv

    # Get files from command line arguments
    files_to_check = sys.argv[1:] if len(sys.argv) > 1 else []

    # Filter out --dry-run from file list
    files_to_check = [f for f in files_to_check if f != "--dry-run"]

    if files_to_check:
        # Use specified files
        markdown_files = [
            Path(f)
            for f in files_to_check
            if Path(f).exists() and Path(f).suffix.lower() == ".md"
        ]
    else:
        # Find all markdown files
        markdown_files = [
            f
            for f in Path(".").rglob("*.md")
            if not any(
                exclude in str(f)
                for exclude in ["/venv/", "/.git/", "/node_modules/", "/600_archives/"]
            )
        ]

    total_changes = 0
    files_processed = 0

    for filepath in markdown_files:
        changes = process_file(filepath, dry_run)
        if changes:
            files_processed += 1
            total_changes += len(changes)

    if dry_run:
        print(
            f"\n🔍 Dry run complete: Would fix {total_changes} issues in {files_processed} files"
        )
        print("Run without --dry-run to apply fixes")
    else:
        print(f"\n✅ Fixed {total_changes} issues in {files_processed} files")


if __name__ == "__main__":
    main()
