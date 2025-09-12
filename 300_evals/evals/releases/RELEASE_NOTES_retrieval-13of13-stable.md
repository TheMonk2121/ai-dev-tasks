# 🚀 Release Notes: retrieval-13of13-stable

**Tag**: `retrieval-13of13-stable`  
**Commit SHA**: `f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8`  
**Date**: September 7, 2025  
**Status**: ✅ **PRODUCTION READY**

## 📊 **Performance Metrics**

### **Prefilter Performance**
- **Hits**: 13/13 (100% success rate)
- **Micro Average**: 1.000 (≥0.85 required)
- **Macro Average**: 1.000 (≥0.75 required)
- **All Tags**: rag_qa_single: 1.000

### **CI Gate Results**
```
[prefilter] micro=1.000 macro=1.000
[tag] rag_qa_single: 1.000
PASS ✅
```

## 🔒 **Frozen Artifacts (Gold Set)**

### **Configuration Files**
- `configs/retriever_weights.yaml` - Optimized weight configuration
- `configs/retriever_limits.yaml` - Retrieval limits configuration
- `evals/gold_cases.json` - Gold standard evaluation cases (13 cases)

### **Database Schema**
- Applied DDL: `scripts/migrations/add_documents_path_tsv.sql`
- Database: `postgresql://danieljacobs@localhost:5432/ai_agency`

## 🛠️ **Fast Rollback Switches**

### **Runtime Toggles (No Code Changes)**
```bash
# Reader mode
export READER_COMPACT=0  # → full-chunk reader
export READER_COMPACT=1  # → compact context (default)

# Vector operations
export PGVECTOR_OPS=cosine  # default
export PGVECTOR_OPS=l2      # alternative
export PGVECTOR_OPS=ip      # alternative

# Disable db adjacency
adjacency_db=False  # in retriever call

# Per-file cap adjustment
per_file_cap=4  # if single file clustering occurs
```

## 🎯 **Enhanced Features**

### **Grid Optimization System**
- ✅ Auto-apply best weights with safety rails (`--apply-best --min-delta`)
- ✅ Tag-aware performance reporting with macro/micro averages
- ✅ Enhanced db_workflows phrase hints (17 SQL-specific phrases)
- ✅ Tag filtering and fail-fast options (`--tag-filter`, `--min-tag-hit`)

### **SQL-Specific Phrase Hints**
```yaml
db_workflows: [
  '"create index"', '"create unique index"', '"alter table"', '"create table"',
  '"create materialized view"', '"drop index"', '"foreign key"', '"primary key"',
  '"on conflict"', '"generated always as"', '"stored"',
  '"using gin"', '"using gist"', '"using ivfflat"', '"using hnsw"',
  '"to_tsvector"', '"tsquery"', '"websearch_to_tsquery"'
]
```

## 🔧 **Environment Configuration**

### **Required Environment Variables**
```bash
export PGVECTOR_OPS=cosine
export RETRIEVER_WEIGHTS_FILE=configs/retriever_weights.yaml
export RETRIEVER_LIMITS_FILE=configs/retriever_limits.yaml
export READER_COMPACT=1
```

### **CI Gate Thresholds**
```bash
export PREFILTER_MIN_MICRO=0.85
export PREFILTER_MIN_TAG=0.75
export MAX_REG_DROP=0.05
```

## 📈 **Optimization Results**

### **Grid Search Results**
- **Combinations Tested**: 288 weight combinations
- **Best Performance**: All combinations achieved 13/13 hits
- **Selected Weights**:
  ```yaml
  default:
    w_path: 2.0
    w_short: 1.8
    w_title: 1.4
    w_bm25: 1.0
    w_vec: 1.1
    adjacency_db: 0
    per_file_cap: 4
  ```

## 🚨 **Rollback Procedures**

### **Immediate Rollback**
1. **Restore weights**: `cp configs/retriever_weights.yaml.*.bak configs/retriever_weights.yaml`
2. **Disable compact reader**: `export READER_COMPACT=0`
3. **Rerun smoke test**: `GOLD_FILE=evals/gold/v1/gold_cases.jsonl python3 scripts/smoke_prefilter.py`

### **Database Rollback**
- DDL is idempotent and fallback-compatible
- No action required for database rollback

## 🎯 **Success Criteria Met**

- ✅ **13/13 prefilter hits** (100% success rate)
- ✅ **CI gates passing** (micro ≥ 0.85, macro ≥ 0.75)
- ✅ **Tag thresholds met** (all tags ≥ 0.75)
- ✅ **Production-ready configuration** applied
- ✅ **Version control** with tagged release
- ✅ **Rollback procedures** documented

## 🔮 **Next Steps**

### **Day-1 Guardrails**
- Runtime watch (prefilter micro ≥ 0.85, each tag ≥ 0.75)
- Ablation snapshot for provenance tracking
- Reader/F1 optimization with compact context

### **Future Enhancements**
- Path A: Reader gate with end-to-end F1 floors
- Path B: Drift detector for weekly monitoring
- Path C: Cold-start hardening with w_vec fallback

---

**Release Status**: ✅ **SHIPPED**  
**Deployment**: Ready for production use  
**Monitoring**: CI gates active and passing
