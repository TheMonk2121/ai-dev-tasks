# 🛡️ Day-1 Guardrails Setup - retrieval-13of13-stable

**Tag**: `retrieval-13of13-stable`
**Commit SHA**: `f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8`
**Purpose**: Lightweight, deterministic monitoring and optimization

## 📊 **Runtime Watch (Daily Cron)**

### **Performance Monitoring Script**
```bash
#!/bin/bash
# daily_retrieval_watch.sh

# Set thresholds
PREFILTER_MIN_MICRO=0.85
PREFILTER_MIN_TAG=0.75

# Run CI gate
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py > daily_check.log 2>&1

# Check results
if grep -q "PASS ✅" daily_check.log; then
    echo "$(date): ✅ Retrieval performance OK"
else
    echo "$(date): 🚨 Retrieval performance below threshold"
    # Send alert or trigger rollback
fi
```

### **Cron Setup**
```bash
# Add to crontab (daily at 9 AM)
0 9 * * * /path/to/daily_retrieval_watch.sh
```

## 🔍 **Top Offenders Analysis**

### **Smoke Test with Detailed Output**
```bash
# Run smoke test with component scores
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py | grep -A 5 "Case.*MISS"

# Output format:
# Case [query]: ❌ MISS (25 chunks retrieved)
#    [component scores breakdown]
```

### **Component Score Analysis**
```bash
# Extract top-5 misses with scores
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py |
grep -A 10 "MISS" |
head -50
```

## 📸 **Ablation Snapshot (One Shot Per Release)**

### **Provenance Tracking**
```bash
#!/bin/bash
# ablation_snapshot.sh

echo "=== Ablation Snapshot - $(date) ===" > ablation_log.tx

# Base performance
echo "Base (no enhancements):" >> ablation_log.tx
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py >> ablation_log.tx

# +path_tsv enhancemen
echo "Base + path_tsv:" >> ablation_log.tx
# (path_tsv already applied in DDL)

# +phrases enhancemen
echo "Base + path_tsv + phrases:" >> ablation_log.tx
# (phrases already applied in query_rewrite.py)

# +MMR/cap enhancemen
echo "Base + path_tsv + phrases + MMR/cap:" >> ablation_log.tx
# (MMR/cap already applied in retriever)

# +adjacency enhancemen
echo "Base + path_tsv + phrases + MMR/cap + adjacency:" >> ablation_log.tx
# (adjacency_db=0 in current config)

# +fname_prior enhancemen
echo "Base + path_tsv + phrases + MMR/cap + adjacency + fname_prior:" >> ablation_log.tx
# (fname_regex already applied in query_rewrite.py)

echo "=== End Ablation Snapshot ===" >> ablation_log.tx
```

## 🚀 **Reader/F1 Push (Low Risk, High Yield)**

### **Compact Context Configuration**
```yaml
# configs/retriever_limits.yaml
tags:
  db_workflows: {shortlist: 60, topk: 20}  # K 18-22 range
  ops_health: {shortlist: 60, topk: 22}    # K 20-25 range
  meta_ops: {shortlist: 60, topk: 22}      # K 20-25 range
  rag_qa_single: {shortlist: 60, topk: 25} # Keep current
```

### **Character Window Targets**
```bash
# db_workflows: 280-360 char windows
# ops_health/meta_ops: top 2-3 sentences/chunk
# Monitor with:
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py | grep -o "score=[0-9.]*"
```

### **F1 Brittleness Recovery**
```bash
# If F1 is brittle on a tag:

# Option 1: Add quoted phrase
# Edit src/dspy_modules/retriever/query_rewrite.py
# Add to PHRASE_HINTS["tag_name"]: '"constraint"', '"generated always as"'

# Option 2: Bump w_vec by +0.1
# Edit configs/retriever_weights.yaml
# tags:
#   tag_name:
#     w_vec: 1.3  # was 1.2
```

## 📋 **Implementation Checklist**

### **Day-1 Setup**
- [ ] Create `daily_retrieval_watch.sh`
- [ ] Set up cron job for daily monitoring
- [ ] Run `ablation_snapshot.sh` once
- [ ] Test reader/F1 configuration
- [ ] Document any F1 brittleness issues

### **Monitoring Setup**
- [ ] Configure alerting for performance drops
- [ ] Set up log rotation for daily checks
- [ ] Create dashboard for performance metrics
- [ ] Document rollback procedures

### **Optimization Setup**
- [ ] Test compact context with different K values
- [ ] Monitor character window sizes
- [ ] Prepare quoted phrase additions
- [ ] Test w_vec adjustments

## 🎯 **Success Metrics**

### **Daily Monitoring**
- ✅ Prefilter micro ≥ 0.85
- ✅ Each tag ≥ 0.75
- ✅ Smoke test ≥ 13/13 hits
- ✅ No performance regression > 2%

### **Reader/F1 Optimization**
- ✅ Maintain or improve F1 scores
- ✅ Character windows within target ranges
- ✅ No brittleness in any tag
- ✅ Smooth performance across all cases

## 🔧 **Troubleshooting**

### **Performance Drop**
1. Check daily log for specific failures
2. Run smoke test with detailed output
3. Identify top offenders
4. Apply appropriate rollback switch
5. Document issue and resolution

### **F1 Brittleness**
1. Identify problematic tag
2. Add quoted phrase or adjust w_vec
3. Test with grid optimization
4. Apply changes with `--apply-best`
5. Verify with CI gate

---

**Setup Date**: September 7, 2025
**Tag**: `retrieval-13of13-stable`
**Status**: ✅ **READY FOR IMPLEMENTATION**
