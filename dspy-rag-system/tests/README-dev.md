# Test Development Guide

## Import Path Management

### Centralized Import Logic
All test files should rely on `conftest.py` for import path setup. The `conftest.py` file ensures that `dspy_modules` and `utils` packages are available to all tests, regardless of where pytest is run from.

### Configuration Policy: "One Source Per Scope"
- **Root scope** (repo open in Cursor): `pyrightconfig.json` handles repo-wide analysis
- **Subproject scope** (dspy-rag-system/ opened directly): `dspy-rag-system/pyrightconfig.json` handles local development
- **No conflicts**: Avoid `[tool.pyright]` in pyproject.toml files
- **VS Code alignment**: `.vscode/settings.json` mirrors root pyrightconfig.json

### When to Use Custom Import Logic
- **Keep dynamic imports** for legitimate use cases (e.g., database mocking, model switching)
- **Remove per-file sys.path hacks** - these are now handled centrally
- **Use setup_imports.py** only for scripts that run outside pytest context

### Migration Guidelines
- Tests that previously used `sys.path.append("src")` can now rely on conftest.py
- Complex dynamic loading (e.g., `test_database_resilience.py`) should remain as-is
- Scripts that import `setup_imports.py` will continue to work unchanged

## Test Organization
- **Tier 1 tests**: Critical system components (vector store, document processor)
- **Tier 2 tests**: High-priority infrastructure (database resilience, error handling)
- **Tier 3 tests**: Supporting utilities and maintenance

## Running Tests
```bash
# From repo root
pytest dspy-rag-system/tests/

# From dspy-rag-system directory
pytest tests/
```

## Import Policy
- **Prefer conftest.py**: All tests automatically get proper import paths
- **Keep dynamic imports**: For database mocking, model switching, etc.
- **Remove manual sys.path**: No need for per-file path manipulation
- **Backward compatibility**: setup_imports.py still works for scripts

## Test Variable Management

### F841 Error Prevention
- **Avoid variable overwriting**: Use unique names for each test case
- **Remove unused variables**: Clean up test setup variables
- **Use descriptive names**: `critical_error` vs `medium_error` instead of reusing `error_message`

### Examples
```python
# ❌ Bad: Variable overwriting
def test_severity_scores():
    error_message = "Security violation"
    error_message = "File not found"  # Overwrites previous!

# ✅ Good: Unique variable names
def test_severity_scores():
    critical_error = "Security violation"
    medium_error = "File not found"
```

### Test-Specific Guidelines
- **Use descriptive variable names** for test data
- **Remove unused test setup variables**
- **Keep dynamic imports** for legitimate use cases (database mocking, model switching)
- **Apply F841 best practices** from comprehensive coding guide
