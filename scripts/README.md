# Scripts Directory Organization

This directory contains all executable scripts organized by functional purpose. The organization follows a logical structure that groups related functionality together.

## Directory Structure

### Core System Scripts (`core/`)
Core system functionality and orchestration scripts:
- `unified_memory_orchestrator.py` - Main memory system orchestrator
- `enhanced_memory_orchestrator.py` - Enhanced memory orchestration
- `episodic_workflow_integration.py` - Episodic workflow integration
- `migrate_vector_dimensions.py` - Vector dimension migration
- `recreate_database_schema.py` - Database schema recreation
- `_bootstrap.py` - System bootstrap script

### Memory System (`memory/`)
Memory-related scripts and utilities:
- `enhanced_memory_orchestrator_with_heuristics.py` - Memory orchestrator with heuristics
- `episodic_memory_mock.py` - Episodic memory mock implementation
- `capture_current_conversation.py` - Conversation capture utility
- `setup_auto_capture.py` - Auto-capture setup
- `simple_auto_capture.py` - Simple auto-capture implementation

### Data Processing (`data_processing/`)
Data processing and transformation scripts:
- `chunking/` - Text chunking algorithms
- `cleanup/` - Data cleanup utilities
- `core/` - Core data processing functions

### Evaluation System (`evaluation/`)
Evaluation and testing scripts:
- Contains 126+ evaluation scripts
- Performance testing and validation
- RAGChecker integration scripts

### Monitoring (`monitoring/`)
System monitoring and observability:
- `48_hour_bakeoff.py` - 48-hour system bakeoff
- `48_hour_canary_monitor.py` - Canary monitoring
- `agent_monitor.py` - Agent monitoring
- `bedrock_cost_monitor.py` - AWS Bedrock cost monitoring
- `cache_performance_monitoring.py` - Cache performance monitoring
- `comprehensive_system_monitor.py` - Comprehensive system monitoring
- `database_performance_monitor.py` - Database performance monitoring
- `drift_detector.py` - Model drift detection
- `evolution_tracker.py` - System evolution tracking
- `health_gate.py` - Health check gates
- `kpi_monitor.py` - KPI monitoring
- `log_monitor.py` - Log monitoring
- `observability.py` - Observability utilities
- `performance_monitor.py` - Performance monitoring
- `production_health_monitor.py` - Production health monitoring
- `system_monitor.py` - System monitoring
- `uv_performance_monitor.py` - UV package manager performance monitoring
- `weekly_optimization.py` - Weekly optimization tasks

### Utilities (`utilities/`)
General utility scripts and tools:
- `cache_invalidation_integration.py` - Cache invalidation
- `cache_invalidation_system.py` - Cache invalidation system
- `postgresql_cache_service.py` - PostgreSQL cache service
- `similarity_scoring_algorithms.py` - Similarity scoring
- `heuristics_pack_generator.py` - Heuristics pack generation
- `check_lm_studio_status.js` - LM Studio status checker
- Contains 156+ utility scripts

### Testing (`testing/`)
Test-related scripts and configurations:
- `test_query_storage.py` - Query storage testing
- `test_real_query_storage.py` - Real query storage testing
- `simple_query_test.py` - Simple query testing
- `test_integration_config.json` - Integration test configuration
- `test_results*.json` - Test result files

### Deployment (`deployment/`)
Deployment and migration scripts:
- `migrate_eval_results_to_timescale.py` - TimescaleDB migration
- `migrate_schema_vector_dimensions.py` - Vector dimension migration
- `comprehensive_vector_migration.py` - Comprehensive vector migration
- `robust_vector_migration.py` - Robust vector migration
- `safe_migrate_vector_dimensions.py` - Safe vector dimension migration
- `deduplicate_database.py` - Database deduplication

### Maintenance (`maintenance/`)
System maintenance and housekeeping:
- Contains 43+ maintenance scripts
- Database maintenance utilities
- System cleanup scripts

### Analysis (`analysis/`)
Data analysis and reporting scripts:
- `ablation_snapshot.py` - Ablation analysis
- `analyze_cache_trends.py` - Cache trend analysis
- `analyze_file_naming.py` - File naming analysis
- `analyze_gold_cases_accuracy.py` - Gold case accuracy analysis
- `analyze_maintenance_data.py` - Maintenance data analysis
- `analyze_markdown_issues.py` - Markdown issue analysis
- `capture_hypothesis_findings.py` - Hypothesis findings capture

### Shell Scripts (`shell/`)
Shell scripts organized by purpose:
- `ci/` - Continuous integration scripts (12 files)
- `deployment/` - Deployment scripts (43 files)
- `maintenance/` - Maintenance scripts (6 files)
- `monitoring/` - Monitoring scripts
- `setup/` - Setup scripts (10 files)
- `utilities/` - Utility shell scripts (17 files)

### Configuration (`configs/`)
Configuration files and profiles:
- `mcp_api_keys.json` - MCP API keys
- `profiles/` - Environment profiles (3 files)
- `setup/` - Setup configurations

### SQL Scripts (`sql/`)
Database schema and migration scripts:
- `00_extensions.sql` - PostgreSQL extensions
- `01_documents_chunks_ddl.sql` - Documents and chunks DDL
- `02_indexes_online.sql` - Online index creation
- `03_retrieval_view.sql` - Retrieval view creation
- `04_backfill_archives_and_tsv.sql` - Archive backfill
- `05_timescale_eval_telemetry.sql` - TimescaleDB telemetry
- `06_sanity_checks.sql` - Sanity check queries
- Various cleanup and maintenance SQL scripts

## Usage Guidelines

1. **Core System**: Use scripts in `core/` for main system orchestration
2. **Memory Operations**: Use scripts in `memory/` for memory-related tasks
3. **Data Processing**: Use scripts in `data_processing/` for data transformation
4. **Evaluation**: Use scripts in `evaluation/` for testing and validation
5. **Monitoring**: Use scripts in `monitoring/` for system observability
6. **Utilities**: Use scripts in `utilities/` for general-purpose tasks
7. **Testing**: Use scripts in `testing/` for test execution and validation
8. **Deployment**: Use scripts in `deployment/` for system deployment
9. **Maintenance**: Use scripts in `maintenance/` for system upkeep
10. **Analysis**: Use scripts in `analysis/` for data analysis and reporting

## Execution

All Python scripts should be executed using the UV package manager:
```bash
uv run python scripts/<category>/<script_name>.py
```

Shell scripts can be executed directly:
```bash
./scripts/shell/<category>/<script_name>.sh
```

## Dependencies

- Python 3.12+
- UV package manager
- PostgreSQL with pgvector extension
- Various Python packages as defined in `pyproject.toml`

## Maintenance

This organization is maintained to ensure:
- Clear separation of concerns
- Easy discovery of functionality
- Logical grouping of related scripts
- Consistent naming conventions
- Proper dependency management