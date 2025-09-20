#!/usr/bin/env python3
"""
Script to fix missing 'from typing import Any' imports in Python files.
"""

import os
import re
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Fix missing typing imports in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if file already has 'from typing import Any'
        if "from typing import Any" in content:
            return False

        # Check if file uses 'Any' type annotation
        if "Any" not in content:
            return False

        # Find the import section
        lines = content.split("\n")
        import_end = 0

        # Find where imports end
        for i, line in enumerate(lines):
            if (
                line.strip()
                and not line.startswith(("import ", "from "))
                and not line.startswith("#")
                and not line.startswith('"""')
                and not line.startswith("'''")
            ):
                import_end = i
                break

        # Insert the import
        if import_end > 0:
            lines.insert(import_end, "from typing import Any")
        else:
            # If no imports found, add at the beginning
            lines.insert(0, "from typing import Any")

        # Write back
        new_content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Fixed: {file_path}")
        return True

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all Python files in the project."""
    project_root = Path(".")
    fixed_count = 0

    # Get all Python files that were modified
    python_files = [
        "scripts/data_processing/chunking/test_standards_compliant_chunking.py",
        "scripts/memory/setup_auto_capture.py",
        "scripts/memory/simple_auto_capture.py",
        "scripts/testing/test_query_storage.py",
        "scripts/utilities/cursor_daemon_capture.py",
        "scripts/utilities/cursor_file_trigger.py",
        "scripts/utilities/cursor_mcp_capture.py",
        "scripts/utilities/tools/atlas_cli.py",
        "src/retrieval/packer.py",
        "src/retrieval/reranker.py",
        "tests/implementation/run_real_database_tests.py",
        "tests/integration/run_real_database_tests.py",
        "tests/property/test_vector_props.py",
    ]

    for file_path in python_files:
        if Path(file_path).exists():
            if fix_file(Path(file_path)):
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
