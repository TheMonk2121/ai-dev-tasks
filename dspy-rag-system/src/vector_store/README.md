# Vector Store Package

This package provides a unified interface for vector store implementations with two complementary tiers.

## Architecture

### CoreVectorStore (core.py)
- **Purpose**: Stable baseline with hybrid search capabilities
- **Implementation**: Wraps HybridVectorStore
- **Use Case**: General applications, development, testing
- **Features**: Dense + sparse fusion, span-based search, stable API

### PerfVectorStore (perf.py)
- **Purpose**: Performance-focused with monitoring and caching
- **Implementation**: Wraps EnhancedVectorStore
- **Use Case**: Production monitoring, performance-critical applications
- **Features**: Performance monitoring, caching, health checks, index management

## Usage

### Factory Pattern (Recommended)
```python
from vector_store import get_vector_store

# Explicit mode selection
vs = get_vector_store(mode="perf", db_connection_string=dsn)

# Environment-driven (VECTOR_STORE_MODE=perf)
vs = get_vector_store(db_connection_string=dsn)
```

### Direct Class Usage
```python
from vector_store import CoreVectorStore, PerfVectorStore

# Core implementation
core_vs = CoreVectorStore(db_connection_string)

# Performance implementation
perf_vs = PerfVectorStore(db_connection_string, dimension=384)
```

## Protocol Interface

Both implementations satisfy the `IVectorStore` protocol:

```python
from vector_store import IVectorStore

def process_documents(vs: IVectorStore):
    # Add documents
    vs.add_documents(documents)

    # Search
    results = vs.similarity_search(query_embedding, top_k=5)

    # Health check
    status = vs.get_health_status()

    # Statistics
    stats = vs.get_stats()
```

## Migration

### From EnhancedVectorStore
```python
# Old
from dspy_modules.enhanced_vector_store import EnhancedVectorStore
vs = EnhancedVectorStore(dsn)

# New
from vector_store import get_vector_store
vs = get_vector_store(mode="perf", db_connection_string=dsn)
```

### From HybridVectorStore
```python
# Old
from dspy_modules.vector_store import HybridVectorStore
vs = HybridVectorStore(dsn)

# New
from vector_store import get_vector_store
vs = get_vector_store(mode="core", db_connection_string=dsn)
```

## Governance

- **Shadow Fork Prevention**: No more `_enhanced.py` or `_optimized.py` variants
- **Documentation Required**: All changes must update docs (see PR template)
- **Validator Enforcement**: WARN → FAIL after migration complete

## Files

- `__init__.py` - Package exports
- `protocols.py` - IVectorStore interface definition
- `core.py` - CoreVectorStore implementation
- `perf.py` - PerfVectorStore implementation
- `factory.py` - get_vector_store factory function
- `README.md` - This file

<!-- README_AUTOFIX_START -->
# Auto-generated sections for README.md
# Generated: 2025-08-17T21:49:49.336678

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

RAG Subsystem Maintainers

## Purpose

[Describe the purpose and scope of this document]

<!-- README_AUTOFIX_END -->
