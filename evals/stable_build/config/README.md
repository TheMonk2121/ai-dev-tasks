# Active Configuration Files

## ✅ Current Configuration Directory

This directory contains **all actively used configuration files** for the AI Development Tasks evaluation system.

### 📁 Contents

**21 Active Configuration Files:**

#### **Profile Configurations (4 files):**
- `precision_elevated.env` - Primary precision optimization configuration
- `recall_optimized.env` - Primary recall optimization configuration (backend-agnostic)
- `recall_optimized_bedrock.env` - Primary recall optimization configuration (Bedrock-specific)
- `stable_bedrock.env` - Primary stable configuration (locked for regression tracking)

#### **Layer Configurations (5 files):**
- `base.env` - Base evaluation configuration
- `stable.env` - Stable evaluation configuration (conservative settings)
- `reranker_on.env` - Enable cross-encoder reranker
- `reranker_off.env` - Disable cross-encoder reranker
- `delta_fewshot.env` - Few-shot evaluation configuration

#### **System Configurations (8 files):**
- `base.yaml` - Base system configuration
- `dev.yaml` - Development environment configuration
- `prod.yaml` - Production environment configuration
- `test.yaml` - Test environment configuration
- `retrieval.yaml` - Retrieval system configuration
- `retriever_weights.yaml` - Retriever scoring weights
- `retriever_limits.yaml` - Retriever limits and budgets
- `reader_limits.yaml` - Reader sentence budgets and limits
- `agent_memory_spec.yaml` - Agent memory specification

#### **CI/CD Configurations (2 files):**
- `.pre-commit-config.yml` - Pre-commit hooks configuration
- `.cz.yaml` - Commitizen configuration

### 🎯 Usage

These configuration files are **actively referenced** by:
- Evaluation scripts (`evals/scripts/evaluation/`)
- Deployment scripts (`scripts/shell/deployment/`)
- CI/CD pipelines
- System initialization
- Memory management systems

### 🔄 Maintenance

- **Profile configs**: Updated based on evaluation results and performance tuning
- **Layer configs**: Updated for different evaluation scenarios
- **System configs**: Updated for environment-specific settings
- **CI configs**: Updated for code quality and deployment standards

### 📝 Notes

- **Last Updated**: 2025-09-14
- **Organization**: All active configs consolidated in single directory
- **Legacy Files**: Moved to `evals/artifacts/300_legacy_configs/`
- **Database Impact**: None (configs are not ingested into database)
