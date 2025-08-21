#!/usr/bin/env python3
"""
Worklog Summarizer - Extract insights from Scribe worklogs
---------------------------------------------------------
Automatically summarizes worklog content into actionable insights,
decisions, and next steps for backlog items.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def read_worklog(backlog_id: str) -> str:
    """Read worklog content for a given backlog ID."""
    worklog_path = Path(f"artifacts/worklogs/{backlog_id}.md")
    if not worklog_path.exists():
        raise FileNotFoundError(f"Worklog not found: {worklog_path}")

    return worklog_path.read_text(encoding="utf-8")


def extract_ideas(worklog_content: str) -> List[str]:
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


def extract_decisions(worklog_content: str) -> List[str]:
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


def extract_file_changes(worklog_content: str) -> List[str]:
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


def extract_implementation_progress(worklog_content: str) -> Dict[str, Any]:
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

        elif any(keyword in line.lower() for keyword in ["planned", "todo", "next:", "future:"]):
            clean_line = re.sub(r"^\s*-\s*\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s*-\s*", "", line)
            clean_line = re.sub(r"^\s*-\s*", "", clean_line)
            if clean_line and len(clean_line) > 10:
                progress["planned"].append(clean_line)

    return progress


def extract_session_metadata(worklog_content: str) -> Dict[str, Any]:
    """Extract session metadata from worklog content."""
    metadata = {"session_count": 0, "total_duration": "unknown", "branch": "unknown", "last_activity": "unknown"}

    # Count session starts
    session_starts = re.findall(r"Session started", worklog_content)
    metadata["session_count"] = len(session_starts)

    # Extract branch info
    branch_match = re.search(r"Branch:\s*(\S+)", worklog_content)
    if branch_match:
        metadata["branch"] = branch_match.group(1)

    # Extract last activity timestamp
    timestamps = re.findall(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", worklog_content)
    if timestamps:
        metadata["last_activity"] = timestamps[-1]

    return metadata


def generate_next_steps(ideas: List[str], decisions: List[str], progress: Dict[str, Any]) -> List[str]:
    """Generate next steps based on ideas and progress."""
    next_steps = []

    # Look for ideas that haven't been implemented
    implemented_keywords = ["implemented", "added", "created", "updated"]

    for idea in ideas:
        idea_lower = idea.lower()
        if not any(keyword in idea_lower for keyword in implemented_keywords):
            # Extract the core concept from the idea
            if ":" in idea:
                core_concept = idea.split(":", 1)[1].strip()
            else:
                core_concept = idea

            next_steps.append(f"Implement: {core_concept}")

    # Add any planned items
    next_steps.extend(progress.get("planned", []))

    return next_steps[:5]  # Limit to top 5 next steps


def generate_markdown_summary(backlog_id: str, summary_data: Dict[str, Any]) -> str:
    """Generate markdown summary from summary data."""
    md = f"# {backlog_id} Session Summary\n\n"
    md += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Session metadata
    metadata = summary_data.get("metadata", {})
    md += f"**Sessions**: {metadata.get('session_count', 0)}\n"
    md += f"**Branch**: {metadata.get('branch', 'unknown')}\n"
    md += f"**Last Activity**: {metadata.get('last_activity', 'unknown')}\n\n"

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

    return md


def summarize_worklog(backlog_id: str) -> Dict[str, Any]:
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

    return 0


if __name__ == "__main__":
    exit(main())
