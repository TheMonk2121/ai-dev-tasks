#!/usr/bin/env python3
"""
Cursor Memory Context Updater

Automatically updates CURSOR_MEMORY_CONTEXT.md based on current backlog state
and system status. This ensures Cursor AI always has current context.
"""

import json
import re
from datetime import datetime
from pathlib import Path

FENCE_PRIORITIES_START = "<!-- AUTO:current_priorities:start -->"
FENCE_PRIORITIES_END = "<!-- AUTO:current_priorities:end -->"
FENCE_HEALTH_START = "<!-- AUTO:doc_health:start -->"
FENCE_HEALTH_END = "<!-- AUTO:doc_health:end -->"


def extract_backlog_priorities():
    """Extract current priorities from 000_backlog.md"""
    backlog_file = Path("000_backlog.md")
    if not backlog_file.exists():
        return []

    priorities = []

    with open(backlog_file, "r") as f:
        content = f.read()

    # Extract todo items with 🔥 priority
    lines = content.split("\n")
    for line in lines:
        if "| B‑" in line and "🔥" in line and "todo" in line:
            # Parse backlog item
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 8:
                item_id = parts[1].strip()
                title = parts[2].strip()
                points = parts[3].strip()
                problem = parts[5].strip()

                # Clean up the problem description
                problem = problem.replace("<!--score:", "").replace("-->", "").strip()

                priorities.append({"id": item_id, "title": title, "points": points, "problem": problem})

    return priorities[:3]  # Top 3 priorities


def extract_completed_items():
    """Extract recently completed items"""
    backlog_file = Path("000_backlog.md")
    if not backlog_file.exists():
        return []

    completed = []

    with open(backlog_file, "r") as f:
        content = f.read()

    # Look for completed items section
    if "## ✅ **Completed Items**" in content:
        completed_section = content.split("## ✅ **Completed Items**")[1].split("##")[0]

        # Extract last 3 completed items
        lines = completed_section.split("\n")
        for line in lines:
            if "| C‑" in line and "✅ done" in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    item_id = parts[1].strip()
                    title = parts[2].strip()
                    completion_date = parts[5].strip()

                    completed.append({"id": item_id, "title": title, "date": completion_date})

    return completed[-3:]  # Last 3 completed


def _replace_between_fences(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    if start_marker in text and end_marker in text:
        pattern = re.compile(re.escape(start_marker) + r"[\s\S]*?" + re.escape(end_marker))
        return pattern.sub(start_marker + "\n" + replacement.strip() + "\n" + end_marker, text)
    return text


def load_doc_health():
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
            # Invariant warnings recorded in validation_results? We store warnings list
            warnings = data.get("warnings", [])
            health["invariant_warnings"] = sum(1 for w in warnings if isinstance(w, dict) and "invariant_issues" in w)
            if health["files_checked"] is None:
                health["files_checked"] = data.get("files_checked")
        except Exception:
            pass
    return health


def render_doc_health_block(health: dict) -> str:
    lines = []
    lines.append("### Documentation Health")
    lines.append("")
    lines.append(f"- Files checked: {health.get('files_checked', 'n/a')}")
    lines.append(f"- Anchor warnings: {health.get('anchor_warnings', 0)}")
    lines.append(f"- Invariant warnings: {health.get('invariant_warnings', 0)}")
    lines.append(f"- Last run: {health.get('timestamp')}")
    return "\n".join(lines)


def update_memory_context():
    """Update CURSOR_MEMORY_CONTEXT.md with current state"""

    # Extract current state
    priorities = extract_backlog_priorities()
    completed = extract_completed_items()

    # Read current memory context
    memory_file = Path("100_cursor-memory-context.md")
    if not memory_file.exists():
        print("❌ 100_cursor-memory-context.md not found")
        return

    with open(memory_file, "r") as f:
        content = f.read()

    # Build Current Priorities block (rendered as list)
    if priorities:
        block = []
        block.append("### **Immediate Focus (Next 1-2 weeks)**")
        for i, priority in enumerate(priorities, 1):
            block.append(f"{i}. **{priority['id']}**: {priority['title']} ({priority['points']} points)")
            block.append(f"   - {priority['problem']}")
        priorities_text = "\n".join(block) + "\n"

        # Preferred: replace between fences
        fenced_priorities = priorities_text.strip()
        content_after_fence_try = _replace_between_fences(
            content, FENCE_PRIORITIES_START, FENCE_PRIORITIES_END, fenced_priorities
        )
        if content_after_fence_try != content:
            content = content_after_fence_try
        else:
            # Fallback: legacy section replacement
            content = re.sub(
                r"### \*\*Immediate Focus \(Next 1-2 weeks\)\*\*.*?(?=### \*\*Infrastructure Status\*\*)",
                "\n" + priorities_text,
                content,
                flags=re.DOTALL,
            )

    # Update completed items
    if completed:
        completed_text = "\n### **Recently Completed**\n"
        for item in completed:
            completed_text += f"- ✅ **{item['id']}**: {item['title']} ({item['date']})\n"

        # Add after infrastructure status
        if "### **Infrastructure Status**" in content:
            infrastructure_section = content.split("### **Infrastructure Status**")[1]
            if "### **Recently Completed**" not in infrastructure_section:
                # Insert after infrastructure status
                content = re.sub(
                    r"(### \*\*Infrastructure Status\*\*.*?)(\n## )",
                    r"\1" + completed_text + r"\2",
                    content,
                    flags=re.DOTALL,
                )

    # Insert/replace Doc Health block
    health = load_doc_health()
    health_text = render_doc_health_block(health)
    content = _replace_between_fences(content, FENCE_HEALTH_START, FENCE_HEALTH_END, health_text)
    if FENCE_HEALTH_START not in content or FENCE_HEALTH_END not in content:
        # Append a fenced Doc Health section if missing
        content += "\n\n" + FENCE_HEALTH_START + "\n" + health_text + "\n" + FENCE_HEALTH_END + "\n"

    # Update timestamp (keep existing format if present)
    content = re.sub(
        r"\*Last Updated: \d{4}-\d{2}-\d{2}\*", f'*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*', content
    )

    # Write updated content
    with open(memory_file, "w") as f:
        f.write(content)

    print("✅ 100_cursor-memory-context.md updated successfully")
    print(f"📋 Current priorities: {len(priorities)} items")
    print(f"✅ Recent completions: {len(completed)} items")


def main():
    """Main function"""
    print("🧠 Updating Cursor Memory Context...")

    try:
        update_memory_context()
        print("✅ Memory context updated successfully")
    except Exception as e:
        print(f"❌ Error updating memory context: {e}")


if __name__ == "__main__":
    main()
