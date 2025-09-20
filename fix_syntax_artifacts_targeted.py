#!/usr/bin/env python3
"""
Fix syntax artifacts in the codebase - targeted version.

This script removes corrupted syntax artifacts like:
- result.get("key", "") placeholders
- \1 regex backreference artifacts
- Other common syntax corruption patterns

Only processes project files, not venv or other external directories.
"""

import os
import re
from pathlib import Path


def fix_file(file_path: Path) -> bool:
    """Fix syntax artifacts in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix result.get("key", "") artifacts - simple string replacement
        content = content.replace('result.get("key", "")', "result")

        # Fix \1 backreference artifacts in for loops - simple string replacement
        content = content.replace("\\1.items()", ".items()")
        content = content.replace("\\1.keys()", ".keys()")
        content = content.replace("\\1.values()", ".values()")

        # Fix incomplete f-strings with result.get artifacts
        content = re.sub(r'f"([^"]*)\{result\.get\("key", ""\)\}([^"]*)"', r'f"\1{result}\2"', content)

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
    """Main function to fix syntax artifacts."""
    print("🔧 Fixing syntax artifacts in codebase (targeted)...")

    # Find all Python files in project directories only
    python_files = []
    project_dirs = ["scripts", "src", "tests", "evals"]

    for project_dir in project_dirs:
        if os.path.exists(project_dir):
            for root, dirs, files in os.walk(project_dir):
                # Skip certain directories
                if any(skip in root for skip in [".git", "__pycache__", ".venv", "node_modules", "venv"]):
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

    print(f"\n🎉 Fixed {fixed_count} files with syntax artifacts")

    # Check for remaining artifacts
    print("\n🔍 Checking for remaining artifacts...")
    remaining_artifacts = 0

    for file_path in python_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if 'result.get("key", "")' in content or "\\1" in content:
                print(f"⚠️  Still has artifacts: {file_path}")
                remaining_artifacts += 1
        except:
            pass

    if remaining_artifacts == 0:
        print("✅ No remaining syntax artifacts found!")
    else:
        print(f"⚠️  {remaining_artifacts} files still have artifacts")


if __name__ == "__main__":
    main()
