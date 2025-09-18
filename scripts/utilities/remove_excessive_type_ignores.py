#!/usr/bin/env python3
"""
Remove excessive type ignore comments that were added by overly aggressive fixes.
"""

import re
from pathlib import Path


def remove_excessive_type_ignores_in_file(file_path: Path) -> bool:
    """Remove excessive type ignore comments from a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove all type: ignore[type-arg] comments that were added by the aggressive script
        # These are typically on lines that don't actually need them
        lines = content.split("\n")
        cleaned_lines = []

        for line in lines:
            # Check if this line has a type: ignore[type-arg] comment
            if "type: ignore[type-arg]" in line:
                # Remove the comment and see if the line is still valid
                cleaned_line = re.sub(r"\s*#\s*type:\s*ignore\[type-arg\].*$", "", line)

                # Only keep the type ignore if the line actually has a type error
                # For now, let's be conservative and remove most of them
                # We'll add them back selectively later
                cleaned_lines.append(cleaned_line.rstrip())
            else:
                cleaned_lines.append(line)

        cleaned_content = "\n".join(cleaned_lines)

        # Only write if changes were made
        if cleaned_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)

            print(f"Cleaned: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Remove excessive type ignore comments from all Python files."""
    print("🧹 Removing excessive type ignore comments...")

    # Find all Python files
    python_files = []
    for pattern in ["src/**/*.py", "scripts/**/*.py", "evals/**/*.py", "tests/**/*.py"]:
        python_files.extend(Path(".").glob(pattern))

    # Filter out archive and venv directories
    python_files = [
        f for f in python_files if "600_archives" not in str(f) and "venv" not in str(f) and ".venv" not in str(f)
    ]

    cleaned_count = 0
    for file_path in python_files:
        if remove_excessive_type_ignores_in_file(file_path):
            cleaned_count += 1

    print(f"\\nCleaned {cleaned_count} files")


if __name__ == "__main__":
    main()
