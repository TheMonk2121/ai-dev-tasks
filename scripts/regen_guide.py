#!/usr/bin/env python3
"""
Context Priority Guide Auto-Generator

Automatically generates 400_guides/400_context-priority-guide.md from file headers
to ensure AI agents always have current navigation.

Usage:
    python3 scripts/regen_guide.py --preview    # Show what would be generated
    python3 scripts/regen_guide.py --generate   # Generate the guide
    python3 scripts/regen_guide.py --dry-run    # Test without writing files
"""

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AnchorMetadata:
    """Represents anchor metadata extracted from file headers."""

    file_path: str
    anchor_key: Optional[str] = None
    anchor_priority: Optional[int] = None
    role_pins: Optional[List[str]] = None
    context_reference: Optional[str] = None
    module_reference: Optional[str] = None
    memory_context: Optional[str] = None
    database_sync: Optional[str] = None

class AnchorHeaderScanner:
    """Scans markdown files for anchor metadata headers."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.exclude_patterns = [
            "venv/",
            ".git/",
            "__pycache__/",
            "node_modules/",
            "600_archives/artifacts/",  # Exclude only artifacts, not all archives
            "600_archives/legacy/",  # Exclude legacy, not all archives
            "600_archives/legacy-archives/",  # Exclude legacy archives
            "600_archives/legacy-tests/",  # Exclude legacy tests
            "artifacts/",
            "traces/",
            ".pytest_cache/",
        ]

    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        file_str = str(file_path)
        return any(pattern in file_str for pattern in self.exclude_patterns)

    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the project."""
        markdown_files = []

        for file_path in self.project_root.rglob("*.md"):
            if not self.should_exclude_file(file_path):
                markdown_files.append(file_path)

        return sorted(markdown_files)

    def extract_anchor_metadata(self, file_path: Path) -> Optional[AnchorMetadata]:
        """Extract anchor metadata from a single file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return None

        # Initialize metadata
        metadata = AnchorMetadata(file_path=str(file_path.relative_to(self.project_root)))

        # Extract ANCHOR_KEY (find the first one in the file)
        anchor_key_match = re.search(r"<!--\s*ANCHOR_KEY:\s*([^->]+?)\s*-->", content)
        if anchor_key_match:
            metadata.anchor_key = anchor_key_match.group(1).strip()

        # Extract ANCHOR_PRIORITY
        priority_match = re.search(r"<!--\s*ANCHOR_PRIORITY:\s*(\d+)\s*-->", content)
        if priority_match:
            metadata.anchor_priority = int(priority_match.group(1))

        # Extract ROLE_PINS
        role_pins_match = re.search(r"<!--\s*ROLE_PINS:\s*\[([^\]]+)\]\s*-->", content)
        if role_pins_match:
            role_pins_str = role_pins_match.group(1)
            # Parse the role pins array
            role_pins = [role.strip().strip("\"'") for role in role_pins_str.split(",")]
            metadata.role_pins = role_pins

        # Extract CONTEXT_REFERENCE
        context_ref_match = re.search(r"<!--\s*CONTEXT_REFERENCE:\s*([^->]+?)\s*-->", content)
        if context_ref_match:
            metadata.context_reference = context_ref_match.group(1).strip()

        # Extract MODULE_REFERENCE
        module_ref_match = re.search(r"<!--\s*MODULE_REFERENCE:\s*([^->]+?)\s*-->", content)
        if module_ref_match:
            metadata.module_reference = module_ref_match.group(1).strip()

        # Extract MEMORY_CONTEXT
        memory_context_match = re.search(r"<!--\s*MEMORY_CONTEXT:\s*([^->]+?)\s*-->", content)
        if memory_context_match:
            metadata.memory_context = memory_context_match.group(1).strip()

        # Extract DATABASE_SYNC
        database_sync_match = re.search(r"<!--\s*DATABASE_SYNC:\s*([^->]+?)\s*-->", content)
        if database_sync_match:
            metadata.database_sync = database_sync_match.group(1).strip()

        # Only return metadata if we found at least an anchor key
        return metadata if metadata.anchor_key else None

    def scan_all_files(self) -> List[AnchorMetadata]:
        """Scan all markdown files and extract anchor metadata."""
        markdown_files = self.find_markdown_files()
        metadata_list = []

        print(f"Scanning {len(markdown_files)} markdown files...")

        for file_path in markdown_files:
            metadata = self.extract_anchor_metadata(file_path)
            if metadata:
                metadata_list.append(metadata)
                print(f"  ✓ Found metadata in {metadata.file_path}")

        print(f"Found anchor metadata in {len(metadata_list)} files")
        return metadata_list

class GuideGenerator:
    """Generates the context priority guide from anchor metadata."""

    def __init__(self, metadata_list: List[AnchorMetadata]):
        self.metadata_list = metadata_list
        self.output_path = Path("400_guides/400_context-priority-guide.md")

    def get_priority_tier(self, priority: int) -> str:
        """Convert numeric priority to tier name."""
        if priority == 0:
            return "P0 (Critical)"
        elif priority <= 10:
            return "P1 (High)"
        elif priority <= 30:
            return "P2 (Medium)"
        else:
            return "P3 (Low)"

    def group_by_priority(self) -> Dict[str, List[AnchorMetadata]]:
        """Group metadata by priority tiers."""
        grouped = {}

        for metadata in self.metadata_list:
            if metadata.anchor_priority is not None:
                tier = self.get_priority_tier(metadata.anchor_priority)
                if tier not in grouped:
                    grouped[tier] = []
                grouped[tier].append(metadata)

        # Sort within each tier by priority (lower number = higher priority)
        for tier in grouped:
            grouped[tier].sort(key=lambda x: x.anchor_priority or 999)

        return grouped

    def group_by_role(self) -> Dict[str, List[AnchorMetadata]]:
        """Group metadata by role pins."""
        grouped = {}

        for metadata in self.metadata_list:
            if metadata.role_pins:
                for role in metadata.role_pins:
                    if role not in grouped:
                        grouped[role] = []
                    grouped[role].append(metadata)

        # Sort within each role by priority
        for role in grouped:
            grouped[role].sort(key=lambda x: x.anchor_priority or 999)

        return grouped

    def generate_guide_content(self) -> str:
        """Generate the complete context priority guide content."""

        # Header
        content = f"""

<!-- ANCHOR_KEY: context-priority -->
<!-- ANCHOR_PRIORITY: 30 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->

# 🧠 Context Priority Guide

## 🔎 TL;DR {{#tldr}}

| what this file is | read when | do next |
|---|---|---|
| Auto-generated guide for prioritizing context and documentation access | Organizing documentation or setting up new systems | Apply priority system to current documentation |

## 🎯 **Current Status**
- **Status**: ✅ **ACTIVE** - Auto-generated documentation system
- **Priority**: 🔥 Critical - Essential for AI context rehydration
- **Points**: 5 - Moderate complexity, high importance
- **Dependencies**: 100_memory/100_cursor-memory-context.md, 000_core/000_backlog.md, 400_guides/400_system-overview.md
- **Next Steps**: Maintain cross-reference accuracy and update as system evolves
- **Last Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Priority-Based Organization

"""

        # Priority-based organization
        grouped_by_priority = self.group_by_priority()

        for tier in ["P0 (Critical)", "P1 (High)", "P2 (Medium)", "P3 (Low)"]:
            if tier in grouped_by_priority:
                content += f"\n### {tier}\n\n"
                content += "| File | Anchor | Priority | Roles | Context Reference |\n"
                content += "|------|--------|----------|-------|-------------------|\n"

                for metadata in grouped_by_priority[tier]:
                    roles_str = ", ".join(metadata.role_pins) if metadata.role_pins else "—"
                    context_ref = metadata.context_reference or "—"
                    content += f"| {metadata.file_path} | {metadata.anchor_key} | {metadata.anchor_priority} | {roles_str} | {context_ref} |\n"

                content += "\n"

        # Role-based organization
        content += "\n## 🎭 Role-Based Organization\n\n"

        grouped_by_role = self.group_by_role()
        for role in sorted(grouped_by_role.keys()):
            content += f"\n### {role.title()} Role\n\n"
            content += "| File | Anchor | Priority | Context Reference |\n"
            content += "|------|--------|----------|-------------------|\n"

            for metadata in grouped_by_role[role]:
                context_ref = metadata.context_reference or "—"
                content += (
                    f"| {metadata.file_path} | {metadata.anchor_key} | {metadata.anchor_priority} | {context_ref} |\n"
                )

            content += "\n"

        # Critical path
        content += "\n## 🚀 Critical Path\n\n"
        content += "1. **Memory Context**: `100_memory/100_cursor-memory-context.md` - Primary memory scaffold\n"
        content += "2. **Backlog**: `000_core/000_backlog.md` - Current priorities and dependencies\n"
        content += "3. **System Overview**: `400_guides/400_system-overview.md` - Technical architecture\n"
        content += "4. **Project Overview**: `400_guides/400_project-overview.md` - High-level project structure\n"
        content += "5. **Context Priority**: `400_guides/400_context-priority-guide.md` - This file (reading order)\n\n"

        # Quick navigation
        content += "## 🔗 Quick Navigation\n\n"
        content += "| Topic | File | Anchor | When to read |\n"
        content += "|-------|------|--------|--------------|\n"

        # Add key files to quick navigation
        key_files = [
            ("System overview", "400_guides/400_system-overview.md", "system-overview", "After memory + backlog"),
            ("Backlog & priorities", "000_core/000_backlog.md", "backlog", "Always for work selection"),
            ("Memory context", "100_memory/100_cursor-memory-context.md", "memory-context", "Starting new session"),
            ("DSPy context", "100_memory/104_dspy-development-context.md", "dspy-context", "Deep implementation"),
            (
                "Testing strategy",
                "400_guides/400_testing-strategy-guide.md",
                "testing-strategy",
                "Before writing tests",
            ),
            ("Scribe system", "400_guides/400_scribe-system-guide.md", "scribe-system", "Using context capture"),
        ]

        for topic, file_path, anchor, when in key_files:
            content += f"| {topic} | {file_path} | {anchor} | {when} |\n"

        content += "\n"

        # Footer
        content += """## 🔄 Auto-Generation

This guide is automatically generated from file headers using `scripts/regen_guide.py`.
To regenerate this guide, run:

```bash
python3 scripts/regen_guide.py --generate
```

### Generation Criteria

- **Priority Tiers**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
- **Role Pins**: Files are tagged with role-specific access patterns
- **Context References**: Cross-references to related documentation
- **Anchor Keys**: Unique identifiers for direct navigation

### File Requirements

To be included in this guide, files must have:
- `<!-- ANCHOR_KEY: name -->` - Unique identifier
- `<!-- ANCHOR_PRIORITY: number -->` - Priority level (0-999)
- `<!-- ROLE_PINS: ["role1", "role2"] -->` - Role access patterns

Optional metadata:
- `` - Related documentation
- `` - Module dependencies
- `` - Memory context level
- `` - Database synchronization status
"""

        return content

    def generate_guide(self) -> bool:
        """Generate the context priority guide file."""
        try:
            # Ensure output directory exists
            self.output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate content
            content = self.generate_guide_content()

            # Write to file
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ Generated context priority guide: {self.output_path}")
            print(f"📊 Processed {len(self.metadata_list)} files with anchor metadata")

            return True

        except Exception as e:
            print(f"❌ Error generating guide: {e}")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate Context Priority Guide from file headers")
    parser.add_argument("--preview", action="store_true", help="Show what would be generated")
    parser.add_argument("--generate", action="store_true", help="Generate the guide")
    parser.add_argument("--dry-run", action="store_true", help="Test without writing files")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not any([args.preview, args.generate, args.dry_run]):
        parser.print_help()
        return

    # Initialize scanner
    scanner = AnchorHeaderScanner()

    # Scan for metadata
    metadata_list = scanner.scan_all_files()

    if args.verbose:
        print("\nExtracted metadata:")
        for metadata in metadata_list:
            print(f"  {metadata.file_path}:")
            print(f"    Anchor Key: {metadata.anchor_key}")
            print(f"    Priority: {metadata.anchor_priority}")
            print(f"    Role Pins: {metadata.role_pins}")
            print()

    if args.preview or args.dry_run:
        print(f"\nWould process {len(metadata_list)} files with anchor metadata")

        if args.verbose:
            # Show priority grouping
            generator = GuideGenerator(metadata_list)
            grouped = generator.group_by_priority()
            print("\nPriority grouping:")
            for tier, files in grouped.items():
                print(f"  {tier}: {len(files)} files")
                for metadata in files[:3]:  # Show first 3
                    print(f"    - {metadata.file_path} (priority {metadata.anchor_priority})")
                if len(files) > 3:
                    print(f"    ... and {len(files) - 3} more")

        return

    if args.generate:
        # Generate the guide
        generator = GuideGenerator(metadata_list)
        success = generator.generate_guide()

        if success:
            print("\n🎉 Context Priority Guide generation completed successfully!")
            print("The guide has been updated with current file metadata.")
        else:
            print("\n❌ Context Priority Guide generation failed.")
            return 1

if __name__ == "__main__":
    main()
