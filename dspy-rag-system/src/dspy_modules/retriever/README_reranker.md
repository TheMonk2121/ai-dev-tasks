# PyTorch Reranker Integration

This directory contains the PyTorch-based reranker implementation for the DSPy RAG system.

## Overview

The reranker implements a minimal, surgical approach to cross-encoder reranking:

- **Inference-only**: Uses pre-trained models, no training required
- **Cached scores**: SQLite-based caching for deterministic, fast results
- **Configurable**: Environment variables and YAML config support
- **Fallback**: Graceful fallback to legacy reranker if PyTorch unavailable

## Files

- `reranker_torch.py` - Main PyTorch reranker implementation
- `reranker_config.py` - Configuration loader and environment management
- `README_reranker.md` - This documentation

## Quick Start

### 1. Install Dependencies

```bash
pip install torch sentence-transformers
```

### 2. Enable Reranker

```bash
# Source the configuration
source configs/reranker_toggle.env

# Or set environment variables manually
export RERANKER_ENABLED=true
export RERANKER_MODEL="cross-encoder/ms-marco-MiniLM-L-6-v2"
export RERANK_INPUT_TOPK=50
export RERANK_KEEP=12
export RERANK_BATCH=8
export TORCH_DEVICE="auto"
```

### 3. Test Integration

```bash
python3 scripts/test_reranker_integration.py
```

### 4. Run Evaluation Comparison

```bash
python3 scripts/eval_reranker_comparison.py --output-dir metrics/reranker_comparison
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RERANKER_ENABLED` | `false` | Enable/disable reranker |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Model name |
| `RERANK_INPUT_TOPK` | `50` | Candidates to send to reranker |
| `RERANK_KEEP` | `12` | Final results after reranking |
| `RERANK_BATCH` | `8` | Batch size for inference |
| `TORCH_DEVICE` | `auto` | Device (auto, cpu, mps, cuda) |
| `RERANKER_CACHE_DIR` | `cache` | Cache directory |

### YAML Configuration

Add to `configs/retriever_weights.yaml`:

```yaml
default:
  reranker:
    enabled: true
    model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
    input_topk: 50
    keep: 12
    batch_size: 8
    device: "auto"
    cache_enabled: true
```

## Architecture

### Pipeline Integration

The reranker integrates into the existing retrieval pipeline:

1. **Prefilter**: SQL-based BM25 + vector + metadata fusion
2. **Rerank**: Cross-encoder reranking of top candidates
3. **Final**: Return top-k results to reader

### Caching System

- **SQLite cache**: Stores scores by (model, query_hash, chunk_id)
- **Deterministic**: Same query + model = same scores
- **Fast**: Avoids recomputation for repeated queries

### Device Support

- **Auto**: Automatically selects best available device
- **MPS**: Apple Silicon GPU acceleration
- **CUDA**: NVIDIA GPU acceleration
- **CPU**: Fallback for all systems

## Performance

### Expected Improvements

- **F1 Score**: +0.05 to +0.15 improvement
- **Precision**: Better relevance ranking
- **Recall**: Maintained through prefiltering

### Latency

- **First run**: ~2-5 seconds (model loading)
- **Cached**: ~100-500ms (cache lookup)
- **Batch processing**: Optimized for throughput

## Troubleshooting

### Common Issues

1. **Import errors**: Install `torch` and `sentence-transformers`
2. **MPS issues**: Set `TORCH_DEVICE=cpu` on Apple Silicon
3. **Memory issues**: Reduce `RERANK_BATCH` size
4. **Cache issues**: Clear `cache/` directory

### Debug Mode

```bash
export RERANKER_DEBUG=1
python3 scripts/test_reranker_integration.py
```

## Evaluation

### Comparison Script

```bash
# Compare with/without reranker
python3 scripts/eval_reranker_comparison.py

# Check results
ls metrics/reranker_comparison/
```

### Integration Test

```bash
# Test all components
python3 scripts/test_reranker_integration.py
```

## Future Enhancements

### Path B: Training (Future)

When ready for training:

1. **Mine hard negatives** from gold cases
2. **Export triplets** (query, positive, negative)
3. **Train domain-specific** reranker
4. **Add CI gates** for model validation

### Advanced Features

- **Multi-model ensemble**: Combine multiple rerankers
- **Query-specific routing**: Different models for different query types
- **Dynamic batching**: Adaptive batch sizes based on query complexity
