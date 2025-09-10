#!/usr/bin/env python3
"""
Focused migration analysis for project-specific configuration patterns.
Excludes third-party dependencies and focuses on the actual project code.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


class FocusedConfigurationAnalyzer:
    """Analyzes only project-specific configuration patterns."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.env_vars: Set[str] = set()
        self.os_getenv_calls: List[Tuple[Path, int, str, str]] = []  # file, line, var, context
        self.yaml_files: Set[Path] = set()
        self.config_classes: Set[str] = set()

    def analyze_project(self) -> Dict[str, Any]:
        """Analyze only project-specific files."""
        print("🔍 Analyzing project-specific configuration patterns...")

        # Define project-specific directories
        project_dirs = [
            "src/",
            "scripts/",
            "tests/",
            "config/",
            "configs/",
        ]

        python_files = []
        for dir_name in project_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                python_files.extend(dir_path.rglob("*.py"))

        print(f"Found {len(python_files)} project Python files to analyze")

        for py_file in python_files:
            self._analyze_python_file(py_file)

        # Find project YAML files
        self._find_project_yaml_files()

        return {
            "env_vars": sorted(self.env_vars),
            "yaml_files": sorted(self.yaml_files),
            "config_classes": sorted(self.config_classes),
            "os_getenv_calls": self.os_getenv_calls,
        }

    def _analyze_python_file(self, file_path: Path):
        """Analyze a single Python file for configuration patterns."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Find os.getenv calls with context
            self._find_os_getenv_calls(file_path, content)

            # Find environment variable references
            self._find_env_var_references(content)

            # Find configuration classes
            self._find_config_classes(file_path, content)

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def _find_os_getenv_calls(self, file_path: Path, content: str):
        """Find os.getenv calls with surrounding context."""
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Look for os.getenv patterns
            patterns = [
                r'os\.getenv\(["\']([^"\']+)["\']',
                r'os\.environ\.get\(["\']([^"\']+)["\']',
                r'os\.environ\[["\']([^"\']+)["\']\]',
            ]

            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    env_var = match.group(1)
                    self.env_vars.add(env_var)

                    # Get context (previous and next lines)
                    context_start = max(0, i - 2)
                    context_end = min(len(lines), i + 3)
                    context = "\n".join(lines[context_start:context_end])

                    self.os_getenv_calls.append(
                        (file_path.relative_to(self.project_root), i + 1, env_var, context.strip())
                    )

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
        # Look for class definitions that might be configuration-related
        class_pattern = r"class\s+(\w*(?:Config|Settings|Timeout|Database|RAG|Eval|Memory|Security|Performance|Observability)\w*)\s*[\(:]"

        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            rel_path = file_path.relative_to(self.project_root)
            self.config_classes.add(f"{rel_path}:{class_name}")

    def _find_project_yaml_files(self):
        """Find YAML configuration files in project directories."""
        yaml_patterns = ["*.yaml", "*.yml"]
        for pattern in yaml_patterns:
            self.yaml_files.update(self.project_root.rglob(pattern))

        # Filter out non-project files
        self.yaml_files = {
            f
            for f in self.yaml_files
            if not any(
                skip in str(f)
                for skip in ["venv/", "__pycache__/", ".git/", "600_archives/", "docs/legacy/", "node_modules/"]
            )
        }

    def generate_focused_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a focused migration report."""
        report = []
        report.append("# Focused Configuration Migration Report")
        report.append("")
        report.append("This report focuses on project-specific configuration patterns that need migration.")
        report.append("")

        # Environment variables section
        report.append("## Project Environment Variables")
        report.append(f"Total unique environment variables: {len(analysis['env_vars'])}")
        report.append("")

        # Group by common prefixes
        grouped_vars = {}
        for env_var in analysis["env_vars"]:
            if env_var.startswith(
                ("APP_", "POSTGRES_", "AWS_", "OPENAI_", "DSPY_", "RAG_", "EVAL_", "CHUNK_", "DB_", "HTTP_", "LLM_")
            ):
                prefix = env_var.split("_")[0] + "_"
                if prefix not in grouped_vars:
                    grouped_vars[prefix] = []
                grouped_vars[prefix].append(env_var)
            else:
                if "OTHER" not in grouped_vars:
                    grouped_vars["OTHER"] = []
                grouped_vars["OTHER"].append(env_var)

        for prefix, vars_list in sorted(grouped_vars.items()):
            report.append(f"### {prefix}* variables ({len(vars_list)})")
            for var in sorted(vars_list):
                report.append(f"- `{var}`")
            report.append("")

        # os.getenv calls section
        report.append("## os.getenv() Calls to Migrate")
        report.append(f"Total os.getenv calls: {len(analysis['os_getenv_calls'])}")
        report.append("")

        # Group by file
        calls_by_file = {}
        for file_path, line_num, env_var, context in analysis["os_getenv_calls"]:
            if file_path not in calls_by_file:
                calls_by_file[file_path] = []
            calls_by_file[file_path].append((line_num, env_var, context))

        for file_path in sorted(calls_by_file.keys()):
            report.append(f"### {file_path}")
            for line_num, env_var, context in calls_by_file[file_path]:
                report.append(f"- Line {line_num}: `{env_var}`")
                report.append("  ```python")
                report.append(f"  {context}")
                report.append("  ```")
            report.append("")

        # YAML files section
        report.append("## Project YAML Configuration Files")
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

        # Migration priority
        report.append("## Migration Priority")
        report.append("")
        report.append("### High Priority (Core Configuration)")
        high_priority_vars = [
            "POSTGRES_DSN",
            "AWS_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "OPENAI_API_KEY",
            "DSPY_MODEL",
            "CHUNK_SIZE",
            "OVERLAP_RATIO",
            "DB_CONNECT_TIMEOUT",
            "DB_READ_TIMEOUT",
            "DB_WRITE_TIMEOUT",
            "HTTP_CONNECT_TIMEOUT",
            "HTTP_READ_TIMEOUT",
            "HTTP_TOTAL_TIMEOUT",
            "LLM_REQUEST_TIMEOUT",
            "LLM_STREAM_TIMEOUT",
        ]

        for var in high_priority_vars:
            if var in analysis["env_vars"]:
                report.append(f"- `{var}` - Core system configuration")
        report.append("")

        report.append("### Medium Priority (Feature Configuration)")
        medium_priority_vars = ["RAG_", "EVAL_", "MEMORY_", "CURSOR_", "LTST_", "PRIME_"]

        for prefix in medium_priority_vars:
            matching_vars = [v for v in analysis["env_vars"] if v.startswith(prefix)]
            if matching_vars:
                report.append(f"- `{prefix}*` variables ({len(matching_vars)} found)")
        report.append("")

        return "\n".join(report)


def main():
    """Main focused migration analysis function."""
    project_root = Path(__file__).parent.parent
    analyzer = FocusedConfigurationAnalyzer(project_root)

    print("🚀 Starting focused configuration migration analysis...")

    # Analyze the project
    analysis = analyzer.analyze_project()

    # Generate focused report
    focused_report = analyzer.generate_focused_report(analysis)

    # Write report to file
    report_file = project_root / "FOCUSED_CONFIGURATION_MIGRATION_REPORT.md"
    with open(report_file, "w") as f:
        f.write(focused_report)

    print("✅ Focused migration analysis complete!")
    print(f"📊 Found {len(analysis['env_vars'])} project environment variables")
    print(f"📊 Found {len(analysis['os_getenv_calls'])} os.getenv calls")
    print(f"📊 Found {len(analysis['yaml_files'])} YAML files")
    print(f"📊 Found {len(analysis['config_classes'])} configuration classes")
    print(f"📄 Focused report written to: {report_file}")


if __name__ == "__main__":
    main()
