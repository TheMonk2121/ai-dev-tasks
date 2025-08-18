from __future__ import annotations

from typing import Any


class _DelegatingStore:
    """Base that forwards unknown attributes to the wrapped implementation."""

    def __init__(self, inner: Any):
        self._inner = inner

    def __getattr__(self, name: str) -> Any:  # pragma: no cover
        # Only called if attribute not found on self.
        return getattr(self._inner, name)

    # ---- Compatibility helpers ----

    def _call(self, primary: str, fallback: str, *args: Any, **kwargs: Any) -> Any:
        if hasattr(self._inner, primary):
            return getattr(self._inner, primary)(*args, **kwargs)
        if hasattr(self._inner, fallback):
            return getattr(self._inner, fallback)(*args, **kwargs)
        raise AttributeError(
            f"{self.__class__.__name__} expected inner to expose "
            f"'{primary}' or '{fallback}', but it had neither."
        )
