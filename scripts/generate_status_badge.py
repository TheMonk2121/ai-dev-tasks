#!/usr/bin/env python3
"""
Generate Status Badge

Generates a status badge table for the README showing current validator counts.
"""

import json
import os
from datetime import datetime


def load_metrics() -> dict:
    """Load current validator metrics."""
    metrics_path = "metrics/validator_counts.json"
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            return json.load(f)
    return {}


def generate_status_table() -> str:
    """Generate status table for README."""
    metrics = load_metrics()
    counts = metrics.get("counts", {})

    # Get last updated time
    last_updated = metrics.get("generated_at", "unknown")
    if last_updated != "unknown":
        try:
            # Parse ISO format and format for display
            dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            last_updated = dt.strftime("%Y-%m-%d %H:%M UTC")
        except Exception:
            pass

    table = []
    table.append("## Governance Status")
    table.append("")
    table.append("| Category | Violations | Status |")
    table.append("|----------|------------|--------|")

    categories = ["archive", "shadow_fork", "readme", "multirep"]
    for category in categories:
        count = counts.get(category, 0)
        if count == 0:
            status = "✅ Clean"
        elif count <= 5:
            status = "⚠️ Low"
        elif count <= 20:
            status = "🔶 Medium"
        else:
            status = "🔴 High"

        table.append(f"| {category} | {count} | {status} |")

    table.append("")
    table.append(f"*Last updated: {last_updated}*")
    table.append("")
    table.append(
        "📊 [Weekly Summary](/.github/workflows/nightly.yml) | 📋 [Governance Runbook](400_guides/400_governance-runbook.md)"
    )

    return "\n".join(table)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate status badge table")
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()

    status_table = generate_status_table()

    if args.output:
        with open(args.output, "w") as f:
            f.write(status_table)
        print(f"Status table written to {args.output}")
    else:
        print(status_table)


if __name__ == "__main__":
    main()
