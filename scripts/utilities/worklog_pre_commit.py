from __future__ import annotations

import json
from pathlib import Path

from worklog_summarizer import generate_markdown_summary, summarize_worklog

#!/usr/bin/env python3
"""
Pre-commit worklog summarization
--------------------------------
Automatically generates worklog summaries when scribe sessions are active.
Designed to be called from pre-commit hooks or manually.
"""

def check_active_scribe_session() -> str | None:
    """Check if there's an active scribe session and return backlog ID."""
    state_file = Path(".ai_state.json")

    if not state_file.exists():
        return None

    try:
        with open(state_file) as f:
            state = json.load(f)

        backlog_id = state.get("backlog_id")
        if not backlog_id:
            return None

        # Check if worklog exists
        worklog_path = Path(f"artifacts/worklogs/{backlog_id}.md")
        if not worklog_path.exists():
            return None

        return backlog_id

    except Exception:
        return None

def main():
    """Main function for pre-commit worklog summarization."""
    print("📝 Checking for active scribe session...")

    backlog_id = check_active_scribe_session()
    if not backlog_id:
        print("ℹ️  No active scribe session found")
        return 0

    print(f"📊 Generating worklog summary for {backlog_id}...")

    try:
        # Generate summary
        summary = summarize_worklog(backlog_id)

        if "error" in summary:
            print(f"❌ Error generating summary: {summary['error']}")
            return 1

        # Create summaries directory
        summaries_dir = Path("artifacts/summaries")
        summaries_dir.mkdir(exist_ok=True)

        # Generate markdown summary
        summary_path = summaries_dir / f"{backlog_id}-summary.md"
        content = generate_markdown_summary(backlog_id, summary)
        summary_path.write_text(content, encoding="utf-8")

        print(f"✅ Summary generated: {summary_path}")
        print(f"📊 Ideas: {len(summary['ideas'])}")
        print(f"🎯 Decisions: {len(summary['decisions'])}")
        print(f"📁 Files: {len(summary['files_modified'])}")
        print(f"📋 Next Steps: {len(summary['next_steps'])}")

        return 0

    except Exception as e:
        print(f"❌ Error in worklog summarization: {e}")
        return 1

if __name__ == "__main__":
    exit(main())