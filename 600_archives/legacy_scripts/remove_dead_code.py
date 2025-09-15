#!/usr/bin/env python3
"""
Remove dead code that references 600_archives or other deprecated content.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Files that contain dead code references to 600_archives
DEAD_CODE_FILES = [
    # Files with broken imports from 600_archives
    "scripts/evaluation/evaluation_system_integration.py",
    "scripts/evaluation/synthetic_smoke_test.py",
    "scripts/evaluation/comprehensive_integration_test.py",
    "src/graphs/eval_graph.py",
    # Files that reference 600_archives for file operations
    "scripts/utilities/single_doorway.py",
    "scripts/utilities/task_generator.py",
    "scripts/utilities/prd_generator.py",
    "scripts/utilities/doorway_utils.py",
    "scripts/utilities/executor.py",
    "scripts/utilities/automated_role_assignment.py",
    "scripts/maintenance/archive_move.py",
    # Files that have 600_archives in exclude patterns (should be updated)
    "scripts/data_processing/ingest_real_data.py",
    "scripts/data_processing/ingest_real_data_semantic.py",
    "scripts/data_processing/normalize_metadata_headers.py",
    "scripts/utilities/remove_dead_metadata.py",
    "scripts/utilities/regen_guide.py",
    "scripts/evaluation/file_analysis_checklist.py",
    "scripts/maintenance/fix_database_references.py",
    "scripts/maintenance/migrate_giant_guide_references.py",
    "scripts/maintenance/fix_duplicate_paths.py",
    "scripts/maintenance/fix_broken_links.py",
    "scripts/maintenance/fix_duplicate_tldr.py",
    "scripts/maintenance/cleanup_dspy_venv_references.py",
    "scripts/devtools/add_deprecation_notices.py",
]

# Patterns to remove or fix
DEAD_CODE_PATTERNS = [
    # Broken imports
    (r"from 600_archives\.600_deprecated\._ragchecker_eval_impl import CleanRAGCheckerEvaluator.*", ""),
    (r"from 600_archives\.600_deprecated\._ragchecker_eval_impl import.*", ""),
    # File path references to 600_archives
    (r"600_archives/artifacts/000_core_temp_files/", "artifacts/000_core_temp_files/"),
    (r"600_archives/consolidated-guides/", "consolidated-guides/"),
    (r"600_archives/legacy/", "legacy/"),
    (r"600_archives/legacy-archives/", "legacy-archives/"),
    (r"600_archives/legacy-tests/", "legacy-tests/"),
    # Archive directory references
    (r'archives_dir: str = "600_archives"', 'archives_dir: str = "artifacts"'),
    (r"--archives-dir.*600_archives", "--archives-dir artifacts"),
    (r'Path\("600_archives/', 'Path("artifacts/'),
    # Exclude patterns that reference 600_archives
    (r'"600_archives",', ""),
    (r"'600_archives',", ""),
    (r"600_archives/", ""),
]


def remove_dead_code_from_file(file_path: Path) -> bool:
    """Remove dead code patterns from a file."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False

    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply dead code pattern replacements
        for pattern, replacement in DEAD_CODE_PATTERNS:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        # Clean up multiple empty lines
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        # Clean up trailing whitespace
        content = re.sub(r"[ \t]+$", "", content, flags=re.MULTILINE)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Cleaned: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def remove_dead_files() -> list[str]:
    """Remove files that are entirely dead code."""
    files_to_remove = [
        # Files that are completely broken due to 600_archives references
        "scripts/utilities/automated_role_assignment.py",  # Entirely about 600_archives
        "scripts/maintenance/archive_move.py",  # Moves files to 600_archives
        "scripts/utilities/single_doorway.py",  # References 600_archives extensively
        "scripts/utilities/task_generator.py",  # References 600_archives extensively
        "scripts/utilities/prd_generator.py",  # References 600_archives extensively
        "scripts/utilities/doorway_utils.py",  # References 600_archives extensively
        "scripts/utilities/executor.py",  # References 600_archives extensively
    ]

    removed_files = []
    for file_path in files_to_remove:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
                removed_files.append(file_path)
                print(f"🗑️  Removed dead file: {file_path}")
            except Exception as e:
                print(f"❌ Error removing {file_path}: {e}")

    return removed_files


def main():
    """Main cleanup function."""
    print("🧹 Starting dead code cleanup...")

    # Remove entirely dead files
    print("\n🗑️  Removing entirely dead files...")
    removed_files = remove_dead_files()

    # Clean up files with dead code patterns
    print("\n🔧 Cleaning up files with dead code patterns...")
    cleaned_files = []

    for file_path in DEAD_CODE_FILES:
        path = Path(file_path)
        if path.exists():
            if remove_dead_code_from_file(path):
                cleaned_files.append(file_path)

    # Summary
    print("\n📊 Cleanup Summary:")
    print(f"   🗑️  Files removed: {len(removed_files)}")
    print(f"   🔧 Files cleaned: {len(cleaned_files)}")

    if removed_files:
        print("\n🗑️  Removed files:")
        for file_path in removed_files:
            print(f"   - {file_path}")

    if cleaned_files:
        print("\n🔧 Cleaned files:")
        for file_path in cleaned_files:
            print(f"   - {file_path}")


if __name__ == "__main__":
    main()
