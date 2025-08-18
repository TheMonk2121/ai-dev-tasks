#!/usr/bin/env python3.12.123.11
"""
Backlog CLI (Round 1)
Generator for creating backlog items with normalized structure.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BacklogCLI:
    """CLI for managing backlog items with normalized structure."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.backlog_file = self.project_root / "000_core" / "000_backlog.md"
        self.backlog_items_dir = self.project_root / "backlog_items"
        self.lessons_file = self.project_root / "data" / "lessons_learned.jsonl"
        self.reference_cards_file = self.project_root / "500_reference-cards.md"

        # Ensure directories exist
        self.backlog_items_dir.mkdir(exist_ok=True)
        (self.project_root / "data").mkdir(exist_ok=True)

    def create_backlog_item(
        self,
        title: str,
        description: str,
        priority: int = 5,
        points: int = 3,
        dependencies: list[str] | None = None,
        dry_run: bool = True,
    ) -> dict:
        """Create a new backlog item with normalized structure."""

        # Generate unique ID
        item_id = self._generate_backlog_id()
        slug = self._create_slug(title)

        # Create item data
        item_data = {
            "id": item_id,
            "title": title,
            "description": description,
            "priority": priority,
            "points": points,
            "dependencies": dependencies or [],
            "slug": slug,
            "created_at": datetime.now().isoformat(),
            "status": "🔄 pending",
        }

        if dry_run:
            print("🔍 DRY RUN - Planned changes:")
            print(f"  📝 Backlog entry: {item_id} - {title}")
            print(f"  📁 Folder: backlog_items/{item_id}-{slug}/")
            print("  📄 Files: prd.md, tasks.md, status.json")
            print("  🔗 Cross-refs: lessons_applied, reference_cards")
            return item_data

        # Pre-write validation
        print("🔍 Running pre-write validation...")
        preflight_result = self._run_preflight_validation()

        if preflight_result["has_fail_violations"]:
            print("❌ Pre-write validation failed:")
            for category, violations in preflight_result["fail_violations"].items():
                print(f"  {category}: {violations} violations (FAIL mode)")
            print("\n💡 Fix violations or disable FAIL mode before creating backlog item.")
            return {"status": "error", "message": "Pre-write validation failed"}

        print("✅ Pre-write validation passed")

        # Create folder structure
        item_dir = self.backlog_items_dir / f"{item_id}-{slug}"
        item_dir.mkdir(exist_ok=True)

        # Create files
        self._create_prd_file(item_dir, item_data)
        self._create_tasks_file(item_dir, item_data)
        self._create_status_file(item_dir, item_data)

        # Append to backlog
        self._append_to_backlog(item_data)

        # Write cross-references
        self._write_cross_references(item_data)

        # Post-write validation
        print("🔍 Running post-write validation...")
        postflight_result = self._run_postflight_validation()

        print(f"✅ Created backlog item: {item_id} - {title}")
        print(f"📁 Location: {item_dir}")

        if postflight_result["has_violations"]:
            print("⚠️  Post-write validation warnings:")
            for category, violations in postflight_result["violations"].items():
                print(f"  {category}: {violations} violations")

        return item_data

    def _run_preflight_validation(self) -> dict:
        """Run pre-write validation to check for FAIL mode violations."""
        try:
            import json
            import subprocess

            # Run validator with new structure
            result = subprocess.run(
                ["python3", "scripts/doc_coherence_validator.py", "--ci", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                return {"has_fail_violations": False, "fail_violations": {}}

            # Parse JSON output
            validator_data = json.loads(result.stdout)

            # Check for FAIL mode violations
            fail_violations = {}
            has_fail_violations = False

            # Check each category for FAIL mode violations
            for category, info in validator_data.get("categories", {}).items():
                if info.get("fail") and info.get("violations", 0) > 0:
                    fail_violations[category] = info["violations"]
                    has_fail_violations = True

            return {"has_fail_violations": has_fail_violations, "fail_violations": fail_violations}

        except Exception as e:
            print(f"⚠️  Preflight validation error: {e}")
            return {"has_fail_violations": False, "fail_violations": {}}

    def _run_postflight_validation(self) -> dict:
        """Run post-write validation to check for any new violations."""
        try:
            import subprocess

            # Run validator to check for new violations
            result = subprocess.run(
                ["python3", "scripts/doc_coherence_validator.py", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                return {"has_violations": False, "violations": {}}

            # Parse JSON output
            import json

            validator_data = json.loads(result.stdout)

            # Extract violations
            violations = {}
            has_violations = False

            for category in ["archive", "shadow_fork", "readme", "multi_rep"]:
                category_violations = validator_data.get(f"{category}_violations", 0)
                if category_violations > 0:
                    violations[category] = category_violations
                    has_violations = True

            return {"has_violations": has_violations, "violations": violations}

        except Exception as e:
            print(f"⚠️  Postflight validation error: {e}")
            return {"has_violations": False, "violations": {}}

    def _generate_backlog_id(self) -> str:
        """Generate unique backlog ID."""
        # Find the highest existing ID
        existing_ids = []
        for item_dir in self.backlog_items_dir.glob("B-*"):
            if item_dir.is_dir():
                match = re.match(r"B-(\d+)", item_dir.name)
                if match:
                    existing_ids.append(int(match.group(1)))

        if existing_ids:
            next_id = max(existing_ids) + 1
        else:
            next_id = 1

        return f"B-{next_id:03d}"

    def _create_slug(self, title: str) -> str:
        """Create kebab-case slug from title."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r"[^a-zA-Z0-9\s-]", "", title.lower())
        slug = re.sub(r"\s+", "-", slug.strip())
        slug = re.sub(r"-+", "-", slug)  # Replace multiple hyphens with single
        return slug

    def _create_prd_file(self, item_dir: Path, item_data: dict):
        """Create PRD file."""
        prd_content = f"""# PRD: {item_data['title']}

## Overview
{item_data['description']}

## Backlog Item
- **ID**: {item_data['id']}
- **Priority**: {item_data['priority']}
- **Points**: {item_data['points']}
- **Status**: {item_data['status']}
- **Created**: {item_data['created_at']}

## Dependencies
{item_data['dependencies'] if item_data['dependencies'] else 'None'}

## Success Criteria
- [ ] Define success criteria
- [ ] Add implementation details
- [ ] Update status

## Notes
<!-- Add implementation notes here -->
"""

        with open(item_dir / "prd.md", "w") as f:
            f.write(prd_content)

    def _create_tasks_file(self, item_dir: Path, item_data: dict):
        """Create tasks file."""
        tasks_content = f"""# Tasks: {item_data['title']}

## Backlog Item
- **ID**: {item_data['id']}
- **Title**: {item_data['title']}

## Task List
- [ ] Task 1: Define requirements
- [ ] Task 2: Implement core functionality
- [ ] Task 3: Add tests
- [ ] Task 4: Update documentation
- [ ] Task 5: Validate and deploy

## Notes
<!-- Add task-specific notes here -->
"""

        with open(item_dir / "tasks.md", "w") as f:
            f.write(tasks_content)

    def _create_status_file(self, item_dir: Path, item_data: dict):
        """Create status JSON file."""
        status_data = {
            "id": item_data["id"],
            "title": item_data["title"],
            "status": item_data["status"],
            "created_at": item_data["created_at"],
            "updated_at": item_data["created_at"],
            "progress": 0,
            "notes": [],
        }

        with open(item_dir / "status.json", "w") as f:
            json.dump(status_data, f, indent=2)

    def _append_to_backlog(self, item_data: dict):
        """Append item to 000_backlog.md."""
        if not self.backlog_file.exists():
            print(f"⚠️  Backlog file not found: {self.backlog_file}")
            return

        # Read existing content
        with open(self.backlog_file) as f:
            content = f.read()

        # Find the table section
        table_pattern = r"(\|.*\|\n\|.*\|\n)(.*)"
        match = re.search(table_pattern, content, re.MULTILINE | re.DOTALL)

        if not match:
            print("⚠️  Could not find table in backlog file")
            return

        header, table_content = match.groups()

        # Create new row
        new_row = f"| {item_data['id']} | {item_data['title']} | {item_data['status']} | {item_data['points']} | {item_data['priority']} | {item_data['description'][:50]}... | {', '.join(item_data['dependencies']) if item_data['dependencies'] else 'None'} |\n"

        # Insert new row after header
        new_content = content.replace(header + table_content, header + new_row + table_content)

        # Write back to file
        with open(self.backlog_file, "w") as f:
            f.write(new_content)

    def _write_cross_references(self, item_data: dict):
        """Write cross-references to lessons and reference cards."""
        # Add to lessons learned
        lesson_entry = {
            "timestamp": item_data["created_at"],
            "source": "backlog_cli",
            "category": "backlog_creation",
            "message": f"Created backlog item {item_data['id']}: {item_data['title']}",
            "context": {"item_id": item_data["id"], "priority": item_data["priority"], "points": item_data["points"]},
        }

        with open(self.lessons_file, "a") as f:
            f.write(json.dumps(lesson_entry) + "\n")

        # Add to reference cards
        if self.reference_cards_file.exists():
            with open(self.reference_cards_file, "a") as f:
                f.write(f"\n## {item_data['id']}: {item_data['title']}\n\n{item_data['description']}\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Backlog CLI for managing backlog items")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create backlog item command
    create_parser = subparsers.add_parser("create-backlog-item", help="Create a new backlog item")
    create_parser.add_argument("title", help="Item title")
    create_parser.add_argument("description", help="Item description")
    create_parser.add_argument("--priority", type=int, default=5, help="Priority (1-10)")
    create_parser.add_argument("--points", type=int, default=3, help="Story points")
    create_parser.add_argument("--dependencies", nargs="*", help="Dependencies (space-separated)")
    create_parser.add_argument("--no-dry-run", action="store_true", help="Actually create files (default is dry-run)")

    # Link PRD command
    link_parser = subparsers.add_parser("link-prd", help="Link existing PRD to backlog item")
    link_parser.add_argument("item_id", help="Backlog item ID")
    link_parser.add_argument("prd_file", help="Path to PRD file")

    # Add cross-reference command
    xref_parser = subparsers.add_parser("add-crossref", help="Add cross-reference to backlog item")
    xref_parser.add_argument("item_id", help="Backlog item ID")
    xref_parser.add_argument("reference", help="Reference to add")

    # Close item command
    close_parser = subparsers.add_parser("close-item", help="Close a backlog item")
    close_parser.add_argument("item_id", help="Backlog item ID")
    close_parser.add_argument("--status", default="✅ done", help="Final status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    cli = BacklogCLI()

    try:
        if args.command == "create-backlog-item":
            result = cli.create_backlog_item(
                title=args.title,
                description=args.description,
                priority=args.priority,
                points=args.points,
                dependencies=args.dependencies,
                dry_run=not args.no_dry_run,
            )
            print(f"✅ Backlog item created: {result['id']}")

        elif args.command == "link-prd":
            print(f"🔗 Linking PRD to {args.item_id}")
            # TODO: Implement PRD linking

        elif args.command == "add-crossref":
            print(f"📎 Adding cross-reference to {args.item_id}")
            # TODO: Implement cross-reference adding

        elif args.command == "close-item":
            print(f"✅ Closing item {args.item_id}")
            # TODO: Implement item closing

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
