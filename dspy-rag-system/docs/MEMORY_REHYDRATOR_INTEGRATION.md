# Memory Rehydrator Integration Guide

## 🎯 Overview

The Memory Rehydrator implements the **Lean Hybrid with Kill-Switches** approach for semantic-first memory rehydration. It provides role-aware, task-scoped context assembly from PostgreSQL with configurable complexity.

**Available Implementations:**
- **Python**: `src/utils/memory_rehydrator.py` (primary implementation)
- **Go**: `src/utils/memory_rehydration_cli.go` (alternative implementation)

### **Implementation Comparison**

| Feature | Python | Go |
|---------|--------|-----|
| **Entity Expansion** | ✅ Full implementation | ❌ Not implemented |
| **Self-Critique** | ✅ Built-in | ❌ Not implemented |
| **Structured Tracing** | ✅ OpenTelemetry | ❌ Basic logging |
| **DSPy Integration** | ✅ Native | ❌ Standalone |
| **RRF Fusion** | ✅ Complete algorithm | ✅ Basic implementation |
| **Query Expansion** | ✅ Advanced mining | ✅ Basic expansion |
| **Performance** | ~3-5s startup | <1s startup |
| **Memory Usage** | Higher (AI framework) | Low (minimal deps) |
| **Database Schema** | ✅ Compatible | ⚠️ Needs `start_char` column |

**Recommendation**: Use Python for production DSPy workflows, Go for fast CLI operations (after fixing schema issue).

## 🚀 Quick Start

### Basic Usage

#### Python Implementation
```python
from src.utils.memory_rehydrator import rehydrate

# Create a context bundle with Lean Hybrid approach
bundle = rehydrate(
    query="Plan hybrid search rollout",
    stability=0.6,  # Default stability slider
    max_tokens=6000,
    use_rrf=True,   # RRF fusion (vector + BM25)
    dedupe="file+overlap",
    expand_query="auto"
)

print(bundle.text)  # Formatted context
print(bundle.meta)  # Metadata and performance info
```

#### Go Implementation
```go
package main

import (
    "fmt"
    "log"
    "github.com/ai-dev-tasks/dspy-rag-system/src/utils"
)

func main() {
    config := &utils.Config{
        Stability:   0.6,
        MaxTokens:   6000,
        UseRRF:      true,
        Dedupe:      "file+overlap",
        ExpandQuery: "auto",
    }

    bundle, err := utils.Rehydrate("Plan hybrid search rollout", config)
    if err != nil {
        log.Fatal(err)
    }

    fmt.Println(bundle.Text)  // Formatted context
    fmt.Printf("%+v\n", bundle.Meta)  // Metadata and performance info
}
```

### CLI Usage

#### Python CLI
```bash
# Basic rehydration with Lean Hybrid defaults
python3 scripts/cursor_memory_rehydrate.py planner "Plan hybrid search rollout"

# With custom stability slider
python3 scripts/cursor_memory_rehydrate.py implementer "DSPy integration task" --stability 0.8

# Kill-switches for debugging
python3 scripts/cursor_memory_rehydrate.py researcher "memory context" --no-rrf --dedupe file
```

#### Go CLI
```bash
# Build the Go CLI
cd dspy-rag-system/src/utils
go build -o memory_rehydration_cli memory_rehydration_cli.go

# Basic rehydration with Lean Hybrid defaults
./memory_rehydration_cli --query "Plan hybrid search rollout"

# With custom stability slider
./memory_rehydration_cli --query "DSPy integration task" --stability 0.8

# Kill-switches for debugging
./memory_rehydration_cli --query "memory context" --use-rrf=false --dedupe=file --expand-query=off

# JSON output
./memory_rehydration_cli --query "test query" --json
```

## 🧠 Architecture

### Four-Slot Model

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

### Role Mapping

| Role | Pinned Files | Use Case |
|------|-------------|----------|
| `planner` | `400_guides/400_system-overview.md`, `000_core/000_backlog.md` | Strategic planning and prioritization |
| `implementer` | `100_memory/104_dspy-development-context.md` | Code implementation and technical work |
| `researcher` | (extensible) | Research and analysis tasks |

## ⚙️ Configuration

### Environment Variables

```bash
# Stability slider (0.0-1.0, default 0.6)
export REHYDRATE_STABILITY=0.6

# Kill-switches
export REHYDRATE_USE_RRF=1
export REHYDRATE_DEDUPE="file+overlap"
export REHYDRATE_EXPAND_QUERY="auto"

# Database connection
export POSTGRES_DSN=postgresql://danieljacobs@localhost:5432/ai_agency
```

### Configuration Options

#### **Stability Slider**
- **Range**: 0.0-1.0 (default 0.6)
- **Effect**: Controls anchor influence when semantic confidence is low
- **Usage**: `--stability 0.8` for more anchor inclusion, `--stability 0.2` for semantic-first

#### **Kill-Switches**
- **`--no-rrf`**: Disable BM25+RRF fusion (pure vector search)
- **`--dedupe file`**: Simple file-level deduplication only
- **`--expand-query off`**: Disable automatic query expansion

### Database Requirements

The memory rehydrator requires the clean slate schema with first-class columns:

1. **Core Tables**: `document_chunks`, `documents` (from clean slate schema)
2. **First-Class Columns**:
   - `file_path` (for hot-path filtering)
   - `is_anchor` (for fast anchor detection)
   - `anchor_key` (for anchor-specific queries)
   - `content_tsv` (for BM25 search)
3. **Indexes**:
   - `idx_document_chunks_content_tsv` (GIN for BM25)
   - `idx_document_chunks_anchor_key` (for anchor filtering)
   - `idx_document_chunks_embedding_hnsw` (HNSW for vector search)

## 📊 Performance

### Quality Gates

- **BM25 Search**: < 100ms (EXCELLENT), < 200ms (GOOD)
- **Vector Search**: < 100ms (EXCELLENT), < 200ms (GOOD)
- **Memory Rehydration**: < 5s (EXCELLENT), < 10s (GOOD)
- **Recall@10**: ≥ 0.8 for relevant queries
- **Token Efficiency**: ≤ 1200 tokens for standard bundles

### Current Performance

- **Database**: 1,939 chunks from 20 core documents
- **Search Speed**: BM25 < 50ms, Vector < 100ms
- **Anchor Detection**: 26 anchor chunks across 10 anchor keys
- **Token Budget**: ≤200 tokens for pins, rest for evidence

## 🔧 Integration Patterns

### DSPy Integration

```python
import dspy
from src.utils.memory_rehydrator import rehydrate

class ContextAwareAgent(dspy.Module):
    def __init__(self, role="planner"):
        super().__init__()
        self.role = role

    def forward(self, task):
        # Build context bundle with Lean Hybrid approach
        bundle = rehydrate(
            query=task,
            stability=0.6,
            max_tokens=6000,
            use_rrf=True,
            dedupe="file+overlap",
            expand_query="auto"
        )

        # Use bundle.text as context for LLM
        context = bundle.text
        # ... LLM processing with context
        return result
```

### Testing Integration

```python
# Test with basic functionality
python3 -c "from src.utils.memory_rehydrator import bm25_search; print(bm25_search('memory context', 3))"

# Test vector search
python3 -c "from src.utils.memory_rehydrator import vector_search; print(vector_search('DSPy system', 3))"

# Test full rehydration pipeline
python3 scripts/cursor_memory_rehydrate.py planner "test query"
```

## 🎯 Use Cases

### 1. AI Agent Context Assembly

Replace static Markdown loading with dynamic context:

```python
# Before: Static file loading
with open("100_memory/100_cursor-memory-context.md") as f:
    context = f.read()

# After: Dynamic context assembly with Lean Hybrid
bundle = rehydrate(query="current task", stability=0.6, max_tokens=6000)
context = bundle.text
```

### 2. Role-Based Context Switching

Different roles get different context:

```python
# Planner gets system overview and backlog
planner_bundle = rehydrate(query="planning task", stability=0.6, max_tokens=6000)

# Implementer gets DSPy development context
implementer_bundle = rehydrate(query="coding task", stability=0.6, max_tokens=6000)
```

### 3. Task-Scoped Retrieval

Context adapts to current task:

```python
# Same role, different tasks
bundle1 = rehydrate(query="vector store optimization", stability=0.6, max_tokens=6000)
bundle2 = rehydrate(query="database schema design", stability=0.6, max_tokens=6000)
```

## 🔍 Troubleshooting

### Common Issues

1. **No Anchor Metadata**: Bundle will still work but without pinned anchors
2. **Database Connection**: Check `POSTGRES_DSN` and database accessibility
3. **Import Errors**: Ensure `src/` is in Python path

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check bundle metadata
bundle = rehydrate(query="debug task", stability=0.6, max_tokens=6000)
print(f"Stability: {bundle.meta['stability']}")
print(f"Sim Top: {bundle.meta['sim_top']}")
print(f"Use RRF: {bundle.meta['use_rrf']}")
print(f"Evidence Tokens: {bundle.meta['evidence_tokens']}")
```

## 📈 Future Enhancements

### Planned Features

1. **Strict Anchors Mode**: Enforce anchor metadata requirements
2. **Dynamic Role Mapping**: Extensible role → file mappings
3. **Context Caching**: Cache bundles for repeated tasks
4. **Performance Monitoring**: Integration with OpenTelemetry

### Quality Improvements

1. **Recall@K Validation**: Measure retrieval quality
2. **Token Optimization**: Better token estimation
3. **Fusion Tuning**: Optimize hybrid search weights

## 🔗 Related Documentation

- **System Overview**: `400_guides/400_system-overview.md` (Memory Rehydrator section)
- **Memory Context**: `100_memory/100_cursor-memory-context.md` (Hydration Bundle Policy)
- **Lean Hybrid Guide**: `400_guides/400_lean-hybrid-memory-system.md` (Complete system guide)
- **Vector Store**: `src/dspy_modules/vector_store.py` (Hybrid search implementation)
- **Database Schema**: `clean_slate_schema.sql` (Clean slate schema with first-class columns)
- **Code Criticality**: `400_guides/400_code-criticality-guide.md` (Tier 1 critical files)
