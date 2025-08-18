#!/usr/bin/env python3
"""
Fast Internal Link Validator (PR B)
Validates relative paths and anchors in markdown files.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

from markdown_utils import slugify_heading


class LinkChecker:
    """Validates internal links in markdown files."""

    def __init__(self, root_path: Path, scope: str = "000_core"):
        self.root_path = root_path
        self.scope = scope
        self.scope_path = root_path / scope
        self.file_anchors = {}  # file_path -> set of anchors
        self.existing_files = set()

    def build_file_index(self) -> None:
        """Build index of existing files and their anchors."""
        if not self.scope_path.exists():
            return

        for file_path in self.scope_path.rglob("*.md"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.root_path)
                self.existing_files.add(str(relative_path))

                # Extract anchors from file
                content = file_path.read_text(encoding="utf-8")
                anchors = self._extract_anchors(content)
                self.file_anchors[str(relative_path)] = anchors

    def _extract_anchors(self, content: str) -> Set[str]:
        """Extract all heading anchors from markdown content."""
        anchors = set()
        lines = content.split("\n")

        for line in lines:
            if line.startswith("#"):
                title = line.lstrip("#").strip()
                anchor = slugify_heading(title)
                if anchor:
                    anchors.add(anchor)

        return anchors

    def check_file(self, file_path: Path) -> List[Dict]:
        """Check a single file for broken internal links."""
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding="utf-8")
        relative_path = file_path.relative_to(self.root_path)
        broken_links = []

        # Extract all markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(link_pattern, content)

        for link_text, link_target in matches:
            # Skip external links
            if link_target.startswith(("http://", "https://", "mailto:", "#")):
                continue

            # Skip anchor-only links (same page)
            if link_target.startswith("#"):
                continue

            # Parse target file and anchor
            target_file, target_anchor = self._parse_link_target(link_target)
            if not target_file:
                continue

            # Resolve relative path
            resolved_target = self._resolve_relative_path(str(relative_path), target_file)

            # Check if target file exists
            if resolved_target not in self.existing_files:
                broken_links.append(
                    {
                        "source_file": str(relative_path),
                        "link_text": link_text,
                        "target": link_target,
                        "target_file": resolved_target,
                        "target_anchor": target_anchor,
                        "error": "file_not_found",
                        "line": self._find_line_number(content, link_target),
                    }
                )
                continue

            # Check if anchor exists in target file
            if target_anchor and resolved_target in self.file_anchors:
                if target_anchor not in self.file_anchors[resolved_target]:
                    broken_links.append(
                        {
                            "source_file": str(relative_path),
                            "link_text": link_text,
                            "target": link_target,
                            "target_file": resolved_target,
                            "target_anchor": target_anchor,
                            "error": "anchor_not_found",
                            "line": self._find_line_number(content, link_target),
                        }
                    )

        return broken_links

    def _parse_link_target(self, target: str) -> tuple[Optional[str], Optional[str]]:
        """Parse link target into file and anchor components."""
        if "#" in target:
            file_part, anchor_part = target.split("#", 1)
            return file_part, anchor_part
        else:
            return target, None

    def _resolve_relative_path(self, source_file: str, target: str) -> str:
        """Resolve relative path from source file to target."""
        source_dir = str(Path(source_file).parent)

        if target.startswith("./"):
            target = target[2:]
        elif target.startswith("../"):
            # Handle parent directory navigation
            parts = source_dir.split("/")
            up_count = target.count("../")
            if up_count > len(parts):
                return target  # Invalid path
            target_dir = "/".join(parts[:-up_count])
            target = target_dir + "/" + target[3 * up_count :]
        else:
            # Relative to source directory
            target = source_dir + "/" + target if source_dir else target

        return target

    def _find_line_number(self, content: str, target: str) -> int:
        """Find the line number where a link target appears."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if target in line:
                return i
        return 0

    def check_changed_files(self, changed_files: List[str]) -> List[Dict]:
        """Check only changed files for broken links."""
        all_broken_links = []

        for file_path_str in changed_files:
            file_path = Path(file_path_str)
            if not file_path.is_absolute():
                file_path = self.root_path / file_path

            if file_path.exists() and file_path.suffix == ".md":
                broken_links = self.check_file(file_path)
                all_broken_links.extend(broken_links)

        return all_broken_links

    def check_scope(self) -> List[Dict]:
        """Check all files in scope for broken links."""
        all_broken_links = []

        if not self.scope_path.exists():
            return all_broken_links

        for file_path in self.scope_path.rglob("*.md"):
            if file_path.is_file():
                broken_links = self.check_file(file_path)
                all_broken_links.extend(broken_links)

        return all_broken_links


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fast Internal Link Validator")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--scope", default="000_core", help="Scope to check")
    parser.add_argument("--changed-files", nargs="*", help="List of changed files to check")
    parser.add_argument(
        "--changed-files-from", type=Path, help="File containing newline-separated list of changed files"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--output", type=Path, help="Output file for JSON results")

    args = parser.parse_args()

    # Initialize checker
    checker = LinkChecker(args.root, args.scope)

    # Build file index
    print(f"🔍 Building file index for {args.scope}...")
    checker.build_file_index()

    # Check links
    if args.changed_files_from:
        # Read changed files from file
        with open(args.changed_files_from) as f:
            changed_files = [line.strip() for line in f if line.strip()]
        print(f"🔍 Checking {len(changed_files)} changed files from {args.changed_files_from}...")
        broken_links = checker.check_changed_files(changed_files)
    elif args.changed_files:
        print(f"🔍 Checking {len(args.changed_files)} changed files...")
        broken_links = checker.check_changed_files(args.changed_files)
    else:
        print(f"🔍 Checking all files in {args.scope}...")
        broken_links = checker.check_scope()

    # Generate report
    report = {
        "schema_version": "1.0.0",
        "scope": args.scope,
        "total_broken_links": len(broken_links),
        "broken_links": broken_links,
        "summary": {
            "file_not_found": len([l for l in broken_links if l["error"] == "file_not_found"]),
            "anchor_not_found": len([l for l in broken_links if l["error"] == "anchor_not_found"]),
        },
    }

    # Output results
    if args.json:
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
        else:
            print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        print("\n📊 Link Check Summary:")
        print(f"  Scope: {args.scope}")
        print(f"  Total broken links: {len(broken_links)}")
        print(f"  File not found: {report['summary']['file_not_found']}")
        print(f"  Anchor not found: {report['summary']['anchor_not_found']}")

        if broken_links:
            print("\n❌ Broken Links:")
            for link in broken_links:
                print(f"  {link['source_file']}:{link['line']} - {link['link_text']}")
                print(f"    Target: {link['target']} ({link['error']})")
        else:
            print("\n✅ All internal links are valid!")

    return 0 if len(broken_links) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
