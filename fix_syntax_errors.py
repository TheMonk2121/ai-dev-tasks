#!/usr/bin/env python3
"""
Comprehensive syntax error fixer for Python files.
Fixes common patterns that prevent ruff from processing files.
"""

import os
import re
import sys
from pathlib import Path


def fix_import_placement_errors(content: str) -> str:
    """Fix import statements placed in wrong locations."""

    # Pattern 1: import after except block
    # Fix: except:\n    ...\nimport module\n\n    code -> except:\n    ...\n    import module\n    code
    content = re.sub(
        r"(\s+except.*?:\s*\n\s+.*?\n)import (\w+)\n\n(\s+\w+.*?\n)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    # Pattern 2: import after try block
    # Fix: try:\n    ...\nexcept:\n    ...\nimport module\n\n    code -> try:\n    ...\nexcept:\n    ...\n    import module\n    code
    content = re.sub(
        r"(\s+except.*?:\s*\n\s+.*?\n)import (\w+)\n\n(\s+\w+.*?\n)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    # Pattern 3: import in middle of function
    # Fix: def func():\n    ...\nimport module\n\n    code -> def func():\n    ...\n    import module\n    code
    content = re.sub(
        r"(\s+def \w+.*?:\s*\n\s+.*?\n)import (\w+)\n\n(\s+\w+.*?\n)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    # Pattern 4: import after if __name__ == "__main__":
    # Fix: if __name__ == "__main__":\nimport module\n\n    code -> if __name__ == "__main__":\n    import module\n    code
    content = re.sub(
        r'(\s+if __name__ == "__main__":\s*\n)import (\w+)\n\n(\s+\w+.*?\n)',
        r"\1    import \2\n\3",
        content,
        flags=re.DOTALL,
    )

    return content


def fix_indentation_errors(content: str) -> str:
    """Fix common indentation errors."""

    # Pattern 1: Fix unexpected indentation after import
    # Fix: import module\n    code -> import module\ncode
    content = re.sub(r"^import (\w+)\n(\s{4,})", r"import \1\n", content, flags=re.MULTILINE)

    # Pattern 2: Fix unexpected indentation in function definitions
    # Fix: def func():\n    ...\n    import module\n\n    code -> def func():\n    ...\n    import module\n    code
    content = re.sub(
        r"(\s+def \w+.*?:\s*\n\s+.*?\n)import (\w+)\n\n(\s+\w+.*?\n)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    return content


def fix_try_except_blocks(content: str) -> str:
    """Fix malformed try/except blocks."""

    # Pattern 1: Fix try block with import in middle
    # Fix: try:\n    ...\nimport module\n    ...\nexcept: -> try:\n    ...\n    import module\n    ...\nexcept:
    content = re.sub(
        r"(\s+try:\s*\n\s+.*?\n)import (\w+)\n(\s+.*?\n\s+except)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    # Pattern 2: Fix except block with import in middle
    # Fix: except:\n    ...\nimport module\n    ...\n    code -> except:\n    ...\n    import module\n    ...\n    code
    content = re.sub(
        r"(\s+except.*?:\s*\n\s+.*?\n)import (\w+)\n(\s+.*?\n)", r"\1    import \2\n\3", content, flags=re.DOTALL
    )

    return content


def fix_syntax_errors(file_path: str) -> bool:
    """Fix syntax errors in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_import_placement_errors(content)
        content = fix_indentation_errors(content)
        content = fix_try_except_blocks(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def find_files_with_syntax_errors():
    """Find all Python files with syntax errors."""
    files_with_errors = []

    for root, dirs, files in os.walk("."):
        # Skip problematic directories
        if any(skip in root for skip in ["__pycache__", "venv", "600_archives", "dspy-rag-system", "node_modules"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        compile(f.read(), file_path, "exec")
                except SyntaxError:
                    files_with_errors.append(file_path)

    return files_with_errors


def main():
    """Main function to fix all syntax errors."""
    print("🔍 Finding files with syntax errors...")
    files_with_errors = find_files_with_syntax_errors()

    print(f"Found {len(files_with_errors)} files with syntax errors")

    fixed_count = 0
    for file_path in files_with_errors:
        print(f"Fixing: {file_path}")
        if fix_syntax_errors(file_path):
            fixed_count += 1
            print("  ✅ Fixed")
        else:
            print("  ⚠️  No changes needed")

    print(f"\n🎉 Fixed {fixed_count} files")

    # Verify fixes
    print("\n🔍 Verifying fixes...")
    remaining_errors = find_files_with_syntax_errors()
    print(f"Remaining files with syntax errors: {len(remaining_errors)}")

    if remaining_errors:
        print("Files still with errors:")
        for file_path in remaining_errors[:10]:  # Show first 10
            print(f"  {file_path}")


if __name__ == "__main__":
    main()
