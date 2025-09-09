#!/usr/bin/env python3
"""
Clean up ephemeral metrics files that accumulate during development and testing.

This script removes zero-byte JSON/JSONL files and optionally quarantines invalid JSON files
to reduce noise in test runs and keep the metrics directory clean.
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import List, Tuple


def find_zero_byte_files(directories: List[str]) -> List[Path]:
    """Find all zero-byte JSON/JSONL files in the specified directories."""
    zero_byte_files = []

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*.json"):
            if file_path.stat().st_size == 0:
                zero_byte_files.append(file_path)

        for file_path in dir_path.rglob("*.jsonl"):
            if file_path.stat().st_size == 0:
                zero_byte_files.append(file_path)

    return zero_byte_files


def find_invalid_json_files(directories: List[str]) -> List[Path]:
    """Find JSON/JSONL files with invalid JSON content."""
    invalid_files = []

    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue

        for file_path in dir_path.rglob("*.json"):
            if file_path.stat().st_size == 0:
                continue  # Skip zero-byte files (handled separately)

            try:
                with open(file_path, "r") as f:
                    json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                invalid_files.append(file_path)

        for file_path in dir_path.rglob("*.jsonl"):
            if file_path.stat().st_size == 0:
                continue  # Skip zero-byte files (handled separately)

            try:
                with open(file_path, "r") as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():  # Skip empty lines
                            json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                invalid_files.append(file_path)

    return invalid_files


def quarantine_file(file_path: Path, quarantine_dir: Path) -> None:
    """Move a file to the quarantine directory."""
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    # Create a unique name to avoid conflicts
    counter = 1
    base_name = file_path.name
    while (quarantine_dir / base_name).exists():
        name_parts = file_path.stem, counter, file_path.suffix
        base_name = f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
        counter += 1

    quarantine_path = quarantine_dir / base_name
    shutil.move(str(file_path), str(quarantine_path))
    print(f"  Quarantined: {file_path} → {quarantine_path}")


def main():
    parser = argparse.ArgumentParser(description="Clean up ephemeral metrics files")
    parser.add_argument(
        "--directories",
        nargs="+",
        default=["metrics", "datasets"],
        help="Directories to clean (default: metrics datasets)",
    )
    parser.add_argument(
        "--quarantine-invalid",
        action="store_true",
        help="Move invalid JSON files to quarantine directory instead of deleting",
    )
    parser.add_argument("--apply", action="store_true", help="Actually perform the cleanup (default is dry-run)")
    parser.add_argument(
        "--quarantine-dir",
        default="metrics/_invalid",
        help="Directory for quarantined files (default: metrics/_invalid)",
    )

    args = parser.parse_args()

    print(f"🧹 Cleaning ephemeral metrics in: {', '.join(args.directories)}")
    if not args.apply:
        print("🔍 DRY RUN MODE - use --apply to actually perform cleanup")

    # Find zero-byte files
    zero_byte_files = find_zero_byte_files(args.directories)
    print(f"\n📊 Found {len(zero_byte_files)} zero-byte JSON/JSONL files:")

    for file_path in zero_byte_files:
        print(f"  {file_path}")
        if args.apply:
            file_path.unlink()
            print("    Deleted")

    # Find invalid JSON files
    invalid_files = find_invalid_json_files(args.directories)
    print(f"\n⚠️  Found {len(invalid_files)} invalid JSON/JSONL files:")

    for file_path in invalid_files:
        print(f"  {file_path}")
        if args.apply:
            if args.quarantine_invalid:
                quarantine_file(file_path, Path(args.quarantine_dir))
            else:
                file_path.unlink()
                print("    Deleted")

    # Summary
    total_files = len(zero_byte_files) + len(invalid_files)
    if args.apply:
        print(f"\n✅ Cleanup complete: {total_files} files processed")
        if args.quarantine_invalid and invalid_files:
            print(f"   Quarantined {len(invalid_files)} invalid files to {args.quarantine_dir}")
    else:
        print(f"\n📋 Would process {total_files} files (use --apply to execute)")

    return 0


if __name__ == "__main__":
    exit(main())
