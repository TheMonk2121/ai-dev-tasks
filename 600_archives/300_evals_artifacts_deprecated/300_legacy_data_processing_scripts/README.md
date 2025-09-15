# 300_legacy_data_processing_scripts

## ⚠️ Legacy Directory - Unused Data Processing Scripts

This directory contains **legacy data processing scripts** that were moved from `scripts/data_processing/` because they are no longer used in the current evaluation system.

### 📁 Contents

**24 Legacy Scripts Moved:**
- `backfill_embeddings.py` - Database embedding backfill utility
- `bedrock_batch_processor.py` - AWS Bedrock batch processing system
- `bedrock_client.py` - AWS Bedrock client (superseded by enhanced version)
- `bedrock_openai_shim.py` - OpenAI compatibility shim for Bedrock
- `bedrock_setup_guide.py` - AWS Bedrock setup guide
- `bootstrap_repo_gold_dataset.py` - **DEPRECATED** repo-gold dataset bootstrapper
- `cases_sync_ids.py` - Case ID synchronization utility
- `convert_json_to_jsonl.py` - JSON to JSONL format conversion
- `cross_encoder_reranker.py` - Cross-encoder reranking system (not integrated)
- `dedup_gold.py` - Gold dataset deduplication utility
- `export_hardcoded_gold.py` - Hardcoded gold dataset export
- `export_schemas.py` - Pydantic schema export utility
- `extract_context.py` - Context extraction utility
- `extract_qa_pairs.py` - Q&A pair extraction from gold cases
- `generate_all_summaries.py` - Batch summary generation
- `generate_backlog_cycle_times.py` - Backlog timing analysis
- `generate_prd.py` - PRD generation automation
- `generate_reader_gold_bootstrap.py` - Reader gold dataset bootstrap
- `generation_cache_schema_migration.py` - Database schema migration
- `normalize_gold.py` - Gold dataset normalization
- `normalize_metadata_headers.py` - Metadata header normalization
- `shadow_ingest.py` - Shadow database ingestion system
- `train_fusion_head.py` - Fusion head training utility

### 🚫 Status: Legacy

These scripts are **not actively used** in current evaluation workflows:

#### **Analysis Results:**
- **Zero references** found in current evaluation scripts (`scripts/evaluation/`)
- **Zero references** found in current utilities (`scripts/utilities/`)
- **No imports** found in main codebase
- **Deprecated markers** present in several scripts
- **Historical development artifacts** from earlier phases

#### **Currently Active Data Processing Scripts:**
- `ingest_real_data.py` - Real data ingestion (potentially current)
- `ingest_real_data_semantic.py` - Semantic data ingestion (potentially current)
- `semantic_chunker.py` - Semantic chunking (used by ingestion scripts)

### 🔒 Database Exclusion

This directory is **automatically excluded** from database ingestion by:
- `scripts/data_processing/ingest_real_data.py` (line 144)
- `scripts/data_processing/ingest_real_data_semantic.py` (similar exclusion logic)

### 📊 Migration Summary

- **Total Scripts Moved**: 24
- **Remaining Active Scripts**: 3
- **Migration Date**: September 2025
- **Reason**: Zero usage in current evaluation workflows

### 🎯 Next Steps

1. **Verify Remaining Scripts**: Confirm which of the 3 remaining scripts are actually current
2. **Update Documentation**: Remove references to moved scripts from guides
3. **Clean Imports**: Remove any broken imports that reference moved scripts
4. **Archive Decision**: Consider moving to `600_archives/` if truly historical

---

> **Note**: These scripts represent historical development artifacts and should not be used in current evaluation workflows. Use the remaining active scripts in `scripts/data_processing/` for current data processing needs.
