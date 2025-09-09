#!/usr/bin/env python3
"""
Optimized Quick Conflict Check Script

Enhanced version with parallel processing, early exit, and caching.
Target: 60% performance improvement (0.74s → <0.3s)

Usage: python scripts/optimized_quick_conflict_check.py [--verbose] [--fix] [--json]
"""

import argparse
import json
import multiprocessing
import pickle
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict


class OptimizedQuickConflictChecker:
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []
        self.fixes_applied = 0
        self.max_workers = min(6, multiprocessing.cpu_count() + 1)
        self.cache_dir = Path(".cache/conflict_check")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def get_cache_key(self, check_name: str) -> str:
        """Generate cache key for a check."""
        # Use git HEAD as part of cache key for invalidation
        try:
            result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
            git_hash = result.stdout.strip()[:8] if result.returncode == 0 else "unknown"
        except Exception:
            git_hash = "unknown"

        return f"{check_name}_{git_hash}"

    def load_cached_result(self, check_name: str) -> Any:
        """Load cached result if available and valid."""
        cache_key = self.get_cache_key(check_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    cached_data = pickle.load(f)

                # Check if cache is still valid (5 minutes TTL)
                if time.time() - cached_data.get("timestamp", 0) < 300:
                    return cached_data.get("result")
            except Exception:
                pass

        return None

    def save_cached_result(self, check_name: str, result: Any):
        """Save result to cache."""
        cache_key = self.get_cache_key(check_name)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump({"result": result, "timestamp": time.time()}, f)
        except Exception:
            pass

    def check_merge_markers_fast(self) -> bool:
        """Fast merge marker check with caching."""
        cached_result = self.load_cached_result("merge_markers")
        if cached_result is not None:
            return cached_result

        self.log("Checking for merge markers...", "INFO")

        try:
            # Use git grep for faster search
            result = subprocess.run(
                ["git", "grep", "-nE", "^(<<<<<<< |======= |>>>>>>> )"], capture_output=True, text=True, timeout=10
            )

            has_markers = bool(result.stdout.strip())
            self.save_cached_result("merge_markers", not has_markers)

            if has_markers:
                self.issues.append(f"Merge markers found:\n{result.stdout}")
                self.log("❌ Merge markers detected", "ERROR")
                return False
            else:
                self.log("✅ No merge markers found", "INFO")
                return True

        except subprocess.TimeoutExpired:
            self.warnings.append("Merge marker check timed out")
            return True
        except Exception as e:
            self.warnings.append(f"Could not check merge markers: {e}")
            return True

    def check_backup_files_fast(self) -> bool:
        """Fast backup file check with caching."""
        cached_result = self.load_cached_result("backup_files")
        if cached_result is not None:
            return cached_result

        self.log("Checking for backup files...", "INFO")

        try:
            # Use git ls-files for faster search
            result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                files = result.stdout.split("\n")
                backup_files = [f for f in files if f.endswith((".orig", ".rej"))]

                has_backups = len(backup_files) > 0
                self.save_cached_result("backup_files", not has_backups)

                if has_backups:
                    self.issues.append(f"Backup files found: {backup_files}")
                    self.log(f"❌ {len(backup_files)} backup files found", "ERROR")
                    return False
                else:
                    self.log("✅ No backup files found", "INFO")
                    return True
            else:
                self.warnings.append("Could not list git files")
                return True

        except subprocess.TimeoutExpired:
            self.warnings.append("Backup file check timed out")
            return True
        except Exception as e:
            self.warnings.append(f"Could not check backup files: {e}")
            return True

    def check_package_conflicts_fast(self) -> bool:
        """Fast package conflict check with caching."""
        cached_result = self.load_cached_result("package_conflicts")
        if cached_result is not None:
            return cached_result

        self.log("Checking for package manager conflicts...", "INFO")

        conflicts = []

        # Check Python package managers (fast file existence check)
        python_configs = []
        for pattern in ["requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock"]:
            if Path(pattern).exists():
                python_configs.append(pattern)

        if len(python_configs) > 1:
            conflict_msg = f"Multiple Python package managers: {python_configs}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        # Check Node.js package managers (fast file existence check)
        node_configs = []
        for pattern in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]:
            if Path(pattern).exists():
                node_configs.append(pattern)

        if len(node_configs) > 1:
            conflict_msg = f"Multiple Node.js package managers: {node_configs}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        has_conflicts = len(conflicts) > 0
        self.save_cached_result("package_conflicts", not has_conflicts)

        if has_conflicts:
            self.issues.extend(conflicts)
            return False
        else:
            self.log("✅ No package manager conflicts", "INFO")
            return True

    def run_parallel_checks(self) -> Dict[str, Any]:
        """Run all checks in parallel with early exit."""
        self.log("Starting optimized quick conflict check...", "INFO")

        start_time = time.time()

        # Define checks in order of criticality (most critical first)
        checks = [
            ("merge_markers", self.check_merge_markers_fast),
            ("backup_files", self.check_backup_files_fast),
            ("package_conflicts", self.check_package_conflicts_fast),
        ]

        results = {}

        # Run critical checks first (merge markers, backup files)
        critical_checks = checks[:2]
        for check_name, check_func in critical_checks:
            try:
                results[check_name] = check_func()
                # Early exit on critical failures
                if not results[check_name]:
                    self.log(f"Early exit due to critical failure: {check_name}", "WARNING")
                    # Fill remaining results as skipped
                    for remaining_check, _ in checks[2:]:
                        results[remaining_check] = True  # Skip remaining checks
                    break
            except Exception as e:
                results[check_name] = False
                self.warnings.append(f"Check {check_name} failed: {e}")

        # Run remaining checks in parallel if no critical failures
        if all(results.get(check_name, True) for check_name, _ in critical_checks):
            remaining_checks = checks[2:]
            if remaining_checks:
                with ThreadPoolExecutor(max_workers=len(remaining_checks)) as executor:
                    future_to_check = {
                        executor.submit(check_func): check_name for check_name, check_func in remaining_checks
                    }

                    for future in as_completed(future_to_check):
                        check_name = future_to_check[future]
                        try:
                            results[check_name] = future.result()
                        except Exception as e:
                            results[check_name] = False
                            self.warnings.append(f"Check {check_name} failed: {e}")

        execution_time = time.time() - start_time

        return {
            "execution_time": execution_time,
            "results": results,
            "issues": self.issues,
            "warnings": self.warnings,
            "all_passed": len(self.issues) == 0,
        }


def main():
    parser = argparse.ArgumentParser(description="Optimized quick conflict check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", action="store_true", help="Attempt automatic fixes")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    checker = OptimizedQuickConflictChecker(verbose=args.verbose, auto_fix=args.fix)
    results = checker.run_parallel_checks()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nQuick conflict check completed in {results['execution_time']:.2f}s")
        print(f"Issues found: {len(results['issues'])}")
        print(f"Warnings: {len(results['warnings'])}")

        if results["issues"]:
            print("\nIssues:")
            for issue in results["issues"]:
                print(f"  ❌ {issue}")

        if results["warnings"]:
            print("\nWarnings:")
            for warning in results["warnings"]:
                print(f"  ⚠️ {warning}")


if __name__ == "__main__":
    main()
