from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx


def create_client(timeout_seconds: float = 5.0) -> httpx.Client:
    """Create an httpx Client with an explicit timeout."""
    return httpx.Client(timeout=httpx.Timeout(timeout_seconds))


def get_with_backoff(
    client: httpx.Client,
    url: str,
    max_retries: int = 3,
    initial_backoff_seconds: float = 0.5,
) -> httpx.Response:
    """GET with exponential backoff and raise_for_status on success.

    Backoff sequence: 0.5s, 1.0s, 2.0s by default.
    """
    attempt = 0
    while True:
        try:
            response: Any = client.get(url)
            response.raise_for_status()
            return response
        except (httpx.HTTPError, httpx.TransportError):
            attempt += 1
            if attempt > max_retries:
                raise
            delay = initial_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(delay)
