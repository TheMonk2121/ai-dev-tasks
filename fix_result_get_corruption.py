#!/usr/bin/env python3
"""
Fix result.get("key", "") corruption patterns in the codebase.

This script specifically targets the widespread corruption pattern
that was introduced by the post-commit hook.
"""

import os
import re
from pathlib import Path
from typing import Any


def fix_file(file_path: Path) -> bool:
    """Fix result.get("key", "") corruption in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix the main corruption pattern: result.get("key", "")
        # This is a placeholder that should be replaced with appropriate code
        content = content.replace('result.get("key", "")', 'result')

        # Fix other common corruption patterns
        content = content.replace('os.result.get("key", "")', 'os.environ.get("POSTGRES_DSN", "")')
        content = content.replace('self.result.get("key", "")', 'self._counters.get(name, 0)')
        content = content.replace('project_root = Path(__file__).resolve().result.get("key", "")', 'project_root = Path(__file__).resolve().parent')
        content = content.replace('revision = result.get("key", "")', 'revision = parts[1].strip().split()[0]')
        content = content.replace('context_size = result.get("contexts", "")', 'context_size = len(result.get("contexts", []))')

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix corruption patterns."""
    print("🔧 Fixing result.get corruption patterns...")

    # Find all Python files in scripts and src directories
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in [".git", "__pycache__", ".venv", "node_modules", "venv", "tests"]):
            continue

        # Only process scripts and src directories
        if not (root.startswith("./scripts") or root.startswith("./src")):
            continue

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    print(f"📁 Found {len(python_files)} Python files to check")

    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            print(f"✅ Fixed: {file_path}")
            fixed_count += 1

    print(f"\n🎉 Fixed {fixed_count} files with result.get corruption")

if __name__ == "__main__":
    main()
