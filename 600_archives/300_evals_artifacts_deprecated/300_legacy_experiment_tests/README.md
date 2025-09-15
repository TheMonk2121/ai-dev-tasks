# 300_legacy_experiment_tests

## ⚠️ Legacy Directory - Unused Experiment Tests

This directory contains **legacy test files** that were moved from `300_evals/experiments/` because they are no longer used in the current system.

### 📁 Contents

**18 Test Files Moved:**
- `test_predictive_intelligence.py` - Predictive intelligence testing
- `test_supersedence_retrieval.py` - Supersedence retrieval testing
- `test_enhanced_pipeline.py` - Enhanced pipeline testing
- `test_performance_ltst_integration.py` - Performance-LTST integration testing
- `test_dspy_ltst_integration.py` - DSPy-LTST integration testing
- `test_resilience.py` - System resilience testing
- `test_decision_extractor_direct.py` - Decision extractor testing
- `test_unified_data_pipeline.py` - Unified data pipeline testing
- `test_smart_chunker.py` - Smart chunker testing
- `test_decision_extraction.py` - Decision extraction testing
- `test_n8n_ltst_integration.py` - n8n-LTST integration testing
- `test_ux_ltst_integration.py` - UX-LTST integration testing
- `test_dsn_integration.py` - DSN integration testing
- `test_scribe_ltst_integration.py` - Scribe-LTST integration testing
- `test_document_processor_integration.py` - Document processor testing
- `test_concurrent.py` - Concurrent operations testing
- `test_git_ltst_integration.py` - Git-LTST integration testing
- `test_quality_ltst_integration.py` - Quality-LTST integration testing

### 🚫 Status: Legacy

These test files are **not actively used** because:

#### **CI/CD Exclusion:**
- `pytest.ini` explicitly excludes `300_experiments` from test discovery
- `pyproject.toml` excludes `300_experiments` from CI runs
- **No test discovery** in automated testing pipelines

#### **No Active References:**
- **Zero references** found in main scripts directory
- **Zero imports** found in main codebase
- **No integration** with current testing framework

#### **Purpose:**
- These were **experimental test files** created during development
- **One-off testing** for specific features or integrations
- **Proof-of-concept** implementations that were never integrated

### 🔒 Archive Status

This directory is **archived** and should not be used for active development. The test files are preserved for historical reference only.

### 📅 Archived: September 2025

**Reason**: Legacy experiment tests excluded from CI/CD and not referenced by main codebase.

### 🎯 Remaining Active Files in experiments/

The following files remain in `300_evals/experiments/` as they are still useful:

- `300_rag_pipeline_governance.py` - **Actively used** by `scripts/evaluation/ragchecker_pipeline_governance.py`
- `300_enhanced_query_pattern_graph.py` - Potentially useful graph-based query patterns
- `300_sop_engine.py` - SOP (Standard Operating Procedures) engine
- `demo_query_pattern_knowledge_graph.py` - Demo script
- `demonstrate_smart_chunking.py` - Smart chunking demonstration
- `quick_test.py` - Quick test utility
- `reindex_with_smart_chunking.py` - Reindexing utility
- `300_phase2_exact_config.sh` - Phase 2 configuration script
