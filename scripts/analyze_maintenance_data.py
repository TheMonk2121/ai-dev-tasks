#!/usr/bin/env python3
"""
Maintenance Data Analysis Script

Analyzes maintenance data stored in the database following the same pattern
as evaluation metrics analysis. Provides insights into maintenance patterns,
trends, and effectiveness.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from monitoring.maintenance_metrics import MaintenanceMetricsDB
except ImportError:
    print("❌ Error: monitoring.maintenance_metrics module not found")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def analyze_maintenance_trends(db: MaintenanceMetricsDB, days: int = 30) -> dict[str, Any]:
    """Analyze maintenance trends over time."""
    print(f"📊 Analyzing maintenance trends over the last {days} days...")

    # Get maintenance history
    history = db.get_maintenance_history(days=days)

    if not history:
        print("No maintenance data found for the specified period")
        return {}

    # Analyze trends
    trends = {
        "total_sessions": len(history),
        "by_type": {},
        "by_status": {},
        "performance_metrics": {},
        "cache_analysis_insights": [],
    }

    # Group by maintenance type
    for record in history:
        maint_type = record["maintenance_type"]
        if maint_type not in trends["by_type"]:
            trends["by_type"][maint_type] = {
                "count": 0,
                "total_files_removed": 0,
                "total_directories_removed": 0,
                "total_bytes_freed": 0,
                "avg_duration": 0,
                "success_rate": 0,
            }

        trends["by_type"][maint_type]["count"] += 1
        trends["by_type"][maint_type]["total_files_removed"] += record["files_removed"]
        trends["by_type"][maint_type]["total_directories_removed"] += record["directories_removed"]
        trends["by_type"][maint_type]["total_bytes_freed"] += record["bytes_freed"]

        if record["duration_seconds"]:
            trends["by_type"][maint_type]["avg_duration"] += record["duration_seconds"]

    # Calculate averages and success rates
    for maint_type, data in trends["by_type"].items():
        if data["count"] > 0:
            data["avg_duration"] = data["avg_duration"] / data["count"]
            data["avg_files_per_session"] = data["total_files_removed"] / data["count"]
            data["avg_directories_per_session"] = data["total_directories_removed"] / data["count"]
            data["avg_bytes_per_session"] = data["total_bytes_freed"] / data["count"]

    # Group by status
    for record in history:
        status = record["status"]
        if status not in trends["by_status"]:
            trends["by_status"][status] = 0
        trends["by_status"][status] += 1

    # Extract cache analysis insights
    for record in history:
        if record["analysis_data"] and isinstance(record["analysis_data"], dict):
            analysis = record["analysis_data"]
            if "lessons_learned" in analysis:
                trends["cache_analysis_insights"].append(
                    {
                        "timestamp": record["ts"],
                        "session_id": record["session_id"],
                        "lessons": analysis["lessons_learned"],
                    }
                )

    return trends


def print_maintenance_summary(summary: dict[str, Any]) -> None:
    """Print formatted maintenance summary."""
    print("\n" + "=" * 80)
    print("🧹 MAINTENANCE SUMMARY")
    print("=" * 80)
    print(f"Period: {summary['period_days']} days")
    print(f"Total Sessions: {summary['total_sessions']}")
    print(f"Success Rate: {summary['success_rate']}%")
    print()

    if "by_type" in summary:
        print("📈 BY MAINTENANCE TYPE:")
        for maint_type, data in summary["by_type"].items():
            print(f"  {maint_type}:")
            print(f"    Sessions: {data['total_sessions']}")
            print(
                f"    Success Rate: {data['successful_sessions']}/{data['total_sessions']} ({data['successful_sessions']/data['total_sessions']*100:.1f}%)"
            )
            print(f"    Avg Files Removed: {data['avg_files_removed']:.1f}")
            print(f"    Avg Directories Removed: {data['avg_directories_removed']:.1f}")
            print(f"    Avg Bytes Freed: {data['avg_bytes_freed']:,}")
            print(f"    Avg Duration: {data['avg_duration_seconds']:.2f}s")
            print()


def print_trends_analysis(trends: dict[str, Any]) -> None:
    """Print formatted trends analysis."""
    print("\n" + "=" * 80)
    print("📊 MAINTENANCE TRENDS ANALYSIS")
    print("=" * 80)

    print(f"Total Sessions Analyzed: {trends['total_sessions']}")
    print()

    if "by_type" in trends:
        print("📈 BY MAINTENANCE TYPE:")
        for maint_type, data in trends["by_type"].items():
            print(f"  {maint_type}:")
            print(f"    Sessions: {data['count']}")
            print(f"    Avg Files per Session: {data['avg_files_per_session']:.1f}")
            print(f"    Avg Directories per Session: {data['avg_directories_per_session']:.1f}")
            print(f"    Avg Bytes per Session: {data['avg_bytes_per_session']:,}")
            print(f"    Avg Duration: {data['avg_duration']:.2f}s")
            print()

    if "by_status" in trends:
        print("📊 BY STATUS:")
        for status, count in trends["by_status"].items():
            percentage = (count / trends["total_sessions"]) * 100
            print(f"  {status}: {count} ({percentage:.1f}%)")
        print()

    if "cache_analysis_insights" in trends and trends["cache_analysis_insights"]:
        print("🧠 CACHE ANALYSIS INSIGHTS:")
        for insight in trends["cache_analysis_insights"][-5:]:  # Show last 5
            print(f"  Session {insight['session_id']} ({insight['timestamp']}):")
            if "most_compiled_modules" in insight["lessons"]:
                modules = insight["lessons"]["most_compiled_modules"][:3]
                print(f"    Most Compiled: {', '.join(modules)}")
            if "recommendations" in insight["lessons"]:
                recs = insight["lessons"]["recommendations"][:2]
                for rec in recs:
                    print(f"    💡 {rec}")
            print()


def export_analysis_data(trends: dict[str, Any], output_file: str) -> None:
    """Export analysis data to JSON file."""
    export_data = {"analysis_timestamp": datetime.now().isoformat(), "trends": trends}

    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2, default=str)

    print(f"📁 Analysis data exported to: {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze maintenance data from database")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze (default: 30)")
    parser.add_argument("--type", help="Filter by maintenance type (cache_cleanup, log_cleanup, full_cleanup)")
    parser.add_argument("--export", help="Export analysis to JSON file")
    parser.add_argument("--summary-only", action="store_true", help="Show only summary statistics")

    args = parser.parse_args()

    # Initialize database connection
    try:
        db = MaintenanceMetricsDB()
        print("✅ Connected to maintenance metrics database")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

    # Get summary
    print(f"📊 Getting maintenance summary for last {args.days} days...")
    summary = db.get_maintenance_summary(days=args.days)

    if not summary or summary.get("total_sessions", 0) == 0:
        print(f"No maintenance data found for the last {args.days} days")
        return

    # Print summary
    print_maintenance_summary(summary)

    if not args.summary_only:
        # Analyze trends
        trends = analyze_maintenance_trends(db, days=args.days)
        print_trends_analysis(trends)

        # Export if requested
        if args.export:
            export_analysis_data(trends, args.export)

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
