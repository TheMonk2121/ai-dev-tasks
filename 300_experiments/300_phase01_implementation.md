# Phase 0/1 RAG Enhancement Implementation

## 🚀 Overview

This implementation adds surgical Phase 0 (Eval, Telemetry, Canary) and Phase 1 (Reranker + Recall/Windowing) enhancements to the RAG system based on your detailed mapping. All changes are feature-flagged and can be canary-deployed safely.

## ✅ Completed Features

### Phase 0: Evaluation, Telemetry & Canary

- **✅ Golden Evaluation Slices**
  - `configs/eval/golden/novice_expert_queries.jsonl` - Novice vs Expert queries
  - `configs/eval/golden/hop_complexity_queries.jsonl` - Single vs Multi-hop queries
  - Structured evaluation with slice tags, sub-claims, and expected spans

- **✅ Per-Request Telemetry Logging**
  - `src/telemetry/request_logger.py` - Async structured logging
  - Full pipeline logging: query → candidates → rerank scores → answer → confidence
  - Canary tagging for A/B testing with deterministic sampling
  - JSONL output to `metrics/logs/requests.jsonl`

- **✅ Enhanced Evaluation Metrics**
  - `src/evaluation/enhanced_metrics.py` - Complete metrics suite
  - **nDCG@10**: Normalized Discounted Cumulative Gain for ranking quality
  - **Coverage**: Fraction of sub-claims with supporting evidence ≥ threshold
  - **Exact Match / Span Support**: Extractive query evaluation
  - **F1 Score**: Token-level precision/recall with partial matches
  - **ECE**: Expected Calibration Error with temperature scaling
  - **Temperature Scaling**: Confidence calibration via Platt/Isotonic regression

### Phase 1: Windowing, Deduplication & Cross-Encoder

- **✅ Document Windowing**
  - `src/retrieval/windowing.py` - Smart window creation (120-180 tokens, 33% overlap)
  - Paragraph boundary preservation, citation traceability
  - Token-aware chunking with tiktoken integration

- **✅ Near-Duplicate Suppression**
  - `src/retrieval/deduplication.py` - Multi-method deduplication
  - Cosine similarity (TF-IDF), MinHash (robust), Simple hash (fallback)
  - Applied before cross-encoder to save compute budget

- **✅ Cross-Encoder Client**
  - `src/retrieval/cross_encoder_client.py` - ONNX-optimized reranking
  - Micro-batching (32 pairs), 400ms timeout with BM25 fallback
  - Circuit breaker pattern, async support with worker pools
  - ONNX-INT8 quantization support for CPU efficiency

- **✅ Concurrency & Resilience**
  - Singleflight caching (30s TTL) to deduplicate identical queries
  - Worker bounds (3 max), graceful degradation patterns
  - Timeout handling with fallback to heuristic reranking

## 🔧 Configuration

All features are controlled via `config/retrieval.yaml`:

```yaml
# Phase 0: Evaluation & Telemetry
evaluation:
  golden_sets:
    base_path: "configs/eval/golden/"
    slices: [novice_expert_queries.jsonl, hop_complexity_queries.jsonl]
  metrics:
    enabled: ["ndcg_10", "coverage", "exact_match", "span_support", "f1", "ece"]
    temperature_scaling: true

telemetry:
  enabled: true
  per_request_logging: true
  log_path: "metrics/logs/requests.jsonl"

canary:
  enabled: false  # Feature flag for canary deployment
  sample_pct: 10  # 10% traffic sampling

# Phase 1: Enhanced Reranking
rerank:
  method: cross_encoder
  cross_encoder:
    model_name: "BAAI/bge-reranker-base"
    onnx_path: "models/reranker.onnx"  # Optional ONNX export
    micro_batch_size: 32
    timeout_ms: 400
    workers: 3

  windowing:
    enabled: true
    window_size_tokens: 150
    overlap_pct: 33

  dedup:
    enabled: true
    method: cosine
    threshold: 0.9

resilience:
  singleflight:
    enabled: true
    ttl_seconds: 30
  fallback:
    bm25_only_on_timeout: true
```

## 🚀 Usage

### Integration Script

```bash
# Full golden set evaluation with all Phase 0/1 features
python scripts/phase01_integration.py --config config/retrieval.yaml --golden configs/eval/golden/

# Single query testing
python scripts/phase01_integration.py --single-query "What is DSPy?"
```

### Programmatic Usage

```python
from src.telemetry.request_logger import log_rag_request
from src.retrieval.windowing import create_windower
from src.retrieval.deduplication import create_deduplicator
from src.evaluation.enhanced_metrics import EnhancedEvaluator

# Initialize components
windower = create_windower({"window_size_tokens": 150, "overlap_pct": 33})
deduplicator = create_deduplicator({"method": "cosine", "threshold": 0.9})
evaluator = EnhancedEvaluator()

# Use in retrieval pipeline
windows = windower.create_windows(candidates, max_windows_per_doc=3)
deduplicated = deduplicator.filter_duplicates(windows, text_field="text")

# Log requests with telemetry
await log_rag_request(
    query="User question",
    answer="Generated response",
    confidence=0.85,
    stage_timings={"retrieval": 150, "rerank": 200, "generation": 300}
)
```

## 📊 Evaluation Pipeline

The enhanced evaluation pipeline provides comprehensive metrics:

```bash
# Results in metrics/phase01_evaluation_TIMESTAMP.json
{
  "ndcg_10": 0.75,        # Ranking quality
  "coverage": 0.68,       # Sub-claim support
  "exact_match": 0.45,    # Perfect answer matches
  "span_support": 0.82,   # Evidence backing
  "f1_score": 0.71,       # Token-level F1
  "ece": 0.12,           # Calibration error
  "temperature_param": 1.2, # Scaling factor
  "slice_metrics": {
    "novice": {"f1_score": 0.78, "coverage": 0.72},
    "expert": {"f1_score": 0.65, "coverage": 0.64}
  }
}
```

## 🔄 Integration Points

### Existing Codebase Integration

The implementation integrates cleanly with existing code:

- **`dspy-rag-system/src/utils/hybrid_retriever.py`**: Enhanced with windowing, dedup, cross-encoder support
- **`src/retrieval/`**: Existing fusion, prefilter, reranker modules work unchanged
- **`configs/eval/`**: Existing evaluation structure extended with golden slices
- **`scripts/eval/`**: Compatible with existing `eval_retrieval.py` and `eval_faithfulness.py`

### HybridRetriever Enhancement

```python
# Enhanced constructor with Phase 0/1 features
retriever = HybridRetriever(
    enable_windowing=True,
    enable_dedup=True,
    enable_cross_encoder=False,  # Requires ONNX model
    enable_singleflight=True
)

# Set Phase 0/1 components
retriever.set_phase01_components(
    windower=windower,
    deduplicator=deduplicator,
    cross_encoder_client=cross_encoder_client
)
```

## 🎯 Next Steps (Your One-Sprint Ship Plan)

The implementation delivers your "one-sprint ship first" plan:

1. **✅ Reranker service**: Cross-encoder with ONNX-INT8, micro-batch 32, 400ms budget
2. **✅ RRF fusion + windowing + dedup**: Pre-rerank pipeline with window-level processing
3. **✅ Eval harness**: Golden slices, nDCG@10, Coverage, F1, hard-negative mining logs
4. **✅ Confidence**: Calibrated score with temperature scaling, abstain thresholds
5. **✅ Concurrency/timeouts**: Worker bounds, singleflight, stage timeouts, graceful fallback

## 🚨 Canary Deployment Ready

All features are behind feature flags in `config/retrieval.yaml`:
- Enable canary on 10% traffic with `canary.enabled: true`
- Compare before/after ranks via telemetry logs
- Gradual rollout with circuit breakers and fallback paths

## 📈 Performance Targets

Aligned with your Phase 0 baseline enforcement:

- **Precision**: Maintain ≥0.149 (current baseline)
- **Recall**: Target ≥0.35 (vs current 0.099)
- **F1**: Target ≥0.22 (vs current 0.112)
- **Latency P95**: <250ms per stage budget

The implementation provides the surgical, feature-flagged foundation to push these metrics past the baseline while maintaining production safety.
