#!/usr/bin/env python3
"""
Unit tests for NiceGUI Graph Visualization Application.

Tests the NiceGUI application for graph visualization functionality.
"""

import os
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from src.nicegui_graph_view import GraphVisualizationApp


class TestNiceGUIGraphView(TestCase):
    """Test cases for NiceGUI Graph Visualization Application."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = GraphVisualizationApp()

    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        self.assertIsNotNone(self.app)
        self.assertIsNone(self.app.current_data)
        self.assertIsNone(self.app.cytoscape_container)
        self.assertIsNone(self.app.stats_container)
        self.assertIsNone(self.app.controls_container)
        self.assertIsNone(self.app.loading_indicator)

    def test_create_ui_components(self):
        """Test that UI components are created correctly."""
        # Mock UI components to avoid actual NiceGUI initialization
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.column.return_value.__enter__ = Mock()
            mock_ui.column.return_value.__exit__ = Mock()
            mock_ui.row.return_value.__enter__ = Mock()
            mock_ui.row.return_value.__exit__ = Mock()
            mock_ui.card.return_value.__enter__ = Mock()
            mock_ui.card.return_value.__exit__ = Mock()

            # Create UI
            self.app.create_ui()

            # Verify UI components were created
            self.assertIsNotNone(self.app.loading_indicator)

    @patch("src.nicegui_graph_view.httpx.AsyncClient")
    async def test_load_graph_data_success(self, mock_client_class):
        """Test successful graph data loading."""
        # Mock response data
        mock_data = {
            "nodes": [
                {
                    "id": "chunk_1",
                    "label": "test.md:10-20",
                    "anchor": "test_anchor",
                    "coords": [0.1, 0.2],
                    "category": "documentation",
                }
            ],
            "edges": [{"source": "chunk_1", "target": "chunk_2", "type": "knn", "weight": 0.85}],
            "elapsed_ms": 150.0,
            "v": 1,
            "truncated": False,
        }

        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.notify = Mock()
            mock_ui.run_javascript = AsyncMock()

            # Set up app components
            self.app.loading_indicator = Mock()
            self.app.loading_indicator.classes = Mock()
            self.app.node_count = Mock()
            self.app.edge_count = Mock()
            self.app.load_time = Mock()
            self.app.truncated_status = Mock()
            self.app.query_input = Mock()
            self.app.query_input.value = ""
            self.app.max_nodes_input = Mock()
            self.app.max_nodes_input.value = 2000
            self.app.similarity_slider = Mock()
            self.app.similarity_slider.value = 0.5
            self.app.include_knn = Mock()
            self.app.include_knn.value = True
            self.app.include_entity = Mock()
            self.app.include_entity.value = True

            # Test loading graph data
            await self.app.load_graph_data()

            # Verify API call was made
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            self.assertIn("/graph-data", call_args[0][0])

            # Verify statistics were updated
            self.app.node_count.text.assert_called_with("Nodes: 1")
            self.app.edge_count.text.assert_called_with("Edges: 1")
            self.app.load_time.text.assert_called_with("Load Time: 150ms")

            # Verify data was stored
            self.assertEqual(self.app.current_data, mock_data)

    @patch("src.nicegui_graph_view.httpx.AsyncClient")
    async def test_load_graph_data_with_query(self, mock_client_class):
        """Test graph data loading with query parameter."""
        # Mock response data
        mock_data = {"nodes": [], "edges": [], "elapsed_ms": 50.0, "v": 1, "truncated": False}

        # Mock HTTP client
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.notify = Mock()
            mock_ui.run_javascript = AsyncMock()

            # Set up app components
            self.app.loading_indicator = Mock()
            self.app.loading_indicator.classes = Mock()
            self.app.node_count = Mock()
            self.app.edge_count = Mock()
            self.app.load_time = Mock()
            self.app.truncated_status = Mock()
            self.app.query_input = Mock()
            self.app.query_input.value = "test query"
            self.app.max_nodes_input = Mock()
            self.app.max_nodes_input.value = 1000
            self.app.similarity_slider = Mock()
            self.app.similarity_slider.value = 0.7
            self.app.include_knn = Mock()
            self.app.include_knn.value = False
            self.app.include_entity = Mock()
            self.app.include_entity.value = True

            # Test loading graph data
            await self.app.load_graph_data()

            # Verify API call was made with query parameter
            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            self.assertIn("/graph-data", call_args[0][0])

            # Verify query parameter was included
            params = call_args[1]["params"]
            self.assertEqual(params["q"], "test query")
            self.assertEqual(params["max_nodes"], 1000)
            self.assertEqual(params["min_sim"], 0.7)
            self.assertFalse(params["include_knn"])
            self.assertTrue(params["include_entity"])

    @patch("src.nicegui_graph_view.httpx.AsyncClient")
    async def test_load_graph_data_error(self, mock_client_class):
        """Test graph data loading error handling."""
        # Mock HTTP client to raise exception
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Network error")
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.notify = Mock()

            # Set up app components
            self.app.loading_indicator = Mock()
            self.app.loading_indicator.classes = Mock()
            self.app.query_input = Mock()
            self.app.query_input.value = ""
            self.app.max_nodes_input = Mock()
            self.app.max_nodes_input.value = 2000
            self.app.similarity_slider = Mock()
            self.app.similarity_slider.value = 0.5
            self.app.include_knn = Mock()
            self.app.include_knn.value = True
            self.app.include_entity = Mock()
            self.app.include_entity.value = True

            # Test loading graph data with error
            await self.app.load_graph_data()

            # Verify error notification was shown
            mock_ui.notify.assert_called_once()
            call_args = mock_ui.notify.call_args
            self.assertIn("Error loading graph data", call_args[0][0])
            self.assertEqual(call_args[1]["type"], "error")

    async def test_update_graph_visualization(self):
        """Test graph visualization update."""
        # Mock data
        test_data = {"nodes": [{"id": "test", "label": "Test"}], "edges": []}

        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.run_javascript = AsyncMock()

            # Test updating graph visualization
            await self.app.update_graph_visualization(test_data)

            # Verify JavaScript was executed
            mock_ui.run_javascript.assert_called_once()
            call_args = mock_ui.run_javascript.call_args[0][0]
            self.assertIn("createGraph(", call_args)
            self.assertIn("test", call_args)

    async def test_reset_view(self):
        """Test reset view functionality."""
        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.run_javascript = AsyncMock()

            # Test reset view
            await self.app.reset_view()

            # Verify JavaScript was executed
            mock_ui.run_javascript.assert_called_once_with("resetView()")

    def test_open_dashboard(self):
        """Test opening dashboard functionality."""
        # Mock UI components
        with patch("src.nicegui_graph_view.ui") as mock_ui:
            mock_ui.run_javascript = Mock()

            # Test opening dashboard
            self.app.open_dashboard()

            # Verify JavaScript was executed
            mock_ui.run_javascript.assert_called_once()
            call_args = mock_ui.run_javascript.call_args[0][0]
            self.assertIn("window.open(", call_args)

    def test_environment_configuration(self):
        """Test environment configuration."""
        # Test default configuration
        os.environ.pop("DASHBOARD_URL", None)
        from src.nicegui_graph_view import DASHBOARD_URL, GRAPH_DATA_ENDPOINT

        self.assertEqual(DASHBOARD_URL, "http://localhost:5000")
        self.assertEqual(GRAPH_DATA_ENDPOINT, "http://localhost:5000/graph-data")

        # Test custom configuration
        os.environ["DASHBOARD_URL"] = "http://custom:8080"
        # Note: We can't easily test this without reloading the module
        # The test above verifies the default behavior


if __name__ == "__main__":
    pytest.main([__file__])
