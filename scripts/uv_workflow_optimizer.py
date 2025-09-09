#!/usr/bin/env python3
"""
UV Workflow Optimizer

This script optimizes UV workflows by analyzing usage patterns,
providing automation suggestions, and creating optimized scripts.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path


class UVWorkflowOptimizer:
    """Optimize UV workflows and provide automation suggestions."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.optimization_log = []
        self.workflow_patterns = {}

    def analyze_workflow_patterns(self) -> dict:
        """Analyze common workflow patterns and suggest optimizations."""
        print("🔍 Analyzing workflow patterns...")

        patterns = {
            "timestamp": datetime.now().isoformat(),
            "common_commands": {},
            "performance_bottlenecks": [],
            "automation_opportunities": [],
            "optimization_suggestions": [],
        }

        # Analyze common UV commands
        patterns["common_commands"] = self._analyze_common_commands()

        # Identify performance bottlenecks
        patterns["performance_bottlenecks"] = self._identify_bottlenecks()

        # Find automation opportunities
        patterns["automation_opportunities"] = self._find_automation_opportunities()

        # Generate optimization suggestions
        patterns["optimization_suggestions"] = self._generate_workflow_suggestions(patterns)

        return patterns

    def _analyze_common_commands(self) -> dict:
        """Analyze commonly used UV commands."""
        common_commands = {
            "uv_sync": {
                "frequency": "high",
                "use_case": "Install all dependencies",
                "optimization": "Use 'uv sync --extra dev' for development",
            },
            "uv_run": {
                "frequency": "high",
                "use_case": "Run commands in environment",
                "optimization": "Create aliases for frequently used commands",
            },
            "uv_lock": {
                "frequency": "medium",
                "use_case": "Update lock file",
                "optimization": "Run automatically in CI/CD",
            },
            "uvx": {
                "frequency": "medium",
                "use_case": "One-off tools",
                "optimization": "Create wrapper scripts for common tools",
            },
        }

        return common_commands

    def _identify_bottlenecks(self) -> list[dict]:
        """Identify workflow performance bottlenecks."""
        bottlenecks = []

        # Check for slow operations
        bottlenecks.append(
            {
                "type": "slow_install",
                "description": "Full dependency installation on every change",
                "impact": "high",
                "solution": "Use incremental installs and dependency groups",
            }
        )

        bottlenecks.append(
            {
                "type": "repeated_commands",
                "description": "Running same commands repeatedly",
                "impact": "medium",
                "solution": "Create shell aliases and wrapper scripts",
            }
        )

        bottlenecks.append(
            {
                "type": "manual_processes",
                "description": "Manual dependency updates and checks",
                "impact": "medium",
                "solution": "Automate with scripts and CI/CD",
            }
        )

        return bottlenecks

    def _find_automation_opportunities(self) -> list[dict]:
        """Find opportunities for workflow automation."""
        opportunities = []

        opportunities.append(
            {
                "type": "dependency_updates",
                "description": "Automated dependency updates",
                "script": "uv_dependency_updater.py",
                "benefit": "Keep dependencies current automatically",
            }
        )

        opportunities.append(
            {
                "type": "environment_validation",
                "description": "Automated environment validation",
                "script": "uv_environment_validator.py",
                "benefit": "Ensure consistent development environments",
            }
        )

        opportunities.append(
            {
                "type": "performance_monitoring",
                "description": "Automated performance monitoring",
                "script": "uv_performance_monitor.py",
                "benefit": "Track and optimize UV performance",
            }
        )

        opportunities.append(
            {
                "type": "security_scanning",
                "description": "Automated security scanning",
                "script": "uv_security_scanner.py",
                "benefit": "Regular security vulnerability checks",
            }
        )

        return opportunities

    def _generate_workflow_suggestions(self, patterns: dict) -> list[str]:
        """Generate workflow optimization suggestions."""
        suggestions = []

        # Performance suggestions
        suggestions.append("⚡ Use 'uv sync --extra dev' instead of full installs for development")

        suggestions.append("🔄 Create shell aliases for frequently used UV commands")

        suggestions.append("📦 Use dependency groups to install only what you need")

        suggestions.append("🚀 Use 'uvx' for one-off tools to avoid global installations")

        suggestions.append("🔒 Run 'uv lock' regularly to keep dependencies up to date")

        suggestions.append("📊 Monitor UV performance with automated scripts")

        return suggestions

    def create_optimized_scripts(self) -> dict:
        """Create optimized workflow scripts."""
        print("🛠️ Creating optimized workflow scripts...")

        scripts_created = {"timestamp": datetime.now().isoformat(), "scripts": [], "aliases": [], "automation": []}

        # Create shell aliases
        aliases = self._create_shell_aliases()
        scripts_created["aliases"] = aliases

        # Create wrapper scripts
        wrapper_scripts = self._create_wrapper_scripts()
        scripts_created["scripts"] = wrapper_scripts

        # Create automation scripts
        automation_scripts = self._create_automation_scripts()
        scripts_created["automation"] = automation_scripts

        return scripts_created

    def _create_shell_aliases(self) -> list[dict]:
        """Create shell aliases for common UV commands."""
        aliases = [
            {"alias": "uvd", "command": "uv sync --extra dev", "description": "Quick development environment setup"},
            {"alias": "uvt", "command": "uv run pytest", "description": "Run tests in UV environment"},
            {"alias": "uvl", "command": "uv run python -m lint", "description": "Run linting in UV environment"},
            {"alias": "uvf", "command": "uvx black . && uvx isort .", "description": "Format code with UVX tools"},
            {
                "alias": "uvs",
                "command": "uv run python scripts/system_health_check.py",
                "description": "Run system health check",
            },
            {
                "alias": "uvp",
                "command": "python scripts/uv_performance_monitor.py",
                "description": "Monitor UV performance",
            },
        ]

        # Create aliases file
        aliases_file = self.project_root / "uv_aliases.sh"
        aliases_content = "#!/bin/bash\n# UV Workflow Aliases\n\n"

        for alias in aliases:
            aliases_content += f"alias {alias['alias']}='{alias['command']}'\n"

        aliases_file.write_text(aliases_content)
        aliases_file.chmod(0o755)

        return aliases

    def _create_wrapper_scripts(self) -> list[dict]:
        """Create wrapper scripts for common workflows."""
        scripts = []

        # Development setup script
        dev_setup_script = self.project_root / "scripts" / "dev_setup.sh"
        dev_setup_content = """#!/bin/bash
# Development Environment Setup

echo "🚀 Setting up development environment..."

# Install dependencies
uv sync --extra dev

# Run pre-commit install
uv run pre-commit install

# Run system health check
uv run python scripts/system_health_check.py

echo "✅ Development environment ready!"
"""
        dev_setup_script.write_text(dev_setup_content)
        dev_setup_script.chmod(0o755)
        scripts.append(
            {
                "name": "dev_setup.sh",
                "path": str(dev_setup_script),
                "description": "Complete development environment setup",
            }
        )

        # Quick test script
        quick_test_script = self.project_root / "scripts" / "quick_test.sh"
        quick_test_content = """#!/bin/bash
# Quick Test Runner

echo "🧪 Running quick tests..."

# Run linting
uvx ruff check .

# Run tests
uv run pytest tests/ -v --tb=short

# Run type checking
uv run python -m pyright

echo "✅ Quick tests completed!"
"""
        quick_test_script.write_text(quick_test_content)
        quick_test_script.chmod(0o755)
        scripts.append(
            {"name": "quick_test.sh", "path": str(quick_test_script), "description": "Quick test and linting workflow"}
        )

        # Performance check script
        perf_check_script = self.project_root / "scripts" / "perf_check.sh"
        perf_check_content = """#!/bin/bash
# Performance Check

echo "📊 Running performance checks..."

# Monitor UV performance
python scripts/uv_performance_monitor.py

# Check dependencies
python scripts/uv_dependency_manager.py --analyze

# Security scan
python scripts/uv_dependency_manager.py --security

echo "✅ Performance checks completed!"
"""
        perf_check_script.write_text(perf_check_content)
        perf_check_script.chmod(0o755)
        scripts.append(
            {
                "name": "perf_check.sh",
                "path": str(perf_check_script),
                "description": "Comprehensive performance and security check",
            }
        )

        return scripts

    def _create_automation_scripts(self) -> list[dict]:
        """Create automation scripts for regular tasks."""
        automation = []

        # Daily maintenance script
        daily_maintenance = self.project_root / "scripts" / "daily_maintenance.py"
        daily_content = '''#!/usr/bin/env python3
"""
Daily UV Maintenance Script

Automated daily maintenance tasks for UV environment.
"""

import subprocess
import sys
from datetime import datetime

def run_daily_maintenance():
    """Run daily maintenance tasks."""
    print(f"🔧 Daily UV Maintenance - {datetime.now().strftime('%Y-%m-%d')}")

    tasks = [
        ("Check for outdated packages", ["uv", "pip", "list", "--outdated"]),
        ("Update lock file", ["uv", "lock"]),
        ("Run security scan", ["python", "scripts/uv_dependency_manager.py", "--security"]),
        ("Performance check", ["python", "scripts/uv_performance_monitor.py"])
    ]

    for task_name, cmd in tasks:
        print(f"\\n📋 {task_name}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {task_name} completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ {task_name} failed: {e}")

if __name__ == "__main__":
    run_daily_maintenance()
'''
        daily_maintenance.write_text(daily_content)
        daily_maintenance.chmod(0o755)
        automation.append(
            {
                "name": "daily_maintenance.py",
                "path": str(daily_maintenance),
                "description": "Automated daily maintenance tasks",
                "schedule": "daily",
            }
        )

        # Weekly optimization script
        weekly_optimization = self.project_root / "scripts" / "weekly_optimization.py"
        weekly_content = '''#!/usr/bin/env python3
"""
Weekly UV Optimization Script

Automated weekly optimization tasks for UV environment.
"""

import subprocess
import sys
from datetime import datetime

def run_weekly_optimization():
    """Run weekly optimization tasks."""
    print(f"⚡ Weekly UV Optimization - {datetime.now().strftime('%Y-%m-%d')}")

    tasks = [
        ("Full dependency analysis", ["python", "scripts/uv_dependency_manager.py", "--full-report"]),
        ("Performance analysis", ["python", "scripts/uv_performance_monitor.py"]),
        ("Workflow optimization", ["python", "scripts/uv_workflow_optimizer.py"]),
        ("Clean cache", ["uv", "cache", "clean"])
    ]

    for task_name, cmd in tasks:
        print(f"\\n📋 {task_name}...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ {task_name} completed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ {task_name} failed: {e}")

if __name__ == "__main__":
    run_weekly_optimization()
'''
        weekly_optimization.write_text(weekly_content)
        weekly_optimization.chmod(0o755)
        automation.append(
            {
                "name": "weekly_optimization.py",
                "path": str(weekly_optimization),
                "description": "Automated weekly optimization tasks",
                "schedule": "weekly",
            }
        )

        return automation

    def generate_workflow_guide(self, patterns: dict, scripts: dict) -> str:
        """Generate a comprehensive workflow optimization guide."""
        guide = f"""# 🚀 UV Workflow Optimization Guide

**Generated**: {patterns['timestamp']}

## 📊 Workflow Analysis

### Common Commands
"""

        for cmd, info in patterns["common_commands"].items():
            guide += f"- **{cmd}**: {info['use_case']} - {info['optimization']}\n"

        guide += "\n### Performance Bottlenecks\n"
        for bottleneck in patterns["performance_bottlenecks"]:
            guide += f"- **{bottleneck['type']}**: {bottleneck['description']} (Impact: {bottleneck['impact']})\n"
            guide += f"  - Solution: {bottleneck['solution']}\n"

        guide += "\n### Automation Opportunities\n"
        for opp in patterns["automation_opportunities"]:
            guide += f"- **{opp['type']}**: {opp['description']}\n"
            guide += f"  - Script: {opp['script']}\n"
            guide += f"  - Benefit: {opp['benefit']}\n"

        guide += "\n## 🛠️ Optimized Scripts Created\n"

        guide += "\n### Shell Aliases\n"
        for alias in scripts["aliases"]:
            guide += f"- `{alias['alias']}`: {alias['description']}\n"
            guide += f"  - Command: `{alias['command']}`\n"

        guide += "\n### Wrapper Scripts\n"
        for script in scripts["scripts"]:
            guide += f"- **{script['name']}**: {script['description']}\n"
            guide += f"  - Path: `{script['path']}`\n"

        guide += "\n### Automation Scripts\n"
        for automation in scripts["automation"]:
            guide += f"- **{automation['name']}**: {automation['description']}\n"
            guide += f"  - Schedule: {automation['schedule']}\n"
            guide += f"  - Path: `{automation['path']}`\n"

        guide += "\n## 💡 Optimization Recommendations\n"
        for i, suggestion in enumerate(patterns["optimization_suggestions"], 1):
            guide += f"{i}. {suggestion}\n"

        guide += "\n## 🚀 Quick Start\n"
        guide += "1. Source the aliases: `source uv_aliases.sh`\n"
        guide += "2. Run development setup: `./scripts/dev_setup.sh`\n"
        guide += "3. Use quick test: `./scripts/quick_test.sh`\n"
        guide += "4. Schedule automation: Add to crontab or CI/CD\n"

        return guide


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Optimize UV workflows")
    parser.add_argument("--analyze", action="store_true", help="Analyze workflow patterns")
    parser.add_argument("--create-scripts", action="store_true", help="Create optimized scripts")
    parser.add_argument("--full-optimization", action="store_true", help="Run full optimization")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Output file for guide")

    args = parser.parse_args()

    optimizer = UVWorkflowOptimizer()

    if args.analyze:
        patterns = optimizer.analyze_workflow_patterns()
        if args.json:
            print(json.dumps(patterns, indent=2))
        else:
            print("📊 Workflow Analysis Results:")
            print(f"Common commands: {len(patterns['common_commands'])}")
            print(f"Bottlenecks: {len(patterns['performance_bottlenecks'])}")
            print(f"Automation opportunities: {len(patterns['automation_opportunities'])}")
            for suggestion in patterns["optimization_suggestions"][:3]:
                print(f"💡 {suggestion}")

    elif args.create_scripts:
        scripts = optimizer.create_optimized_scripts()
        if args.json:
            print(json.dumps(scripts, indent=2))
        else:
            print("🛠️ Created optimized scripts:")
            print(f"Aliases: {len(scripts['aliases'])}")
            print(f"Wrapper scripts: {len(scripts['scripts'])}")
            print(f"Automation scripts: {len(scripts['automation'])}")

    elif args.full_optimization:
        print("🚀 Running full workflow optimization...")

        patterns = optimizer.analyze_workflow_patterns()
        scripts = optimizer.create_optimized_scripts()

        guide = optimizer.generate_workflow_guide(patterns, scripts)

        if args.output:
            output_file = Path(args.output)
            output_file.write_text(guide)
            print(f"📄 Optimization guide saved to {output_file}")
        else:
            print(guide)

    else:
        # Default: run analysis
        patterns = optimizer.analyze_workflow_patterns()

        if args.json:
            print(json.dumps(patterns, indent=2))
        else:
            print("📊 Quick Workflow Analysis:")
            print(f"Common commands: {len(patterns['common_commands'])}")
            print(f"Bottlenecks: {len(patterns['performance_bottlenecks'])}")
            print(f"Automation opportunities: {len(patterns['automation_opportunities'])}")

            print("\n💡 Top Recommendations:")
            for suggestion in patterns["optimization_suggestions"][:3]:
                print(f"- {suggestion}")


if __name__ == "__main__":
    main()
