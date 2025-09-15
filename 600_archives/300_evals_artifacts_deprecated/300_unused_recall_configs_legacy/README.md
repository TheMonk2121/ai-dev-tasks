# 300_unused_recall_configs_legacy

## ⚠️ Legacy Directory - Unused Recall Configurations

This directory contains **unused recall configuration files** that are no longer referenced in current evaluation scripts.

### 📁 Contents

- `recall_path_c.env` - Recall Path C configuration (evidence budget & filter logic)
- `recall_path_a_fusion.env` - Recall Path A Fusion configuration (RRF + cross-encoder rerank)

### 🚫 Status: Unused

These configuration files are **not actively used** in current evaluation scripts:

#### **Analysis Results:**
- **No script references** found in current evaluation workflows
- **No active usage** in deployment or CI/CD pipelines
- **Experimental configurations** that were tested but not adopted
- **Historical configurations** from previous recall optimization attempts

#### **Currently Active Recall Configs:**
- `recall_optimized_bedrock.env` - Primary recall optimization config
- `recall_optimized.env` - Alternative recall optimization config
- `recall_path_a.env` - Retrieval breadth + evidence budget
- `recall_path_b.env` - Query expansion with HyDE
- `recall_path_d.env` - Reader loop with answerability check

### 🔒 Archive Status

This directory is **archived** and should not be used for active development. The configurations are preserved for historical reference only.

### 📅 Archived: September 2025

**Reason**: Unused recall configurations not referenced in current evaluation scripts.
