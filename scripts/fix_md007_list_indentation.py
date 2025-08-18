#!/usr/bin/env python3.12.123.11
"""
Fix MD007 - Unordered list indentation.
Fixes unordered list indentation to use consistent spacing.
"""

import glob
import re


def fix_md007_list_indentation():
    """Fix MD007 violations by correcting unordered list indentation."""
    print("🔧 Fixing MD007 - Unordered List Indentation")
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
            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                # Check if this is an unordered list item
                # Pattern: spaces followed by -, *, or +
                match = re.match(r"^(\s*)([-*+])\s*(.*)$", line)
                if match:
                    indent, marker, content_part = match.groups()

                    # Calculate proper indentation
                    # Level 0: no indent
                    # Level 1: 2 spaces
                    # Level 2: 4 spaces
                    # Level 3: 6 spaces, etc.

                    # Count the current indentation level
                    current_level = len(indent) // 2

                    # Ensure proper indentation (2 spaces per level)
                    proper_indent = "  " * current_level

                    # Reconstruct the line with proper indentation
                    fixed_line = f"{proper_indent}{marker} {content_part}"
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)

            content = "\n".join(fixed_lines)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Count the number of fixes
                original_issues = len(re.findall(r"^\s*[-*+]\s+", original_content, flags=re.MULTILINE))
                new_issues = len(re.findall(r"^\s*[-*+]\s+", content, flags=re.MULTILINE))
                fixes = original_issues - new_issues

                print(f"OK Fixed: {file_path} ({fixes} list items)")
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
    print(f"  Total list items fixed: {total_fixes}")

    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print("\ni️  No files needed fixing.")


if __name__ == "__main__":
    fix_md007_list_indentation()
