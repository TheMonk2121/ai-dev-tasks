#!/usr/bin/env python3.12.123.11
"""
File Name Migration Script

This script helps migrate files to follow the naming conventions defined in
200_naming-conventions.md. It provides both a dry-run mode to preview changes
and an execution mode to actually rename files.

Usage:
    python3 scripts/migrate_file_names.py --dry-run  # Preview changes
    python3 scripts/migrate_file_names.py --execute   # Actually rename files
"""

import shutil
import sys
from pathlib import Path
from typing import List, Tuple

# Migration mapping based on 200_naming-conventions.md
MIGRATION_MAP = {
    # High Priority (Core Files)
    "README.md": "400_project-overview.md",
    "SYSTEM_OVERVIEW.md": "400_system-overview.md",
    "SETUP_REQUIREMENTS.md": "202_setup-requirements.md",
    "CURSOR_MEMORY_CONTEXT.md": "100_cursor-memory-context.md",
    # Medium Priority (Documentation)
    "CONTEXT_PRIORITY_GUIDE.md": "400_context-priority-guide.md",
    "MEMORY_CONTEXT_GUIDE.md": "400_context-priority-guide.md",
    "TIMESTAMP_UPDATE_GUIDE.md": "400_timestamp-update-guide.md",
    # Low Priority (Templates & Archives)
    "DOCUMENTATION_EXAMPLE.md": "300_documentation-example.md",
    "C9_COMPLETION_SUMMARY.md": "500_c9-completion-summary.md",
    "C10_COMPLETION_SUMMARY.md": "500_c10-completion-summary.md",
}


def get_migration_plan() -> list[tuple[str, str]]:
    """Get the migration plan with file existence checks."""
    plan = []
    root_dir = Path(".")

    for old_name, new_name in MIGRATION_MAP.items():
        old_path = root_dir / old_name
        new_path = root_dir / new_name

        if old_path.exists():
            plan.append((str(old_path), str(new_path)))
        else:
            print(f"⚠️  Warning: {old_name} not found, skipping")

    return plan


def update_file_references(old_name: str, new_name: str) -> None:
    """Update references to the old filename in other files."""
    root_dir = Path(".")

    # Files that might contain references
    reference_files = [
        "README.md",
        "SYSTEM_OVERVIEW.md",
        "CONTEXT_PRIORITY_GUIDE.md",
        "CURSOR_MEMORY_CONTEXT.md",
        ".cursorrules",
        "200_naming-conventions.md",
    ]

    for ref_file in reference_files:
        ref_path = root_dir / ref_file
        if ref_path.exists():
            try:
                content = ref_path.read_text(encoding="utf-8")
                if old_name in content:
                    new_content = content.replace(old_name, new_name)
                    ref_path.write_text(new_content, encoding="utf-8")
                    print(f"  ✅ Updated references in {ref_file}")
            except Exception as e:
                print(f"  ⚠️  Warning: Could not update {ref_file}: {e}")


def preview_migration() -> None:
    """Preview the migration without making changes."""
    print("🔍 **Migration Preview**")
    print("=" * 50)

    plan = get_migration_plan()

    if not plan:
        print("✅ No files need migration!")
        return

    print(f"📋 Found {len(plan)} files to migrate:")
    print()

    for old_path, new_path in plan:
        print(f"📁 {old_path} → {new_path}")

    print()
    print("💡 Run with --execute to perform the migration")


def execute_migration() -> None:
    """Execute the migration."""
    print("🚀 **Executing Migration**")
    print("=" * 50)

    plan = get_migration_plan()

    if not plan:
        print("✅ No files need migration!")
        return

    # Create backup
    backup_dir = Path("backup_before_migration")
    if not backup_dir.exists():
        backup_dir.mkdir()
        print(f"📦 Created backup directory: {backup_dir}")

    for old_path, new_path in plan:
        old_file = Path(old_path)
        new_file = Path(new_path)

        # Create backup
        backup_file = backup_dir / old_file.name
        shutil.copy2(old_file, backup_file)

        # Rename file
        try:
            old_file.rename(new_file)
            print(f"✅ Renamed: {old_path} → {new_path}")

            # Update references
            update_file_references(old_file.name, new_file.name)

        except Exception as e:
            print(f"❌ Error renaming {old_path}: {e}")
            # Restore from backup
            shutil.copy2(backup_file, old_file)
            print(f"🔄 Restored {old_path} from backup")

    print()
    print("🎉 Migration completed!")
    print(f"📦 Backup files available in: {backup_dir}")


def main():
    """Main function."""
    if len(sys.argv) != 2 or sys.argv[1] not in ["--dry-run", "--execute"]:
        print("Usage: python3 scripts/migrate_file_names.py --dry-run|--execute")
        print()
        print("Options:")
        print("  --dry-run   Preview changes without making them")
        print("  --execute   Actually rename files and update references")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "--dry-run":
        preview_migration()
    elif mode == "--execute":
        execute_migration()


if __name__ == "__main__":
    main()
