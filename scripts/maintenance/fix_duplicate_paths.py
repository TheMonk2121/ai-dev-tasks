from __future__ import annotations

import re
import sys
from pathlib import Path

#!/usr/bin/env python3
"""
Fix Duplicate Paths

This script fixes the duplicate paths that were created by the previous broken links fix.
"""

def find_files_with_duplicate_paths() -> list[str]:
    """Find files that contain duplicate path patterns."""
    duplicate_patterns = [
        r"100_memory/100_memory/",
        r"200_setup/200_setup/",
        r"300_examples/300_examples/",
        r"400_guides/400_guides/",
        r"500_research/500_research/",
        r"",
        r"docs/docs/",
        r"dspy-rag-system/docs/dspy-rag-system/docs/",
    ]

    files_to_fix = []

    # Find all markdown files
    for md_file in Path(".").rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            has_duplicates = False

            for pattern in duplicate_patterns:
                if re.search(pattern, content):
                    has_duplicates = True
                    break

            if has_duplicates:
                files_to_fix.append(str(md_file))
        except Exception:
            continue

    return files_to_fix

def fix_duplicate_paths(file_path: str) -> bool:
    """Fix duplicate paths in a file."""
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        original_content = content

        # Fix duplicate patterns
        replacements = [
            (r"100_memory/100_memory/", "100_memory/"),
            (r"200_setup/200_setup/", "200_setup/"),
            (r"300_examples/300_examples/", "300_examples/"),
            (r"400_guides/400_guides/", "400_guides/"),
            (r"500_research/500_research/", "500_research/"),
            (r"", ""),
            (r"docs/docs/", "docs/"),
            (r"dspy-rag-system/docs/dspy-rag-system/docs/", "dspy-rag-system/docs/"),
        ]

        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # Write back if changed
        if content != original_content:
            Path(file_path).write_text(content, encoding="utf-8")
            print(f"  ✅ Fixed duplicate paths in: {file_path}")
            return True

        return False
    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False

def main():
    print("🔧 Finding files with duplicate paths...")
    files_to_fix = find_files_with_duplicate_paths()

    print(f"📁 Found {len(files_to_fix)} files with duplicate paths")

    if not files_to_fix:
        print("✅ No duplicate paths found!")
        return

    fixed_count = 0
    for file_path in files_to_fix:
        print(f"\n🔧 Fixing {file_path}:")
        if fix_duplicate_paths(file_path):
            fixed_count += 1

    print("\n📊 Summary:")
    print(f"  Files processed: {len(files_to_fix)}")
    print(f"  Files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
