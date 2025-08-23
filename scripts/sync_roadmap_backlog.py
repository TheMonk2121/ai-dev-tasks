#!/usr/bin/env python3
"""
Roadmap-Backlog Synchronization Script

This script automatically updates the development roadmap based on backlog changes,
ensuring the roadmap reflects current priorities, sprint status, and completion progress.

Usage:
    python3 scripts/sync_roadmap_backlog.py
    python3 scripts/sync_roadmap_backlog.py --dry-run
    python3 scripts/sync_roadmap_backlog.py --validate-only
"""

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
BACKLOG_PATH = Path("000_core/000_backlog.md")
ROADMAP_PATH = Path("000_core/004_development-roadmap.md")
BACKUP_PATH = Path("000_core/004_development-roadmap.md.backup")

# Regex patterns for parsing
BACKLOG_ITEM_RE = re.compile(
    r"^\|\s*(B‑\d{3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|"
)
SCORE_RE = re.compile(r"<!--\s*score:\s*(\{.*?\})\s*-->", re.DOTALL | re.IGNORECASE)
SCORE_TOTAL_RE = re.compile(r"<!--\s*score_total:\s*([0-9]+(?:\.[0-9]+)?)\s*-->", re.IGNORECASE)
STATUS_RE = re.compile(r"<!--\s*status:\s*(.*?)\s*-->", re.IGNORECASE)
COMPLETION_DATE_RE = re.compile(r"<!--\s*completion_date:\s*(\d{4}-\d{2}-\d{2})\s*-->", re.IGNORECASE)

@dataclass
class BacklogItem:
    """Represents a backlog item with its metadata."""

    id: str
    title: str
    icon: str
    points_raw: str
    status: str
    desc: str
    line_idx: int
    score_total: Optional[float] = None
    completion_date: Optional[str] = None

class RoadmapBacklogSync:
    """Handles synchronization between roadmap and backlog."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.backlog_items: Dict[str, BacklogItem] = {}
        self.roadmap_content: str = ""
        self.changes_made: List[str] = []

    def parse_backlog(self) -> None:
        """Parse the backlog file and extract items."""
        if not BACKLOG_PATH.exists():
            raise FileNotFoundError(f"Backlog file not found: {BACKLOG_PATH}")

        lines = BACKLOG_PATH.read_text(encoding="utf-8").splitlines()
        i = 0

        while i < len(lines):
            m = BACKLOG_ITEM_RE.match(lines[i])
            if not m:
                i += 1
                continue

            item = BacklogItem(
                id=m.group(1).strip(),
                title=m.group(2).strip(),
                icon=m.group(3).strip(),
                points_raw=m.group(4).strip(),
                status=m.group(5).strip().lower(),
                desc=m.group(6).strip() + " | " + m.group(7).strip() + " | " + m.group(8).strip(),
                line_idx=i + 1,
            )

            # Extract metadata from following lines
            region = self._find_region(lines, i)

            # Score total
            score_match = SCORE_TOTAL_RE.search(region)
            if score_match:
                item.score_total = float(score_match.group(1))

            # Completion date
            completion_match = COMPLETION_DATE_RE.search(region)
            if completion_match:
                item.completion_date = completion_match.group(1)

            self.backlog_items[item.id] = item
            i += 1

    def _find_region(self, lines: List[str], start_idx: int) -> str:
        """Capture metadata lines until next table row or blank line break."""
        buff = []
        i = start_idx + 1
        while i < len(lines):
            if BACKLOG_ITEM_RE.match(lines[i]) or (lines[i].strip() == "" and buff):
                break
            buff.append(lines[i])
            i += 1
        return "\n".join(buff)

    def read_roadmap(self) -> None:
        """Read the current roadmap content."""
        if not ROADMAP_PATH.exists():
            raise FileNotFoundError(f"Roadmap file not found: {ROADMAP_PATH}")

        self.roadmap_content = ROADMAP_PATH.read_text(encoding="utf-8")

    def backup_roadmap(self) -> None:
        """Create a backup of the current roadmap."""
        if not self.dry_run:
            BACKUP_PATH.write_text(self.roadmap_content, encoding="utf-8")
            print(f"Backup created: {BACKUP_PATH}")

    def update_sprint_status(self) -> None:
        """Update the current sprint status section."""
        # Get current sprint items
        current_sprint_items = [
            item
            for item in self.backlog_items.values()
            if item.status in ["todo", "in-progress"] and item.score_total and item.score_total >= 3.0
        ]

        # Sort by score_total (highest first)
        current_sprint_items.sort(key=lambda x: x.score_total or 0, reverse=True)

        # Update the sprint status section
        sprint_pattern = r"(### \*\*Active Sprint:.*?\n\n#### \*\*Next Up.*?\n)(.*?)(\n\n### \*\*Sprint Goals)"

        def replace_sprint_status(match):
            header = match.group(1)
            footer = match.group(3)

            # Build new next up section
            next_up_lines = []
            for item in current_sprint_items[:5]:  # Top 5 items
                points = item.points_raw if item.points_raw else "?"
                next_up_lines.append(f"- **{item.id}**: {item.title} ({points} points)")

            if not next_up_lines:
                next_up_lines.append("- No high-priority items currently queued")

            return header + "\n".join(next_up_lines) + footer

        new_content = re.sub(sprint_pattern, replace_sprint_status, self.roadmap_content, flags=re.DOTALL)

        if new_content != self.roadmap_content:
            self.roadmap_content = new_content
            self.changes_made.append("Updated current sprint status")

    def update_phase_status(self) -> None:
        """Update the strategic phases section."""
        # Categorize items by phase
        phase1_items = [
            item
            for item in self.backlog_items.values()
            if item.status == "todo" and item.score_total and item.score_total >= 3.0
        ]
        phase2_items = [
            item
            for item in self.backlog_items.values()
            if item.status == "todo" and item.score_total and 2.0 <= item.score_total < 3.0
        ]
        phase3_items = [
            item
            for item in self.backlog_items.values()
            if item.status == "todo" and item.score_total and item.score_total < 2.0
        ]

        # Update Phase 1 (Foundation & Consensus)
        phase1_pattern = r"(#### \*\*Consensus Framework\*\*\n)(.*?)(\n\n### \*\*Phase 2)"

        def replace_phase1(match):
            header = match.group(1)
            footer = match.group(3)

            phase1_lines = []
            for item in phase1_items[:3]:  # Top 3 items
                points = item.points_raw if item.points_raw else "?"
                status_icon = "🔄" if item.status == "in-progress" else ""
                phase1_lines.append(f"- {status_icon} **{item.id}**: {item.title} ({points} points)")

            if not phase1_lines:
                phase1_lines.append("- All Phase 1 items completed")

            return header + "\n".join(phase1_lines) + footer

        new_content = re.sub(phase1_pattern, replace_phase1, self.roadmap_content, flags=re.DOTALL)

        if new_content != self.roadmap_content:
            self.roadmap_content = new_content
            self.changes_made.append("Updated Phase 1 status")

    def update_completed_items(self) -> None:
        """Update the completed items section."""
        completed_items = [
            item
            for item in self.backlog_items.values()
            if item.status in ["done", "✅ done", "complete", "completed"] and item.completion_date
        ]

        # Sort by completion date (newest first)
        completed_items.sort(key=lambda x: x.completion_date or "", reverse=True)

        # Update the completed items section
        completed_pattern = r"(#### \*\*Completed This Sprint\*\*\n)(.*?)(\n\n#### \*\*In Progress)"

        def replace_completed(match):
            header = match.group(1)
            footer = match.group(3)

            completed_lines = []
            for item in completed_items[:5]:  # Top 5 recent completions
                points = item.points_raw if item.points_raw else "?"
                completed_lines.append(f"- ✅ **{item.id}**: {item.title} ({points} points) - {item.completion_date}")

            if not completed_lines:
                completed_lines.append("- No items completed this sprint yet")

            return header + "\n".join(completed_lines) + footer

        new_content = re.sub(completed_pattern, replace_completed, self.roadmap_content, flags=re.DOTALL)

        if new_content != self.roadmap_content:
            self.roadmap_content = new_content
            self.changes_made.append("Updated completed items")

    def update_statistics(self) -> None:
        """Update the backlog integration statistics."""
        # Calculate statistics
        p0_items = [
            item
            for item in self.backlog_items.values()
            if item.status in ["todo", "in-progress"] and item.score_total and item.score_total >= 4.0
        ]
        p1_items = [
            item
            for item in self.backlog_items.values()
            if item.status in ["todo", "in-progress"] and item.score_total and 2.0 <= item.score_total < 4.0
        ]
        p2_items = [
            item
            for item in self.backlog_items.values()
            if item.status in ["todo", "in-progress"] and item.score_total and item.score_total < 2.0
        ]

        # Update statistics section
        stats_pattern = r"(### \*\*Priority Distribution\*\*\n)(.*?)(\n\n### \*\*Points Distribution)"

        def replace_stats(match):
            header = match.group(1)
            footer = match.group(3)

            stats_lines = [
                f"- **P0 (Critical)**: {len(p0_items)} items - Core system stability and consensus framework",
                f"- **P1 (High)**: {len(p1_items)} items - Advanced RAG and extraction capabilities",
                f"- **P2 (Medium)**: {len(p2_items)} items - Performance and optimization",
            ]

            return header + "\n".join(stats_lines) + footer

        new_content = re.sub(stats_pattern, replace_stats, self.roadmap_content, flags=re.DOTALL)

        if new_content != self.roadmap_content:
            self.roadmap_content = new_content
            self.changes_made.append("Updated priority distribution statistics")

    def update_timestamp(self) -> None:
        """Update the last updated timestamp."""
        timestamp_pattern = r"(\*\*Last Updated\*\*: ).*?(\n\*\*Next Review\*\*)"
        new_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        def replace_timestamp(match):
            return match.group(1) + new_timestamp + match.group(2)

        new_content = re.sub(timestamp_pattern, replace_timestamp, self.roadmap_content)

        if new_content != self.roadmap_content:
            self.roadmap_content = new_content
            self.changes_made.append("Updated timestamp")

    def write_roadmap(self) -> None:
        """Write the updated roadmap back to file."""
        if not self.dry_run:
            ROADMAP_PATH.write_text(self.roadmap_content, encoding="utf-8")
            print(f"Roadmap updated: {ROADMAP_PATH}")
        else:
            print("DRY RUN: Would update roadmap with changes")

    def sync(self) -> None:
        """Perform the complete synchronization process."""
        print("Starting roadmap-backlog synchronization...")

        try:
            # Parse backlog
            print("Parsing backlog...")
            self.parse_backlog()
            print(f"Found {len(self.backlog_items)} backlog items")

            # Read roadmap
            print("Reading roadmap...")
            self.read_roadmap()

            # Create backup
            self.backup_roadmap()

            # Perform updates
            print("Updating roadmap sections...")
            self.update_sprint_status()
            self.update_phase_status()
            self.update_completed_items()
            self.update_statistics()
            self.update_timestamp()

            # Write changes
            if self.changes_made:
                self.write_roadmap()
                print(f"Changes made: {', '.join(self.changes_made)}")
            else:
                print("No changes needed - roadmap is already up to date")

        except Exception as e:
            print(f"Error during synchronization: {e}")
            sys.exit(1)

    def validate(self) -> None:
        """Validate that roadmap and backlog are in sync."""
        print("Validating roadmap-backlog synchronization...")

        try:
            self.parse_backlog()
            self.read_roadmap()

            # Check for missing items
            roadmap_item_ids = re.findall(r"B‑\d{3}", self.roadmap_content)
            backlog_item_ids = list(self.backlog_items.keys())

            missing_in_roadmap = set(backlog_item_ids) - set(roadmap_item_ids)
            missing_in_backlog = set(roadmap_item_ids) - set(backlog_item_ids)

            if missing_in_roadmap:
                print(f"WARNING: Items in backlog but not in roadmap: {missing_in_roadmap}")

            if missing_in_backlog:
                print(f"WARNING: Items in roadmap but not in backlog: {missing_in_backlog}")

            if not missing_in_roadmap and not missing_in_backlog:
                print("✅ Roadmap and backlog are in sync")
            else:
                print("❌ Roadmap and backlog are out of sync")
                sys.exit(1)

        except Exception as e:
            print(f"Error during validation: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Synchronize roadmap with backlog")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate synchronization without making changes"
    )

    args = parser.parse_args()

    sync = RoadmapBacklogSync(dry_run=args.dry_run)

    if args.validate_only:
        sync.validate()
    else:
        sync.sync()

if __name__ == "__main__":
    main()
