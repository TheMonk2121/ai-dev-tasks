# 🚨 Fast Rollback Switches - retrieval-13of13-stable

**Tag**: `retrieval-13of13-stable`  
**Commit SHA**: `f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8`  
**Status**: Production-ready with instant rollback capabilities

## ⚡ **Instant Rollback Switches (No Code Changes)**

### **1. Reader Mode Toggle**
```bash
# Current (compact context)
export READER_COMPACT=1

# Rollback (full-chunk reader)
export READER_COMPACT=0
```

### **2. Vector Operations**
```bash
# Current (cosine similarity)
export PGVECTOR_OPS=cosine

# Alternatives
export PGVECTOR_OPS=l2      # L2 distance
export PGVECTOR_OPS=ip      # Inner product
```

### **3. Database Adjacency**
```python
# Current (disabled)
adjacency_db=False

# Enable if needed
adjacency_db=True
```

### **4. Per-File Cap Adjustment**
```yaml
# Current
per_file_cap: 4

# Reduce if single file clustering
per_file_cap: 3
# or
per_file_cap: 2
```

## 🔧 **Configuration Rollback**

### **Restore Previous Weights**
```bash
# List available backups
ls -la configs/retriever_weights.yaml.*.bak

# Restore specific backup (example)
cp configs/retriever_weights.yaml.20250907_162045.bak configs/retriever_weights.yaml

# Or restore to tag state
git checkout retrieval-13of13-stable -- configs/retriever_weights.yaml
```

### **Restore Previous Limits**
```bash
# Restore limits to tag state
git checkout retrieval-13of13-stable -- configs/retriever_limits.yaml
```

## 🧪 **Rollback Verification**

### **Quick Smoke Test**
```bash
# Run smoke test to verify rollback
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py

# Expected: "Prefilter hits: 13/13" or better
```

### **CI Gate Test**
```bash
# Run CI gate to verify thresholds
export PREFILTER_MIN_MICRO=0.85
export PREFILTER_MIN_TAG=0.75
export MAX_REG_DROP=0.05
CASES_FILE=evals/gold_cases.json python3 scripts/ci_gate_retrieval.py

# Expected: "PASS ✅"
```

## 🚨 **Emergency Rollback Procedures**

### **Complete System Rollback**
```bash
# 1. Restore all configs to tag state
git checkout retrieval-13of13-stable -- configs/

# 2. Disable compact reader
export READER_COMPACT=0

# 3. Verify with smoke test
CASES_FILE=evals/gold_cases.json python3 scripts/smoke_prefilter.py

# 4. If still failing, check database connection
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "SELECT 1;"
```

### **Database Rollback**
```bash
# DDL is idempotent - no rollback needed
# If issues persist, check:
# 1. Database connection
# 2. Index status
# 3. Table structure
```

## 📊 **Rollback Decision Matrix**

| Issue | Rollback Action | Verification |
|-------|----------------|--------------|
| **Performance Drop** | Restore weights backup | Smoke test |
| **Reader Issues** | `READER_COMPACT=0` | Smoke test |
| **Vector Issues** | `PGVECTOR_OPS=l2` | Smoke test |
| **File Clustering** | `per_file_cap=3` | Smoke test |
| **Complete Failure** | Full config rollback | CI gate |

## 🔍 **Monitoring Thresholds**

### **Performance Floors**
- **Prefilter Micro**: ≥ 0.85
- **Prefilter Macro**: ≥ 0.75
- **Per-Tag Hit Rate**: ≥ 0.75
- **Smoke Test**: ≥ 13/13 hits

### **Alert Conditions**
- Any metric below floor
- Smoke test < 13/13 hits
- CI gate failure
- Performance drop > 5%

## 📝 **Rollback Log Template**

```bash
# Log rollback actions
echo "$(date): Rollback initiated - [REASON]" >> rollback.log
echo "$(date): Action taken - [ACTION]" >> rollback.log
echo "$(date): Verification - [RESULT]" >> rollback.log
```

---

**Last Updated**: September 7, 2025  
**Tag**: `retrieval-13of13-stable`  
**Status**: ✅ **READY FOR PRODUCTION**
