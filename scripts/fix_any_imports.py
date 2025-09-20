#!/usr/bin/env python3
"""
Fix missing Any imports in Python files.

This script identifies files that use 'Any' type hints but are missing
the 'from typing import Any' import and adds it automatically.
"""

import os
import re
import sys
from pathlib import Path


def has_any_usage(content: str) -> bool:
    """Check if file uses Any type hints."""
    # Look for Any in type hints: variable: Any, -> Any, etc.
    patterns = [
        r":\s*Any\b",  # variable: Any
        r"->\s*Any\b",  # -> Any
        r"Any\s*\[",  # Any[...]
        r"list\[Any\]",  # list[Any]
        r"dict\[.*Any.*\]",  # dict[str, Any]
    ]
    return any(re.search(pattern, content) for pattern in patterns)


def has_any_import(content: str) -> bool:
    """Check if file already imports Any."""
    return "from typing import Any" in content or "from typing import" in content and "Any" in content


def add_any_import(content: str) -> str:
    """Add Any import to file content."""
    lines = content.split("\n")

    # Find the best place to insert the import
    insert_line = 0
    for i, line in enumerate(lines):
        # Skip shebang and docstring
        if line.startswith("#!") or line.startswith('"""') or line.startswith("'''"):
            continue
        # Skip __future__ imports
        if line.startswith("from __future__"):
            continue
        # Find first import or after docstring
        if line.startswith("import ") or line.startswith("from "):
            insert_line = i
            break
        # If we hit non-import code, insert before it
        if line.strip() and not line.startswith("#"):
            insert_line = i
            break

    # Insert the import
    lines.insert(insert_line, "from typing import Any")
    return "\n".join(lines)


def fix_file(file_path: Path) -> bool:
    """Fix Any import in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Skip if already has Any import or doesn't use Any
        if has_any_import(content) or not has_any_usage(content):
            return False

        # Add the import
        new_content = add_any_import(content)

        # Write back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Fixed: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix Any imports in all Python files."""
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = Path(".")

    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist")
        sys.exit(1)

    print(f"Fixing Any imports in {target_dir}")

    # Find all Python files
    python_files = list(target_dir.rglob("*.py"))

    fixed_count = 0
    total_files = len(python_files)

    for file_path in python_files:
        # Skip __pycache__ and .venv directories
        if "__pycache__" in str(file_path) or ".venv" in str(file_path):
            continue

        if fix_file(file_path):
            fixed_count += 1

    print("\n📊 Summary:")
    print(f"   Total Python files: {total_files}")
    print(f"   Files fixed: {fixed_count}")
    print(f"   Files unchanged: {total_files - fixed_count}")


if __name__ == "__main__":
    main()
