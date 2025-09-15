from __future__ import annotations

import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

#!/usr/bin/env python3
"""
Duplicate File Finder - Content-Based Analysis

Finds duplicate files using SHA-256 hashes and provides detailed analysis.
Useful for repository cleanup and maintenance.

Usage: python3 scripts/find_duplicates.py [--path .] [--extensions md,txt,py] [--exclude venv,node_modules]
"""

class DuplicateFinder:
    def __init__(self, path: str = ".", extensions: list[str] | None = None, exclude_patterns: list[str] | None = None):
        self.root_path = Path(path)
        self.extensions = extensions or ["md", "txt", "py"]
        self.exclude_patterns = exclude_patterns or ["venv", "node_modules", "__pycache__", ".git"]

        self.hash_to_files = defaultdict(list)
        self.file_sizes = {}
        self.total_files = 0
        self.total_size = 0

    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        return any(pattern in str(file_path) for pattern in self.exclude_patterns)

    def calculate_file_hash(self, file_path: Path) -> str | None:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None

    def scan_files(self) -> None:
        """Scan all files and build hash-to-files mapping."""
        print(f"Scanning files in {self.root_path}...")

        for ext in self.extensions:
            pattern = f"**/*.{ext}"
            for file_path in self.root_path.rglob(pattern):
                if self.should_exclude(file_path):
                    continue

                if file_path.is_file():
                    self.total_files += 1
                    file_size = file_path.stat().st_size
                    self.total_size += file_size
                    self.file_sizes[file_path] = file_size

                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        self.hash_to_files[file_hash].append(file_path)

    def analyze_duplicates(self) -> dict[str, list[Path]]:
        """Find files with identical content."""
        duplicates = {hash_val: files for hash_val, files in self.hash_to_files.items() if len(files) > 1}
        return duplicates

    def categorize_files(self, files: list[Path]) -> dict[str, list[Path]]:
        """Categorize files by location (main, archives, etc.)."""
        categories = {"main": [], "archives": [], "backup": [], "legacy": [], "other": []}

        for file_path in files:
            if any(pattern in str(file_path) for pattern in ["archives", "backup", "legacy"]):
                if "archives" in str(file_path):
                    categories["archives"].append(file_path)
                elif "backup" in str(file_path):
                    categories["backup"].append(file_path)
                elif "legacy" in str(file_path):
                    categories["legacy"].append(file_path)
                else:
                    categories["other"].append(file_path)
            else:
                categories["main"].append(file_path)

        return categories

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def print_summary(self) -> None:
        """Print scanning summary."""
        print("\n📊 SCANNING SUMMARY")
        print("=" * 50)
        print(f"Total files scanned: {self.total_files}")
        print(f"Total size: {self.format_size(self.total_size)}")
        print(f"Unique hashes: {len(self.hash_to_files)}")
        print(f"Duplicate groups: {len(self.analyze_duplicates())}")

    def print_duplicate_analysis(self, duplicates: dict[str, list[Path]]) -> None:
        """Print detailed duplicate analysis."""
        if not duplicates:
            print("\n✅ No duplicate files found!")
            return

        print("\n🔍 DUPLICATE ANALYSIS")
        print("=" * 50)

        total_duplicate_size = 0
        for hash_val, files in duplicates.items():
            categories = self.categorize_files(files)

            print(f"\n📁 Duplicate Group (Hash: {hash_val[:8]}...)")
            print(f"   Files: {len(files)}")

            # Calculate size for this group
            group_size = sum(self.file_sizes.get(f, 0) for f in files)
            total_duplicate_size += group_size * (len(files) - 1)  # Size of duplicates only

            for category, category_files in categories.items():
                if category_files:
                    print(f"   {category.title()}:")
                    for file_path in category_files:
                        size = self.format_size(self.file_sizes.get(file_path, 0))
                        print(f"     - {file_path} ({size})")

            # Suggest which files to keep/archive
            if categories["main"]:
                keep_file = categories["main"][0]
                archive_files = (
                    categories["main"][1:] + categories["archives"] + categories["backup"] + categories["legacy"]
                )
                print(f"   💡 Suggestion: Keep {keep_file}")
                if archive_files:
                    print(f"   📦 Archive: {len(archive_files)} files")
            else:
                keep_file = files[0]
                archive_files = files[1:]
                print(f"   💡 Suggestion: Keep {keep_file}")
                print(f"   📦 Archive: {len(archive_files)} files")

        print("\n💰 SPACE SAVINGS")
        print("=" * 50)
        print(f"Potential space saved: {self.format_size(total_duplicate_size)}")
        print(f"Duplicate files: {sum(len(files) - 1 for files in duplicates.values())}")

    def generate_cleanup_script(
        self, duplicates: dict[str, list[Path]], output_file: str = "cleanup_duplicates.sh"
    ) -> None:
        """Generate a shell script to clean up duplicates."""
        if not duplicates:
            return

        script_content = ["#!/bin/bash", "# Auto-generated duplicate cleanup script", ""]

        for hash_val, files in duplicates.items():
            categories = self.categorize_files(files)

            if categories["main"]:
                keep_file = categories["main"][0]
                archive_files = (
                    categories["main"][1:] + categories["archives"] + categories["backup"] + categories["legacy"]
                )
            else:
                keep_file = files[0]
                archive_files = files[1:]

            script_content.append(f"# Duplicate group: {hash_val[:8]}...")
            script_content.append(f"# Keep: {keep_file}")

            for archive_file in archive_files:
                if archive_file.exists():
                    legacy_path = f"docs/legacy/{archive_file.name}"
                    script_content.append("mkdir -p docs/legacy")
                    script_content.append(f"mv '{archive_file}' '{legacy_path}'")

            script_content.append("")

        with open(output_file, "w") as f:
            f.write("\n".join(script_content))

        print(f"\n📝 Generated cleanup script: {output_file}")
        print(f"   Run: chmod +x {output_file} && ./{output_file}")

def main():
    parser = argparse.ArgumentParser(description="Find duplicate files using content hashes")
    parser.add_argument("--path", default=".", help="Root path to scan")
    parser.add_argument("--extensions", default="md,txt,py", help="File extensions to scan (comma-separated)")
    parser.add_argument(
        "--exclude", default="venv,node_modules,__pycache__,.git", help="Patterns to exclude (comma-separated)"
    )
    parser.add_argument("--generate-script", action="store_true", help="Generate cleanup script")

    args = parser.parse_args()

    # Parse arguments
    extensions = [ext.strip() for ext in args.extensions.split(",")]
    exclude_patterns = [pattern.strip() for pattern in args.exclude.split(",")]

    # Initialize finder
    finder = DuplicateFinder(path=args.path, extensions=extensions, exclude_patterns=exclude_patterns)

    # Scan and analyze
    finder.scan_files()
    duplicates = finder.analyze_duplicates()

    # Print results
    finder.print_summary()
    finder.print_duplicate_analysis(duplicates)

    # Generate cleanup script if requested
    if args.generate_script and duplicates:
        finder.generate_cleanup_script(duplicates)

    # Exit with appropriate code
    sys.exit(1 if duplicates else 0)

if __name__ == "__main__":
    main()
