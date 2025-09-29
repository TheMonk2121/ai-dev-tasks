"""
Test suite for HTTP migration utilities.

Tests the drop-in replacement functions for migrating from requests to httpx.
"""

#!/usr/bin/env python3

from unittest.mock import Mock, patch

import httpx
import pytest

from scripts.utilities.http_migration import (
    MIGRATION_MAP,
    HTTPMigrationError,
    create_httpx_client,
    get_migration_suggestions,
    get_with_backoff_httpx,
    migrate_requests_delete,
    migrate_requests_get,
    migrate_requests_head,
    migrate_requests_options,
    migrate_requests_patch,
    migrate_requests_post,
    migrate_requests_put,
)


class TestHTTPMigrationUtilities:
    """Test cases for HTTP migration utilities."""

    def test_migrate_requests_get_success(self):
        """Test successful GET request migration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            response = migrate_requests_get("http://example.com/api")

            assert response == mock_response
            mock_client.get.assert_called_once_with("http://example.com/api", params=None, headers=None)
            mock_response.raise_for_status.assert_called_once()

    def test_migrate_requests_get_with_params(self):
        """Test GET request with query parameters."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            params = {"key": "value", "page": 1}
            headers = {"Authorization": "Bearer token"}

            migrate_requests_get("http://example.com/api", params=params, headers=headers)

            mock_client.get.assert_called_once_with("http://example.com/api", params=params, headers=headers)

    def test_migrate_requests_post_success(self):
        """Test successful POST request migration."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            json_data = {"name": "test", "value": 123}
            response = migrate_requests_post("http://example.com/api", json=json_data)

            assert response == mock_response
            mock_client.post.assert_called_once_with("http://example.com/api", data=None, json=json_data, headers=None)
            mock_response.raise_for_status.assert_called_once()

    def test_migrate_requests_post_with_data(self):
        """Test POST request with form data."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            form_data = {"username": "test", "password": "secret"}
            migrate_requests_post("http://example.com/api", data=form_data)

            mock_client.post.assert_called_once_with("http://example.com/api", data=form_data, json=None, headers=None)

    def test_migrate_requests_put_success(self):
        """Test successful PUT request migration."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.put.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            json_data = {"id": 1, "name": "updated"}
            migrate_requests_put("http://example.com/api/1", json=json_data)

            mock_client.put.assert_called_once_with("http://example.com/api/1", data=None, json=json_data, headers=None)

    def test_migrate_requests_delete_success(self):
        """Test successful DELETE request migration."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.delete.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            migrate_requests_delete("http://example.com/api/1")

            mock_client.delete.assert_called_once_with("http://example.com/api/1", headers=None)

    def test_migrate_requests_patch_success(self):
        """Test successful PATCH request migration."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.patch.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            json_data = {"status": "updated"}
            migrate_requests_patch("http://example.com/api/1", json=json_data)

            mock_client.patch.assert_called_once_with(
                "http://example.com/api/1", data=None, json=json_data, headers=None
            )

    def test_migrate_requests_head_success(self):
        """Test successful HEAD request migration."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.head.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            migrate_requests_head("http://example.com/api")

            mock_client.head.assert_called_once_with("http://example.com/api", headers=None)

    def test_migrate_requests_options_success(self):
        """Test successful OPTIONS request migration."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.options.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            migrate_requests_options("http://example.com/api")

            mock_client.options.assert_called_once_with("http://example.com/api", headers=None)

    def test_http_error_handling(self):
        """Test HTTP error handling and custom exception."""
        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.side_effect = httpx.HTTPError("Connection failed")
            mock_get_client.return_value.__enter__.return_value = mock_client

            with pytest.raises(HTTPMigrationError) as exc_info:
                migrate_requests_get("http://example.com/api")

            assert "GET request failed for http://example.com/api" in str(exc_info.value)
            assert "Connection failed" in str(exc_info.value)

    def test_get_with_backoff_httpx_success(self):
        """Test GET request with backoff on success."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            response = get_with_backoff_httpx("http://example.com/api")

            assert response == mock_response
            mock_client.get.assert_called_once_with("http://example.com/api")

    def test_get_with_backoff_httpx_retry_success(self):
        """Test GET request with backoff retry on failure then success."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with (
            patch("scripts.utilities.http_migration._get_client") as mock_get_client,
            patch("time.sleep") as mock_sleep,
        ):
            mock_client = Mock()
            mock_client.get.side_effect = [
                httpx.HTTPError("First attempt failed"),
                httpx.HTTPError("Second attempt failed"),
                mock_response,
            ]
            mock_get_client.return_value.__enter__.return_value = mock_client

            response = get_with_backoff_httpx("http://example.com/api", max_retries=3)

            assert response == mock_response
            assert mock_client.get.call_count == 3
            assert mock_sleep.call_count == 2  # Two retries

    def test_get_with_backoff_httpx_max_retries_exceeded(self):
        """Test GET request with backoff when max retries exceeded."""
        with (
            patch("scripts.utilities.http_migration._get_client") as mock_get_client,
            patch("time.sleep") as mock_sleep,
        ):
            mock_client = Mock()
            mock_client.get.side_effect = httpx.HTTPError("All attempts failed")
            mock_get_client.return_value.__enter__.return_value = mock_client

            with pytest.raises(HTTPMigrationError) as exc_info:
                get_with_backoff_httpx("http://example.com/api", max_retries=2)

            assert "GET request failed after 2 retries" in str(exc_info.value)
            assert mock_client.get.call_count == 3  # Initial + 2 retries
            assert mock_sleep.call_count == 2  # Two retries

    def test_create_httpx_client(self):
        """Test httpx client creation with proper configuration."""
        client = create_httpx_client(timeout_seconds=10.0)

        assert isinstance(client, httpx.Client)
        assert client.timeout.connect == 10.0
        assert client.timeout.read == 10.0
        assert client.timeout.write == 10.0
        assert client.timeout.pool == 10.0

        # Clean up
        client.close()

    def test_migration_map_completeness(self):
        """Test that migration map covers all common requests methods."""
        expected_methods = [
            "requests.get",
            "requests.post",
            "requests.put",
            "requests.delete",
            "requests.patch",
            "requests.head",
            "requests.options",
        ]

        for method in expected_methods:
            assert method in MIGRATION_MAP
            assert MIGRATION_MAP[method].startswith("migrate_requests_")

    def test_get_migration_suggestions(self):
        """Test migration suggestion analysis."""
        file_content = """
import requests

def make_request():
    response = result
    data = requests.post("http://example.com/api", json={"key": "value"})
    return response, data
"""

        suggestions = get_migration_suggestions(file_content)

        assert len(suggestions) == 2
        assert any("requests.get" in suggestion for suggestion in suggestions.keys())
        assert any("requests.post" in suggestion for suggestion in suggestions.keys())
        assert all("migrate_requests_" in suggestion for suggestion in suggestions.values())

    def test_timeout_configuration(self):
        """Test that timeout is properly configured in all methods."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            migrate_requests_get("http://example.com/api", timeout=15.0)

            # Verify timeout was passed to _get_client
            mock_get_client.assert_called_once()
            call_kwargs = mock_get_client.call_args
            assert "timeout" in call_kwargs.kwargs

    def test_headers_passthrough(self):
        """Test that headers are properly passed through all methods."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}

        with patch("scripts.utilities.http_migration._get_client") as mock_get_client:
            mock_client = Mock()
            mock_client.get.return_value = mock_response
            mock_get_client.return_value.__enter__.return_value = mock_client

            migrate_requests_get("http://example.com/api", headers=headers)

            mock_client.get.assert_called_once_with("http://example.com/api", params=None, headers=headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
