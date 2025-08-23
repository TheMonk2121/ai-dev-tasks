#!/usr/bin/env python3
"""
Fix MD047 - Files should end with a single newline character
Adds trailing newlines to markdown files that don't have them.
"""

import os


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

def needs_trailing_newline(file_path):
    """Check if a file needs a trailing newline."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file ends with newline
        if content and not content.endswith("\n"):
            return True

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return False

def add_trailing_newline(file_path):
    """Add a trailing newline to a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Add newline if not present
        if content and not content.endswith("\n"):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            return True

    except Exception as e:
        print(f"Error writing {file_path}: {e}")

    return False

def main():
    """Main function to fix trailing newlines."""
    print("🔧 Fixing MD047 - Trailing Newlines")
    print("=" * 50)

    # Find all markdown files
    markdown_files = find_markdown_files()
    print(f"Found {len(markdown_files)} markdown files")

    # Check which files need fixing
    files_needing_fix = []
    for file_path in markdown_files:
        if needs_trailing_newline(file_path):
            files_needing_fix.append(file_path)

    print(f"Files needing trailing newlines: {len(files_needing_fix)}")

    if not files_needing_fix:
        print("✅ All files already have trailing newlines!")
        return

    # Fix files
    fixed_count = 0
    for file_path in files_needing_fix:
        if add_trailing_newline(file_path):
            print(f"✅ Fixed: {file_path}")
            fixed_count += 1
        else:
            print(f"❌ Failed: {file_path}")

    print("\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files needing fix: {len(files_needing_fix)}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files failed: {len(files_needing_fix) - fixed_count}")

    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} files!")
    else:
        print("\n⚠️  No files were fixed.")

if __name__ == "__main__":
    main()
