# 📈 Growth & Hygiene Procedures - retrieval-13of13-stable

**Tag**: `retrieval-13of13-stable`  
**Commit**: `f2bea2500c709e80e4b24fc4aeb11e6e0ac6d8a8`  
**Purpose**: Systematic growth and maintenance procedures

## 📊 **Gold Growth Rule**

### **Weekly Gold Addition**
- **Target**: +2 cases per tag per week
- **Process**: Add file path or glob at the same time
- **Quality**: Ensure cases cover edge cases and new content

### **Gold Case Template (v1)**
```json
{
  "id": "DESCRIPTIVE_CASE_ID",
  "mode": "retrieval",
  "query": "specific query text",
  "tags": ["rag_qa_single"],
  "expected_files": ["path/to/relevant/file.md"],
  "globs": ["**/*relevant*.md"]
}
```

### **Gold Growth Checklist**
- [ ] Case covers new content or edge case
- [ ] Case added to `evals/gold/v1/gold_cases.jsonl`
- [ ] Case tested with current retrieval system
- [ ] Case added to appropriate tag
- [ ] Performance impact assessed

## 🗄️ **Index Hygiene**

### **Nightly ANALYZE**
```bash
#!/bin/bash
# nightly_analyze.sh
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "
ANALYZE documents;
ANALYZE documents_embeddings;
"
```

### **Weekly VACUUM (ANALYZE)**
```bash
#!/bin/bash
# weekly_vacuum.sh
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "
VACUUM (ANALYZE) documents;
VACUUM (ANALYZE) documents_embeddings;
"
```

### **Post-Ingest Reindex**
```bash
#!/bin/bash
# reindex_ivfflat.sh
psql postgresql://danieljacobs@localhost:5432/ai_agency -c "
REINDEX INDEX CONCURRENTLY idx_documents_embedding_ivfflat;
"
```

## 📊 **Signal Telemetry**

### **Query Telemetry Schema**
```json
{
  "timestamp": "2025-09-07T12:00:00Z",
  "query_len": 25,
  "cold_start": false,
  "tag": "rag_qa_single",
  "weights": {
    "w_path": 2.0,
    "w_short": 1.8,
    "w_title": 1.4,
    "w_bm25": 1.0,
    "w_vec": 1.1
  },
  "contributions": {
    "path": 0.15,
    "short": 0.25,
    "title": 0.20,
    "bm25": 0.30,
    "vec": 0.10
  },
  "mmr_novelty": 0.75,
  "top_demotions": 2,
  "hit_at_k": {
    "k1": 1.0,
    "k5": 1.0,
    "k10": 1.0,
    "k25": 1.0
  },
  "per_file_cap_applied": 4,
  "adjacency_db": false,
  "cold_start_boost": 0.0
}
```

### **Telemetry Collection Script**
```python
#!/usr/bin/env python3
# scripts/collect_telemetry.py

import json
import os
import time
from typing import Dict, Any

def log_query_telemetry(
    query: str,
    tag: str,
    weights: Dict[str, float],
    contributions: Dict[str, float],
    mmr_novelty: float,
    top_demotions: int,
    hit_at_k: Dict[str, float],
    per_file_cap: int,
    adjacency_db: bool,
    cold_start_boost: float
):
    """Log query telemetry to JSONL file."""
    
    if not os.getenv("ENABLE_QUERY_TELEMETRY", "0") == "1":
        return
    
    telemetry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "query_len": len(query),
        "cold_start": len(query.split()) < 3,
        "tag": tag,
        "weights": weights,
        "contributions": contributions,
        "mmr_novelty": mmr_novelty,
        "top_demotions": top_demotions,
        "hit_at_k": hit_at_k,
        "per_file_cap_applied": per_file_cap,
        "adjacency_db": adjacency_db,
        "cold_start_boost": cold_start_boost
    }
    
    log_file = os.getenv("TELEMETRY_LOG_FILE", "logs/query_telemetry.jsonl")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(telemetry) + "\n")
```

## 🔄 **Known Trade-offs**

### **Overfit to Structure vs. Recall**
- **Current**: Nudge toward artifacts; vector stays semantic escape hatch
- **If recall dips on narrative answers**: Slightly raise w_vec for that tag
- **Monitoring**: Track per-tag recall metrics

### **Phrase Precision vs. Brittleness**
- **Current**: Keep phrases quoted; add 1-2 generic ones
- **Generic phrases**: "constraint", "schema", "indexing"
- **Goal**: Reduce brittleness without polluting BM25

### **Per-Tag Sentence Budgets**
- **Current**: Mirror limits in YAML
- **Control**: Fine-tune per-tag sentence selection
- **Balance**: Precision vs. context coverage

## 🚨 **Canary Alert Channel**

### **GitHub Actions Integration**
```yaml
# .github/workflows/canary-alerts.yml
name: Canary Alerts

on:
  workflow_run:
    workflows: ["CI Gate"]
    types: [completed]

jobs:
  canary-alert:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Send Canary Alert
        run: |
          echo "🚨 CI Gate Failed - Retrieval Performance Issue"
          echo "Top 5 rows for offending case/tag:"
          # Add logic to extract top-5 rows with channel scores
```

### **Alert Thresholds**
- **Prefilter Micro**: < 0.85
- **Per-tag**: < 0.75
- **Drift**: > 0.05
- **Cold-start**: < 0.20

## 📅 **Maintenance Schedule**

### **Daily**
- [ ] Health check (smoke test + CI gate)
- [ ] Telemetry review
- [ ] Performance monitoring

### **Weekly**
- [ ] Gold case addition (+2 per tag)
- [ ] VACUUM (ANALYZE) database
- [ ] Drift detection report
- [ ] Performance trend analysis

### **Monthly**
- [ ] Index optimization review
- [ ] Weight tuning assessment
- [ ] Phrase hint evaluation
- [ ] Cold-start boost calibration

### **Quarterly**
- [ ] Full ablation snapshot
- [ ] Performance baseline update
- [ ] System architecture review
- [ ] Trade-off analysis

## 🎯 **Success Metrics**

### **Performance Targets**
- **Prefilter Micro**: ≥ 0.85
- **Per-tag**: ≥ 0.75
- **Drift**: ≤ 0.05
- **Cold-start**: ≥ 0.20

### **Growth Targets**
- **Gold cases**: +2 per tag per week
- **Coverage**: 95% of content types
- **Edge cases**: 90% coverage

### **Hygiene Targets**
- **Index health**: 95% efficiency
- **Query performance**: < 100ms p95
- **Telemetry coverage**: 100% of queries
