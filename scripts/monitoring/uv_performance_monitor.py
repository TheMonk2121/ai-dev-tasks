from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

#!/usr/bin/env python3
"""
UV Performance Monitor

This script monitors UV performance metrics and provides optimization recommendations.
It tracks installation times, cache hit rates, and dependency resolution performance.
"""

class UVPerformanceMonitor:
    """Monitor UV performance metrics and provide optimization insights."""

    def __init__(self: Any):
        self.metrics_file: Any = Path("metrics/uv_performance.json")
        self.metrics_file.parent.mkdir(exist_ok=True)
        self.metrics: Any = self._load_metrics()

    def _load_metrics(self) -> dict:
        """Load existing performance metrics."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return {
            "install_times": [],
            "resolve_times": [],
            "cache_hits": [],
            "package_counts": [],
            "optimization_recommendations": [],
        }

    def _save_metrics(self: Any):
        """Save metrics to file."""
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)

    def measure_install_time(self, packages: list[str] | None = None) -> float:
        """Measure UV installation time."""
        start_time: Any = time.time()

        try:
            if packages:
                cmd = ["uv", "pip", "install"] + packages
            else:
                cmd = ["uv", "sync"]

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            end_time: Any = time.time()
            install_time = end_time - start_time

            # Record metrics
            self.metrics["install_times"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "duration": install_time,
                    "packages": packages or "all",
                    "success": True,
                }
            )

            return install_time

        except subprocess.CalledProcessError as e:
            end_time: Any = time.time()
            install_time = end_time - start_time

            self.metrics["install_times"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "duration": install_time,
                    "packages": packages or "all",
                    "success": False,
                    "error": str(e),
                }
            )

            raise

    def measure_resolve_time(self) -> float:
        """Measure UV dependency resolution time."""
        start_time: Any = time.time()

        try:
            subprocess.run(["uv", "lock", "--dry-run"], capture_output=True, text=True, check=True)

            end_time: Any = time.time()
            resolve_time = end_time - start_time

            self.metrics["resolve_times"].append(
                {"timestamp": datetime.now().isoformat(), "duration": resolve_time, "success": True}
            )

            return resolve_time

        except subprocess.CalledProcessError as e:
            end_time: Any = time.time()
            resolve_time = end_time - start_time

            self.metrics["resolve_times"].append(
                {"timestamp": datetime.now().isoformat(), "duration": resolve_time, "success": False, "error": str(e)}
            )

            raise

    def check_cache_status(self) -> dict:
        """Check UV cache status and statistics."""
        try:
            # Get cache info
            result: Any = subprocess.run(["uv", "cache", "info"], capture_output=True, text=True, check=True)

            cache_info = {"timestamp": datetime.now().isoformat(), "status": "available", "info": result.stdout}

            self.metrics["cache_hits"].append(cache_info)
            return cache_info

        except subprocess.CalledProcessError:
            cache_info = {
                "timestamp": datetime.now().isoformat(),
                "status": "unavailable",
                "info": "Cache info not available",
            }

            self.metrics["cache_hits"].append(cache_info)
            return cache_info

    def count_packages(self) -> int:
        """Count total packages in the environment."""
        try:
            result: Any = subprocess.run(["uv", "pip", "list"], capture_output=True, text=True, check=True)

            # Count lines (excluding header)
            lines = result.stdout.strip().split("\n")
            package_count = max(0, len(lines) - 2)  # Subtract header lines

            self.metrics["package_counts"].append({"timestamp": datetime.now().isoformat(), "count": package_count})

            return package_count

        except subprocess.CalledProcessError:
            return 0

    def generate_recommendations(self) -> list[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Analyze install times
        if self.metrics["install_times"]:
            recent_installs = [m for m in self.metrics["install_times"][-10:] if m.get("success")]
            if recent_installs:
                avg_install_time = sum(m["duration"] for m in recent_installs) / len(recent_installs)

                if avg_install_time > 10:
                    recommendations.append(
                        f"⚠️ Slow installation detected ({avg_install_time:.1f}s avg). "
                        "Consider using 'uv sync' instead of 'uv pip install' for better performance."
                    )
                elif avg_install_time < 2:
                    recommendations.append(
                        f"✅ Excellent installation performance ({avg_install_time:.1f}s avg). "
                        "UV is performing optimally."
                    )

        # Analyze resolve times
        if self.metrics["resolve_times"]:
            recent_resolves = [m for m in self.metrics["resolve_times"][-5:] if m.get("success")]
            if recent_resolves:
                avg_resolve_time = sum(m["duration"] for m in recent_resolves) / len(recent_resolves)

                if avg_resolve_time > 5:
                    recommendations.append(
                        f"⚠️ Slow dependency resolution ({avg_resolve_time:.1f}s avg). "
                        "Consider updating uv.lock more frequently to avoid complex resolution."
                    )

        # Check package count
        if self.metrics["package_counts"]:
            latest_count = self.metrics["package_counts"][-1]["count"]
            if latest_count > 200:
                recommendations.append(
                    f"📦 Large dependency tree ({latest_count} packages). "
                    "Consider using optional dependency groups to reduce installation time."
                )

        # Cache recommendations
        if self.metrics["cache_hits"]:
            latest_cache = self.metrics["cache_hits"][-1]
            if latest_cache["status"] == "unavailable":
                recommendations.append("💾 UV cache not available. Consider enabling caching for faster installs.")

        # General recommendations
        recommendations.extend(
            [
                "💡 Use 'uv sync' for faster dependency installation",
                "💡 Use 'uvx' for one-off tools to avoid global installations",
                "💡 Run 'uv lock' regularly to keep dependencies up to date",
                "💡 Use dependency groups (--extra dev) to install only what you need",
            ]
        )

        self.metrics["optimization_recommendations"] = recommendations
        return recommendations

    def run_full_analysis(self) -> dict:
        """Run a complete performance analysis."""
        print("🔍 Running UV Performance Analysis...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "install_time": None,
            "resolve_time": None,
            "cache_status": None,
            "package_count": None,
            "recommendations": [],
        }

        try:
            # Measure install time
            print("⏱️ Measuring installation time...")
            analysis["install_time"] = self.measure_install_time()
            print(f"   ✅ Installation: {analysis['install_time']:.2f}s")

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Installation failed: {e}")

        try:
            # Measure resolve time
            print("⏱️ Measuring dependency resolution time...")
            analysis["resolve_time"] = self.measure_resolve_time()
            print(f"   ✅ Resolution: {analysis['resolve_time']:.2f}s")

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Resolution failed: {e}")

        # Check cache status
        print("💾 Checking cache status...")
        analysis["cache_status"] = self.check_cache_status()
        print(f"   ✅ Cache: {analysis['cache_status']['status']}")

        # Count packages
        print("📦 Counting packages...")
        analysis["package_count"] = self.count_packages()
        print(f"   ✅ Packages: {analysis['package_count']}")

        # Generate recommendations
        print("💡 Generating recommendations...")
        analysis["recommendations"] = self.generate_recommendations()

        # Save metrics
        self._save_metrics()

        return analysis

    def print_report(self, analysis: dict):
        """Print a formatted performance report."""
        print("\n" + "=" * 60)
        print("📊 UV PERFORMANCE REPORT")
        print("=" * 60)

        print(f"🕐 Analysis Time: {analysis['timestamp']}")

        if analysis["install_time"]:
            print(f"⏱️ Installation Time: {analysis['install_time']:.2f}s")

        if analysis["resolve_time"]:
            print(f"🔍 Resolution Time: {analysis['resolve_time']:.2f}s")

        if analysis["cache_status"]:
            print(f"💾 Cache Status: {analysis['cache_status']['status']}")

        if analysis["package_count"]:
            print(f"📦 Package Count: {analysis['package_count']}")

        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"   {i}. {rec}")

        print("\n" + "=" * 60)

def main() -> Any:
    """Main function."""
    parser: Any = argparse.ArgumentParser(description="Monitor UV performance metrics")
    parser.add_argument("--install-only", action="store_true", help="Only measure installation time")
    parser.add_argument("--resolve-only", action="store_true", help="Only measure resolution time")
    parser.add_argument("--cache-only", action="store_true", help="Only check cache status")
    parser.add_argument("--packages", nargs="+", help="Specific packages to install for testing")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args: Any = parser.parse_args()

    monitor = UVPerformanceMonitor()

    if args.install_only:
        try:
            install_time: Any = monitor.measure_install_time(args.packages)
            if args.json:
                print(json.dumps({"install_time": install_time}))
            else:
                print(f"⏱️ Installation time: {install_time:.2f}s")
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)

    elif args.resolve_only:
        try:
            resolve_time: Any = monitor.measure_resolve_time()
            if args.json:
                print(json.dumps({"resolve_time": resolve_time}))
            else:
                print(f"🔍 Resolution time: {resolve_time:.2f}s")
        except subprocess.CalledProcessError as e:
            print(f"❌ Resolution failed: {e}")
            sys.exit(1)

    elif args.cache_only:
        cache_status: Any = monitor.check_cache_status()
        if args.json:
            print(json.dumps(cache_status))
        else:
            print(f"💾 Cache status: {cache_status['status']}")

    else:
        # Full analysis
        analysis: Any = monitor.run_full_analysis()

        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            monitor.print_report(analysis)

        # Save metrics
        monitor._save_metrics()

if __name__ == "__main__":
    main()