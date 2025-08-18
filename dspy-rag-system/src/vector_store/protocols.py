#!/usr/bin/env python3.12.123.11
"""
Vector Store Protocols

Defines the unified interface for vector store implementations.
"""

from __future__ import annotations

from typing import Any, Protocol


class VectorStoreProtocol(Protocol):
    # Legacy + new names, both supported for compatibility
    def get_statistics(self) -> dict[str, Any]: ...
    def get_stats(self) -> dict[str, Any]: ...

    # Minimal surface used by our app/tests; passthrough allowed
    def store_document(self, *args: Any, **kwargs: Any) -> Any: ...
    def store_chunk(self, *args: Any, **kwargs: Any) -> Any: ...
    def get_documents(self, *args: Any, **kwargs: Any) -> Any: ...
