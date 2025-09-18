# Deprecated Historical Evaluation Migration Scripts

## Overview

This directory contains deprecated migration scripts that were used to load historical evaluation data into TimescaleDB. These scripts have been superseded by more robust and maintainable solutions.

## Deprecated Scripts

### `load_historical_evals.py`
- **Original Purpose**: Main historical evaluation data migration script
- **Deprecation Date**: 2025-01-27
- **Reason**: Replaced by improved versions with better error handling and batch processing
- **Features**: 
  - Handled multiple evaluation formats (clean harness, baseline, evaluation suite, metrics)
  - Comprehensive error handling and progress tracking
  - Support for dry-run mode

### `load_historical_evals_v2.py`
- **Original Purpose**: Improved version with better batch processing
- **Deprecation Date**: 2025-01-27
- **Reason**: Superseded by v3 with proper JSONB serialization fixes
- **Improvements over v1**:
  - Better batch processing with proper transaction management
  - Enhanced data type validation and conversion
  - Improved error handling and recovery
  - Progress tracking and resumability

### `load_historical_evals_v3.py`
- **Original Purpose**: Fixed version with proper JSONB serialization
- **Deprecation Date**: 2025-01-27
- **Reason**: All historical migration needs have been addressed
- **Key Fixes**:
  - Proper JSON serialization for JSONB fields
  - Fixed database connection issues
  - Improved error handling for JSONB operations

### `load_sample_historical_evals.py`
- **Original Purpose**: Sample migration script for testing
- **Deprecation Date**: 2025-01-27
- **Reason**: Testing completed, no longer needed
- **Features**:
  - Loaded sample evaluation files for testing
  - Simplified migration logic for validation

### `migrate_to_absolute_imports.py`
- **Original Purpose**: Migrate relative imports to absolute imports across the repository
- **Deprecation Date**: 2025-01-27
- **Reason**: Migration completed successfully, no longer needed
- **Features**:
  - Systematic conversion of relative imports to absolute imports
  - PEP 8 compliance enforcement
  - Project standards alignment

## Migration Status

All historical evaluation data has been successfully migrated to TimescaleDB. The migration process included:

- ✅ Clean harness evaluation format migration
- ✅ Baseline evaluation format migration  
- ✅ Evaluation suite format migration
- ✅ System metrics format migration
- ✅ Proper JSONB serialization
- ✅ Batch processing with transaction management
- ✅ Error handling and recovery
- ✅ Progress tracking and resumability

## Current State

The historical evaluation data is now available in the TimescaleDB tables:
- `eval_run` - Evaluation run metadata
- `eval_event` - Individual metric events
- `eval_case_result` - Case-level results

## Notes

- These scripts are preserved for historical reference
- Do not use these scripts for new migrations
- All functionality has been integrated into the current evaluation system
- Database schema and migration patterns have been standardized

## Archive Information

- **Archived By**: AI Development Assistant
- **Archive Date**: 2025-01-27
- **Archive Reason**: Historical migration completed, scripts no longer needed
- **Replacement**: Current evaluation system handles all migration needs
- **Total Scripts Archived**: 5 (4 historical evaluation migration scripts + 1 import migration script)
