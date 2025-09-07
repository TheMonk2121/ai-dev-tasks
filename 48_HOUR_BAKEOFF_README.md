# 48-Hour Bakeoff - Production Rollout Guide

## 🎯 Overview

This guide provides the complete 48-hour bakeoff process for rolling out the validated 450/0.10/J=0.8/prefix-A configuration to production. The system includes comprehensive monitoring, rollback capabilities, and regression prevention.

## 🚀 Quick Start

### One-Command Bakeoff
```bash
# Complete 48-hour bakeoff
python scripts/48_hour_bakeoff.py

# With custom monitoring duration
python scripts/48_hour_bakeoff.py --monitor-hours 72
```

### Step-by-Step Process
```bash
# 1. Lock configuration
python scripts/lock_production_config.py \
  --chunk-size 450 --overlap-ratio 0.10 \
  --jaccard-threshold 0.8 --prefix-policy A \
  --generate-runbook

# 2. Shadow ingest
python scripts/shadow_ingest.py

# 3. Evaluation
python scripts/production_evaluation.py

# 4. Sanity probes
python scripts/sanity_probes.py

# 5. KPI monitoring
python scripts/kpi_monitor.py --promote-check

# 6. CI parity tests
python scripts/ci_parity_tests.py

# 7. Start canary rollout
python scripts/canary_rollout.py --start
```

## 📊 Pre-Bake Setup

### Configuration Freezing
- **CHUNK_VERSION**: `2025-09-07-v1`
- **CONFIG_HASH**: `deb4bee72d017024`
- **EMBEDDER_NAME**: `BAAI/bge-large-en-v1.5`
- **TOKENIZER_NAME**: `BAAI/bge-large-en-v1.5`
- **TOKENIZER_HASH**: `f3fcfcadaa2cc403`

### Model Prewarming
- Cross-encoder: Load once at process start
- Bedrock: Keep off for evals unless wrapped with hard deadlines
- Cache stance: `EVAL_DISABLE_CACHE=1`

### Database Hygiene
```sql
VACUUM ANALYZE document_chunks_2025_09_07_040048_v1;
-- Verify indexes exist and are used (BM25 GIN & pgvector IVFFLAT)
```

### Concurrency Limits
- Limit to 2-3 workers
- `BEDROCK_MAX_IN_FLIGHT=1` if Bedrock enabled

## 🔍 Sanity Probes

### Run/Variant Fingerprints
```bash
# Check ingest_run_id and chunk_version in artifacts
jq '.case_results[0].retrieval_snapshot[0:8][].fp' metrics/baseline_evaluations/*.json
```

### Breadth and Usage
```bash
# Retrieval snapshot sizes (expect 30-60+)
jq '.case_results | map(.retrieval_snapshot|length) | max' metrics/*/ragchecker_*.json

# Retrieved context lengths (expect up to 12)
jq '.case_results | map(.retrieved_context|length) | max' metrics/*/ragchecker_*.json
```

### Oracle Path Validation
```bash
# Oracle hit rates
jq '[.case_results[].oracle_retrieval_hit_prefilter] | add' metrics/*/ragchecker_*.json
jq '[.case_results[].reader_used_gold] | add' metrics/*/ragchecker_*.json
```

### Prefix Leakage Check
```sql
-- Should return 0 rows
SELECT COUNT(*) FROM document_chunks_2025_09_07_040048_v1 
WHERE bm25_text LIKE 'Document:%';
```

## 📈 KPI Thresholds

### Retrieval Metrics (Dev Set)
- **oracle_retrieval_hit_prefilter**: +5-15 points vs baseline
- **filter_hit_postfilter**: ≥ baseline
- **reader_used_gold**: ≥ baseline

### End Metrics
- **F1**: ≥ baseline
- **Precision drift**: ≤ 2 points

### Latency
- **p95 end-to-end**: ≤ +15% vs baseline

### Data Quality
- **max(embedding_token_count)**: ≤ 1024 (0 violations)
- **Dedup rate**: 10-35%
- **retrieval_snapshot_size**: Stable (no silent clamps)
- **Prefix leakage**: 0 chunks

## 🚀 Canary Rollout

### Traffic Routing
- **0-16 hours**: 10% traffic to new configuration
- **16-32 hours**: 50% traffic to new configuration  
- **32-48 hours**: 100% traffic to new configuration

### Rollout Commands
```bash
# Start canary (10%)
python scripts/canary_rollout.py --start

# Promote to 50%
python scripts/canary_rollout.py --promote-50

# Promote to 100%
python scripts/canary_rollout.py --promote-100

# Check status
python scripts/canary_rollout.py --status
```

## 🔄 Rollback Plan

### Instant Rollback
```bash
# Rollback to previous configuration
python scripts/canary_rollout.py --rollback

# Verify rollback
python scripts/sanity_probes.py
```

### Rollback Triggers
- Any KPI threshold breach
- Oracle hit rate drops below baseline
- F1 score drops below baseline
- Precision drift > 2 points
- Token budget violations
- Prefix leakage detected

## 🧪 CI Parity Tests

### Build Failure Conditions
- `eval_path != "dspy_rag"`
- `retrieval_snapshot_size < 20`
- Missing oracle metrics
- Chunks over max_tokens
- BM25 rows with contextual prefix

### Deterministic Behavior
- Chunk IDs: `sha1(doc_id|byte_span|CHUNK_VERSION|CONFIG_HASH)`
- Global seed for stochastic reranking
- Idempotent operations

## 📊 Monitoring Dashboard

### Key Metrics to Watch
- **Oracle Hit Rate**: Target ≥0.45
- **Filter Hit Rate**: Target ≥0.20
- **Reader Gold Usage**: Target ≥baseline
- **Retrieval Snapshot Size**: Target 30-60 chunks
- **CE Score Distribution**: Monitor for drift
- **Ingest Throughput**: Monitor performance
- **Deduplication Rate**: Target 10-35%

### Alert Conditions
- 🚨 Oracle hit rate drops below baseline
- 🚨 F1 score drops below baseline
- 🚨 Precision drift > 2 points
- 🚨 Token budget violations
- 🚨 Prefix leakage detected
- ⚠️ Low retrieval snapshot size
- ⚠️ High latency

## 🔧 Troubleshooting

### Common Issues

#### Configuration Not Found
```bash
# Check active configuration
cat config/locked_configs/active_config.json
```

#### Environment Variables Not Set
```bash
# Verify environment setup
python scripts/production_evaluation.py --skip-ingest --skip-eval
```

#### Retrieval Health Issues
```bash
# Run health monitor
python scripts/production_health_monitor.py
```

#### Evaluation Failures
```bash
# Check evaluation results
ls -la metrics/baseline_evaluations/
jq '.case_results | length' metrics/baseline_evaluations/*.json
```

### Debug Commands
```bash
# Check configuration status
python -c "
from dspy_rag_system.src.utils.config_lock import ConfigLockManager
manager = ConfigLockManager()
config = manager.get_active_config()
print(f'Active config: {config.chunk_version if config else \"None\"}')
"

# Validate configuration
python -c "
from dspy_rag_system.src.utils.config_lock import ProductionGuardrails, LockedConfig
import json

with open('config/locked_configs/active_config.json') as f:
    config_data = json.load(f)
config = LockedConfig.from_dict(config_data)
guardrails = ProductionGuardrails(config)
validation = guardrails.validate_config()
print(f'Config valid: {validation[\"valid\"]}')
"
```

## 📋 Checklist

### Pre-Bake
- [ ] Configuration locked and versioned
- [ ] Models prewarmed
- [ ] Database hygiene completed
- [ ] Cache stance configured
- [ ] Concurrency limits set

### Evaluation
- [ ] Shadow ingest completed
- [ ] Evaluation run successfully
- [ ] Sanity probes passed
- [ ] KPI monitoring passed
- [ ] CI parity tests passed

### Rollout
- [ ] Canary rollout started (10%)
- [ ] Monitoring active
- [ ] Rollback plan ready
- [ ] Alerts configured

### Post-Rollout
- [ ] 48-hour monitoring completed
- [ ] All metrics within thresholds
- [ ] v1 configuration archived
- [ ] Documentation updated

## 🎯 Success Criteria

### Promotion Ready
- All sanity probes pass
- KPI thresholds met
- CI parity tests pass
- No regression detected

### Rollout Complete
- 48-hour monitoring successful
- All metrics stable
- No rollback required
- v1 configuration archived

## 📚 Additional Resources

- [Production Configuration Locking Guide](400_guides/400_production-configuration-locking.md)
- [Enhanced Chunking Documentation](dspy-rag-system/src/utils/enhanced_chunking.py)
- [Configuration Lock System](dspy-rag-system/src/utils/config_lock.py)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the configuration locking guide
3. Run the debug commands
4. Check the monitoring dashboard

---

**Remember**: The 48-hour bakeoff is designed to be safe and reversible. If any issues arise, use the rollback plan immediately.
