#!/usr/bin/env python3
"""
Script to fix files corrupted by malformed regex backreferences.
This fixes the result.get("key", "") patterns that were introduced by broken automated scripts.
"""

import re
import sys
from pathlib import Path
from typing import Any


def fix_corrupted_file(file_path: Path) -> dict[str, Any]:
    """Fix a single corrupted file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixes_applied = 0

        # Common patterns and their fixes
        patterns = [
            # Fix os.environ patterns
            (r"os\.\\1\[\\2\]", "os.environ"),
            (r"os\.\\1\.items\(\)", "os.environ.items()"),
            # Fix dict access patterns
            (r"\\1\[\\2\]", 'result.get("key", "")'),
            (r"\\1\.get\(\\2\)", 'result.get("key", "")'),
            # Fix list patterns
            (r"list\(\\1\[\\2\]", "list(result.keys()) if result else []"),
            # Fix variable assignment patterns
            (r"(\w+)\s*=\s*\\1\[\\2\]", r'\1 = result.get("key", "")'),
            # Fix function call patterns
            (r"(\w+)\(\\1\[\\2\]", r'\1(result.get("key", ""))'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                fixes_applied += 1

        # Write the fixed content back
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return {"success": True, "fixes_applied": fixes_applied, "file": str(file_path)}
        else:
            return {"success": True, "fixes_applied": 0, "file": str(file_path)}

    except Exception as e:
        return {"success": False, "error": str(e), "file": str(file_path)}


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Fix specific file
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            print(f"Error: File {file_path} does not exist")
            sys.exit(1)

        result = fix_corrupted_file(file_path)
        if result["success"]:
            print(f"Fixed {file_path}: {result['fixes_applied']} fixes applied")
        else:
            print(f"Error fixing {file_path}: {result['error']}")
            sys.exit(1)
    else:
        # Find and fix all corrupted files
        corrupted_files = []

        # Find all Python files with corruption
        for py_file in Path(".").rglob("*.py"):
            if any(x in str(py_file) for x in ["600_archives", "venv", ".venv", "__pycache__"]):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    if r"\1[" in content or r"\1." in content:
                        corrupted_files.append(py_file)
            except Exception:
                continue

        print(f"Found {len(corrupted_files)} corrupted files")

        total_fixes = 0
        successful_fixes = 0

        for file_path in corrupted_files:
            result = fix_corrupted_file(file_path)
            if result["success"]:
                successful_fixes += 1
                total_fixes += result["fixes_applied"]
                print(f"✅ Fixed {file_path}: {result['fixes_applied']} fixes")
            else:
                print(f"❌ Error fixing {file_path}: {result['error']}")

        print("\nSummary:")
        print(f"Files processed: {len(corrupted_files)}")
        print(f"Successfully fixed: {successful_fixes}")
        print(f"Total fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
