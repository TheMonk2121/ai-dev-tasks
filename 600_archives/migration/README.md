# Deprecated Migration Scripts

This directory contains deprecated versions of the historical evaluation migration scripts.

## Files

- `load_historical_evals_v1_deprecated.py` - Original version with comprehensive format support but JSONB serialization issues
- `load_historical_evals_v2_deprecated.py` - Improved version with batch processing but JSONB serialization issues  
- `load_historical_evals_v3_deprecated.py` - Fixed version with proper JSONB serialization but limited format support
- `load_sample_historical_evals_deprecated.py` - Sample script with hardcoded files, replaced by --limit option

## Current Version

The current, complete version is located at:
`scripts/migration/load_historical_evals.py`

This version combines the best features from all three deprecated versions:
- ✅ Comprehensive format support (from v1)
- ✅ Batch processing and transaction management (from v2)
- ✅ Proper JSONB serialization (from v3)
- ✅ Enhanced error handling and progress tracking
- ✅ Modern Python patterns and type safety

## Migration History

1. **v1**: Original comprehensive version with 4 format types but database serialization issues
2. **v2**: Added batch processing and better error handling but still had serialization issues
3. **v3**: Fixed JSONB serialization but only supported 2 format types
4. **Complete**: Combined all best features into one robust migration script

## Usage

Use the current version:
```bash
# Full migration
python scripts/migration/load_historical_evals.py

# Sample migration (replaces load_sample_historical_evals.py)
python scripts/migration/load_historical_evals.py --limit 10

# Dry run
python scripts/migration/load_historical_evals.py --dry-run --limit 5
```

Do not use the deprecated versions in this directory.
