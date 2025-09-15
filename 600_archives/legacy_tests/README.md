# Legacy Test Files

This directory contains test files that have been migrated from the main `tests/` directory due to outdated patterns and standards.

## Migration Date
**January 2025** - Migrated from `tests/` directory

## Files Migrated

The following test files were moved here because they use legacy patterns:

- `test_bedrock_client.py` - Uses `unittest` instead of `pytest`
- `test_config_profiles.py` - Uses `unittest` instead of `pytest`
- `test_config_settings.py` - Uses `unittest` instead of `pytest`
- `test_cross_encoder_client_fallback.py` - Uses `unittest` instead of `pytest`
- `test_doorway_utils.py` - Uses `unittest` instead of `pytest`
- `test_enhanced_schemas.py` - Uses `unittest` instead of `pytest`
- `test_eval_graph_smoke.py` - Uses `unittest` instead of `pytest`
- `test_factories.py` - Uses `unittest` instead of `pytest`

## Legacy Patterns Identified

These files were identified as legacy because they use:

1. **`unittest` instead of `pytest`** - Current project standard
2. **Manual `sys.path.insert(0, ...)` manipulation** - Instead of proper package imports
3. **No modern pytest markers** - Missing `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
4. **`unittest.TestCase` pattern** - Instead of modern pytest class structure
5. **Manual subprocess calls** - Instead of proper mocking
6. **`main()` functions** - Instead of pytest discovery

## Current Project Test Standards

The project now uses:

- **`pytest`** with proper markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.critical`)
- **Proper package imports** (`from src.module import Class`)
- **Modern pytest fixtures** and test organization
- **Tier-based markers** (`tier1`, `tier2`, `tier3`)
- **Category markers** (`unit`, `integration`, `smoke`, `prop`)

## Status

These files are **excluded from CI pipeline** and **not executed** during test runs. They are preserved for historical reference and potential future migration to modern patterns.

## Future Migration

If any of these tests need to be reactivated, they should be:

1. **Rewritten using pytest** instead of unittest
2. **Updated to use proper package imports** (`from src.`)
3. **Added appropriate pytest markers** for categorization
4. **Converted to modern fixture patterns**
5. **Moved back to the main `tests/` directory**

## Related Documentation

- [Testing Standards](../.cursor/rules/repo/testing_standards.mdc)
- [Codebase Organization Patterns](../400_guides/400_05_codebase-organization-patterns.md)
- [Development Workflow and Standards](../400_guides/400_04_development-workflow-and-standards.md)