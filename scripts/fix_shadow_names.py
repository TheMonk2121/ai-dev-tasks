#!/usr/bin/env python3
"""
Shadow Name Fixer - Fix shadow fork names by renaming to role suffix patterns.

This script scans for disallowed patterns like *_enhanced.py, *-optimized.py and
suggests/executes renames to role suffix patterns (*_core.py, *_perf.py, *_compat.py)
or routes behind a facade.
"""

import ast
import json
import os
import re
import sys
from datetime import datetime, timezone, UTC
from typing import List, Tuple

# Disallowed patterns that indicate shadow forks
DISALLOWED_PATTERNS = [
    r".*_enhanced\.py$",
    r".*_optimized\.py$",
    r".*_improved\.py$",
    r".*_better\.py$",
    r".*_new\.py$",
    r".*_v2\.py$",
    r".*_v3\.py$",
    r".*_updated\.py$",
    r".*_fixed\.py$",
    r".*_patched\.py$",
]

# Role suffix patterns (allowed)
ROLE_SUFFIXES = ["_core", "_perf", "_compat", "_facade", "_shim"]

# Mapping of common patterns to role suffixes
PATTERN_MAPPINGS = {
    "_enhanced": "_perf",
    "_optimized": "_perf",
    "_improved": "_perf",
    "_better": "_perf",
    "_new": "_core",
    "_v2": "_perf",
    "_v3": "_perf",
    "_updated": "_core",
    "_fixed": "_core",
    "_patched": "_core",
}


def find_shadow_files() -> list[str]:
    """Find all files with disallowed shadow fork patterns."""
    shadow_files = []

    for root, _, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in [".git", "node_modules", "__pycache__", "venv", ".venv"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                for pattern in DISALLOWED_PATTERNS:
                    if re.match(pattern, file):
                        shadow_files.append(file_path)
                        break

    return shadow_files


def suggest_rename(file_path: str) -> tuple[str, str]:
    """Suggest a new name for a shadow file."""
    dir_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)

    # Find which pattern matches
    for old_suffix, new_suffix in PATTERN_MAPPINGS.items():
        if name.endswith(old_suffix):
            new_name = name.replace(old_suffix, new_suffix) + ext
            new_path = os.path.join(dir_path, new_name)
            return new_path, f"Replace {old_suffix} with {new_suffix}"

    # Default to _core if no specific mapping
    new_name = name + "_core" + ext
    new_path = os.path.join(dir_path, new_name)
    return new_path, "Add _core suffix"


def find_imports(file_path: str) -> list[str]:
    """Find all import statements in a Python file."""
    imports = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    if module:
                        imports.append(f"{module}.{alias.name}")
                    else:
                        imports.append(alias.name)

    except Exception:
        pass

    return imports


def find_files_importing(module_name: str) -> list[str]:
    """Find all files that import a specific module."""
    importing_files = []

    for root, _, files in os.walk("."):
        if any(skip in root for skip in [".git", "node_modules", "__pycache__", "venv", ".venv"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imports = find_imports(file_path)

                for imp in imports:
                    if module_name in imp or imp.endswith(module_name):
                        importing_files.append(file_path)
                        break

    return importing_files


def update_imports_in_file(file_path: str, old_module: str, new_module: str):
    """Update import statements in a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Simple string replacement for imports
        # This is a basic approach - in production you'd want more sophisticated AST manipulation
        updated_content = content.replace(old_module, new_module)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return True
    except Exception:
        return False


def main():
    """Main function to fix shadow fork names."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix shadow fork names")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--write", action="store_true", help="Actually rename files and update imports")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print("❌ Must specify --dry-run or --write")
        sys.exit(1)

    print("🔍 Scanning for shadow fork files...")

    # Find shadow files
    shadow_files = find_shadow_files()
    print(f"📋 Found {len(shadow_files)} shadow fork files")

    if not shadow_files:
        print("✅ No shadow fork files found")
        return

    # Plan renames
    rename_plan = []
    import_updates = []

    for file_path in shadow_files:
        new_path, reason = suggest_rename(file_path)

        # Check if new path already exists
        if os.path.exists(new_path):
            print(f"⚠️  {file_path} -> {new_path} (target exists, skipping)")
            continue

        # Get module name for import updates
        old_module = os.path.splitext(file_path)[0].replace("/", ".").replace("\\", ".")
        new_module = os.path.splitext(new_path)[0].replace("/", ".").replace("\\", ".")

        # Find files that import this module
        importing_files = find_files_importing(old_module)

        rename_plan.append(
            {"old_path": file_path, "new_path": new_path, "reason": reason, "importing_files": importing_files}
        )

        for importing_file in importing_files:
            import_updates.append({"file": importing_file, "old_import": old_module, "new_import": new_module})

    # Show plan
    print(f"\n📝 Rename Plan ({len(rename_plan)} files):")
    for item in rename_plan:
        print(f"  {item['old_path']} -> {item['new_path']}")
        print(f"    Reason: {item['reason']}")
        print(f"    Import updates: {len(item['importing_files'])} files")

    if args.write:
        print("\n🔄 Executing renames...")

        # Execute renames
        for item in rename_plan:
            try:
                os.rename(item["old_path"], item["new_path"])
                print(f"  ✅ Renamed: {item['old_path']} -> {item['new_path']}")
            except Exception as e:
                print(f"  ❌ Failed to rename {item['old_path']}: {e}")

        # Update imports
        print("\n🔄 Updating imports...")
        updated_imports = 0

        for update in import_updates:
            if update_imports_in_file(update["file"], update["old_import"], update["new_import"]):
                updated_imports += 1
                print(f"  ✅ Updated imports in: {update['file']}")
            else:
                print(f"  ⚠️  Failed to update imports in: {update['file']}")

        print("\n📊 Shadow fix complete:")
        print(f"  - Files renamed: {len(rename_plan)}")
        print(f"  - Import updates: {updated_imports}")

        # Create migration map
        migration_map = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "renames": rename_plan,
            "import_updates": import_updates,
        }

        with open("artifacts/shadow_migration_map.json", "w") as f:
            json.dump(migration_map, f, indent=2)

        print("  - Migration map saved: artifacts/shadow_migration_map.json")

    else:
        print("\n📊 Shadow fix plan:")
        print(f"  - Files to rename: {len(rename_plan)}")
        print(f"  - Import updates: {len(import_updates)}")
        print("  - Dry run mode: No changes made")

    # JSON output
    if args.json:
        results = {
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "shadow_files_found": len(shadow_files),
            "rename_plan": rename_plan,
            "import_updates": import_updates,
            "dry_run": args.dry_run,
        }
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
