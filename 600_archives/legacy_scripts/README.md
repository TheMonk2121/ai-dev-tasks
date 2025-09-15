# Legacy Scripts Archive

## ⚠️ Legacy Directory - Deprecated Scripts

This directory contains **legacy scripts** that were moved from `scripts/` because they are no longer actively used in the current system.

### 📁 Contents

**33 Legacy Scripts Moved:**

#### **Data Processing Scripts (1 file):**
- `ingest_real_data_semantic.py` - Legacy semantic data ingestion

#### **Utility Scripts (9 files):**
- `integrate_pydantic_models.py` - Legacy Pydantic model integration
- `run_add_content_tsv.py` - Legacy TSV content utility
- `tiny_grid.py` - Legacy grid utility
- `create_backlog_item.py` - Legacy backlog item creation
- `regen_guide.py` - Legacy guide regeneration utility
- `repo_gold_setup_summary.py` - Legacy repo-gold setup summary
- `role_assignment_metadata.py` - Legacy role assignment metadata
- `documentation_indexer.py` - Legacy documentation indexer
- `find_duplicates.py` - Legacy duplicate finder
- `doc_coherence_validator.py` - Legacy document coherence validator

#### **Development Tools (2 files):**
- `add_deprecation_notices.py` - Legacy deprecation notice utility
- `upgrade_typing_builtins.py` - Legacy typing upgrade utility

#### **Evaluation Scripts (12 files):**
- `migrate_to_pydantic_evals.py` - Legacy Pydantic evaluation migration
- `system_health_check.py` - Legacy system health check
- `db_readiness_check.py` - Legacy database readiness check
- `baseline_metrics_collector.py` - Legacy baseline metrics collector
- `ci_gate_retrieval.py` - Legacy CI gate for retrieval
- `file_analysis_checklist.py` - Legacy file analysis checklist
- `smoke_prefilter.py` - Legacy smoke test prefilter
- `run_evaluation_suite.py` - **DEPRECATED** comprehensive evaluation suite runner
- `apply_test_dispositions.py` - Legacy test disposition application
- `ci_schema_guardrails.py` - Legacy CI schema guardrails
- `gate_and_promote.py` - **DEPRECATED** gate and promote system
- `ci_evaluation_pipeline.py` - Legacy CI evaluation pipeline

#### **Maintenance Scripts (4 files):**
- `documentation_cleanup.py` - Legacy documentation cleanup
- `repo_maintenance.py` - Legacy repository maintenance
- `migrate_to_vscode_markdown.py` - Legacy VSCode markdown migration
- `fix_broken_links.py` - Legacy broken link fixer

#### **Monitoring Scripts (1 file):**
- `dependency_monitor.py` - Legacy dependency monitoring

#### **Root Scripts (1 file):**
- `remove_dead_code.py` - Legacy dead code removal utility

### 🚫 Status: Legacy

These scripts are **not actively used** in current workflows:

#### **Analysis Results:**
- **Explicitly marked as DEPRECATED** in source code comments
- **No active references** found in current evaluation workflows
- **Superseded by newer implementations** or alternative approaches
- **One-off utilities** that were used once and never referenced again
- **Legacy maintenance tools** that are no longer needed

#### **Currently Active Scripts:**
All active scripts remain in the `scripts/` directory:
- **Core evaluation scripts**: `ragchecker_official_evaluation.py`, `production_evaluation.py`
- **Core utility scripts**: `unified_memory_orchestrator.py`, `mcp_memory_server.py`
- **Core data processing**: `ingest_real_data.py`, `semantic_chunker.py`
- **Core maintenance**: `cleanup_database_content.py`, `audit_chunking_standards.py`

### 📝 Notes

- **Last Updated**: 2025-09-14
- **Reason for Archive**: Script cleanup and organization
- **Replacement**: Active scripts remain in `scripts/` directory
- **Database Impact**: None (scripts are not ingested into database)
- **Total Moved**: 33 scripts (reduced scripts directory from 427 to 396 files)
