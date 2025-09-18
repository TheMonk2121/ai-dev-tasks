#!/usr/bin/env python3
"""
Add missing Any imports where needed.
"""

import os
import re
from pathlib import Path
from typing import Any


def fix_any_imports_in_file(file_path: Path) -> bool:
    """Add Any import if needed."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()

        original_content = content

        # Check if Any is used but not imported
        if "Any" in content and "from typing import Any" not in content and "import Any" not in content:
            lines: Any = content.split("\n")
            new_lines = []

            # Find the first import line
            import_line_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_line_index = i
                    break

            if import_line_index >= 0:
                # Insert Any import after the first import
                lines.insert(import_line_index + 1, "from typing import Any")
            else:
                # Insert at the beginning if no imports found
                lines.insert(0, "from typing import Any")

            content = "\n".join(lines)

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

    parser: Any = argparse.ArgumentParser(description="Add missing Any imports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")
    parser.add_argument("--file", type=str, help="Specific file to process")

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
        if fix_any_imports_in_file(file_path):
            changes_made += 1
            if args.dry_run:
                print(f"Would fix: {file_path}")
            else:
                print(f"Fixed: {file_path}")

    print(f"\n{'Would fix' if args.dry_run else 'Fixed'} {changes_made} files")


if __name__ == "__main__":
    main()
