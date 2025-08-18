# validator: allow-shadow-fork
#!/usr/bin/env python3
"""
Temporary shim for backward compatibility.
This file will be removed once all callers are updated to use the new vector_store package.
"""

from vector_store.perf import PerfVectorStore as EnhancedVectorStore

__all__ = ["EnhancedVectorStore"]
