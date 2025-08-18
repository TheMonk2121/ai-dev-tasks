#!/usr/bin/env python3
"""
README autofix tool - idempotent section insertion with markers.

Usage:
    python3 scripts/readme_autofix.py --dry-run  # Default: analyze only
    python3 scripts/readme_autofix.py --write    # Actually modify files
    python3 scripts/readme_autofix.py --scope 400_guides  # Limit scope
    python3 scripts/readme_autofix.py --root /path/to/repo  # Custom root
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from readme_consts import (
    AUTOFIX_MARKER_END,
    AUTOFIX_MARKER_START,
    OWNER_PATTERNS,
    README_IGNORE_SEGMENTS,
    README_SCOPE_DIRS,
    REQUIRED_SECTIONS,
    SECTION_TEMPLATES,
)


def discover_readme_files(root: str) -> List[str]:
    """Discover README files within scope."""
    readme_files = []
    root_path = Path(root)

    for scope_dir in README_SCOPE_DIRS:
        scope_path = root_path / scope_dir
        if not scope_path.exists():
            continue

        if scope_path.is_file():
            # Single file like 500_reference-cards.md
            if scope_path.name.lower().endswith((".md", ".txt")):
                readme_files.append(str(scope_path))
        else:
            # Directory - find all markdown files
            for file_path in scope_path.rglob("*.md"):
                # Skip ignored segments
                if any(segment in str(file_path) for segment in README_IGNORE_SEGMENTS):
                    continue
                readme_files.append(str(file_path))

    return sorted(readme_files)


def has_section_synonym(content: str, section_type: str) -> bool:
    """Check if content has any synonym for the required section."""
    synonyms = REQUIRED_SECTIONS[section_type]
    content_lower = content.lower()

    for synonym in synonyms:
        # Look for section headers with this synonym
        pattern = rf"^#+\s*{re.escape(synonym)}"
        if re.search(pattern, content_lower, re.MULTILINE):
            return True

    return False


def find_marker_block(content: str) -> Optional[Tuple[int, int]]:
    """Find existing autofix marker block, return (start, end) positions."""
    start_match = re.search(re.escape(AUTOFIX_MARKER_START), content)
    end_match = re.search(re.escape(AUTOFIX_MARKER_END), content)

    if start_match and end_match:
        return (start_match.start(), end_match.end())
    return None


def infer_owner(file_path: str) -> str:
    """Infer owner based on file path patterns."""
    # Extract the relative path from the full path
    path_parts = file_path.split(os.sep)
    for i, part in enumerate(path_parts):
        if part in OWNER_PATTERNS:
            return OWNER_PATTERNS[part]
        # Check for patterns with trailing slash
        if part + "/" in OWNER_PATTERNS:
            return OWNER_PATTERNS[part + "/"]
    return "TBD"


def get_missing_sections(content: str) -> Set[str]:
    """Identify which required sections are missing."""
    missing = set()

    # Remove marker block content before checking for sections
    marker_block = find_marker_block(content)
    if marker_block:
        start, end = marker_block
        content_without_marker = content[:start] + content[end:]
    else:
        content_without_marker = content

    for section_type in REQUIRED_SECTIONS:
        if not has_section_synonym(content_without_marker, section_type):
            missing.add(section_type)

    return missing


def build_marker_content(missing_sections: Set[str], file_path: str, write_mode: bool) -> str:
    """Build content for the autofix marker block."""
    lines = [AUTOFIX_MARKER_START]
    lines.append(f"# Auto-generated sections for {os.path.basename(file_path)}")
    lines.append(f"# Generated: {datetime.datetime.now().isoformat()}")

    if missing_sections:
        lines.append("")
        lines.append("## Missing sections to add:")
        for section in sorted(missing_sections):
            template = SECTION_TEMPLATES[section]

            if section == "owner":
                owner = infer_owner(file_path)
                if owner != "TBD":
                    template = template.replace("[Document owner/maintainer information]", owner)
            elif section == "last_reviewed" and write_mode:
                template = template.replace(
                    "[Date when this document was last reviewed]", datetime.date.today().isoformat()
                )

            lines.append("")
            lines.append(template)
    else:
        lines.append("")
        lines.append("All required sections present.")

    lines.append("")
    lines.append(AUTOFIX_MARKER_END)
    return "\n".join(lines)


def process_readme_file(file_path: str, write_mode: bool = False) -> Dict[str, Any]:
    """Process a single README file, return analysis results."""
    try:
        with open(file_path, encoding="utf-8", errors="strict") as f:
            content = f.read()
    except UnicodeDecodeError:
        return {
            "file": file_path,
            "error": "Unicode decode error - skipping binary-like file",
            "missing_sections": set(),
            "modified": False,
        }
    except FileNotFoundError:
        return {"file": file_path, "error": "File not found", "missing_sections": set(), "modified": False}

    missing_sections = get_missing_sections(content)
    marker_block = find_marker_block(content)

    # If no missing sections and no marker block, file is complete
    if not missing_sections and not marker_block:
        return {"file": file_path, "missing_sections": set(), "modified": False, "status": "complete"}

    # If no missing sections but has marker block, file is complete (marker can be removed)
    if not missing_sections and marker_block:
        if write_mode:
            # Remove the marker block
            start, end = marker_block
            new_content = content[:start].rstrip() + "\n" + content[end:].lstrip()
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                return {"file": file_path, "missing_sections": set(), "modified": True, "status": "cleaned"}
            else:
                return {"file": file_path, "missing_sections": set(), "modified": False, "status": "complete"}
        else:
            return {"file": file_path, "missing_sections": set(), "modified": False, "status": "complete"}

    if write_mode:
        marker_content = build_marker_content(missing_sections, file_path, write_mode)

        if marker_block:
            # Update existing marker block
            start, end = marker_block
            new_content = content[:start] + marker_content + content[end:]
        else:
            # Add new marker block at end
            new_content = content.rstrip() + "\n\n" + marker_content + "\n"

        # Only write if content actually changed (ignoring timestamp differences)
        # Normalize timestamps for comparison
        def normalize_timestamps(text):
            import re

            return re.sub(r"# Generated: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+", "# Generated: TIMESTAMP", text)

        normalized_new = normalize_timestamps(new_content)
        normalized_old = normalize_timestamps(content)

        if normalized_new != normalized_old:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return {"file": file_path, "missing_sections": missing_sections, "modified": True, "status": "updated"}
        else:
            return {"file": file_path, "missing_sections": missing_sections, "modified": False, "status": "no_change"}
    else:
        return {"file": file_path, "missing_sections": missing_sections, "modified": False, "status": "dry_run"}


def main():
    parser = argparse.ArgumentParser(description="README autofix tool")
    parser.add_argument("--write", action="store_true", help="Actually modify files (default: dry-run)")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: current)")
    parser.add_argument("--scope", help="Limit scope to specific directory (e.g., 400_guides)")
    parser.add_argument("--owners-map", help="Custom owners mapping file (not implemented)")

    args = parser.parse_args()

    # Override scope if specified
    if args.scope:
        global README_SCOPE_DIRS
        README_SCOPE_DIRS = [args.scope]

    # Discover files
    readme_files = discover_readme_files(args.root)

    if not readme_files:
        print("No README files found in scope.")
        return 0

    print(f"Found {len(readme_files)} README files in scope")
    if not args.write:
        print("Running in dry-run mode (use --write to modify files)")

    # Process files
    results = []
    total_missing = 0

    for file_path in readme_files:
        result = process_readme_file(file_path, args.write)
        results.append(result)
        total_missing += len(result.get("missing_sections", set()))

        if "error" in result:
            print(f"ERROR {file_path}: {result['error']}")
        elif result.get("missing_sections"):
            status = result.get("status", "unknown")
            missing = ", ".join(sorted(result["missing_sections"]))
            print(f"{status.upper():8} {file_path}: missing {missing}")
        else:
            print(f"COMPLETE {file_path}")

    # Summary
    print("\nSummary:")
    print(f"- Files processed: {len(readme_files)}")
    print(f"- Files with missing sections: {len([r for r in results if r.get('missing_sections')])}")
    print(f"- Total missing sections: {total_missing}")

    if args.write:
        modified = [r for r in results if r.get("modified")]
        print(f"- Files modified: {len(modified)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
