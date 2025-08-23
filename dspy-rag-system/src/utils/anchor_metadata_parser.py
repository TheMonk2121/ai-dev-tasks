#!/usr/bin/env python3
"""
Anchor Metadata Parser

Extracts anchor metadata from HTML comments in Markdown content.
Maps to JSONB metadata for the memory rehydrator.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AnchorMetadata:
    """Structured anchor metadata"""

    anchor_key: Optional[str] = None
    anchor_priority: Optional[int] = None
    role_pins: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSONB storage"""
        result = {}
        if self.anchor_key:
            result["anchor_key"] = self.anchor_key
        if self.anchor_priority is not None:
            result["anchor_priority"] = self.anchor_priority
        if self.role_pins:
            result["role_pins"] = self.role_pins
        return result

# Canonical anchor keys that are always loaded first
CANONICAL_ANCHORS = {"tldr", "quick-start", "quick-links", "commands"}

# Valid roles for role pinning
VALID_ROLES = {"planner", "implementer", "researcher", "coder"}

# Default priorities for canonical anchors
DEFAULT_PRIORITIES = {"tldr": 0, "quick-start": 1, "quick-links": 2, "commands": 3}

def extract_anchor_metadata(content: str) -> AnchorMetadata:
    """
    Extract anchor metadata from HTML comments in Markdown content.

    Args:
        content: Markdown content with HTML comments

    Returns:
        AnchorMetadata object with extracted fields
    """
    metadata = AnchorMetadata()

    # Parse ANCHOR_KEY
    anchor_match = re.search(r"<!--\s*ANCHOR_KEY:\s*(\w+(?:-\w+)*)\s*-->", content, re.IGNORECASE)
    if anchor_match:
        key = anchor_match.group(1).lower()
        if key in CANONICAL_ANCHORS:
            metadata.anchor_key = key
            # Set default priority for canonical anchors
            metadata.anchor_priority = DEFAULT_PRIORITIES.get(key)
        else:
            # Custom anchor key - validate format
            if re.match(r"^[a-z0-9-]+$", key):
                metadata.anchor_key = key

    # Parse ANCHOR_PRIORITY
    priority_match = re.search(r"<!--\s*ANCHOR_PRIORITY:\s*(\d+)\s*-->", content, re.IGNORECASE)
    if priority_match:
        priority = int(priority_match.group(1))
        # Validate priority range (0-999)
        if 0 <= priority <= 999:
            metadata.anchor_priority = priority

    # Parse ROLE_PINS
    role_match = re.search(r"<!--\s*ROLE_PINS:\s*\[(.*?)\]\s*-->", content, re.IGNORECASE)
    if role_match:
        roles_str = role_match.group(1)
        # Parse comma-separated roles, handling quotes
        roles = []
        for role in re.findall(r'"([^"]+)"|\'([^\']+)\'|(\w+)', roles_str):
            role_name = next(r for r in role if r).strip().lower()
            if role_name in VALID_ROLES:
                roles.append(role_name)
        if roles:
            metadata.role_pins = roles

    return metadata

def validate_anchor_metadata(metadata: AnchorMetadata) -> List[str]:
    """
    Validate anchor metadata for consistency and correctness.

    Args:
        metadata: AnchorMetadata object to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Validate anchor_key
    if metadata.anchor_key:
        if metadata.anchor_key not in CANONICAL_ANCHORS:
            # Custom anchor key - check format
            if not re.match(r"^[a-z0-9-]+$", metadata.anchor_key):
                errors.append(f"Invalid anchor_key format: {metadata.anchor_key}")

    # Validate anchor_priority
    if metadata.anchor_priority is not None:
        if not (0 <= metadata.anchor_priority <= 999):
            errors.append(f"Invalid anchor_priority: {metadata.anchor_priority} (must be 0-999)")

    # Validate role_pins
    if metadata.role_pins:
        for role in metadata.role_pins:
            if role not in VALID_ROLES:
                errors.append(f"Invalid role in role_pins: {role}")

    # Validate canonical anchor priorities
    if metadata.anchor_key in CANONICAL_ANCHORS:
        expected_priority = DEFAULT_PRIORITIES.get(metadata.anchor_key)
        if metadata.anchor_priority is not None and metadata.anchor_priority != expected_priority:
            errors.append(f"Canonical anchor {metadata.anchor_key} should have priority {expected_priority}")

    return errors

def extract_anchor_metadata_from_file(file_path: str) -> AnchorMetadata:
    """
    Extract anchor metadata from a Markdown file.

    Args:
        file_path: Path to Markdown file

    Returns:
        AnchorMetadata object with extracted fields
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return extract_anchor_metadata(content)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return AnchorMetadata()

def batch_extract_metadata(file_paths: List[str]) -> Dict[str, AnchorMetadata]:
    """
    Extract anchor metadata from multiple files.

    Args:
        file_paths: List of file paths to process

    Returns:
        Dictionary mapping file paths to AnchorMetadata objects
    """
    results = {}
    for file_path in file_paths:
        metadata = extract_anchor_metadata_from_file(file_path)
        results[file_path] = metadata
    return results

def generate_metadata_report(file_paths: List[str]) -> Dict[str, Any]:
    """
    Generate a report of anchor metadata across files.

    Args:
        file_paths: List of file paths to analyze

    Returns:
        Report dictionary with statistics and validation results
    """
    results = batch_extract_metadata(file_paths)

    report = {
        "total_files": len(file_paths),
        "files_with_metadata": 0,
        "canonical_anchors": {},
        "custom_anchors": {},
        "role_pins": {},
        "validation_errors": [],
        "file_details": {},
    }

    for file_path, metadata in results.items():
        file_has_metadata = any([metadata.anchor_key, metadata.anchor_priority is not None, metadata.role_pins])

        if file_has_metadata:
            report["files_with_metadata"] += 1

            # Track anchor keys
            if metadata.anchor_key:
                if metadata.anchor_key in CANONICAL_ANCHORS:
                    if metadata.anchor_key not in report["canonical_anchors"]:
                        report["canonical_anchors"][metadata.anchor_key] = []
                    report["canonical_anchors"][metadata.anchor_key].append(file_path)
                else:
                    if metadata.anchor_key not in report["custom_anchors"]:
                        report["custom_anchors"][metadata.anchor_key] = []
                    report["custom_anchors"][metadata.anchor_key].append(file_path)

            # Track role pins
            if metadata.role_pins:
                for role in metadata.role_pins:
                    if role not in report["role_pins"]:
                        report["role_pins"][role] = []
                    report["role_pins"][role].append(file_path)

            # Validate metadata
            errors = validate_anchor_metadata(metadata)
            if errors:
                report["validation_errors"].extend([f"{file_path}: {error}" for error in errors])

        # Store file details
        report["file_details"][file_path] = {
            "has_metadata": file_has_metadata,
            "anchor_key": metadata.anchor_key,
            "anchor_priority": metadata.anchor_priority,
            "role_pins": metadata.role_pins,
            "validation_errors": validate_anchor_metadata(metadata),
        }

    return report

# CLI interface for testing and validation
def main():
    """CLI interface for anchor metadata parser"""
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Extract and validate anchor metadata from Markdown files")
    parser.add_argument("files", nargs="+", help="Markdown files to process")
    parser.add_argument("--validate", action="store_true", help="Validate metadata and report errors")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    # Check if files exist
    valid_files = []
    for file_path in args.files:
        if Path(file_path).exists():
            valid_files.append(file_path)
        else:
            print(f"Warning: File not found: {file_path}", file=sys.stderr)

    if not valid_files:
        print("No valid files found", file=sys.stderr)
        sys.exit(1)

    if args.report:
        # Generate detailed report
        report = generate_metadata_report(valid_files)

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("Anchor Metadata Report")
            print("=====================")
            print(f"Total files: {report['total_files']}")
            print(f"Files with metadata: {report['files_with_metadata']}")
            print()

            if report["canonical_anchors"]:
                print("Canonical Anchors:")
                for anchor, files in report["canonical_anchors"].items():
                    print(f"  {anchor}: {len(files)} files")
                    for file_path in files:
                        print(f"    - {file_path}")
                print()

            if report["custom_anchors"]:
                print("Custom Anchors:")
                for anchor, files in report["custom_anchors"].items():
                    print(f"  {anchor}: {len(files)} files")
                    for file_path in files:
                        print(f"    - {file_path}")
                print()

            if report["role_pins"]:
                print("Role Pins:")
                for role, files in report["role_pins"].items():
                    print(f"  {role}: {len(files)} files")
                    for file_path in files:
                        print(f"    - {file_path}")
                print()

            if report["validation_errors"]:
                print("Validation Errors:")
                for error in report["validation_errors"]:
                    print(f"  ❌ {error}")
                print()
            else:
                print("✅ No validation errors found")

    else:
        # Simple extraction
        for file_path in valid_files:
            metadata = extract_anchor_metadata_from_file(file_path)

            if args.json:
                result = {"file": file_path, "metadata": metadata.to_dict()}
                print(json.dumps(result))
            else:
                print(f"File: {file_path}")
                if metadata.anchor_key:
                    print(f"  Anchor Key: {metadata.anchor_key}")
                if metadata.anchor_priority is not None:
                    print(f"  Priority: {metadata.anchor_priority}")
                if metadata.role_pins:
                    print(f"  Role Pins: {metadata.role_pins}")

                if args.validate:
                    errors = validate_anchor_metadata(metadata)
                    if errors:
                        print("  Validation Errors:")
                        for error in errors:
                            print(f"    ❌ {error}")
                    else:
                        print("  ✅ Valid")
                print()

if __name__ == "__main__":
    main()
