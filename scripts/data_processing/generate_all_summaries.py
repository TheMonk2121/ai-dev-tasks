from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any
    import re
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Generate All Summaries - Batch summary generation for Scribe worklogs
---------------------------------------------------------------------
Automatically generates summaries for all active worklogs with proper
memory rehydration tags and graph integration metadata.

This script ensures all Scribe data is properly integrated into the
memory rehydration system and graph visualization.
"""

def get_active_worklogs() -> list[str]:
    """Get all active worklog files."""
    worklog_dir = Path("artifacts/worklogs")
    if not worklog_dir.exists():
        return []

    worklog_files = list(worklog_dir.glob("*.md"))
    return [f.stem for f in worklog_files]  # Return just the backlog IDs

def get_existing_summaries() -> list[str]:
    """Get all existing summary files."""
    summaries_dir = Path("artifacts/summaries")
    if not summaries_dir.exists():
        return []

    summary_files = list(summaries_dir.glob("*-summary.md"))
    return [f.stem.replace("-summary", "") for f in summary_files]

def needs_summary(backlog_id: str) -> bool:
    """Check if a worklog needs a summary generated."""
    worklog_path = Path(f"artifacts/worklogs/{backlog_id}.md")
    summary_path = Path(f"artifacts/summaries/{backlog_id}-summary.md")

    # If no summary exists, it needs one
    if not summary_path.exists():
        return True

    # If worklog is newer than summary, it needs updating
    if worklog_path.exists() and summary_path.exists():
        worklog_mtime = worklog_path.stat().st_mtime
        summary_mtime = summary_path.stat().st_mtime
        return worklog_mtime > summary_mtime

    return False

def generate_summary(backlog_id: str, force: bool = False) -> dict[str, Any]:
    """Generate summary for a specific backlog ID."""
    try:
        if not force and not needs_summary(backlog_id):
            return {"status": "skipped", "reason": "up to date"}

        # Run the worklog summarizer
        result = subprocess.run(
            [sys.executable, "scripts/worklog_summarizer.py", "--backlog-id", backlog_id, "--quiet"],
            capture_output=True,
            text=True,
            cwd=Path.cwd(),
        )

        if result.returncode == 0:
            return {"status": "success", "backlog_id": backlog_id}
        else:
            return {"status": "error", "backlog_id": backlog_id, "error": result.stderr}

    except Exception as e:
        return {"status": "error", "backlog_id": backlog_id, "error": str(e)}

def update_memory_rehydration_integration() -> dict[str, Any]:
    """Ensure summaries are properly integrated into memory rehydration."""
    try:
        # Check if summaries directory is in memory rehydrator
        memory_rehydrator_path = Path("src/utils/memory_rehydrator.py")

        if not memory_rehydrator_path.exists():
            return {"status": "error", "error": "Memory rehydrator not found"}

        content = memory_rehydrator_path.read_text()

        if "artifacts/summaries/" not in content:
            return {"status": "error", "error": "Summaries not integrated into memory rehydrator"}

        return {"status": "success", "message": "Summaries properly integrated"}

    except Exception as e:
        return {"status": "error", "error": str(e)}

def generate_graph_integration_report() -> dict[str, Any]:
    """Generate a report on graph integration status."""
    try:
        summaries_dir = Path("artifacts/summaries")
        if not summaries_dir.exists():
            return {"status": "error", "error": "Summaries directory not found"}

        summary_files = list(summaries_dir.glob("*-summary.md"))

        graph_nodes = []
        for summary_file in summary_files:
            content = summary_file.read_text()

            # Extract graph metadata
            node_type_match = re.search(r"GRAPH_NODE_TYPE:\s*(\w+)", content)
            category_match = re.search(r"GRAPH_CATEGORY:\s*(\w+)", content)
            weight_match = re.search(r"GRAPH_WEIGHT:\s*(\d+)", content)

            if node_type_match and category_match and weight_match:
                graph_nodes.append(
                    {
                        "file": summary_file.name,
                        "node_type": node_type_match.group(1),
                        "category": category_match.group(1),
                        "weight": int(weight_match.group(1)),
                    }
                )

        return {"status": "success", "total_nodes": len(graph_nodes), "nodes": graph_nodes}

    except Exception as e:
        return {"status": "error", "error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Generate summaries for all active worklogs")
    parser.add_argument("--force", action="store_true", help="Force regeneration of all summaries")
    parser.add_argument("--backlog-id", help="Generate summary for specific backlog ID only")
    parser.add_argument("--check-integration", action="store_true", help="Check memory rehydration integration")
    parser.add_argument("--graph-report", action="store_true", help="Generate graph integration report")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")

    args = parser.parse_args()

    if not args.quiet:
        print("🔍 Generating summaries for all active worklogs...")
        print("=" * 60)

    # Handle specific backlog ID
    if args.backlog_id:
        result = generate_summary(args.backlog_id, args.force)
        if not args.quiet:
            if result["status"] == "success":
                print(f"✅ Generated summary for {args.backlog_id}")
            else:
                print(f"❌ Failed to generate summary for {args.backlog_id}: {result.get('error', 'Unknown error')}")
        return 0 if result["status"] == "success" else 1

    # Get all active worklogs
    active_worklogs = get_active_worklogs()
    if not active_worklogs:
        if not args.quiet:
            print("❌ No active worklogs found")
        return 1

    if not args.quiet:
        print(f"📋 Found {len(active_worklogs)} active worklogs")

    # Generate summaries
    results = []
    for backlog_id in active_worklogs:
        result = generate_summary(backlog_id, args.force)
        results.append(result)

        if not args.quiet:
            if result["status"] == "success":
                print(f"✅ {backlog_id}: Summary generated")
            elif result["status"] == "skipped":
                print(f"⏭️  {backlog_id}: {result['reason']}")
            else:
                print(f"❌ {backlog_id}: {result.get('error', 'Unknown error')}")

    # Check integration
    if args.check_integration or not args.quiet:
        if not args.quiet:
            print("\n🔗 Checking memory rehydration integration...")

        integration_result = update_memory_rehydration_integration()
        if not args.quiet:
            if integration_result["status"] == "success":
                print(f"✅ {integration_result['message']}")
            else:
                print(f"❌ Integration check failed: {integration_result['error']}")

    # Generate graph report
    if args.graph_report or not args.quiet:
        if not args.quiet:
            print("\n📊 Generating graph integration report...")

        graph_result = generate_graph_integration_report()
        if not args.quiet:
            if graph_result["status"] == "success":
                print(f"✅ Graph integration: {graph_result['total_nodes']} nodes ready")
                for node in graph_result["nodes"][:5]:  # Show first 5
                    print(f"   - {node['file']}: {node['node_type']}/{node['category']} (weight: {node['weight']})")
                if len(graph_result["nodes"]) > 5:
                    print(f"   ... and {len(graph_result['nodes']) - 5} more")
            else:
                print(f"❌ Graph report failed: {graph_result['error']}")

    # Summary
    success_count = sum(1 for r in results if r["status"] == "success")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    error_count = sum(1 for r in results if r["status"] == "error")

    if not args.quiet:
        print("\n" + "=" * 60)
        print(f"📊 Summary: {success_count} generated, {skipped_count} skipped, {error_count} errors")

        if success_count > 0:
            print("✅ All summaries now include:")
            print("   - Memory rehydration tags for DSPy integration")
            print("   - Timestamp tracking for creation and updates")
            print("   - Graph visualization metadata")
            print("   - Cross-reference linking")
            print("   - Role-based context assignment")

    return 0 if error_count == 0 else 1

if __name__ == "__main__":

    exit(main())
