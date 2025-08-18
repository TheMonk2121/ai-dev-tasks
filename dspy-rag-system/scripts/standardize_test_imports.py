#!/usr/bin/env python3
"""
Standardize test file imports

This script removes manual path manipulation from test files since conftest.py
now handles import path configuration centrally.
"""

import re
from pathlib import Path


def fix_test_file(file_path):
    """Fix a single test file by removing manual path manipulation"""
    with open(file_path) as f:
        content = f.read()

    original_content = content

    # Remove sys.path.insert and sys.path.append lines
    content = re.sub(r"# Add.*path.*\n", "", content)
    content = re.sub(r"sys\.path\.insert\(0,.*\)\n", "", content)
    content = re.sub(r"sys\.path\.append\(.*\)\n", "", content)

    # Remove unused imports
    content = re.sub(r"import os\n", "", content)
    content = re.sub(r"import sys\n", "", content)

    # Clean up multiple blank lines
    content = re.sub(r"\n\n\n+", "\n\n", content)

    # Only write if content changed
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    else:
        print(f"No changes needed: {file_path}")
        return False


def main():
    """Main function to process all test files"""
    tests_dir = Path(__file__).parent.parent / "tests"

    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return

    fixed_count = 0
    total_count = 0

    for test_file in tests_dir.glob("test_*.py"):
        if test_file.name == "conftest.py":
            continue

        total_count += 1
        if fix_test_file(test_file):
            fixed_count += 1

    print(f"\nSummary: Fixed {fixed_count} out of {total_count} test files")
    print("All test files now use centralized import configuration from conftest.py")


if __name__ == "__main__":
    main()
