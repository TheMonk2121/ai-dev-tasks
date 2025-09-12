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

# 3. Re-run gate (unified gold)
uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 30
```

### **Symptom: README Monopolizes K**
```bash
# 1. Lower per-file cap
export PER_FILE_CAP=4
# or for severe cases:
export PER_FILE_CAP=3

# 2. Re-run gate (unified gold)
uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 30
```

### **Symptom: Cold "One-Word" Queries Underperform**
```bash
# 1. Boost cold-start vector weight
export COLD_START_WVEC_BOOST=0.15

# 2. Test with sparse queries
echo '{"query": "help", "context": "...", "tag": "rag_qa_single"}' | python3 scripts/run_reader.py --model local

# 3. Re-run gate (unified gold)
uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 30
```

### **Symptom: Path Rename/Dir Shuffle**
```bash
# 1. Add matching case to evals/gold/v1/gold_cases.jsonl
# Example (retrieval mode):
echo '{"id":"PATH_RENAME_CASE","mode":"retrieval","query":"Locate the new file path for ...","tags":["rag_qa_single"],"expected_files":["docs/new/path.md"],"globs":["docs/**/*.md"]}' >> evals/gold/v1/gold_cases.jsonl

# 2. Commit and re-gate
git add evals/gold/v1/gold_cases.jsonl
git commit -m "fix: add v1 gold case for path rename"
uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 30
```

## 🔧 **Quick Diagnostic Commands**

### **Check Current Performance**
```bash
# Smoke test
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/smoke_prefilter.py

# Full CI gate
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/ci_gate_retrieval.py

# Reader gate (if implemented)
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/ci_gate_reader.py
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
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/smoke_prefilter.py --verbose

# Check specific tag performance
python3 -c "
from scripts.migrate_to_pydantic_evals import load_eval_cases
cases = load_eval_cases('gold')
tag_counts = {}
for case in cases:
    for tag in case.tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
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
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/smoke_prefilter.py
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
GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/smoke_prefilter.py

# 2. CI gate
echo "2. CI Gate:"
uv run python scripts/smoke_eval_gate.py --gold-file evals/gold/v1/gold_cases.jsonl --gold-size 30

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
