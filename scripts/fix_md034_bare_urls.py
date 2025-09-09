#!/usr/bin/env python3
"""
Fix MD034 - Bare URL used
Wraps bare URLs in angle brackets to make them proper markdown links.
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


def has_bare_urls(content):
    """Check if content has bare URLs."""
    # Simple pattern to find http/https URLs
    pattern = r"https?://[^\s<>\[\]()]+"
    matches = re.findall(pattern, content)

    # Filter out URLs that are already in angle brackets or markdown links
    bare_urls = []
    for match in matches:
        # Check if this URL is already in angle brackets or markdown links
        url_start = content.find(match)
        if url_start > 0:
            # Check if preceded by < or [text](
            before_url = content[:url_start]
            if not (before_url.endswith("<") or before_url.endswith("(")):
                bare_urls.append(match)

    return len(bare_urls) > 0


def fix_bare_urls(content):
    """Wrap bare URLs in angle brackets."""
    # Simple pattern to find http/https URLs
    pattern = r"https?://[^\s<>\[\]()]+"

    def replace_url(match):
        url = match.group(0)
        # Check if this URL is already in angle brackets or markdown links
        url_start = match.start()
        if url_start > 0:
            before_url = content[:url_start]
            if before_url.endswith("<") or before_url.endswith("("):
                return url  # Already properly formatted
        return f"<{url}>"

    fixed_content = re.sub(pattern, replace_url, content)
    return fixed_content


def process_file(file_path):
    """Process a single file to fix bare URLs."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if file needs fixing
        if not has_bare_urls(content):
            return False, "No bare URLs found"

        # Fix the content
        fixed_content = fix_bare_urls(content)

        # Check if content actually changed
        if content == fixed_content:
            return False, "No changes needed"

        # Write the fixed content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        return True, "Fixed bare URLs"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main function to fix bare URLs."""
    print("🔧 Fixing MD034 - Bare URLs")
    print("=" * 40)

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
        print("   Wrapped bare URLs in angle brackets")
    else:
        print("\n⚠️  No files needed fixing.")


if __name__ == "__main__":
    main()
