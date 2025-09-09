#!/usr/bin/env python3
"""
Auto Timestamp Update Script for Pre-commit Hooks

This script updates timestamps only for markdown files that are being committed,
making it suitable for pre-commit hooks and CI/CD automation.
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def get_staged_markdown_files() -> set[Path]:
    """Get all staged markdown files that are being committed."""
    import subprocess

    try:
        # Get staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], capture_output=True, text=True, check=True
        )

        staged_files = set()
        for line in result.stdout.strip().split("\n"):
            if line.strip() and line.endswith(".md"):
                staged_files.add(Path(line.strip()))

        return staged_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e}")
        return set()


def update_timestamp_in_content(content: str) -> str:
    """Update any old timestamp to current date."""
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Pattern 1: "Last Updated: YYYY-MM-DD" (any old date)
    content = re.sub(r"Last Updated: \d{4}-\d{2}-\d{2}", f"Last Updated: {current_date}", content)

    # Pattern 2: "*Last Updated: YYYY-MM-DD*"
    content = re.sub(r"\*Last Updated: \d{4}-\d{2}-\d{2}\*", f"*Last Updated: {current_date}*", content)

    # Pattern 3: "**Last Updated**: YYYY-MM-DD"
    content = re.sub(r"\*\*Last Updated\*\*: \d{4}-\d{2}-\d{2}", f"**Last Updated**: {current_date}", content)

    # Pattern 4: "- Last Updated: YYYY-MM-DD"
    content = re.sub(r"- Last Updated: \d{4}-\d{2}-\d{2}", f"- Last Updated: {current_date}", content)

    # Pattern 5: "- *Last Updated**: YYYY-MM-DD"
    content = re.sub(r"- \*Last Updated\*\*: \d{4}-\d{2}-\d{2}", f"- *Last Updated**: {current_date}", content)

    return content


def update_file_timestamp(file_path: Path) -> bool:
    """Update timestamp in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        updated_content = update_timestamp_in_content(content)

        if updated_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            # Stage the updated file
            import subprocess

            subprocess.run(["git", "add", str(file_path)], check=True)
            return True

        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False


def main():
    """Main function for pre-commit hook usage."""
    # Get staged markdown files
    staged_files = get_staged_markdown_files()

    if not staged_files:
        print("No staged markdown files found.")
        return 0

    print(f"Checking {len(staged_files)} staged markdown files for timestamp updates...")

    updated_count = 0
    for file_path in staged_files:
        if update_file_timestamp(file_path):
            print(f"✅ Updated timestamp: {file_path}")
            updated_count += 1

    if updated_count > 0:
        print(f"🎉 Updated timestamps in {updated_count} files")
        print(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")
    else:
        print("✅ All timestamps are current")

    return 0


if __name__ == "__main__":
    sys.exit(main())
