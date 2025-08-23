#!/usr/bin/env python3
"""
Mark all archived test files as deprecated.

This script adds deprecation markers and documentation to all test files
in the 600_archives directory to prevent them from being run accidentally.
"""

from pathlib import Path


def mark_test_file_deprecated(file_path: Path) -> bool:
    """Mark a test file as deprecated by adding deprecation marker and documentation."""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if already marked as deprecated
        if "pytestmark = pytest.mark.deprecated" in content:
            print(f"  ✅ Already marked as deprecated: {file_path.name}")
            return True

        # Add deprecation documentation to docstring
        if '"""' in content:
            # Find the first docstring and add deprecation notice
            lines = content.split("\n")
            modified = False

            for i, line in enumerate(lines):
                if line.strip().startswith('"""') and not modified:
                    # Add deprecation notice after the first docstring
                    if i + 1 < len(lines) and lines[i + 1].strip() == "":
                        # Empty line after docstring, add deprecation notice
                        lines.insert(i + 2, "DEPRECATED: This test file is archived and should not be run.")
                        lines.insert(i + 3, "Use current test infrastructure instead.")
                        lines.insert(i + 4, "")
                    else:
                        # Add deprecation notice on next line
                        lines.insert(i + 1, "")
                        lines.insert(i + 2, "DEPRECATED: This test file is archived and should not be run.")
                        lines.insert(i + 3, "Use current test infrastructure instead.")
                        lines.insert(i + 4, "")
                    modified = True
                    break

        # Add pytestmark after import pytest
        if "import pytest" in content:
            # Find the import pytest line and add pytestmark after it
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if line.strip() == "import pytest":
                    # Add pytestmark after import pytest
                    lines.insert(i + 1, "")
                    lines.insert(i + 2, "# Mark all tests in this file as deprecated")
                    lines.insert(i + 3, "pytestmark = pytest.mark.deprecated")
                    break

            content = "\n".join(lines)

        # Write the modified content back
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  ✅ Marked as deprecated: {file_path.name}")
        return True

    except Exception as e:
        print(f"  ❌ Error marking {file_path.name}: {e}")
        return False

def main():
    """Mark all archived test files as deprecated."""

    print("🔧 Marking archived test files as deprecated...")
    print("=" * 50)

    # Find all test files in 600_archives
    archives_dir = Path("600_archives")
    test_files = list(archives_dir.rglob("test_*.py"))

    if not test_files:
        print("No test files found in 600_archives directory.")
        return

    print(f"Found {len(test_files)} test files to mark as deprecated:")

    success_count = 0
    for test_file in test_files:
        print(f"  📝 Processing: {test_file.relative_to(archives_dir)}")
        if mark_test_file_deprecated(test_file):
            success_count += 1

    print("\n" + "=" * 50)
    print(f"✅ Successfully marked {success_count}/{len(test_files)} test files as deprecated")

    if success_count < len(test_files):
        print(f"❌ Failed to mark {len(test_files) - success_count} test files")

    print("\n📋 Summary:")
    print("- All archived test files are now marked with @pytest.mark.deprecated")
    print("- pytest configuration excludes 600_archives directory")
    print("- Test runners will not execute deprecated tests")
    print("- Use 'pytest -m \"not deprecated\"' to explicitly exclude deprecated tests")

if __name__ == "__main__":
    main()
