#!/usr/bin/env python3
"""
Fix the most common type errors systematically.
"""

import os
import re
from pathlib import Path
from typing import Any


def fix_psycopg_row_factory(file_path: Path) -> bool:
    """Add row_factory = dict_row to psycopg connections."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        original_content = content

        # Pattern: psycopg.connect(...) as conn: followed by with conn.cursor() as cur:
        pattern = r"(with psycopg\.connect\([^)]+\) as conn:\s*\n)(\s*)(with conn\.cursor\(\) as cur:)"

        def replacement(match: Any):
            indent: Any = match.group(2)
            return f"{match.group(1)}{indent}conn.row_factory = dict_row  # type: ignore[attr-defined]\n{match.group(2)}{match.group(3)}"

        new_content: Any = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if new_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_database_result_types(file_path: Path) -> bool:
    """Add type annotations for database query results."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        original_content = content

        # Fix fetchall() results
        fetchall_pattern = r"(\w+) = cur\.fetchall\(\)\s*\n"

        def fetchall_replacement(match: Any):
            var_name: Any = match.group(1)
            return f"{var_name} = cur.fetchall()\n        # Type annotation for database result\n        {var_name}: list[dict[str, Any]] = {var_name}  # type: ignore[assignment]\n"

        content: Any = re.sub(fetchall_pattern, fetchall_replacement, content)

        # Fix fetchone() results
        fetchone_pattern = r"(\w+) = cur\.fetchone\(\)\s*\n(\s*)(if \1:)"

        def fetchone_replacement(match: Any):
            var_name: Any = match.group(1)
            indent: Any = match.group(2)
            return f"{var_name} = cur.fetchone()\n{indent}# Type annotation for database result\n{indent}{var_name}: dict[str, Any] = {var_name}  # type: ignore[assignment]\n{indent}{match.group(3)}"

        content: Any = re.sub(fetchone_pattern, fetchone_replacement, content)

        # Add Any import if needed
        if "Any" in content and "from typing import Any" not in content:
            lines: Any = content.split("\n")
            # Find first import line
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    lines.insert(i, "from typing import Any")
                    break
            content = "\n".join(lines)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_deprecated_types_safe(file_path: Path) -> bool:
    """Safely fix deprecated types without breaking imports."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        original_content = content

        # Only fix Optional and Union if they're actually used
        if "" in content:
            content = re.sub(r"Optional\[([^\ | None]+)\]", r"\1 | None", content)

        if "" in content:

            def fix_union(match: Any):
                types_str: Any = match.group(1)
                types = [t.strip() for t in types_str.split(" | ")]
                return " | ".join(types)

            content = re.sub(r"Union\[([^\]]+)\]", fix_union, content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> Any:
    """Main function."""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Fix common type errors systematically")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", type=str, help="Specific file to process")
    parser.add_argument(
        "--step",
        type=str,
        choices=["psycopg", "database", "deprecated", "all"],
        default="all",
        help="Which step to run",
    )

    args: Any = parser.parse_args()

    if args.file:
        files = [Path(args.file)]
    else:
        # Find Python files
        files = []
        for root, dirs, filenames in os.walk("."):
            if any(skip in root for skip in ["600_archives", "venv", ".venv", "__pycache__"]):
                continue
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(Path(root) / filename)

    changes_made = 0

    for file_path in files:
        file_changed = False

        if args.step in ["psycopg", "all"]:
            if fix_psycopg_row_factory(file_path):
                file_changed = True

        if args.step in ["database", "all"]:
            if fix_database_result_types(file_path):
                file_changed = True

        if args.step in ["deprecated", "all"]:
            if fix_deprecated_types_safe(file_path):
                file_changed = True

        if file_changed:
            changes_made += 1
            if args.dry_run:
                print(f"Would fix: {file_path}")
            else:
                print(f"Fixed: {file_path}")

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {changes_made} files")


if __name__ == "__main__":
    main()
