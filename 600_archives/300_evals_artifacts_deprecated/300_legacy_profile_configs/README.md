# 300_legacy_profile_configs

## ⚠️ Legacy Directory - Unused Profile Configuration Files

This directory contains **legacy profile configuration files** that were moved from `300_evals/configs/profiles/` because they are no longer actively used in the current evaluation system.

### 📁 Contents

**17 Legacy Profile Files Moved:**
- `bedrock_conservative.env` - Conservative Bedrock settings to prevent hangs
- `current_best.env` - Current best configuration (symlink to precision_elevated)
- `deterministic_evaluation.env` - Deterministic evaluation settings with temperature=0
- `learned_fusion.env` - Learned fusion head configuration
- `precision_evidence_filter.env` - Precision evidence filter configuration
- `precision_optimized_bedrock.env` - Precision optimized Bedrock configuration
- `precision_optimized_bedrock_correct.env` - Corrected precision optimized Bedrock
- `real_rag_evaluation.env` - Real RAG system evaluation configuration
- `recall_path_a.env` - Recall Path A: Retrieval breadth + smarter fusion
- `recall_path_b.env` - Recall Path B: Query expansion (HyDE + PRF)
- `recall_path_d.env` - Recall Path D: Reader loop with answerability check
- `repo_gold_evaluation.env` - Repo-gold evaluation configuration
- `reranker_disabled.env` - Reranker disabled configuration
- `reranker_off.env` - Reranker off configuration layer
- `reranker_on.env` - Reranker on configuration layer
- `reranker_toggle.env` - Reranker toggle configuration
- `retrieval-13of13-stable.env` - Retrieval-13of13-stable runtime configuration

### 🚫 Status: Legacy

These profile files are **not actively used** in current evaluation workflows:

#### **Analysis Results:**
- **Minimal references** found in current evaluation scripts
- **No active imports** found in main codebase
- **Documentation references only** in most cases
- **Experimental configurations** from earlier development phases
- **Superseded by current active profiles**

#### **Currently Active Profile Files:**
- `stable_bedrock.env` - **ACTIVELY USED** (canonical evaluation environment)
- `precision_elevated.env` - **ACTIVELY USED** (precision optimization)
- `recall_optimized.env` - **ACTIVELY USED** (recall optimization)
- `recall_optimized_bedrock.env` - **ACTIVELY USED** (recall optimization with Bedrock)

### 🔒 Database Exclusion

This directory is **automatically excluded** from database ingestion by:
- `scripts/data_processing/ingest_real_data.py` (line 144)
- `scripts/data_processing/ingest_real_data_semantic.py` (similar exclusion logic)

### 📊 Migration Summary

- **Total Profile Files Moved**: 17
- **Remaining Active Profiles**: 4
- **Migration Date**: September 2025
- **Reason**: Minimal usage in current evaluation workflows

### 🎯 Next Steps

1. **Verify Remaining Profiles**: Confirm which of the 4 remaining profiles are actually current
2. **Update Documentation**: Remove references to moved profiles from guides
3. **Clean Imports**: Remove any broken imports that reference moved profiles
4. **Archive Decision**: Consider moving to `600_archives/` if truly historical

### 📋 Profile Categories

#### **Experimental/Research Profiles:**
- `learned_fusion.env` - Fusion head training
- `precision_evidence_filter.env` - Evidence filtering research
- `precision_optimized_bedrock.env` - Precision optimization experiments
- `recall_path_a.env`, `recall_path_b.env`, `recall_path_d.env` - Recall path experiments

#### **Configuration Layer Profiles:**
- `reranker_disabled.env`, `reranker_off.env`, `reranker_on.env`, `reranker_toggle.env` - Reranker configuration layers
- `deterministic_evaluation.env` - Deterministic evaluation settings

#### **Legacy Evaluation Profiles:**
- `repo_gold_evaluation.env` - Legacy repo-gold evaluation
- `real_rag_evaluation.env` - Legacy real RAG evaluation
- `retrieval-13of13-stable.env` - Legacy retrieval configuration

#### **Utility Profiles:**
- `bedrock_conservative.env` - Conservative Bedrock settings
- `current_best.env` - Symlink to precision_elevated

---

> **Note**: These profile files represent historical development artifacts and should not be used in current evaluation workflows. Use the remaining active profiles in `300_evals/configs/profiles/` for current evaluation needs.
