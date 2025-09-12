from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Cache Analysis Trends Script

Analyzes multiple cache analysis files to identify patterns and trends
in Python cache usage over time. Useful for understanding development
patterns and optimizing cleanup schedules.
"""

class CacheTrendAnalyzer:
    """Analyzes cache trends from multiple analysis files"""

    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        self.analysis_files = self._find_analysis_files()

    def _find_analysis_files(self) -> list[str]:
        """Find all cache analysis files"""
        analysis_files = []
        if not os.path.exists(self.logs_dir):
            return analysis_files

        for file_name in os.listdir(self.logs_dir):
            if file_name.startswith("cache_analysis_") and file_name.endswith(".json"):
                analysis_files.append(os.path.join(self.logs_dir, file_name))

        return sorted(analysis_files)

    def load_analysis_data(self) -> list[dict[str, Any]]:
        """Load all analysis data from files"""
        data = []
        for file_path in self.analysis_files:
            try:
                with open(file_path) as f:
                    analysis = json.load(f)
                    data.append(analysis)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"⚠️  Error loading {file_path}: {e}")
                continue
        return data

    def analyze_trends(self) -> dict[str, Any]:
        """Analyze trends across multiple cache analyses"""
        data = self.load_analysis_data()
        if not data:
            return {"error": "No analysis data found"}

        trends = {
            "total_analyses": len(data),
            "time_span": self._calculate_time_span(data),
            "cache_growth": self._analyze_cache_growth(data),
            "module_activity": self._analyze_module_activity(data),
            "cleanup_frequency": self._analyze_cleanup_frequency(data),
            "recommendations": self._generate_trend_recommendations(data),
            "insights": self._extract_insights(data),
        }

        return trends

    def _calculate_time_span(self, data: list[dict[str, Any]]) -> dict[str, str | int]:
        """Calculate the time span of analyses"""
        timestamps = [datetime.fromisoformat(d["timestamp"]) for d in data]
        return {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat(),
            "duration_days": int((max(timestamps) - min(timestamps)).days),
        }

    def _analyze_cache_growth(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze cache growth patterns"""
        cache_dirs = [d["summary"]["total_cache_dirs"] for d in data]
        pyc_files = [d["summary"]["total_pyc_files"] for d in data]

        return {
            "cache_dirs": {
                "min": min(cache_dirs),
                "max": max(cache_dirs),
                "avg": sum(cache_dirs) / len(cache_dirs),
                "trend": "increasing" if cache_dirs[-1] > cache_dirs[0] else "decreasing",
            },
            "pyc_files": {
                "min": min(pyc_files),
                "max": max(pyc_files),
                "avg": sum(pyc_files) / len(pyc_files),
                "trend": "increasing" if pyc_files[-1] > pyc_files[0] else "decreasing",
            },
        }

    def _analyze_module_activity(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze module activity patterns"""
        all_modules = {}

        for analysis in data:
            modules = analysis["summary"]["most_active_modules"]
            for module, count in modules:
                if module not in all_modules:
                    all_modules[module] = []
                all_modules[module].append(count)

        # Calculate module statistics
        module_stats = {}
        for module, counts in all_modules.items():
            module_stats[module] = {
                "appearances": len(counts),
                "avg_count": sum(counts) / len(counts),
                "max_count": max(counts),
                "frequency": len(counts) / len(data) * 100,
            }

        # Sort by frequency and average count
        most_frequent = sorted(module_stats.items(), key=lambda x: x[1]["frequency"], reverse=True)[:10]
        most_active = sorted(module_stats.items(), key=lambda x: x[1]["avg_count"], reverse=True)[:10]

        return {
            "total_unique_modules": len(all_modules),
            "most_frequent_modules": most_frequent,
            "most_active_modules": most_active,
            "module_stats": module_stats,
        }

    def _analyze_cleanup_frequency(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze cleanup frequency patterns"""
        timestamps = [datetime.fromisoformat(d["timestamp"]) for d in data]
        intervals = []

        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i - 1]
            intervals.append(interval.total_seconds() / 3600)  # Convert to hours

        if not intervals:
            return {"error": "Not enough data points for frequency analysis"}

        return {
            "avg_interval_hours": sum(intervals) / len(intervals),
            "min_interval_hours": min(intervals),
            "max_interval_hours": max(intervals),
            "total_cleanups": len(data),
            "intervals": intervals,
        }

    def _generate_trend_recommendations(self, data: list[dict[str, Any]]) -> list[str]:
        """Generate recommendations based on trends"""
        recommendations = []

        # Analyze cache growth
        cache_growth = self._analyze_cache_growth(data)
        if cache_growth["cache_dirs"]["trend"] == "increasing":
            recommendations.append("Cache directories are growing - consider more frequent cleanup")

        if cache_growth["pyc_files"]["trend"] == "increasing":
            recommendations.append("Python cache files are growing - consider automated cleanup")

        # Analyze cleanup frequency
        cleanup_freq = self._analyze_cleanup_frequency(data)
        if "avg_interval_hours" in cleanup_freq:
            if cleanup_freq["avg_interval_hours"] > 24:
                recommendations.append("Cleanup frequency is low - consider daily cleanup")
            elif cleanup_freq["avg_interval_hours"] < 1:
                recommendations.append("Cleanup frequency is very high - consider less frequent cleanup")

        # Analyze module activity
        module_activity = self._analyze_module_activity(data)
        if module_activity["total_unique_modules"] > 50:
            recommendations.append("High module diversity - consider module-specific cleanup strategies")

        return recommendations

    def _extract_insights(self, data: list[dict[str, Any]]) -> list[str]:
        """Extract key insights from the data"""
        insights = []

        # Cache growth insights
        cache_growth = self._analyze_cache_growth(data)
        if cache_growth["cache_dirs"]["max"] > 100:
            insights.append(f"Peak cache directories: {cache_growth['cache_dirs']['max']} (high development activity)")

        if cache_growth["pyc_files"]["max"] > 500:
            insights.append(f"Peak .pyc files: {cache_growth['pyc_files']['max']} (intensive compilation)")

        # Module activity insights
        module_activity = self._analyze_module_activity(data)
        if module_activity["most_frequent_modules"]:
            top_module = module_activity["most_frequent_modules"][0]
            insights.append(
                f"Most frequently compiled module: {top_module[0]} ({top_module[1]['frequency']:.1f}% of cleanups)"
            )

        # Time-based insights
        time_span = self._calculate_time_span(data)
        duration_days = time_span["duration_days"]
        if isinstance(duration_days, int) and duration_days > 30:
            insights.append(f"Analysis spans {duration_days} days - good for trend analysis")

        return insights

    def print_trend_report(self, trends: dict[str, Any]):
        """Print a comprehensive trend report"""
        print("=" * 80)
        print("📊 PYTHON CACHE TREND ANALYSIS REPORT")
        print("=" * 80)

        if "error" in trends:
            print(f"❌ Error: {trends['error']}")
            return

        # Basic statistics
        print("\n📈 OVERVIEW")
        print(f"  • Total analyses: {trends['total_analyses']}")
        print(f"  • Time span: {trends['time_span']['start']} to {trends['time_span']['end']}")
        print(f"  • Duration: {trends['time_span']['duration_days']} days")

        # Cache growth
        print("\n📊 CACHE GROWTH PATTERNS")
        cache_growth = trends["cache_growth"]
        print(
            f"  • Cache directories: {cache_growth['cache_dirs']['min']}-{cache_growth['cache_dirs']['max']} (avg: {cache_growth['cache_dirs']['avg']:.1f})"
        )
        print(
            f"  • .pyc files: {cache_growth['pyc_files']['min']}-{cache_growth['pyc_files']['max']} (avg: {cache_growth['pyc_files']['avg']:.1f})"
        )
        print(
            f"  • Trend: {cache_growth['cache_dirs']['trend']} directories, {cache_growth['pyc_files']['trend']} files"
        )

        # Module activity
        print("\n🔧 MODULE ACTIVITY")
        module_activity = trends["module_activity"]
        print(f"  • Unique modules: {module_activity['total_unique_modules']}")
        print("  • Most frequent modules:")
        for module, stats in module_activity["most_frequent_modules"][:5]:
            print(f"    - {module}: {stats['frequency']:.1f}% frequency, {stats['avg_count']:.1f} avg files")

        # Cleanup frequency
        if "error" not in trends["cleanup_frequency"]:
            cleanup_freq = trends["cleanup_frequency"]
            print("\n⏰ CLEANUP FREQUENCY")
            print(f"  • Average interval: {cleanup_freq['avg_interval_hours']:.1f} hours")
            print(f"  • Range: {cleanup_freq['min_interval_hours']:.1f}-{cleanup_freq['max_interval_hours']:.1f} hours")
            print(f"  • Total cleanups: {cleanup_freq['total_cleanups']}")

        # Insights
        print("\n💡 KEY INSIGHTS")
        for insight in trends["insights"]:
            print(f"  • {insight}")

        # Recommendations
        print("\n🎯 RECOMMENDATIONS")
        for rec in trends["recommendations"]:
            print(f"  • {rec}")

        print("=" * 80)

    def save_trend_report(self, trends: dict[str, Any], filename: str | None = None) -> str:
        """Save trend report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/cache_trends_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(trends, f, indent=2, default=str)

        return filename

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Analyze Python cache trends")
    parser.add_argument("--logs-dir", default="logs", help="Directory containing cache analysis files")
    parser.add_argument("--save-report", action="store_true", help="Save trend report to file")
    parser.add_argument("--output-file", help="Output file for trend report")

    args = parser.parse_args()

    analyzer = CacheTrendAnalyzer(logs_dir=args.logs_dir)
    trends = analyzer.analyze_trends()

    analyzer.print_trend_report(trends)

    if args.save_report:
        filename = analyzer.save_trend_report(trends, args.output_file)
        print(f"\n📄 Trend report saved to: {filename}")

if __name__ == "__main__":
    main()
