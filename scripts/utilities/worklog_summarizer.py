from __future__ import annotations
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env -S uv run python
"""
Worklog Summarizer - Extract insights from Scribe worklogs
---------------------------------------------------------
Automatically summarizes worklog content into actionable insights,
decisions, and next steps for backlog items.

Enhanced with:
- Memory rehydration tags for DSPy integration
- Timestamp tracking for creation and updates
- Graph visualization metadata
- Cross-reference linking
"""

def read_worklog(backlog_id: str) -> str:
    """Read worklog content for a given backlog ID."""
    worklog_path = Path(f"artifacts/worklogs/{backlog_id}.md")
    if not worklog_path.exists():
        raise FileNotFoundError(f"Worklog not found: {worklog_path}")

    return worklog_path.read_text(encoding="utf-8")

def extract_ideas(worklog_content: str) -> list[str]:
    """Extract ideas from worklog content."""
    ideas = []

    # Look for lines that contain "idea", "new idea", "enhanced", etc.
    lines = worklog_content.split("\n")
    for line in lines:
        line = line.strip()
        if any(keyword in line.lower() for keyword in ["idea:", "new idea", "enhanced", "proposed", "suggestion"]):
            # Clean up the line
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                ideas.append(clean_line)

    return ideas

def extract_decisions(worklog_content: str) -> list[str]:
    """Extract decisions from worklog content."""
    decisions = []

    lines = worklog_content.split("\n")
    for line in lines:
        line = line.strip()
        if any(
            keyword in line.lower() for keyword in ["decision:", "decided", "chose", "selected", "implemented", "added"]
        ):
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                decisions.append(clean_line)

    return decisions

def extract_file_changes(worklog_content: str) -> list[str]:
    """Extract file changes from worklog content."""
    files = set()

    # Look for "Changes: X file(s)" sections
    lines = worklog_content.split("\n")
    for i, line in enumerate(lines):
        if "Changes:" in line and "file(s)" in line:
            # Look for file paths in subsequent lines
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- "):
                file_path = lines[j].strip()[2:]  # Remove "- "
                if file_path and not file_path.startswith("(+"):
                    files.add(file_path)
                j += 1

    return sorted(list(files))

def extract_implementation_progress(worklog_content: str) -> dict[str, Any]:
    """Extract implementation progress from worklog content."""
    progress = {"completed": [], "in_progress": [], "planned": []}

    lines = worklog_content.split("\n")
    for line in lines:
        line = line.strip()

        # Look for implementation indicators
        if any(keyword in line.lower() for keyword in ["implemented:", "added", "updated", "created"]):
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                progress["completed"].append(clean_line)

        elif any(keyword in line.lower() for keyword in ["planning", "designing", "analyzing"]):
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                progress["in_progress"].append(clean_line)

        elif any(keyword in line.lower() for keyword in ["todo", "planned", "future"]):
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                progress["planned"].append(clean_line)

    return progress

def extract_session_metadata(worklog_content: str) -> dict[str, Any]:
    """Extract session metadata from worklog content."""
    metadata = {
        "session_count": 0,
        "branch": "unknown",
        "last_activity": "unknown",
        "total_lines": len(worklog_content.split("\n")),
        "ideas_count": 0,
        "decisions_count": 0,
        "files_modified_count": 0,
    }

    lines = worklog_content.split("\n")

    # Count sessions
    for line in lines:
        if "Session started" in line:
            metadata["session_count"] += 1

    # Extract branch
    for line in lines:
        if "Branch:" in line:
            branch_match = re.search(r"Branch:\s*(.+)", line)
            if branch_match:
                metadata["branch"] = branch_match.group(1).strip()

    # Extract last activity
    timestamp_pattern = r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
    timestamps = re.findall(timestamp_pattern, worklog_content)
    if timestamps:
        metadata["last_activity"] = timestamps[-1]

    # Count content types
    metadata["ideas_count"] = len(extract_ideas(worklog_content))
    metadata["decisions_count"] = len(extract_decisions(worklog_content))
    metadata["files_modified_count"] = len(extract_file_changes(worklog_content))

    return metadata

def generate_next_steps(ideas: list[str], decisions: list[str], progress: dict[str, Any]) -> list[str]:
    """Generate next steps based on ideas, decisions, and progress."""
    next_steps = []

    # If there are ideas but no implementations, suggest implementation
    if ideas and not progress.get("completed"):
        next_steps.append("Implement the generated ideas")

    # If there are decisions but no progress, suggest action
    if decisions and not progress.get("completed"):
        next_steps.append("Take action on the decisions made")

    # If there are in-progress items, suggest completion
    if progress.get("in_progress"):
        next_steps.append("Complete the in-progress implementations")

    # Add any planned items
    next_steps.extend(progress.get("planned", []))

    return next_steps[:5]  # Limit to top 5 next steps

def generate_memory_rehydration_tags(backlog_id: str, summary_data: dict[str, Any]) -> str:
    """Generate memory rehydration tags for DSPy integration."""
    metadata = summary_data.get("metadata", {})
    ideas_count = metadata.get("ideas_count", 0)
    decisions_count = metadata.get("decisions_count", 0)

    # Determine primary role based on content
    primary_role = "implementer"  # Default for Scribe summaries
    if ideas_count > decisions_count:
        primary_role = "planner"
    elif decisions_count > ideas_count:
        primary_role = "implementer"

    tags = f"""

<!-- DSPY_ROLE: {primary_role} -->
<!-- DSPY_AUTHORITY: scribe_session_insights -->
<!-- DSPY_FILES: artifacts/worklogs/{backlog_id}.md, artifacts/summaries/{backlog_id}-summary.md -->
<!-- DSPY_CONTEXT: AI-generated summary of Scribe brainstorming session with actionable insights -->
<!-- DSPY_VALIDATION: session_analysis, decision_tracking, implementation_progress -->
<!-- DSPY_RESPONSIBILITIES: context_capture, insight_extraction, progress_tracking -->
<!-- GRAPH_NODE_TYPE: scribe_summary -->
<!-- GRAPH_CATEGORY: session_insights -->
<!-- GRAPH_WEIGHT: {min(ideas_count + decisions_count, 10)} -->
<!-- CREATED_AT: {datetime.now().isoformat()} -->
<!-- UPDATED_AT: {datetime.now().isoformat()} -->
<!-- SESSION_COUNT: {metadata.get('session_count', 0)} -->
<!-- IDEAS_COUNT: {ideas_count} -->
<!-- DECISIONS_COUNT: {decisions_count} -->
<!-- BRANCH: {metadata.get('branch', 'unknown')} -->
<!-- LAST_ACTIVITY: {metadata.get('last_activity', 'unknown')} -->
"""
    return tags

def generate_markdown_summary(backlog_id: str, summary_data: dict[str, Any]) -> str:
    """Generate markdown summary from summary data with enhanced metadata."""
    # Generate memory rehydration tags
    tags = generate_memory_rehydration_tags(backlog_id, summary_data)

    md = tags + "\n"
    md += f"# {backlog_id} Session Summary\n\n"
    md += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Session metadata
    metadata = summary_data.get("metadata", {})
    md += f"**Sessions**: {metadata.get('session_count', 0)}\n"
    md += f"**Branch**: {metadata.get('branch', 'unknown')}\n"
    md += f"**Last Activity**: {metadata.get('last_activity', 'unknown')}\n"
    md += f"**Total Lines**: {metadata.get('total_lines', 0)}\n"
    md += f"**Ideas Generated**: {metadata.get('ideas_count', 0)}\n"
    md += f"**Decisions Made**: {metadata.get('decisions_count', 0)}\n"
    md += f"**Files Modified**: {metadata.get('files_modified_count', 0)}\n\n"

    # Key ideas
    ideas = summary_data.get("ideas", [])
    if ideas:
        md += "## Key Ideas Generated\n"
        for idea in ideas:
            md += f"- {idea}\n"
        md += "\n"

    # Decisions made
    decisions = summary_data.get("decisions", [])
    if decisions:
        md += "## Decisions Made\n"
        for decision in decisions:
            md += f"- {decision}\n"
        md += "\n"

    # Implementation progress
    progress = summary_data.get("implementation_progress", {})
    if progress.get("completed"):
        md += "## Implementation Progress\n"
        md += "### Completed\n"
        for item in progress["completed"]:
            md += f"- ✅ {item}\n"
        md += "\n"

    if progress.get("in_progress"):
        md += "### In Progress\n"
        for item in progress["in_progress"]:
            md += f"- 🔄 {item}\n"
        md += "\n"

    # Next steps
    next_steps = summary_data.get("next_steps", [])
    if next_steps:
        md += "## Next Steps\n"
        for step in next_steps:
            md += f"- {step}\n"
        md += "\n"

    # Files modified
    files = summary_data.get("files_modified", [])
    if files:
        md += "## Files Modified\n"
        for file_path in files:
            md += f"- `{file_path}`\n"
        md += "\n"

    # Graph integration metadata
    md += "## Graph Integration\n"
    md += "- **Node Type**: scribe_summary\n"
    md += "- **Category**: session_insights\n"
    md += f"- **Weight**: {min(metadata.get('ideas_count', 0) + metadata.get('decisions_count', 0), 10)}\n"
    md += f"- **Related Nodes**: {backlog_id}, {metadata.get('branch', 'unknown')}\n\n"

    return md

def summarize_worklog(backlog_id: str) -> dict[str, Any]:
    """Main function to summarize a worklog."""
    try:
        worklog_content = read_worklog(backlog_id)

        summary = {
            "backlog_id": backlog_id,
            "ideas": extract_ideas(worklog_content),
            "decisions": extract_decisions(worklog_content),
            "files_modified": extract_file_changes(worklog_content),
            "implementation_progress": extract_implementation_progress(worklog_content),
            "metadata": extract_session_metadata(worklog_content),
        }

        # Generate next steps
        summary["next_steps"] = generate_next_steps(
            summary["ideas"], summary["decisions"], summary["implementation_progress"]
        )

        return summary

    except FileNotFoundError:
        print(f"❌ Worklog not found for {backlog_id}")
        return {"error": f"Worklog not found for {backlog_id}"}
    except Exception as e:
        print(f"❌ Error summarizing worklog: {e}")
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Summarize Scribe worklog content")
    parser.add_argument("--backlog-id", required=True, help="Backlog ID to summarize")
    parser.add_argument("--output", help="Output file path (default: artifacts/summaries/{backlog_id}-summary.md)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    # Generate summary
    summary = summarize_worklog(args.backlog_id)

    if "error" in summary:
        if not args.quiet:
            print(summary["error"])
        return 1

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        # Create summaries directory if it doesn't exist
        summaries_dir = Path("artifacts/summaries")
        summaries_dir.mkdir(exist_ok=True)
        output_path = summaries_dir / f"{args.backlog_id}-summary.md"

    # Write output
    if args.format == "markdown":
        content = generate_markdown_summary(args.backlog_id, summary)
        Path(output_path).write_text(content, encoding="utf-8")
    else:  # json
        Path(output_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if not args.quiet:
        print(f"✅ Summary generated: {output_path}")
        print(f"📊 Ideas: {len(summary['ideas'])}")
        print(f"🎯 Decisions: {len(summary['decisions'])}")
        print(f"📁 Files: {len(summary['files_modified'])}")
        print(f"📋 Next Steps: {len(summary['next_steps'])}")
        print("🏷️  Memory rehydration tags: ✅")
        print("📊 Graph integration metadata: ✅")

    return 0

if __name__ == "__main__":
    exit(main())
