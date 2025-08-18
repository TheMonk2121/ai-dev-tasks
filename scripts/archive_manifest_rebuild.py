#!/usr/bin/env python3.12.123.11
"""
Archive Manifest Rebuild - Build/refresh manifest by discovering first-add commits.

This script discovers the first commit that added each file under 600_archives/
and records the blob SHA for immutable snapshots.
"""

import json
import os
import subprocess
from datetime import datetime, timezone, UTC
from typing import Optional


def get_archive_files() -> list[str]:
    """Get all files under 600_archives/ directory."""
    archive_files = []

    for root, _, files in os.walk("600_archives"):
        for file in files:
            if file.endswith((".md", ".py", ".txt", ".json", ".yaml", ".yml")):
                file_path = os.path.join(root, file)
                archive_files.append(file_path)

    return archive_files


def get_introduced_commit(file_path: str) -> str | None:
    """Get the first commit that introduced a file."""
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        commits = result.stdout.strip().split("\n")
        return commits[-1] if commits else None  # Last (oldest) commit
    except subprocess.CalledProcessError:
        return None


def get_blob_sha(commit: str, file_path: str) -> str | None:
    """Get the blob SHA for a file at a specific commit."""
    try:
        result = subprocess.run(["git", "ls-tree", commit, file_path], capture_output=True, text=True, check=True)
        # Format: 100644 blob <sha> <filename>
        parts = result.stdout.strip().split()
        return parts[2] if len(parts) >= 3 else None
    except subprocess.CalledProcessError:
        return None


def load_manifest() -> dict:
    """Load existing manifest."""
    manifest_path = "data/archive_manifest.json"

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path) as f:
                return json.load(f)
        except Exception:
            pass

    return {
        "schema_version": "1.0",
        "generated_at": "",
        "description": "Immutable snapshots of archived files",
        "files": {},
    }


def save_manifest(manifest: dict):
    """Save manifest to file."""
    manifest["generated_at"] = datetime.now(UTC).isoformat() + "Z"

    with open("data/archive_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


def main():
    """Main function to rebuild archive manifest."""
    print("🔍 Rebuilding archive manifest...")

    # Load existing manifest
    manifest = load_manifest()
    existing_files = set(manifest.get("files", {}).keys())

    # Get all archive files
    archive_files = get_archive_files()
    print(f"📁 Found {len(archive_files)} files in 600_archives/")

    # Process each file
    new_entries = 0
    enrolled_entries = 0

    for file_path in archive_files:
        if file_path in existing_files:
            print(f"  ⏭️  Skipping existing: {file_path}")
            continue

        print(f"  🔍 Processing: {file_path}")

        # Get introduced commit
        introduced_commit = get_introduced_commit(file_path)
        if not introduced_commit:
            print(f"    ⚠️  Could not find introduced commit for {file_path}")
            continue

        # Get blob SHA
        blob_sha = get_blob_sha(introduced_commit, file_path)
        if not blob_sha:
            print(f"    ⚠️  Could not find blob SHA for {file_path}")
            continue

        # Add to manifest
        manifest["files"][file_path] = {
            "path": file_path,
            "introduced_commit": introduced_commit,
            "blob_sha": blob_sha,
            "recorded_at": datetime.now(UTC).isoformat() + "Z",
            "enrollment": True,  # Mark as auto-enrolled
        }

        new_entries += 1
        enrolled_entries += 1
        print(f"    ✅ Enrolled: {introduced_commit[:8]} -> {blob_sha[:8]}")

    # Save manifest
    save_manifest(manifest)

    print("\n📊 Manifest rebuild complete:")
    print(f"  - New entries: {new_entries}")
    print(f"  - Auto-enrolled: {enrolled_entries}")
    print(f"  - Total files: {len(manifest['files'])}")
    print("  - Manifest saved: data/archive_manifest.json")


if __name__ == "__main__":
    main()
