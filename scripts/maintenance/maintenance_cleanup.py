from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
    from monitoring.health_endpoints import HealthEndpointManager
    from monitoring.maintenance_metrics import store_maintenance_analysis
    from monitoring.metrics import get_metrics
        from collections import defaultdict
import json
import glob
            from monitoring.health_endpoints import HealthEndpointManager
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Maintenance Cleanup Script for AI Development Tasks

Automated cleanup script that runs various maintenance tasks:
- Python cache cleanup
- Temporary file cleanup
- Log file rotation
- Database maintenance
- Test artifact cleanup
- Monitoring data cleanup
"""

# Add src directory to Python path for monitoring modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
except ImportError:
    print("⚠️  Monitoring modules not available - some features will be limited")
    store_maintenance_analysis = None

class MaintenanceCleanup:
    """Automated maintenance and cleanup for AI development tasks"""

    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.cleanup_stats = {
            "files_removed": 0,
            "directories_removed": 0,
            "bytes_freed": 0,
            "errors": 0,
        }
        self.start_time = datetime.now()

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ️ ", "WARN": "⚠️ ", "ERROR": "❌", "SUCCESS": "✅"}
        print(f"[{timestamp}] {prefix.get(level, '')} {message}")

    def safe_remove(self, path: str, is_dir: bool = False) -> bool:
        """Safely remove file or directory"""
        try:
            if not os.path.exists(path):
                return True

            if self.dry_run:
                self.log(f"DRY RUN: Would remove {path}", "INFO")
                return True

            if is_dir:
                shutil.rmtree(path)
                self.cleanup_stats["directories_removed"] += 1
            else:
                # Get file size before removal
                try:
                    size = os.path.getsize(path)
                    self.cleanup_stats["bytes_freed"] += size
                except OSError:
                    pass

                os.remove(path)
                self.cleanup_stats["files_removed"] += 1

            if self.verbose:
                self.log(f"Removed: {path}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Failed to remove {path}: {e}", "ERROR")
            self.cleanup_stats["errors"] += 1
            return False

    def cleanup_python_cache(self) -> dict[str, Any]:
        """Clean up Python cache files and directories"""
        self.log("Cleaning up Python cache files...")

        cache_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
        ]

        results = {
            "cache_dirs_removed": 0,
            "pyc_files_removed": 0,
            "bytes_freed": 0,
            "cache_analysis": {
                "total_cache_dirs": 0,
                "total_pyc_files": 0,
                "cache_by_module": {},
                "oldest_cache": None,
                "newest_cache": None,
                "largest_cache_dir": None,
                "cache_summary": [],
            },
        }

        # First pass: analyze cache before removal
        cache_analysis = self._analyze_python_cache()
        results["cache_analysis"] = cache_analysis

        # Log analysis summary
        self._log_cache_analysis(cache_analysis)

        # Save analysis to file for lessons learned
        self._save_cache_analysis(cache_analysis)

        # Second pass: remove cache files
        for root, dirs, files in os.walk("."):
            # Skip virtual environment directories
            if ".venv" in root or ".venv-linux" in root:
                continue

            for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
                if dir_name == "__pycache__":
                    cache_dir = os.path.join(root, dir_name)
                    if self.safe_remove(cache_dir, is_dir=True):
                        results["cache_dirs_removed"] += 1
                    dirs.remove(dir_name)  # Don't recurse into removed directory

        # Find and remove .pyc files
        for root, dirs, files in os.walk("."):
            if ".venv" in root or ".venv-linux" in root:
                continue

            for file_name in files:
                if file_name.endswith((".pyc", ".pyo", ".pyd")):
                    file_path = os.path.join(root, file_name)
                    if self.safe_remove(file_path):
                        results["pyc_files_removed"] += 1

        self.log(
            f"Removed {results['cache_dirs_removed']} cache directories and {results['pyc_files_removed']} .pyc files"
        )
        return results

    def _analyze_python_cache(self) -> dict[str, Any]:
        """Analyze Python cache before removal to capture lessons learned"""
        analysis = {
            "total_cache_dirs": 0,
            "total_pyc_files": 0,
            "cache_by_module": {},
            "oldest_cache": None,
            "newest_cache": None,
            "largest_cache_dir": None,
            "cache_summary": [],
            "module_activity": {},
            "cache_timeline": [],
        }

        cache_timestamps = []
        module_cache_counts = defaultdict(int)
        cache_dir_sizes = {}

        # Analyze __pycache__ directories
        for root, dirs, files in os.walk("."):
            if ".venv" in root or ".venv-linux" in root:
                continue

            for dir_name in dirs[:]:
                if dir_name == "__pycache__":
                    cache_dir = os.path.join(root, dir_name)
                    if os.path.exists(cache_dir):
                        analysis["total_cache_dirs"] += 1

                        # Get directory size
                        dir_size = 0
                        pyc_count = 0
                        try:
                            for file_name in os.listdir(cache_dir):
                                file_path = os.path.join(cache_dir, file_name)
                                if os.path.isfile(file_path):
                                    dir_size += os.path.getsize(file_path)
                                    if file_name.endswith(".pyc"):
                                        pyc_count += 1
                                        analysis["total_pyc_files"] += 1

                                        # Get file modification time
                                        mtime = os.path.getmtime(file_path)
                                        cache_timestamps.append(mtime)

                                        # Track module activity
                                        module_name = root.replace("./", "").replace("/", ".")
                                        module_cache_counts[module_name] += 1
                        except OSError:
                            continue

                        cache_dir_sizes[cache_dir] = dir_size

                        # Track cache timeline
                        try:
                            dir_mtime = os.path.getmtime(cache_dir)
                            analysis["cache_timeline"].append(
                                {
                                    "path": cache_dir,
                                    "size": dir_size,
                                    "pyc_count": pyc_count,
                                    "mtime": dir_mtime,
                                    "module": root.replace("./", "").replace("/", "."),
                                }
                            )
                        except OSError:
                            continue

        # Analyze .pyc files outside __pycache__
        for root, dirs, files in os.walk("."):
            if ".venv" in root or ".venv-linux" in root:
                continue

            for file_name in files:
                if file_name.endswith((".pyc", ".pyo", ".pyd")):
                    file_path = os.path.join(root, file_name)
                    if os.path.exists(file_path):
                        analysis["total_pyc_files"] += 1
                        try:
                            mtime = os.path.getmtime(file_path)
                            cache_timestamps.append(mtime)

                            module_name = root.replace("./", "").replace("/", ".")
                            module_cache_counts[module_name] += 1
                        except OSError:
                            continue

        # Process analysis data
        analysis["cache_by_module"] = dict(module_cache_counts)

        if cache_timestamps:
            analysis["oldest_cache"] = min(cache_timestamps)
            analysis["newest_cache"] = max(cache_timestamps)

        if cache_dir_sizes:
            analysis["largest_cache_dir"] = max(cache_dir_sizes.items(), key=lambda x: x[1])

        # Sort cache timeline by modification time
        analysis["cache_timeline"].sort(key=lambda x: x["mtime"], reverse=True)

        # Create summary
        analysis["cache_summary"] = [
            f"Total cache directories: {analysis['total_cache_dirs']}",
            f"Total .pyc files: {analysis['total_pyc_files']}",
            f"Most active modules: {sorted(module_cache_counts.items(), key=lambda x: x[1], reverse=True)[:5]}",
            (
                f"Cache age range: {self._format_timestamp(analysis['oldest_cache'])} to {self._format_timestamp(analysis['newest_cache'])}"
                if analysis["oldest_cache"]
                else "No cache timestamps found"
            ),
        ]

        return analysis

    def _log_cache_analysis(self, analysis: dict[str, Any]):
        """Log detailed cache analysis for lessons learned"""
        self.log("📊 Python Cache Analysis (before cleanup):")

        # Basic stats
        self.log(f"  • Cache directories: {analysis['total_cache_dirs']}")
        self.log(f"  • .pyc files: {analysis['total_pyc_files']}")

        # Most active modules
        if analysis["cache_by_module"]:
            top_modules = sorted(analysis["cache_by_module"].items(), key=lambda x: x[1], reverse=True)[:5]
            self.log("  • Most active modules:")
            for module, count in top_modules:
                self.log(f"    - {module}: {count} cache files")

        # Cache timeline
        if analysis["cache_timeline"]:
            recent_caches = analysis["cache_timeline"][:3]
            self.log("  • Recent cache activity:")
            for cache in recent_caches:
                self.log(
                    f"    - {cache['module']}: {cache['pyc_count']} files, {self._format_timestamp(cache['mtime'])}"
                )

        # Size analysis
        if analysis["largest_cache_dir"]:
            largest_path, largest_size = analysis["largest_cache_dir"]
            self.log(f"  • Largest cache: {largest_path} ({largest_size:,} bytes)")

    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        if timestamp is None:
            return "Unknown"
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _save_cache_analysis(self, analysis: dict[str, Any]):
        """Save cache analysis to file for lessons learned and debugging"""
        try:

            # Create logs directory if it doesn't exist
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)

            # Create analysis report
            report = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "python_cache_cleanup",
                "summary": {
                    "total_cache_dirs": analysis["total_cache_dirs"],
                    "total_pyc_files": analysis["total_pyc_files"],
                    "oldest_cache": self._format_timestamp(analysis["oldest_cache"]),
                    "newest_cache": self._format_timestamp(analysis["newest_cache"]),
                    "most_active_modules": sorted(
                        analysis["cache_by_module"].items(), key=lambda x: x[1], reverse=True
                    )[:10],
                },
                "detailed_analysis": analysis,
                "lessons_learned": {
                    "most_compiled_modules": self._extract_lessons_from_cache(analysis),
                    "cache_patterns": self._analyze_cache_patterns(analysis),
                    "recommendations": self._generate_cache_recommendations(analysis),
                },
            }

            # Save to file
            filename = f"logs/cache_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)

            if self.verbose:
                self.log(f"Cache analysis saved to: {filename}")

        except Exception as e:
            self.log(f"Failed to save cache analysis: {e}", "WARN")

    def _extract_lessons_from_cache(self, analysis: dict[str, Any]) -> list[str]:
        """Extract lessons learned from cache analysis"""
        lessons = []

        if analysis["total_cache_dirs"] > 50:
            lessons.append("High number of cache directories suggests frequent module compilation")

        if analysis["total_pyc_files"] > 200:
            lessons.append("Large number of .pyc files indicates active development")

        # Check for modules with many cache files
        top_modules = sorted(analysis["cache_by_module"].items(), key=lambda x: x[1], reverse=True)
        if top_modules and top_modules[0][1] > 10:
            lessons.append(f"Module '{top_modules[0][0]}' has {top_modules[0][1]} cache files - consider optimization")

        # Check cache age
        if analysis["oldest_cache"] and analysis["newest_cache"]:
            age_days = (analysis["newest_cache"] - analysis["oldest_cache"]) / (24 * 3600)
            if age_days > 30:
                lessons.append(f"Cache spans {age_days:.1f} days - consider more frequent cleanup")

        return lessons

    def _analyze_cache_patterns(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Analyze patterns in cache data"""
        patterns = {
            "module_distribution": "even" if len(set(analysis["cache_by_module"].values())) <= 2 else "uneven",
            "cache_concentration": "high" if analysis["total_pyc_files"] > 100 else "low",
            "temporal_distribution": (
                "recent"
                if analysis["newest_cache"] and (datetime.now().timestamp() - analysis["newest_cache"]) < 86400
                else "stale"
            ),
        }

        # Analyze module patterns
        if analysis["cache_by_module"]:
            module_counts = list(analysis["cache_by_module"].values())
            patterns["module_variance"] = (
                str(max(module_counts) - min(module_counts)) if len(module_counts) > 1 else "0"
            )

        return patterns

    def _generate_cache_recommendations(self, analysis: dict[str, Any]) -> list[str]:
        """Generate recommendations based on cache analysis"""
        recommendations = []

        if analysis["total_cache_dirs"] > 100:
            recommendations.append("Consider implementing more aggressive cache cleanup schedule")

        if analysis["total_pyc_files"] > 500:
            recommendations.append("High .pyc file count suggests need for automated cleanup")

        # Check for large cache directories
        if analysis["largest_cache_dir"]:
            largest_path, largest_size = analysis["largest_cache_dir"]
            if largest_size > 1024 * 1024:  # > 1MB
                recommendations.append(f"Large cache directory detected: {largest_path} ({largest_size:,} bytes)")

        # Check for stale caches
        if analysis["oldest_cache"]:
            age_days = (datetime.now().timestamp() - analysis["oldest_cache"]) / (24 * 3600)
            if age_days > 7:
                recommendations.append(f"Stale cache detected (oldest: {age_days:.1f} days old)")

        return recommendations

    def cleanup_temporary_files(self) -> dict[str, Any]:
        """Clean up temporary files and directories"""
        self.log("Cleaning up temporary files...")

        temp_patterns = [
            "**/*.tmp",
            "**/*.temp",
            "**/*.log",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.swp",
            "**/*.swo",
            "**/*~",
            "**/.pytest_cache",
            "**/.coverage",
            "**/.mypy_cache",
            "**/.ruff_cache",
        ]

        results = {
            "temp_files_removed": 0,
            "bytes_freed": 0,
        }

        for root, dirs, files in os.walk("."):
            # Skip certain directories
            if any(skip in root for skip in [".venv", ".git", ".hypothesis", "node_modules"]):
                continue

            for file_name in files:
                if any(file_name.endswith(pattern.replace("**/", "")) for pattern in temp_patterns):
                    file_path = os.path.join(root, file_name)
                    if self.safe_remove(file_path):
                        results["temp_files_removed"] += 1

        self.log(f"Removed {results['temp_files_removed']} temporary files")
        return results

    def cleanup_old_logs(self, days_old: int = 7) -> dict[str, Any]:
        """Clean up old log files"""
        self.log(f"Cleaning up log files older than {days_old} days...")

        cutoff_time = datetime.now() - timedelta(days=days_old)
        results = {
            "log_files_removed": 0,
            "bytes_freed": 0,
        }

        log_dirs = ["logs", "traces", ".hypothesis"]

        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue

            for root, dirs, files in os.walk(log_dir):
                for file_name in files:
                    if file_name.endswith((".log", ".json", ".txt")):
                        file_path = os.path.join(root, file_name)
                        try:
                            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                            if file_time < cutoff_time:
                                if self.safe_remove(file_path):
                                    results["log_files_removed"] += 1
                        except OSError:
                            continue

        self.log(f"Removed {results['log_files_removed']} old log files")
        return results

    def cleanup_test_artifacts(self) -> dict[str, Any]:
        """Clean up test artifacts and temporary test files"""
        self.log("Cleaning up test artifacts...")

        test_artifacts = [
            "tests/.pytest_cache",
            "tests/__pycache__",
            "tests/data/temp_*",
            "tests/data/*.tmp",
            ".coverage",
            "htmlcov",
            ".pytest_cache",
        ]

        results = {
            "artifacts_removed": 0,
        }

        for artifact in test_artifacts:
            if os.path.exists(artifact):
                if os.path.isdir(artifact):
                    if self.safe_remove(artifact, is_dir=True):
                        results["artifacts_removed"] += 1
                else:
                    if self.safe_remove(artifact):
                        results["artifacts_removed"] += 1

        self.log(f"Removed {results['artifacts_removed']} test artifacts")
        return results

    def cleanup_monitoring_data(self, days_old: int = 30) -> dict[str, Any]:
        """Clean up old monitoring data and reports"""
        self.log(f"Cleaning up monitoring data older than {days_old} days...")

        cutoff_time = datetime.now() - timedelta(days=days_old)
        results = {
            "monitoring_files_removed": 0,
            "bytes_freed": 0,
        }

        monitoring_patterns = [
            "monitoring_report_*.json",
            "dashboard_report_*.json",
            "final_monitoring_report.json",
            "metrics/baseline_evaluations/*.json",
        ]

        for pattern in monitoring_patterns:
            if "*" in pattern:
                # Handle glob patterns

                for file_path in glob.glob(pattern):
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            if self.safe_remove(file_path):
                                results["monitoring_files_removed"] += 1
                    except OSError:
                        continue
            else:
                # Handle specific files
                if os.path.exists(pattern):
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(pattern))
                        if file_time < cutoff_time:
                            if self.safe_remove(pattern):
                                results["monitoring_files_removed"] += 1
                    except OSError:
                        continue

        self.log(f"Removed {results['monitoring_files_removed']} old monitoring files")
        return results

    def cleanup_hypothesis_cache(self, keep_recent: bool = True) -> dict[str, Any]:
        """Clean up Hypothesis cache while keeping recent examples"""
        self.log("Cleaning up Hypothesis cache...")

        results = {
            "hypothesis_files_removed": 0,
            "bytes_freed": 0,
        }

        hypothesis_dir = ".hypothesis"
        if not os.path.exists(hypothesis_dir):
            return results

        # Keep recent examples but clean up old ones
        examples_dir = os.path.join(hypothesis_dir, "examples")
        if os.path.exists(examples_dir):
            cutoff_time = datetime.now() - timedelta(days=7) if keep_recent else datetime.now()

            for root, dirs, files in os.walk(examples_dir):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    try:
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_time:
                            if self.safe_remove(file_path):
                                results["hypothesis_files_removed"] += 1
                    except OSError:
                        continue

        self.log(f"Removed {results['hypothesis_files_removed']} old Hypothesis cache files")
        return results

    def run_database_maintenance(self) -> dict[str, Any]:
        """Run database maintenance tasks"""
        self.log("Running database maintenance...")

        results = {
            "maintenance_queries_run": 0,
            "errors": 0,
        }

        try:
            # Add database maintenance queries here
            # For now, just check if database is accessible

            health_manager = HealthEndpointManager()
            health_status = health_manager.get_health_status()

            if health_status["status"] == "healthy":
                self.log("Database is healthy - no maintenance needed", "SUCCESS")
            else:
                self.log(f"Database status: {health_status['status']}", "WARN")

        except Exception as e:
            self.log(f"Database maintenance failed: {e}", "ERROR")
            results["errors"] += 1

        return results

    def run_full_cleanup(self) -> dict[str, Any]:
        """Run all cleanup tasks"""
        self.log("Starting full maintenance cleanup...")

        all_results = {}

        # Run all cleanup tasks
        all_results["python_cache"] = self.cleanup_python_cache()
        all_results["temp_files"] = self.cleanup_temporary_files()
        all_results["old_logs"] = self.cleanup_old_logs()
        all_results["test_artifacts"] = self.cleanup_test_artifacts()
        all_results["monitoring_data"] = self.cleanup_monitoring_data()
        all_results["hypothesis_cache"] = self.cleanup_hypothesis_cache()
        all_results["database_maintenance"] = self.run_database_maintenance()

        # Store analysis in database if available
        self._store_analysis_in_database(all_results)

        return all_results

    def _store_analysis_in_database(self, results: dict[str, Any]) -> None:
        """Store maintenance analysis in database if available."""
        if not store_maintenance_analysis:
            self.log("Database integration not available - skipping storage", "WARN")
            return

        try:
            # Generate session ID
            session_id = f"maintenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Calculate total metrics
            total_files = sum(r.get("files_removed", 0) for r in results.values() if isinstance(r, dict))
            total_dirs = sum(r.get("directories_removed", 0) for r in results.values() if isinstance(r, dict))
            total_bytes = sum(r.get("bytes_freed", 0) for r in results.values() if isinstance(r, dict))
            total_errors = sum(r.get("errors", 0) for r in results.values() if isinstance(r, dict))

            # Prepare cleanup results
            cleanup_results = {
                "files_removed": total_files,
                "directories_removed": total_dirs,
                "bytes_freed": total_bytes,
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "error_count": total_errors,
            }

            # Extract analysis data from Python cache cleanup (if available)
            analysis_data = {}
            if "python_cache" in results and isinstance(results["python_cache"], dict):
                analysis_data = results["python_cache"].get("analysis_data", {})

            # Prepare metadata
            metadata = {
                "cleanup_type": "full_cleanup",
                "dry_run": self.dry_run,
                "verbose": self.verbose,
                "individual_results": results,
            }

            # Store in database
            success = store_maintenance_analysis(
                session_id=session_id,
                maintenance_type="full_cleanup",
                cleanup_results=cleanup_results,
                analysis_data=analysis_data,
                metadata=metadata,
            )

            if success:
                self.log(f"Maintenance analysis stored in database (session: {session_id})", "INFO")
            else:
                self.log("Failed to store maintenance analysis in database", "ERROR")

        except Exception as e:
            self.log(f"Error storing maintenance analysis: {e}", "ERROR")

    def print_summary(self, results: dict[str, Any]):
        """Print cleanup summary"""
        duration = datetime.now() - self.start_time

        print("\n" + "=" * 60)
        print("🧹 MAINTENANCE CLEANUP SUMMARY")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print(f"Files removed: {self.cleanup_stats['files_removed']}")
        print(f"Directories removed: {self.cleanup_stats['directories_removed']}")
        print(f"Bytes freed: {self.cleanup_stats['bytes_freed']:,}")
        print(f"Errors: {self.cleanup_stats['errors']}")

        if self.cleanup_stats["bytes_freed"] > 0:
            mb_freed = self.cleanup_stats["bytes_freed"] / (1024 * 1024)
            print(f"Space freed: {mb_freed:.2f} MB")

        print("=" * 60)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Development Tasks Maintenance Cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without actually cleaning")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--python-cache", action="store_true", help="Clean Python cache only")
    parser.add_argument("--temp-files", action="store_true", help="Clean temporary files only")
    parser.add_argument("--logs", action="store_true", help="Clean old logs only")
    parser.add_argument("--test-artifacts", action="store_true", help="Clean test artifacts only")
    parser.add_argument("--monitoring", action="store_true", help="Clean monitoring data only")
    parser.add_argument("--hypothesis", action="store_true", help="Clean Hypothesis cache only")
    parser.add_argument("--database", action="store_true", help="Run database maintenance only")
    parser.add_argument("--days", type=int, default=7, help="Age threshold for log files (default: 7 days)")

    args = parser.parse_args()

    cleanup = MaintenanceCleanup(dry_run=args.dry_run, verbose=args.verbose)

    if args.dry_run:
        cleanup.log("Running in DRY RUN mode - no files will be actually removed", "WARN")

    # Run specific cleanup tasks or full cleanup
    if any(
        [
            args.python_cache,
            args.temp_files,
            args.logs,
            args.test_artifacts,
            args.monitoring,
            args.hypothesis,
            args.database,
        ]
    ):
        results = {}
        if args.python_cache:
            results["python_cache"] = cleanup.cleanup_python_cache()
        if args.temp_files:
            results["temp_files"] = cleanup.cleanup_temporary_files()
        if args.logs:
            results["old_logs"] = cleanup.cleanup_old_logs(args.days)
        if args.test_artifacts:
            results["test_artifacts"] = cleanup.cleanup_test_artifacts()
        if args.monitoring:
            results["monitoring_data"] = cleanup.cleanup_monitoring_data(args.days)
        if args.hypothesis:
            results["hypothesis_cache"] = cleanup.cleanup_hypothesis_cache()
        if args.database:
            results["database_maintenance"] = cleanup.run_database_maintenance()
    else:
        # Run full cleanup
        results = cleanup.run_full_cleanup()

    cleanup.print_summary(results)

if __name__ == "__main__":
    main()
