# 🚨 Fast Incident Response Playbook - retrieval-13of13-stable

**Tag**: `retrieval-13of13-stable`  
**Commit**: `f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8`  
**Status**: Production-ready with instant rollback procedures

## ⚡ **Red Light Response Procedures**

### **Symptom: Prefilter Micro < Floor**
```bash
# 1. Immediate response
export PREFILTER_MIN_MICRO=0.85
export PREFILTER_MIN_TAG=0.75

# 2. Apply fixes
# Set adjacency_db=False in retriever call
# Raise w_vec +0.1 for worst tag in YAML
python3 scripts/tiny_grid.py --apply-best --min-delta 0

# 3. Re-run gate
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py
```

### **Symptom: README Monopolizes K**
```bash
# 1. Lower per-file cap
export PER_FILE_CAP=4
# or for severe cases:
export PER_FILE_CAP=3

# 2. Re-run gate
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py
```

### **Symptom: Cold "One-Word" Queries Underperform**
```bash
# 1. Boost cold-start vector weight
export COLD_START_WVEC_BOOST=0.15

# 2. Test with sparse queries
echo '{"query": "help", "context": "...", "tag": "rag_qa_single"}' | python3 scripts/run_reader.py --model local

# 3. Re-run gate
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py
```

### **Symptom: Path Rename/Dir Shuffle**
```bash
# 1. Add matching glob to evals/gold.jsonl
echo '{"case_id": "new_path_case", "query": "...", "answers": ["..."], "tag": "rag_qa_single"}' >> evals/gold.jsonl

# 2. Commit and re-gate
git add evals/gold.jsonl
git commit -m "fix: Add gold case for path rename"
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py
```

## 🔧 **Quick Diagnostic Commands**

### **Check Current Performance**
```bash
# Smoke test
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py

# Full CI gate
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py

# Reader gate (if implemented)
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_reader.py
```

### **Check Drift**
```bash
# Weekly drift check
python3 scripts/drift_detector.py

# Manual drift analysis
python3 -c "
import json
latest = json.load(open('evals/latest_retrieval_metrics.json'))
baseline = json.load(open('evals/baseline_metrics.json'))
print(f'Drift: {latest[\"micro\"] - baseline[\"micro\"]:.3f}')
"
```

### **Check Top Offenders**
```bash
# Run smoke with detailed output
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py --verbose

# Check specific tag performance
python3 -c "
from evals.load_cases import load_eval_cases
cases = load_eval_cases('gold')
tag_counts = {}
for case in cases:
    tag_counts[case.tag] = tag_counts.get(case.tag, 0) + 1
print('Tag distribution:', tag_counts)
"
```

## 🚨 **Emergency Rollback Procedures**

### **Full System Rollback**
```bash
# 1. Restore previous weights
cp configs/retriever_weights.yaml.$(date +%Y%m%d_%H%M%S).bak configs/retriever_weights.yaml

# 2. Disable all optimizations
export READER_COMPACT=0
export COLD_START_WVEC_BOOST=0.0
export PER_FILE_CAP=5

# 3. Re-run smoke test
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py
```

### **Database Rollback**
```bash
# If DDL caused issues (rare)
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "
DROP INDEX IF EXISTS idx_documents_path_tsv;
ALTER TABLE documents DROP COLUMN IF EXISTS path_tsv;
"
```

## 📊 **Performance Monitoring**

### **Daily Health Check**
```bash
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Health Check $(date) ==="

# 1. Smoke test
echo "1. Smoke Test:"
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py

# 2. CI gate
echo "2. CI Gate:"
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py

# 3. Drift check
echo "3. Drift Check:"
python3 scripts/drift_detector.py

echo "=== Health Check Complete ==="
```

### **Alert Thresholds**
- **Prefilter Micro**: < 0.85 (immediate action)
- **Per-tag**: < 0.75 (investigate specific tag)
- **Drift**: > 0.05 (investigate recent changes)
- **Cold-start**: < 0.20 (boost vector weight)

## 🔄 **Recovery Verification**

After applying any fix:

1. **Run smoke test** - should show 13/13 hits
2. **Run CI gate** - should show PASS ✅
3. **Check drift** - should be within limits
4. **Test edge cases** - sparse queries, long queries, mixed tags
5. **Monitor for 24h** - ensure stability

## 📞 **Escalation Path**

1. **Level 1**: Apply quick fixes (5 minutes)
2. **Level 2**: Rollback to previous config (10 minutes)
3. **Level 3**: Full system rollback (15 minutes)
4. **Level 4**: Database rollback (30 minutes)

**Success Criteria**: All gates pass, drift within limits, no performance regression.
