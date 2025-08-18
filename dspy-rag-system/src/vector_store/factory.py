#!/usr/bin/env python3
"""
Vector Store Factory

Factory for creating vector store instances based on mode or environment.
"""

import os
from typing import Optional

from .core import CoreVectorStore
from .perf import PerfVectorStore
from .protocols import IVectorStore


def get_vector_store(mode: Optional[str] = None, **kwargs) -> IVectorStore:
    """
    Get a vector store instance based on mode or environment.

    Args:
        mode: "core" | "perf" | "enhanced" | "production"
        **kwargs: Arguments passed to the vector store constructor

    Returns:
        IVectorStore: Vector store instance
    """
    mode = (mode or os.getenv("VECTOR_STORE_MODE", "core")).lower()

    if mode in ("perf", "enhanced", "production"):
        return PerfVectorStore(**kwargs)

    return CoreVectorStore(**kwargs)
