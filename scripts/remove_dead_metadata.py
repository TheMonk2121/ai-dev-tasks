#!/usr/bin/env python3
"""
Remove dead metadata headers from all files in the repository.

This script removes the following unverified metadata headers:
- CONTEXT_REFERENCE
- MODULE_REFERENCE
- MEMORY_CONTEXT
- DATABASE_SYNC

These headers were found to be unused in the actual codebase and are considered dead code.
"""

import re
from pathlib import Path
from typing import Tuple

# Patterns to remove
DEAD_METADATA_PATTERNS = [
    r"<!--\s*CONTEXT_REFERENCE:\s*[^>]*?-->",
    r"<!--\s*MODULE_REFERENCE:\s*[^>]*?-->",
    r"<!--\s*MEMORY_CONTEXT:\s*[^>]*?-->",
    r"<!--\s*DATABASE_SYNC:\s*[^>]*?-->",
]

# Directories to skip
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "600_archives",  # Skip archives
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    "*.egg-info",
}

# File extensions to process
PROCESS_EXTENSIONS = {
    ".md",
    ".py",
    ".sh",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
}


def should_process_file(file_path: Path) -> bool:
    """Check if a file should be processed."""
    # Skip directories
    if file_path.is_dir():
        return False

    # Skip files in skip directories
    for skip_dir in SKIP_DIRS:
        if skip_dir in file_path.parts:
            return False

    # Skip files without target extensions
    if file_path.suffix not in PROCESS_EXTENSIONS:
        return False

    return True


def remove_dead_metadata(content: str) -> Tuple[str, int]:
    """Remove dead metadata patterns from content."""
    removed_count = 0

    for pattern in DEAD_METADATA_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)
            removed_count += len(matches)

    # Clean up multiple consecutive empty lines that might be left
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

    return content, removed_count


def process_file(file_path: Path) -> Tuple[bool, int]:
    """Process a single file and remove dead metadata."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        content, removed_count = remove_dead_metadata(content)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, removed_count

        return False, 0

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    """Main function to remove dead metadata from all files."""
    repo_root = Path.cwd()
    print(f"🔍 Scanning repository: {repo_root}")

    total_files_processed = 0
    total_files_modified = 0
    total_headers_removed = 0

    # Find all files to process
    files_to_process = []
    for file_path in repo_root.rglob("*"):
        if should_process_file(file_path):
            files_to_process.append(file_path)

    print(f"📁 Found {len(files_to_process)} files to process")

    # Process each file
    for file_path in files_to_process:
        total_files_processed += 1
        modified, removed_count = process_file(file_path)

        if modified:
            total_files_modified += 1
            total_headers_removed += removed_count
            print(f"✅ Modified {file_path} (removed {removed_count} headers)")

    # Summary
    print("\n📊 Summary:")
    print(f"   Files processed: {total_files_processed}")
    print(f"   Files modified: {total_files_modified}")
    print(f"   Headers removed: {total_headers_removed}")

    if total_headers_removed > 0:
        print(f"\n🎯 Successfully removed {total_headers_removed} dead metadata headers!")
    else:
        print("\n✨ No dead metadata headers found to remove.")


if __name__ == "__main__":
    main()
