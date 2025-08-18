#!/usr/bin/env python3
"""
Vector Store Package

Unified interface for vector store implementations.
Provides CoreVectorStore (hybrid search) and PerfVectorStore (performance monitoring).
"""

from .core import CoreVectorStore
from .factory import get_vector_store
from .perf import PerfVectorStore
from .protocols import IVectorStore

__all__ = ["get_vector_store", "CoreVectorStore", "PerfVectorStore", "IVectorStore"]
