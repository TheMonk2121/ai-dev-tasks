#!/usr/bin/env python3.12.123.11
"""
Fix MD012 - Multiple consecutive blank lines
Removes multiple consecutive blank lines, keeping only single blank lines.
"""

import os
import re


def find_markdown_files():
    """Find all markdown files excluding venv, node_modules, and .git."""
    markdown_files = []

    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in ["venv", "node_modules", ".git"]]

        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    return markdown_files


def has_multiple_blanks(content):
    """Check if content has multiple consecutive blank lines."""
    # Look for patterns like \n\n\n or more
    return re.search(r"\n\s*\n\s*\n", content) is not None


def fix_multiple_blanks(content):
    """Fix multiple consecutive blank lines."""
    # Replace multiple consecutive blank lines with single blank lines
    # This regex matches 2 or more consecutive blank lines and replaces with 1
    fixed_content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)
    return fixed_content


def process_file(file_path):
    """Process a single file to fix multiple blank lines."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if file needs fixing
        if not has_multiple_blanks(content):
            return False, "No multiple blanks found"

        # Fix the content
        fixed_content = fix_multiple_blanks(content)

        # Check if content actually changed
        if content == fixed_content:
            return False, "No changes needed"

        # Write the fixed content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        return True, "Fixed multiple blank lines"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main function to fix multiple blank lines."""
    print("🔧 Fixing MD012 - Multiple Consecutive Blank Lines")
    print("=" * 60)

    # Find all markdown files
    markdown_files = find_markdown_files()
    print(f"Found {len(markdown_files)} markdown files")

    # Process files
    processed_count = 0
    fixed_count = 0
    failed_count = 0

    for file_path in markdown_files:
        processed_count += 1
        success, message = process_file(file_path)

        if success:
            print(f"OK Fixed: {file_path}")
            fixed_count += 1
        elif "Error" in message:
            print(f"X Failed: {file_path} - {message}")
            failed_count += 1
        # Don't print anything for files that don't need fixing

    print("\n📊 Summary:")
    print(f"  Files processed: {processed_count}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files failed: {failed_count}")
    print(f"  Files unchanged: {processed_count - fixed_count - failed_count}")

    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} files!")
    else:
        print("\n!️  No files needed fixing.")


if __name__ == "__main__":
    main()
