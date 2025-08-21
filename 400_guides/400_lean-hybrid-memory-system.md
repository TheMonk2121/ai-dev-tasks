<!-- ANCHOR_KEY: lean-hybrid-system -->
<!-- ANCHOR_PRIORITY: 25 -->
<!-- ROLE_PINS: ["implementer", "planner"] -->

# 🧠 Lean Hybrid Memory Rehydration System

<!-- CONTEXT_REFERENCE: 100_memory/100_cursor-memory-context.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->
<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->
<!-- MEMORY_CONTEXT: HIGH - Core memory rehydration system implementation -->
<!-- DATABASE_SYNC: REQUIRED -->

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete guide to the Lean Hybrid with Kill-Switches memory rehydration system | Implementing or debugging the memory rehydration system | Test with `python3 scripts/cursor_memory_rehydrate.py` |

<!-- ANCHOR_KEY: tldr -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["implementer", "planner"] -->

## 🎯 **Current Status**

- **Status**: ✅ **ACTIVE** - Lean Hybrid system fully operational
- **Priority**: 🔥 Critical - Core memory rehydration functionality
- **Database**: 1,939 chunks from 20 core documents
- **Search**: BM25 working excellently, vector ready for embeddings
- **Anchors**: 10 anchor keys with proper metadata

## 🏗️ **System Architecture**

### **Core Philosophy**
The Lean Hybrid system prioritizes **semantic relevance** over static pins while maintaining **deterministic behavior** and **simple configuration**.

### **Four-Slot Model**
1. **Pinned Invariants** (≤200 tokens, hard cap)
   - Project style TL;DR, repo topology, naming conventions
   - Always present, pre-compressed micro-summaries

2. **Anchor Priors** (0-20% tokens, dynamic)
   - Used for query expansion (not included in bundle)
   - Soft inclusion only if they truly match query scope

3. **Semantic Evidence** (50-80% tokens)
   - Top chunks from HybridVectorStore (vector + BM25 fused)
   - RRF fusion with deterministic tie-breaking

4. **Recency/Diff Shots** (0-10% tokens)
   - Recent changes, changelogs, "what moved lately"

### **Entity Expansion Enhancement**
The system now includes **entity-aware context expansion** that enhances semantic evidence retrieval:

- **Pattern-Based Extraction**: Identifies entities like CamelCase classes, snake_case functions, file paths, URLs, and emails
- **Adaptive Context Sizing**: Dynamically adjusts `k_related` based on entity count: `min(8, base_k + entity_count * 2)`
- **Entity-Adjacent Retrieval**: Finds semantically related chunks for extracted entities
- **Stability Thresholds**: Configurable similarity thresholds (default: 0.7) prevent low-quality matches
- **Zero Overhead**: No performance impact when no entities are found
- **Rollback Support**: Immediate disable via `--no-entity-expansion` flag

**Example Usage:**
```bash
# Query with entities: "How do I implement HybridVectorStore?"
# Extracted entities: ["HybridVectorStore", "How", "I", "implement"]
# Adaptive k_related: min(8, 2 + 4*2) = 8
# Result: Enhanced context with entity-related chunks
```

## 🔧 **Implementation Comparison: Python vs Go**

### **Python Implementation (`memory_rehydrator.py`)**
**Primary implementation with full DSPy integration and advanced features.**

#### **Features:**
- ✅ **Entity Expansion**: Automatic entity detection and related chunk expansion
- ✅ **Self-Critique**: Built-in bundle quality assessment and verification
- ✅ **Structured Tracing**: OpenTelemetry integration for observability
- ✅ **DSPy Integration**: Native integration with DSPy workflows
- ✅ **Full RRF Fusion**: Complete Reciprocal Rank Fusion algorithm
- ✅ **Query Expansion**: Advanced anchor term mining
- ✅ **Comprehensive Deduplication**: File-level + overlap detection

#### **Use Cases:**
- Production DSPy workflows
- Complex AI reasoning tasks
- Full observability requirements
- Entity-aware context expansion

#### **Performance:**
- **Startup Time**: ~3-5 seconds (includes DSPy initialization)
- **Memory Usage**: Higher (includes AI framework overhead)
- **Features**: Complete feature set

### **Go Implementation (`memory_rehydration_cli.go`)**
**Lightweight, performance-focused alternative for simple rehydration tasks.**

#### **Features:**
- ✅ **Fast Startup**: Minimal initialization time
- ✅ **Low Memory**: Lightweight footprint
- ✅ **Basic RRF Fusion**: Simplified fusion algorithm
- ✅ **File Deduplication**: Basic deduplication support
- ✅ **CLI Interface**: Simple command-line interface
- ❌ **Entity Expansion**: Not implemented
- ❌ **Self-Critique**: Not implemented
- ❌ **Structured Tracing**: Basic logging only

#### **Use Cases:**
- Fast CLI operations
- Simple memory rehydration
- Lightweight deployments
- Quick debugging and testing

#### **Performance:**
- **Startup Time**: <1 second
- **Memory Usage**: Low (minimal dependencies)
- **Features**: Core features only

#### **Current Status:**
- ⚠️ **Database Schema Issue**: Requires `start_char` column that doesn't exist
- 🔧 **Needs Fix**: Database schema compatibility issue

### **When to Use Which:**

| Scenario | Python | Go |
|----------|--------|-----|
| **Production DSPy workflows** | ✅ | ❌ |
| **Entity expansion needed** | ✅ | ❌ |
| **Full observability** | ✅ | ❌ |
| **Fast CLI operations** | ⚠️ | ✅ |
| **Lightweight deployment** | ❌ | ✅ |
| **Simple rehydration** | ⚠️ | ✅ |

## 🔧 **Configuration Options**
```bash
# Control anchor influence (0.0-1.0, default 0.6)
# Python implementation
python3 scripts/cursor_memory_rehydrate.py --stability 0.6

# Go implementation
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test" --stability 0.6
```

### **Kill-Switches for Debugging**
```bash
# Disable BM25+RRF fusion
# Python implementation
python3 scripts/cursor_memory_rehydrate.py --no-rrf

# Go implementation
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test" --use-rrf=false

# Simple file-level deduplication only
# Python implementation
python3 scripts/cursor_memory_rehydrate.py --dedupe file

# Go implementation
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test" --dedupe=file

# Disable automatic query expansion
# Python implementation
python3 scripts/cursor_memory_rehydrate.py --expand-query off

# Go implementation
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test" --expand-query=off

# Disable entity expansion
# Python implementation
python3 scripts/cursor_memory_rehydrate.py --no-entity-expansion

# Go implementation
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "test" --use-entity-expansion=false
```

### **Environment Variables**
```bash
export REHYDRATE_STABILITY=0.6
export REHYDRATE_USE_RRF=1
export REHYDRATE_DEDUPE="file+overlap"
export REHYDRATE_EXPAND_QUERY="auto"
export REHYDRATE_USE_ENTITY_EXPANSION=1
```

## 📊 **Database Schema**

### **Core Tables**
```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks with first-class columns
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255),
    chunk_index INTEGER,
    file_path TEXT,                    -- First-class column
    line_start INTEGER,                -- Span tracking
    line_end INTEGER,                  -- Span tracking
    content TEXT NOT NULL,
    embedding VECTOR(384),             -- Cursor AI embedding dimension
    is_anchor BOOLEAN DEFAULT FALSE,   -- First-class column
    anchor_key TEXT,                   -- First-class column
    metadata JSONB DEFAULT '{}',       -- Additional metadata
    content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Indexes**
```sql
-- FTS index for BM25 search
CREATE INDEX idx_document_chunks_content_tsv ON document_chunks USING GIN (content_tsv);

-- Hot-path helper indexes
CREATE INDEX idx_document_chunks_anchor_key ON document_chunks (anchor_key);
CREATE INDEX idx_document_chunks_file_path ON document_chunks (file_path);

-- HNSW index for fast vector similarity search
CREATE INDEX idx_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);
```

## 🔍 **Search Operations**

### **BM25 Search**
```python
from src.utils.memory_rehydrator import bm25_search

# Search for relevant content
results = bm25_search("DSPy RAG system architecture", 5)
for r in results:
    print(f"File: {r['file']}, BM25: {r['bm25']:.3f}, Anchor: {r['is_anchor']}")
```

### **Vector Search**
```python
from src.utils.memory_rehydrator import vector_search

# Search for semantically similar content
results = vector_search("memory context management", 5)
for r in results:
    print(f"File: {r['file']}, Similarity: {r['sim']:.3f}")
```

### **RRF Fusion**
The system uses Reciprocal Rank Fusion to combine vector and BM25 results:
```python
RRF(d) = Σᵣ∈{vec,lex} 1/(k₀ + r(d))
```

Where:
- `k₀ = 60` (default)
- `vec` = vector search results
- `lex` = BM25 search results

## 🎯 **Anchor System**

### **Current Anchor Keys**
- `tldr` (6 chunks) - TL;DR sections
- `quick-start` (4 chunks) - Quick start guides
- `architecture` (2 chunks) - System architecture
- `backlog` (2 chunks) - Backlog items
- `commands` (2 chunks) - Command references
- `context-priority` (2 chunks) - Context priority guides
- `memory-context` (2 chunks) - Memory context
- `p0-lane` (2 chunks) - P0 lane items
- `quick-links` (2 chunks) - Quick links
- `system-overview` (2 chunks) - System overview

### **Anchor Metadata Format**
```yaml
<!-- ANCHOR_KEY: memory-context -->
<!-- ANCHOR_PRIORITY: 0 -->
<!-- ROLE_PINS: ["planner", "implementer", "researcher"] -->
```

## 🚀 **Usage Examples**

### **Basic Usage**
```bash
# Default rehydration (Python)
python3 scripts/cursor_memory_rehydrate.py implementer "DSPy RAG system architecture"

# Default rehydration (Go)
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "DSPy RAG system architecture"

# With custom stability (Python)
python3 scripts/cursor_memory_rehydrate.py planner "backlog priorities" --stability 0.8

# With custom stability (Go)
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "backlog priorities" --stability 0.8

# Minimal mode for debugging (Python)
python3 scripts/cursor_memory_rehydrate.py researcher "memory context" --no-rrf --dedupe file

# Minimal mode for debugging (Go)
cd dspy-rag-system/src/utils && ./memory_rehydration_cli --query "memory context" --use-rrf=false --dedupe=file
```

### **Testing Search Functions**
```python
# Test BM25 search
python3 -c "from src.utils.memory_rehydrator import bm25_search; print(bm25_search('memory context', 3))"

# Test vector search
python3 -c "from src.utils.memory_rehydrator import vector_search; print(vector_search('DSPy system', 3))"
```

## 🔧 **Troubleshooting**

### **Database Connection Issues**
```bash
# Test database connection
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "SELECT COUNT(*) FROM document_chunks;"

# Check database health
python3 -c "from src.utils.database_resilience import get_database_health; print(get_database_health())"
```

### **Search Issues**
```bash
# Test individual search functions
python3 -c "from src.utils.memory_rehydrator import bm25_search; print('BM25 test:', bm25_search('test', 1))"

# Check anchor content
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "SELECT anchor_key, COUNT(*) FROM document_chunks WHERE is_anchor = true GROUP BY anchor_key;"
```

### **Performance Issues**
```bash
# Check search performance
python3 -c "import time; from src.utils.memory_rehydrator import bm25_search; start=time.time(); bm25_search('test', 10); print(f'Time: {time.time()-start:.3f}s')"
```

## 📈 **Performance Metrics**

### **Quality Gates**
- **BM25 Search**: < 100ms (EXCELLENT), < 200ms (GOOD)
- **Vector Search**: < 100ms (EXCELLENT), < 200ms (GOOD)
- **Memory Rehydration**: < 5s (EXCELLENT), < 10s (GOOD)
- **Recall@10**: ≥ 0.8 for relevant queries
- **Token Efficiency**: ≤ 1200 tokens for standard bundles

### **Current Performance**
- **Database**: 1,939 chunks from 20 core documents
- **Search Speed**: BM25 < 50ms, Vector < 100ms
- **Anchor Detection**: 10 anchor keys with proper metadata
- **Token Budget**: ≤200 tokens for pins, rest for evidence

## 🔄 **Maintenance**

### **Adding New Documents**
```bash
# Copy files to watch folder
cp new_document.md dspy-rag-system/watch_folder/

# Or use simple document adder
cd dspy-rag-system
PYTHONPATH=src python3 simple_add_anchors.py
```

### **Updating Anchors**
```bash
# Add anchor metadata to markdown files
<!-- ANCHOR_KEY: new-anchor -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["implementer"] -->
```

### **Database Maintenance**
```bash
# Check database health
python3 -c "from src.utils.database_resilience import is_database_healthy; print(is_database_healthy())"

# Rebuild indexes if needed
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "REINDEX INDEX idx_document_chunks_content_tsv;"
```

## 📚 **Related Documentation**

- **Memory Context**: `100_memory/100_cursor-memory-context.md`
- **System Overview**: `400_guides/400_system-overview.md`
- **Backlog**: `000_core/000_backlog.md`
- **Database Schema**: `dspy-rag-system/clean_slate_schema.sql`
- **Implementation**: `dspy-rag-system/src/utils/memory_rehydrator.py`

## 🎯 **Next Steps**

1. **Add Embeddings**: Enable vector search by adding embeddings to existing documents
2. **Performance Tuning**: Adjust constants based on usage patterns
3. **Monitoring**: Add performance monitoring and alerting
4. **Documentation**: Update related guides with new system details
