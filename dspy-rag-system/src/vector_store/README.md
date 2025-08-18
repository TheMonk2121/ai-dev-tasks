<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->

# Vector Store README

> Canonical notice: This file is the primary source of truth for the vector store component. If any files under `dspy-rag-system/src/vector_store/` change, update this README and add an entry to `401_consensus-log.md`. For broader architecture changes, also update `400_guides/400_system-overview.md`; for public options/APIs, update `500_reference-cards.md`.

## Purpose

Document the design, configuration, and operational behavior of the vector store component (core/perf modes, index lifecycle, retrieval strategies), and serve as the single, component-scoped place to capture changes.

## Usage/Integration

- Import: `from vector_store import get_vector_store`
- Select mode: `get_vector_store(mode="core"|"perf")`
- See project overview for system wiring: [Project README](../../README.md)

## Owner

Documentation Team (Vector Store Maintainers)

## Last Reviewed

2025-08-18

---

## Quick Links

- System architecture: [System Overview](../../../400_guides/400_system-overview.md)
- Project overview: [Project README](../../README.md)
- Reference options: [Reference Cards](../../../500_reference-cards.md)
- Change log: [Consensus Log](../../../401_consensus-log.md)

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

Describe the purpose and scope of this document.

<!-- README_AUTOFIX_END -->
