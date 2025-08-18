#!/usr/bin/env python3
"""
XRef Hotspots Analysis

Analyzes validator_report.json to group multirep violations by top-level directory
and identify cleanup hotspots for targeted XRef remediation.
"""

import json
import os
from collections import defaultdict
from typing import Dict, List, Tuple


def load_validator_report() -> Dict:
    """Load validator report."""
    report_path = "validator_report.json"

    if not os.path.exists(report_path):
        print("❌ Validator report not found. Run validator first.")
        return {}

    with open(report_path) as f:
        return json.load(f)


def analyze_hotspots(report: Dict) -> Dict[str, List[str]]:
    """Analyze multirep violations by top-level directory."""
    violations = report.get("impacted_files", {}).get("multirep", [])

    # Group by top-level directory
    hotspots = defaultdict(list)

    for violation in violations:
        # Convert absolute path to relative if needed
        rel_path = violation
        if violation.startswith("/"):
            cwd = os.getcwd()
            if violation.startswith(cwd):
                rel_path = violation[len(cwd) :].lstrip("/")

        # Get top-level directory
        top_dir = rel_path.split("/")[0] if "/" in rel_path else rel_path
        hotspots[top_dir].append(rel_path)

    return dict(hotspots)


def print_hotspots(hotspots: Dict[str, List[str]], top_n: int = 10):
    """Print hotspots analysis."""
    print("## XRef Hotspots Analysis")
    print()

    # Sort by violation count
    sorted_hotspots = sorted(hotspots.items(), key=lambda x: len(x[1]), reverse=True)

    print("| Directory | Violations | Files |")
    print("|-----------|------------|-------|")

    for directory, files in sorted_hotspots[:top_n]:
        print(f"| {directory} | {len(files)} | {', '.join(files[:3])}{'...' if len(files) > 3 else ''} |")

    print()
    print(f"**Total violations**: {sum(len(files) for files in hotspots.values())}")
    print(f"**Top directories**: {', '.join(d[0] for d in sorted_hotspots[:5])}")

    return sorted_hotspots


def generate_cleanup_plan(hotspots: Dict[str, List[str]]) -> List[Tuple[str, List[str]]]:
    """Generate cleanup plan for top directories."""
    sorted_hotspots = sorted(hotspots.items(), key=lambda x: len(x[1]), reverse=True)

    print("## Cleanup Plan")
    print()
    print("**Pass A (High-confidence auto-links)**:")
    print("Target top 3-4 directories with highest violation counts:")

    cleanup_plan = []
    for i, (directory, files) in enumerate(sorted_hotspots[:4]):
        print(f"{i+1}. `{directory}/` - {len(files)} violations")
        cleanup_plan.append((directory, files))

    print()
    print("**Pass B (Short-lived ledger for residue)**:")
    print("Generate 7-day expiry ledger entries for remaining low-confidence cases")

    return cleanup_plan


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze XRef violations by directory")
    parser.add_argument("--top", type=int, default=10, help="Number of top directories to show")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    print("🔍 Loading validator report...")
    report = load_validator_report()

    if not report:
        return

    print("📊 Analyzing XRef hotspots...")
    hotspots = analyze_hotspots(report)

    if not hotspots:
        print("✅ No multirep violations found")
        return

    # Print analysis
    sorted_hotspots = print_hotspots(hotspots, args.top)

    # Generate cleanup plan
    cleanup_plan = generate_cleanup_plan(hotspots)

    # JSON output
    if args.json:
        results = {
            "total_violations": sum(len(files) for files in hotspots.values()),
            "hotspots": {k: len(v) for k, v in hotspots.items()},
            "cleanup_plan": [{"directory": d, "violations": len(f), "files": f[:5]} for d, f in cleanup_plan],
        }
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
