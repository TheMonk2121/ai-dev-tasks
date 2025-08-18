#!/usr/bin/env python3.12.123.11
"""
Fix MD004 - Unordered list style.
Standardizes unordered list markers to use consistent style (dashes).
"""

import glob
import re


def fix_md004_list_style():
    """Fix MD004 violations by standardizing unordered list markers."""
    print("🔧 Fixing MD004 - Unordered List Style")
    print("=" * 60)

    # Find all markdown files
    markdown_files = []
    for pattern in ["**/*.md", "**/*.markdown"]:
        markdown_files.extend(glob.glob(pattern, recursive=True))

    # Remove files in certain directories
    markdown_files = [
        f
        for f in markdown_files
        if not any(exclude in f for exclude in ["node_modules", ".git", "__pycache__", ".pytest_cache", "venv"])
    ]

    print(f"Found {len(markdown_files)} markdown files")

    files_fixed = 0
    files_failed = 0
    files_unchanged = 0
    total_fixes = 0

    for file_path in markdown_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix unordered list markers to use consistent style (dashes)
            # Replace * and + with - for list markers
            content = re.sub(r"^(\s*)\*\s+", r"\1- ", content, flags=re.MULTILINE)
            content = re.sub(r"^(\s*)\+\s+", r"\1- ", content, flags=re.MULTILINE)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Count the number of fixes
                original_asterisks = len(re.findall(r"^\s*\*\s+", original_content, flags=re.MULTILINE))
                original_pluses = len(re.findall(r"^\s*\+\s+", original_content, flags=re.MULTILINE))
                new_asterisks = len(re.findall(r"^\s*\*\s+", content, flags=re.MULTILINE))
                new_pluses = len(re.findall(r"^\s*\+\s+", content, flags=re.MULTILINE))

                fixes = (original_asterisks - new_asterisks) + (original_pluses - new_pluses)

                print(f"OK Fixed: {file_path} ({fixes} list markers)")
                files_fixed += 1
                total_fixes += fixes
            else:
                files_unchanged += 1

        except Exception as e:
            print(f"X Failed: {file_path} - {str(e)}")
            files_failed += 1

    print("\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Files unchanged: {files_unchanged}")
    print(f"  Total list markers fixed: {total_fixes}")

    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print("\ni️  No files needed fixing.")


if __name__ == "__main__":
    fix_md004_list_style()
