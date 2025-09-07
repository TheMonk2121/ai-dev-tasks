# 🚀 Production Go-Live Checklist

**Final tighten before production deployment**

## 📋 Pre-Deployment Checklist

### ✅ Run Manifest System
- [ ] **Freeze run manifest per eval/deploy**
  - [ ] Model IDs captured and versioned
  - [ ] CONFIG_HASH generated and stored
  - [ ] INGEST_RUN_ID tracked and validated
  - [ ] Rerank settings documented
  - [ ] Thresholds defined and locked
  - [ ] Prompt audit flags enabled

**Command**: `python3 scripts/eval_manifest_generator.py --format yaml`

### ✅ Deterministic Evaluations
- [ ] **Temperature=0** for all generation models
- [ ] **EVAL_DISABLE_CACHE=1** to prevent cache contamination
- [ ] **Prompt audit on** with few_shot_ids tracking
- [ ] **Prompt hash** validation enabled
- [ ] **CoT flag** controlled and audited
- [ ] **Random seed=42** for reproducibility

**Command**: `source configs/deterministic_evaluation.env`

### ✅ Health-Gated Evaluation
- [ ] **Environment validation** - all critical env vars present
- [ ] **Index presence** - vector index and data validated
- [ ] **Token budget** - limits within acceptable ranges
- [ ] **Prefix leakage** - BM25 text isolation verified
- [ ] **Database connectivity** - all connections tested
- [ ] **Model availability** - all models responsive

**Command**: `python3 scripts/health_gated_evaluation.py`

### ✅ Concurrency Controls
- [ ] **2-3 workers maximum** until live profiling
- [ ] **BEDROCK_MAX_IN_FLIGHT=1** to prevent rate limiting
- [ ] **Conservative RPS limits** (0.12 for Bedrock)
- [ ] **Timeout configurations** (35s call, 25s text)
- [ ] **Resource monitoring** enabled

### ✅ Backup System
- [ ] **Document chunks snapshot** before cutover
- [ ] **Active-pointer tables** backed up
- [ ] **Configuration state** preserved
- [ ] **Restore script** generated and tested
- [ ] **Backup integrity** validated

**Command**: `python3 scripts/backup_system.py --action create --description "Pre-production cutover"`

## 🧪 48-Hour Canary Monitoring

### 📊 KPI Monitoring vs Baseline

#### Oracle Metrics
- [ ] **oracle_retrieval_hit_prefilter** ↑ (target +5-15 pts)
- [ ] **reader_used_gold** ≥ baseline
- [ ] **F1 score** ≥ baseline
- [ ] **Precision drift** ≤ 2 pts
- [ ] **P95 latency** ≤ +15%

#### Data Quality Gates
- [ ] **0 budget violations** - context size limits respected
- [ ] **0 prefix leakage** - BM25 text isolation maintained
- [ ] **Dedup 10-35%** - appropriate deduplication rate
- [ ] **Snapshot breadth stable** - no silent clamps

#### Tool Governance
- [ ] **>95% schema-conformant** tool calls
- [ ] **Dry-run required** for all mutating tools
- [ ] **"tool-intent" line** present in traces

### 🚨 Rollback Triggers
If any KPI crosses thresholds:
- [ ] **Flip active pointer back** (instant rollback)
- [ ] **Clear cache** completely
- [ ] **Rerun smoke eval** to verify baseline

**Command**: `python3 scripts/48_hour_canary_monitor.py --baseline <baseline_file> --eval-results <current_file>`

## 🌙 Nightly Operations

### Smoke Evaluation
- [ ] **Ops/health** - system health checks
- [ ] **DB workflows** - database operations validation
- [ ] **RAG QA** - retrieval and generation quality
- [ ] **Meta-ops** - evaluation pipeline health
- [ ] **Negatives** - error handling and edge cases

**Command**: `python3 scripts/nightly_smoke_evaluation.py`

### Weekly Full Evaluation
- [ ] **Full eval + triage** - comprehensive performance review
- [ ] **SOP cards** - standard operating procedures
- [ ] **Small config nudges** - RRF weights, per-doc caps
- [ ] **Domain chunk overrides** - code-heavy vs prose optimization

### Few-Shot Refresh
- [ ] **Deterministic KNN** - consistent few-shot selection
- [ ] **Leakage guard on** - prevent eval contamination
- [ ] **Curated pool rotation** - maintain quality standards

## 🎯 Success Criteria (Day-2 SLOs)

### Accuracy Targets
- [ ] **Oracle prefilter ≥ 85%** - retrieval quality
- [ ] **Reader used gold ≥ 70%** - generation quality
- [ ] **Dev set performance** maintained or improved

### Reliability Targets
- [ ] **Zero hard timeouts** in eval path
- [ ] **<1% tool call retries** with backoff
- [ ] **Graceful degradation** under load

### Performance Targets
- [ ] **P95 end-to-end ≤ baseline +15%** - latency
- [ ] **Embeddings ≤ 35ms** on MPS (65ms CPU acceptable)
- [ ] **Throughput maintained** under load

### Governance Targets
- [ ] **100% runs with prompt audit** + manifest attached
- [ ] **Zero leakage** of eval items into few-shot pool
- [ ] **Complete audit trails** for all operations

## 🔧 Production Commands

### Initial Deployment
```bash
# 1. Create backup
python3 scripts/backup_system.py --action create --description "Pre-production cutover"

# 2. Run health checks
python3 scripts/health_gated_evaluation.py

# 3. Generate manifest
python3 scripts/eval_manifest_generator.py --format yaml

# 4. Run deterministic evaluation
source configs/deterministic_evaluation.env
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable
```

### Canary Monitoring
```bash
# Start 48-hour canary monitoring
python3 scripts/48_hour_canary_monitor.py \
  --baseline metrics/baseline_evaluations/latest_baseline.json \
  --eval-results metrics/baseline_evaluations/latest_eval.json \
  --duration 48
```

### Nightly Operations
```bash
# Run nightly smoke evaluation
python3 scripts/nightly_smoke_evaluation.py

# Check backup status
python3 scripts/backup_system.py --action list
```

### Emergency Rollback
```bash
# If rollback required
python3 scripts/backup_system.py --action restore --backup-id <backup_id> --confirm
```

## 📝 Documentation Requirements

### Run Manifest Template
Each evaluation run must generate a manifest with:
- **Model IDs** and versions
- **CONFIG_HASH** for reproducibility
- **INGEST_RUN_ID** for data lineage
- **Rerank settings** and parameters
- **Thresholds** and quality gates
- **Dataset IDs** and checksums
- **Few_shot_ids** and prompt_hash
- **Audit trail** information

### Quality Gates Configuration
```yaml
quality_gates:
  precision_min: 0.20
  recall_min: 0.45
  f1_min: 0.22
  latency_max: 30.0
  faithfulness_min: 0.60
  oracle_retrieval_hit_min: 0.85
  reader_used_gold_min: 0.70
```

## 🚨 Emergency Procedures

### Critical Failure Response
1. **Immediate rollback** using backup system
2. **Clear all caches** to prevent contamination
3. **Rerun smoke evaluation** to verify baseline
4. **Document incident** with full audit trail
5. **Root cause analysis** before retry

### Performance Degradation Response
1. **Check canary monitoring** for threshold breaches
2. **Analyze deltas** and regression patterns
3. **Review configuration changes** since last stable run
4. **Consider rollback** if degradation > 15%
5. **Implement fixes** before retry

## ✅ Final Sign-off

- [ ] **All pre-deployment checks** completed
- [ ] **Backup system** tested and validated
- [ ] **Health gates** configured and tested
- [ ] **Canary monitoring** ready for deployment
- [ ] **Rollback procedures** tested and documented
- [ ] **Team notified** of go-live schedule
- [ ] **Monitoring dashboards** configured
- [ ] **Alert thresholds** set and tested

**Ready for production deployment** ✅

---

*This checklist ensures safe, monitored production deployment with comprehensive rollback capabilities and continuous quality assurance.*
