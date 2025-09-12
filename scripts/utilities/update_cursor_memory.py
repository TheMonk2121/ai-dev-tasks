from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
    from few_shot_integration import FewShotExampleLoader
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Cursor Memory Context Auto-Update Helper (B-061)

Enhanced script to update 100_memory/100_cursor-memory-context.md based on current backlog state
and system status. This ensures Cursor AI always has current context.

Features:
- Fenced sections for automated updates
- Dry-run mode to preview changes
- Improved backlog parsing
- Better error handling and validation
"""

# Import few-shot integration framework
try:

    FEW_SHOT_AVAILABLE = True
except ImportError:
    FEW_SHOT_AVAILABLE = False
    print("⚠️  Few-shot integration not available - running in standard mode")

# Fenced section markers for automated updates
FENCE_PRIORITIES_START = "<!-- AUTO:current_priorities:start -->"
FENCE_PRIORITIES_END = "<!-- AUTO:current_priorities:end -->"
FENCE_HEALTH_START = "<!-- AUTO:doc_health:start -->"
FENCE_HEALTH_END = "<!-- AUTO:doc_health:end -->"
FENCE_COMPLETED_START = "<!-- AUTO:recently_completed:start -->"
FENCE_COMPLETED_END = "<!-- AUTO:recently_completed:end -->"

def parse_backlog_item(line: str, few_shot_loader: FewShotExampleLoader | None = None) -> dict[str, str] | None:
    """Parse a single backlog item line with improved error handling and few-shot enhancement"""
    if not line.strip() or "| B-" not in line:
        return None

    try:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            return None

        item_id = parts[1].strip()
        title = parts[2].strip()
        priority = parts[3].strip()
        points = parts[4].strip()
        status = parts[5].strip() if len(parts) > 5 else ""
        problem = parts[6].strip() if len(parts) > 6 else ""

        # Clean up the problem description
        problem = re.sub(r"<!--.*?-->", "", problem).strip()

        result = {
            "id": item_id,
            "title": title,
            "priority": priority,
            "points": points,
            "status": status,
            "problem": problem,
        }

        # Apply few-shot enhancement if available
        if few_shot_loader:
            try:
                # Load backlog analysis examples
                examples = few_shot_loader.load_examples_by_category("backlog_analysis")
                patterns = few_shot_loader.extract_patterns(examples)

                # Apply patterns to the line (use slightly lower threshold for backlog use-case)
                few_shot_results = few_shot_loader.apply_patterns_to_content(line, patterns, threshold=0.2)

                # Add few-shot insights to the result
                if few_shot_results.get("matched_patterns"):
                    result["few_shot_insights"] = few_shot_results["matched_patterns"]

                if few_shot_results.get("validation_suggestions"):
                    result["validation_suggestions"] = few_shot_results["validation_suggestions"]

            except Exception:
                # Don't fail the parsing if few-shot enhancement fails
                pass

        return result
    except Exception:
        return None

def extract_backlog_priorities(enable_few_shot: bool = True) -> list[dict[str, str]]:
    """Extract current priorities from 000_core/000_backlog.md with improved parsing and few-shot enhancement"""
    backlog_file = Path("000_core/000_backlog.md")
    if not backlog_file.exists():
        print(f"⚠️  Backlog file not found: {backlog_file}")
        return []

    priorities = []
    few_shot_loader = None

    # Initialize few-shot loader if enabled
    if enable_few_shot and FEW_SHOT_AVAILABLE:
        try:
            few_shot_loader = FewShotExampleLoader()
            print("✅ Few-shot enhancement enabled for backlog parsing")
        except Exception as e:
            print(f"⚠️  Failed to initialize few-shot loader: {e}")

    try:
        with open(backlog_file, encoding="utf-8") as f:
            content = f.read()

        # Extract todo items with 🔥 priority
        lines = content.split("\n")
        for line in lines:
            if "| B‑" in line and "🔥" in line and "todo" in line:
                item = parse_backlog_item(line, few_shot_loader)
                if item:
                    priorities.append(item)

        # Sort by ID number as proxy for priority
        def priority_sort_key(item):
            try:
                num = int(item["id"].split("-")[1])
                return num
            except (ValueError, IndexError, KeyError):
                return 999

        priorities.sort(key=priority_sort_key)
        return priorities[:5]  # Top 5 priorities

    except Exception as e:
        print(f"❌ Error parsing backlog: {e}")
        return []

def extract_completed_items() -> list[dict[str, str]]:
    """Extract recently completed items with improved parsing"""
    backlog_file = Path("000_core/000_backlog.md")
    if not backlog_file.exists():
        return []

    completed = []

    try:
        with open(backlog_file, encoding="utf-8") as f:
            content = f.read()

        # Look for completed items section
        if "## ✅ **Completed Items**" in content:
            completed_section = content.split("## ✅ **Completed Items**")[1].split("##")[0]

            # Extract completed items
            lines = completed_section.split("\n")
            for line in lines:
                if "| B‑" in line and "✅ done" in line:
                    item = parse_backlog_item(line)
                    if item:
                        completed.append(item)

        return completed[-5:]  # Last 5 completed

    except Exception as e:
        print(f"❌ Error parsing completed items: {e}")
        return []

def _replace_between_fences(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    """Replace content between fenced markers"""
    if start_marker in text and end_marker in text:
        pattern = re.compile(re.escape(start_marker) + r"[\s\S]*?" + re.escape(end_marker))
        return pattern.sub(start_marker + "\n" + replacement.strip() + "\n" + end_marker, text)
    return text

def _add_fenced_section(text: str, start_marker: str, end_marker: str, content: str) -> str:
    """Add a new fenced section if it doesn't exist"""
    if start_marker in text and end_marker in text:
        return _replace_between_fences(text, start_marker, end_marker, content)
    else:
        # Add at the end before the last section
        return text.rstrip() + "\n\n" + start_marker + "\n" + content + "\n" + end_marker + "\n"

def load_doc_health() -> dict[str, Any]:
    """Load health telemetry from docs_health.json or validation report."""
    health = {
        "files_checked": None,
        "anchor_warnings": 0,
        "invariant_warnings": 0,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    # Preferred source
    health_path = Path("docs_health.json")
    if health_path.exists():
        try:
            data = json.loads(health_path.read_text())
            health["files_checked"] = data.get("files_checked")
            warnings = data.get("warnings", [])
            health["anchor_warnings"] = sum(1 for w in warnings if "anchor" in w)
        except Exception:
            pass

    # Fallback to validation report
    report_path = Path("docs/validation_report.json")
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text())
            health["timestamp"] = data.get("timestamp", health["timestamp"])
            warnings = data.get("warnings", [])
            health["invariant_warnings"] = sum(1 for w in warnings if isinstance(w, dict) and "invariant_issues" in w)
            if health["files_checked"] is None:
                health["files_checked"] = data.get("files_checked")
        except Exception:
            pass

    return health

def render_priorities_block(priorities: list[dict[str, str]]) -> str:
    """Render priorities as a formatted block"""
    if not priorities:
        return "No current priorities found."

    lines = []
    lines.append("### **Current Priorities**")
    lines.append("")

    for i, priority in enumerate(priorities, 1):
        lines.append(f"{i}. **{priority['id']}**: {priority['title']} ({priority['points']} points)")
        if priority["problem"]:
            lines.append(f"   - {priority['problem']}")
        lines.append("")

    return "\n".join(lines)

def render_completed_block(completed: list[dict[str, str]]) -> str:
    """Render completed items as a formatted block"""
    if not completed:
        return "No recently completed items."

    lines = []
    lines.append("### **Recently Completed**")
    lines.append("")

    for item in completed:
        lines.append(f"- ✅ **{item['id']}**: {item['title']}")

    return "\n".join(lines)

def render_doc_health_block(health: dict[str, Any]) -> str:
    """Render documentation health as a formatted block"""
    lines = []
    lines.append("### **Documentation Health**")
    lines.append("")
    lines.append(f"- Files checked: {health.get('files_checked', 'n/a')}")
    lines.append(f"- Anchor warnings: {health.get('anchor_warnings', 0)}")
    lines.append(f"- Invariant warnings: {health.get('invariant_warnings', 0)}")
    lines.append(f"- Last run: {health.get('timestamp')}")
    return "\n".join(lines)

def update_memory_context(dry_run: bool = False, enable_few_shot: bool = True) -> tuple[bool, str]:
    """Update 100_memory/100_cursor-memory-context.md with current state"""

    # Extract current state
    priorities = extract_backlog_priorities(enable_few_shot=enable_few_shot)
    completed = extract_completed_items()
    health = load_doc_health()

    # Read current memory context
    memory_file = Path("100_memory/100_cursor-memory-context.md")
    if not memory_file.exists():
        return False, f"❌ Memory context file not found: {memory_file}"

    try:
        with open(memory_file, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"❌ Error reading memory context: {e}"

    # Build updated content
    updated_content = content

    # Update priorities section
    priorities_text = render_priorities_block(priorities)
    updated_content = _add_fenced_section(
        updated_content, FENCE_PRIORITIES_START, FENCE_PRIORITIES_END, priorities_text
    )

    # Update completed items section
    completed_text = render_completed_block(completed)
    updated_content = _add_fenced_section(updated_content, FENCE_COMPLETED_START, FENCE_COMPLETED_END, completed_text)

    # Update health section
    health_text = render_doc_health_block(health)
    updated_content = _add_fenced_section(updated_content, FENCE_HEALTH_START, FENCE_HEALTH_END, health_text)

    # Update timestamp
    updated_content = re.sub(
        r"\*Last Updated: \d{4}-\d{2}-\d{2}\*",
        f'*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*',
        updated_content,
    )

    # Show changes in dry-run mode
    if dry_run:
        print("🔍 DRY RUN - Preview of changes:")
        print(f"📋 Priorities to update: {len(priorities)} items")
        print(f"✅ Completed items to update: {len(completed)} items")
        print(f"📊 Health data to update: {health.get('files_checked', 'n/a')} files checked")

        if content != updated_content:
            print("✅ Changes would be applied")
            return True, "Dry run completed - changes would be applied"
        else:
            print("ℹ️  No changes needed")
            return True, "Dry run completed - no changes needed"

    # Write updated content
    try:
        with open(memory_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return (
            True,
            f"✅ Memory context updated successfully\n"
            f"📋 Priorities: {len(priorities)} items\n"
            f"✅ Completed: {len(completed)} items",
        )

    except Exception as e:
        return False, f"❌ Error writing memory context: {e}"

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description="Update Cursor Memory Context")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--no-few-shot", action="store_true", help="Disable few-shot enhanced parsing")

    args = parser.parse_args()

    print("🧠 Updating Cursor Memory Context...")
    if args.dry_run:
        print("🔍 Running in dry-run mode")

    try:
        success, message = update_memory_context(dry_run=args.dry_run, enable_few_shot=not args.no_few_shot)
        print(message)

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error updating memory context: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
