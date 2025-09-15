# 300_eval_configs_legacy

## ⚠️ Legacy Directory - Do Not Use

This directory contains **legacy evaluation configuration files** that are no longer used by the current evaluation system.

### 📁 Contents

- `golden/hop_complexity_queries.jsonl` - Single vs multi-hop query test cases
- `golden/novice_expert_queries.jsonl` - Novice vs expert difficulty test cases

### 🚫 Status: Legacy

These files were created during development but **never integrated** into the main evaluation system. The current evaluation system uses:

- **Active Golden Datasets**: `300_evals/evals/data/gold/v1/gold_cases.jsonl`
- **Configuration**: `300_evals/configs/yaml/retrieval.yaml`
- **Unified Loader**: `src/utils/gold_loader.py`

### 🔒 Database Exclusion

This directory is **automatically excluded** from database ingestion by:
- `scripts/data_processing/ingest_real_data.py` (line 144)
- `scripts/data_processing/ingest_real_data_semantic.py` (line 104)

### 📅 Moved

**Date**: 2025-09-15  
**From**: `300_evals/experiments/300_eval_configs/`  
**To**: `300_evals/artifacts/300_eval_configs_legacy/`  
**Reason**: Legacy files not referenced by current evaluation system

### 🗑️ Safe to Remove

This directory can be safely archived or removed as it contains no active code or configuration.
