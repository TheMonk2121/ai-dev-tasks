#!/usr/bin/env python3
"""
Quick Conflict Check Script

Runs the 10-minute triage checks for immediate conflict detection.
Implements the systematic approach from 400_comprehensive-coding-best-practices.md

Usage: python scripts/quick_conflict_check.py [--verbose] [--fix]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict


class QuickConflictChecker:
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.issues = []
        self.warnings = []
        self.fixes_applied = 0

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_merge_markers(self) -> bool:
        """Check for leftover merge markers."""
        self.log("Checking for merge markers...", "INFO")

        try:
            result = subprocess.run(
                ["git", "grep", "-nE", "^(<<<<<<<|=======|>>>>>>>)"], capture_output=True, text=True
            )

            if result.stdout.strip():
                self.issues.append(f"Merge markers found:\n{result.stdout}")
                self.log(f"❌ Merge markers detected in {result.stdout.count('<<<<<<<')} files", "ERROR")
                return False
            else:
                self.log("✅ No merge markers found", "INFO")
                return True

        except Exception as e:
            self.warnings.append(f"Could not check merge markers: {e}")
            self.log(f"⚠️ Could not check merge markers: {e}", "WARNING")
            return True

    def check_backup_files(self) -> bool:
        """Check for backup files from merge conflicts."""
        self.log("Checking for backup files...", "INFO")

        try:
            result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True)

            if result.returncode == 0:
                files = result.stdout.split("\0")
                backup_files = [f for f in files if f.endswith((".orig", ".rej"))]

                if backup_files:
                    self.issues.append(f"Backup files found: {backup_files}")
                    self.log(f"❌ {len(backup_files)} backup files found", "ERROR")
                    return False
                else:
                    self.log("✅ No backup files found", "INFO")
                    return True
            else:
                self.warnings.append("Could not list git files")
                return True

        except Exception as e:
            self.warnings.append(f"Could not check backup files: {e}")
            self.log(f"⚠️ Could not check backup files: {e}", "WARNING")
            return True

    def check_package_conflicts(self) -> bool:
        """Check for package manager conflicts."""
        self.log("Checking for package manager conflicts...", "INFO")

        conflicts = []

        # Check Python package managers
        python_configs = []
        for pattern in ["requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock"]:
            python_configs.extend(Path(".").glob(pattern))

        if len(python_configs) > 1:
            conflict_msg = f"Multiple Python package managers: {[str(f) for f in python_configs]}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        # Check Node.js package managers
        node_configs = []
        for pattern in ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"]:
            node_configs.extend(Path(".").glob(pattern))

        if len(node_configs) > 1:
            conflict_msg = f"Multiple Node.js package managers: {[str(f) for f in node_configs]}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        if conflicts:
            self.issues.extend(conflicts)
            return False
        else:
            self.log("✅ No package manager conflicts found", "INFO")
            return True

    def check_dual_configs(self) -> bool:
        """Check for dual configuration files."""
        self.log("Checking for dual configuration files...", "INFO")

        conflicts = []

        # Check Python configs
        python_configs = []
        for pattern in [".flake8", ".ruff.toml", "pyproject.toml", "setup.cfg"]:
            python_configs.extend(Path(".").glob(pattern))

        if len(python_configs) > 1:
            conflict_msg = f"Multiple Python config files: {[str(f) for f in python_configs]}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        # Check TypeScript configs
        ts_configs = []
        for pattern in ["tsconfig*.json", ".eslintrc*", "eslint.config.*"]:
            ts_configs.extend(Path(".").glob(pattern))

        if len(ts_configs) > 1:
            conflict_msg = f"Multiple TypeScript config files: {[str(f) for f in ts_configs]}"
            conflicts.append(conflict_msg)
            self.log(f"❌ {conflict_msg}", "ERROR")

        if conflicts:
            self.issues.extend(conflicts)
            return False
        else:
            self.log("✅ No dual configuration conflicts found", "INFO")
            return True

    def check_module_shadowing(self) -> bool:
        """Check for local modules shadowing stdlib (Python)."""
        self.log("Checking for module shadowing...", "INFO")

        try:
            # Check for common stdlib modules that might be shadowed
            stdlib_modules = ["email", "json", "jwt", "requests", "string", "typing", "dataclasses"]

            shadowed_modules = []
            for module in stdlib_modules:
                module_files = list(Path(".").rglob(f"{module}.py"))
                if module_files:
                    shadowed_modules.extend(module_files)

            if shadowed_modules:
                conflict_msg = f"Local modules shadowing stdlib: {[str(f) for f in shadowed_modules]}"
                self.issues.append(conflict_msg)
                self.log(f"❌ {conflict_msg}", "ERROR")
                return False
            else:
                self.log("✅ No module shadowing issues found", "INFO")
                return True

        except Exception as e:
            self.warnings.append(f"Could not check module shadowing: {e}")
            self.log(f"⚠️ Could not check module shadowing: {e}", "WARNING")
            return True

    def check_case_collisions(self) -> bool:
        """Check for case-sensitive name collisions."""
        self.log("Checking for case-sensitive name collisions...", "INFO")

        try:
            result = subprocess.run(["git", "ls-files"], capture_output=True, text=True)

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                lower_files = [f.lower() for f in files if f.strip()]

                # Find duplicates (case-insensitive)
                from collections import Counter

                duplicates = [item for item, count in Counter(lower_files).items() if count > 1]

                if duplicates:
                    conflict_msg = f"Case-sensitive name collisions: {duplicates}"
                    self.issues.append(conflict_msg)
                    self.log(f"❌ {conflict_msg}", "ERROR")
                    return False
                else:
                    self.log("✅ No case-sensitive name collisions found", "INFO")
                    return True
            else:
                self.warnings.append("Could not list git files")
                return True

        except Exception as e:
            self.warnings.append(f"Could not check case collisions: {e}")
            self.log(f"⚠️ Could not check case collisions: {e}", "WARNING")
            return True

    def check_dependency_conflicts(self) -> bool:
        """Check for dependency conflicts."""
        self.log("Checking for dependency conflicts...", "INFO")

        conflicts = []

        # Check Python dependencies
        try:
            result = subprocess.run(["python", "-m", "pip", "check"], capture_output=True, text=True)

            if result.returncode != 0:
                conflict_msg = f"Python dependency conflicts: {result.stdout}"
                conflicts.append(conflict_msg)
                self.log(f"❌ {conflict_msg}", "ERROR")
            else:
                self.log("✅ No Python dependency conflicts", "INFO")

        except Exception as e:
            self.warnings.append(f"Could not check Python dependencies: {e}")
            self.log(f"⚠️ Could not check Python dependencies: {e}", "WARNING")

        # Check Node.js dependencies
        try:
            result = subprocess.run(["npm", "ls", "--all"], capture_output=True, text=True)

            if "invalid" in result.stdout or "unmet" in result.stdout:
                conflict_msg = f"Node.js dependency conflicts: {result.stdout}"
                conflicts.append(conflict_msg)
                self.log(f"❌ {conflict_msg}", "ERROR")
            else:
                self.log("✅ No Node.js dependency conflicts", "INFO")

        except Exception as e:
            self.warnings.append(f"Could not check Node.js dependencies: {e}")
            self.log(f"⚠️ Could not check Node.js dependencies: {e}", "WARNING")

        if conflicts:
            self.issues.extend(conflicts)
            return False
        else:
            return True

    def run_auto_fix(self) -> bool:
        """Attempt to automatically fix common issues."""
        if not self.auto_fix:
            return False

        self.log("Attempting automatic fixes...", "INFO")

        # Try to fix merge markers
        if any("Merge markers found" in issue for issue in self.issues):
            self.log("⚠️ Merge markers require manual resolution", "WARNING")

        # Try to fix backup files
        if any("Backup files found" in issue for issue in self.issues):
            try:
                result = subprocess.run(
                    ["find", ".", "-name", "*.orig", "-o", "-name", "*.rej"], capture_output=True, text=True
                )
                if result.stdout.strip():
                    files = result.stdout.strip().split("\n")
                    for file in files:
                        if file.strip():
                            Path(file.strip()).unlink()
                            self.log(f"Deleted backup file: {file.strip()}", "INFO")
                            self.fixes_applied += 1
            except Exception as e:
                self.log(f"Could not fix backup files: {e}", "ERROR")

        return self.fixes_applied > 0

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all quick conflict checks."""
        self.log("Starting quick conflict check...", "INFO")

        checks = [
            ("merge_markers", self.check_merge_markers),
            ("backup_files", self.check_backup_files),
            ("package_conflicts", self.check_package_conflicts),
            ("dual_configs", self.check_dual_configs),
            ("module_shadowing", self.check_module_shadowing),
            ("case_collisions", self.check_case_collisions),
            ("dependency_conflicts", self.check_dependency_conflicts),
        ]

        results = {}
        for name, check_func in checks:
            results[name] = check_func()

        # Try auto-fix if enabled
        if self.auto_fix:
            self.run_auto_fix()

        return {
            "all_passed": all(results.values()),
            "results": results,
            "issues": self.issues,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


def main():
    parser = argparse.ArgumentParser(description="Quick conflict check for immediate issues")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", action="store_true", help="Attempt automatic fixes")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    checker = QuickConflictChecker(verbose=args.verbose, auto_fix=args.fix)
    results = checker.run_all_checks()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 60)
        print("🔍 QUICK CONFLICT CHECK RESULTS")
        print("=" * 60)

        if results["all_passed"]:
            print("✅ All conflict checks passed!")
        else:
            print(f"❌ {len(results['issues'])} conflict issues detected:")
            for issue in results["issues"]:
                print(f"  - {issue}")

        if results["warnings"]:
            print(f"\n⚠️ {len(results['warnings'])} warnings:")
            for warning in results["warnings"]:
                print(f"  - {warning}")

        if results["fixes_applied"] > 0:
            print(f"\n🔧 {results['fixes_applied']} automatic fixes applied")

        print("\n📊 Summary:")
        print(f"  - Checks passed: {sum(results['results'].values())}/{len(results['results'])}")
        print(f"  - Issues found: {len(results['issues'])}")
        print(f"  - Warnings: {len(results['warnings'])}")
        print(f"  - Fixes applied: {results['fixes_applied']}")

    sys.exit(0 if results["all_passed"] else 1)


if __name__ == "__main__":
    main()
