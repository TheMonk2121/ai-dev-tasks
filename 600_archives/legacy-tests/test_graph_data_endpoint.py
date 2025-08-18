#!/usr/bin/env python3.11
"""
Unit tests for /graph-data endpoint.

Tests the Flask endpoint for chunk relationship visualization
with comprehensive validation and error handling.
"""

import json
import os
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from src.dashboard import DashboardConfig, app


class TestGraphDataEndpoint(TestCase):
    """Test cases for /graph-data endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Reset the real state for each test
        from src.dashboard import state

        state.graph_data_provider = None

    def test_get_graph_data_success(self):
        """Test successful graph data retrieval."""
        # Mock GraphDataProvider
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = [
            Mock(
                id="chunk_1", label="test.md:10-20", anchor="test_anchor", coords=(0.1, 0.2), category="documentation"
            ),
        ]
        mock_graph_data.edges = [
            Mock(source="chunk_1", target="chunk_2", type="knn", weight=0.85),
        ]
        mock_graph_data.elapsed_ms = 150.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = False

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                # Make request
                response = self.client.get("/graph-data")

                # Verify response
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)

                self.assertIn("nodes", data)
                self.assertIn("edges", data)
                self.assertIn("elapsed_ms", data)
                self.assertIn("v", data)
                self.assertIn("truncated", data)

                self.assertEqual(len(data["nodes"]), 1)
                self.assertEqual(len(data["edges"]), 1)
                self.assertEqual(data["elapsed_ms"], 150.0)
                self.assertEqual(data["v"], 1)
                self.assertFalse(data["truncated"])

    def test_get_graph_data_with_query(self):
        """Test graph data retrieval with query parameter."""
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = []
        mock_graph_data.edges = []
        mock_graph_data.elapsed_ms = 50.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = False

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                # Make request with query
                response = self.client.get("/graph-data?q=test+query")

                # Verify response
                self.assertEqual(response.status_code, 200)

                # Verify provider was called with query
                mock_provider.get_graph_data.assert_called_once()
                call_args = mock_provider.get_graph_data.call_args[1]
                self.assertEqual(call_args["query"], "test query")

    def test_get_graph_data_with_parameters(self):
        """Test graph data retrieval with all parameters."""
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = []
        mock_graph_data.edges = []
        mock_graph_data.elapsed_ms = 75.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = False

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                # Make request with all parameters
                response = self.client.get(
                    "/graph-data?q=test&include_knn=false&include_entity=true&min_sim=0.7&max_nodes=500"
                )

                # Verify response
                self.assertEqual(response.status_code, 200)

                # Verify provider was called with correct parameters
                mock_provider.get_graph_data.assert_called_once()
                call_args = mock_provider.get_graph_data.call_args[1]
                self.assertEqual(call_args["query"], "test")
                self.assertFalse(call_args["include_knn"])
                self.assertTrue(call_args["include_entity"])
                self.assertEqual(call_args["min_sim"], 0.7)
                self.assertEqual(call_args["max_nodes"], 500)

    def test_get_graph_data_feature_flag_disabled(self):
        """Test graph data when feature flag is disabled."""
        with patch.dict(os.environ, {"GRAPH_VISUALIZATION_ENABLED": "false"}):
            response = self.client.get("/graph-data")

            self.assertEqual(response.status_code, 403)
            data = json.loads(response.data)
            self.assertIn("error", data)
            self.assertIn("disabled", data["error"])

    def test_get_graph_data_invalid_min_sim(self):
        """Test graph data with invalid min_sim parameter."""
        response = self.client.get("/graph-data?min_sim=1.5")

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("min_sim must be between 0.0 and 1.0", data["error"])

    def test_get_graph_data_invalid_max_nodes(self):
        """Test graph data with invalid max_nodes parameter."""
        response = self.client.get("/graph-data?max_nodes=15000")

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("max_nodes must be between 1 and 10000", data["error"])

    def test_get_graph_data_query_too_long(self):
        """Test graph data with query that exceeds length limit."""
        long_query = "a" * (DashboardConfig.MAX_QUERY_LENGTH + 1)
        response = self.client.get(f"/graph-data?q={long_query}")

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Query too long", data["error"])

    def test_get_graph_data_provider_error(self):
        """Test graph data when provider raises an error."""
        mock_provider = Mock()
        mock_provider.get_graph_data.side_effect = ValueError("Test error")

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                response = self.client.get("/graph-data")

                self.assertEqual(response.status_code, 400)
                data = json.loads(response.data)
                self.assertIn("error", data)
                self.assertEqual(data["error"], "Test error")

    def test_get_graph_data_internal_error(self):
        """Test graph data when provider raises internal error."""
        mock_provider = Mock()
        mock_provider.get_graph_data.side_effect = Exception("Internal error")

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                response = self.client.get("/graph-data")

                self.assertEqual(response.status_code, 500)
                data = json.loads(response.data)
                self.assertIn("error", data)
                self.assertEqual(data["error"], "Internal server error")

    def test_get_graph_data_provider_initialization(self):
        """Test that GraphDataProvider is initialized correctly."""
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = []
        mock_graph_data.edges = []
        mock_graph_data.elapsed_ms = 100.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = False

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                # Make request
                response = self.client.get("/graph-data?max_nodes=1000")

                # Verify response
                self.assertEqual(response.status_code, 200)

                # Verify GraphDataProvider was initialized correctly
                mock_graph_provider_class.assert_called_once()
                call_args = mock_graph_provider_class.call_args[1]
                self.assertEqual(call_args["max_nodes"], 1000)
                self.assertTrue(call_args["cache_enabled"])
                self.assertTrue(call_args["feature_flag_enabled"])

    def test_get_graph_data_reuses_provider(self):
        """Test that GraphDataProvider is reused on subsequent calls."""
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = []
        mock_graph_data.edges = []
        mock_graph_data.elapsed_ms = 50.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = False

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                # Make first request
                response1 = self.client.get("/graph-data")
                self.assertEqual(response1.status_code, 200)

                # Make second request
                response2 = self.client.get("/graph-data")
                self.assertEqual(response2.status_code, 200)

                # Verify GraphDataProvider was only created once
                mock_graph_provider_class.assert_called_once()

    def test_get_graph_data_json_serialization(self):
        """Test that response data is properly JSON serializable."""
        mock_provider = Mock()
        mock_graph_data = Mock()
        mock_graph_data.nodes = [
            Mock(
                id="chunk_1", label="test.md:10-20", anchor="test_anchor", coords=(0.1, 0.2), category="documentation"
            ),
            Mock(id="chunk_2", label="test2.py:15-25", anchor=None, coords=(-0.3, 0.4), category="code"),
        ]
        mock_graph_data.edges = [
            Mock(source="chunk_1", target="chunk_2", type="knn", weight=0.85),
            Mock(source="chunk_2", target="chunk_3", type="entity", weight=1.0),
        ]
        mock_graph_data.elapsed_ms = 200.0
        mock_graph_data.v = 1
        mock_graph_data.truncated = True

        mock_provider.get_graph_data.return_value = mock_graph_data

        with patch("utils.database_resilience.DatabaseResilienceManager"):
            with patch("utils.graph_data_provider.GraphDataProvider") as mock_graph_provider_class:
                mock_graph_provider_class.return_value = mock_provider

                response = self.client.get("/graph-data")

                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)

                # Verify nodes are properly serialized
                self.assertEqual(len(data["nodes"]), 2)
                self.assertEqual(data["nodes"][0]["id"], "chunk_1")
                self.assertEqual(data["nodes"][0]["label"], "test.md:10-20")
                self.assertEqual(data["nodes"][0]["anchor"], "test_anchor")
                self.assertEqual(data["nodes"][0]["coords"], [0.1, 0.2])
                self.assertEqual(data["nodes"][0]["category"], "documentation")

                # Verify edges are properly serialized
                self.assertEqual(len(data["edges"]), 2)
                self.assertEqual(data["edges"][0]["source"], "chunk_1")
                self.assertEqual(data["edges"][0]["target"], "chunk_2")
                self.assertEqual(data["edges"][0]["type"], "knn")
                self.assertEqual(data["edges"][0]["weight"], 0.85)

                # Verify metadata
                self.assertEqual(data["elapsed_ms"], 200.0)
                self.assertEqual(data["v"], 1)
                self.assertTrue(data["truncated"])


if __name__ == "__main__":
    pytest.main([__file__])
