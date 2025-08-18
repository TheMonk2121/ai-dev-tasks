#!/usr/bin/env python3
"""
Anchor Drift Check

Detect when renamed/removed headings break existing anchors elsewhere.
Run nightly to catch potential stale links before they reach users.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Set

# Import slugify function from markdown_utils
try:
    from scripts.markdown_utils import slugify_heading
except ImportError:
    # Fallback implementation
    def slugify_heading(heading: str) -> str:
        """Convert heading to GitHub-style slug."""
        import unicodedata

        # Convert to lowercase and normalize Unicode
        slug = unicodedata.normalize("NFKD", heading.lower())
        # Replace HTML tags
        slug = re.sub(r"<[^>]+>", "", slug)
        # Replace ampersands with double hyphens
        slug = slug.replace("&", "--")
        # Replace underscores with hyphens
        slug = slug.replace("_", "-")
        # Remove punctuation except hyphens
        slug = re.sub(r"[^\w\-]", "", slug)
        # Replace whitespace with hyphens
        slug = re.sub(r"\s+", "-", slug)
        # Remove leading/trailing hyphens
        slug = slug.strip("-")
        return slug


def get_changed_markdown_files(window_hours: int = 24) -> List[str]:
    """Get list of changed markdown files in the specified time window."""
    try:
        # Get files changed in the last N hours
        since = f"{window_hours} hours ago"
        result = subprocess.run(
            ["git", "log", "--since", since, "--name-only", "--pretty=format:", "--diff-filter=AM"],
            capture_output=True,
            text=True,
            check=True,
        )

        changed_files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip() and line.endswith(".md"):
                changed_files.append(line.strip())

        return list(set(changed_files))  # Remove duplicates
    except subprocess.CalledProcessError:
        print("⚠️  Could not determine changed files, using empty list")
        return []


def extract_anchors(content: str) -> Set[str]:
    """Extract all anchor IDs from markdown content."""
    anchors = set()

    # Extract headings and convert to slugs
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    for match in heading_pattern.finditer(content):
        level, heading = match.groups()
        slug = slugify_heading(heading)
        if slug:
            anchors.add(slug)

    # Extract explicit anchor tags
    anchor_pattern = re.compile(r'<a\s+id="([^"]+)"\s*>', re.IGNORECASE)
    for match in anchor_pattern.finditer(content):
        anchors.add(match.group(1))

    # Extract markdown-style anchors
    markdown_anchor_pattern = re.compile(r"\{#([^}]+)\}", re.IGNORECASE)
    for match in markdown_anchor_pattern.finditer(content):
        anchors.add(match.group(1))

    return anchors


def get_file_content_at_commit(file_path: str, commit: str = "HEAD") -> str:
    """Get file content at a specific commit."""
    try:
        result = subprocess.run(["git", "show", f"{commit}:{file_path}"], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def find_inbound_links(target_file: str, target_anchor: str) -> List[Dict[str, str]]:
    """Find all inbound links pointing to the target anchor."""
    inbound_links = []

    try:
        # Search for markdown links pointing to the target
        pattern = rf"\[([^\]]+)\]\([^)]*{re.escape(target_file)}#{re.escape(target_anchor)}\)"

        # Walk through all markdown files
        for root, _, files in os.walk("."):
            if ".git" in root or "node_modules" in root:
                continue

            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()

                        for match in re.finditer(pattern, content):
                            link_text = match.group(1)
                            inbound_links.append(
                                {"from": file_path, "link_text": link_text, "to": target_file, "anchor": target_anchor}
                            )
                    except Exception:
                        continue

    except Exception as e:
        print(f"⚠️  Error searching for inbound links: {e}")

    return inbound_links


def check_anchor_drift(changed_files: List[str], window_hours: int = 24) -> Dict:
    """Check for anchor drift in changed files."""
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "window_hours": window_hours,
        "changed_files": changed_files,
        "broken": [],
        "summary": {"files_checked": 0, "anchors_removed": 0, "broken_links": 0},
    }

    for file_path in changed_files:
        if not os.path.exists(file_path):
            continue

        report["summary"]["files_checked"] += 1

        # Get current content
        try:
            with open(file_path, encoding="utf-8") as f:
                current_content = f.read()
        except Exception:
            continue

        # Get previous content (before changes)
        previous_content = get_file_content_at_commit(file_path, "HEAD~1")

        # Extract anchors
        current_anchors = extract_anchors(current_content)
        previous_anchors = extract_anchors(previous_content)

        # Find removed anchors
        removed_anchors = previous_anchors - current_anchors

        for anchor in removed_anchors:
            report["summary"]["anchors_removed"] += 1

            # Find inbound links to this anchor
            inbound_links = find_inbound_links(file_path, anchor)

            for link in inbound_links:
                report["summary"]["broken_links"] += 1
                report["broken"].append(
                    {
                        "from": link["from"],
                        "link_text": link["link_text"],
                        "to": link["to"],
                        "anchor": link["anchor"],
                        "status": "removed",
                    }
                )

    return report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Check for anchor drift in changed markdown files")
    parser.add_argument("--window", type=int, default=24, help="Time window in hours (default: 24)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", help="Output file for JSON report")

    args = parser.parse_args()

    # Get changed files
    changed_files = get_changed_markdown_files(args.window)

    if not changed_files:
        print(f"📊 No markdown files changed in the last {args.window} hours")
        if args.json:
            report = {
                "schema_version": "1.0",
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "window_hours": args.window,
                "changed_files": [],
                "broken": [],
                "summary": {"files_checked": 0, "anchors_removed": 0, "broken_links": 0},
            }
            if args.output:
                with open(args.output, "w") as f:
                    json.dump(report, f, indent=2)
            else:
                print(json.dumps(report, indent=2))
        sys.exit(0)

    print(f"🔍 Checking anchor drift for {len(changed_files)} changed files...")

    # Check for anchor drift
    report = check_anchor_drift(changed_files, args.window)

    # Output results
    if args.json:
        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"✅ Report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2))
    else:
        # Human-readable output
        summary = report["summary"]
        print("\n📊 Anchor Drift Summary:")
        print(f"  Files checked: {summary['files_checked']}")
        print(f"  Anchors removed: {summary['anchors_removed']}")
        print(f"  Broken links: {summary['broken_links']}")

        if report["broken"]:
            print("\n❌ Broken Links Found:")
            for item in report["broken"][:10]:  # Show first 10
                print(f"  {item['from']} → {item['to']}#{item['anchor']} (removed)")
            if len(report["broken"]) > 10:
                print(f"  ... and {len(report['broken']) - 10} more")
        else:
            print("\n✅ No broken links detected")


if __name__ == "__main__":
    main()
