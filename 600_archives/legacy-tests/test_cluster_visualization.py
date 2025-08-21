#!/usr/bin/env python3
"""
Unit tests for cluster visualization page.

Tests the Flask route for cluster visualization page.

DEPRECATED: This test file is archived and should not be run.
Use current test infrastructure instead.
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated

from src.dashboard import app


class TestClusterVisualization:
    """Test cases for cluster visualization page."""

    def test_cluster_route_returns_200(self):
        """Test that /cluster route returns 200 status."""
        with app.test_client() as client:
            response = client.get("/cluster")
            assert response.status_code == 200

    def test_cluster_route_returns_html(self):
        """Test that /cluster route returns HTML content."""
        with app.test_client() as client:
            response = client.get("/cluster")
            assert "text/html" in response.headers["Content-Type"]
            assert "Chunk Cluster Visualization" in response.data.decode()

    def test_cluster_route_contains_plotly(self):
        """Test that cluster page contains Plotly.js."""
        with app.test_client() as client:
            response = client.get("/cluster")
            html = response.data.decode()
            assert "plotly-latest.min.js" in html

    def test_cluster_route_contains_controls(self):
        """Test that cluster page contains interactive controls."""
        with app.test_client() as client:
            response = client.get("/cluster")
            html = response.data.decode()
            assert "queryInput" in html
            assert "maxNodesInput" in html
            assert "minSimSlider" in html
            assert "includeKnnCheck" in html
            assert "includeEntityCheck" in html

    def test_cluster_route_contains_visualization_area(self):
        """Test that cluster page contains visualization area."""
        with app.test_client() as client:
            response = client.get("/cluster")
            html = response.data.decode()
            assert "clusterPlot" in html

    def test_cluster_route_contains_back_link(self):
        """Test that cluster page contains back to dashboard link."""
        with app.test_client() as client:
            response = client.get("/cluster")
            html = response.data.decode()
            assert "Back to Dashboard" in html
            assert 'href="/"' in html


if __name__ == "__main__":
    pytest.main([__file__])
