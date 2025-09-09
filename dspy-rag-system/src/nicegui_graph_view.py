#!/usr/bin/env python3
"""
NiceGUI Graph Visualization Application

Interactive network graph visualization for chunk relationships using Cytoscape.js.
Provides a dedicated interface for exploring document chunk relationships with
advanced graph visualization capabilities.
"""

import json
import logging
import os
from typing import Any, cast

import httpx

# Best-effort import for type checkers and runtime; set to Any for linters
try:  # pragma: no cover - UI import is environment-dependent
    from nicegui import ui as _ui  # type: ignore[import-not-found]
except Exception:  # pragma: no cover
    _ui = None  # type: ignore[assignment]

# Expose 'ui' as Any to avoid attribute-resolution lints when NiceGUI isn't installed
ui = cast(Any, _ui)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")
GRAPH_DATA_ENDPOINT = f"{DASHBOARD_URL}/graph-data"


class GraphVisualizationApp:
    """NiceGUI application for graph visualization."""

    def __init__(self):
        self.current_data: dict[str, Any] | None = None
        self.cytoscape_container = None
        self.stats_container = None
        self.controls_container = None
        self.loading_indicator = None

    def create_ui(self):
        """Create the main UI components."""
        if ui is None:  # pragma: no cover
            logging.warning("NiceGUI not available; skipping UI creation")
            return
        # Main container
        with ui.column().classes("w-full h-full p-4"):
            # Header
            with ui.row().classes("w-full justify-between items-center mb-4"):
                ui.html("<h1><i class='fas fa-project-diagram'></i> Graph Visualization</h1>").classes(
                    "text-2xl font-bold"
                )
                ui.button("Back to Dashboard", on_click=self.open_dashboard).classes("bg-blue-500 text-white")

            # Controls section
            self.create_controls()

            # Statistics section
            self.create_statistics()

            # Graph visualization section
            self.create_graph_visualization()

    def create_controls(self):
        """Create the controls section."""
        if ui is None:  # pragma: no cover
            return
        with ui.card().classes("w-full mb-4"):
            ui.label("Graph Controls").classes("text-lg font-semibold mb-2")

            with ui.row().classes("w-full gap-4"):
                # Query input
                with ui.column().classes("flex-1"):
                    ui.label("Search Query (Optional)")
                    self.query_input = ui.input(placeholder="Enter search query to filter chunks...").classes("w-full")

                # Max nodes input
                with ui.column().classes("w-32"):
                    ui.label("Max Nodes")
                    self.max_nodes_input = ui.number(value=2000, min=100, max=10000).classes("w-full")

            with ui.row().classes("w-full gap-4 mt-2"):
                # Similarity slider
                with ui.column().classes("flex-1"):
                    ui.label("Minimum Similarity")
                    self.similarity_slider = ui.slider(min=0.0, max=1.0, step=0.1, value=0.5).classes("w-full")
                    ui.label("0.5").bind_text_from(self.similarity_slider, "value")

                # Edge toggles
                with ui.column().classes("flex-1"):
                    with ui.row().classes("gap-4"):
                        self.include_knn = ui.checkbox("Include KNN Edges", value=True)
                        self.include_entity = ui.checkbox("Include Entity Edges", value=True)

                # Action buttons
                with ui.column().classes("flex-1"):
                    with ui.row().classes("gap-2"):
                        ui.button("Load Graph", on_click=self.load_graph_data).classes("bg-green-500 text-white")
                        ui.button("Reset View", on_click=self.reset_view).classes("bg-gray-500 text-white")

    def create_statistics(self):
        """Create the statistics section."""
        if ui is None:  # pragma: no cover
            return
        with ui.card().classes("w-full mb-4"):
            ui.label("Graph Statistics").classes("text-lg font-semibold mb-2")

            with ui.row().classes("w-full gap-4"):
                self.node_count = ui.label("Nodes: 0").classes("text-sm")
                self.edge_count = ui.label("Edges: 0").classes("text-sm")
                self.load_time = ui.label("Load Time: 0ms").classes("text-sm")
                self.truncated_status = ui.label("").classes("text-sm text-orange-600")

    def create_graph_visualization(self):
        """Create the graph visualization section."""
        if ui is None:  # pragma: no cover - guard when NiceGUI unavailable
            logging.warning("NiceGUI not available; skipping graph UI setup")
            return

        with ui.card().classes("w-full flex-1"):
            ui.label("Network Graph").classes("text-lg font-semibold mb-2")

            # Loading indicator
            self.loading_indicator = ui.spinner(size="lg").classes("hidden")

            # Add Cytoscape and helper functions
            ui.add_body_html(
                """
                <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
                <script>
                  window.cy = null;
                  window.createGraph = function(data) {
                    if (window.cy) {
                      window.cy.destroy();
                    }
                    const nodes = (data.nodes || []).map(n => ({ data: { id: n.id, label: n.label, category: n.category, anchor: n.anchor || '', coords: n.coords } }));
                    const edges = (data.edges || []).map(e => ({ data: { id: e.source + '-' + e.target, source: e.source, target: e.target, type: e.type, weight: e.weight } }));
                    window.cy = cytoscape({
                      container: document.getElementById('cy'),
                      elements: { nodes: nodes, edges: edges },
                      style: [
                        { selector: 'node', style: {
                            'background-color': function(ele){
                              const c = ele.data('category');
                              const colors = { anchor:'#ef4444', documentation:'#10b981', code:'#6366f1', other:'#6b7280' };
                              return colors[c] || colors['other'];
                            },
                            'label': 'data(label)', 'text-valign': 'center', 'text-halign': 'center', 'text-wrap': 'wrap', 'text-max-width': '80px',
                            'font-size': '8px', 'color': '#ffffff', 'text-outline-width': 1, 'text-outline-color': '#000000', 'width': 20, 'height': 20
                        }},
                        { selector: 'edge', style: {
                            'width': function(ele){ return Math.max(1, (ele.data('weight')||0.3) * 3); },
                            'line-color': function(ele){ return ele.data('type') === 'knn' ? '#8b5cf6' : '#f59e0b'; },
                            'opacity': 0.6, 'curve-style': 'bezier'
                        }},
                        { selector: 'edge[type="knn"]', style: { 'line-color': '#8b5cf6' } },
                        { selector: 'edge[type="entity"]', style: { 'line-color': '#f59e0b' } }
                      ],
                      layout: { name: 'cose', animate: 'end', animationDuration: 800, nodeDimensionsIncludeLabels: true }
                    });
                    window.cy.on('tap', 'node', function(evt){
                      const d = evt.target.data();
                      alert('Node: ' + d.label + '\nCategory: ' + d.category + '\nAnchor: ' + (d.anchor || 'None'));
                    });
                    window.cy.fit();
                  };
                  window.resetView = function(){ if (window.cy) { window.cy.fit(); } };
                </script>
                """
            )

            # Cytoscape container
            self.cytoscape_container = ui.html(
                '<div id="cy" style="width: 100%; height: 600px; border: 1px solid #ccc;"></div>'
            ).classes("w-full")

    async def load_graph_data(self):
        """Load graph data from the API."""
        try:
            # Show loading indicator
            if ui and self.loading_indicator:
                self.loading_indicator.classes(replace="block")

            # Build query parameters
            params = {
                "max_nodes": self.max_nodes_input.value,
                "min_sim": self.similarity_slider.value,
                "include_knn": self.include_knn.value,
                "include_entity": self.include_entity.value,
            }

            if self.query_input.value.strip():
                params["q"] = self.query_input.value.strip()

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.get(GRAPH_DATA_ENDPOINT, params=params)
                response.raise_for_status()
                data = response.json()

            # Store current data
            self.current_data = data

            # Update statistics
            self.node_count.text = f"Nodes: {len(data['nodes'])}"
            self.edge_count.text = f"Edges: {len(data['edges'])}"
            self.load_time.text = f"Load Time: {data['elapsed_ms']:.0f}ms"

            if data.get("truncated"):
                self.truncated_status.text = "⚠️ Truncated"
            else:
                self.truncated_status.text = ""

            # Update graph visualization
            await self.update_graph_visualization(data)

        except Exception as e:
            logger.error(f"Error loading graph data: {e}")
            ui.notify(f"Error loading graph data: {str(e)}", type="negative")

        finally:
            # Hide loading indicator
            if ui and self.loading_indicator:
                self.loading_indicator.classes(replace="hidden")

    async def update_graph_visualization(self, data: dict[str, Any]):
        """Update the graph visualization with new data."""
        # Convert data to JSON string for JavaScript
        data_json = json.dumps(data)

        # Execute JavaScript to update the graph
        if ui:
            await ui.run_javascript(f"createGraph({data_json})")

    async def reset_view(self):
        """Reset the graph view."""
        if ui:
            await ui.run_javascript("resetView()")

    def open_dashboard(self):
        """Open the main dashboard in a new tab."""
        if ui:
            ui.run_javascript(f"window.open('{DASHBOARD_URL}', '_blank')")


def create_app() -> GraphVisualizationApp:
    """Create and configure the NiceGUI application."""
    app_instance = GraphVisualizationApp()
    app_instance.create_ui()
    return app_instance


# Main application entry point
if __name__ == "__main__":
    # Create the application
    graph_app = create_app()

    # Configure NiceGUI
    ui.run(title="Graph Visualization - DSPy RAG System", port=8080, reload=False, show=True, favicon="🔗")
