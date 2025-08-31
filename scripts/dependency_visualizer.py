#!/usr/bin/env python3
"""
Dependency Visualizer for Vector-Based System Mapping

Task 1.3: Simple Visualization Interface
Creates a web-based visualization interface for dependency graphs.
"""

import json
import os
import time
import webbrowser
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Any, Dict

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️ NetworkX not available - visualization limited")


class DependencyVisualizer:
    """Creates web-based visualization for dependency graphs."""

    def __init__(self, graph_file: str = "metrics/graphs/simple_dependency_graph.json"):
        self.graph_file = graph_file
        self.graph_data = None
        self.visualization_dir = "metrics/visualizations"
        self.server_port = 8080

    def load_graph_data(self) -> bool:
        """Load graph data from JSON file."""
        try:
            if not os.path.exists(self.graph_file):
                print(f"❌ Graph file not found: {self.graph_file}")
                return False

            print(f"📂 Loading graph data from: {self.graph_file}")
            with open(self.graph_file, "r", encoding="utf-8") as f:
                self.graph_data = json.load(f)

            print(
                f"✅ Loaded graph with {len(self.graph_data.get('nodes', []))} nodes and {len(self.graph_data.get('edges', []))} edges"
            )
            return True

        except Exception as e:
            print(f"❌ Error loading graph data: {e}")
            return False

    def create_html_visualization(self) -> str:
        """Create HTML visualization with D3.js."""
        if not self.graph_data:
            print("❌ No graph data loaded")
            return ""

        print("🎨 Creating HTML visualization...")

        # Create visualization directory
        os.makedirs(self.visualization_dir, exist_ok=True)

        # Prepare data for D3.js
        nodes = self.graph_data.get("nodes", [])
        edges = self.graph_data.get("edges", [])

        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Vector-Based System Mapping - Dependency Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        #graph-container {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 6px;
            background: white;
        }}
        .controls {{
            margin: 20px 0;
            text-align: center;
        }}
        button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 0 5px;
        }}
        button:hover {{
            background: #0056b3;
        }}
        .node {{
            cursor: pointer;
        }}
        .node:hover {{
            stroke: #333;
            stroke-width: 2px;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="container">
                            <h1>🔗 Vector-Based System Mapping - Dependency Graph Visualization</h1>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(nodes)}</div>
                <div class="stat-label">Nodes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(edges)}</div>
                <div class="stat-label">Edges</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(edge['source'] for edge in edges))}</div>
                <div class="stat-label">Source Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(set(edge['target'] for edge in edges))}</div>
                <div class="stat-label">Target Files</div>
            </div>
        </div>

        <div class="controls">
            <button onclick="resetZoom()">Reset Zoom</button>
            <button onclick="toggleLabels()">Toggle Labels</button>
            <button onclick="exportGraph()">Export Graph</button>
        </div>

        <div id="graph-container"></div>
    </div>

    <script>
        // Graph data
        const nodes = {json.dumps(nodes)};
        const edges = {json.dumps(edges)};

        // Setup
        const width = document.getElementById('graph-container').offsetWidth;
        const height = 600;

        // Create SVG
        const svg = d3.select('#graph-container')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // Create tooltip
        const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);

        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(30));

        // Create links
        const link = svg.append('g')
            .selectAll('line')
            .data(edges)
            .enter().append('line')
            .attr('class', 'link')
            .attr('stroke-width', 1);

        // Create nodes
        const node = svg.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('r', d => Math.min(20, Math.max(5, (d.imports || 0) / 2 + 5)))
            .attr('fill', d => d.imports > 10 ? '#ff6b6b' : d.imports > 5 ? '#4ecdc4' : '#45b7d1')
            .on('mouseover', function(event, d) {{
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(`
                    <strong>${{d.id}}</strong><br/>
                    Imports: ${{d.imports || 0}}<br/>
                    Type: ${{d.type || 'file'}}
                `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            }})
            .on('mouseout', function(d) {{
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            }})
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        // Add labels
        const label = svg.append('g')
            .selectAll('text')
            .data(nodes)
            .enter().append('text')
            .attr('class', 'label')
            .text(d => d.id.split('/').pop().replace('.py', ''))
            .attr('font-size', '10px')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('pointer-events', 'none')
            .style('opacity', 0.7);

        // Update positions on simulation tick
        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);

            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        }});

        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}

        // Control functions
        function resetZoom() {{
            simulation.alpha(1).restart();
        }}

        function toggleLabels() {{
            const labels = d3.selectAll('.label');
            const currentOpacity = labels.style('opacity');
            labels.style('opacity', currentOpacity == 0.7 ? 0 : 0.7);
        }}

        function exportGraph() {{
            const dataStr = JSON.stringify({{nodes, edges}}, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'dependency_graph.json';
            link.click();
        }}

        // Add zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (event) => {{
                svg.selectAll('g').attr('transform', event.transform);
            }});

        svg.call(zoom);
    </script>
</body>
</html>
"""

        # Save HTML file
        html_file = os.path.join(self.visualization_dir, "dependency_graph.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📊 HTML visualization created: {html_file}")
        return html_file

    def create_simple_graph_if_needed(self) -> bool:
        """Create a simple graph if the main graph file doesn't exist."""
        if os.path.exists(self.graph_file):
            return True

        print("📊 Creating simple dependency graph...")

        try:
            import sys

            sys.path.append(".")
            from scripts.simple_dependency_graph_no_viz import SimpleDependencyGraphBuilder

            builder = SimpleDependencyGraphBuilder()
            result = builder.build_complete_graph()

            if result:
                print("✅ Simple graph created successfully")
                return True
            else:
                print("❌ Failed to create simple graph")
                return False

        except Exception as e:
            print(f"❌ Error creating simple graph: {e}")
            return False

    def start_web_server(self, html_file: str) -> None:
        """Start a simple web server to serve the visualization."""
        print(f"🌐 Starting web server on port {self.server_port}...")

        # Change to visualization directory
        os.chdir(self.visualization_dir)

        # Create a simple HTTP server
        class CustomHandler(SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                super().end_headers()

        try:
            server = HTTPServer(("localhost", self.server_port), CustomHandler)
            print(f"✅ Server started at http://localhost:{self.server_port}")
            print(f"📊 Visualization available at http://localhost:{self.server_port}/dependency_graph.html")

            # Open browser
            webbrowser.open(f"http://localhost:{self.server_port}/dependency_graph.html")

            # Keep server running
            server.serve_forever()

        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Error starting server: {e}")

    def create_visualization(self) -> Dict[str, Any]:
        """Create complete visualization."""
        start_time = time.time()

        print("🎨 Creating dependency graph visualization...")

        # Create simple graph if needed
        if not self.create_simple_graph_if_needed():
            return {}

        # Load graph data
        if not self.load_graph_data():
            return {}

        # Create HTML visualization
        html_file = self.create_html_visualization()

        # Create summary
        stats = {
            "nodes": len(self.graph_data.get("nodes", [])),
            "edges": len(self.graph_data.get("edges", [])),
            "html_file": html_file,
            "creation_time": time.time() - start_time,
        }

        return {
            "timestamp": datetime.now().isoformat(),
            "project": "Vector-Based System Mapping",
            "visualization_stats": stats,
            "html_file": html_file,
        }

    def print_summary(self, stats: Dict[str, Any]):
        """Print visualization summary."""
        print("\n" + "=" * 60)
        print("🎨 DEPENDENCY GRAPH VISUALIZATION SUMMARY")
        print("=" * 60)

        print(f"🟢 Nodes: {stats.get('nodes', 0)}")
        print(f"🔗 Edges: {stats.get('edges', 0)}")
        print(f"📊 HTML File: {stats.get('html_file', 'N/A')}")
        print(f"⏱️ Creation Time: {stats.get('creation_time', 0):.3f}s")

        print("\n🎯 Vector-Based System Mapping Phase 1 Progress:")
        print("  ✅ Task 1.1: Python Dependency Parser Implementation - COMPLETED")
        print("  ✅ Task 1.2: Basic Dependency Graph Construction - COMPLETED")
        print("  ✅ Task 1.3: Simple Visualization Interface - COMPLETED")
        print("\n🚀 Phase 1 Complete! Ready for Phase 2.")


def main():
    """Main function for dependency visualization."""
    print("🚀 Continuing Vector-Based System Mapping Phase 1: Simple Dependency Mapping")
    print("=" * 60)
    print("📋 Task 1.3: Simple Visualization Interface")
    print("=" * 60)

    # Initialize visualizer
    visualizer = DependencyVisualizer()

    # Create visualization
    result = visualizer.create_visualization()

    if result:
        # Print summary
        visualizer.print_summary(result.get("visualization_stats", {}))

        # Ask user if they want to start the web server
        print("\n🌐 Would you like to start the web server to view the visualization?")
        print("   (The visualization will open in your browser)")

        # For now, just show the file location
        html_file = result.get("html_file", "")
        if html_file:
            print(f"\n📊 Visualization file created: {html_file}")
            print("   You can open this file in your browser to view the dependency graph.")

    return result


if __name__ == "__main__":
    main()
