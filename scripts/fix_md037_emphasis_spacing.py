#!/usr/bin/env python3
"""
Fix MD037 - Spaces inside emphasis markers.
Removes spaces inside emphasis markers like ** text ** → **text**.
"""

import glob
import re


def fix_md037_emphasis_spacing():
    """Fix MD037 violations by removing spaces inside emphasis markers."""
    print("🔧 Fixing MD037 - Emphasis Spacing")
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
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix bold emphasis: ** text ** → **text**
            content = re.sub(r"\*\*\s+([^*]+?)\s+\*\*", r"**\1**", content)

            # Fix italic emphasis: * text * → *text*
            content = re.sub(r"\*\s+([^*]+?)\s+\*", r"*\1*", content)

            # Fix bold emphasis with underscores: __ text __ → __text__
            content = re.sub(r"__\s+([^_]+?)\s+__", r"__\1__", content)

            # Fix italic emphasis with underscores: _ text _ → _text_
            content = re.sub(r"_\s+([^_]+?)\s+_", r"_\1_", content)

            # Write back if changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Count the number of fixes
                original_emphasis = len(re.findall(r"\*\*\s+[^*]+\s+\*\*", original_content))
                original_emphasis += len(re.findall(r"\*\s+[^*]+\s+\*", original_content))
                original_emphasis += len(re.findall(r"__\s+[^_]+\s+__", original_content))
                original_emphasis += len(re.findall(r"_\s+[^_]+\s+_", original_content))

                new_emphasis = len(re.findall(r"\*\*\s+[^*]+\s+\*\*", content))
                new_emphasis += len(re.findall(r"\*\s+[^*]+\s+\*", content))
                new_emphasis += len(re.findall(r"__\s+[^_]+\s+__", content))
                new_emphasis += len(re.findall(r"_\s+[^_]+\s+_", content))

                fixes = original_emphasis - new_emphasis

                print(f"✅ Fixed: {file_path} ({fixes} emphasis markers)")
                files_fixed += 1
                total_fixes += fixes
            else:
                files_unchanged += 1

        except Exception as e:
            print(f"❌ Failed: {file_path} - {str(e)}")
            files_failed += 1

    print("\n📊 Summary:")
    print(f"  Files processed: {len(markdown_files)}")
    print(f"  Files fixed: {files_fixed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Files unchanged: {files_unchanged}")
    print(f"  Total emphasis markers fixed: {total_fixes}")

    if files_fixed > 0:
        print(f"\n🎉 Successfully fixed {files_fixed} files!")
    else:
        print("\nℹ️  No files needed fixing.")

if __name__ == "__main__":
    fix_md037_emphasis_spacing()
