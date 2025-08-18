#!/usr/bin/env python3.12
"""Fix RUF001 errors (ambiguous dashes) systematically"""

import re
import subprocess
from pathlib import Path


def fix_ruf001_errors(file_path: Path) -> bool:
    """Fix RUF001 errors in a single file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Replace en dashes (-) with hyphens (-) in strings
        # This is the most common RUF001 error
        content = re.sub(r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content)

        # Also fix em dashes (-) with hyphens
        content = re.sub(r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content)

        # Fix Unicode symbols that might be ambiguous
        # Replace i (INFORMATION SOURCE) with i
        content = re.sub(r'(["\'])([^"\']*)(i)([^"\']*)(["\'])', r"\1\2i\4\5", content)

        # Replace other common Unicode symbols
        content = re.sub(r'(["\'])([^"\']*)(!)([^"\']*)(["\'])', r"\1\2!\4\5", content)
        content = re.sub(
            r'(["\'])([^"\']*)(OK)([^"\']*)(["\'])', r"\1\2OK\4\5", content
        )
        content = re.sub(r'(["\'])([^"\']*)(X)([^"\']*)(["\'])', r"\1\2X\4\5", content)

        # Fix non-breaking hyphens and other Unicode dashes
        content = re.sub(
            r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content
        )  # NON-BREAKING HYPHEN
        content = re.sub(
            r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content
        )  # FIGURE DASH
        content = re.sub(
            r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content
        )  # EN DASH
        content = re.sub(
            r'(["\'])([^"\']*)(-)([^"\']*)(["\'])', r"\1\2-\4\5", content
        )  # EM DASH

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix RUF001 errors across the project"""
    project_dirs = ["scripts", "dspy-rag-system", "tests"]
    fixed_files = 0

    for dir_name in project_dirs:
        if not Path(dir_name).exists():
            continue

        for py_file in Path(dir_name).rglob("*.py"):
            if fix_ruf001_errors(py_file):
                fixed_files += 1
                print(f"Fixed: {py_file}")

    print(f"\nFixed {fixed_files} files")

    # Run Ruff to check remaining RUF001 errors
    print("\nChecking remaining RUF001 errors...")
    result = subprocess.run(
        [
            "ruff",
            "check",
            "--select",
            "RUF001",
            "scripts/",
            "dspy-rag-system/",
            "tests/",
        ],
        capture_output=True,
        text=True,
    )

    if result.stdout:
        remaining_count = len(result.stdout.strip().split("\n"))
        print(f"Remaining RUF001 errors: {remaining_count}")
        if remaining_count <= 10:
            print("First few remaining errors:")
            print(result.stdout[:500])
    else:
        print("No RUF001 errors remaining!")


if __name__ == "__main__":
    main()
