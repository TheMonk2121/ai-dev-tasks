#!/usr/bin/env python3
"""
Bulk Timestamp Update Script

This script updates all "Last Updated: 2024-08-07" timestamps to the current date
across all documentation files in the project.
"""

import re
from datetime import datetime
from pathlib import Path


def find_files_with_old_timestamp(root_dir: Path) -> list[tuple[Path, str]]:
    """Find all files containing the old timestamp."""
    old_timestamp_pattern = r"Last Updated: 2024-08-07"
    files_to_update = []

    # Common documentation directories
    doc_dirs = [
        "000_core",
        "100_memory",
        "200_setup",
        "400_guides",
        "500_research",
        "scripts",
        "dspy-rag-system/docs",
        "dspy-rag-system/processed_documents",
    ]

    for doc_dir in doc_dirs:
        dir_path = root_dir / doc_dir
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*.md"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                if re.search(old_timestamp_pattern, content):
                    files_to_update.append((file_path, content))
                    print(f"Found: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Also check root level files
    for file_path in root_dir.glob("*.md"):
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if re.search(old_timestamp_pattern, content):
                files_to_update.append((file_path, content))
                print(f"Found: {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return files_to_update


def update_timestamp_in_content(content: str) -> str:
    """Update the old timestamp to current date."""
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Pattern 1: "Last Updated: 2024-08-07"
    content = re.sub(r"Last Updated: 2024-08-07", f"Last Updated: {current_date}", content)

    # Pattern 2: "*Last Updated: 2024-08-07*"
    content = re.sub(r"\*Last Updated: 2024-08-07\*", f"*Last Updated: {current_date}*", content)

    # Pattern 3: "**Last Updated**: 2024-08-07"
    content = re.sub(r"\*\*Last Updated\*\*: 2024-08-07", f"**Last Updated**: {current_date}", content)

    # Pattern 4: "- Last Updated: 2024-08-07"
    content = re.sub(r"- Last Updated: 2024-08-07", f"- Last Updated: {current_date}", content)

    # Pattern 5: "- *Last Updated**: 2024-08-07"
    content = re.sub(r"- \*Last Updated\*\*: 2024-08-07", f"- *Last Updated**: {current_date}", content)

    return content


def main():
    """Main function to update all timestamps."""
    root_dir = Path.cwd()
    print(f"Scanning for files with old timestamps in: {root_dir}")

    # Find files to update
    files_to_update = find_files_with_old_timestamp(root_dir)

    if not files_to_update:
        print("✅ No files found with old timestamps!")
        return

    print(f"\nFound {len(files_to_update)} files to update:")
    for file_path, _ in files_to_update:
        print(f"  - {file_path}")

    # Auto-confirm for non-interactive execution
    print(f"\nAuto-updating timestamps in {len(files_to_update)} files...")

    # Update files
    updated_count = 0
    for file_path, content in files_to_update:
        try:
            updated_content = update_timestamp_in_content(content)

            if updated_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                updated_count += 1
                print(f"✅ Updated: {file_path}")
            else:
                print(f"⚠️  No changes needed: {file_path}")

        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")

    print(f"\n🎉 Successfully updated {updated_count} files!")
    print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")


if __name__ == "__main__":
    main()
