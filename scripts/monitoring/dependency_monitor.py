from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Dependency Graph Monitor - Automated Dependency Analysis

Automatically generates and tracks dependency graphs for the AI development ecosystem.
Integrates with existing automation systems and provides change detection.

Usage: python scripts/dependency_monitor.py [--dry-run] [--force] [--output-dir]
"""

# <!-- ANCHOR_KEY: dependency-monitor -->
# <!-- ANCHOR_PRIORITY: 18 -->
#
#
# <!-- ROLE_PINS: ["coder", "implementer"] -->

class DependencyMonitor:
    def __init__(self, dry_run: bool = False, force: bool = False, output_dir: str = "metrics"):
        self.dry_run = dry_run
        self.force = force
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # File paths
        self.dependency_file = self.output_dir / "dependency_graph.json"
        self.circular_file = self.output_dir / "circular_dependencies.json"
        self.import_conflicts_file = self.output_dir / "import_conflicts.json"
        self.change_log_file = self.output_dir / "dependency_changes.log"

        # Previous state for comparison
        self.previous_state = self._load_previous_state()

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

        # Also log to file
        with open(self.change_log_file, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def _load_previous_state(self) -> dict[str, Any]:
        """Load previous dependency state for comparison."""
        previous_state = {}

        # Load dependency tree state
        if self.dependency_file.exists():
            try:
                with open(self.dependency_file) as f:
                    previous_state["dependency_tree"] = json.load(f)
            except Exception as e:
                self.log(f"Failed to load dependency tree state: {e}", "WARNING")

        # Load circular dependencies state
        if self.circular_file.exists():
            try:
                with open(self.circular_file) as f:
                    previous_state["circular_dependencies"] = json.load(f)
            except Exception as e:
                self.log(f"Failed to load circular dependencies state: {e}", "WARNING")

        # Load import conflicts state
        if self.import_conflicts_file.exists():
            try:
                with open(self.import_conflicts_file) as f:
                    previous_state["import_conflicts"] = json.load(f)
            except Exception as e:
                self.log(f"Failed to load import conflicts state: {e}", "WARNING")

        return previous_state

    def _save_state(self, state: dict[str, Any], filename: Path):
        """Save state to file."""
        if self.dry_run:
            self.log(f"DRY RUN: Would save to {filename}")
            return

        try:
            with open(filename, "w") as f:
                json.dump(state, f, indent=2, default=str)
            self.log(f"Saved state to {filename}")
        except Exception as e:
            self.log(f"Failed to save state to {filename}: {e}", "ERROR")

    def generate_dependency_tree(self) -> dict[str, Any] | None:
        """Generate dependency tree using pipdeptree."""
        try:
            self.log("Generating dependency tree with pipdeptree...")
            result = subprocess.run(["pipdeptree", "-j"], capture_output=True, text=True, check=True)

            dependencies = json.loads(result.stdout)

            # Add metadata
            state = {
                "timestamp": datetime.now().isoformat(),
                "tool": "pipdeptree",
                "dependencies": dependencies,
                "total_packages": len(dependencies),
                "hash": hashlib.md5(result.stdout.encode()).hexdigest(),
            }

            self.log(f"Generated dependency tree with {len(dependencies)} packages")
            return state

        except subprocess.CalledProcessError as e:
            self.log(f"pipdeptree failed: {e}", "ERROR")
            return None
        except json.JSONDecodeError as e:
            self.log(f"Failed to parse pipdeptree output: {e}", "ERROR")
            return None

    def check_circular_dependencies(self) -> dict[str, Any] | None:
        """Check for circular dependencies using pycycle."""
        # Skip circular dependency check by default due to performance issues
        # This can be enabled with --force flag for manual runs
        if not self.force:
            self.log("Skipping circular dependency check (use --force to enable)", "INFO")
            return None

        try:
            self.log("Checking for circular dependencies with pycycle...")
            result = subprocess.run(
                ["pycycle", "--here", "--ignore", "venv,600_archives,docs/legacy"],
                capture_output=True,
                text=True,
                check=False,  # pycycle may exit with non-zero if it finds cycles
                timeout=30,  # 30 second timeout to prevent hanging
            )

            state = {
                "timestamp": datetime.now().isoformat(),
                "tool": "pycycle",
                "exit_code": result.returncode,
                "output": result.stdout,
                "error": result.stderr,
                "has_circular_dependencies": result.returncode != 0,
                "hash": hashlib.md5(result.stdout.encode()).hexdigest(),
            }

            if result.returncode == 0:
                self.log("No circular dependencies detected")
            else:
                self.log(f"Circular dependencies detected: {result.stdout}", "WARNING")

            return state

        except FileNotFoundError:
            self.log("pycycle not found, skipping circular dependency check", "WARNING")
            return None
        except subprocess.TimeoutExpired:
            self.log("pycycle timed out after 30 seconds, skipping circular dependency check", "WARNING")
            return None
        except Exception as e:
            self.log(f"pycycle check failed: {e}", "ERROR")
            return None

    def analyze_import_conflicts(self) -> dict[str, Any] | None:
        """Analyze import conflicts using existing scripts."""
        try:
            self.log("Analyzing import conflicts...")
            result = subprocess.run(
                [sys.executable, "scripts/conflict_audit.py", "--json"], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                conflicts = json.loads(result.stdout)
            else:
                conflicts = {"error": result.stderr, "status": "failed"}

            state = {
                "timestamp": datetime.now().isoformat(),
                "tool": "conflict_audit.py",
                "conflicts": conflicts,
                "exit_code": result.returncode,
                "hash": hashlib.md5(result.stdout.encode()).hexdigest(),
            }

            self.log("Import conflict analysis completed")
            return state

        except Exception as e:
            self.log(f"Import conflict analysis failed: {e}", "ERROR")
            return None

    def detect_changes(self, current_state: dict[str, Any], previous_state: dict[str, Any]) -> dict[str, Any]:
        """Detect changes between current and previous states."""
        changes = {"timestamp": datetime.now().isoformat(), "changes_detected": False, "details": {}}

        for key in current_state:
            if key not in previous_state:
                changes["details"][key] = "new"
                changes["changes_detected"] = True
            else:
                # Compare states ignoring timestamps
                current_copy = current_state[key].copy() if isinstance(current_state[key], dict) else current_state[key]
                previous_copy = (
                    previous_state[key].copy() if isinstance(previous_state[key], dict) else previous_state[key]
                )

                # Remove timestamps for comparison
                if isinstance(current_copy, dict) and "timestamp" in current_copy:
                    del current_copy["timestamp"]
                if isinstance(previous_copy, dict) and "timestamp" in previous_copy:
                    del previous_copy["timestamp"]

                if current_copy != previous_copy:
                    changes["details"][key] = "modified"
                    changes["changes_detected"] = True

        if changes["changes_detected"]:
            self.log("Changes detected in dependency state")
        else:
            self.log("No changes detected in dependency state")

        return changes

    def run_analysis(self) -> dict[str, Any]:
        """Run complete dependency analysis."""
        self.log("Starting dependency analysis...")

        # Generate dependency tree
        dependency_state = self.generate_dependency_tree()

        # Check circular dependencies
        circular_state = self.check_circular_dependencies()

        # Analyze import conflicts
        import_state = self.analyze_import_conflicts()

        # Combine all states
        current_state = {
            "dependency_tree": dependency_state,
            "circular_dependencies": circular_state,
            "import_conflicts": import_state,
        }

        # Detect changes
        changes = self.detect_changes(current_state, self.previous_state)
        current_state["changes"] = changes

        # Save states
        if dependency_state:
            self._save_state(dependency_state, self.dependency_file)
        if circular_state:
            self._save_state(circular_state, self.circular_file)
        if import_state:
            self._save_state(import_state, self.import_conflicts_file)

        self.log("Dependency analysis completed")
        return current_state

    def generate_summary(self, analysis_result: dict[str, Any]) -> str:
        """Generate human-readable summary."""
        summary = []
        summary.append("=" * 60)
        summary.append("DEPENDENCY ANALYSIS SUMMARY")
        summary.append("=" * 60)

        # Dependency tree summary
        if analysis_result.get("dependency_tree"):
            deps = analysis_result["dependency_tree"]
            summary.append(f"📦 Dependencies: {deps.get('total_packages', 'unknown')} packages")

        # Circular dependencies summary
        if analysis_result.get("circular_dependencies"):
            circ = analysis_result["circular_dependencies"]
            if circ.get("has_circular_dependencies"):
                summary.append("⚠️  Circular dependencies: DETECTED")
            else:
                summary.append("✅ Circular dependencies: None detected")

        # Import conflicts summary
        if analysis_result.get("import_conflicts"):
            conflicts = analysis_result["import_conflicts"]
            if conflicts.get("exit_code") == 0:
                summary.append("✅ Import conflicts: Analysis completed")
            else:
                summary.append("❌ Import conflicts: Analysis failed")

        # Changes summary
        changes = analysis_result.get("changes", {})
        if changes.get("changes_detected"):
            summary.append("🔄 Changes detected: Yes")
            for key, change_type in changes.get("details", {}).items():
                summary.append(f"   - {key}: {change_type}")
        else:
            summary.append("🔄 Changes detected: No")

        summary.append("=" * 60)
        return "\n".join(summary)

def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Monitor")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without saving")
    parser.add_argument("--force", action="store_true", help="Force analysis even if no changes")
    parser.add_argument("--output-dir", default="metrics", help="Output directory for results")

    args = parser.parse_args()

    monitor = DependencyMonitor(dry_run=args.dry_run, force=args.force, output_dir=args.output_dir)

    try:
        analysis_result = monitor.run_analysis()
        summary = monitor.generate_summary(analysis_result)
        print(summary)

        # Exit with appropriate code
        if analysis_result.get("changes", {}).get("changes_detected"):
            sys.exit(1)  # Changes detected
        else:
            sys.exit(0)  # No changes

    except Exception as e:
        monitor.log(f"Analysis failed: {e}", "ERROR")
        sys.exit(2)

if __name__ == "__main__":
    main()
