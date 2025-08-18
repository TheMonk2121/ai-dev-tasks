#!/usr/bin/env python3.12
"""
Fix ambiguous Unicode characters that cause RUF001 errors.

This script replaces Unicode characters with their ASCII equivalents:
- Non-breaking hyphen (-) → hyphen (-)
- Information source (i) → i
- En dash (-) → hyphen (-)
- Em dash (-) → hyphen (-)
- Multiplication sign (x) → x
- Warning sign (!) → !
- Check mark (OK) → OK
- Cross mark (X) → X
- Figure dash (-) → hyphen (-)
"""

import sys
from pathlib import Path

# Unicode character mappings (using escape sequences to avoid RUF001)
UNICODE_REPLACEMENTS = {
    # Hyphens and dashes
    "\u2011": "-",  # Non-breaking hyphen
    "\u2013": "-",  # En dash
    "\u2014": "-",  # Em dash
    "\u2012": "-",  # Figure dash
    # Symbols
    "\u2139": "i",  # Information source
    "\u26a0": "!",  # Warning sign
    "\u2705": "OK",  # Check mark
    "\u274c": "X",  # Cross mark
    "\u00d7": "x",  # Multiplication sign
}

# File patterns to process
INCLUDE_PATTERNS = [
    "*.py",
    "*.md",
    "*.txt",
    "*.yml",
    "*.yaml",
    "*.json",
    "*.sh",
]

# Directories to exclude
EXCLUDE_DIRS = {
    "venv",
    "node_modules",
    "site-packages",
    ".pytest_cache",
    "__pycache__",
    ".git",
    "600_archives",
}


def should_process_file(file_path: Path) -> bool:
    """Check if file should be processed."""
    # Check if file matches include patterns
    if not any(file_path.match(pattern) for pattern in INCLUDE_PATTERNS):
        return False

    # Check if file is in excluded directory
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    return True


def fix_unicode_in_file(file_path: Path) -> tuple[bool, list[str]]:
    """Fix Unicode characters in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = []

        # Apply all replacements
        for unicode_char, ascii_char in UNICODE_REPLACEMENTS.items():
            if unicode_char in content:
                old_content = content
                content = content.replace(unicode_char, ascii_char)
                if content != old_content:
                    changes.append(f"  {unicode_char} → {ascii_char}")

        # Write back if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []


def find_files_to_process(root_dir: Path) -> list[Path]:
    """Find all files that should be processed."""
    files = []

    for file_path in root_dir.rglob("*"):
        if file_path.is_file() and should_process_file(file_path):
            files.append(file_path)

    return files


def main():
    """Main function."""
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
    else:
        target_path = Path(".")

    if not target_path.exists():
        print(f"Error: Path {target_path} does not exist")
        sys.exit(1)

    print(f"🔍 Scanning for Unicode characters in {target_path}")
    print(f"📝 Processing files: {', '.join(INCLUDE_PATTERNS)}")
    print(f"🚫 Excluding directories: {', '.join(EXCLUDE_DIRS)}")
    print()

    if target_path.is_file():
        files_to_process = [target_path]
    else:
        files_to_process = find_files_to_process(target_path)

    print(f"📁 Found {len(files_to_process)} files to process")
    print()

    fixed_files = 0
    total_changes = 0

    for file_path in files_to_process:
        was_fixed, changes = fix_unicode_in_file(file_path)

        if was_fixed:
            fixed_files += 1
            total_changes += len(changes)
            print(f"OK Fixed {file_path}")
            for change in changes:
                print(change)
            print()

    print("🎉 Summary:")
    print(f"   Files processed: {len(files_to_process)}")
    print(f"   Files fixed: {fixed_files}")
    print(f"   Total changes: {total_changes}")

    if fixed_files > 0:
        print("\n💡 Run 'ruff check --select RUF001' to verify fixes")


if __name__ == "__main__":
    main()
