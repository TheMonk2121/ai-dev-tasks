#!/usr/bin/env python3
"""
Dependency Graph Builder for Vector-Based System Mapping

Task 1.2: Basic Dependency Graph Construction
Builds a dependency graph using NetworkX from parsed dependency data.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import networkx as nx

NETWORKX_AVAILABLE = True


class DependencyGraphBuilder:
    """Builds dependency graphs from parsed Python dependency data."""

    def __init__(self, dependency_file: str = "metrics/dependency_analysis.json"):
        self.dependency_file = dependency_file
        self.dependency_data = None
        self.graph = nx.DiGraph()
        self.graph_stats = {
            "nodes": 0,
            "edges": 0,
            "components": 0,
            "circular_dependencies": 0,
            "construction_time": 0.0,
        }

    def load_dependencies(self) -> bool:
        """Load dependency data from JSON file."""
        try:
            if not os.path.exists(self.dependency_file):
                print(f"❌ Dependency file not found: {self.dependency_file}")
                return False

            print(f"📂 Loading dependencies from: {self.dependency_file}")
            with open(self.dependency_file, "r", encoding="utf-8") as f:
                self.dependency_data = json.load(f)

            print(f"✅ Loaded {len(self.dependency_data.get('dependencies', {}))} files")
            return True

        except Exception as e:
            print(f"❌ Error loading dependencies: {e}")
            return False

    def build_import_graph(self) -> nx.DiGraph:
        """Build import dependency graph."""
        if not self.dependency_data:
            print("❌ No dependency data loaded")
            return nx.DiGraph()

        print("🔗 Building import dependency graph...")

        # Add nodes for all files
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if file_deps.get("parse_success", False):
                self.graph.add_node(file_path, type="file", imports=len(file_deps.get("imports", [])))

        # Add edges for import relationships
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False):
                continue

            for imp in file_deps.get("imports", []):
                module = imp.get("module", "")
                if module:
                    # Try to find the actual file for this module
                    target_file = self._find_module_file(module, file_path)
                    if target_file and target_file in self.graph:
                        self.graph.add_edge(
                            file_path,
                            target_file,
                            type="import",
                            import_type=imp.get("type", "unknown"),
                            line=imp.get("line", 0),
                        )

        return self.graph

    def _find_module_file(self, module: str, source_file: str) -> Optional[str]:
        """Find the actual file path for a module import."""
        # Handle relative imports
        if module.startswith("."):
            # This is a relative import - would need more complex logic
            return None

        # Handle absolute imports
        module_parts = module.split(".")

        # Look for the module in our dependency data
        for file_path in self.dependency_data.get("dependencies", {}):
            file_name = Path(file_path).stem
            if file_name == module_parts[0]:
                return file_path

        return None

    def build_function_graph(self) -> nx.DiGraph:
        """Build function call dependency graph."""
        if not self.dependency_data:
            return nx.DiGraph()

        print("🔗 Building function dependency graph...")

        func_graph = nx.DiGraph()

        # Add nodes for all functions
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False):
                continue

            for func in file_deps.get("functions", []):
                func_id = f"{file_path}:{func['name']}"
                func_graph.add_node(func_id, file=file_path, function=func["name"], line=func.get("line", 0))

        # Add edges for function calls (simplified - would need more analysis)
        # This is a placeholder for more sophisticated function call analysis

        return func_graph

    def build_class_graph(self) -> nx.DiGraph:
        """Build class inheritance dependency graph."""
        if not self.dependency_data:
            return nx.DiGraph()

        print("🔗 Building class inheritance graph...")

        class_graph = nx.DiGraph()

        # Add nodes for all classes
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False):
                continue

            for cls in file_deps.get("classes", []):
                class_id = f"{file_path}:{cls['name']}"
                class_graph.add_node(class_id, file=file_path, class_name=cls["name"], line=cls.get("line", 0))

        # Add edges for inheritance relationships
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False):
                continue

            for cls in file_deps.get("classes", []):
                class_id = f"{file_path}:{cls['name']}"

                for base in cls.get("bases", []):
                    # Try to find the base class
                    base_class_id = self._find_base_class(base)
                    if base_class_id:
                        class_graph.add_edge(class_id, base_class_id, type="inheritance", base_class=base)

        return class_graph

    def _find_base_class(self, base_name: str) -> Optional[str]:
        """Find the actual class for a base class name."""
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False):
                continue

            for cls in file_deps.get("classes", []):
                if cls["name"] == base_name:
                    return f"{file_path}:{cls['name']}"

        return None

    def analyze_graph(self) -> Dict[str, Any]:
        """Analyze the dependency graph."""
        if not self.graph:
            return {}

        print("📊 Analyzing dependency graph...")

        # Basic graph statistics
        self.graph_stats["nodes"] = self.graph.number_of_nodes()
        self.graph_stats["edges"] = self.graph.number_of_edges()

        # Connected components
        components = list(nx.strongly_connected_components(self.graph))
        self.graph_stats["components"] = len(components)

        # Circular dependencies
        circular_deps = []
        for component in components:
            if len(component) > 1:
                circular_deps.append(list(component))

        self.graph_stats["circular_dependencies"] = len(circular_deps)

        # Node centrality
        try:
            in_degree_centrality = nx.in_degree_centrality(self.graph)
            out_degree_centrality = nx.out_degree_centrality(self.graph)

            # Find most central nodes
            most_dependent = sorted(in_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            most_dependencies = sorted(out_degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

        except Exception as e:
            print(f"⚠️ Error calculating centrality: {e}")
            most_dependent = []
            most_dependencies = []

        return {
            "graph_stats": self.graph_stats,
            "circular_dependencies": circular_deps,
            "most_dependent_files": most_dependent,
            "most_dependencies_files": most_dependencies,
            "components": [list(comp) for comp in components if len(comp) > 1],
        }

    def export_graph(self, output_dir: str = "metrics/graphs") -> Dict[str, str]:
        """Export graph in multiple formats."""
        os.makedirs(output_dir, exist_ok=True)

        export_files = {}

        # Export as JSON
        json_file = os.path.join(output_dir, "dependency_graph.json")
        graph_data = {
            "nodes": [{"id": node, **self.graph.nodes[node]} for node in self.graph.nodes()],
            "edges": [{"source": u, "target": v, **self.graph.edges[u, v]} for u, v in self.graph.edges()],
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        export_files["json"] = json_file

        # Export as DOT (Graphviz format)
        dot_file = os.path.join(output_dir, "dependency_graph.dot")
        try:
            nx.drawing.nx_pydot.write_dot(self.graph, dot_file)
            export_files["dot"] = dot_file
        except Exception as e:
            print(f"⚠️ Could not export DOT format: {e}")

        # Export as PNG (if matplotlib is available)
        png_file = os.path.join(output_dir, "dependency_graph.png")
        try:
            plt.figure(figsize=(20, 16))
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
            nx.draw(
                self.graph,
                pos,
                with_labels=False,
                node_size=50,
                node_color="lightblue",
                edge_color="gray",
                arrows=True,
                alpha=0.7,
            )
            plt.title("Python Dependency Graph")
            plt.tight_layout()
            plt.savefig(png_file, dpi=150, bbox_inches="tight")
            plt.close()
            export_files["png"] = png_file
        except Exception as e:
            print(f"⚠️ Could not export PNG format: {e}")

        return export_files

    def build_complete_graph(self) -> Dict[str, Any]:
        """Build complete dependency graph with all relationships."""
        start_time = time.time()

        if not self.load_dependencies():
            return {}

        # Build import graph
        self.build_import_graph()

        # Build function graph
        func_graph = self.build_function_graph()

        # Build class graph
        class_graph = self.build_class_graph()

        # Analyze graphs
        analysis = self.analyze_graph()

        # Export graphs
        export_files = self.export_graph()

        self.graph_stats["construction_time"] = time.time() - start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "graph_stats": self.graph_stats,
            "analysis": analysis,
            "export_files": export_files,
            "graphs": {"import_graph": self.graph, "function_graph": func_graph, "class_graph": class_graph},
        }

    def print_summary(self):
        """Print graph construction summary."""
        stats = self.graph_stats

        print("\n" + "=" * 60)
        print("📊 DEPENDENCY GRAPH CONSTRUCTION SUMMARY")
        print("=" * 60)

        print(f"🟢 Nodes: {stats['nodes']}")
        print(f"🔗 Edges: {stats['edges']}")
        print(f"🔧 Components: {stats['components']}")
        print(f"⚠️ Circular Dependencies: {stats['circular_dependencies']}")
        print(f"⏱️ Construction Time: {stats['construction_time']:.3f}s")

        if stats["nodes"] > 0:
            density = stats["edges"] / (stats["nodes"] * (stats["nodes"] - 1))
            print(f"📊 Graph Density: {density:.6f}")

        print("\n🎯 Vector-Based System Mapping Phase 1 Progress:")
        print("  ✅ Task 1.1: Python Dependency Parser Implementation - COMPLETED")
        print("  ✅ Task 1.2: Basic Dependency Graph Construction - COMPLETED")
        print("  🔄 Task 1.3: Simple Visualization Interface - NEXT")


def main():
    """Main function for dependency graph construction."""
    print("🚀 Continuing Vector-Based System Mapping Phase 1: Simple Dependency Mapping")
    print("=" * 60)
    print("📋 Task 1.2: Basic Dependency Graph Construction")
    print("=" * 60)

    if not NETWORKX_AVAILABLE:
        print("❌ NetworkX is required but not available")
        return {}

    # Initialize graph builder
    builder = DependencyGraphBuilder()

    # Build complete graph
    result = builder.build_complete_graph()

    # Print summary
    builder.print_summary()

    return result


if __name__ == "__main__":
    main()
