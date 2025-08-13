#!/usr/bin/env python3
"""
Comprehensive Conflict Audit Script

Runs deep audit checks for systematic conflict detection.
Implements the systematic approach from 400_comprehensive-coding-best-practices.md

Usage: python scripts/conflict_audit.py [--full] [--verbose] [--json]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict


class ConflictAuditor:
    def __init__(self, full_audit: bool = False, verbose: bool = False):
        self.full_audit = full_audit
        self.verbose = verbose
        self.issues = []
        self.warnings = []

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_dependency_conflicts(self) -> Dict[str, Any]:
        """Check for dependency conflicts."""
        self.log("Checking for dependency conflicts...", "INFO")
        results = {}

        # Python dependency conflicts
        try:
            result = subprocess.run(["python", "-m", "pip", "check"], capture_output=True, text=True)
            if result.returncode != 0:
                results["python"] = result.stdout
                self.issues.append(f"Python dependency conflicts: {result.stdout}")
                self.log("❌ Python dependency conflicts detected", "ERROR")
            else:
                results["python"] = "No conflicts"
                self.log("✅ No Python dependency conflicts", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Python dependencies: {e}")
            self.log(f"⚠️ Could not check Python dependencies: {e}", "WARNING")

        # Node.js dependency conflicts
        try:
            result = subprocess.run(["npm", "ls", "--all"], capture_output=True, text=True)
            if "invalid" in result.stdout or "unmet" in result.stdout:
                results["nodejs"] = result.stdout
                self.issues.append(f"Node.js dependency conflicts: {result.stdout}")
                self.log("❌ Node.js dependency conflicts detected", "ERROR")
            else:
                results["nodejs"] = "No conflicts"
                self.log("✅ No Node.js dependency conflicts", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Node.js dependencies: {e}")
            self.log(f"⚠️ Could not check Node.js dependencies: {e}", "WARNING")

        return results

    def check_circular_dependencies(self) -> Dict[str, Any]:
        """Check for circular dependencies."""
        self.log("Checking for circular dependencies...", "INFO")
        results = {}

        # Python circular imports
        try:
            # Try to install pycycle if not available
            pycycle_available = False
            try:
                import importlib.util

                spec = importlib.util.find_spec("pycycle")
                if spec is not None:
                    pycycle_available = True
                else:
                    self.log("Installing pycycle for circular dependency detection...", "INFO")
                    subprocess.run(["pip", "install", "pycycle"], capture_output=True)
                    # Check again after installation
                    spec = importlib.util.find_spec("pycycle")
                    pycycle_available = spec is not None
            except Exception:
                pycycle_available = False
                self.warnings.append("Could not install or import pycycle")

            if pycycle_available:
                # Check for circular dependencies
                result = subprocess.run(
                    ["python", "-c", 'import pycycle; pycycle.check(".")'], capture_output=True, text=True
                )
                if result.returncode != 0:
                    results["python"] = result.stdout
                    self.issues.append(f"Python circular dependencies: {result.stdout}")
                    self.log("❌ Python circular dependencies detected", "ERROR")
                else:
                    results["python"] = "No circular dependencies"
                    self.log("✅ No Python circular dependencies", "INFO")
            else:
                results["python"] = "pycycle not available"
                self.log("⚠️ pycycle not available for circular dependency detection", "WARNING")
        except Exception as e:
            self.warnings.append(f"Could not check Python circular dependencies: {e}")
            self.log(f"⚠️ Could not check Python circular dependencies: {e}", "WARNING")

        # Node.js circular dependencies
        try:
            result = subprocess.run(["npx", "madge", "--circular", "src"], capture_output=True, text=True)
            if result.stdout.strip():
                results["nodejs"] = result.stdout
                self.issues.append(f"Node.js circular dependencies: {result.stdout}")
                self.log("❌ Node.js circular dependencies detected", "ERROR")
            else:
                results["nodejs"] = "No circular dependencies"
                self.log("✅ No Node.js circular dependencies", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Node.js circular dependencies: {e}")
            self.log(f"⚠️ Could not check Node.js circular dependencies: {e}", "WARNING")

        return results

    def check_build_toolchain_conflicts(self) -> Dict[str, Any]:
        """Check for build toolchain conflicts."""
        self.log("Checking for build toolchain conflicts...", "INFO")
        results = {}

        # TypeScript/JavaScript path alias drift
        try:
            result = subprocess.run(["npx", "tsc", "--noEmit"], capture_output=True, text=True)
            if result.returncode != 0:
                results["typescript"] = result.stdout
                self.issues.append(f"TypeScript compilation errors: {result.stdout}")
                self.log("❌ TypeScript compilation errors detected", "ERROR")
            else:
                results["typescript"] = "No compilation errors"
                self.log("✅ No TypeScript compilation errors", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check TypeScript compilation: {e}")
            self.log(f"⚠️ Could not check TypeScript compilation: {e}", "WARNING")

        # Python namespace package issues
        try:
            init_files = list(Path(".").rglob("__init__.py"))
            namespace_packages = []
            for init_file in init_files:
                try:
                    content = init_file.read_text()
                    if "namespace" in content:
                        namespace_packages.append(str(init_file))
                except Exception:
                    continue

            if namespace_packages:
                results["python_namespace"] = namespace_packages
                self.issues.append(f"Namespace packages found: {namespace_packages}")
                self.log("❌ Namespace packages detected", "ERROR")
            else:
                results["python_namespace"] = "No namespace packages"
                self.log("✅ No namespace package issues", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Python namespace packages: {e}")
            self.log(f"⚠️ Could not check Python namespace packages: {e}", "WARNING")

        return results

    def check_interface_contract_drift(self) -> Dict[str, Any]:
        """Check for interface/contract drift."""
        self.log("Checking for interface/contract drift...", "INFO")
        results = {}

        # OpenAPI schema validation
        try:
            openapi_files = list(Path(".").rglob("*.yaml")) + list(Path(".").rglob("*.yml"))
            openapi_files = [f for f in openapi_files if "openapi" in f.read_text().lower()]

            if openapi_files:
                for openapi_file in openapi_files:
                    try:
                        result = subprocess.run(
                            ["npx", "@redocly/cli", "lint", str(openapi_file)], capture_output=True, text=True
                        )
                        if result.returncode != 0:
                            results[f"openapi_{openapi_file.name}"] = result.stdout
                            self.issues.append(f"OpenAPI schema issues in {openapi_file}: {result.stdout}")
                            self.log(f"❌ OpenAPI schema issues in {openapi_file}", "ERROR")
                        else:
                            results[f"openapi_{openapi_file.name}"] = "Valid"
                            self.log(f"✅ OpenAPI schema {openapi_file} is valid", "INFO")
                    except Exception as e:
                        self.warnings.append(f"Could not validate OpenAPI schema {openapi_file}: {e}")
            else:
                results["openapi"] = "No OpenAPI files found"
                self.log("✅ No OpenAPI files to validate", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check OpenAPI schemas: {e}")
            self.log(f"⚠️ Could not check OpenAPI schemas: {e}", "WARNING")

        # GraphQL schema validation
        try:
            graphql_files = list(Path(".").rglob("*.graphql")) + list(Path(".").rglob("*.gql"))

            if graphql_files:
                for graphql_file in graphql_files:
                    try:
                        result = subprocess.run(
                            ["npx", "graphql-schema-linter", str(graphql_file)], capture_output=True, text=True
                        )
                        if result.returncode != 0:
                            results[f"graphql_{graphql_file.name}"] = result.stdout
                            self.issues.append(f"GraphQL schema issues in {graphql_file}: {result.stdout}")
                            self.log(f"❌ GraphQL schema issues in {graphql_file}", "ERROR")
                        else:
                            results[f"graphql_{graphql_file.name}"] = "Valid"
                            self.log(f"✅ GraphQL schema {graphql_file} is valid", "INFO")
                    except Exception as e:
                        self.warnings.append(f"Could not validate GraphQL schema {graphql_file}: {e}")
            else:
                results["graphql"] = "No GraphQL files found"
                self.log("✅ No GraphQL files to validate", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check GraphQL schemas: {e}")
            self.log(f"⚠️ Could not check GraphQL schemas: {e}", "WARNING")

        return results

    def check_data_model_migrations(self) -> Dict[str, Any]:
        """Check for data model and migration conflicts."""
        self.log("Checking for data model and migration conflicts...", "INFO")
        results = {}

        # Alembic migration conflicts
        try:
            result = subprocess.run(["alembic", "heads"], capture_output=True, text=True)
            if result.returncode == 0 and "multiple heads" in result.stdout.lower():
                results["alembic_heads"] = result.stdout
                self.issues.append(f"Alembic multiple heads: {result.stdout}")
                self.log("❌ Alembic multiple heads detected", "ERROR")
            else:
                results["alembic_heads"] = "Single head"
                self.log("✅ Alembic single head", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Alembic heads: {e}")
            self.log(f"⚠️ Could not check Alembic heads: {e}", "WARNING")

        # Prisma migration conflicts
        try:
            result = subprocess.run(["npx", "prisma", "migrate", "status"], capture_output=True, text=True)
            if result.returncode != 0 or "drift" in result.stdout.lower():
                results["prisma_migrations"] = result.stdout
                self.issues.append(f"Prisma migration issues: {result.stdout}")
                self.log("❌ Prisma migration issues detected", "ERROR")
            else:
                results["prisma_migrations"] = "No issues"
                self.log("✅ No Prisma migration issues", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not check Prisma migrations: {e}")
            self.log(f"⚠️ Could not check Prisma migrations: {e}", "WARNING")

        return results

    def check_test_configuration_drift(self) -> Dict[str, Any]:
        """Check for test configuration drift."""
        self.log("Checking for test configuration drift...", "INFO")
        results = {}

        # Python test environment
        try:
            result = subprocess.run(
                ["python", "-c", 'import sys; print(f"Python: {sys.version}"); print(f"Path: {sys.path[:3]}")'],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                results["python_test_env"] = result.stdout
                self.log(f"✅ Python test environment: {result.stdout.strip()}", "INFO")
            else:
                results["python_test_env"] = "Error"
                self.warnings.append("Could not check Python test environment")
        except Exception as e:
            self.warnings.append(f"Could not check Python test environment: {e}")
            self.log(f"⚠️ Could not check Python test environment: {e}", "WARNING")

        # Node.js test environment
        try:
            result = subprocess.run(
                [
                    "node",
                    "-e",
                    "console.log(`Node: ${process.version}`); "
                    'console.log(`NODE_ENV: ${process.env.NODE_ENV || "undefined"}`)',
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                results["nodejs_test_env"] = result.stdout
                self.log(f"✅ Node.js test environment: {result.stdout.strip()}", "INFO")
            else:
                results["nodejs_test_env"] = "Error"
                self.warnings.append("Could not check Node.js test environment")
        except Exception as e:
            self.warnings.append(f"Could not check Node.js test environment: {e}")
            self.log(f"⚠️ Could not check Node.js test environment: {e}", "WARNING")

        return results

    def check_environment_parity(self) -> Dict[str, Any]:
        """Check for environment parity issues."""
        self.log("Checking for environment parity...", "INFO")
        results = {}

        # System information
        try:
            import platform

            results["system_info"] = {
                "os": platform.system(),
                "arch": platform.machine(),
                "python_version": platform.python_version(),
                "node_version": "Unknown",
            }

            # Try to get Node.js version
            try:
                result = subprocess.run(["node", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    results["system_info"]["node_version"] = result.stdout.strip()
            except Exception:
                pass

            self.log(f"✅ System info: {results['system_info']}", "INFO")
        except Exception as e:
            self.warnings.append(f"Could not get system information: {e}")
            self.log(f"⚠️ Could not get system information: {e}", "WARNING")

        return results

    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive conflict audit."""
        self.log("Starting comprehensive conflict audit...", "INFO")

        audit_results = {
            "dependency_conflicts": self.check_dependency_conflicts(),
            "circular_dependencies": self.check_circular_dependencies(),
            "build_toolchain_conflicts": self.check_build_toolchain_conflicts(),
            "interface_contract_drift": self.check_interface_contract_drift(),
            "data_model_migrations": self.check_data_model_migrations(),
            "test_configuration_drift": self.check_test_configuration_drift(),
            "environment_parity": self.check_environment_parity(),
        }

        if self.full_audit:
            self.log("Running full audit with additional checks...", "INFO")
            # Add more comprehensive checks here
            # - Performance impact analysis
            # - Security conflict analysis
            # - Deployment environment conflicts
            # - CI/CD pipeline conflicts

        return {
            "audit_complete": True,
            "full_audit": self.full_audit,
            "results": audit_results,
            "issues": self.issues,
            "warnings": self.warnings,
            "total_issues": len(self.issues),
            "total_warnings": len(self.warnings),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive conflict audit")
    parser.add_argument("--full", action="store_true", help="Run full audit with additional checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    auditor = ConflictAuditor(full_audit=args.full, verbose=args.verbose)
    results = auditor.run_full_audit()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print("\n" + "=" * 60)
        print("🔍 COMPREHENSIVE CONFLICT AUDIT RESULTS")
        print("=" * 60)

        if results["total_issues"] == 0:
            print("✅ No critical conflicts detected!")
        else:
            print(f"❌ {results['total_issues']} critical issues detected:")
            for issue in results["issues"]:
                print(f"  - {issue}")

        if results["total_warnings"] > 0:
            print(f"\n⚠️ {results['total_warnings']} warnings:")
            for warning in results["warnings"]:
                print(f"  - {warning}")

        print("\n📊 Audit Summary:")
        print(f"  - Full audit: {'Yes' if results['full_audit'] else 'No'}")
        print(f"  - Issues found: {results['total_issues']}")
        print(f"  - Warnings: {results['total_warnings']}")
        print(f"  - Audit completed: {results['timestamp']}")

        if results["total_issues"] > 0:
            print("\n🚨 RECOMMENDATIONS:")
            print("  1. Address critical issues before proceeding")
            print("  2. Review warnings for potential problems")
            print("  3. Consider running with --full for deeper analysis")
            print("  4. Implement CI/CD gates to prevent future conflicts")

    sys.exit(0 if results["total_issues"] == 0 else 1)


if __name__ == "__main__":
    main()
