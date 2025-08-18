#!/usr/bin/env python3.12.123.11
"""
Vector Store Package

Unified interface for vector store implementations.
Provides CoreVectorStore (hybrid search) and PerfVectorStore (performance monitoring).
"""

from .core import CoreVectorStore
from .factory import get_vector_store
from .perf import PerfVectorStore
from .protocols import VectorStoreProtocol

__all__ = [
    "CoreVectorStore",
    "PerfVectorStore",
    "VectorStoreProtocol",
    "get_vector_store",
]
