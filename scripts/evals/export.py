#!/usr/bin/env python3
"""
Evaluation System Export Script

Reads evals/manifest.yml and exports all required files for the evaluation system
into a single bundle directory. This creates a self-contained package that can
be ingested into the code corpus without breaking existing imports.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load the evaluation manifest YAML file."""
    with open(manifest_path) as f:
        return yaml.safe_load(f)


def resolve_glob_patterns(patterns: list[str], base_dir: Path) -> set[Path]:
    """Resolve glob patterns to actual file paths using git ls-files."""
    resolved_files = set()

    for pattern in patterns:
        try:
            # Use git ls-files to resolve patterns (respects .gitignore)
            cmd = ["git", "ls-files", pattern]
            result = subprocess.run(cmd, cwd=base_dir, capture_output=True, text=True, check=True)

            for file_path in result.stdout.strip().split("\n"):
                if file_path:  # Skip empty lines
                    full_path = base_dir / file_path
                    if full_path.exists():
                        resolved_files.add(full_path)

        except subprocess.CalledProcessError:
            # If git ls-files fails, fall back to pathlib glob
            for path in base_dir.glob(pattern):
                if path.is_file():
                    resolved_files.add(path)

    return resolved_files


def should_include_file(file_path: Path, include_patterns: list[str], exclusions: list[str]) -> bool:
    """Check if a file should be included based on patterns and exclusions."""
    file_str = str(file_path)

    # Check exclusions first
    for exclusion in exclusions:
        if file_path.match(exclusion):
            return False

    # Check include patterns
    for pattern in include_patterns:
        if file_path.match(pattern):
            return True

    return False


def export_evaluation_bundle(manifest_path: Path, output_dir: Path, entrypoint: str = "clean_dspy") -> None:
    """Export evaluation system files based on manifest."""
    manifest = load_manifest(manifest_path)
    base_dir = manifest_path.parent.parent  # Project root

    if entrypoint not in manifest["entrypoints"]:
        raise ValueError(f"Entrypoint '{entrypoint}' not found in manifest")

    entrypoint_config = manifest["entrypoints"][entrypoint]
    include_patterns = manifest.get("include_patterns", ["**/*"])
    exclusions = manifest.get("exclusions", [])

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Track all files to copy
    all_files = set()

    # Process each category (code, config, data, output)
    for category in ["code", "config", "data", "output"]:
        if category in entrypoint_config:
            patterns = entrypoint_config[category]
            if isinstance(patterns, list):
                category_files = resolve_glob_patterns(patterns, base_dir)
                all_files.update(category_files)
                print(f"📁 {category}: {len(category_files)} files")

    # Filter files based on include/exclude patterns
    filtered_files = set()
    for file_path in all_files:
        if should_include_file(file_path, include_patterns, exclusions):
            filtered_files.add(file_path)

    print(f"📦 Total files to export: {len(filtered_files)}")

    # Copy files to output directory, preserving directory structure
    copied_count = 0
    for file_path in filtered_files:
        # Calculate relative path from project root
        rel_path = file_path.relative_to(base_dir)
        dest_path = output_dir / rel_path

        # Create destination directory
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(file_path, dest_path)
        copied_count += 1

        if copied_count % 50 == 0:
            print(f"   Copied {copied_count}/{len(filtered_files)} files...")

    print(f"✅ Export complete: {copied_count} files copied to {output_dir}")

    # Create a summary file
    summary_path = output_dir / "export_summary.txt"
    with open(summary_path, "w") as f:
        f.write("Evaluation System Export Summary\n")
        f.write("================================\n\n")
        f.write(f"Entrypoint: {entrypoint}\n")
        f.write(f"Export Date: {subprocess.check_output(['date'], text=True).strip()}\n")
        f.write(f"Total Files: {copied_count}\n\n")
        f.write("Categories:\n")
        for category in ["code", "config", "data", "output"]:
            if category in entrypoint_config:
                patterns = entrypoint_config[category]
                if isinstance(patterns, list):
                    category_files = resolve_glob_patterns(patterns, base_dir)
                    filtered_category = [
                        f for f in category_files if should_include_file(f, include_patterns, exclusions)
                    ]
                    f.write(f"  {category}: {len(filtered_category)} files\n")
        f.write("\nFiles:\n")
        for file_path in sorted(filtered_files):
            f.write(f"  {file_path.relative_to(base_dir)}\n")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Export evaluation system bundle")
    parser.add_argument("--manifest", type=Path, default=Path("evals/manifest.yml"), help="Path to manifest file")
    parser.add_argument("--output", type=Path, default=Path("evals_export"), help="Output directory for bundle")
    parser.add_argument("--entrypoint", default="clean_dspy", help="Entrypoint to export")
    parser.add_argument("--clean", action="store_true", help="Clean output directory before export")

    args = parser.parse_args()

    # Validate manifest exists
    if not args.manifest.exists():
        print(f"❌ Manifest file not found: {args.manifest}")
        return 1

    # Clean output directory if requested
    if args.clean and args.output.exists():
        shutil.rmtree(args.output)
        print(f"🧹 Cleaned output directory: {args.output}")

    try:
        export_evaluation_bundle(args.manifest, args.output, args.entrypoint)
        return 0
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
