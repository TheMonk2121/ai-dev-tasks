#!/usr/bin/env python3.12.123.11
"""
Enhanced Backlog Status Tracking with Timestamps

This script adds timestamp tracking to backlog items to help identify:
- When work started on items
- When items were last updated
- Items that have been in-progress too long (stale items)
- Items that need attention

Usage:
    python3 scripts/enhanced_backlog_tracking.py --check-stale
    python3 scripts/enhanced_backlog_tracking.py --start-work B-099
    python3 scripts/enhanced_backlog_tracking.py --update-status B-099 in-progress
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class BacklogItem:
    """Represents a backlog item with enhanced tracking."""

    def __init__(
        self, id: str, title: str, status: str, started_at: str | None = None, last_updated: str | None = None
    ):
        self.id = id
        self.title = title
        self.status = status
        self.started_at = started_at
        self.last_updated = last_updated

    def is_stale(self, stale_days: int = 7) -> bool:
        """Check if item has been in-progress too long."""
        if self.status != "in-progress" or not self.started_at:
            return False

        try:
            started = datetime.fromisoformat(self.started_at)
            return datetime.now() - started > timedelta(days=stale_days)
        except ValueError:
            return False

    def days_in_progress(self) -> int | None:
        """Get number of days item has been in progress."""
        if self.status != "in-progress" or not self.started_at:
            return None

        try:
            started = datetime.fromisoformat(self.started_at)
            return (datetime.now() - started).days
        except ValueError:
            return None


class EnhancedBacklogTracker:
    """Enhanced backlog tracking with timestamps."""

    def __init__(self, backlog_file: str = "000_core/000_backlog.md"):
        self.backlog_file = Path(backlog_file)
        self.content = self.backlog_file.read_text()
        self.items = self._parse_backlog_items()

    def _parse_backlog_items(self) -> dict[str, BacklogItem]:
        """Parse backlog items from the markdown file."""
        items = {}

        # Pattern to match backlog table rows (8 columns)
        row_pattern = r"\| (B[‑-]\d+[a-z]?) \| ([^|]+) \| [^|]+ \| [^|]+ \| ([^|]+)\| [^|]+ \| [^|]+ \| [^|]+ \|"

        for match in re.finditer(row_pattern, self.content):
            item_id = match.group(1)
            title = match.group(2).strip()
            status = match.group(3).strip()

            # Extract timestamps from HTML comments
            started_at = self._extract_timestamp(item_id, "started_at")
            last_updated = self._extract_timestamp(item_id, "last_updated")

            items[item_id] = BacklogItem(item_id, title, status, started_at, last_updated)

        return items

    def _extract_timestamp(self, item_id: str, field: str) -> str | None:
        """Extract timestamp from HTML comments for a specific item."""
        # Look for timestamp after the specific item
        item_pattern = rf"\| {re.escape(item_id)} \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\|"
        item_match = re.search(item_pattern, self.content)
        if not item_match:
            return None

        # Look for timestamp in the next few lines after the item
        start_pos = item_match.end()
        end_pos = min(start_pos + 500, len(self.content))  # Look in next 500 chars
        search_content = self.content[start_pos:end_pos]

        pattern = rf"<!-- {field}: (\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}(?:\.\d+)?) -->"
        match = re.search(pattern, search_content)
        return match.group(1) if match else None

    def start_work(self, item_id: str) -> bool:
        """Mark an item as started with timestamp."""
        if item_id not in self.items:
            print(f"❌ Error: Backlog item {item_id} not found")
            return False

        item = self.items[item_id]
        if item.status == "in-progress":
            print(f"⚠️  Warning: {item_id} is already in progress")
            return False

        # Update status and add started_at timestamp
        timestamp = datetime.now().isoformat()
        self._update_item_status(item_id, "in-progress", started_at=timestamp)

        print(f"✅ Started work on {item_id}: {item.title}")
        print(f"   Started at: {timestamp}")
        return True

    def update_status(self, item_id: str, new_status: str) -> bool:
        """Update item status with last_updated timestamp."""
        if item_id not in self.items:
            print(f"❌ Error: Backlog item {item_id} not found")
            return False

        timestamp = datetime.now().isoformat()
        self._update_item_status(item_id, new_status, last_updated=timestamp)

        print(f"✅ Updated {item_id} status to '{new_status}'")
        print(f"   Updated at: {timestamp}")
        return True

    def _update_item_status(
        self, item_id: str, new_status: str, started_at: str | None = None, last_updated: str | None = None
    ) -> None:
        """Update item status and timestamps in the backlog file."""
        # Update status in table
        status_pattern = rf"(\| {re.escape(item_id)} \| [^|]+ \| [^|]+ \| [^|]+ \| )[^|]+(\|)"
        replacement = rf"\1{new_status}\2"
        self.content = re.sub(status_pattern, replacement, self.content)

        # Add timestamps as HTML comments
        timestamp_comments = []
        if started_at:
            timestamp_comments.append(f"<!-- started_at: {started_at} -->")
        if last_updated:
            timestamp_comments.append(f"<!-- last_updated: {last_updated} -->")

        if timestamp_comments:
            # Find the line with the item and add comments after it
            item_pattern = rf"(\| {re.escape(item_id)} \| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\| [^|]+\|)"
            replacement = rf"\1\n{chr(10).join(timestamp_comments)}"
            self.content = re.sub(item_pattern, replacement, self.content)

        # Write updated content back to file
        self.backlog_file.write_text(self.content)

        # Update local item
        if item_id in self.items:
            if started_at:
                self.items[item_id].started_at = started_at
            if last_updated:
                self.items[item_id].last_updated = last_updated
            self.items[item_id].status = new_status

    def check_stale_items(self, stale_days: int = 7) -> list[BacklogItem]:
        """Find items that have been in-progress too long."""
        stale_items = []

        for item in self.items.values():
            if item.is_stale(stale_days):
                stale_items.append(item)

        return stale_items

    def list_in_progress(self) -> list[BacklogItem]:
        """List all items currently in progress."""
        return [item for item in self.items.values() if item.status == "in-progress"]

    def get_item_summary(self, item_id: str) -> str | None:
        """Get a summary of an item's tracking information."""
        if item_id not in self.items:
            return None

        item = self.items[item_id]
        summary = [f"📋 {item_id}: {item.title}"]
        summary.append(f"   Status: {item.status}")

        if item.started_at:
            days = item.days_in_progress()
            summary.append(f"   Started: {item.started_at}")
            if days is not None:
                summary.append(f"   Days in progress: {days}")

        if item.last_updated:
            summary.append(f"   Last updated: {item.last_updated}")

        if item.is_stale():
            summary.append("   ⚠️  STALE - Needs attention!")

        return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description="Enhanced Backlog Status Tracking")
    parser.add_argument("--check-stale", action="store_true", help="Check for stale in-progress items")
    parser.add_argument("--start-work", type=str, metavar="ITEM_ID", help="Start work on a backlog item")
    parser.add_argument(
        "--update-status", nargs=2, metavar=("ITEM_ID", "STATUS"), help="Update status of a backlog item"
    )
    parser.add_argument("--list-in-progress", action="store_true", help="List all items currently in progress")
    parser.add_argument("--item-summary", type=str, metavar="ITEM_ID", help="Get detailed summary of a specific item")
    parser.add_argument(
        "--stale-days", type=int, default=7, help="Number of days before item is considered stale (default: 7)"
    )

    args = parser.parse_args()

    tracker = EnhancedBacklogTracker()

    if args.check_stale:
        stale_items = tracker.check_stale_items(args.stale_days)
        if stale_items:
            print(f"⚠️  Found {len(stale_items)} stale items (in-progress > {args.stale_days} days):")
            for item in stale_items:
                days = item.days_in_progress()
                print(f"   {item.id}: {item.title} ({days} days in progress)")
        else:
            print(f"✅ No stale items found (threshold: {args.stale_days} days)")

    elif args.start_work:
        tracker.start_work(args.start_work)

    elif args.update_status:
        item_id, status = args.update_status
        tracker.update_status(item_id, status)

    elif args.list_in_progress:
        in_progress = tracker.list_in_progress()
        if in_progress:
            print(f"🔄 {len(in_progress)} items currently in progress:")
            for item in in_progress:
                days = item.days_in_progress()
                stale_indicator = " ⚠️" if item.is_stale() else ""
                print(f"   {item.id}: {item.title} ({days} days){stale_indicator}")
        else:
            print("✅ No items currently in progress")

    elif args.item_summary:
        summary = tracker.get_item_summary(args.item_summary)
        if summary:
            print(summary)
        else:
            print(f"❌ Item {args.item_summary} not found")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
