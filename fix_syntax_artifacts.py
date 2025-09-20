#!/usr/bin/env python3
"""
Fix syntax artifacts in the codebase.

This script removes corrupted syntax artifacts like:
- result.get("key", "") placeholders
- \1 regex backreference artifacts
- Other common syntax corruption patterns
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

        # Fix result.get("key", "") artifacts
        content = re.sub(r'result\.get\("key", ""\)', "result", content)

        # Fix \1 backreference artifacts in for loops
        content = re.sub(r"for ([^,]+), ([^,]+) in \\1\.items\(\)", r"for \1, \2 in \1.items()", content)

        # Fix \1 artifacts in other contexts
        content = re.sub(r"\\1\.keys\(\)", r"\1.keys()", content)
        content = re.sub(r"\\1\.values\(\)", r"\1.values()", content)
        content = re.sub(r"\\1\.items\(\)", r"\1.items()", content)

        # Fix incomplete f-strings with result.get artifacts
        content = re.sub(r'f"([^"]*)\{result\.get\("key", ""\)\}([^"]*)"', r'f"\1{result}\2"', content)

        # Fix other common patterns
        content = re.sub(r'result\.get\("key", ""\)', "result", content)

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
    print("🔧 Fixing syntax artifacts in codebase...")

    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in [".git", "__pycache__", ".venv", "node_modules"]):
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
