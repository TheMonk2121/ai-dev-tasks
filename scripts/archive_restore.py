#!/usr/bin/env python3.12.123.11
"""
Archive Restore - Restore archive files to immutable snapshots and create errata.

This script reads validator_report.json + archive_manifest.json and restores
violating archive files to their recorded blob state, creating errata files
for any intended changes.
"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime


def load_manifest() -> dict:
    """Load archive manifest."""
    manifest_path = "data/archive_manifest.json"

    if not os.path.exists(manifest_path):
        print("❌ Archive manifest not found. Run archive_manifest_rebuild.py first.")
        sys.exit(1)

    with open(manifest_path) as f:
        return json.load(f)


def load_validator_report() -> dict:
    """Load validator report."""
    report_path = "validator_report.json"

    if not os.path.exists(report_path):
        print("❌ Validator report not found. Run validator first.")
        sys.exit(1)

    with open(report_path) as f:
        return json.load(f)


def get_blob_content(blob_sha: str) -> str | None:
    """Get content of a git blob."""
    try:
        result = subprocess.run(["git", "show", blob_sha], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def normalize_content(content: str) -> str:
    """Normalize content for comparison (LF, trim whitespace, etc.)."""
    # Convert to LF line endings
    content = content.replace("\r\n", "\n")
    # Trim trailing whitespace
    lines = [line.rstrip() for line in content.split("\n")]
    # Remove trailing empty lines
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def create_errata_file(
    archive_path: str, manifest_entry: dict, current_content: str, blob_content: str
) -> tuple[str, str]:
    """Create an errata file for changes to an archive file."""
    # Create errata directory structure
    relative_path = archive_path.replace("600_archives/", "")
    errata_dir = os.path.join("200_errata", os.path.dirname(relative_path))
    os.makedirs(errata_dir, exist_ok=True)

    # Create errata filename
    base_name = os.path.splitext(os.path.basename(relative_path))[0]
    errata_path = os.path.join(errata_dir, f"{base_name}.errata.md")

    # Get git blame info for context
    try:
        blame_result = subprocess.run(
            ["git", "blame", "--porcelain", archive_path], capture_output=True, text=True, check=True
        )
        # Extract author from blame (simplified)
        lines = blame_result.stdout.split("\n")
        author = "Unknown"
        for line in lines:
            if line.startswith("author "):
                author = line[7:]
                break
    except subprocess.CalledProcessError:
        author = "Unknown"

    # Create errata content
    errata_content = f"""# Errata: {archive_path}

**Source**: {archive_path}
**Recorded Commit**: {manifest_entry['introduced_commit']}
**Recorded Date**: {manifest_entry['recorded_at']}
**Author**: {author}
**Created**: {datetime.now(UTC).isoformat()}Z

## Changes Made

The original archived file has been modified. This errata documents the intended changes.

### Original Content (Blob {manifest_entry['blob_sha'][:8]})

```markdown
{blob_content}
```

### Current Content

```markdown
{current_content}
```

### Intended Changes

*Document the specific changes that were intended to be made to the archive file.*

## Notes

- This errata preserves the original archived content
- The archive file has been restored to its immutable snapshot
- Future changes should be made to this errata file, not the archive
"""

    return errata_path, errata_content


def update_errata_index(errata_path: str, archive_path: str):
    """Update the errata index with a new entry."""
    index_path = "400_guides/ERRATA_INDEX.md"

    # Create index if it doesn't exist
    if not os.path.exists(index_path):
        index_content = """# Errata Index

This file tracks errata for archived content.

| Archive File | Errata File | Created | Status |
|---|---|---|---|
"""
    else:
        with open(index_path) as f:
            index_content = f.read()

    # Add new entry
    timestamp = datetime.now(UTC).isoformat()[:10]
    new_entry = f"| {archive_path} | [{os.path.basename(errata_path)}]({errata_path}) | {timestamp} | Active |\n"

    # Insert after header
    lines = index_content.split("\n")
    header_end = 0
    for i, line in enumerate(lines):
        if line.startswith("| Archive File |"):
            header_end = i + 2  # Skip header and separator
            break

    lines.insert(header_end, new_entry)

    with open(index_path, "w") as f:
        f.write("\n".join(lines))


def main():
    """Main function to restore archive files."""
    import argparse

    parser = argparse.ArgumentParser(description="Restore archive files to immutable snapshots")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--write", action="store_true", help="Actually restore files and create errata")

    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print("❌ Must specify --dry-run or --write")
        sys.exit(1)

    print("🔍 Loading archive manifest and validator report...")

    # Load data
    manifest = load_manifest()
    report = load_validator_report()

    # Get archive violations
    archive_violations = report.get("impacted_files", {}).get("archive", [])
    print(f"📋 Found {len(archive_violations)} archive violations")

    if not archive_violations:
        print("✅ No archive violations found")
        return

    # Process each violation
    restored_files = []
    errata_files = []

    for archive_path in archive_violations:
        # Convert absolute path to relative if needed
        if archive_path.startswith("/"):
            # Extract relative path from absolute path
            cwd = os.getcwd()
            if archive_path.startswith(cwd):
                archive_path = archive_path[len(cwd) :].lstrip("/")
            else:
                print(f"⚠️  {archive_path} not in current directory, skipping")
                continue

        if archive_path not in manifest["files"]:
            print(f"⚠️  {archive_path} not in manifest, skipping")
            continue

        manifest_entry = manifest["files"][archive_path]
        blob_sha = manifest_entry["blob_sha"]

        print(f"🔍 Processing: {archive_path}")

        # Get current content
        if os.path.exists(archive_path):
            with open(archive_path, encoding="utf-8") as f:
                current_content = f.read()
        else:
            current_content = ""

        # Get blob content
        blob_content = get_blob_content(blob_sha)
        if blob_content is None:
            print(f"  ⚠️  Could not get blob content for {blob_sha}")
            continue

        # Normalize for comparison
        current_normalized = normalize_content(current_content)
        blob_normalized = normalize_content(blob_content)

        if current_normalized == blob_normalized:
            print("  ✅ Content matches blob (normalized)")
            continue

        print(f"  🔄 Content differs from blob {blob_sha[:8]}")

        if args.write:
            # Restore to blob content
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(blob_content)
            restored_files.append(archive_path)

            # Create errata file
            errata_path, errata_content = create_errata_file(
                archive_path, manifest_entry, current_content, blob_content
            )
            with open(errata_path, "w", encoding="utf-8") as f:
                f.write(errata_content)
            errata_files.append(errata_path)

            # Update errata index
            update_errata_index(errata_path, archive_path)

            print(f"  ✅ Restored and created errata: {errata_path}")
        else:
            print("  📝 Would restore and create errata")
            restored_files.append(archive_path)

    # Summary
    print("\n📊 Archive restore complete:")
    print(f"  - Files to restore: {len(restored_files)}")
    print(f"  - Errata files created: {len(errata_files)}")

    if args.write:
        print("  - Changes applied: ✅")
    else:
        print("  - Dry run mode: No changes made")


if __name__ == "__main__":
    main()
