#!/usr/bin/env python3
"""
Fix MD033 - Inline HTML (anchor tags)
Converts HTML anchor tags to markdown-style anchors.
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

def has_html_anchors(content):
    """Check if content has HTML anchor tags."""
    # Look for <a id="..."> patterns
    return re.search(r'<a\s+id="[^"]+"\s*>', content) is not None

def fix_html_anchors(content):
    """Convert HTML anchor tags to markdown-style anchors."""
    # Pattern to match <a id="name"> or <a id="name"></a>
    # This handles both self-closing and explicit closing tags
    pattern = r'<a\s+id="([^"]+)"\s*>(?:</a>)?'

    def replace_anchor(match):
        anchor_id = match.group(1)
        return f"{{#{anchor_id}}}"

    fixed_content = re.sub(pattern, replace_anchor, content)
    return fixed_content

def process_file(file_path):
    """Process a single file to fix HTML anchors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if file needs fixing
        if not has_html_anchors(content):
            return False, "No HTML anchors found"

        # Fix the content
        fixed_content = fix_html_anchors(content)

        # Check if content actually changed
        if content == fixed_content:
            return False, "No changes needed"

        # Write the fixed content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        return True, "Fixed HTML anchors"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Main function to fix HTML anchors."""
    print("🔧 Fixing MD033 - HTML Anchor Tags")
    print("=" * 50)

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
            print(f"✅ Fixed: {file_path}")
            fixed_count += 1
        elif "Error" in message:
            print(f"❌ Failed: {file_path} - {message}")
            failed_count += 1
        # Don't print anything for files that don't need fixing

    print("\n📊 Summary:")
    print(f"  Files processed: {processed_count}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files failed: {failed_count}")
    print(f"  Files unchanged: {processed_count - fixed_count - failed_count}")

    if fixed_count > 0:
        print(f"\n🎉 Successfully fixed {fixed_count} files!")
        print("   Converted HTML anchor tags to markdown-style anchors")
    else:
        print("\n⚠️  No files needed fixing.")

if __name__ == "__main__":
    main()
