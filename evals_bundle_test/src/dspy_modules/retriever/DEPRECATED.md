# DEPRECATED: Legacy DSPy Retrieval System

⚠️ **WARNING: This retrieval system is deprecated and will be removed in a future version.**

## Migration Notice

The DSPy retrieval system in this directory has been superseded by the advanced retrieval system in `src/retrieval/`. 

### What's Deprecated

- `pg.py` - Legacy PostgreSQL retrieval with basic fusion
- `rerank.py` - Simple MMR reranking only
- `weights.py` - Basic weight loading
- `limits.py` - Simple limit configuration

### What to Use Instead

Use the new advanced retrieval system:

```python
# OLD (deprecated)
from dspy_modules.retriever.pg import run_fused_query

# NEW (recommended)
from src.retrieval.advanced_retriever import run_fused_query
```

### New Features Available

- **Advanced Fusion**: Weighted RRF with configurable profiles
- **Prefiltering**: Recall-friendly quality gates and diversity filtering
- **Sophisticated Reranking**: Heuristic + cross-encoder reranking
- **Quality Gates**: Configurable evaluation thresholds
- **Intent Routing**: Query-aware parameter adjustment
- **Production Monitoring**: Health checks and performance metrics

### Migration Timeline

- **Phase 1** (Current): Legacy system still works, new system available
- **Phase 2** (Next release): Legacy system marked as deprecated
- **Phase 3** (Future): Legacy system removed

### Configuration

The new system uses YAML configuration:

```yaml
# config/retrieval.yaml
candidates:
  bm25_limit: 100
  vector_limit: 100
  final_limit: 50

fusion:
  k: 60
  lambda_lex: 0.6
  lambda_sem: 0.4

prefilter:
  min_bm25_score: 0.1
  min_vector_score: 0.7
  enable_diversity: true

rerank:
  enabled: true
  alpha: 0.7
  top_m: 25
```

### Questions?

See `src/retrieval/README.md` for complete documentation of the new system.
