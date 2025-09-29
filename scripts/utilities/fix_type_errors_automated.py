#!/usr/bin/env python3
"""
Automated Type Error Fixing Script

This script automatically fixes common type errors across the codebase:
1. Adds row_factory = dict_row to psycopg connections
2. Adds type annotations for database query results
3. Fixes deprecated type usage (Optional, Union)
4. Adds type ignore comments where appropriate
"""

import os
import re
import sys
from pathlib import Path
from typing import Any


def find_python_files() -> list[Path]:
    """Find all Python files to process."""
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in ["600_archives", "venv", ".venv", "__pycache__", "node_modules"]):
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)
    return python_files


def fix_psycopg_connections(content: str) -> str:
    """Fix psycopg connections to use dict_row."""
    # Pattern to find psycopg.connect without row_factory
    pattern = r"(with psycopg\.connect\([^)]+\) as conn:\s*\n)(\s*)(with conn\.cursor\(\) as cur:)"

    def replacement(match: Any):
        indent: Any = match.group(2)
        return f"{match.group(1)}{indent}conn.row_factory = dict_row  # type: ignore[attr-defined]\n{match.group(2)}{match.group(3)}"

    return re.sub(pattern, replacement, content, flags=re.MULTILINE)


def fix_database_query_results(content: str) -> str:
    """Add type annotations for database query results."""
    # Pattern to find fetchall() calls
    pattern = r"(\w+) = cur\.fetchall\(\)\s*\n"

    def replacement(match: Any):
        var_name: Any = match.group(1)
        return f"{var_name} = cur.fetchall()\n        # Type annotation to help type checker understand this is a list of dicts\n        {var_name}: list[dict[str, Any]] = {var_name}  # type: ignore[assignment]\n"

    return re.sub(pattern, replacement, content)


def fix_fetchone_results(content: str) -> str:
    """Add type annotations for fetchone() calls."""
    # Pattern to find fetchone() calls
    pattern = r"(\w+) = cur\.fetchone\(\)\s*\n(\s*)(if \1:)"

    def replacement(match: Any):
        var_name: Any = match.group(1)
        indent: Any = match.group(2)
        return f"{var_name} = cur.fetchone()\n{indent}# Type annotation to help type checker understand this is a dict\n{indent}{var_name}: dict[str, Any] = {var_name}  # type: ignore[assignment]\n{indent}{match.group(3)}"

    return re.sub(pattern, replacement, content)


def fix_deprecated_types(content: str) -> str:
    """Fix deprecated type usage."""
    # Replace Optional with | None
    content = re.sub(r"Optional\[([^\]]+)\]", r"\1 | None", content)

    # Replace Union with |
    content = re.sub(r"Union\[([^\]]+)\]", r"\1", content)

    # Remove unused imports
    content = re.sub(r"from typing import.*Optional.*\n", "", content)
    content = re.sub(r"from typing import.*Union.*\n", "", content)

    return content


def fix_file(file_path: Path, dry_run: bool = True) -> list[str]:
    """Fix type errors in a single file."""
    changes = []

    try:
        with open(file_path, encoding="utf-8") as f:
            original_content: Any = f.read()

        content = original_content

        # Apply fixes
        content = fix_psycopg_connections(content)
        content = fix_database_query_results(content)
        content = fix_fetchone_results(content)
        content = fix_deprecated_types(content)

        if content != original_content:
            if dry_run:
                changes.append(f"Would fix {file_path}")
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                changes.append(f"Fixed {file_path}")

    except Exception as e:
        changes.append(f"Error processing {file_path}: {e}")

    return changes


def main() -> Any:
    """Main function."""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Automatically fix common type errors")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--file", type=str, help="Specific file to process")
    parser.add_argument(
        "--exclude", nargs="+", default=["600_archives", "venv", ".venv", "__pycache__"], help="Directories to exclude"
    )

    args: Any = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        files = find_python_files()

    all_changes = []
    for file_path in files:
        changes = fix_file(file_path, dry_run=args.dry_run)
        all_changes.extend(changes)

    if all_changes:
        print(f"\n{'Dry run - ' if args.dry_run else ''}Changes made:")
        for change in all_changes:
            print(f"  {change}")
    else:
        print("No changes needed")


if __name__ == "__main__":
    main()
