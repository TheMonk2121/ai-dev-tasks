#!/usr/bin/env python3.12.123.11
"""
Bracketed Placeholder Checker

This script detects bracketed placeholders in markdown files that can break rendering.
It's designed to be used as a pre-commit hook to prevent these issues from being committed.
"""

import re
import sys
from pathlib import Path


def find_bracketed_placeholders(
    content: str, filename: str
) -> list[tuple[int, str, str]]:
    """
    Find bracketed placeholders in markdown content.

    Returns list of (line_number, line_content, placeholder_text) tuples.
    """
    issues = []
    lines = content.splitlines()

    # Patterns that indicate bracketed placeholders
    patterns = [
        # Standalone bracketed text: [Describe something...]
        r"^\s*\[[A-Za-z][^\]]+\]\s*$",
        # List items with brackets: - [Describe something...]
        r"^\s*[-*+]\s*\[[A-Za-z][^\]]+\]\s*$",
        # Numbered list items: 1. [Describe something...]
        r"^\s*\d+\.\s*\[[A-Za-z][^\]]+\]\s*$",
    ]

    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                # Extract the bracketed content
                match = re.search(r"\[([^\]]+)\]", line)
                if match:
                    placeholder = match.group(1)
                    # Skip legitimate markdown links and references
                    if not (
                        placeholder.startswith("http")
                        or placeholder.startswith("#")
                        or "|" in placeholder
                        or placeholder in ["TODO", "FIXME", "NOTE", "WARNING"]
                        or placeholder.startswith("mailto:")
                        or placeholder.startswith("https://")
                        or placeholder.startswith("http://")
                        or placeholder.startswith("www.")
                        or "(" in placeholder  # Likely a markdown link
                        or ")" in placeholder  # Likely a markdown link
                    ):
                        issues.append((line_num, line.strip(), placeholder))
                break

    return issues


def check_file(filepath: Path) -> list[tuple[int, str, str]]:
    """Check a single markdown file for bracketed placeholders."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        return find_bracketed_placeholders(content, str(filepath))
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return []


def main():
    """Main function for pre-commit hook usage."""
    # Get files from command line arguments (pre-commit passes changed files)
    files_to_check = sys.argv[1:] if len(sys.argv) > 1 else []

    if not files_to_check:
        # If no files specified, check all markdown files in current directory
        files_to_check = [
            str(f)
            for f in Path(".").rglob("*.md")
            if not any(
                exclude in str(f)
                for exclude in [
                    "/venv/",
                    "/.git/",
                    "/node_modules/",
                    "/600_archives/",
                    "/site-packages/",
                    "/.pytest_cache/",
                    "/.ruff_cache/",
                    "/__pycache__/",
                    "/dist-info/",
                    "/Library/",
                ]
            )
        ]

    issues_found = []

    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() == ".md":
            file_issues = check_file(path)
            if file_issues:
                issues_found.extend(
                    [
                        (str(path), line_num, line, placeholder)
                        for line_num, line, placeholder in file_issues
                    ]
                )

    if issues_found:
        print("X Bracketed placeholders detected in markdown files:")
        print(
            "These can break markdown rendering and should be replaced with plain text."
        )
        print()

        for file_path, line_num, line, placeholder in issues_found:
            print(f"📄 {file_path}:{line_num}")
            print(f"   {line}")
            print(f"   💡 Replace '[{placeholder}]' with plain text")
            print()

        print("🔧 Quick fixes:")
        print("   - Replace [Describe something] with: Describe the purpose and scope")
        print("   - Replace [Owner] with: Core Team")
        print("   - Replace [Usage] with: How to use this document")
        print()
        print(
            "💡 Use: python scripts/fix_bracketed_placeholders.py to auto-fix common patterns"
        )

        sys.exit(1)
    else:
        print("OK No bracketed placeholders found in markdown files")
        sys.exit(0)


if __name__ == "__main__":
    main()
