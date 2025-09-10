#!/usr/bin/env python3
"""
Migration script to transition from old configuration system to pydantic-settings.

This script helps identify and migrate existing configuration patterns.
"""

import ast
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


class ConfigurationMigrationAnalyzer:
    """Analyzes the codebase for configuration patterns that need migration."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_vars: Set[str] = set()
        self.yaml_files: Set[Path] = set()
        self.config_classes: Set[str] = set()
        self.os_getenv_calls: List[Tuple[Path, int, str]] = []

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze the entire codebase for configuration patterns."""
        print("🔍 Analyzing codebase for configuration patterns...")

        # Find all Python files
        python_files = list(self.project_root.rglob("*.py"))
        print(f"Found {len(python_files)} Python files to analyze")

        for py_file in python_files:
            if self._should_skip_file(py_file):
                continue

            self._analyze_python_file(py_file)

        # Find YAML configuration files
        self._find_yaml_configs()

        return {
            "env_vars": sorted(self.env_vars),
            "yaml_files": sorted(self.yaml_files),
            "config_classes": sorted(self.config_classes),
            "os_getenv_calls": self.os_getenv_calls,
        }

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during analysis."""
        skip_patterns = [
            "venv/",
            "__pycache__/",
            ".git/",
            "600_archives/",
            "docs/legacy/",
            "node_modules/",
        ]

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_python_file(self, file_path: Path):
        """Analyze a single Python file for configuration patterns."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find os.getenv calls
            self._find_os_getenv_calls(file_path, content)

            # Find environment variable references
            self._find_env_var_references(content)

            # Find configuration classes
            self._find_config_classes(file_path, content)

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _find_os_getenv_calls(self, file_path: Path, content: str):
        """Find os.getenv calls in the file."""
        pattern = r'os\.getenv\(["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content):
            env_var = match.group(1)
            line_num = content[: match.start()].count("\n") + 1
            self.os_getenv_calls.append((file_path, line_num, env_var))
            self.env_vars.add(env_var)

    def _find_env_var_references(self, content: str):
        """Find environment variable references in the content."""
        # Look for patterns like os.environ['VAR'] or os.environ.get('VAR')
        patterns = [
            r'os\.environ\[["\']([^"\']+)["\']\]',
            r'os\.environ\.get\(["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                env_var = match.group(1)
                self.env_vars.add(env_var)

    def _find_config_classes(self, file_path: Path, content: str):
        """Find configuration-related classes in the file."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    if any(keyword in class_name.lower() for keyword in ["config", "settings", "timeout", "database"]):
                        self.config_classes.add(f"{file_path}:{class_name}")
        except SyntaxError:
            pass  # Skip files with syntax errors

    def _find_yaml_configs(self):
        """Find YAML configuration files."""
        yaml_patterns = ["*.yaml", "*.yml"]
        for pattern in yaml_patterns:
            self.yaml_files.update(self.project_root.rglob(pattern))

    def generate_migration_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive migration report."""
        report = []
        report.append("# Configuration Migration Report")
        report.append("")

        # Environment variables section
        report.append("## Environment Variables Found")
        report.append(f"Total unique environment variables: {len(analysis['env_vars'])}")
        report.append("")

        for env_var in analysis["env_vars"]:
            report.append(f"- `{env_var}`")
        report.append("")

        # os.getenv calls section
        report.append("## os.getenv() Calls to Migrate")
        report.append(f"Total os.getenv calls: {len(analysis['os_getenv_calls'])}")
        report.append("")

        for file_path, line_num, env_var in analysis["os_getenv_calls"]:
            rel_path = file_path.relative_to(self.project_root)
            report.append(f"- `{rel_path}:{line_num}` - `{env_var}`")
        report.append("")

        # YAML files section
        report.append("## YAML Configuration Files")
        report.append(f"Total YAML files: {len(analysis['yaml_files'])}")
        report.append("")

        for yaml_file in analysis["yaml_files"]:
            rel_path = yaml_file.relative_to(self.project_root)
            report.append(f"- `{rel_path}`")
        report.append("")

        # Configuration classes section
        report.append("## Configuration Classes Found")
        report.append(f"Total configuration classes: {len(analysis['config_classes'])}")
        report.append("")

        for config_class in analysis["config_classes"]:
            report.append(f"- `{config_class}`")
        report.append("")

        # Migration recommendations
        report.append("## Migration Recommendations")
        report.append("")
        report.append("### 1. High Priority Migrations")
        report.append("- Replace `os.getenv()` calls with `get_settings()`")
        report.append("- Migrate custom configuration classes to pydantic-settings models")
        report.append("- Consolidate YAML configuration files")
        report.append("")

        report.append("### 2. Files to Update")
        files_to_update = set()
        for file_path, _, _ in analysis["os_getenv_calls"]:
            files_to_update.add(file_path.relative_to(self.project_root))

        for file_path in sorted(files_to_update):
            report.append(f"- `{file_path}`")
        report.append("")

        return "\n".join(report)

    def generate_migration_examples(self, analysis: Dict[str, Any]) -> str:
        """Generate migration examples for common patterns."""
        examples = []
        examples.append("# Migration Examples")
        examples.append("")

        # os.getenv migration examples
        examples.append("## os.getenv() Migration Examples")
        examples.append("")

        examples.append("### Before (old pattern):")
        examples.append("```python")
        examples.append("import os")
        examples.append("")
        examples.append("db_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))")
        examples.append("aws_region = os.getenv('AWS_REGION', 'us-east-1')")
        examples.append("chunk_size = int(os.getenv('CHUNK_SIZE', 450))")
        examples.append("```")
        examples.append("")

        examples.append("### After (pydantic-settings):")
        examples.append("```python")
        examples.append("from src.config import get_settings")
        examples.append("")
        examples.append("settings = get_settings()")
        examples.append("db_timeout = settings.performance.db_connect_timeout")
        examples.append("aws_region = settings.security.aws_region")
        examples.append("chunk_size = settings.rag.chunk_size")
        examples.append("```")
        examples.append("")

        # Configuration class migration examples
        examples.append("## Configuration Class Migration Examples")
        examples.append("")

        examples.append("### Before (custom class):")
        examples.append("```python")
        examples.append("@dataclass")
        examples.append("class TimeoutConfig:")
        examples.append("    db_connect_timeout: int = 10")
        examples.append("    db_read_timeout: int = 30")
        examples.append("    # ... manual loading logic")
        examples.append("```")
        examples.append("")

        examples.append("### After (pydantic-settings):")
        examples.append("```python")
        examples.append("from pydantic import BaseModel, Field")
        examples.append("from pydantic_settings import BaseSettings")
        examples.append("")
        examples.append("class Performance(BaseModel):")
        examples.append("    db_connect_timeout: int = Field(ge=1, le=60, default=10)")
        examples.append("    db_read_timeout: int = Field(ge=5, le=300, default=30)")
        examples.append("```")
        examples.append("")

        return "\n".join(examples)


def main():
    """Main migration analysis function."""
    project_root = Path(__file__).parent.parent
    analyzer = ConfigurationMigrationAnalyzer(project_root)

    print("🚀 Starting configuration migration analysis...")

    # Analyze the codebase
    analysis = analyzer.analyze_codebase()

    # Generate reports
    migration_report = analyzer.generate_migration_report(analysis)
    migration_examples = analyzer.generate_migration_examples(analysis)

    # Write reports to files
    report_file = project_root / "CONFIGURATION_MIGRATION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(migration_report)

    examples_file = project_root / "CONFIGURATION_MIGRATION_EXAMPLES.md"
    with open(examples_file, "w") as f:
        f.write(migration_examples)

    print("✅ Migration analysis complete!")
    print(f"📊 Found {len(analysis['env_vars'])} environment variables")
    print(f"📊 Found {len(analysis['os_getenv_calls'])} os.getenv calls")
    print(f"📊 Found {len(analysis['yaml_files'])} YAML files")
    print(f"📊 Found {len(analysis['config_classes'])} configuration classes")
    print("📄 Reports written to:")
    print(f"   - {report_file}")
    print(f"   - {examples_file}")


if __name__ == "__main__":
    main()
