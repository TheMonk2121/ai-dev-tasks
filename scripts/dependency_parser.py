#!/usr/bin/env python3
"""
Python Dependency Parser for Vector-Based System Mapping

Task 1.1: Python Dependency Parser Implementation
Extracts imports and relationships from Python files using AST module.
"""

import ast
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class PythonDependencyParser:
    """Parses Python files to extract dependencies and relationships."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.dependencies = {}
        self.relationships = {}
        self.parsing_stats = {
            "files_processed": 0,
            "files_failed": 0,
            "total_imports": 0,
            "total_functions": 0,
            "total_classes": 0,
            "processing_time": 0.0,
        }

    def parse_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single Python file and extract dependencies."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            file_deps = {
                "file_path": str(file_path.relative_to(self.project_root)),
                "absolute_path": str(file_path),
                "imports": [],
                "functions": [],
                "classes": [],
                "relationships": [],
                "parse_success": True,
                "error": None,
            }

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_deps["imports"].append(
                            {"type": "import", "module": alias.name, "alias": alias.asname, "line": node.lineno}
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        file_deps["imports"].append(
                            {
                                "type": "from_import",
                                "module": module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )

                elif isinstance(node, ast.FunctionDef):
                    file_deps["functions"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
                        }
                    )

                elif isinstance(node, ast.ClassDef):
                    file_deps["classes"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "bases": [self._get_base_name(base) for base in node.bases],
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        }
                    )

            return file_deps

        except Exception as e:
            return {
                "file_path": str(file_path.relative_to(self.project_root)),
                "absolute_path": str(file_path),
                "imports": [],
                "functions": [],
                "classes": [],
                "relationships": [],
                "parse_success": False,
                "error": str(e),
            }

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_attr_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{self._get_attr_name(decorator.func.value)}.{decorator.func.attr}"
        return "unknown_decorator"

    def _get_attr_name(self, node: ast.expr) -> str:
        """Extract attribute name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_attr_name(node.value)}.{node.attr}"
        return "unknown"

    def _get_base_name(self, base: ast.expr) -> str:
        """Extract base class name from AST node."""
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self._get_attr_name(base.value)}.{base.attr}"
        return "unknown_base"

    def find_python_files(self, directories: List[str] = None) -> List[Path]:
        """Find all Python files in specified directories."""
        if directories is None:
            directories = ["scripts", "tests", "dspy-rag-system"]

        python_files = []
        for directory in directories:
            dir_path = self.project_root / directory
            if dir_path.exists():
                python_files.extend(dir_path.rglob("*.py"))

        # Also include Python files in root directory
        root_files = list(self.project_root.glob("*.py"))
        python_files.extend(root_files)

        return python_files

    def parse_project(self, directories: List[str] = None) -> Dict[str, Any]:
        """Parse all Python files in the project."""
        start_time = time.time()

        python_files = self.find_python_files(directories)

        print(f"🔍 Found {len(python_files)} Python files to parse...")

        for file_path in python_files:
            try:
                file_deps = self.parse_python_file(file_path)

                if file_deps["parse_success"]:
                    self.dependencies[str(file_path.relative_to(self.project_root))] = file_deps
                    self.parsing_stats["files_processed"] += 1
                    self.parsing_stats["total_imports"] += len(file_deps["imports"])
                    self.parsing_stats["total_functions"] += len(file_deps["functions"])
                    self.parsing_stats["total_classes"] += len(file_deps["classes"])
                else:
                    self.parsing_stats["files_failed"] += 1
                    print(f"⚠️ Failed to parse {file_path}: {file_deps['error']}")

            except Exception as e:
                self.parsing_stats["files_failed"] += 1
                print(f"❌ Error processing {file_path}: {e}")

        self.parsing_stats["processing_time"] = time.time() - start_time

        return self.generate_dependency_report()

    def generate_dependency_report(self) -> Dict[str, Any]:
        """Generate comprehensive dependency report."""
        # Build import relationships
        import_relationships = {}
        for file_path, file_deps in self.dependencies.items():
            if not file_deps["parse_success"]:
                continue

            for imp in file_deps["imports"]:
                module = imp.get("module", "")
                if module:
                    if module not in import_relationships:
                        import_relationships[module] = []
                    import_relationships[module].append(
                        {"file": file_path, "type": imp["type"], "line": imp.get("line", 0)}
                    )

        # Build function call relationships (simplified)
        function_relationships = {}
        for file_path, file_deps in self.dependencies.items():
            if not file_deps["parse_success"]:
                continue

            for func in file_deps["functions"]:
                func_name = func["name"]
                if func_name not in function_relationships:
                    function_relationships[func_name] = []
                function_relationships[func_name].append({"file": file_path, "line": func["line"]})

        # Build class inheritance relationships
        class_relationships = {}
        for file_path, file_deps in self.dependencies.items():
            if not file_deps["parse_success"]:
                continue

            for cls in file_deps["classes"]:
                class_name = cls["name"]
                if class_name not in class_relationships:
                    class_relationships[class_name] = {
                        "file": file_path,
                        "bases": cls["bases"],
                        "methods": cls["methods"],
                    }

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "parsing_stats": self.parsing_stats,
            "dependencies": self.dependencies,
            "relationships": {
                "imports": import_relationships,
                "functions": function_relationships,
                "classes": class_relationships,
            },
            "summary": {
                "total_files": len(self.dependencies),
                "successful_parses": self.parsing_stats["files_processed"],
                "failed_parses": self.parsing_stats["files_failed"],
                "total_imports": self.parsing_stats["total_imports"],
                "total_functions": self.parsing_stats["total_functions"],
                "total_classes": self.parsing_stats["total_classes"],
                "processing_time": self.parsing_stats["processing_time"],
            },
        }

    def save_dependencies(self, output_file: str = "metrics/dependency_analysis.json"):
        """Save dependency analysis to JSON file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        report = self.generate_dependency_report()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 Dependency analysis saved to: {output_file}")
        return output_file

    def print_summary(self):
        """Print parsing summary."""
        stats = self.parsing_stats

        print("\n" + "=" * 60)
        print("📊 PYTHON DEPENDENCY PARSING SUMMARY")
        print("=" * 60)

        print(f"📁 Files Processed: {stats['files_processed']}")
        print(f"❌ Files Failed: {stats['files_failed']}")
        print(f"📦 Total Imports: {stats['total_imports']}")
        print(f"🔧 Total Functions: {stats['total_functions']}")
        print(f"🏗️ Total Classes: {stats['total_classes']}")
        print(f"⏱️ Processing Time: {stats['processing_time']:.3f}s")

        if stats["files_processed"] > 0:
            avg_time = stats["processing_time"] / stats["files_processed"]
            print(f"⚡ Average Time per File: {avg_time:.3f}s")

        print("\n🎯 Vector-Based System Mapping Phase 1 Progress:")
        print("  ✅ Task 1.1: Python Dependency Parser Implementation - COMPLETED")
        print("  🔄 Task 1.2: Basic Dependency Graph Construction - NEXT")
        print("  ⏳ Task 1.3: Simple Visualization Interface - PENDING")


def main():
    """Main function for dependency parsing."""
    print("🚀 Starting Vector-Based System Mapping Phase 1: Simple Dependency Mapping")
    print("=" * 60)
    print("📋 Task 1.1: Python Dependency Parser Implementation")
    print("=" * 60)

    # Initialize parser
    parser = PythonDependencyParser()

    # Parse project
    report = parser.parse_project()

    # Save results
    output_file = parser.save_dependencies()

    # Print summary
    parser.print_summary()

    return report


if __name__ == "__main__":
    main()
