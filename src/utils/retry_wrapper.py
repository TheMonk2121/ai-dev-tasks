from __future__ import annotations

import json
import random
import time
from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any

try:
    from requests.exceptions import Timeout
except Exception:  # requests may not be installed in some lanes

    class Timeout(Exception):  # type: ignore
        pass


# Domain-specific error types used by tests and callers
class RetryableError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class DataStoreError(Exception):
    pass


DEFAULT_POLICY = {
    "max_retries": 3,
    "backoff_factor": 2.0,
    "timeout_seconds": 30,
    "fatal_errors": [
        "AuthenticationError",
        "PermissionError",
        "ResourceBusyError",
        "KeyboardInterrupt",
    ],
}


def load_error_policy(path: str = "configs/system.json") -> dict:
    """
    Load retry/error policy from JSON file. Returns defaults on error.
    Tests patch builtins.open to simulate various cases.
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.loads(f.read())
        policy = data.get("error_policy", {})
        out = DEFAULT_POLICY.copy()
        out.update({k: v for k, v in policy.items() if k in out})
        return out
    except Exception:
        return DEFAULT_POLICY.copy()


def is_fatal_error(err: BaseException, fatal_names: Iterable[str]) -> bool:
    name = type(err).__name__
    for pat in fatal_names:
        if pat in name:
            return True
    # Built-in fatal classes
    if isinstance(err, AuthenticationError | DataStoreError):
        return True
    return False


def _sleep_with_jitter(base: float, jitter: bool) -> None:
    delay = base
    if jitter:
        delay += random.random()  # up to +1s random jitter
    time.sleep(delay)


def retry(
    *,
    max_retries: int | None = None,
    backoff_factor: float | None = None,
    fatal_errors: Iterable[str] | None = None,
    jitter: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Generic retry decorator with exponential backoff and optional jitter."""

    policy = load_error_policy()
    max_r = policy["max_retries"] if max_retries is None else max_retries
    factor = policy["backoff_factor"] if backoff_factor is None else backoff_factor
    fatal = list(policy["fatal_errors"]) if fatal_errors is None else list(fatal_errors)

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:  # noqa: BLE001 - intentional broad catch for retry wrapper
                    if is_fatal_error(e, fatal):
                        raise
                    if attempts >= max_r:
                        raise
                    # backoff: factor^attempts seconds (1,2,4,...)
                    base = (factor or 1.0) ** attempts
                    attempts += 1
                    _sleep_with_jitter(base, jitter)

        return wrapper

    return decorator


# Convenience retry presets used by code/tests
def retry_http(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def inner(*args: Any, **kwargs: Any) -> Any:
        @retry(max_retries=3, backoff_factor=1.5, fatal_errors=["AuthenticationError"])  # presets
        def _wrapped() -> Any:
            try:
                return fn(*args, **kwargs)
            except Timeout as e:  # map to retryable
                raise RetryableError(str(e))

        return _wrapped()

    return inner


def retry_database(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def inner(*args: Any, **kwargs: Any) -> Any:
        @retry(max_retries=3, backoff_factor=1.5, fatal_errors=["DataStoreError"])  # db preset
        def _wrapped() -> Any:
            return fn(*args, **kwargs)

        return _wrapped()

    return inner


def retry_llm(fn: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(fn)
    def inner(*args: Any, **kwargs: Any) -> Any:
        @retry(max_retries=2, backoff_factor=1.0, fatal_errors=["AuthenticationError"])  # llm preset
        def _wrapped() -> Any:
            return fn(*args, **kwargs)

        return _wrapped()

    return inner


def handle_retryable_errors(callable_fn: Callable[[], Any]) -> Any:
    """Wrap a callable and raise RetryableError for transient conditions (e.g., Timeout)."""
    try:
        return callable_fn()
    except Timeout as e:
        raise RetryableError(str(e))
