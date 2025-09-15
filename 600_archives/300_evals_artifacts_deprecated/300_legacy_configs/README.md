# 300_legacy_configs

## ⚠️ Legacy Directory - Unused Configuration Files

This directory contains **legacy configuration files** that were moved from `300_evals/configs/` because they are no longer actively used in the current evaluation system.

### 📁 Contents

**42 Legacy Configuration Files Moved:**

#### **Experiment Configs (6 files):**
- `300_enhanced_bedrock_config.env` - Enhanced Bedrock client configuration
- `300_multi_key_bedrock.env` - Multi-key Bedrock configuration
- `retrieval_quality.yaml` - Retrieval quality test configuration
- `robustness_quality.yaml` - Robustness quality test configuration
- `faithfulness_quality.yaml` - Faithfulness quality test configuration
- `latency_quality.yaml` - Latency quality test configuration

#### **Testing Configs (2 files):**
- `sentinels.yml` - Test sentinel configuration
- `budgets.yml` - Test budget configuration

#### **Auto-Generated Meta Files (17 files):**
- `bedrock_conservative.meta.yml` - Auto-generated metadata
- `current_best.meta.yml` - Auto-generated metadata
- `deterministic_evaluation.meta.yml` - Auto-generated metadata
- `learned_fusion.meta.yml` - Auto-generated metadata
- `precision_aggressive_debug.meta.yml` - Auto-generated metadata
- `precision_elevated.meta.yml` - Auto-generated metadata
- `precision_evidence_filter.meta.yml` - Auto-generated metadata
- `precision_final_push.meta.yml` - Auto-generated metadata
- `precision_focused.meta.yml` - Auto-generated metadata
- `precision_optimization_grid.meta.yml` - Auto-generated metadata
- `precision_optimized_bedrock.meta.yml` - Auto-generated metadata
- `precision_optimized_bedrock_correct.meta.yml` - Auto-generated metadata
- `precision_outlier_focused.meta.yml` - Auto-generated metadata
- `precision_percentile_mode.meta.yml` - Auto-generated metadata
- `precision_push.meta.yml` - Auto-generated metadata
- `real_rag_evaluation.meta.yml` - Auto-generated metadata
- `recall_optimized.meta.yml` - Auto-generated metadata
- `recall_optimized_bedrock.meta.yml` - Auto-generated metadata
- `recall_path_a.meta.yml` - Auto-generated metadata
- `recall_path_a_fusion.meta.yml` - Auto-generated metadata
- `recall_path_b.meta.yml` - Auto-generated metadata
- `recall_path_c.meta.yml` - Auto-generated metadata
- `recall_path_d.meta.yml` - Auto-generated metadata
- `repo_gold_evaluation.meta.yml` - Auto-generated metadata
- `reranker_disabled.meta.yml` - Auto-generated metadata
- `reranker_off.meta.yml` - Auto-generated metadata
- `reranker_on.meta.yml` - Auto-generated metadata
- `reranker_toggle.meta.yml` - Auto-generated metadata
- `retrieval-13of13-stable.meta.yml` - Auto-generated metadata
- `stable_bedrock.meta.yml` - Auto-generated metadata

#### **Other Legacy Files:**
- `.env` - Legacy environment file (if present)

### 🚫 Status: Legacy

These configuration files are **not actively used** in current evaluation scripts:

#### **Analysis Results:**
- **No script references** found in current evaluation workflows
- **No active usage** in deployment or CI/CD pipelines
- **Auto-generated metadata** files that were created but never integrated
- **Experimental configurations** that were tested but not adopted
- **Historical configurations** from previous evaluation attempts

#### **Currently Active Configs:**
All active configuration files have been moved to `300_evals/configs/active/`:
- **Profile configs**: `precision_elevated.env`, `recall_optimized.env`, `recall_optimized_bedrock.env`, `stable_bedrock.env`
- **Layer configs**: `base.env`, `stable.env`, `reranker_on.env`, `reranker_off.env`, `delta_fewshot.env`
- **System configs**: `base.yaml`, `dev.yaml`, `prod.yaml`, `test.yaml`, `retrieval.yaml`
- **CI configs**: `.pre-commit-config.yml`, `.cz.yaml`

### 🔒 Database Exclusion

This directory is **automatically excluded** from database ingestion by:
- `scripts/data_processing/ingest_real_data.py` (line 144)
- `scripts/data_processing/ingest_real_data_semantic.py` (line 144)

### 📝 Notes

- **Last Updated**: 2025-09-14
- **Reason for Archive**: Configuration cleanup and organization
- **Replacement**: Active configs moved to `300_evals/configs/active/`
- **Database Impact**: None (excluded from ingestion)
