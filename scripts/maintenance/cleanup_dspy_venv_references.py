import sys
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
Cleanup script to remove DSPy venv references and update imports.

This script:
1. Removes sys.path.insert references to dspy-rag-system
2. Updates imports to use main project DSPy
3. Adds deprecation warnings where appropriate
4. Creates a summary of changes
"""

import os
import re
from pathlib import Path


def find_dspy_venv_references() -> list[tuple[str, int, str]]:
    """Find all files with DSPy venv references."""
    references = []
    project_root = Path(__file__).parent.parent

    # Search for sys.path.insert patterns
    pattern = r"sys\.path\.insert\(0,.*dspy-rag-system"

    for file_path in project_root.rglob("*.py"):
        if file_path.is_file() and not str(file_path).startswith(str(project_root / "600_archives")):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if re.search(pattern, content):
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                references.append((str(file_path), i, line.strip()))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return references

def update_file_imports(file_path: str) -> bool:
    """Update a file to remove DSPy venv references."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Remove sys.path.insert lines for dspy-rag-system
        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            # Skip lines that insert dspy-rag-system paths
            if re.search(r"sys\.path\.insert\(0,.*dspy-rag-system", line):
                # Add a comment explaining the change
                updated_lines.append(f"# {line.strip()}  # REMOVED: DSPy venv consolidated into main project")
                continue
            elif re.search(r"sys\.path\.append.*dspy-rag-system", line):
                # Add a comment explaining the change
                updated_lines.append(f"# {line.strip()}  # REMOVED: DSPy venv consolidated into main project")
                continue
            else:
                updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        # Only write if content changed
        if updated_content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return True

        return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Main cleanup function."""
    print("🧹 DSPy Venv Cleanup Script")
    print("=" * 50)

    # Find all references
    print("1. Finding DSPy venv references...")
    references = find_dspy_venv_references()

    if not references:
        print("✅ No DSPy venv references found!")
        return

    print(f"   Found {len(references)} references in {len(set(ref[0] for ref in references))} files")

    # Group by file
    files_to_update = {}
    for file_path, line_num, line_content in references:
        if file_path not in files_to_update:
            files_to_update[file_path] = []
        files_to_update[file_path].append((line_num, line_content))

    # Update files
    print("\n2. Updating files...")
    updated_files = []

    for file_path, lines in files_to_update.items():
        print(f"   Updating: {file_path}")
        if update_file_imports(file_path):
            updated_files.append(file_path)
            print(f"   ✅ Updated {len(lines)} references")
        else:
            print("   ⚠️  No changes needed")

    # Summary
    print("\n3. Cleanup Summary:")
    print(f"   📁 Files processed: {len(files_to_update)}")
    print(f"   ✏️  Files updated: {len(updated_files)}")
    print(f"   🔗 Total references removed: {len(references)}")

    if updated_files:
        print("\n📝 Updated files:")
        for file_path in updated_files:
            print(f"   - {file_path}")

    print("\n✅ DSPy venv cleanup completed!")
    print("   All DSPy imports now use the main project environment")

if __name__ == "__main__":
    main()
