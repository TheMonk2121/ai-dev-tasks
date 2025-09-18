from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any

import httpx

from src.config.settings import get_settings


class HTTPClientError(Exception):
    """Custom exception for HTTP client errors."""

    pass


def create_client(timeout_seconds: float | None = None, **kwargs: Any) -> httpx.Client:
    """
    Create an httpx Client with an explicit timeout and proper configuration.

    Args:
        timeout_seconds: Request timeout in seconds (uses settings if None)
        **kwargs: Additional httpx client arguments

    Returns:
        Configured httpx.Client instance
    """
    if timeout_seconds is None:
        settings = get_settings()
        timeout_seconds = settings.performance.http_total_timeout

    return httpx.Client(timeout=httpx.Timeout(timeout_seconds), **kwargs)


@contextmanager
def create_client_context(timeout_seconds: float | None = None, **kwargs: Any):
    """
    Context manager for httpx client with proper resource cleanup.

    Args:
        timeout_seconds: Request timeout in seconds (uses settings if None)
        **kwargs: Additional httpx client arguments

    Yields:
        httpx.Client instance
    """
    client = create_client(timeout_seconds, **kwargs)
    try:
        yield client
    finally:
        client.close()


def get_with_backoff(
    client: httpx.Client,
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> httpx.Response:
    """
    GET with exponential backoff and raise_for_status on success.

    Backoff sequence: 0.5s, 1.0s, 2.0s by default.

    Args:
        client: httpx.Client instance
        url: URL to make GET request to
        max_retries: Maximum number of retry attempts
        initial_backoff_seconds: Initial backoff delay
        **kwargs: Additional httpx request arguments

    Returns:
        httpx.Response object

    Raises:
        HTTPClientError: If all retry attempts fail
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            response: Any = client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

    raise HTTPClientError(f"GET request failed after {max_retries} retries for {url}: {last_error}") from last_error


def post_with_backoff(
    client: httpx.Client,
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> httpx.Response:
    """
    POST with exponential backoff and raise_for_status on success.

    Args:
        client: httpx.Client instance
        url: URL to make POST request to
        max_retries: Maximum number of retry attempts
        initial_backoff_seconds: Initial backoff delay
        **kwargs: Additional httpx request arguments

    Returns:
        httpx.Response object

    Raises:
        HTTPClientError: If all retry attempts fail
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            response: Any = client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

    raise HTTPClientError(f"POST request failed after {max_retries} retries for {url}: {last_error}") from last_error


def put_with_backoff(
    client: httpx.Client,
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> httpx.Response:
    """
    PUT with exponential backoff and raise_for_status on success.

    Args:
        client: httpx.Client instance
        url: URL to make PUT request to
        max_retries: Maximum number of retry attempts
        initial_backoff_seconds: Initial backoff delay
        **kwargs: Additional httpx request arguments

    Returns:
        httpx.Response object

    Raises:
        HTTPClientError: If all retry attempts fail
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            response: Any = client.put(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

    raise HTTPClientError(f"PUT request failed after {max_retries} retries for {url}: {last_error}") from last_error


def delete_with_backoff(
    client: httpx.Client,
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
    **kwargs: Any,
) -> httpx.Response:
    """
    DELETE with exponential backoff and raise_for_status on success.

    Args:
        client: httpx.Client instance
        url: URL to make DELETE request to
        max_retries: Maximum number of retry attempts
        initial_backoff_seconds: Initial backoff delay
        **kwargs: Additional httpx request arguments

    Returns:
        httpx.Response object

    Raises:
        HTTPClientError: If all retry attempts fail
    """
    attempt = 0
    last_error = None

    while attempt <= max_retries:
        try:
            response: Any = client.delete(url, **kwargs)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TransportError) as e:
            last_error = e
            attempt += 1
            if attempt > max_retries:
                break
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)

    raise HTTPClientError(f"DELETE request failed after {max_retries} retries for {url}: {last_error}") from last_error


def health_check(url: str, timeout_seconds: float = 5.0, expected_status: int = 200, **kwargs: Any) -> bool:
    """
    Perform a health check on a URL.

    Args:
        url: URL to check
        timeout_seconds: Request timeout in seconds
        expected_status: Expected HTTP status code
        **kwargs: Additional httpx client arguments

    Returns:
        True if health check passes, False otherwise
    """
    try:
        with create_client_context(timeout_seconds, **kwargs) as client:
            response: Any = client.get(url)
            return response.status_code == expected_status
    except Exception:
        return False


def safe_request(
    method: str,
    url: str,
    timeout_seconds: float = 5.0,
    max_retries: int = 3,
    **kwargs: Any,
) -> httpx.Response | None:
    """
    Make a safe HTTP request with error handling.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: URL to make request to
        timeout_seconds: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        **kwargs: Additional httpx request arguments

    Returns:
        httpx.Response object if successful, None if failed
    """
    try:
        with create_client_context(timeout_seconds) as client:
            method_func = getattr(client, method.lower())

            attempt = 0
            while attempt <= max_retries:
                try:
                    response = method_func(url, **kwargs)
                    response.raise_for_status()
                    return response
                except (httpx.HTTPError, httpx.TransportError):
                    attempt += 1
                    if attempt > max_retries:
                        break
                    time.sleep(0.5 * (2 ** (attempt - 1)))

            return None
    except Exception:
        return None


# Convenience functions for common patterns
def get_safe(url: str, timeout_seconds: float = 5.0, **kwargs: Any) -> httpx.Response | None:
    """Safe GET request that returns None on failure."""
    return safe_request("GET", url, timeout_seconds, **kwargs)


def post_safe(url: str, timeout_seconds: float = 5.0, **kwargs: Any) -> httpx.Response | None:
    """Safe POST request that returns None on failure."""
    return safe_request("POST", url, timeout_seconds, **kwargs)


def put_safe(url: str, timeout_seconds: float = 5.0, **kwargs: Any) -> httpx.Response | None:
    """Safe PUT request that returns None on failure."""
    return safe_request("PUT", url, timeout_seconds, **kwargs)


def delete_safe(url: str, timeout_seconds: float = 5.0, **kwargs: Any) -> httpx.Response | None:
    """Safe DELETE request that returns None on failure."""
    return safe_request("DELETE", url, timeout_seconds, **kwargs)


# Settings-aware helper functions
def create_health_check_client() -> httpx.Client:
    """Create httpx client configured for health checks using settings."""
    settings = get_settings()
    return httpx.Client(timeout=httpx.Timeout(settings.performance.health_check_timeout))


def create_metrics_client() -> httpx.Client:
    """Create httpx client configured for metrics collection using settings."""
    settings = get_settings()
    return httpx.Client(timeout=httpx.Timeout(settings.performance.metrics_timeout))


def create_async_client(timeout_seconds: float | None = None, **kwargs: Any) -> httpx.AsyncClient:
    """
    Create an httpx AsyncClient with settings-aware timeout configuration.

    Args:
        timeout_seconds: Request timeout in seconds (uses settings if None)
        **kwargs: Additional httpx client arguments

    Returns:
        Configured httpx.AsyncClient instance
    """
    if timeout_seconds is None:
        settings = get_settings()
        timeout_seconds = settings.performance.http_total_timeout

    return httpx.AsyncClient(timeout=httpx.Timeout(timeout_seconds), **kwargs)
