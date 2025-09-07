# 🎯 Verbal Definition of Ready

**Production readiness criteria that can be verified verbally**

## Core Readiness Criteria

### 1. **"What produced this eval?" - Complete Traceability**

**Verbal Check**: *"I can answer 'what produced this eval' from the manifest alone"*

**Required Information**:
- **Models**: embedder, reranker, generator with versions
- **Config hash**: CONFIG_HASH for complete configuration traceability
- **Run ID**: INGEST_RUN_ID for data lineage
- **Dataset**: dataset_id, data_checksum, dataset version
- **Thresholds**: all production thresholds and their values
- **Few-shot IDs**: specific few-shot examples used
- **Prompt hash**: prompt version and content hash

**Manifest Structure**:
```yaml
run_id: ${INGEST_RUN_ID}
config_hash: ${CONFIG_HASH}
models:
  embedder: intfloat/e5-large-v2
  reranker: BAAI/bge-reranker-base
  generator: <name-or-bedrock-id>
dataset:
  dataset_id: dev
  data_checksum: abc123...
  version: 2025-09-07-v1
thresholds:
  f1_min: 0.22
  precision_drift_max: 0.02
  oracle_prefilter_target: 0.85
provenance:
  few_shot_ids: [fs_001, fs_002, fs_003]
  prompt_hash: def456...
  pool_version: 2025-09-07-v1
```

---

### 2. **"One-Command Rollback" - Emergency Response**

**Verbal Check**: *"I can roll back in one command and prove it with a smoke eval"*

**Required Capabilities**:
- **Single command**: `python3 scripts/on_call_ready_system.py --action rollback --reason "Emergency"`
- **Active pointer flip**: Automatic reversion to prior run
- **Cache clearing**: Complete retrieval cache cleanup
- **Smoke eval**: Automatic validation that system is healthy
- **Audit trail**: Complete rollback logging and verification

**Rollback Process**:
1. **Flip active pointer** to previous run
2. **Clear retrieval cache** completely
3. **Re-run smoke evaluation** for validation
4. **Log rollback** with timestamp and reason
5. **Verify system health** with automated checks

---

### 3. **"Automated Triage Play" - KPI Response**

**Verbal Check**: *"If a KPI dips, I have an automated triage play that points to retrieval vs filter vs reader vs tool"*

**Required Triage Categories**:

#### **Retrieval Issues** (oracle_prefilter_rate ↓)
- **Root cause**: Retrieval breadth/fusion problems
- **Automated actions**:
  - Check run-gating (retrieved contexts span current RUN only)
  - Adjust RRF weights for dense/sparse fusion
  - Disable HyDE/PRF if enabled
- **Command**: `python3 scripts/kpi_triage_system.py --action triage --metric oracle_prefilter_rate`

#### **Filter Issues** (postfilter metrics ↓)
- **Root cause**: Evidence selector too strict/duplicative
- **Automated actions**:
  - Raise evidence budget
  - Enable novelty-first selection
  - Adjust per-document cap
- **Command**: `python3 scripts/kpi_triage_system.py --action triage --metric evidence_selector`

#### **Reader Issues** (reader_used_gold_rate ↓)
- **Root cause**: Prompt/few-shot gap
- **Automated actions**:
  - Refresh deterministic few-shots
  - Keep CoT off until stable
  - Validate leakage guard
- **Command**: `python3 scripts/kpi_triage_system.py --action triage --metric reader_used_gold_rate`

#### **Tool Issues** (tool_schema_conformance ↓)
- **Root cause**: Tool call compliance problems
- **Automated actions**:
  - Validate tool schemas
  - Enforce dry-run for mutating tools
  - Check tool call format
- **Command**: `python3 scripts/kpi_triage_system.py --action triage --metric tool_schema_conformance`

---

## Production Readiness Checklist

### **Pre-Go-Live Verification**

**Day-0 Sanity (2-minute checklist)**:
- [ ] **Secrets loaded & scoped**: POSTGRES_DSN, OPENAI_API_KEY, AWS_REGION present
- [ ] **Active pointer / run-id**: INGEST_RUN_ID and CONFIG_HASH in first log line
- [ ] **Cache stance**: EVAL_DISABLE_CACHE=1 for evals, enabled for prod
- [ ] **Reranker prewarm**: Model instantiated at process start
- [ ] **Kill switch**: DEPLOY_DISABLE_NEW_CONFIG=1 env toggle available

**Game-Day Drills (10-minute validation)**:
- [ ] **Brownout/rollback drill**: Active pointer flips, cache clears, smoke eval green
- [ ] **Negative control audit**: 3 "no-answer" cases reply "not found"
- [ ] **Prefix guard**: Zero rows in BM25 with prefix leakage

### **Week-1 Watch Criteria**

**Retrieval Quality**:
- [ ] **Oracle prefilter**: ≥ 0.85, snapshot breadth stable
- [ ] **Retrieval consistency**: No silent clamps or unexpected filtering

**Generation Quality**:
- [ ] **Reader used gold**: ≥ 0.70, "not found" correctness on negatives
- [ ] **Response quality**: Appropriate handling of edge cases

**Governance**:
- [ ] **Tool schema conformance**: > 95%, dry-run on all mutating tools
- [ ] **Audit compliance**: 100% runs with prompt audit + manifest

**Performance**:
- [ ] **P95 latency**: ≤ baseline +15%, embeddings trending down with MPS
- [ ] **Resource usage**: Stable memory and CPU patterns

**Data Quality**:
- [ ] **Token budget**: 0 violations, dedup rate 10-35%
- [ ] **Prefix leakage**: Zero rows, complete text isolation

---

## Operational Excellence

### **Continuous Monitoring**

**Nightly Smoke Tests**:
- [ ] **Ops/health**: Operations and health checks
- [ ] **DB workflows**: Database workflow validation
- [ ] **RAG QA**: RAG QA functionality
- [ ] **Meta-ops**: Meta-operations validation
- [ ] **Negatives**: Negative test cases

**Weekly Full Evaluation**:
- [ ] **Complete system validation** with comprehensive metrics
- [ ] **Triage worst cases** with automated issue identification
- [ ] **SOP card generation** for standard operating procedures
- [ ] **Config nudges** (RRF weights, per-doc caps, domain overrides)

### **Emergency Response**

**One-Command Operations**:
```bash
# Emergency rollback
python3 scripts/on_call_ready_system.py --action rollback --reason "Emergency"

# Blast radius control
python3 scripts/on_call_ready_system.py --action blast-radius --canary-limit 50

# Definition of done verification
python3 scripts/on_call_ready_system.py --action dod

# KPI triage
python3 scripts/kpi_triage_system.py --action triage --metric oracle_prefilter_rate --current-value 0.82 --threshold 0.85
```

---

## Success Criteria

### **Production Ready When**:

1. **Complete Traceability**: Every evaluation can be fully explained from its manifest
2. **Emergency Response**: One-command rollback with automatic validation
3. **Automated Triage**: KPI breaches trigger specific remediation actions
4. **Operational Rhythm**: Nightly smoke, weekly full eval, few-shot refresh
5. **Safety Controls**: Canary limits, blast radius control, kill switches
6. **Quality Gates**: All production thresholds met and monitored

### **Definition of Done**:

- ✅ **eval_path='dspy_rag'** with manifests attached to every run
- ✅ **Oracle prefilter ≥ 85%** for retrieval quality maintenance
- ✅ **Reader used gold ≥ 70%** for generation quality assurance
- ✅ **F1 ≥ baseline, precision drift ≤ 2 pts** for performance maintenance
- ✅ **P95 ≤ baseline +15%** for latency budget compliance
- ✅ **0 budget violations, 0 prefix leakage** for data integrity
- ✅ **Tool schema conformance > 95%** for governance compliance
- ✅ **Dry-run for all mutating tools** for safety enforcement

---

**Last Updated**: 2025-09-07  
**Next Review**: 2025-10-07  
**Owner**: Production Engineering Team

---

## Quick Reference

### **Verbal Readiness Check**:
1. *"Can I explain what produced this eval from the manifest alone?"* → **Yes/No**
2. *"Can I roll back in one command and prove it works?"* → **Yes/No**
3. *"Do I have automated triage for KPI breaches?"* → **Yes/No**

### **If all three are "Yes"**: **Production Ready** ✅  
### **If any are "No"**: **Not Production Ready** ❌
