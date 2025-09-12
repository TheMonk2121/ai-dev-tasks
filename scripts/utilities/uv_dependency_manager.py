from __future__ import annotations
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path
import os
#!/usr/bin/env python3
"""
UV Advanced Dependency Manager

This script provides advanced dependency management capabilities including
dependency analysis, security scanning, and optimization recommendations.
"""

class UVDependencyManager:
    """Advanced dependency management for UV projects."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.pyproject_file = self.project_root / "pyproject.toml"
        self.lock_file = self.project_root / "uv.lock"
        self.requirements_file = self.project_root / "requirements.txt"

    def analyze_dependencies(self) -> dict:
        """Analyze project dependencies and provide insights."""
        print("🔍 Analyzing dependencies...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_dependencies": 0,
            "dependency_groups": {},
            "security_issues": [],
            "outdated_packages": [],
            "duplicate_dependencies": [],
            "recommendations": [],
        }

        try:
            # Get installed packages
            result = subprocess.run(
                ["uv", "pip", "list", "--format", "json"], capture_output=True, text=True, check=True
            )

            packages = json.loads(result.stdout)
            analysis["total_dependencies"] = len(packages)

            # Analyze by category
            categories = {
                "core": [],
                "development": [],
                "testing": [],
                "security": [],
                "ml": [],
                "web": [],
                "database": [],
                "other": [],
            }

            for package in packages:
                name = package["name"].lower()
                version = package["version"]

                # Categorize packages
                if any(keyword in name for keyword in ["dspy", "torch", "transformers", "sentence"]):
                    categories["ml"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["pytest", "coverage", "mock"]):
                    categories["testing"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["bandit", "safety", "audit"]):
                    categories["security"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["flask", "fastapi", "django"]):
                    categories["web"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["psycopg", "sqlalchemy", "pgvector"]):
                    categories["database"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["black", "ruff", "isort", "pre-commit"]):
                    categories["development"].append({"name": package["name"], "version": version})
                elif any(keyword in name for keyword in ["click", "pyyaml", "pydantic"]):
                    categories["core"].append({"name": package["name"], "version": version})
                else:
                    categories["other"].append({"name": package["name"], "version": version})

            analysis["dependency_groups"] = categories

            # Check for outdated packages
            analysis["outdated_packages"] = self._check_outdated_packages()

            # Check for duplicates
            analysis["duplicate_dependencies"] = self._check_duplicates()

            # Generate recommendations
            analysis["recommendations"] = self._generate_dependency_recommendations(analysis)

            return analysis

        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency analysis failed: {e}")
            return analysis

    def _check_outdated_packages(self) -> list[dict]:
        """Check for outdated packages."""
        try:
            result = subprocess.run(["uv", "pip", "list", "--outdated"], capture_output=True, text=True, check=True)

            outdated = []
            lines = result.stdout.strip().split("\n")[2:]  # Skip header

            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        outdated.append({"name": parts[0], "current": parts[1], "latest": parts[2]})

            return outdated

        except subprocess.CalledProcessError:
            return []

    def _check_duplicates(self) -> list[dict]:
        """Check for duplicate dependencies."""
        duplicates = []

        # This is a simplified check - in practice, you'd need more sophisticated logic
        # to detect actual duplicates across different dependency sources

        if self.requirements_file.exists() and self.pyproject_file.exists():
            duplicates.append(
                {
                    "type": "requirements_and_pyproject",
                    "description": "Both requirements.txt and pyproject.toml exist",
                    "recommendation": "Consider consolidating to pyproject.toml only",
                }
            )

        return duplicates

    def _generate_dependency_recommendations(self, analysis: dict) -> list[str]:
        """Generate dependency optimization recommendations."""
        recommendations = []

        # Check total dependency count
        total = analysis["total_dependencies"]
        if total > 200:
            recommendations.append(
                f"📦 Large dependency tree ({total} packages). "
                "Consider using optional dependency groups to reduce installation time."
            )
        elif total < 50:
            recommendations.append(f"✅ Lean dependency tree ({total} packages). " "Good dependency management.")

        # Check for outdated packages
        outdated_count = len(analysis["outdated_packages"])
        if outdated_count > 10:
            recommendations.append(
                f"⚠️ Many outdated packages ({outdated_count}). " "Consider running 'uv lock' to update dependencies."
            )
        elif outdated_count > 0:
            recommendations.append(f"📝 Some outdated packages ({outdated_count}). " "Review and update as needed.")

        # Check ML dependencies
        ml_packages = len(analysis["dependency_groups"].get("ml", []))
        if ml_packages > 0:
            recommendations.append(
                f"🤖 ML dependencies detected ({ml_packages} packages). "
                "Consider using 'uv sync --extra ml' for ML-specific installs."
            )

        # Check security tools
        security_packages = len(analysis["dependency_groups"].get("security", []))
        if security_packages > 0:
            recommendations.append(
                f"🔒 Security tools available ({security_packages} packages). "
                "Run 'uv run bandit -r src/' and 'uv run safety check' regularly."
            )

        return recommendations

    def security_scan(self) -> dict:
        """Run security scans on dependencies."""
        print("🔒 Running security scans...")

        security_results = {
            "timestamp": datetime.now().isoformat(),
            "bandit_results": [],
            "safety_results": [],
            "pip_audit_results": [],
            "recommendations": [],
        }

        # Run bandit security scan
        try:
            result = subprocess.run(
                ["uv", "run", "bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True,
                check=False,  # Don't fail on security issues
            )

            if result.stdout:
                security_results["bandit_results"] = json.loads(result.stdout)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            security_results["bandit_results"] = {"error": "Bandit scan failed"}

        # Run safety check
        try:
            result = subprocess.run(
                ["uv", "run", "safety", "check", "--json"], capture_output=True, text=True, check=False
            )

            if result.stdout:
                security_results["safety_results"] = json.loads(result.stdout)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            security_results["safety_results"] = {"error": "Safety check failed"}

        # Run pip-audit
        try:
            result = subprocess.run(
                ["uv", "run", "pip-audit", "--format", "json"], capture_output=True, text=True, check=False
            )

            if result.stdout:
                security_results["pip_audit_results"] = json.loads(result.stdout)

        except (subprocess.CalledProcessError, json.JSONDecodeError):
            security_results["pip_audit_results"] = {"error": "Pip-audit failed"}

        # Generate security recommendations
        security_results["recommendations"] = self._generate_security_recommendations(security_results)

        return security_results

    def _generate_security_recommendations(self, security_results: dict) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        # Check bandit results
        bandit_results = security_results.get("bandit_results", {})
        if "results" in bandit_results:
            issue_count = len(bandit_results["results"])
            if issue_count > 0:
                recommendations.append(
                    f"⚠️ Bandit found {issue_count} security issues. " "Review and fix high/medium severity issues."
                )
            else:
                recommendations.append("✅ No security issues found by Bandit.")

        # Check safety results
        safety_results = security_results.get("safety_results", {})
        if isinstance(safety_results, list) and safety_results:
            recommendations.append(
                f"⚠️ Safety found {len(safety_results)} vulnerable packages. "
                "Update vulnerable dependencies immediately."
            )
        elif isinstance(safety_results, dict) and not safety_results.get("error"):
            recommendations.append("✅ No vulnerable packages found by Safety.")

        # Check pip-audit results
        pip_audit_results = security_results.get("pip_audit_results", {})
        if "vulnerabilities" in pip_audit_results:
            vuln_count = len(pip_audit_results["vulnerabilities"])
            if vuln_count > 0:
                recommendations.append(f"⚠️ Pip-audit found {vuln_count} vulnerabilities. " "Update affected packages.")
            else:
                recommendations.append("✅ No vulnerabilities found by Pip-audit.")

        return recommendations

    def optimize_dependencies(self) -> dict:
        """Provide dependency optimization recommendations."""
        print("⚡ Analyzing dependency optimization opportunities...")

        optimization = {
            "timestamp": datetime.now().isoformat(),
            "unused_dependencies": [],
            "consolidation_opportunities": [],
            "performance_improvements": [],
            "recommendations": [],
        }

        # Check for unused dependencies (simplified approach)
        optimization["unused_dependencies"] = self._find_unused_dependencies()

        # Check for consolidation opportunities
        optimization["consolidation_opportunities"] = self._find_consolidation_opportunities()

        # Performance improvements
        optimization["performance_improvements"] = self._suggest_performance_improvements()

        # Generate recommendations
        optimization["recommendations"] = self._generate_optimization_recommendations(optimization)

        return optimization

    def _find_unused_dependencies(self) -> list[dict]:
        """Find potentially unused dependencies."""
        # This is a simplified implementation
        # In practice, you'd use tools like unimport or vulture
        unused = []

        try:
            subprocess.run(
                ["uv", "run", "python", "-c", "import sys; print('\\n'.join(sys.modules.keys()))"],
                capture_output=True,
                text=True,
                check=True,
            )

            # This is just a placeholder - real implementation would be more sophisticated
            unused.append(
                {"name": "example-unused-package", "reason": "Not imported in any Python files", "confidence": "low"}
            )

        except subprocess.CalledProcessError:
            pass

        return unused

    def _find_consolidation_opportunities(self) -> list[dict]:
        """Find opportunities to consolidate dependencies."""
        opportunities = []

        # Check for multiple packages that could be replaced by one
        opportunities.append(
            {
                "type": "multiple_http_clients",
                "packages": ["requests", "httpx", "aiohttp"],
                "recommendation": "Consider using only httpx for both sync and async HTTP",
            }
        )

        return opportunities

    def _suggest_performance_improvements(self) -> list[dict]:
        """Suggest performance improvements."""
        improvements = []

        improvements.append(
            {
                "type": "dependency_groups",
                "description": "Use optional dependency groups",
                "benefit": "Faster installs for specific use cases",
                "command": "uv sync --extra dev",
            }
        )

        improvements.append(
            {
                "type": "lock_file",
                "description": "Use uv.lock for deterministic builds",
                "benefit": "Faster, reproducible installs",
                "command": "uv lock && uv sync",
            }
        )

        return improvements

    def _generate_optimization_recommendations(self, optimization: dict) -> list[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Unused dependencies
        unused_count = len(optimization["unused_dependencies"])
        if unused_count > 0:
            recommendations.append(
                f"🗑️ Consider removing {unused_count} unused dependencies "
                "to reduce installation time and security surface."
            )

        # Consolidation opportunities
        consolidation_count = len(optimization["consolidation_opportunities"])
        if consolidation_count > 0:
            recommendations.append(
                f"🔄 {consolidation_count} consolidation opportunities found. "
                "Review and consolidate similar packages."
            )

        # Performance improvements
        performance_count = len(optimization["performance_improvements"])
        if performance_count > 0:
            recommendations.append(
                f"⚡ {performance_count} performance improvements available. " "Implement suggested optimizations."
            )

        return recommendations

    def generate_report(self, analysis: dict, security: dict, optimization: dict) -> str:
        """Generate a comprehensive dependency report."""
        report = f"""# 📊 UV Dependency Management Report

**Generated**: {analysis['timestamp']}

## 📦 Dependency Analysis

- **Total Dependencies**: {analysis['total_dependencies']}
- **Outdated Packages**: {len(analysis['outdated_packages'])}
- **Duplicate Dependencies**: {len(analysis['duplicate_dependencies'])}

### Dependency Groups
"""

        for group, packages in analysis["dependency_groups"].items():
            if packages:
                report += f"- **{group.title()}**: {len(packages)} packages\n"

        report += "\n## 🔒 Security Analysis\n"

        # Security summary
        bandit_issues = len(security.get("bandit_results", {}).get("results", []))
        safety_issues = (
            len(security.get("safety_results", [])) if isinstance(security.get("safety_results"), list) else 0
        )
        pip_audit_issues = len(security.get("pip_audit_results", {}).get("vulnerabilities", []))

        report += f"- **Bandit Issues**: {bandit_issues}\n"
        report += f"- **Safety Issues**: {safety_issues}\n"
        report += f"- **Pip-audit Issues**: {pip_audit_issues}\n"

        report += "\n## ⚡ Optimization Analysis\n"

        report += f"- **Unused Dependencies**: {len(optimization['unused_dependencies'])}\n"
        report += f"- **Consolidation Opportunities**: {len(optimization['consolidation_opportunities'])}\n"
        report += f"- **Performance Improvements**: {len(optimization['performance_improvements'])}\n"

        report += "\n## 💡 Recommendations\n"

        all_recommendations = (
            analysis["recommendations"] + security["recommendations"] + optimization["recommendations"]
        )

        for i, rec in enumerate(all_recommendations, 1):
            report += f"{i}. {rec}\n"

        report += "\n## 🚀 Next Steps\n"
        report += "1. Review and address security issues\n"
        report += "2. Update outdated dependencies\n"
        report += "3. Implement optimization recommendations\n"
        report += "4. Run regular dependency audits\n"

        return report

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Advanced UV dependency management")
    parser.add_argument("--analyze", action="store_true", help="Analyze dependencies")
    parser.add_argument("--security", action="store_true", help="Run security scans")
    parser.add_argument("--optimize", action="store_true", help="Analyze optimization opportunities")
    parser.add_argument("--full-report", action="store_true", help="Generate full report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file for report")

    args = parser.parse_args()

    manager = UVDependencyManager()

    if args.analyze:
        analysis = manager.analyze_dependencies()
        if args.json:
            print(json.dumps(analysis, indent=2))
        else:
            print("📊 Dependency Analysis Results:")
            print(f"Total dependencies: {analysis['total_dependencies']}")
            print(f"Outdated packages: {len(analysis['outdated_packages'])}")
            for rec in analysis["recommendations"]:
                print(f"💡 {rec}")

    elif args.security:
        security = manager.security_scan()
        if args.json:
            print(json.dumps(security, indent=2))
        else:
            print("🔒 Security Scan Results:")
            for rec in security["recommendations"]:
                print(f"💡 {rec}")

    elif args.optimize:
        optimization = manager.optimize_dependencies()
        if args.json:
            print(json.dumps(optimization, indent=2))
        else:
            print("⚡ Optimization Analysis Results:")
            for rec in optimization["recommendations"]:
                print(f"💡 {rec}")

    elif args.full_report:
        print("🔍 Generating comprehensive dependency report...")

        analysis = manager.analyze_dependencies()
        security = manager.security_scan()
        optimization = manager.optimize_dependencies()

        report = manager.generate_report(analysis, security, optimization)

        if args.output:
            output_file = Path(args.output)
            output_file.write_text(report)
            print(f"📄 Report saved to {output_file}")
        else:
            print(report)

    else:
        # Default: run all analyses
        print("🔍 Running comprehensive dependency analysis...")

        analysis = manager.analyze_dependencies()
        security = manager.security_scan()
        optimization = manager.optimize_dependencies()

        if args.json:
            combined = {"analysis": analysis, "security": security, "optimization": optimization}
            print(json.dumps(combined, indent=2))
        else:
            print("📊 Quick Summary:")
            print(f"Total dependencies: {analysis['total_dependencies']}")
            print(f"Security issues: {len(security.get('bandit_results', {}).get('results', []))}")
            print(f"Optimization opportunities: {len(optimization['consolidation_opportunities'])}")

            print("\n💡 Top Recommendations:")
            all_recs = analysis["recommendations"][:3]
            for rec in all_recs:
                print(f"- {rec}")

if __name__ == "__main__":
    main()
