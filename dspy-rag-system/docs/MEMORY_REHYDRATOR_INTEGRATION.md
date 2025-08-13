# Memory Rehydrator Integration Guide

## 🎯 Overview

The Memory Rehydrator (`src/utils/memory_rehydrator.py`) provides role-aware, task-scoped context assembly from Postgres. It replaces static Markdown file loading with dynamic context bundles.

## 🚀 Quick Start

### Basic Usage

```python
from src.utils.memory_rehydrator import build_hydration_bundle

# Create a planner bundle
bundle = build_hydration_bundle(
    role="planner",
    task="Plan hybrid search rollout",
    limit=8,
    token_budget=1200
)

print(bundle.text)  # Formatted context
print(bundle.meta)  # Metadata and performance info
```

### CLI Usage

```bash
# Planner role
python3 -m src.utils.memory_rehydrator \
  --role planner \
  --task "Plan hybrid search rollout" \
  --limit 8 \
  --budget 1200

# Implementer role with JSON output
python3 -m src.utils.memory_rehydrator \
  --role implementer \
  --task "Refactor vector store search path" \
  --limit 8 \
  --budget 1200 \
  --json
```

## 🧠 Architecture

### Bundle Structure

1. **Pinned Anchors** (stable backbone)
   - TL;DR → quick-start → quick-links → commands
   - Role-specific pins (planner → system overview/backlog, implementer → DSPy context)

2. **Task-Scoped Retrieval** (hybrid search)
   - Uses optimized vector store for relevant content
   - Span-level grounding with citations

3. **Token Budgeting** (~1,200 tokens default)
   - Pins first, then anchor-like content, then general spans
   - Trims soft layers first to keep stable anchors intact

### Role Mapping

| Role | Pinned Files | Use Case |
|------|-------------|----------|
| `planner` | `400_guides/400_system-overview.md`, `000_core/000_backlog.md` | Strategic planning and prioritization |
| `implementer` | `100_memory/104_dspy-development-context.md` | Code implementation and technical work |
| `researcher` | (extensible) | Research and analysis tasks |

## ⚙️ Configuration

### Environment Variables

```bash
# Fusion method (zscore/rrf)
REHYDRATE_FUSION_METHOD=zscore

# Weights for hybrid search
REHYDRATE_W_DENSE=0.7
REHYDRATE_W_SPARSE=0.3

# Retrieval parameters
REHYDRATE_TOPK=8
REHYDRATE_TOKEN_BUDGET=1200

# Database connection
POSTGRES_DSN=postgresql://danieljacobs@localhost:5432/ai_agency
```

### Database Requirements

The memory rehydrator requires:

1. **Existing Tables**: `document_chunks`, `documents` (from vector store)
2. **Indexes**:
   - `idx_documents_file_path` (for role-based filtering)
   - `idx_dc_metadata_gin` (for JSONB anchor queries)
3. **Anchor Metadata**: JSONB metadata with `anchor_key` and `role_pins`

## 📊 Performance

### Quality Gates

- **Memory Rehydration**: < 5s (EXCELLENT), < 10s (GOOD)
- **Token Efficiency**: ≤ 1200 tokens for standard bundles
- **Bundle Sections**: 3-8 sections typical

### Current Performance

- **Bundle Creation**: ~3.6s first run, ~0.01-0.03s subsequent
- **Token Usage**: Efficient budgeting (213 tokens for 4 sections)
- **Vector Integration**: 5 dense results found, hybrid search operational

## 🔧 Integration Patterns

### DSPy Integration

```python
import dspy
from src.utils.memory_rehydrator import build_hydration_bundle

class ContextAwareAgent(dspy.Module):
    def __init__(self, role="planner"):
        super().__init__()
        self.role = role

    def forward(self, task):
        # Build context bundle
        bundle = build_hydration_bundle(
            role=self.role,
            task=task,
            limit=8,
            token_budget=1200
        )

        # Use bundle.text as context for LLM
        context = bundle.text
        # ... LLM processing with context
        return result
```

### Testing Integration

```python
# Test with basic functionality
python3 test_memory_rehydrator_basic.py

# Test with smoke tests (requires anchor metadata)
python3 test_memory_rehydrator_smoke.py
```

## 🎯 Use Cases

### 1. AI Agent Context Assembly

Replace static Markdown loading with dynamic context:

```python
# Before: Static file loading
with open("100_memory/100_cursor-memory-context.md") as f:
    context = f.read()

# After: Dynamic context assembly
bundle = build_hydration_bundle(role="planner", task="current task")
context = bundle.text
```

### 2. Role-Based Context Switching

Different roles get different context:

```python
# Planner gets system overview and backlog
planner_bundle = build_hydration_bundle(role="planner", task="planning task")

# Implementer gets DSPy development context
implementer_bundle = build_hydration_bundle(role="implementer", task="coding task")
```

### 3. Task-Scoped Retrieval

Context adapts to current task:

```python
# Same role, different tasks
bundle1 = build_hydration_bundle(role="implementer", task="vector store optimization")
bundle2 = build_hydration_bundle(role="implementer", task="database schema design")
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
bundle = build_hydration_bundle(role="planner", task="debug task")
print(f"Sections: {bundle.meta['sections']}")
print(f"Tokens: {bundle.meta['tokens_est']}")
print(f"Time: {bundle.meta['elapsed_s']}s")
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
- **Vector Store**: `src/dspy_modules/vector_store.py` (Hybrid search implementation)
- **Testing**: `test_memory_rehydrator_basic.py` (Basic functionality tests)
