#!/usr/bin/env python3
"""
XRef Scanner & Safe Writer (PR B)
Scans for missing cross-references and applies them safely.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from markdown_utils import (
    extract_backticked_refs,
    extract_code_fences,
    extract_title_mentions,
    find_existing_links,
    generate_xref_block,
    normalize_filename,
    slugify_heading,
)


class XRefScanner:
    """Scans for missing cross-references in markdown files."""

    def __init__(self, root_path: Path, scope: str = "000_core"):
        self.root_path = root_path
        self.scope = scope
        self.scope_path = root_path / scope
        self.repo_index = {}
        self.exceptions = {}

    def build_repo_index(self) -> Dict:
        """Build index of all files, titles, and anchors in scope."""
        index = {
            "files": {},
            "titles": {},
            "anchors": {},
        }

        if not self.scope_path.exists():
            return index

        for file_path in self.scope_path.rglob("*.md"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.root_path)
                content = file_path.read_text(encoding="utf-8")

                # Index file
                index["files"][str(relative_path)] = {
                    "path": str(relative_path),
                    "title": self._extract_title(content),
                    "size": len(content),
                }

                # Index titles and anchors
                self._index_headings(content, str(relative_path), index)

        return index

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return ""

    def _index_headings(self, content: str, file_path: str, index: Dict):
        """Index headings and their anchors."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                anchor = slugify_heading(title)

                if title and anchor:
                    # Index by title
                    index["titles"][normalize_filename(title)] = {
                        "file": file_path,
                        "anchor": anchor,
                        "title": title,
                    }

                    # Index by anchor
                    index["anchors"][anchor] = {
                        "file": file_path,
                        "title": title,
                        "anchor": anchor,
                    }

    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for missing cross-references."""
        if not file_path.exists():
            return []

        content = file_path.read_text(encoding="utf-8")
        relative_path = file_path.relative_to(self.root_path)
        suggestions = []

        # Skip if already has xref-autofix block
        if "<!-- xref-autofix:begin -->" in content:
            return []

        # Extract code fences to skip
        fences = extract_code_fences(content)

        # Find existing links
        existing_links = set(find_existing_links(content))

        # Extract references
        backticked_refs = extract_backticked_refs(content)
        title_mentions = extract_title_mentions(content)

        # Combine all references
        all_refs = set(backticked_refs + title_mentions)

        # Check each reference
        for ref in all_refs:
            if ref in existing_links:
                continue  # Already linked

            # Check if reference exists in repo index
            target_info = self._find_target(ref)
            if target_info:
                # Skip self-references
                if target_info["file"] == str(relative_path):
                    continue

                # Calculate confidence
                confidence = self._calculate_confidence(ref, target_info["title"])

                suggestion = {
                    "source_file": str(relative_path),
                    "reference": ref,
                    "target_path": target_info["file"],
                    "target_title": target_info["title"],
                    "target_anchor": target_info.get("anchor", ""),
                    "confidence": confidence,
                    "type": "backtick" if ref in backticked_refs else "mention",
                }

                suggestions.append(suggestion)

        return suggestions

    def _find_target(self, ref: str) -> Optional[Dict]:
        """Find target file for a reference."""
        # Check files first
        for file_path, file_info in self.repo_index["files"].items():
            if normalize_filename(file_path) == ref:
                return {
                    "file": file_path,
                    "title": file_info["title"],
                }

        # Check titles
        if ref in self.repo_index["titles"]:
            return self.repo_index["titles"][ref]

        # Check anchors
        if ref in self.repo_index["anchors"]:
            return self.repo_index["anchors"][ref]

        return None

    def _calculate_confidence(self, ref: str, target_title: str) -> float:
        """Calculate confidence score for a reference match."""
        ref_norm = normalize_filename(ref)
        title_norm = normalize_filename(target_title)

        if ref_norm == title_norm:
            return 1.0

        # Check for partial matches
        if ref_norm in title_norm or title_norm in ref_norm:
            return 0.9

        # Calculate similarity
        ref_chars = set(ref_norm)
        title_chars = set(title_norm)
        intersection = ref_chars & title_chars
        union = ref_chars | title_chars

        if union:
            return len(intersection) / len(union)

        return 0.0

    def load_exceptions(self, exceptions_file: Optional[Path]) -> None:
        """Load exceptions from file."""
        if not exceptions_file or not exceptions_file.exists():
            return

        try:
            with open(exceptions_file) as f:
                data = json.load(f)
                self.exceptions = data.get("exceptions", {})
        except Exception as e:
            print(f"Warning: Could not load exceptions: {e}")

    def is_excepted(self, file_path: str, key: str) -> bool:
        """Check if a file has an exception for a given key."""
        if file_path not in self.exceptions:
            return False

        for exception in self.exceptions[file_path]:
            if exception.get("key") == key:
                # Check expiry
                expires = exception.get("expires")
                if expires:
                    try:
                        expiry_date = datetime.strptime(expires, "%Y-%m-%d")
                        if datetime.now() > expiry_date:
                            print(f"Warning: Expired exception for {file_path}: {exception.get('reason', 'No reason')}")
                            return False
                    except ValueError:
                        # Invalid date format - treat as expired
                        print(f"Warning: Invalid date format for {file_path}: {expires}")
                        return False
                return True

        return False


class XRefWriter:
    """Safely writes cross-references to files."""

    def __init__(self, scanner: XRefScanner):
        self.scanner = scanner

    def write_suggestions(self, file_path: Path, suggestions: List[Dict], apply_mode: str = "stubs") -> bool:
        """Write suggestions to file."""
        if not suggestions:
            return False

        content = file_path.read_text(encoding="utf-8")

        # Check if already has xref-autofix block
        if "<!-- xref-autofix:begin -->" in content:
            return False

        # Generate xref block
        if apply_mode == "links":
            # Only apply high-confidence links
            high_confidence = [s for s in suggestions if s.get("confidence", 0) >= 0.8]
            xref_block = generate_xref_block(high_confidence)
        else:
            # Apply all as stubs
            xref_block = generate_xref_block(suggestions)

        if not xref_block:
            return False

        # Insert at end of file
        new_content = content.rstrip() + "\n\n" + xref_block + "\n"

        # Write file
        file_path.write_text(new_content, encoding="utf-8")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="XRef Scanner & Safe Writer")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--scope", default="000_core", help="Scope to scan")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (default when --write not specified)")
    parser.add_argument("--write", action="store_true", help="Actually write changes")
    parser.add_argument("--apply", choices=["stubs", "links"], default="stubs", help="Apply mode")
    parser.add_argument("--exceptions", type=Path, help="Exceptions file")
    parser.add_argument("--output", type=Path, help="Output JSON file")

    args = parser.parse_args()

    # Initialize scanner
    scanner = XRefScanner(args.root, args.scope)
    scanner.load_exceptions(args.exceptions)

    # Build repo index
    print(f"🔍 Building repo index for {args.scope}...")
    scanner.repo_index = scanner.build_repo_index()

    # Scan files
    scope_path = args.root / args.scope
    if not scope_path.exists():
        print(f"❌ Scope path does not exist: {scope_path}")
        return 1

    all_suggestions = []
    total_files = 0
    files_with_suggestions = 0

    for file_path in scope_path.rglob("*.md"):
        if file_path.is_file():
            total_files += 1
            relative_path = file_path.relative_to(args.root)

            # Check exceptions
            if scanner.is_excepted(str(relative_path), "xref-missing"):
                continue

            suggestions = scanner.scan_file(file_path)
            if suggestions:
                # Cap suggestions per file to prevent over-linking
                if len(suggestions) > 10:
                    suggestions = suggestions[:10]  # Take first 10 (highest confidence)
                    print(f"⚠️  Capped suggestions for {relative_path} to 10 (found {len(suggestions)})")

                files_with_suggestions += 1
                all_suggestions.extend(suggestions)

    # Generate report
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now().isoformat(),
        "scope": args.scope,
        "total_files": total_files,
        "files_with_suggestions": files_with_suggestions,
        "total_suggestions": len(all_suggestions),
        "per_file_suggestions": {},
        "totals": {
            "high_confidence": len([s for s in all_suggestions if s.get("confidence", 0) >= 0.8]),
            "low_confidence": len([s for s in all_suggestions if s.get("confidence", 0) < 0.8]),
            "backtick_refs": len([s for s in all_suggestions if s["type"] == "backtick"]),
            "title_mentions": len([s for s in all_suggestions if s["type"] == "mention"]),
        },
    }

    # Group by file
    for suggestion in all_suggestions:
        file_path = suggestion["source_file"]
        if file_path not in report["per_file_suggestions"]:
            report["per_file_suggestions"][file_path] = []
        report["per_file_suggestions"][file_path].append(suggestion)

    # Write report
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 XRef Scan Summary:")
    print(f"  Scope: {args.scope}")
    print(f"  Files scanned: {total_files}")
    print(f"  Files with suggestions: {files_with_suggestions}")
    print(f"  Total suggestions: {len(all_suggestions)}")
    print(f"  High confidence: {report['totals']['high_confidence']}")
    print(f"  Low confidence: {report['totals']['low_confidence']}")

    # Apply changes if requested
    if args.write:
        print(f"\n✍️  Applying changes in {args.apply} mode...")
        writer = XRefWriter(scanner)
        files_modified = 0

        for file_path, suggestions in report["per_file_suggestions"].items():
            full_path = args.root / file_path
            if writer.write_suggestions(full_path, suggestions, args.apply):
                files_modified += 1
                print(f"  ✅ Modified: {file_path}")

        print(f"\n📝 Files modified: {files_modified}")
    else:
        print("\n🔍 Dry run mode - no changes written")

    return 0


if __name__ == "__main__":
    sys.exit(main())
