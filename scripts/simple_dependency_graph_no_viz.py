#!/usr/bin/env python3
"""
Simple Dependency Graph Builder (No Visualization) for Vector-Based System Mapping

Task 1.2: Basic Dependency Graph Construction
Builds a dependency graph using NetworkX from parsed dependency data.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import networkx as nx


class SimpleDependencyGraphBuilder:
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

    def build_simple_graph(self) -> nx.DiGraph:
        """Build a simple import dependency graph."""
        if not self.dependency_data:
            print("❌ No dependency data loaded")
            return nx.DiGraph()

        print("🔗 Building simple import dependency graph...")

        # Add nodes for all files (limit to first 1000 for performance)
        file_count = 0
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if file_deps.get("parse_success", False) and file_count < 1000:
                self.graph.add_node(file_path, type="file", imports=len(file_deps.get("imports", [])))
                file_count += 1

        print(f"🟢 Added {file_count} nodes to graph")

        # Add edges for import relationships (limit to first 5000 for performance)
        edge_count = 0
        for file_path, file_deps in self.dependency_data.get("dependencies", {}).items():
            if not file_deps.get("parse_success", False) or edge_count >= 5000:
                continue

            for imp in file_deps.get("imports", []):
                module = imp.get("module", "")
                if module and edge_count < 5000:
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
                        edge_count += 1

        print(f"🔗 Added {edge_count} edges to graph")
        return self.graph

    def _find_module_file(self, module: str, source_file: str) -> Optional[str]:
        """Find the actual file path for a module import."""
        # Handle relative imports
        if module.startswith("."):
            return None

        # Handle absolute imports
        module_parts = module.split(".")

        # Look for the module in our dependency data
        for file_path in self.dependency_data.get("dependencies", {}):
            file_name = Path(file_path).stem
            if file_name == module_parts[0]:
                return file_path

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
        try:
            components = list(nx.strongly_connected_components(self.graph))
            self.graph_stats["components"] = len(components)

            # Circular dependencies
            circular_deps = []
            for component in components:
                if len(component) > 1:
                    circular_deps.append(list(component))

            self.graph_stats["circular_dependencies"] = len(circular_deps)

        except Exception as e:
            print(f"⚠️ Error analyzing components: {e}")
            self.graph_stats["components"] = 0
            self.graph_stats["circular_dependencies"] = 0
            circular_deps = []

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
        }

    def export_graph(self, output_dir: str = "metrics/graphs") -> Dict[str, str]:
        """Export graph in JSON format."""
        os.makedirs(output_dir, exist_ok=True)

        export_files = {}

        # Export as JSON
        json_file = os.path.join(output_dir, "simple_dependency_graph.json")
        graph_data = {
            "nodes": [{"id": node, **self.graph.nodes[node]} for node in self.graph.nodes()],
            "edges": [{"source": u, "target": v, **self.graph.edges[u, v]} for u, v in self.graph.edges()],
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        export_files["json"] = json_file
        print(f"📊 Graph exported to JSON: {json_file}")

        return export_files

    def build_complete_graph(self) -> Dict[str, Any]:
        """Build complete dependency graph with all relationships."""
        start_time = time.time()

        if not self.load_dependencies():
            return {}

        # Build simple graph
        self.build_simple_graph()

        # Analyze graph
        analysis = self.analyze_graph()

        # Export graph
        export_files = self.export_graph()

        self.graph_stats["construction_time"] = time.time() - start_time

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "graph_stats": self.graph_stats,
            "analysis": analysis,
            "export_files": export_files,
        }

    def print_summary(self):
        """Print graph construction summary."""
        stats = self.graph_stats

        print("\n" + "=" * 60)
        print("📊 SIMPLE DEPENDENCY GRAPH CONSTRUCTION SUMMARY")
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
    print("📋 Task 1.2: Basic Dependency Graph Construction (Simplified)")
    print("=" * 60)

    # Initialize graph builder
    builder = SimpleDependencyGraphBuilder()

    # Build complete graph
    result = builder.build_complete_graph()

    # Print summary
    builder.print_summary()

    return result


if __name__ == "__main__":
    main()
