#!/usr/bin/env python3.12.123.11
"""
Validator Metrics Generator

Reads validator_report.json and emits metrics/validator_counts.json with:
- Current violation counts per category
- Top impacted files
- Schema version and timestamp
"""

import json
import sys
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any


def load_validator_report(report_path: str = "validator_report.json") -> dict[str, Any]:
    """Load validator report from JSON file."""
    try:
        with open(report_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Validator report not found: {report_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in validator report: {e}")
        sys.exit(1)


def generate_metrics(report: dict[str, Any]) -> dict[str, Any]:
    """Generate metrics from validator report."""
    categories = report.get("categories", {})
    impacted_files = report.get("impacted_files", {})

    # Extract counts
    counts = {}
    for category, info in categories.items():
        counts[category] = info.get("violations", 0)

    # Extract top impacted files (limit to 10 per category)
    top_impacted = {}
    for category, files in impacted_files.items():
        if files:
            # Sort by filename for consistent ordering
            sorted_files = sorted(files)[:10]
            top_impacted[category] = sorted_files

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat() + "Z",
        "counts": counts,
        "top_impacted": top_impacted,
    }


def save_metrics(metrics: dict[str, Any], output_path: str = "metrics/validator_counts.json"):
    """Save metrics to JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Metrics saved to: {output_file}")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate validator metrics")
    parser.add_argument("--input", default="validator_report.json", help="Input validator report")
    parser.add_argument("--output", default="metrics/validator_counts.json", help="Output metrics file")
    parser.add_argument("--print", action="store_true", help="Print metrics to stdout")

    args = parser.parse_args()

    # Load validator report
    report = load_validator_report(args.input)

    # Generate metrics
    metrics = generate_metrics(report)

    # Save metrics
    save_metrics(metrics, args.output)

    # Print if requested
    if args.print:
        print(json.dumps(metrics, indent=2))

    # Print summary
    counts = metrics["counts"]
    print("\n📊 Validator Metrics Summary:")
    for category, count in counts.items():
        status = "✅" if count == 0 else "❌"
        print(f"  {category}: {count} violations {status}")


if __name__ == "__main__":
    main()
