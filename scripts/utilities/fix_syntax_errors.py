#!/usr/bin/env python3
"""
Script to fix syntax errors created by the previous corruption fix.
This fixes specific patterns that created invalid Python syntax.
"""

import re
import sys
from pathlib import Path
from typing import Any


def fix_syntax_errors(file_path: Path) -> dict[str, Any]:
    """Fix syntax errors in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        fixes_applied = 0

        # Fix specific syntax error patterns
        patterns = [
            # Fix missing closing parenthesis in print statements
            (
                r'print\(f"[^"]*\{result\.get\("key", ""\)[^"]*"',
                lambda m: m.group(0).replace('result.get("key", "")', 'result.get("key", "")') + ")",
            ),
            # Fix incomplete dictionary comprehensions
            (r"\{k: str\(v\) for k, v in \\1\.items\(\)", "os.environ.items()"),
            # Fix incomplete function calls
            (r'parameters=result\.get\("key", ""\)', 'parameters=result.get("key", "")'),
            # Fix incomplete string formatting
            (r'\{result\.get\("key", ""\)', 'result.get("key", "")'),
            # Fix incomplete expressions
            (r"\\1\.items\(\)", "os.environ.items()"),
            (r"\\1\[\\2\]", 'result.get("key", "")'),
        ]

        for pattern, replacement in patterns:
            if callable(replacement):
                # For lambda functions, use sub with a function
                new_content = re.sub(pattern, replacement, content)
            else:
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

        result = fix_syntax_errors(file_path)
        if result["success"]:
            print(f"Fixed {file_path}: {result['fixes_applied']} fixes applied")
        else:
            print(f"Error fixing {file_path}: {result['error']}")
            sys.exit(1)
    else:
        # Find and fix all files with syntax errors
        syntax_error_files = []

        # Check all Python files for syntax errors
        for py_file in Path("evals/").rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    # Look for common syntax error patterns
                    if r'result.get("key", "")' in content and (
                        content.count("(") != content.count(")")
                        or content.count("{") != content.count("}")
                        or content.count("[") != content.count("]")
                    ):
                        syntax_error_files.append(py_file)
            except Exception:
                continue

        print(f"Found {len(syntax_error_files)} files with potential syntax errors")

        total_fixes = 0
        successful_fixes = 0

        for file_path in syntax_error_files:
            result = fix_syntax_errors(file_path)
            if result["success"]:
                successful_fixes += 1
                total_fixes += result["fixes_applied"]
                print(f"✅ Fixed {file_path}: {result['fixes_applied']} fixes")
            else:
                print(f"❌ Error fixing {file_path}: {result['error']}")

        print("\nSummary:")
        print(f"Files processed: {len(syntax_error_files)}")
        print(f"Successfully fixed: {successful_fixes}")
        print(f"Total fixes applied: {total_fixes}")


if __name__ == "__main__":
    main()
