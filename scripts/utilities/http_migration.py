#!/usr/bin/env python3
"""
HTTP Migration Utilities - Drop-in replacements for requests using httpx

This module provides migration utilities to help transition from requests to httpx
while maintaining API compatibility and following project standards.

Usage:
    from scripts.utilities.http_migration import migrate_requests_get, migrate_requests_post

    # Drop-in replacement for requests.get
    response = migrate_requests_get("http://example.com/api", timeout=5.0)

    # Drop-in replacement for requests.post
    response = migrate_requests_post("http://example.com/api", json={"key": "value"})
"""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import httpx

try:  # Local import with graceful fallback for test environments
    from src.config.settings import get_settings  # type: ignore
except Exception:  # pragma: no cover - fallback when settings stack isn't available

    class _Perf:
        http_total_timeout: float = 5.0

    class _Settings:
        performance = _Perf()

    def get_settings() -> _Settings:  # type: ignore
        return _Settings()


class HTTPMigrationError(Exception):
    """Custom exception for HTTP migration errors."""

    pass


@contextmanager
def _get_client(timeout: float | None = None, **kwargs: Any) -> Generator[httpx.Client, None, None]:
    """Context manager for httpx client with proper resource cleanup."""
    if timeout is None:
        settings = get_settings()
        timeout = settings.performance.http_total_timeout

    client = httpx.Client(timeout=httpx.Timeout(timeout), **kwargs)
    try:
        yield client
    finally:
        client.close()


def migrate_requests_get(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 5.0,
    **kwargs: Any,
) -> httpx.Response:
    """
    Drop-in replacement for requests.get using httpx.

    Args:
        url: URL to make GET request to
        params: Query parameters
        headers: HTTP headers
        timeout: Request timeout in seconds
        **kwargs: Additional httpx client arguments

    Returns:
        httpx.Response object with raise_for_status() applied

    Raises:
        HTTPMigrationError: If request fails after retries
    """
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"GET request failed for {url}: {e}") from e


def migrate_requests_post(
    url: str,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 5.0,
    **kwargs: Any,
) -> httpx.Response:
    """
    Drop-in replacement for requests.post using httpx.

    Args:
        url: URL to make POST request to
        data: Form data or raw data
        json: JSON data to send
        headers: HTTP headers
        timeout: Request timeout in seconds
        **kwargs: Additional httpx client arguments

    Returns:
        httpx.Response object with raise_for_status() applied

    Raises:
        HTTPMigrationError: If request fails after retries
    """
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.post(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"POST request failed for {url}: {e}") from e


def migrate_requests_put(
    url: str,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 5.0,
    **kwargs: Any,
) -> httpx.Response:
    """Drop-in replacement for requests.put using httpx."""
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.put(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"PUT request failed for {url}: {e}") from e


def migrate_requests_delete(
    url: str, headers: dict[str, str] | None = None, timeout: float = 5.0, **kwargs: Any
) -> httpx.Response:
    """Drop-in replacement for requests.delete using httpx."""
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.delete(url, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"DELETE request failed for {url}: {e}") from e


def migrate_requests_patch(
    url: str,
    data: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 5.0,
    **kwargs: Any,
) -> httpx.Response:
    """Drop-in replacement for requests.patch using httpx."""
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.patch(url, data=data, json=json, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"PATCH request failed for {url}: {e}") from e


def migrate_requests_head(
    url: str, headers: dict[str, str] | None = None, timeout: float = 5.0, **kwargs: Any
) -> httpx.Response:
    """Drop-in replacement for requests.head using httpx."""
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.head(url, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"HEAD request failed for {url}: {e}") from e


def migrate_requests_options(
    url: str, headers: dict[str, str] | None = None, timeout: float = 5.0, **kwargs: Any
) -> httpx.Response:
    """Drop-in replacement for requests.options using httpx."""
    try:
        with _get_client(timeout=timeout, **kwargs) as client:
            response = client.options(url, headers=headers)
            response.raise_for_status()
            return response
    except httpx.HTTPError as e:
        raise HTTPMigrationError(f"OPTIONS request failed for {url}: {e}") from e


def get_with_backoff_httpx(
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
    timeout: float = 5.0,
    **kwargs: Any,
) -> httpx.Response:
    """
    GET request with exponential backoff using httpx.

    Backoff sequence: 0.5s, 1.0s, 2.0s by default.

    Args:
        url: URL to make GET request to
        max_retries: Maximum number of retry attempts
        initial_backoff_seconds: Initial backoff delay
        timeout: Request timeout in seconds
        **kwargs: Additional httpx client arguments

    Returns:
        httpx.Response object

    Raises:
        HTTPMigrationError: If all retry attempts fail
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            with _get_client(timeout=timeout, **kwargs) as client:
                response = client.get(url, **kwargs)
                response.raise_for_status()
                return response
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

    raise HTTPMigrationError(f"GET request failed after {max_retries} retries for {url}: {last_error}") from last_error


def create_httpx_client(timeout_seconds: float = 5.0, **kwargs: Any) -> httpx.Client:
    """
    Create an httpx Client with explicit timeout and proper configuration.

    Args:
        timeout_seconds: Request timeout in seconds
        **kwargs: Additional httpx client arguments

    Returns:
        Configured httpx.Client instance
    """
    return httpx.Client(timeout=httpx.Timeout(timeout_seconds), **kwargs)


# Convenience aliases for common patterns
migrate_get = migrate_requests_get
migrate_post = migrate_requests_post
migrate_put = migrate_requests_put
migrate_delete = migrate_requests_delete

# Map of requests usages to migration function names for static analysis and guidance
MIGRATION_MAP: dict[str, str] = {
    "requests.get": "migrate_requests_get",
    "requests.post": "migrate_requests_post",
    "requests.put": "migrate_requests_put",
    "requests.delete": "migrate_requests_delete",
    "requests.patch": "migrate_requests_patch",
    "requests.head": "migrate_requests_head",
    "requests.options": "migrate_requests_options",
}


def get_migration_suggestions(file_content: str) -> dict[str, str]:
    """
    Analyze Python source content for requests usages and suggest httpx-based replacements.

    Returns a mapping of the found requests method (e.g., "requests.get") to the
    corresponding migration helper function name (e.g., "migrate_requests_get").
    """
    import re

    methods_pattern = re.compile(r"\brequests\.(get|post|put|delete|patch|head|options)\b")
    found: set[str] = set()

    for match in methods_pattern.finditer(file_content):
        method = match.group(1)
        found.add(f"requests.{method}")

    return {method: MIGRATION_MAP[method] for method in sorted(found) if method in MIGRATION_MAP}
