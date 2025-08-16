# Legacy Test Files - Archived

## 📋 **Archive Information**

**Date Archived**: 2025-08-16
**Reason**: Legacy test system replaced by modern marker-based approach
**Original Location**: `dspy-rag-system/tests/`
**Replacement**: Modern tests in `tests/` directory with marker-based selection

## 🎯 **Why Archived**

These test files were explicitly marked as **LEGACY** and caused confusion:

- **126 Ruff errors** (47 undefined names, 30 unused imports, 29 unused variables)
- **Old unittest patterns** not aligned with modern pytest standards
- **Explicitly marked as deprecated** in `comprehensive_test_suite.py`
- **Replaced by marker-based system** using `./run_tests.sh --tiers 1 --kinds smoke`

## 📁 **Contents**

### Test Files
- `comprehensive_test_suite.py` - Legacy comprehensive test runner (⚠️ LEGACY)
- `test_*.py` - Individual test files using old unittest patterns
- `conftest.py` - Legacy pytest configuration
- `framework/` - Legacy test framework components
- `queries/` - Legacy test query sets

### Documentation
- `README.md` - Legacy test setup guide
- `README-dev.md` - Legacy development documentation

## 🚀 **Modern Replacement**

**Use the new marker-based test system instead:**

```bash
# Fast PR gate
./run_tests.sh --tiers 1 --kinds smoke

# Critical unit tests
./run_tests.sh --tiers 1 --kinds unit

# Production integration
./run_tests.sh --tiers 1 2 --kinds integration

# Custom expressions
./run_tests.sh --markers 'tier1 and not e2e'
```

## 📊 **Impact**

- **Eliminated**: 126 Ruff errors from codebase
- **Reduced**: Maintenance burden and confusion
- **Improved**: Code quality metrics
- **Aligned**: With archival policies for deprecated code

## 🔗 **Related Files**

- **Modern Tests**: `tests/` directory (active, properly formatted)
- **Test Runner**: `dspy-rag-system/run_tests.sh` (marker-based)
- **Configuration**: `dspy-rag-system/pytest.ini` (modern markers)
- **Archival Policy**: `200_setup/200_naming-conventions.md`

---

*This archive follows our established policy of moving deprecated code to `600_archives/` while preserving historical context.*
